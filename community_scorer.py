"""
community_scorer.py — Compute community vulnerability score (0–100) for each CHSA.

Weighted composite of six normalized indicators:
  30%  pct_without_family_doctor
  20%  pct_below_poverty_line
  15%  opioid_overdose_rate
  15%  chronic_disease_burden  (avg of diabetes + hypertension prevalence)
  10%  mental_health_hospitalization_rate
  10%  er_visits_per_1000
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from config import COMMUNITY_WEIGHTS


INDICATOR_COLS = list(COMMUNITY_WEIGHTS.keys())


def score_communities(community: pd.DataFrame) -> pd.DataFrame:
    """
    Add vulnerability_score (0-100) to the community DataFrame.
    Returns a new DataFrame with chsa_code, chsa_name, vulnerability_score,
    plus the normalised individual indicators.
    """
    df = community.copy()

    # Ensure derived column exists
    if "chronic_disease_burden" not in df.columns:
        df["chronic_disease_burden"] = (
            df["diabetes_prevalence"] + df["hypertension_prevalence"]
        ) / 2

    # Min-max normalize each indicator across all communities
    scaler = MinMaxScaler()
    norm_cols = {col: f"{col}_norm" for col in INDICATOR_COLS}
    df[list(norm_cols.values())] = scaler.fit_transform(df[INDICATOR_COLS])

    # Weighted sum → scale to 0-100
    df["vulnerability_score"] = (
        sum(
            df[norm_col] * COMMUNITY_WEIGHTS[orig_col]
            for orig_col, norm_col in norm_cols.items()
        )
        * 100
    ).round(1)

    # Vulnerability tier label
    df["vulnerability_tier"] = pd.cut(
        df["vulnerability_score"],
        bins=[0, 33, 66, 100],
        labels=["Low", "Moderate", "High"],
        include_lowest=True,
    )

    keep_cols = [
        "chsa_code", "chsa_name", "health_authority",
        "vulnerability_score", "vulnerability_tier",
        # raw indicators for display
        "pct_without_family_doctor", "pct_below_poverty_line",
        "opioid_overdose_rate", "chronic_disease_burden",
        "mental_health_hospitalization_rate", "er_visits_per_1000",
        "median_household_income", "hospital_beds_per_1000",
        "life_expectancy", "population",
    ]
    return df[[c for c in keep_cols if c in df.columns]]


if __name__ == "__main__":
    from data_pipeline import load_all
    data = load_all()
    comm_scores = score_communities(data["community"])
    print(comm_scores[["chsa_name", "vulnerability_score", "vulnerability_tier",
                        "pct_without_family_doctor", "pct_below_poverty_line"]]
          .sort_values("vulnerability_score", ascending=False)
          .to_string())
