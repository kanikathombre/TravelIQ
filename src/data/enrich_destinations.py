"""
enrich_destinations.py
======================
Enriches the India destination master with:
  - Per-person-per-day cost estimates (accommodation, food, local transport, activity)
  - 10-point interest scores (rule-based expert classification — NOT empirical data)
  - Tourist rating (subjective editorial rating 1–5)
  - Safety score (NOT populated — no reliable, citation-ready source available)
  - Data-quality / provenance metadata per cost component

Cost methodology
----------------
* All monetary values are in INR (Indian Rupee).
* Accommodation cost = per-person per night, assuming DOUBLE OCCUPANCY
  (two people sharing a standard mid-range room; budget travellers sharing
  a dormitory would pay less; solo travellers in a private room would pay more).
* Food cost = per-person per day, covering three meals at local/tourist
  restaurants that are typical for that destination tier.
* Local transport cost = per-person per day covering internal transfers,
  rickshaws, local buses, shared cabs.
* Activity cost = per-person per day covering typical entry tickets,
  guided walks, and minor paid experiences.
* avg_daily_cost = sum of the four components above.
* All estimates are for a STANDARD travel style.
* Source classification:
    "estimated_research" = synthesised from publicly available tourism
    blogs, Incredible India, and state tourism board pages (Oct 2024).
    No live booking API was used. Values are approximate mid-range estimates.

Interest score rubric (rule-based, 0–10)
-----------------------------------------
0   = interest fully absent
1-3 = minor or incidental presence
4-6 = moderate; considered part of the destination mix
7-8 = strong, primary or well-known draw
9-10= exceptional, defining characteristic

Scores are assigned by the author based on published tourism characterisation
of each destination.  They are NOT derived from visitor-survey data.

Safety score
------------
No reliable, citation-ready, city-level safety index was available for all
20 destinations at the time of this analysis.  The column retains NaN.

Tourist rating
--------------
Subjective editorial rating 1–5 based on national tourism recognition,
UNESCO listings, and Incredible India marketing tier.

Data quality indicator (cost_data_quality)
-------------------------------------------
"estimated_research" = method above
"missing"           = no data populated
"""

import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE  = BASE_DIR / "data" / "processed" / "india_destination_master.csv"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "destinations_enriched.csv"

# ---------------------------------------------------------------------------
# ENRICHMENT DATA
# All monetary values: INR, per person per day (accommodation assumes double
# occupancy; see module docstring for full assumptions).
# Source: estimated_research (see docstring)
# ---------------------------------------------------------------------------

ENRICHMENT: dict[str, dict] = {

    # ── Hampi ──────────────────────────────────────────────────────────────
    "Hampi": {
        "accommodation_cost": 800,   # budget guesthouse per person (shared)
        "food_cost": 400,
        "transport_cost": 200,       # coracle, auto, cycle
        "activity_cost": 300,        # ASI site tickets, guide
        "avg_daily_cost": 1700,
        "cost_data_quality": "estimated_research",
        "tourist_rating": 4,
        # Interest scores (0–10, rule-based)
        "adventure_score": 4,
        "beach_score": 0,
        "nature_score": 5,
        "culture_score": 9,
        "food_score": 3,
        "nightlife_score": 1,
        "romance_score": 5,
        "wildlife_score": 2,
        "winter_score": 6,
        "wellness_score": 4,
    },

    # ── Mysuru ─────────────────────────────────────────────────────────────
    "Mysuru": {
        "accommodation_cost": 1200,
        "food_cost": 500,
        "transport_cost": 300,
        "activity_cost": 400,        # Palace, Brindavan Gardens, zoo
        "avg_daily_cost": 2400,
        "cost_data_quality": "estimated_research",
        "tourist_rating": 5,
        "adventure_score": 2,
        "beach_score": 0,
        "nature_score": 4,
        "culture_score": 9,
        "food_score": 7,
        "nightlife_score": 3,
        "romance_score": 6,
        "wildlife_score": 2,
        "winter_score": 6,
        "wellness_score": 5,
    },

    # ── Kumarakom ──────────────────────────────────────────────────────────
    "Kumarakom": {
        "accommodation_cost": 2000,  # mid-range backwater resort per person
        "food_cost": 700,
        "transport_cost": 400,       # houseboat transfers, boat taxi
        "activity_cost": 600,        # houseboat day cruise, bird sanctuary
        "avg_daily_cost": 3700,
        "cost_data_quality": "estimated_research",
        "tourist_rating": 5,
        "adventure_score": 3,
        "beach_score": 5,
        "nature_score": 9,
        "culture_score": 5,
        "food_score": 7,
        "nightlife_score": 2,
        "romance_score": 9,
        "wildlife_score": 6,
        "winter_score": 4,
        "wellness_score": 8,
    },

    # ── Shillong ───────────────────────────────────────────────────────────
    "Shillong": {
        "accommodation_cost": 1000,
        "food_cost": 450,
        "transport_cost": 300,
        "activity_cost": 300,
        "avg_daily_cost": 2050,
        "cost_data_quality": "estimated_research",
        "tourist_rating": 4,
        "adventure_score": 6,
        "beach_score": 0,
        "nature_score": 8,
        "culture_score": 5,
        "food_score": 5,
        "nightlife_score": 4,
        "romance_score": 6,
        "wildlife_score": 4,
        "winter_score": 5,
        "wellness_score": 6,
    },

    # ── Sohra (Cherrapunjee) ───────────────────────────────────────────────
    "Sohra": {
        "accommodation_cost": 900,
        "food_cost": 400,
        "transport_cost": 350,
        "activity_cost": 400,        # waterfall treks, living root bridges
        "avg_daily_cost": 2050,
        "cost_data_quality": "estimated_research",
        "tourist_rating": 4,
        "adventure_score": 8,
        "beach_score": 0,
        "nature_score": 10,
        "culture_score": 4,
        "food_score": 4,
        "nightlife_score": 1,
        "romance_score": 6,
        "wildlife_score": 5,
        "winter_score": 3,
        "wellness_score": 7,
    },

    # ── Jodhpur ────────────────────────────────────────────────────────────
    "Jodhpur": {
        "accommodation_cost": 1100,
        "food_cost": 450,
        "transport_cost": 250,
        "activity_cost": 350,        # Mehrangarh, Jaswant Thada
        "avg_daily_cost": 2150,
        "cost_data_quality": "estimated_research",
        "tourist_rating": 5,
        "adventure_score": 4,
        "beach_score": 0,
        "nature_score": 3,
        "culture_score": 9,
        "food_score": 7,
        "nightlife_score": 3,
        "romance_score": 7,
        "wildlife_score": 1,
        "winter_score": 7,
        "wellness_score": 4,
    },

    # ── Gangtok ────────────────────────────────────────────────────────────
    "Gangtok": {
        "accommodation_cost": 1200,
        "food_cost": 500,
        "transport_cost": 400,       # shared jeeps to viewpoints
        "activity_cost": 400,
        "avg_daily_cost": 2500,
        "cost_data_quality": "estimated_research",
        "tourist_rating": 4,
        "adventure_score": 7,
        "beach_score": 0,
        "nature_score": 9,
        "culture_score": 5,
        "food_score": 6,
        "nightlife_score": 3,
        "romance_score": 7,
        "wildlife_score": 4,
        "winter_score": 6,
        "wellness_score": 6,
    },

    # ── Leh ────────────────────────────────────────────────────────────────
    "Leh": {
        "accommodation_cost": 1400,
        "food_cost": 600,
        "transport_cost": 600,       # shared taxis, motorbike hire
        "activity_cost": 500,        # permits, monastery entries
        "avg_daily_cost": 3100,
        "cost_data_quality": "estimated_research",
        "tourist_rating": 5,
        "adventure_score": 10,
        "beach_score": 0,
        "nature_score": 10,
        "culture_score": 7,
        "food_score": 5,
        "nightlife_score": 2,
        "romance_score": 6,
        "wildlife_score": 5,
        "winter_score": 2,            # road/flight access very limited in winter
        "wellness_score": 6,
    },

    # ── Kargil ─────────────────────────────────────────────────────────────
    "Kargil": {
        "accommodation_cost": 900,
        "food_cost": 400,
        "transport_cost": 400,
        "activity_cost": 300,
        "avg_daily_cost": 2000,
        "cost_data_quality": "estimated_research",
        "tourist_rating": 3,
        "adventure_score": 8,
        "beach_score": 0,
        "nature_score": 8,
        "culture_score": 6,
        "food_score": 4,
        "nightlife_score": 1,
        "romance_score": 3,
        "wildlife_score": 3,
        "winter_score": 1,
        "wellness_score": 4,
    },

    # ── Lakshadweep ────────────────────────────────────────────────────────
    "Lakshadweep": {
        "accommodation_cost": 3000,  # permit-only island; limited resorts
        "food_cost": 800,
        "transport_cost": 500,       # boat transfers between islands
        "activity_cost": 800,        # snorkelling, scuba, glass-bottom boat
        "avg_daily_cost": 5100,
        "cost_data_quality": "estimated_research",
        "tourist_rating": 5,
        "adventure_score": 7,
        "beach_score": 10,
        "nature_score": 8,
        "culture_score": 3,
        "food_score": 6,
        "nightlife_score": 1,
        "romance_score": 9,
        "wildlife_score": 7,
        "winter_score": 4,
        "wellness_score": 8,
    },

    # ── Puducherry ─────────────────────────────────────────────────────────
    "Puducherry": {
        "accommodation_cost": 1300,
        "food_cost": 600,
        "transport_cost": 250,
        "activity_cost": 300,
        "avg_daily_cost": 2450,
        "cost_data_quality": "estimated_research",
        "tourist_rating": 4,
        "adventure_score": 3,
        "beach_score": 7,
        "nature_score": 4,
        "culture_score": 7,
        "food_score": 8,
        "nightlife_score": 5,
        "romance_score": 7,
        "wildlife_score": 2,
        "winter_score": 6,
        "wellness_score": 7,
    },

    # ── Gwalior ────────────────────────────────────────────────────────────
    "Gwalior": {
        "accommodation_cost": 900,
        "food_cost": 400,
        "transport_cost": 200,
        "activity_cost": 300,
        "avg_daily_cost": 1800,
        "cost_data_quality": "estimated_research",
        "tourist_rating": 4,
        "adventure_score": 2,
        "beach_score": 0,
        "nature_score": 3,
        "culture_score": 9,
        "food_score": 5,
        "nightlife_score": 2,
        "romance_score": 4,
        "wildlife_score": 1,
        "winter_score": 7,
        "wellness_score": 2,
    },

    # ── Chitrakoot ─────────────────────────────────────────────────────────
    "Chitrakoot": {
        "accommodation_cost": 700,
        "food_cost": 300,
        "transport_cost": 200,
        "activity_cost": 200,
        "avg_daily_cost": 1400,
        "cost_data_quality": "estimated_research",
        "tourist_rating": 3,
        "adventure_score": 3,
        "beach_score": 0,
        "nature_score": 6,
        "culture_score": 8,
        "food_score": 4,
        "nightlife_score": 1,
        "romance_score": 4,
        "wildlife_score": 3,
        "winter_score": 6,
        "wellness_score": 7,
    },

    # ── Amritsar ───────────────────────────────────────────────────────────
    "Amritsar": {
        "accommodation_cost": 1000,
        "food_cost": 500,
        "transport_cost": 200,
        "activity_cost": 200,        # Golden Temple free; Wagah border ceremony
        "avg_daily_cost": 1900,
        "cost_data_quality": "estimated_research",
        "tourist_rating": 5,
        "adventure_score": 2,
        "beach_score": 0,
        "nature_score": 2,
        "culture_score": 10,
        "food_score": 9,
        "nightlife_score": 2,
        "romance_score": 4,
        "wildlife_score": 1,
        "winter_score": 5,
        "wellness_score": 5,
    },

    # ── Kapurthala ─────────────────────────────────────────────────────────
    "Kapurthala": {
        "accommodation_cost": 700,
        "food_cost": 350,
        "transport_cost": 150,
        "activity_cost": 150,
        "avg_daily_cost": 1350,
        "cost_data_quality": "estimated_research",
        "tourist_rating": 2,
        "adventure_score": 1,
        "beach_score": 0,
        "nature_score": 2,
        "culture_score": 6,
        "food_score": 5,
        "nightlife_score": 1,
        "romance_score": 3,
        "wildlife_score": 1,
        "winter_score": 4,
        "wellness_score": 2,
    },

    # ── Bundi ──────────────────────────────────────────────────────────────
    "Bundi": {
        "accommodation_cost": 900,
        "food_cost": 400,
        "transport_cost": 200,
        "activity_cost": 250,
        "avg_daily_cost": 1750,
        "cost_data_quality": "estimated_research",
        "tourist_rating": 4,
        "adventure_score": 3,
        "beach_score": 0,
        "nature_score": 4,
        "culture_score": 9,
        "food_score": 5,
        "nightlife_score": 1,
        "romance_score": 6,
        "wildlife_score": 2,
        "winter_score": 7,
        "wellness_score": 5,
    },

    # ── Mamallapuram ───────────────────────────────────────────────────────
    "Mamallapuram": {
        "accommodation_cost": 1100,
        "food_cost": 450,
        "transport_cost": 200,
        "activity_cost": 300,
        "avg_daily_cost": 2050,
        "cost_data_quality": "estimated_research",
        "tourist_rating": 4,
        "adventure_score": 4,
        "beach_score": 7,
        "nature_score": 4,
        "culture_score": 9,
        "food_score": 6,
        "nightlife_score": 3,
        "romance_score": 6,
        "wildlife_score": 2,
        "winter_score": 7,
        "wellness_score": 4,
    },

    # ── Nilgiris ───────────────────────────────────────────────────────────
    "Nilgiris": {
        "accommodation_cost": 1200,
        "food_cost": 400,
        "transport_cost": 300,
        "activity_cost": 300,
        "avg_daily_cost": 2200,
        "cost_data_quality": "estimated_research",
        "tourist_rating": 4,
        "adventure_score": 5,
        "beach_score": 0,
        "nature_score": 9,
        "culture_score": 4,
        "food_score": 5,
        "nightlife_score": 2,
        "romance_score": 7,
        "wildlife_score": 7,
        "winter_score": 5,
        "wellness_score": 8,
    },

    # ── Agartala ───────────────────────────────────────────────────────────
    "Agartala": {
        "accommodation_cost": 800,
        "food_cost": 350,
        "transport_cost": 200,
        "activity_cost": 200,
        "avg_daily_cost": 1550,
        "cost_data_quality": "estimated_research",
        "tourist_rating": 3,
        "adventure_score": 3,
        "beach_score": 0,
        "nature_score": 5,
        "culture_score": 7,
        "food_score": 5,
        "nightlife_score": 2,
        "romance_score": 4,
        "wildlife_score": 4,
        "winter_score": 5,
        "wellness_score": 4,
    },

    # ── Unakoti ────────────────────────────────────────────────────────────
    "Unakoti": {
        "accommodation_cost": 600,   # basic lodging near Kailashahar
        "food_cost": 300,
        "transport_cost": 250,
        "activity_cost": 150,
        "avg_daily_cost": 1300,
        "cost_data_quality": "estimated_research",
        "tourist_rating": 3,
        "adventure_score": 4,
        "beach_score": 0,
        "nature_score": 7,
        "culture_score": 8,
        "food_score": 4,
        "nightlife_score": 1,
        "romance_score": 4,
        "wildlife_score": 4,
        "winter_score": 5,
        "wellness_score": 5,
    },
}

# ---------------------------------------------------------------------------
# LOAD
# ---------------------------------------------------------------------------

df = pd.read_csv(INPUT_FILE)
print(f"Loaded {len(df)} destinations from {INPUT_FILE}")

# ---------------------------------------------------------------------------
# APPLY ENRICHMENT — only update columns that exist in the master
# ---------------------------------------------------------------------------

numeric_cost_cols = [
    "accommodation_cost", "food_cost", "transport_cost",
    "activity_cost", "avg_daily_cost",
]
score_cols = [
    "tourist_rating",
    "adventure_score", "beach_score", "nature_score", "culture_score",
    "food_score", "nightlife_score", "romance_score", "wildlife_score",
    "winter_score", "wellness_score",
]

# Add missing columns if not present
for col in numeric_cost_cols + score_cols:
    if col not in df.columns:
        df[col] = float("nan")

if "cost_data_quality" not in df.columns:
    df["cost_data_quality"] = "missing"

# Safety score deliberately left as NaN — no reliable source
if "safety_score" not in df.columns:
    df["safety_score"] = float("nan")

# Apply enrichment row-by-row
updated = 0
for dest, values in ENRICHMENT.items():
    mask = df["destination_name"] == dest
    if not mask.any():
        print(f"  WARNING: '{dest}' not found in master — skipping")
        continue
    for col, val in values.items():
        if col not in df.columns:
            df[col] = float("nan")
        df.loc[mask, col] = val
    updated += 1

print(f"Enriched {updated} / {len(ENRICHMENT)} destinations")

# ---------------------------------------------------------------------------
# VALIDATION
# ---------------------------------------------------------------------------

print("\n── Data-quality summary ──")
for col in numeric_cost_cols:
    n_missing = df[col].isna().sum()
    flag = "⚠ MISSING" if n_missing > 0 else "✓"
    print(f"  {flag}  {col}: {n_missing} missing")

print()
for col in score_cols:
    n_missing = df[col].isna().sum()
    flag = "⚠ MISSING" if n_missing > 0 else "✓"
    print(f"  {flag}  {col}: {n_missing} missing")

# avg_daily_cost consistency check
df["_computed_daily"] = (
    df["accommodation_cost"].fillna(0)
    + df["food_cost"].fillna(0)
    + df["transport_cost"].fillna(0)
    + df["activity_cost"].fillna(0)
)
mismatch = df[
    df["avg_daily_cost"].notna()
    & (abs(df["avg_daily_cost"] - df["_computed_daily"]) > 1)
]
if len(mismatch) > 0:
    print(f"\n⚠  avg_daily_cost mismatch in {len(mismatch)} rows:")
    print(mismatch[["destination_name", "avg_daily_cost", "_computed_daily"]])
else:
    print("\n✓  avg_daily_cost is consistent with component sum")

df.drop(columns=["_computed_daily"], inplace=True)

# ---------------------------------------------------------------------------
# SAVE
# ---------------------------------------------------------------------------

df.to_csv(OUTPUT_FILE, index=False)
print(f"\nSaved enriched dataset → {OUTPUT_FILE}")
print("[Done]")
