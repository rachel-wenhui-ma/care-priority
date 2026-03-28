# 🏥 AI-Enabled Care Prioritization System

**Healthcare AI Hackathon — March 27–28, 2026 | UVic**

> Context-aware care gap detection that combines patient clinical risk with community structural vulnerability to prioritize outreach for patients most likely to fall through the cracks.

[![Track](https://img.shields.io/badge/Track%202-Population%20Health%20%26%20Health%20Equity-2e7d32)]()
[![Built With](https://img.shields.io/badge/Built%20With-Streamlit%20%2B%20Claude%20AI-ff4b4b)]()

---

## Team

| Name | Role |
|------|------|
| **Rachel Ma** | Lead Developer |
| **Joel Li** | Lead Developer |

**Challenge Track:** Track 2 — Population Health & Health Equity

---

## The Problem

In British Columbia, **1 in 5 residents lacks a family doctor**. Patients in underserved communities cycle through emergency departments without continuity of care, while care coordinators have no systematic way to identify who needs proactive outreach most urgently.

Existing tools look at clinical data OR community data — never both together. A patient with uncontrolled diabetes is high-risk anywhere, but that risk compounds dramatically when they live in a community where 25% of residents can't get a GP referral.

## Our Solution

An **AI-enabled prioritization system** that fuses individual patient clinical signals (Track 1) with community-level structural barriers (Track 2) into a single actionable priority score, enabling care coordinators to direct limited outreach resources where they matter most.

### What makes it different

- **Cross-track data fusion:** Links patient postal codes to BC Community Health Service Areas using area-based socioeconomic measures (the same ABSM approach used by CIHI for equity stratification)
- **Not a black box:** Every patient score is decomposed into *Clinical Need*, *Access Barrier*, and *System Impact* — care coordinators see exactly **why** someone is flagged
- **Actionable, not just descriptive:** Includes an intervention planner ("if you can reach 50 patients this week, here's who and what you'll prevent") and a community scenario simulator ("what if primary care attachment improves by 5pp in this community?")
- **Honest methodology:** Proactively discloses ecological fallacy risk, synthetic data limitations, and frames outputs as prioritization support — not prediction

### Key Features

| Feature | Description |
|---------|-------------|
| **Priority Queue** | Ranked patient list with combined scores, expandable "Why Now?" reasoning per patient |
| **7-Component Risk Scoring** | ED frequency, chronic disease control, polypharmacy, AMA history, follow-up gap, wait burden, language barrier (0–100) |
| **Community Vulnerability Index** | Weighted composite of 6 BC health indicators across all 78 communities (0–100) |
| **Intervention Planner** | Given N outreach capacity → optimal patient selection → estimated avoided ED visits and cost savings |
| **Community Scenario Simulator** | What-if analysis: improve primary care attachment → recalculate vulnerability → show tier shifts |
| **AI Rationale Generation** | Claude 3.5 Haiku generates natural-language explanations per patient |
| **Full BC Context** | Opioid crisis trends, elective procedure wait times, 78-community vulnerability ranking |

---

## How It Works

```
┌─────────────────┐    ┌──────────────────────┐
│  Track 1 Data   │    │    Track 2 Data       │
│  (Patient-level)│    │  (Community-level)    │
│                 │    │                       │
│ • Encounters    │    │ • BC Health Indicators│
│ • Labs          │    │ • CIHI Wait Times     │
│ • Medications   │    │ • Opioid Surveillance │
└────────┬────────┘    └──────────┬────────────┘
         │                        │
         ▼                        ▼
   Patient Risk Score      Community Vulnerability
      (0–100)                   Score (0–100)
         │                        │
         └──────────┬─────────────┘
                    ▼
          Combined Priority Score
      (60% clinical + 40% community)
                    │
                    ▼
        ┌───────────────────────┐
        │   Percentile-Based    │
        │   Tier Assignment     │
        │                       │
        │ 🔴 CRITICAL (top 5%)  │
        │ 🟠 HIGH (80th–95th)   │
        │ 🟡 MEDIUM (50th–80th) │
        │ 🟢 LOW (bottom 50%)   │
        └───────────────────────┘
```

### Data Linkage

Patient postal codes (FSA) → BC Community Health Service Areas (CHSA) via geographic mapping, following the **area-based socioeconomic measures** approach used by CIHI for health equity analysis.

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Streamlit 1.35+ |
| Visualization | Plotly 5.20+ |
| Data Processing | Pandas, NumPy, scikit-learn |
| AI Explanations | Claude 3.5 Haiku (Anthropic API) |
| Language | Python 3.11+ |

---

## Project Structure

```
care-priority/
├── app.py                 # Streamlit dashboard (3-tab UI)
├── config.py              # All weights, thresholds, paths, mappings
├── data_pipeline.py       # Load, clean, join Track 1 + Track 2 data
├── patient_scorer.py      # 7-component patient risk scoring (0–100)
├── community_scorer.py    # Community vulnerability index (0–100)
├── priority_engine.py     # Combined scoring, tiers, simulation engines
├── llm_explainer.py       # Claude AI rationale generation
├── requirements.txt       # Python dependencies
└── README.md
```

---

## Demo

🌐 **Live Demo:** [https://care-priority.streamlit.app](https://care-priority.streamlit.app)

📊 **Presentation Slides:** [slides.pptx](slides.pptx)

🎬 **Demo Recording:** [care-priority.mp4](care-priority.mp4)

### Run Locally

```bash
# Clone the repo
git clone <repo-url>
cd care-priority

# Install dependencies
pip install -r requirements.txt

# (Optional) Set Anthropic API key for AI explanations
export ANTHROPIC_API_KEY=your_key_here

# Launch
streamlit run app.py --server.port 8502
```

> **Note:** The AI rationale feature requires an Anthropic API key. All other features work without it.

---

## Data Sources

| Dataset | Source | Level |
|---------|--------|-------|
| Synthea Patient Records | Hackathon Track 1 | Individual (2,000 synthetic patients) |
| BC Community Health Profiles | Hackathon Track 2 | 78 BC communities |
| CIHI Wait Times | Hackathon Track 2 | Provincial (BC) |
| Opioid Surveillance | Hackathon Track 2 | Provincial (BC) |

All Track 1 data is synthetic (Synthea-generated). Track 2 data is based on real BC public health indicators.

---

## Methodology Notes

- **Scoring is rule-based with explicit weights** — not a trained ML model. All parameters are in `config.py` and fully auditable.
- **Community vulnerability is a contextual modifier**, not an individual-level diagnosis. We use area-based linkage (CIHI ABSM approach), which introduces ecological fallacy risk — disclosed in the app.
- **Intervention estimates assume 30% ED visit reduction** from proactive outreach — a conservative modeled assumption, not an observed outcome.
- **Scenario projections are sensitivity analyses** within the scoring framework, not causal predictions.

---

## Acknowledgments

- **Synthea** for realistic synthetic patient data
- **CIHI** for the area-based equity stratification methodology that inspired our linkage approach
- **Anthropic Claude** for natural-language patient rationale generation
- **UVic Hacks × BuildersVault** for organizing the hackathon

---

*Built at the UVic Healthcare AI Hackathon, March 2026*
