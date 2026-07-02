# ml-service/pipeline.py
# Full end-to-end orchestration: raw transaction → compliance-ready investigation output
# Day 19 — June 19

from __future__ import annotations
import joblib
import numpy as np
import pandas as pd
import shap as shap_lib
import time

from feature_engineering import (
    add_time_features,
    add_amount_features,
    add_email_features,
    add_device_features,
    add_card_features,
    apply_uid_features,       # inference-only: takes df + uid_stats dict
    apply_product_features,   # inference-only: takes df + prod_cols list
)
from shap_narratives import build_shap_dict
from sar_drafter import draft_sar_narrative


# ---------------------------------------------------------------------------
# Module-level loads — NEVER load inside the prediction function
# ---------------------------------------------------------------------------
# Loading from disk on every API call would add 400–800ms per request.
# Module-level loading happens once at server startup. Subsequent calls reuse
# the in-memory objects. This is the correct pattern for production ML APIs.
# ---------------------------------------------------------------------------

model     = joblib.load('../models/fraud_model.pkl')
feat_cols = joblib.load('../models/feature_cols.pkl')
threshold = joblib.load('../models/threshold.pkl')      # from Week 2 tuning
uid_stats = joblib.load('../models/uid_stats.pkl')      # from build_uid_stats(df_train)
df_train  = joblib.load('../models/df_train_sample.pkl')  # small sample for freq encoding lookups
cat_id_freq_maps = joblib.load('../models/cat_id_freq_maps.pkl')
_bg_sample = (
    df_train.sample(100, random_state=42)[feat_cols]
    .fillna(-999)
    .to_numpy(dtype=np.float64)
)
explainer = shap_lib.TreeExplainer(
    model,
    data=_bg_sample,
    feature_perturbation="interventional"
)

# prod_cols derived from feat_cols — no separate pkl needed
prod_cols = [c for c in feat_cols if c.startswith('prod_')]


# ---------------------------------------------------------------------------
# Preprocessing
# ---------------------------------------------------------------------------

def preprocess_transaction(txn: dict) -> np.ndarray:
    """
    Apply full feature engineering to a single transaction dict.

    CRITICAL: Must match exactly what was done during training.
    Any divergence — different fillna, different column order, missing
    features — causes training-serving skew. The model then scores
    against a different distribution than it was trained on.

    Args:
        txn : dict with raw transaction fields

    Returns:
        numpy array of shape (1, n_features)
    """
    df = pd.DataFrame([txn])

    # Stateless transforms first
    df = add_time_features(df)
    df = add_device_features(df)

    # Train-reference transforms — use df_train for frequency lookups
    df = add_amount_features(df, df_train=df_train)
    df = add_email_features(df, df_train=df_train)
    df = add_card_features(df, df_train=df_train)

    # UID features — use pre-computed lookup maps, not the raw training df
    # apply_uid_features maps card1/card2/addr1 combos to their training stats
    df = apply_uid_features(df, uid_stats)

    # ProductCD one-hot — aligned to training columns
    df = apply_product_features(df, prod_cols)

    # C/M columns: M cols need T/F → 1/0 mapping (same as training notebook)
    m_cols = [c for c in feat_cols if c.startswith('M')]
    for col in m_cols:
        if col in df.columns:
            df[col] = df[col].map({'T': 1, 'F': 0}).fillna(-1)

    # Categorical id_ columns: freq encode from df_train
    # Categorical id_ columns: freq encode using precomputed training maps
    # (built once from full df_train — see training notebook — not recomputed per call)
    for col, freq in cat_id_freq_maps.items():
        if col in df.columns:
            df[f'{col}_freq'] = df[col].map(freq).fillna(0)
        else:
            df[f'{col}_freq'] = 0
    # cat_id_cols = [
    #     c for c in df.columns
    #     if c.startswith('id_') and df[c].dtype == 'object'
    # ]
    # for col in cat_id_cols:
    #     freq = df_train[col].value_counts(normalize=True) if col in df_train.columns else pd.Series(dtype=float)
    #     df[f'{col}_freq'] = df[col].map(freq).fillna(0)

    # Select features in training order, fill remaining NaN with -999
    # (matches training notebook: X_train = df_train[FEATURE_COLS].fillna(-999))
    X = df.reindex(columns=feat_cols).fillna(-999)
    return X


# ---------------------------------------------------------------------------
# Full prediction + explanation + narrative pipeline
# ---------------------------------------------------------------------------
from collections import OrderedDict

def group_top_features(top_features: list) -> list:
    """
    Groups risk-increasing SHAP features by category for cleaner API output.
    Mirrors _print_shap_grouped() from the Day 18 notebook — same grouping
    logic, JSON output instead of print statements.
    """
    positive = [f for f in top_features if f.get('shap_value', 0) > 0]
    if not positive:
        return []

    groups = OrderedDict()
    for f in positive:
        category = f.get('category', 'Unknown')
        groups.setdefault(category, []).append(f)

    grouped = []
    for category, features in groups.items():
        rep = features[0]
        grouped.append({
            'category': category,
            'features': [
                {'feature': f['feature'], 'shap_value': f['shap_value'], 'abs_impact': f['abs_impact']}
                for f in features
            ],
            'narrative': rep['narrative'],
            'fatf_ref': rep['fatf_ref'],
            'uk_ref': rep['uk_ref'],
        })
    return grouped


def predict_and_explain(
    txn: dict,
    generate_narrative: bool = True
) -> dict:
    """
    Full pipeline: raw transaction dict → fraud score → SHAP explanation →
    compliance-annotated SAR narrative → structured response.

    Args:
        txn                : dict with raw transaction fields
        generate_narrative : if False, skip the Groq LLM call.
                             Use this for latency benchmarking or when
                             Groq rate limits are tight — SHAP + tier
                             classification still runs, narrative is None.

    Returns:
        dict with keys:
            transaction_id       : str
            fraud_score          : float (0.0–1.0)
            is_fraud             : bool (score >= threshold)
            risk_tier            : str ('HIGH RISK' / 'ELEVATED RISK' / 'LOW RISK')
            top_shap             : list of top SHAP features with compliance annotations
            narrative            : dict from draft_sar_narrative(), or None
            model_version        : str
            pipeline_latency_ms  : float (wall-clock ms for this call)
    """
    t_start = time.time()

    # 1. Preprocess
    X = preprocess_transaction(txn)

    # 2. Fraud probability
    fraud_prob = float(model.predict_proba(X)[0, 1])
    is_fraud   = fraud_prob >= threshold

    # 3. SHAP explanation with compliance annotations
    # SHAP output shape is RF-specific: depending on shap version this is either
    # a list [class0_array, class1_array] (each shape (n_samples, n_feats)),
    # or a single array of shape (n_samples, n_feats, 2). Handle both.
    raw_shap = explainer.shap_values(X, check_additivity=False)

    if isinstance(raw_shap, list):
        # older shap API: list of per-class arrays
        shap_values_row = raw_shap[1][0]
    else:
        # newer shap API: (n_samples, n_feats, n_classes) — take class 1 (fraud)
        shap_values_row = raw_shap[0, :, 1]

    shap_values_row = np.asarray(shap_values_row, dtype=np.float64)

    shap_dict = build_shap_dict(
        transaction_id=str(txn.get('TransactionID', 'UNKNOWN')),
        fraud_prob=fraud_prob,
        shap_values_row=shap_values_row,
        feature_names=feat_cols,
    )

    # 4. SAR narrative (conditionally)
    narrative_output = draft_sar_narrative(shap_dict) if generate_narrative else None

    t_end = time.time()

    return {
        'transaction_id':      txn.get('TransactionID', 'UNKNOWN'),
        'fraud_score':         round(fraud_prob, 4),
        'is_fraud':            bool(is_fraud),
        'risk_tier':           shap_dict['risk_tier'],
        'risk_themes':         shap_dict.get('risk_themes', []),
        'top_shap':            group_top_features(shap_dict['top_features']),
        'narrative':           narrative_output,
        'model_version':       'fraud_rf_ieee',
        'pipeline_latency_ms': round((t_end - t_start) * 1000, 1),
    }

