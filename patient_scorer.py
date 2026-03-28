"""
patient_scorer.py — Compute per-patient clinical risk score (0–100).

Score breakdown (max points):
  25  ED visit frequency  (past 12 months)
  20  Chronic disease control  (abnormal labs)
  15  Polypharmacy  (active medications)
  15  Left-AMA history
  15  Post-discharge follow-up gap
  10  Language barrier
 ───
 100  Total
"""

import pandas as pd
from config import RISK_MAX


def _ed_score(ed_visits_12m: int) -> tuple[int, str | None]:
    if ed_visits_12m >= 3:
        return RISK_MAX["ed_frequency"], f"{ed_visits_12m} ED visits in past 12 months"
    if ed_visits_12m == 2:
        return round(RISK_MAX["ed_frequency"] * 0.6), "2 ED visits in past 12 months"
    if ed_visits_12m == 1:
        return round(RISK_MAX["ed_frequency"] * 0.3), None
    return 0, None


def _chronic_score(hba1c_elevated: bool,
                   abnormal_chronic_labs: int,
                   troponin_elevated: bool) -> tuple[int, list[str]]:
    pts, flags = 0, []
    if hba1c_elevated:
        pts += 12
        flags.append("Uncontrolled diabetes (HbA1c elevated)")
    if troponin_elevated:
        pts += 8
        flags.append("Elevated troponin — cardiac concern")
    extra = min(abnormal_chronic_labs, 2) * 4   # up to 8 pts for other markers
    pts += extra
    if abnormal_chronic_labs > 0 and not hba1c_elevated:
        flags.append(f"{abnormal_chronic_labs} abnormal chronic-disease lab(s)")
    return min(pts, RISK_MAX["chronic_disease"]), flags


def _poly_score(active_med_count: int) -> tuple[int, str | None]:
    if active_med_count >= 8:
        return RISK_MAX["polypharmacy"], f"High polypharmacy: {active_med_count} active medications"
    if active_med_count >= 5:
        return round(RISK_MAX["polypharmacy"] * 0.6), f"Polypharmacy: {active_med_count} active medications"
    return 0, None


def _ama_score(left_ama: bool) -> tuple[int, str | None]:
    if left_ama:
        return RISK_MAX["left_ama"], "History of leaving against medical advice (AMA)"
    return 0, None


def _followup_score(no_followup: bool, total_admissions: int) -> tuple[int, str | None]:
    if no_followup and total_admissions > 0:
        return RISK_MAX["no_followup"], "Hospital admission(s) without timely outpatient follow-up"
    return 0, None


def _wait_burden_score(has_wait_burden: bool,
                       wait_procedure: str,
                       wait_days_bc: float,
                       pct_without_family_doctor: float) -> tuple[int, str | None]:
    """
    Systemic access barrier: patient needs a long-wait procedure (Track 2 wait times)
    AND lives in a community where getting a referral is hard (no family doctor).
    """
    if not has_wait_burden or not wait_procedure:
        return 0, None
    # Scale: longer wait + worse access = higher score
    access_factor = min(pct_without_family_doctor / 20.0, 1.5)  # normalise around 20%
    pts = min(round(RISK_MAX["wait_burden"] * access_factor), RISK_MAX["wait_burden"])
    flag = (f"Needs {wait_procedure} — BC median wait: {int(wait_days_bc)} days "
            f"(community-level access barrier: {pct_without_family_doctor:.0f}% unattached)")
    return pts, flag


def _language_score(primary_language: str) -> tuple[int, str | None]:
    if str(primary_language).strip().lower() not in ("english", "nan", ""):
        return RISK_MAX["language_barrier"], f"Primary language: {primary_language}"
    return 0, None


# ── Main scorer ───────────────────────────────────────────────────────────────

def score_patients(master: pd.DataFrame) -> pd.DataFrame:
    """
    Add risk_score (0-100) and risk_flags (list[str]) columns to master.
    Returns the enriched DataFrame.
    """
    records = []

    for _, row in master.iterrows():
        total = 0
        flags = []

        # ED frequency
        pts, flag = _ed_score(int(row.get("ed_visits_12m", 0)))
        total += pts
        if flag:
            flags.append(flag)

        # Chronic disease
        pts, f_list = _chronic_score(
            bool(row.get("hba1c_elevated", False)),
            int(row.get("abnormal_chronic_labs", 0)),
            bool(row.get("troponin_elevated", False)),
        )
        total += pts
        flags.extend(f_list)

        # Polypharmacy
        pts, flag = _poly_score(int(row.get("active_med_count", 0)))
        total += pts
        if flag:
            flags.append(flag)

        # Left AMA
        pts, flag = _ama_score(bool(row.get("left_ama", False)))
        total += pts
        if flag:
            flags.append(flag)

        # Follow-up gap
        pts, flag = _followup_score(
            bool(row.get("no_followup", False)),
            int(row.get("total_admissions", 0)),
        )
        total += pts
        if flag:
            flags.append(flag)

        # Wait time burden (Track 2 integration)
        pts, flag = _wait_burden_score(
            bool(row.get("has_wait_burden", False)),
            str(row.get("wait_procedure", "")),
            float(row.get("wait_days_bc", 0)),
            float(row.get("pct_without_family_doctor", 20)),
        )
        total += pts
        if flag:
            flags.append(flag)

        # Language barrier
        pts, flag = _language_score(str(row.get("primary_language", "English")))
        total += pts
        if flag:
            flags.append(flag)

        records.append({
            "patient_id":  row["patient_id"],
            "risk_score":  min(total, 100),
            "risk_flags":  flags,
        })

    scores_df = pd.DataFrame(records)
    return master.merge(scores_df, on="patient_id", how="left")


# ── "Why now?" structured reasoning ──────────────────────────────────────────

# Keywords that map each flag string into one of three reasoning categories.
_CLINICAL_KEYWORDS = [
    "ED visit", "HbA1c", "troponin", "Polypharmacy", "polypharmacy",
    "chronic-disease", "AMA", "follow-up", "abnormal",
]
_ACCESS_KEYWORDS = ["language", "Needs", "wait", "GP to refer"]


def categorize_flags(flags: list[str]) -> dict[str, list[str]]:
    """
    Split a flat list of risk flag strings into structured categories:
      clinical_need, access_barrier  (system_impact added by caller).
    """
    clinical, access = [], []
    for f in flags:
        if any(kw in f for kw in _ACCESS_KEYWORDS):
            access.append(f)
        elif any(kw in f for kw in _CLINICAL_KEYWORDS):
            clinical.append(f)
        else:
            clinical.append(f)       # default bucket
    return {"clinical_need": clinical, "access_barrier": access}


def compute_system_impact(row) -> list[str]:
    """
    Generate system-impact statements based on patient-level data.
    These are *derived*, not stored as flags.
    """
    impacts = []
    ed = int(row.get("ed_visits_12m", 0))
    if ed >= 2:
        impacts.append(
            f"Potentially avoidable ED burden ({ed} visits/yr) if primary care access improves"
        )
    if row.get("no_followup", False) and int(row.get("total_admissions", 0)) > 0:
        impacts.append(
            "Higher 30-day readmission risk due to care continuity gap"
        )
    if row.get("has_wait_burden", False):
        impacts.append(
            "Referral delay compounds procedure wait — prolonged symptom burden"
        )
    if not impacts:
        impacts.append("Lower acute-utilization risk — standard monitoring sufficient")
    return impacts


if __name__ == "__main__":
    from data_pipeline import load_all
    data = load_all()
    scored = score_patients(data["master"])
    print(scored[["patient_id", "risk_score", "risk_flags"]].sort_values(
        "risk_score", ascending=False).head(10).to_string())
