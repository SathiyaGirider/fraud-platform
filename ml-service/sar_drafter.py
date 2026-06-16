# sar_drafter.py
# SAR narrative drafter with compliance escalation injection
# UK AML / FATF / POCA 2002 framing — DRAFT ONLY, NOT LEGAL ADVICE


from __future__ import annotations
import os
import logging
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Compliance escalation blocks — deterministic, NOT LLM-generated
# ---------------------------------------------------------------------------

_ESCALATION_BLOCK_HIGH_RISK = """
AUTOMATED ESCALATION NOTICE — FOR ANALYST REVIEW:

This transaction has been flagged at HIGH RISK tier by the automated detection \
system. This output represents an automated escalation for human analyst review \
to determine whether a disclosure to the UK Financial Intelligence Unit (UKFIU) \
within the National Crime Agency (NCA) is required.

Under the Proceeds of Crime Act 2002 (POCA 2002), Section 330, individuals \
working in the regulated sector who know or suspect that another person is \
engaged in money laundering are required to make a disclosure to their \
nominated officer as soon as is practicable. Failure to disclose where \
suspicion has been formed may constitute a criminal offence under POCA 2002.

IMPORTANT: This automated system does not confirm that money laundering has \
occurred and does not constitute a legal determination. It serves as an \
operational decision-support layer to assist compliance analysts in their \
assessment. The decision to escalate a matter for SAR consideration and any \
subsequent SAR submission rests solely with the authorised nominated officer \
and the firm's established compliance procedures.

Analyst action required: Review this transaction and all associated account \
history. Escalate to the nominated officer as soon as is practicable if \
suspicion is formed or cannot be ruled out.
"""

_ESCALATION_BLOCK_ELEVATED_RISK = """
ANALYST REVIEW REQUIRED:

This transaction has been flagged at ELEVATED RISK tier by the automated \
detection system. An analyst should review this case in full before a \
determination is made regarding escalation. If, following review, suspicion \
of money laundering is formed and cannot be adequately resolved, the case \
should be escalated to the nominated officer in accordance with the firm's \
AML procedures and POCA 2002 Section 330 obligations.

IMPORTANT: This automated system does not confirm that money laundering has \
occurred and does not constitute a legal determination. It serves as an \
operational decision-support layer to assist compliance analysts in their \
assessment.
"""


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

def build_sar_prompt(shap_dict: dict) -> str:
    score    = shap_dict.get('fraud_score', 0.0)
    tier_info = shap_dict.get('risk_tier', {})
    tier     = tier_info.get('tier', 'UNKNOWN')
    action   = tier_info.get('action', '')
    features = shap_dict.get('top_features', [])
    themes   = shap_dict.get('risk_themes', [])

    risk_factor_lines = [
        f"- {f['narrative']}"
        for f in features
        if f.get('shap_value', 0) > 0
    ]
    if not risk_factor_lines:
        risk_factor_lines = ["- No dominant risk-increasing factors identified."]

    themes_str = (
        f"Risk theme areas: {', '.join(themes)}" if themes
        else "Risk theme areas: General"
    )

    prompt = f"""You are a fraud compliance analyst drafting an investigation brief.

Transaction ID    : {shap_dict.get('transaction_id', 'UNKNOWN')}
Fraud Risk Score  : {score:.3f} (scale 0.000–1.000)
Risk Tier         : {tier}
Recommended Action: {action}
{themes_str}

Key risk factors identified by the automated detection system:
{chr(10).join(risk_factor_lines)}

Draft a concise investigation brief (3–5 sentences) that:
1. States the fraud risk tier and overall risk assessment clearly
2. Describes the specific risk patterns in plain analyst language — do not use \
feature names with underscores, model terminology, or SHAP jargon
3. Notes combinations of factors that are particularly significant together
4. States the recommended next action for the analyst

Rules:
- Write only the investigation brief prose. No preamble. No bullet points. \
No headings. Plain paragraph prose only.
- Do not mention model names, SHAP, XGBoost, Random Forest, or any ML terms.
- Do not fabricate information not present in the risk factors above.
- Do not assert "this transaction is suspicious" as a bare claim — describe \
the specific indicators and why they are noteworthy.
- Language must be professional and appropriate for a compliance file."""

    return prompt


# ---------------------------------------------------------------------------
# Narrative fallback — used when Groq is unavailable, key missing, or empty response
# ---------------------------------------------------------------------------

def _build_fallback_brief(tier: str, features: list) -> str:
    """
    Constructs a rule-based investigation brief from SHAP narratives directly.
    Used when the Groq LLM call fails, the API key is missing, or returns an
    empty response.

    Interview framing: "The LLM is an enhancement layer, not a dependency.
    Core fraud scoring and compliance escalation continue even if narrative
    generation fails."
    """
    risk_narratives = [
        f['narrative']
        for f in features
        if f.get('shap_value', 0) > 0
    ]

    if risk_narratives:
        indicators = "; ".join(risk_narratives)[:500]
        return (
            f"This transaction has been classified as {tier}. "
            f"Primary risk indicators include: {indicators}. "
            "Analyst review is required to determine appropriate next steps."
        )
    return (
        f"This transaction has been classified as {tier}. "
        "No dominant risk-increasing factors were identified by the automated system. "
        "Analyst review is required to confirm this assessment."
    )


# ---------------------------------------------------------------------------
# Main drafter
# ---------------------------------------------------------------------------

def draft_sar_narrative(shap_dict: dict) -> dict:
    """
    Generate a complete SAR narrative from a shap_dict.

    Returns:
        investigation_brief : LLM-generated prose, or rule-based fallback
        compliance_notice   : deterministic escalation block, or None for LOW RISK
        risk_tier           : tier string
        full_narrative      : combined string for display and audit logging
        llm_model           : model name used (aids audit log on Day 23+)
        narrative_source    : 'llm' | 'fallback' — lets audit log record which path ran
    """
    tier     = shap_dict.get('risk_tier', {}).get('tier', 'LOW RISK')
    features = shap_dict.get('top_features', [])

    LLM_MODEL = 'llama-3.3-70b-versatile'
    narrative_source = 'llm'

    try:
        # API key validation now lives inside the try block — a missing key
        # is treated the same as any other LLM-unavailable condition and
        # falls through to the rule-based brief, rather than crashing the
        # whole request. The LLM is an enhancement layer, not a dependency.
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not configured. "
                "Set it in your .env file and ensure load_dotenv() runs at startup."
            )

        llm = ChatGroq(
            model=LLM_MODEL,
            temperature=0.2,
            max_tokens=400,
            api_key=api_key
        )

        system_prompt = (
            "You are a senior compliance analyst writing fraud investigation briefs "
            "for a financial institution's AML team. Write in clear, professional, "
            "non-technical language. Be precise and concise. Do not fabricate "
            "information. Do not use ML or statistical terminology."
        )

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=build_sar_prompt(shap_dict)),
        ]

        response = llm.invoke(messages)

        investigation_brief = (
            response.content.strip()
            if response and response.content
            else None
        )

        if not investigation_brief:
            raise ValueError("Groq returned an empty response.")

    except Exception as e:
        # Missing API key, Groq outage, rate limit, empty response — all fall
        # back to the rule-based brief instead of raising.
        logger.warning(f"[sar_drafter] LLM call failed: {e}. Using fallback brief.", exc_info=True)
        investigation_brief = _build_fallback_brief(tier, features)
        narrative_source = 'fallback'
        LLM_MODEL = 'none'

    # Deterministic compliance block — always injected regardless of LLM path
    if tier == 'HIGH RISK':
        compliance_notice = _ESCALATION_BLOCK_HIGH_RISK.strip()
    elif tier == 'ELEVATED RISK':
        compliance_notice = _ESCALATION_BLOCK_ELEVATED_RISK.strip()
    else:
        compliance_notice = None

    full_narrative = (
        f"{investigation_brief}\n\n{'-' * 60}\n{compliance_notice}"
        if compliance_notice
        else investigation_brief
    )

    return {
        'investigation_brief': investigation_brief,
        'compliance_notice':   compliance_notice,
        'risk_tier':           tier,
        'full_narrative':      full_narrative,
        'llm_model':           LLM_MODEL,
        'narrative_source':    narrative_source,
    }
