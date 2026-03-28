"""
data_pipeline.py — Load, clean, and join all Track-1 and Track-2 data.

Public API
----------
load_all() -> dict with keys:
    patients, encounters, vitals, medications, labs, community
    + 'master': one row per patient, with community columns attached
"""

import pandas as pd
import numpy as np
from pathlib import Path
from config import (TRACK1_DIR, TRACK2_DIR, FSA_TO_CHSA,
                    WAIT_TIMES_CSV, OPIOID_CSV,
                    DIAGNOSIS_TO_PROCEDURE, WAIT_BARRIER_DAYS)


# ── Loaders ──────────────────────────────────────────────────────────────────

def _load_track1() -> dict[str, pd.DataFrame]:
    patients   = pd.read_csv(TRACK1_DIR / "patients.csv")
    encounters = pd.read_csv(TRACK1_DIR / "encounters.csv",
                             parse_dates=["encounter_date"])
    vitals     = pd.read_csv(TRACK1_DIR / "vitals.csv")
    medications = pd.read_csv(TRACK1_DIR / "medications.csv",
                              parse_dates=["start_date", "end_date"])
    labs       = pd.read_csv(TRACK1_DIR / "lab_results.csv",
                             parse_dates=["collected_date"])
    return dict(patients=patients, encounters=encounters,
                vitals=vitals, medications=medications, labs=labs)


def _load_track2() -> dict:
    """Load all three Track-2 datasets."""
    bc = pd.read_csv(TRACK2_DIR / "bc_health_indicators.csv")
    bc["chronic_disease_burden"] = (bc["diabetes_prevalence"] + bc["hypertension_prevalence"]) / 2

    wait = pd.read_csv(WAIT_TIMES_CSV)
    opioid = pd.read_csv(OPIOID_CSV)

    return dict(community=bc, wait_times=wait, opioid=opioid)


def _bc_wait_lookup(wait_df: pd.DataFrame, recent_years: int = 3) -> dict[str, float]:
    """
    Return {procedure: median_wait_days} for BC, averaged over the most recent years.
    Used to look up wait times by procedure name.
    """
    max_year = wait_df["year"].max()
    recent = wait_df[
        (wait_df["province"] == "BC") &
        (wait_df["year"] >= max_year - recent_years + 1)
    ]
    return recent.groupby("procedure")["median_wait_days"].mean().to_dict()


def _bc_opioid_trend(opioid_df: pd.DataFrame) -> pd.DataFrame:
    """Return BC annual opioid summary (deaths, rate, hospitalizations)."""
    bc = opioid_df[opioid_df["province"] == "BC"].copy()
    return (
        bc.groupby("year")
        .agg(
            deaths=("apparent_opioid_toxicity_deaths", "sum"),
            hospitalizations=("opioid_hospitalizations", "sum"),
            ed_visits=("opioid_ed_visits", "sum"),
            rate_per_100k=("rate_per_100k_deaths", "mean"),
        )
        .reset_index()
    )


# ── Geographic linkage ────────────────────────────────────────────────────────

def _attach_community(patients: pd.DataFrame, community: pd.DataFrame) -> pd.DataFrame:
    """Map patient FSA → CHSA, then join community indicators."""
    patients = patients.copy()
    patients["fsa"]       = patients["postal_code"].str[:3].str.upper()
    patients["chsa_code"] = patients["fsa"].map(FSA_TO_CHSA)

    community_cols = [
        "chsa_code", "chsa_name", "health_authority",
        "pct_without_family_doctor", "pct_below_poverty_line",
        "opioid_overdose_rate", "chronic_disease_burden",
        "mental_health_hospitalization_rate", "er_visits_per_1000",
        "median_household_income", "hospital_beds_per_1000",
        "life_expectancy", "population",
    ]
    merged = patients.merge(
        community[community_cols], on="chsa_code", how="left"
    )
    return merged


# ── Derived encounter features (per patient) ──────────────────────────────────

def _derive_encounter_features(encounters: pd.DataFrame) -> pd.DataFrame:
    """Return one row per patient with aggregate encounter features."""
    enc = encounters.copy()
    ref_date = enc["encounter_date"].max()   # most recent date in dataset = "today"

    # --- Emergency visit frequency (past 12 months) ---
    recent = enc[enc["encounter_date"] >= ref_date - pd.DateOffset(months=12)]
    ed_recent = (
        recent[recent["encounter_type"] == "emergency"]
        .groupby("patient_id")
        .size()
        .rename("ed_visits_12m")
    )

    # --- Left AMA flag ---
    left_ama = (
        enc[enc["disposition"] == "left AMA"]
        .groupby("patient_id")
        .size()
        .gt(0)
        .rename("left_ama")
    )

    # --- Post-discharge follow-up gap ---
    # For each admission, check if there is an outpatient visit within 30 days
    admissions = enc[enc["disposition"] == "admitted"][
        ["patient_id", "encounter_date", "length_of_stay_hours"]
    ].copy()
    admissions["discharge_date"] = (
        admissions["encounter_date"]
        + pd.to_timedelta(admissions["length_of_stay_hours"].fillna(0), unit="h")
    )

    outpatient = enc[enc["encounter_type"] == "outpatient"][
        ["patient_id", "encounter_date"]
    ].rename(columns={"encounter_date": "op_date"})

    # Cross-join then filter: op_date within (discharge, discharge+30d)
    gap_flags = []
    if len(admissions) and len(outpatient):
        merged = admissions.merge(outpatient, on="patient_id", how="left")
        merged["days_to_op"] = (merged["op_date"] - merged["discharge_date"]).dt.days
        within_30 = merged[(merged["days_to_op"] >= 0) & (merged["days_to_op"] <= 30)]
        patients_with_followup = set(within_30["patient_id"].unique())
        patients_ever_admitted = set(admissions["patient_id"].unique())
        no_followup_patients = patients_ever_admitted - patients_with_followup
        gap_flags = list(no_followup_patients)

    no_followup_series = pd.Series(
        True,
        index=pd.Index(gap_flags, name="patient_id"),
        name="no_followup",
        dtype=bool,
    )

    # --- Most recent triage level ---
    latest_triage = (
        enc.sort_values("encounter_date")
        .groupby("patient_id")["triage_level"]
        .last()
        .rename("latest_triage")
    )

    # --- Total admissions ---
    total_admissions = (
        enc[enc["disposition"] == "admitted"]
        .groupby("patient_id")
        .size()
        .rename("total_admissions")
    )

    # Combine
    features = pd.DataFrame(index=enc["patient_id"].unique())
    features.index.name = "patient_id"
    for s in [ed_recent, left_ama, no_followup_series, latest_triage, total_admissions]:
        features = features.join(s, how="left")

    features["ed_visits_12m"]    = features["ed_visits_12m"].fillna(0).astype(int)
    features["left_ama"]         = features["left_ama"].fillna(False).infer_objects(copy=False)
    features["no_followup"]      = features["no_followup"].fillna(False).infer_objects(copy=False)
    features["total_admissions"] = features["total_admissions"].fillna(0).astype(int)

    return features.reset_index()


def _derive_lab_features(labs: pd.DataFrame) -> pd.DataFrame:
    """Return one row per patient with abnormal lab flags."""
    abnormal = labs[labs["abnormal_flag"].isin(["H", "L"])].copy()

    # Key chronic-disease markers
    chronic_labs = ["HbA1c", "Glucose, Fasting", "Total Cholesterol",
                    "LDL Cholesterol", "Creatinine"]
    relevant = abnormal[abnormal["test_name"].isin(chronic_labs)]

    abn_count = (
        relevant.groupby("patient_id")["test_name"]
        .nunique()
        .rename("abnormal_chronic_labs")
    )
    hba1c_high = (
        labs[(labs["test_name"] == "HbA1c") & (labs["abnormal_flag"] == "H")]
        .groupby("patient_id")
        .size()
        .gt(0)
        .rename("hba1c_elevated")
    )
    troponin_high = (
        labs[(labs["test_name"] == "Troponin I") & (labs["abnormal_flag"] == "H")]
        .groupby("patient_id")
        .size()
        .gt(0)
        .rename("troponin_elevated")
    )

    feat = pd.DataFrame(index=pd.Index(labs["patient_id"].unique(), name="patient_id"))
    for s in [abn_count, hba1c_high, troponin_high]:
        feat = feat.join(s, how="left")

    feat["abnormal_chronic_labs"] = feat["abnormal_chronic_labs"].fillna(0).astype(int)
    feat["hba1c_elevated"]        = feat["hba1c_elevated"].fillna(False).infer_objects(copy=False)
    feat["troponin_elevated"]     = feat["troponin_elevated"].fillna(False).infer_objects(copy=False)
    return feat.reset_index()


def _derive_wait_burden(encounters: pd.DataFrame,
                        bc_wait: dict[str, float]) -> pd.DataFrame:
    """
    For each patient, check if any encounter diagnosis maps to a long-wait BC procedure.
    Returns: patient_id, wait_procedure, wait_days_bc, has_wait_burden (bool)
    """
    rows = []
    for patient_id, grp in encounters.groupby("patient_id"):
        best_proc, best_days = None, 0
        for diag in grp["diagnosis_description"].unique():
            proc = DIAGNOSIS_TO_PROCEDURE.get(diag)
            if proc and proc in bc_wait:
                days = bc_wait[proc]
                if days > best_days:
                    best_proc, best_days = proc, days
        rows.append({
            "patient_id":      patient_id,
            "wait_procedure":  best_proc,
            "wait_days_bc":    best_days if best_proc else 0,
            "has_wait_burden": best_days >= WAIT_BARRIER_DAYS,
        })
    return pd.DataFrame(rows)


def _derive_med_features(medications: pd.DataFrame) -> pd.DataFrame:
    """Return one row per patient with medication features."""
    active = medications[medications["active"] == True]
    med_count = (
        active.groupby("patient_id")["drug_name"]
        .nunique()
        .rename("active_med_count")
    )
    return med_count.reset_index()


# ── Public entry point ────────────────────────────────────────────────────────

def load_all() -> dict:
    """Load and join all data; return dict of DataFrames."""
    t1  = _load_track1()
    t2  = _load_track2()
    community = t2["community"]

    # BC wait time lookup (most recent 3 years)
    bc_wait = _bc_wait_lookup(t2["wait_times"])

    # Attach community to patients
    master = _attach_community(t1["patients"], community)

    # Derived features
    enc_feat  = _derive_encounter_features(t1["encounters"])
    lab_feat  = _derive_lab_features(t1["labs"])
    med_feat  = _derive_med_features(t1["medications"])
    wait_feat = _derive_wait_burden(t1["encounters"], bc_wait)

    master = (
        master
        .merge(enc_feat,  on="patient_id", how="left")
        .merge(lab_feat,  on="patient_id", how="left")
        .merge(med_feat,  on="patient_id", how="left")
        .merge(wait_feat, on="patient_id", how="left")
    )

    # Fill derived columns that may be missing for patients with no encounters/labs/meds
    master["ed_visits_12m"]        = master["ed_visits_12m"].fillna(0).astype(int)
    master["left_ama"]             = master["left_ama"].fillna(False).infer_objects(copy=False)
    master["no_followup"]          = master["no_followup"].fillna(False).infer_objects(copy=False)
    master["abnormal_chronic_labs"]= master["abnormal_chronic_labs"].fillna(0).astype(int)
    master["hba1c_elevated"]       = master["hba1c_elevated"].fillna(False).infer_objects(copy=False)
    master["troponin_elevated"]    = master["troponin_elevated"].fillna(False).infer_objects(copy=False)
    master["active_med_count"]     = master["active_med_count"].fillna(0).astype(int)
    master["total_admissions"]     = master["total_admissions"].fillna(0).astype(int)
    master["has_wait_burden"]      = master["has_wait_burden"].fillna(False).infer_objects(copy=False)
    master["wait_days_bc"]         = master["wait_days_bc"].fillna(0)
    master["wait_procedure"]       = master["wait_procedure"].fillna("")

    # BC opioid trend (for dashboard)
    opioid_trend = _bc_opioid_trend(t2["opioid"])

    return dict(
        patients=t1["patients"],
        encounters=t1["encounters"],
        vitals=t1["vitals"],
        medications=t1["medications"],
        labs=t1["labs"],
        community=community,
        wait_times=t2["wait_times"],
        opioid=t2["opioid"],
        opioid_trend=opioid_trend,
        bc_wait=bc_wait,
        master=master,
    )


if __name__ == "__main__":
    data = load_all()
    m = data["master"]
    print(f"Master table: {m.shape}")
    print(m[["patient_id", "chsa_name", "ed_visits_12m",
             "hba1c_elevated", "active_med_count", "no_followup"]].head(10))
