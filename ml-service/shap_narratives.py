# shap_narratives.py
# Day 16 final — covers full feat_cols list exactly as used in the pipeline

from __future__ import annotations
from typing import List, Dict


# ---------------------------------------------------------------------------
# Compliance Annotation Disclaimer
# ---------------------------------------------------------------------------
#
# FATF and UK regulatory references are provided as compliance-context
# annotations only. They do not indicate money laundering, terrorist
# financing, sanctions evasion, regulatory breaches, or suspicious activity.
#
# The mappings illustrate how transaction-risk indicators may relate to
# broader financial-crime monitoring, governance, and risk-assessment
# frameworks commonly used by regulated institutions.
#
# These references are intended to support explainability and analyst
# interpretation and are not used as model features.
#
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# NARRATIVE_MAP — exact feature matches
# ---------------------------------------------------------------------------

NARRATIVE_MAP: Dict[str, Dict[str, str]] = {

    # -----------------------------------------------------------------------
    # Transaction timing
    # -----------------------------------------------------------------------
    'hour': {
        'category': 'Behavioral Timing',
        'text': (
            "Transaction hour deviates from this card's historical pattern. "
            "Temporal anomalies may support escalation consideration under "
            "transaction monitoring frameworks."
        ),
        'fatf_ref': (
            "Supports transaction-monitoring assessments that may contribute "
            "to transaction-monitoring and risk-assessment activities associated with "
            "FATF Recommendation 20"
        ),
        'uk_ref': (
            "Relevant to ongoing monitoring under MLR 2017 Regulation 28(11) "
            "and FCA SYSC 6.3."
        ),
    },

    'day_of_week': {
        'category': 'Behavioral Timing',
        'text': (
            "Day-of-week pattern differs from this card's historical baseline, "
            "contributing a contextual timing signal to the risk assessment."
        ),
        'fatf_ref': (
            "Contextual indicator that may support transaction-monitoring "
            "assessments associated with FATF Recommendation 20."
        ),
        'uk_ref': (
            "Supports ongoing monitoring obligations under MLR 2017 "
            "Regulation 28(11)."
        ),
    },


    # -----------------------------------------------------------------------
    # Transaction amount
    # -----------------------------------------------------------------------

    'amount_to_card_mean': {
        'category': 'Transaction Amount Anomaly',
        'text': (
    "Transaction amount significantly exceeds this card's historical "
    "average. This deviation from established spending patterns may "
    "warrant further analyst review."
),
        'fatf_ref': (
            "Aligns with transaction monitoring expectations supporting FATF "
            "Recommendation 20 transaction-monitoring considerations. Significant deviation "
            "from established customer transaction patterns is a core typology "
            "indicator in FATF guidance."
        ),
        'uk_ref': (
            "Relevant to ongoing monitoring and analyst-review considerations under "
            "POCA 2002 and MLR 2017 Regulation 28, and FCA SYSC 6.3."
        ),
    },

    'log_amount': {
        'category': 'Transaction Amount Anomaly',
        'text': (
    "Transaction involves an unusually high amount relative to the "
    "customer's historical profile. This anomaly may warrant further review."
),
        'fatf_ref': (
            "Supports risk assessments relevant to FATF Recommendation 20 "
            "transaction-monitoring considerations. Transactions materially inconsistent with "
            "known customer behaviour are a core typology indicator in FATF guidance."
        ),
        'uk_ref': (
            "Relevant to ongoing monitoring and financial-crime risk management "
            "under POCA 2002 and MLR 2017 Regulation 28."
        ),
    },

    # Both column name variants kept — check feat_cols for which appears
    'card1_amt_mean': {
        'category': 'Transaction Amount Anomaly',
        'text': (
            "Transaction amount deviates significantly from the historical "
            "average for this card. This deviation from established card "
            "spending patterns may warrant further analyst review."
        ),
        'fatf_ref': (
            "Aligns with transaction monitoring expectations supporting FATF "
            "Recommendation 20 transaction-monitoring considerations. Deviation from "
            "established customer transaction patterns is a core typology "
            "indicator in FATF guidance."
        ),
        'uk_ref': (
            "Relevant to ongoing monitoring and analyst-review considerations under "
            "POCA 2002 and MLR 2017 Regulation 28, and FCA SYSC 6.3."
        ),
    },

    'amt_to_card1_mean': {
        'category': 'Transaction Amount Anomaly',
        'text': (
    "Transaction amount deviates significantly from the historical "
    "average for this card. This deviation from established card "
    "spending patterns may warrant further analyst review."
),
        'fatf_ref': (
            "Aligns with transaction monitoring expectations supporting FATF "
            "Recommendation 20 transaction-monitoring considerations. Deviation from "
            "established customer transaction patterns is a core typology "
            "indicator in FATF guidance."
        ),
        'uk_ref': (
            "Relevant to ongoing monitoring and analyst-review considerations under "
            "POCA 2002 and MLR 2017 Regulation 28, and FCA SYSC 6.3."
        ),
    },

    # -----------------------------------------------------------------------
    # UID-level behavioural amount statistics
    # -----------------------------------------------------------------------

    'uid_amt_mean': {
        'category': 'Transaction Amount Anomaly',
        'text': (
            "The average transaction amount for this user ID is atypical "
            "relative to the broader population. An elevated average may "
            "indicate a pattern of high-value transactions inconsistent "
            "with expected customer behaviour."
        ),
        'fatf_ref': (
            "Supports transaction-monitoring assessments that may contribute "
            "to transaction-monitoring and risk-assessment activities associated "
            "with FATF Recommendation 20. Deviation from expected customer transaction "
            "value patterns is a recognised anomaly indicator in transaction monitoring."
        ),
        'uk_ref': (
            "Relevant to ongoing monitoring obligations under MLR 2017 "
            "Regulation 28 and FCA SYSC 6.3."
        ),
    },

    'uid_amt_std': {
        'category': 'Transaction Amount Anomaly',
        'text': (
            "The standard deviation of transaction amounts for this user ID "
            "is atypical — indicating either unusually consistent or unusually "
            "erratic spending behaviour, both of which may warrant further review."
        ),
        'fatf_ref': (
            "Supports transaction-monitoring assessments that may contribute "
            "to transaction-monitoring and risk-assessment activities associated with "
            "FATF Recommendation 20"
        ),
        'uk_ref': (
            "Relevant to ongoing monitoring obligations under MLR 2017 "
            "Regulation 28."
        ),
    },

    'uid_amt_zscore': {
        'category': 'Transaction Amount Anomaly',
        'text': (
            "This transaction's amount is a significant statistical outlier "
            "relative to the user ID's own historical distribution. A high "
            "z-score indicates the amount is substantially above or below "
            "what would be expected for this account."
        ),
        'fatf_ref': (
            "Aligns with transaction monitoring expectations supporting FATF "
            "Recommendation 20 transaction-monitoring considerations. Statistical outliers "
            "in customer transaction amounts are a core anomaly-detection "
            "indicator."
        ),
        'uk_ref': (
            "Relevant to ongoing monitoring and analyst-review considerations under "
            "POCA 2002 and MLR 2017 Regulation 28, and FCA SYSC 6.3."
        ),
    },

    # -----------------------------------------------------------------------
    # UID-level identity count
    # -----------------------------------------------------------------------

    'uid_count': {
        'category': 'Identity Association',
        'text': (
            "The number of unique identities (cards, emails, or devices) "
            "associated with this user ID is atypical. An unusually high "
            "count of linked identifiers may indicate account-sharing, "
            "synthetic identity patterns, or coordinated fraud ring activity."
        ),
        'fatf_ref': (
            "Contributes to monitoring considerations associated with FATF "
            "R.10 (Customer Due Diligence). Anomalous identity-linkage counts "
            "are a recognised typology indicator for synthetic identity fraud "
            "and account-takeover in FATF guidance."
        ),
        'uk_ref': (
            "Relevant to CDD and EDD obligations under MLR 2017 Regulations "
            "28 and 33, and FCA SYSC 6.3 financial crime controls."
        ),
    },

    # -----------------------------------------------------------------------
    # Identity presence flag
    # -----------------------------------------------------------------------

    'has_identity': {
        'category': 'Device / Network',
        'text': (
            "This transaction either lacks associated device and network "
            "identity attributes, or the presence of such attributes is "
            "itself an atypical signal for this card. The absence of device "
            "fingerprint data may indicate an unusual access channel."
        ),
        'fatf_ref': (
            "Provides contextual information regarding the availability of "
            "device and network identity attributes, which may contribute to "
            "broader transaction-risk assessments."
        ),
        'uk_ref': (
            "Relevant to MLR 2017 Regulation 18 (risk assessment) and "
            "FCA SYSC 6.3."
        ),
    },

    # -----------------------------------------------------------------------
    # Identity and email
    # -----------------------------------------------------------------------

    'email_domain_mismatch': {
        'category': 'Identity Association',
        'text': (
            "The purchaser's and recipient's email domains differ. Identity "
            "attribute inconsistencies may indicate elevated account-takeover "
            "or identity-verification risk."
        ),
        'fatf_ref': (
            "Contributes to identity-verification and customer due diligence "
            "considerations associated with FATF R.10. Identity inconsistencies "
            "may warrant additional verification depending on transaction context."
        ),
        'uk_ref': (
            "Informs CDD and EDD obligations under MLR 2017 Regulations 28 "
            "and 33, and FCA SYSC 6.3."
        ),
    },

    'purchaser_email_risk': {
        'category': 'Identity Association',
        'text': (
            "Purchaser email domain is a free consumer account with limited "
            "identity verification characteristics, indicating reduced "
            "identity assurance."
        ),
        'fatf_ref': (
            "Provides contextual information that may contribute to customer "
            "identity-assurance and due-diligence assessments associated with "
            "FATF R.10."
        ),
        'uk_ref': (
            "Relevant to CDD requirements under MLR 2017 Regulation 28 "
            "and FCA SYSC 6.3."
        ),
    },

    'p_email_freq': {
        'category': 'Identity Association',
        'text': (
            "Purchaser email domain has low historical frequency — potentially "
            "a rare or recently registered domain. Low-frequency identity "
            "attributes may indicate elevated due diligence considerations."
        ),
        'fatf_ref': (
            "Provides contextual information that may contribute to identity-"
            "verification and due-diligence assessments associated with FATF R.10."
        ),
        'uk_ref': (
            "Relevant to CDD obligations under MLR 2017 Regulation 28."
        ),
    },

    # -----------------------------------------------------------------------
    # Card metadata — frequency-encoded
    # card2: card issuer bank, card3: card country/type sub-category,
    # card4: network (Visa/MC), card5: card sub-type, card6: debit/credit/prepaid
    # Exact definitions are Vesta-proprietary; framed at card-attribute level.
    # -----------------------------------------------------------------------

    'card2_freq': {
        'category': 'Card / Channel Signal',
        'text': (
            "The issuing bank or card attribute associated with this card "
            "is uncommon in the historical transaction population — a "
            "contextual signal contributing to the overall risk profile."
        ),
        'fatf_ref': (
            "Provides contextual support for risk assessments within a FATF "
            "R.20 transaction monitoring framework when combined with other "
            "indicators."
        ),
        'uk_ref': (
            "Relevant to ongoing transaction monitoring under MLR 2017 "
            "Regulation 28."
        ),
    },

    'card3_freq': {
        'category': 'Card / Channel Signal',
        'text': (
            "A card attribute associated with this transaction is atypical "
            "relative to the historical population — contributing a contextual "
            "risk signal."
        ),
        'fatf_ref': (
            "Provides contextual support for risk assessments within a FATF "
            "R.20 transaction monitoring framework when combined with other "
            "indicators."
        ),
        'uk_ref': (
            "Relevant to ongoing transaction monitoring under MLR 2017 "
            "Regulation 28."
        ),
    },

    'card4_freq': {
        'category': 'Card / Channel Signal',
        'text': (
            "Card network type is uncommon in the historical transaction "
            "population — a contextual signal contributing to the risk profile."
        ),
        'fatf_ref': (
            "Provides contextual support for risk assessments within a FATF "
            "R.20 transaction monitoring framework when combined with other "
            "indicators."
        ),
        'uk_ref': (
            "Relevant to ongoing transaction monitoring under MLR 2017 "
            "Regulation 28."
        ),
    },

    'card5_freq': {
        'category': 'Card / Channel Signal',
        'text': (
            "Card sub-type attribute is atypical relative to the historical "
            "population — contributing a contextual card-level risk signal."
        ),
        'fatf_ref': (
            "Provides contextual support for risk assessments within a FATF "
            "R.20 transaction monitoring framework when combined with other "
            "indicators."
        ),
        'uk_ref': (
            "Relevant to ongoing transaction monitoring under MLR 2017 "
            "Regulation 28."
        ),
    },

    'card6_freq': {
        'category': 'Card / Channel Signal',
        'text': (
            "Card category (debit, credit, or prepaid) is atypical in this "
            "transaction context. Prepaid card instruments may present  "
            "distinct fraud and financial-crime risk considerations."
        ),
        'fatf_ref': (
            "Provides contextual information regarding payment-instrument "
            "characteristics and may contribute to broader transaction-risk "
            "assessments when considered alongside other indicators."
        ),
        'uk_ref': (
            "Relevant to ongoing monitoring under MLR 2017 Regulation 28 and "
            "EDD obligations under Regulation 33."
        ),
    },

    # -----------------------------------------------------------------------
    # Product category dummies (prod_C/H/R/S/W)
    # IEEE-CIS ProductCD column one-hot encoded.
    # Exact product definitions are Vesta-proprietary.
    # Framed as product-category risk signal — consistent with R.20 typology
    # guidance on product-specific fraud patterns.
    # -----------------------------------------------------------------------

    'prod_C': {
        'category': 'Product / Merchant Category',
        'text': (
            "Transaction belongs to a specific product category (C) that "
            "carries a distinct risk profile in the historical fraud "
            "distribution. Product category is a recognised stratification "
            "variable in transaction monitoring frameworks."
        ),
        'fatf_ref': (
            "Contributes to risk stratification supporting FATF R.20 "
            "transaction monitoring. Product-category-specific fraud "
            "patterns are a recognised typology dimension."
        ),
        'uk_ref': (
            "Relevant to ongoing monitoring under MLR 2017 Regulation 28 "
            "and FCA SYSC 6.3."
        ),
    },

    'prod_H': {
        'category': 'Product / Merchant Category',
        'text': (
            "Transaction belongs to product category H — a category with "
            "a distinct fraud risk profile in the historical distribution."
        ),
        'fatf_ref': (
            "Contributes to risk stratification supporting FATF R.20 "
            "transaction monitoring."
        ),
        'uk_ref': (
            "Relevant to ongoing monitoring under MLR 2017 Regulation 28."
        ),
    },

    'prod_R': {
        'category': 'Product / Merchant Category',
        'text': (
            "Transaction belongs to product category R — a category with "
            "a distinct fraud risk profile in the historical distribution."
        ),
        'fatf_ref': (
            "Contributes to risk stratification supporting FATF R.20 "
            "transaction monitoring."
        ),
        'uk_ref': (
            "Relevant to ongoing monitoring under MLR 2017 Regulation 28."
        ),
    },

    'prod_S': {
        'category': 'Product / Merchant Category',
        'text': (
            "Transaction belongs to product category S — a category with "
            "a distinct fraud risk profile in the historical distribution."
        ),
        'fatf_ref': (
            "Contributes to risk stratification supporting FATF R.20 "
            "transaction monitoring."
        ),
        'uk_ref': (
            "Relevant to ongoing monitoring under MLR 2017 Regulation 28."
        ),
    },

    'prod_W': {
        'category': 'Product / Merchant Category',
        'text': (
            "Transaction belongs to product category W — a category with "
            "a distinct fraud risk profile in the historical distribution."
        ),
        'fatf_ref': (
            "Contributes to risk stratification supporting FATF R.20 "
            "transaction monitoring."
        ),
        'uk_ref': (
            "Relevant to ongoing monitoring under MLR 2017 Regulation 28."
        ),
    },

    # -----------------------------------------------------------------------
    # Device and channel
    # -----------------------------------------------------------------------

    'is_mobile': {
        'category': 'Device / Network',
        'text': (
            "Transaction initiated via a mobile device. Mobile channel access "
            "patterns are monitored to support channel-specific risk assessments."
        ),
        'fatf_ref': (
            "Provides contextual information regarding the transaction access "
            "channel and may contribute to broader technology and operational "
            "risk assessments."
        ),
        'uk_ref': (
            "Relevant to FCA SYSC 6.3 and technology risk assessment "
            "obligations under MLR 2017 Regulation 18."
        ),
    },

    'DeviceType': {
        'category': 'Device / Network',
        'text': (
            "Device type presents a channel risk signal contributing to the "
            "overall transaction risk assessment."
        ),
        'fatf_ref': (
            "Provides contextual information regarding the transaction channel "
            "and device environment, which may contribute to broader risk "
            "assessment activities."
        ),
        'uk_ref': (
            "Relevant to MLR 2017 Regulation 18 and FCA SYSC 6.3."
        ),
    },

    # -----------------------------------------------------------------------

    '_default': {
        'category': 'General Risk Signal',
        'text': (
            "This feature contributed a risk signal to the model's assessment. "
            "Analysts should review in the context of the full transaction profile."
        ),
        'fatf_ref': (
            "May contribute to monitoring considerations under the firm's "
            "risk-based AML programme, consistent with FATF R.1 "
            "(Risk-Based Approach)."
        ),
        'uk_ref': (
            "Relevant to MLR 2017 Regulation 28 ongoing monitoring obligations."
        ),
    },
}


# ---------------------------------------------------------------------------
# FAMILY_MAP — prefix-level fallbacks for anonymised IEEE-CIS feature families
# ---------------------------------------------------------------------------
# Why families and not individual C1/C2/.../C14 entries:
#   Vesta's exact definitions are proprietary and undocumented.
#   Individual per-feature mappings would imply precision that cannot be verified.
#   Family-level mappings reflect functional interpretation supported by the
#   published IEEE-CIS benchmark literature.
#
# Interview answer:
#   "IEEE-CIS anonymizes these variables. Rather than inventing meanings I
#    cannot verify, I mapped feature families to behavioral concepts supported
#    by the benchmark paper. That is a more defensible approach."

FAMILY_MAP: Dict[str, Dict[str, str]] = {

    # C1-C14: counting features (identity / account association)
    # Official dataset description: "counting, such as how many addresses are
    # found to be associated with the payment card. Actual meaning masked."
    'C': {
        'category': 'Identity Association',
        'text': (
            "This signal relates to counts of addresses or other entities "
            "associated with this payment card. Anomalous association counts "
            "may indicate elevated identity-linkage risk, informing ongoing "
            "monitoring considerations associated with FATF Recommendation 10."
        ),
        'fatf_ref': (
            "Contributes to monitoring considerations associated with FATF "
            "R.10 (Customer Due Diligence). Anomalous counts of linked "
            "identities or addresses are an identity-association typology "
            "indicator in FATF guidance."
        ),
        'uk_ref': (
            "Relevant to CDD and ongoing monitoring obligations under "
            "MLR 2017 Regulation 28."
        ),
    },

    # D1-D15: time-delta features (behavioral recency)
    # Official dataset description: "timedelta, such as days between previous transaction"
    'D': {
        'category': 'Behavioral Timing',
        'text': (
            "This signal reflects a time delta associated with this card or "
            "account — such as the number of days since a previous transaction. "
            "A deviation from the customer's established transaction frequency "
            "pattern is a recognised anomaly indicator in transaction monitoring."
        ),
        'fatf_ref': (
            "Supports transaction-monitoring assessments that may contribute "
            "to transaction-monitoring and risk-assessment activities associated "
            "with FATF Recommendation 20. Deviations from established "
            "behavioural recency patterns are a recognised anomaly-detection "
            "indicator."
        ),
        'uk_ref': (
            "Relevant to ongoing monitoring obligations under MLR 2017 "
            "Regulation 28(11) and FCA SYSC 6.3."
        ),
    },

    # M1-M9: match/consistency flags
    # Official dataset description: "match, such as names on card and address"
    'M': {
        'category': 'Attribute Consistency',
        'text': (
            "This signal reflects a match or mismatch between identity "
            "attributes associated with this transaction — such as names "
            "on the card versus the billing address. Inconsistencies of "
            "this type may indicate elevated identity verification risk "
            "warranting further review."
        ),
        'fatf_ref': (
            "Contributes to monitoring considerations associated with FATF "
            "R.10 (Customer Due Diligence). Attribute-consistency "
            "discrepancies are cited as identity-risk indicators in FATF "
            "typology guidance."
        ),
        'uk_ref': (
            "Relevant to CDD and EDD obligations under MLR 2017 "
            "Regulations 28 and 33."
        ),
    },

    # id_01-id_38 (numeric) and id_XX_freq (frequency-encoded):
    # both start with 'id_' so one family entry covers both patterns
    'id_': {
        'category': 'Device / Network',
        'text': (
            "This signal relates to device or network identity attributes "
            "associated with the transaction (e.g. browser, OS, or network "
            "fingerprint characteristics). Atypical attributes may indicate "
            "elevated channel risk."
        ),
        'fatf_ref': (
            "Provides contextual information regarding device and network "
            "characteristics that may contribute to broader technology, "
            "channel-risk, and transaction-monitoring assessments."
        ),
        'uk_ref': (
            "Relevant to MLR 2017 Regulation 18 (risk assessment) and "
            "FCA SYSC 6.3."
        ),
    },

    # addr1, addr2: billing region / country
    'addr': {
        'category': 'Geographic / Location Signal',
        'text': (
            "This signal relates to the billing address region or country "
            "associated with this card. Atypical or mismatched location "
            "attributes may indicate elevated geographic or identity risk."
        ),
        'fatf_ref': (
            "Contributes to monitoring considerations associated with FATF "
            "R.10 (Customer Due Diligence) in relation to address "
            "verification, and geographic risk assessment under FATF R.1."
        ),
        'uk_ref': (
            "Relevant to CDD obligations under MLR 2017 Regulation 28 and "
            "geographic risk factors under Regulation 33."
        ),
    },

    # dist1, dist2: distance metrics between addresses
    'dist': {
        'category': 'Geographic / Location Signal',
        'text': (
            "This signal reflects a distance metric between addresses "
            "associated with this transaction. An unusually large distance "
            "may indicate a delivery or identity mismatch risk."
        ),
        'fatf_ref': (
            "Contributes to monitoring considerations associated with FATF "
            "R.10 (Customer Due Diligence), as geographic distance between "
            "identity attributes is a recognised mismatch indicator."
        ),
        'uk_ref': (
            "Relevant to ongoing monitoring obligations under MLR 2017 "
            "Regulation 28."
        ),
    },
}


# ---------------------------------------------------------------------------
# Resolver
# ---------------------------------------------------------------------------

def _resolve_narrative(feat: str) -> Dict[str, str]:
    """
    Three-tier resolution:

    Tier 1 — Exact match in NARRATIVE_MAP
      Engineered features, card freq columns, uid stats, prod dummies,
      device flags, identity flags.

    Tier 2 — Family prefix in FAMILY_MAP
      id_*   → Device / Network       (covers id_01..id_32 AND id_XX_freq)
      addr*  → Geographic
      dist*  → Geographic
      C[digit+] → Identity Association  (digit guard excludes card1_amt_mean etc.)
      D[digit+] → Behavioral Timing
      M[digit+] → Attribute Consistency

    Tier 3 — _default fallback

    Digit guard detail:
      'C13'[1:]         = '13'   isdigit() True  → C-family  ✓
      'card1_amt_mean'  lowercase 'c'             → no match  ✓
      'card6_freq'      lowercase 'c'             → no match  ✓
    """
    # Tier 1
    if feat in NARRATIVE_MAP:
        return NARRATIVE_MAP[feat]

    # Tier 2 — longer/more specific prefixes first
    if feat.startswith('id_'):
        return FAMILY_MAP['id_']
    if feat.startswith('addr'):
        return FAMILY_MAP['addr']
    if feat.startswith('dist'):
        return FAMILY_MAP['dist']

    if len(feat) >= 2 and feat[0] == 'C' and feat[1:].isdigit():
        return FAMILY_MAP['C']
    if len(feat) >= 2 and feat[0] == 'D' and feat[1:].isdigit():
        return FAMILY_MAP['D']
    if len(feat) >= 2 and feat[0] == 'M' and feat[1:].isdigit():
        return FAMILY_MAP['M']

    # Tier 3
    return NARRATIVE_MAP['_default']


# ---------------------------------------------------------------------------
# Risk tier
# ---------------------------------------------------------------------------

def get_fraud_risk_tier(fraud_prob: float) -> dict:
    """
    HIGH     >= 0.75 : Auto-escalation, SAR drafting initiated.
    ELEVATED 0.40-0.74: Analyst review required.
    LOW      < 0.40  : Standard monitoring continues.

    Re-evaluate thresholds against Week 2 operating point. Document rationale.
    """
    if fraud_prob >= 0.75:
        return {
            'tier':       'HIGH RISK',
            'action':     'ESCALATE — Enhanced analyst investigation required. '
          'Review transaction context and supporting evidence.',
            'color_code': 'RED',
        }
    elif fraud_prob >= 0.40:
        return {
            'tier':       'ELEVATED RISK',
            'action':     'REVIEW — Analyst assessment required. '
          'Further investigation may be warranted based on transaction context.',
            'color_code': 'AMBER',
        }
    else:
        return {
            'tier':       'LOW RISK',
            'action':     'MONITOR — No immediate action required. '
                          'Continue standard transaction monitoring.',
            'color_code': 'GREEN',
        }


# ---------------------------------------------------------------------------
# SHAP narrative extraction
# ---------------------------------------------------------------------------

def get_shap_narratives(
    shap_values_row: list,
    feature_names: list,
    top_n: int = 5
) -> List[Dict]:
    """
    Extract top SHAP contributors and translate to compliance-annotated narratives.

    Returns list of dicts sorted by abs_impact descending:
        feature, category, shap_value, direction,
        narrative, fatf_ref, uk_ref, abs_impact
    """
    impacts = []
    for i, feat in enumerate(feature_names):
        val     = float(shap_values_row[i])
        mapping = _resolve_narrative(feat)
        impacts.append({
            'feature':    feat,
            'category':   mapping['category'],
            'shap_value': round(val, 5),
            'direction':  'increases fraud risk' if val > 0 else 'reduces fraud risk',
            'narrative':  mapping['text'],
            'fatf_ref':   mapping['fatf_ref'],
            'uk_ref':     mapping['uk_ref'],
            'abs_impact': abs(val),
        })

    impacts.sort(key=lambda x: x['abs_impact'], reverse=True)
    return impacts[:top_n]


# ---------------------------------------------------------------------------
# Full SHAP dict — flows to SAR drafter (Day 17) and audit log (Week 4)
# ---------------------------------------------------------------------------

def build_shap_dict(
    transaction_id: str,
    fraud_prob: float,
    shap_values_row: list,
    feature_names: list
) -> dict:
    """
    Authoritative SHAP explanation artefact for one transaction.
    Consumed by: build_sar_prompt() (Day 17), /predict API response (Week 4),
                 PostgreSQL audit log (Week 4).

    Keys:
        transaction_id : str
        fraud_score    : float
        risk_tier      : dict  (tier, action, color_code)
        risk_themes    : list[str]  unique categories in SHAP rank order
                         → used as SAR section headers by Day 17 drafter
        top_features   : list[dict] → see get_shap_narratives()
    """
    top_features = get_shap_narratives(shap_values_row, feature_names, top_n=5)
    risk_themes  = list(dict.fromkeys(f['category'] for f in top_features))

    return {
        'transaction_id': transaction_id,
        'fraud_score':    round(float(fraud_prob), 4),
        'risk_tier':      get_fraud_risk_tier(fraud_prob),
        'risk_themes':    risk_themes,
        'top_features':   top_features,
    }


# ---------------------------------------------------------------------------
# Unit test — run before Day 17
# ---------------------------------------------------------------------------

if __name__ == '__main__':

    FEAT_COLS = [
        'hour', 'day_of_week', 'log_amount', 'amount_to_card_mean',
        'email_domain_mismatch', 'purchaser_email_risk', 'p_email_freq',
        'is_mobile', 'has_identity', 'card2_freq', 'card3_freq', 'card4_freq',
        'card5_freq', 'card6_freq', 'uid_count', 'uid_amt_mean', 'uid_amt_std',
        'uid_amt_zscore', 'card1_amt_mean', 'amt_to_card1_mean',
        'prod_C', 'prod_H', 'prod_R', 'prod_S', 'prod_W',
        'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10',
        'C11', 'C12', 'C13', 'C14',
        'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9', 'D10',
        'D11', 'D12', 'D13', 'D14', 'D15',
        'M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8', 'M9',
        'dist1', 'dist2', 'addr1', 'addr2',
        'id_01', 'id_02', 'id_03', 'id_04', 'id_05', 'id_06', 'id_07',
        'id_08', 'id_09', 'id_10', 'id_11', 'id_13', 'id_14', 'id_17',
        'id_18', 'id_19', 'id_20', 'id_21', 'id_22', 'id_24', 'id_25',
        'id_26', 'id_32',
        'id_12_freq', 'id_15_freq', 'id_16_freq', 'id_23_freq', 'id_27_freq',
        'id_28_freq', 'id_29_freq', 'id_30_freq', 'id_31_freq', 'id_33_freq',
        'id_34_freq', 'id_35_freq', 'id_36_freq', 'id_37_freq', 'id_38_freq',
    ]

    print(f"=== Full feat_cols coverage check ({len(FEAT_COLS)} features) ===\n")

    default_hits = []
    category_counts: Dict[str, int] = {}

    for f in FEAT_COLS:
        m = _resolve_narrative(f)
        cat = m['category']
        category_counts[cat] = category_counts.get(cat, 0) + 1
        if cat == 'General Risk Signal':
            default_hits.append(f)
            print(f"  DEFAULT: {f}")

    print()
    if default_hits:
        print(f"WARNING: {len(default_hits)} feature(s) still hitting _default:")
        for f in default_hits:
            print(f"  - {f}")
    else:
        print(f"✓ Zero features falling to _default across all {len(FEAT_COLS)} features.")

    print("\nCategory distribution:")
    for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        print(f"  {count:>3}  {cat}")

    print("\n=== Digit guard sanity check ===\n")
    guard_tests = {
        'C13':            'Identity Association',
        'D2':             'Behavioral Timing',
        'M5':             'Attribute Consistency',
        'id_01':          'Device / Network',
        'id_12_freq':     'Device / Network',
        'card1_amt_mean': 'Transaction Amount Anomaly',
        'card6_freq':     'Card / Channel Signal',
        'uid_count':      'Identity Association',
        'prod_W':         'Product / Merchant Category',
        'has_identity':   'Device / Network',
        'uid_amt_zscore': 'Transaction Amount Anomaly',
    }
    all_pass = True
    for feat, expected in guard_tests.items():
        actual = _resolve_narrative(feat)['category']
        status = '✓' if actual == expected else '✗'
        if actual != expected:
            all_pass = False
        print(f"  {status} {feat:<22} expected={expected:<32} got={actual}")

    print()
    print("All guard tests passed." if all_pass else "GUARD TESTS FAILED — fix before Day 17.")