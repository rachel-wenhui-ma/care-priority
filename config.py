"""
config.py — Global constants, paths, and scoring weights
"""

from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR  = Path(__file__).parent
DATA_DIR  = BASE_DIR.parent / "Source" / "Data Sources for Hackathon" / "hackathon-data"

TRACK1_DIR    = DATA_DIR / "track-1-clinical-ai" / "synthea-patients"
TRACK2_DIR    = DATA_DIR / "track-2-population-health" / "bc-community-profiles"
WAIT_TIMES_CSV = DATA_DIR / "track-2-population-health" / "cihi-wait-times" / "wait_times_mock.csv"
OPIOID_CSV     = DATA_DIR / "track-2-population-health" / "opioid-surveillance" / "opioid_harms_mock.csv"

# ── Geography: FSA → CHSA (BC postal code geography, Greater Victoria area) ──
# Source: BC Stats postal code geography; all Track-1 patients are Island Health
FSA_TO_CHSA = {
    # Greater Victoria — downtown, James Bay, Fairfield, Hillside, Esquimalt
    "V8V": 4101, "V8W": 4101, "V8S": 4101, "V8T": 4101,
    "V8R": 4101, "V9A": 4101,
    # Saanich — Gordon Head, Cedar Hill, Royal Oak, Tillicum
    "V8N": 4102, "V8P": 4102, "V8X": 4102, "V8Z": 4102,
    # Western Communities — Langford, Colwood
    "V9B": 4103, "V9C": 4103,
}

# ── Patient risk score components (max points each, total = 100) ─────────────
RISK_MAX = {
    "ed_frequency":    25,   # repeat ED visits in past 12 months
    "chronic_disease": 20,   # uncontrolled chronic conditions (labs)
    "polypharmacy":    15,   # high active medication count
    "left_ama":        15,   # history of leaving against medical advice
    "no_followup":     10,   # admission without post-discharge outpatient visit
    "wait_burden":     10,   # diagnosis requires long-wait procedure + low primary care access
    "language_barrier": 5,   # non-English primary language
}

# ── Diagnosis → elective procedure mapping (Track 2 wait times integration) ───
# Maps patient diagnoses to CIHI procedure names to look up BC median wait days
DIAGNOSIS_TO_PROCEDURE = {
    "Pain in joint":                  "Knee Replacement",
    "Acute myocardial infarction":    "Cardiac Bypass",
    "Chest pain, unspecified":        "Cardiac Bypass",
    "Cataract":                       "Cataract Surgery",
    "Conjunctivitis":                 "Cataract Surgery",   # proxy
    "Low back pain":                  "MRI Scan",
    "Migraine":                       "MRI Scan",
    "Abdominal pain, unspecified":    "CT Scan",
    "Pneumonia, unspecified":         "CT Scan",
}

# Wait threshold above which it becomes a meaningful access barrier (days)
WAIT_BARRIER_DAYS = 60

# ── Community vulnerability weights (must sum to 1.0) ────────────────────────
COMMUNITY_WEIGHTS = {
    "pct_without_family_doctor":          0.30,
    "pct_below_poverty_line":             0.20,
    "opioid_overdose_rate":               0.15,
    "chronic_disease_burden":             0.15,   # derived: avg(diabetes, hypertension)
    "mental_health_hospitalization_rate": 0.10,
    "er_visits_per_1000":                 0.10,
}

# ── Combined priority blend ───────────────────────────────────────────────────
ALPHA = 0.60   # weight for patient clinical risk
BETA  = 0.40   # weight for community vulnerability

# ── Priority tiers — percentile-based (top % of combined_score) ──────────────
# Thresholds are computed dynamically in priority_engine.compute_priorities()
# based on the actual score distribution. These define the population cut-offs.
TIER_PERCENTILES = {
    "CRITICAL": 95,   # top 5%
    "HIGH":     80,   # 80th–95th percentile
    "MEDIUM":   50,   # 50th–80th percentile
    "LOW":       0,   # bottom 50%
}

TIER_ACTIONS = {
    "CRITICAL": "Proactive outreach within 48 h — care coordinator + social work referral",
    "HIGH":     "Schedule follow-up within 2 weeks — chronic disease or mental health review",
    "MEDIUM":   "Add to care management watchlist — next routine contact",
    "LOW":      "Monitor — standard recall schedule",
}

TIER_EMOJIS = {
    "CRITICAL": "🔴",
    "HIGH":     "🟠",
    "MEDIUM":   "🟡",
    "LOW":      "🟢",
}

# ── Claude model ──────────────────────────────────────────────────────────────
CLAUDE_MODEL = "claude-3-5-haiku-20241022"   # fast + cheap for per-patient explanations
