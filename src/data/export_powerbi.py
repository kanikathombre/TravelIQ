"""
export_powerbi.py
=================
Generates clean analytical CSV exports for use in Microsoft Power BI Desktop.

Outputs (written to data/powerbi/):
  destinations_analytics.csv  — full destination dataset, denormalised
  cost_summary.csv            — cost breakdown pivot
  seasonality.csv             — best-month distribution
  interest_scores.csv         — long-format interest scores for bar/radar charts
"""
import pandas as pd
from pathlib import Path

BASE_DIR   = Path(__file__).resolve().parents[2]
INPUT_FILE = BASE_DIR / "data" / "processed" / "destinations_enriched.csv"
OUT_DIR    = BASE_DIR / "data" / "powerbi"
OUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(INPUT_FILE)

# ── 1. Full analytics export ──────────────────────────────────────────────
df.to_csv(OUT_DIR / "destinations_analytics.csv", index=False)
print(f"Written: destinations_analytics.csv ({len(df)} rows)")

# ── 2. Cost summary ───────────────────────────────────────────────────────
cost_cols = ["destination_name", "state_region", "destination_type",
             "accommodation_cost", "food_cost", "transport_cost",
             "activity_cost", "avg_daily_cost", "cost_data_quality",
             "recommended_stay_days", "currency"]
cost_df = df[cost_cols].copy()
cost_df.to_csv(OUT_DIR / "cost_summary.csv", index=False)
print(f"Written: cost_summary.csv ({len(cost_df)} rows)")

# ── 3. Seasonality (one row per month per destination) ────────────────────
MONTH_MAP = {
    "January": 1, "February": 2, "March": 3, "April": 4,
    "May": 5, "June": 6, "July": 7, "August": 8,
    "September": 9, "October": 10, "November": 11, "December": 12,
}
ABBREV_MAP = {
    "Jan": "January", "Feb": "February", "Mar": "March", "Apr": "April",
    "May": "May", "Jun": "June", "Jul": "July", "Aug": "August",
    "Sep": "September", "Oct": "October", "Nov": "November", "Dec": "December",
    "mid December": "December",
}

def parse_best_months(s: str) -> list[str]:
    if pd.isna(s) or str(s).strip() == "":
        return []
    months = []
    parts = [p.strip() for p in str(s).replace(";", ",").split(",")]
    for part in parts:
        if "-" in part:
            tokens = [t.strip() for t in part.split("-")]
            if len(tokens) == 2:
                start_raw, end_raw = tokens
                start = ABBREV_MAP.get(start_raw, start_raw)
                end   = ABBREV_MAP.get(end_raw, end_raw)
                s_idx = MONTH_MAP.get(start)
                e_idx = MONTH_MAP.get(end)
                if s_idx and e_idx:
                    if s_idx <= e_idx:
                        r = range(s_idx, e_idx + 1)
                    else:   # cross-year: e.g. Oct–Mar
                        r = list(range(s_idx, 13)) + list(range(1, e_idx + 1))
                    for m_idx in r:
                        months.append([k for k, v in MONTH_MAP.items() if v == m_idx][0])
        else:
            clean = ABBREV_MAP.get(part, part)
            if clean in MONTH_MAP:
                months.append(clean)
    return months

rows = []
for _, row in df.iterrows():
    for month in parse_best_months(row.get("best_months", "")):
        rows.append({
            "destination_name": row["destination_name"],
            "state_region": row.get("state_region"),
            "destination_type": row.get("destination_type"),
            "month": month,
            "month_num": MONTH_MAP[month],
        })

seasonality_df = pd.DataFrame(rows)
if not seasonality_df.empty:
    seasonality_df.sort_values(["destination_name", "month_num"], inplace=True)
seasonality_df.to_csv(OUT_DIR / "seasonality.csv", index=False)
print(f"Written: seasonality.csv ({len(seasonality_df)} rows)")

# ── 4. Long-format interest scores ────────────────────────────────────────
score_cols = ["adventure_score", "beach_score", "nature_score",
              "culture_score", "food_score", "nightlife_score",
              "romance_score", "wildlife_score", "winter_score",
              "wellness_score"]
id_vars = ["destination_name", "state_region", "destination_type"]
interest_long = df[id_vars + score_cols].melt(
    id_vars=id_vars,
    value_vars=score_cols,
    var_name="interest_raw",
    value_name="score",
)
interest_long["interest"] = interest_long["interest_raw"].str.replace("_score", "").str.title()
interest_long.drop(columns=["interest_raw"], inplace=True)
interest_long.to_csv(OUT_DIR / "interest_scores.csv", index=False)
print(f"Written: interest_scores.csv ({len(interest_long)} rows)")

print("\n[Done] Power BI CSV exports ready in data/powerbi/")
