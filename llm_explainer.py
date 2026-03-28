"""
llm_explainer.py — Generate natural-language care rationale via Claude API.

Each call produces a 3-sentence explanation covering:
  1. Patient's clinical risk reasons
  2. Community context that amplifies risk
  3. Specific recommended action

Uses claude-3-5-haiku for speed and cost efficiency.
Results are cached in memory per session.
"""

import os
import anthropic
from config import CLAUDE_MODEL

_client: anthropic.Anthropic | None = None
_cache: dict[str, str] = {}


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic()   # reads ANTHROPIC_API_KEY from env
    return _client


def _build_prompt(row: dict) -> str:
    flags_text = "\n".join(f"  • {f}" for f in row.get("risk_flags", [])) or "  • No specific clinical flags"
    return f"""You are a Canadian primary care AI assistant supporting a care coordinator.
Summarize why this patient is {row['priority_tier']} priority and what action to take.
Write exactly 3 sentences. Be specific, concise, and compassionate. Use plain English (no jargon).

PATIENT:
- Age: {row['age']} | Sex: {row['sex']} | Language: {row['primary_language']}
- Community: {row['chsa_name']} (Island Health, BC)
- Risk score: {row['risk_score']}/100 | Community vulnerability: {row['vulnerability_score']}/100
- Combined priority score: {row['combined_score']}/100

CLINICAL RISK FLAGS:
{flags_text}

COMMUNITY CONTEXT:
  • {row['pct_without_family_doctor']:.1f}% of residents lack a regular family doctor
  • {row['pct_below_poverty_line']:.1f}% live below the poverty line
  • Opioid overdose rate: {row['opioid_overdose_rate']:.1f}/100,000
  • Avg household income: ${row.get('median_household_income', 'N/A'):,}

RECOMMENDED ACTION: {row['priority_action']}

Write the 3-sentence explanation now:"""


def generate_explanation(row: dict) -> str:
    """
    Generate or retrieve cached explanation for a patient row (dict).
    Returns a string with the 3-sentence rationale.
    Falls back to a rule-based summary if the API key is unavailable.
    """
    pid = row.get("patient_id", "unknown")
    if pid in _cache:
        return _cache[pid]

    # Fallback if no API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        explanation = _fallback_explanation(row)
        _cache[pid] = explanation
        return explanation

    try:
        client = _get_client()
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=200,
            messages=[{"role": "user", "content": _build_prompt(row)}],
        )
        explanation = response.content[0].text.strip()
    except Exception as e:
        explanation = _fallback_explanation(row) + f"\n\n_(API error: {e})_"

    _cache[pid] = explanation
    return explanation


def _fallback_explanation(row: dict) -> str:
    """Rule-based fallback when Claude API is unavailable."""
    flags = row.get("risk_flags", [])
    tier  = row.get("priority_tier", "MEDIUM")
    community = row.get("chsa_name", "their community")
    no_gp_pct = row.get("pct_without_family_doctor", 0)

    clinical_summary = (
        "; ".join(flags[:3]) if flags
        else "multiple risk factors identified across clinical records"
    )
    return (
        f"This patient is flagged as {tier} priority based on: {clinical_summary}. "
        f"They reside in {community}, where {no_gp_pct:.0f}% of residents lack a regular "
        f"family doctor, limiting access to proactive primary care. "
        f"Recommended action: {row.get('priority_action', 'Review and follow up')}."
    )


def clear_cache() -> None:
    """Clear the in-memory explanation cache."""
    _cache.clear()
