"""
priority_engine.py — Combine patient risk + community vulnerability
                      into a single priority score and tier.

Formula:
    combined_score = ALPHA * risk_score + BETA * vulnerability_score
    (ALPHA=0.60, BETA=0.40)

Tiers:
    CRITICAL  ≥ 75
    HIGH      55 – 74
    MEDIUM    35 – 54
    LOW        0 – 34
"""

import pandas as pd
import numpy as np
from config import ALPHA, BETA, TIER_PERCENTILES, TIER_ACTIONS, TIER_EMOJIS


def _compute_thresholds(scores: pd.Series) -> dict[str, float]:
    """Derive absolute score thresholds from percentile targets."""
    return {
        tier: float(np.percentile(scores, pct))
        for tier, pct in TIER_PERCENTILES.items()
        if pct > 0
    }


def _assign_tier(score: float, thresholds: dict[str, float]) -> tuple[str, str, str]:
    if score >= thresholds.get("CRITICAL", float("inf")):
        tier = "CRITICAL"
    elif score >= thresholds.get("HIGH", float("inf")):
        tier = "HIGH"
    elif score >= thresholds.get("MEDIUM", float("inf")):
        tier = "MEDIUM"
    else:
        tier = "LOW"
    return tier, TIER_EMOJIS[tier], TIER_ACTIONS[tier]


def compute_priorities(master_scored: pd.DataFrame,
                       community_scored: pd.DataFrame) -> pd.DataFrame:
    """
    Parameters
    ----------
    master_scored   : output of patient_scorer.score_patients()
    community_scored: output of community_scorer.score_communities()

    Returns
    -------
    DataFrame sorted by combined_score descending, one row per patient.
    """
    # Attach community vulnerability score
    comm_cols = ["chsa_code", "vulnerability_score", "vulnerability_tier"]
    df = master_scored.merge(
        community_scored[comm_cols], on="chsa_code", how="left"
    )

    # Fill missing vulnerability (shouldn't happen, but be safe)
    df["vulnerability_score"] = df["vulnerability_score"].fillna(
        community_scored["vulnerability_score"].mean()
    )

    # Combined score
    df["combined_score"] = (
        ALPHA * df["risk_score"] + BETA * df["vulnerability_score"]
    ).round(1)

    # Percentile-based tier thresholds (calibrated to this dataset)
    thresholds = _compute_thresholds(df["combined_score"])

    # Tier assignment
    tier_tuples = df["combined_score"].apply(lambda s: _assign_tier(s, thresholds))
    df["priority_tier"]   = tier_tuples.apply(lambda t: t[0])
    df["priority_emoji"]  = tier_tuples.apply(lambda t: t[1])
    df["priority_action"] = tier_tuples.apply(lambda t: t[2])

    # Tier ordering for sorting
    tier_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    df["tier_rank"] = df["priority_tier"].map(tier_order)

    df = df.sort_values(["tier_rank", "combined_score"],
                        ascending=[True, False]).reset_index(drop=True)

    return df, thresholds


def summary_stats(priority_df: pd.DataFrame, thresholds: dict | None = None) -> dict:
    """Return dashboard-level summary stats."""
    total = len(priority_df)
    counts = priority_df["priority_tier"].value_counts().to_dict()
    return {
        "total_patients": total,
        "critical": counts.get("CRITICAL", 0),
        "high":     counts.get("HIGH",     0),
        "medium":   counts.get("MEDIUM",   0),
        "low":      counts.get("LOW",      0),
        "pct_no_family_doctor": priority_df["pct_without_family_doctor"].mean(),
        "avg_risk_score":       priority_df["risk_score"].mean(),
        "avg_combined_score":   priority_df["combined_score"].mean(),
    }


# ── Cohort outcome metrics ────────────────────────────────────────────────────

# Average cost of a non-admitted ED visit in BC (CAD), conservative estimate
ED_VISIT_COST_CAD = 500
# Assumed reduction in ED revisits if patient is connected to proactive care
OUTREACH_EFFECTIVENESS = 0.30


def cohort_outcomes(priority_df: pd.DataFrame) -> dict:
    """
    Compute actionable cohort-level metrics for the outcome panel.
    Focuses on CRITICAL + HIGH patients.
    """
    hp = priority_df[priority_df["priority_tier"].isin(["CRITICAL", "HIGH"])]
    total_hp = len(hp)

    no_gp = int((hp["pct_without_family_doctor"] >= 20).sum()) if total_hp else 0
    repeat_ed = int((hp["ed_visits_12m"] >= 3).sum()) if total_hp else 0
    diabetics_no_fu = int(
        (hp["hba1c_elevated"] & hp["no_followup"]).sum()
    ) if total_hp else 0

    # Estimated preventable ED visits for the whole high-priority cohort
    preventable_visits = int((hp["ed_visits_12m"] * OUTREACH_EFFECTIVENESS).sum())
    preventable_cost = preventable_visits * ED_VISIT_COST_CAD

    return {
        "high_priority_count":      total_hp,
        "hp_no_family_doctor":      no_gp,
        "hp_repeat_ed":             repeat_ed,
        "hp_diabetics_overdue":     diabetics_no_fu,
        "preventable_ed_visits":    preventable_visits,
        "preventable_cost_cad":     preventable_cost,
    }


# ── Intervention simulator ────────────────────────────────────────────────────

def simulate_intervention(priority_df: pd.DataFrame,
                          n_outreach: int) -> dict:
    """
    Given capacity to outreach `n_outreach` patients this week,
    recommend the optimal patient mix and estimate impact.

    Picks top N by combined_score (already sorted).
    """
    reached = priority_df.head(n_outreach).copy()
    total   = len(priority_df)

    # Community distribution
    comm_dist = (
        reached.groupby("chsa_name")["patient_id"]
        .count()
        .reset_index()
        .rename(columns={"patient_id": "patients"})
        .sort_values("patients", ascending=False)
    )

    # Tier breakdown of reached patients
    tier_dist = reached["priority_tier"].value_counts().to_dict()

    # Estimated avoided ED visits (per year)
    avoided_visits = int((reached["ed_visits_12m"] * OUTREACH_EFFECTIVENESS).sum())
    avoided_cost   = avoided_visits * ED_VISIT_COST_CAD

    # Key conditions covered
    conditions = []
    if reached["hba1c_elevated"].sum() > 0:
        conditions.append(f"{int(reached['hba1c_elevated'].sum())} uncontrolled diabetics")
    if reached["left_ama"].sum() > 0:
        conditions.append(f"{int(reached['left_ama'].sum())} AMA-history patients")
    if reached["has_wait_burden"].sum() > 0:
        conditions.append(f"{int(reached['has_wait_burden'].sum())} awaiting long-wait procedures")

    return {
        "n_reached":        n_outreach,
        "pct_of_cohort":    round(n_outreach / total * 100, 1),
        "comm_distribution": comm_dist,
        "tier_distribution": tier_dist,
        "avoided_ed_visits": avoided_visits,
        "avoided_cost_cad":  avoided_cost,
        "key_conditions":    conditions,
        "avg_risk_score":    round(reached["risk_score"].mean(), 1),
        "avg_combined_score": round(reached["combined_score"].mean(), 1),
    }


# ── Community scenario simulator ──────────────────────────────────────────────

def simulate_community_scenario(
    priority_df: pd.DataFrame,
    comm_scores: pd.DataFrame,
    chsa_code: int,
    attachment_improvement_pct: float,
) -> dict:
    """
    What-if: if community `chsa_code` improves primary care attachment by
    `attachment_improvement_pct` percentage points, how does the priority
    landscape change for patients in that community?

    Mechanically: lower pct_without_family_doctor → recalculate vulnerability →
    recalculate combined_score → compare tier distribution before/after.
    """
    comm_row = comm_scores[comm_scores["chsa_code"] == chsa_code].iloc[0]
    community_name = comm_row["chsa_name"]

    # Current state
    current_unattached = comm_row["pct_without_family_doctor"]
    current_vuln       = comm_row["vulnerability_score"]

    # Scenario: reduce unattached rate
    new_unattached = max(0, current_unattached - attachment_improvement_pct)

    # Recalculate vulnerability for this one community
    # We need the original community df to re-normalise properly.
    # Shortcut: linearly interpolate the change proportionally.
    # pct_without_family_doctor has weight 0.30 in the vulnerability score.
    # Vulnerability is 0-100 scaled, so a change in the raw indicator maps to:
    #   delta_vuln ≈ (delta_raw / range_of_raw) * weight * 100
    from config import COMMUNITY_WEIGHTS
    full_range = comm_scores["pct_without_family_doctor"].max() - comm_scores["pct_without_family_doctor"].min()
    if full_range > 0:
        delta_norm = (attachment_improvement_pct / full_range)
        delta_vuln = delta_norm * COMMUNITY_WEIGHTS["pct_without_family_doctor"] * 100
    else:
        delta_vuln = 0

    new_vuln = max(0, current_vuln - delta_vuln)

    # Recalculate combined scores for patients in this community
    patients = priority_df[priority_df["chsa_code"] == chsa_code].copy()
    if patients.empty:
        return {
            "community_name": community_name,
            "n_patients": 0,
            "current_unattached": current_unattached,
            "new_unattached": new_unattached,
            "current_vuln": current_vuln,
            "new_vuln": new_vuln,
            "before_tiers": {},
            "after_tiers": {},
            "tier_shifts": {},
            "avoided_hp": 0,
            "avoided_ed_visits": 0,
            "avoided_cost": 0,
        }

    # Before tiers
    before_tiers = patients["priority_tier"].value_counts().to_dict()

    # After: recalculate combined score with new vulnerability
    patients["new_combined"] = (
        ALPHA * patients["risk_score"] + BETA * new_vuln
    ).round(1)

    # Re-derive thresholds from the FULL population (not just this community)
    # We use the existing global thresholds for consistency
    full_thresholds = _compute_thresholds(priority_df["combined_score"])

    def _tier_from_score(s):
        if s >= full_thresholds.get("CRITICAL", float("inf")):
            return "CRITICAL"
        elif s >= full_thresholds.get("HIGH", float("inf")):
            return "HIGH"
        elif s >= full_thresholds.get("MEDIUM", float("inf")):
            return "MEDIUM"
        return "LOW"

    patients["new_tier"] = patients["new_combined"].apply(_tier_from_score)
    after_tiers = patients["new_tier"].value_counts().to_dict()

    # Tier shifts
    tier_order = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
    shifts = (
        patients["priority_tier"].map(tier_order).values
        - patients["new_tier"].map(tier_order).values
    )
    n_improved = int((shifts > 0).sum())
    n_unchanged = int((shifts == 0).sum())

    # Patients moving out of CRITICAL+HIGH
    before_hp = int(patients["priority_tier"].isin(["CRITICAL", "HIGH"]).sum())
    after_hp  = int(patients["new_tier"].isin(["CRITICAL", "HIGH"]).sum())
    avoided_hp = max(0, before_hp - after_hp)

    # Avoided ED visits (rough: patients no longer high-priority × their ED rate × effectiveness)
    improved_patients = patients[
        patients["priority_tier"].isin(["CRITICAL", "HIGH"]) &
        ~patients["new_tier"].isin(["CRITICAL", "HIGH"])
    ]
    avoided_ed = int((improved_patients["ed_visits_12m"] * OUTREACH_EFFECTIVENESS).sum())

    return {
        "community_name":      community_name,
        "n_patients":          len(patients),
        "current_unattached":  round(current_unattached, 1),
        "new_unattached":      round(new_unattached, 1),
        "current_vuln":        round(current_vuln, 1),
        "new_vuln":            round(new_vuln, 1),
        "before_tiers":        before_tiers,
        "after_tiers":         after_tiers,
        "n_improved":          n_improved,
        "n_unchanged":         n_unchanged,
        "avoided_hp":          avoided_hp,
        "avoided_ed_visits":   avoided_ed,
        "avoided_cost":        avoided_ed * ED_VISIT_COST_CAD,
    }


if __name__ == "__main__":
    from data_pipeline import load_all
    from patient_scorer import score_patients
    from community_scorer import score_communities

    data = load_all()
    scored     = score_patients(data["master"])
    comm_sc    = score_communities(data["community"])
    priorities, thresholds = compute_priorities(scored, comm_sc)

    print("Tier thresholds:", thresholds)
    print()
    print(priorities[["patient_id", "chsa_name", "risk_score",
                       "vulnerability_score", "combined_score",
                       "priority_tier"]].head(20).to_string())
    print()
    print(summary_stats(priorities))
