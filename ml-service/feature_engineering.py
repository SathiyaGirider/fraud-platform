import pandas as pd
import numpy as np


# ---------------------------------------------------------------------------
# Time features — stateless, no train reference needed
# ---------------------------------------------------------------------------

def add_time_features(df):
    df = df.copy()
    df['hour'] = df['TransactionDT'] % 86400 // 3600
    df['day_of_week'] = (df['TransactionDT'] // 86400) % 7
    return df


# ---------------------------------------------------------------------------
# Amount features
# card1_mean lookup: computed from train, applied to any df
# ---------------------------------------------------------------------------

def add_amount_features(df, df_train=None):
    df = df.copy()
    df['log_amount'] = np.log1p(df['TransactionAmt'])
    source = df_train if df_train is not None else df
    card_mean = source.groupby('card1')['TransactionAmt'].mean().rename('card1_mean')
    fallback = source['TransactionAmt'].median()
    df = df.merge(card_mean, on='card1', how='left')
    df['card1_mean'] = df['card1_mean'].fillna(fallback)
    df['amount_to_card_mean'] = df['TransactionAmt'] / (df['card1_mean'] + 1e-8)
    df.drop(columns='card1_mean', inplace=True)
    return df


# ---------------------------------------------------------------------------
# Email features
# p_email_freq: frequency encoding computed from train
# ---------------------------------------------------------------------------

def add_email_features(df, df_train=None):
    df = df.copy()
    df['email_domain_mismatch'] = (
        df['P_emaildomain'].fillna('unknown') != df['R_emaildomain'].fillna('unknown')
    ).astype(int)
    high_risk_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'anonymous.com']
    df['purchaser_email_risk'] = df['P_emaildomain'].isin(high_risk_domains).astype(int)
    source = df_train if df_train is not None else df
    p_freq = source['P_emaildomain'].value_counts(normalize=True)
    df['p_email_freq'] = df['P_emaildomain'].map(p_freq).fillna(0)
    return df


# ---------------------------------------------------------------------------
# Device features — stateless
# ---------------------------------------------------------------------------

def add_device_features(df):
    df = df.copy()
    df['is_mobile'] = (df['DeviceType'] == 'mobile').astype(int)
    df['has_identity'] = df['DeviceType'].notna().astype(int)
    return df


# ---------------------------------------------------------------------------
# Card features — frequency encoding from train
# ---------------------------------------------------------------------------

def add_card_features(df, df_train=None):
    df = df.copy()
    source = df_train if df_train is not None else df
    # card4 = network (visa/mc), card6 = type (debit/credit/prepaid)
    # card2, card3, card5 = additional metadata — frequency encoded
    for col in ['card2', 'card3', 'card4', 'card5', 'card6']:
        freq = source[col].value_counts(normalize=True)
        df[f'{col}_freq'] = df[col].map(freq).fillna(0)
    return df


# ---------------------------------------------------------------------------
# UID features — TWO variants:
#
# 1. add_uid_features(df_train, df_val, df_test)
#    Used in notebook/training. Computes lookup maps from train and applies
#    them to all three splits. Call this in your training notebook.
#
# 2. apply_uid_features(df, uid_stats)
#    Used in pipeline.py at inference. Takes one df (single transaction)
#    and the pre-saved uid_stats dict. Call this in pipeline.py.
#
# uid_stats is saved during training:
#   uid_stats = build_uid_stats(df_train)
#   joblib.dump(uid_stats, 'models/uid_stats.pkl')
# ---------------------------------------------------------------------------

def build_uid_stats(df_train):
    """
    Compute UID lookup maps from the training set.
    Save the returned dict as models/uid_stats.pkl.
    Call this once in your training notebook after splits are ready.
    """
    df = df_train.copy()
    df['uid'] = (
        df['card1'].astype(str) + '_' +
        df['card2'].astype(str) + '_' +
        df['addr1'].astype(str)
    )
    return {
        'uid_count':       df.groupby('uid')['isFraud'].count(),
        'uid_amt_mean':    df.groupby('uid')['TransactionAmt'].mean(),
        'uid_amt_std':     df.groupby('uid')['TransactionAmt'].std().fillna(0),
        'card1_amt_mean':  df.groupby('card1')['TransactionAmt'].mean(),
        'global_amt_mean': df['TransactionAmt'].mean(),
        'global_amt_std':  df['TransactionAmt'].std(),
    }


def apply_uid_features(df, uid_stats):
    """
    Apply pre-computed UID lookup maps to a df (any size — one row or full split).
    uid_stats must come from build_uid_stats(df_train) or be loaded from pkl.
    """
    df = df.copy()
    df['uid'] = (
        df['card1'].astype(str) + '_' +
        df['card2'].astype(str) + '_' +
        df['addr1'].astype(str)
    )
    gam = uid_stats['global_amt_mean']
    gas = uid_stats['global_amt_std']

    df['uid_count']      = df['uid'].map(uid_stats['uid_count']).fillna(0)
    df['uid_amt_mean']   = df['uid'].map(uid_stats['uid_amt_mean']).fillna(gam)
    df['uid_amt_std']    = df['uid'].map(uid_stats['uid_amt_std']).fillna(gas)
    df['uid_amt_zscore'] = (
        (df['TransactionAmt'] - df['uid_amt_mean']) /
        df['uid_amt_std'].replace(0, 1)
    )
    df['card1_amt_mean']    = df['card1'].map(uid_stats['card1_amt_mean']).fillna(gam)
    df['amt_to_card1_mean'] = df['TransactionAmt'] / df['card1_amt_mean'].replace(0, 1)
    return df


def add_uid_features(df_train, df_val, df_test):
    """
    Training-notebook version — takes all 3 splits.
    Internally uses build_uid_stats + apply_uid_features.
    """
    uid_stats = build_uid_stats(df_train)
    df_train = apply_uid_features(df_train, uid_stats)
    df_val   = apply_uid_features(df_val,   uid_stats)
    df_test  = apply_uid_features(df_test,  uid_stats)
    return df_train, df_val, df_test


# ---------------------------------------------------------------------------
# Product features — TWO variants (same pattern as UID above)
#
# 1. add_product_features(df_train, df_val, df_test) — for training notebook
# 2. apply_product_features(df, prod_cols) — for pipeline.py at inference
#
# prod_cols is saved during training:
#   prod_cols = [c for c in df_train.columns if c.startswith('prod_')]
#   joblib.dump(prod_cols, 'models/prod_cols.pkl')  # or embedded in feat_cols
# ---------------------------------------------------------------------------

def apply_product_features(df, prod_cols):
    """
    One-hot encode ProductCD for a single df, aligned to the training columns.
    prod_cols: list of prod_* column names from training (e.g. ['prod_C','prod_H','prod_R','prod_S','prod_W'])
    """
    df = df.copy()
    dummies = pd.get_dummies(df['ProductCD'], prefix='prod')
    for col in prod_cols:
        if col not in dummies.columns:
            dummies[col] = 0
    df = pd.concat([df, dummies[prod_cols]], axis=1)
    return df


def add_product_features(df_train, df_val, df_test):
    """
    Training-notebook version — takes all 3 splits, aligns columns to train.
    """
    prod_train = pd.get_dummies(df_train['ProductCD'], prefix='prod')
    prod_val   = pd.get_dummies(df_val['ProductCD'],   prefix='prod')
    prod_test  = pd.get_dummies(df_test['ProductCD'],  prefix='prod')

    for col in prod_train.columns:
        if col not in prod_val.columns:   prod_val[col]  = 0
        if col not in prod_test.columns:  prod_test[col] = 0
    prod_val  = prod_val[prod_train.columns]
    prod_test = prod_test[prod_train.columns]

    df_train = pd.concat([df_train, prod_train], axis=1)
    df_val   = pd.concat([df_val,   prod_val],   axis=1)
    df_test  = pd.concat([df_test,  prod_test],  axis=1)
    return df_train, df_val, df_test

# feature_engineering.py — add this pair

def build_cat_id_freq_maps(df_train, cat_id_cols):
    """
    Compute frequency maps for categorical id_ columns from the full
    training set. Save the returned dict as models/cat_id_freq_maps.pkl.
    Call this once in the training notebook, same pattern as build_uid_stats.
    """
    return {
        col: df_train[col].value_counts(normalize=True)
        for col in cat_id_cols
    }


def apply_cat_id_freq_features(df, cat_id_freq_maps):
    """
    Apply pre-computed cat_id frequency maps to a df (one row or full split).
    cat_id_freq_maps must come from build_cat_id_freq_maps(df_train, cat_id_cols)
    or be loaded from pkl — never recomputed from a sample at inference.
    """
    df = df.copy()
    for col, freq in cat_id_freq_maps.items():
        if col in df.columns:
            df[f'{col}_freq'] = df[col].map(freq).fillna(0)
        else:
            df[f'{col}_freq'] = 0
    return df