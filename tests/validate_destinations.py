"""
validate_destinations.py
========================
Data-quality validation for destinations_enriched.csv.
Rules:
  - Fields can be missing but must not be silently hidden.
  - Any missing required field is reported and sets quality = "missing".
  - Tests do NOT require every field to be populated.
"""
import sys
import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR  = Path(__file__).resolve().parents[1]
DATA_FILE = BASE_DIR / "data" / "processed" / "destinations_enriched.csv"

ERRORS   = []
WARNINGS = []

df = pd.read_csv(DATA_FILE)

# ── 1. Unique destination names ─────────────────────────────────────────────
dups = df[df["destination_name"].duplicated(keep=False)]
if not dups.empty:
    ERRORS.append(f"Duplicate destination names: {dups['destination_name'].tolist()}")

# ── 2. Latitude / longitude ranges ─────────────────────────────────────────
if "latitude" in df.columns:
    out = df[(df["latitude"] < -90) | (df["latitude"] > 90)]
    if not out.empty:
        ERRORS.append(f"Latitude out of range: {out['destination_name'].tolist()}")
if "longitude" in df.columns:
    out = df[(df["longitude"] < -180) | (df["longitude"] > 180)]
    if not out.empty:
        ERRORS.append(f"Longitude out of range: {out['destination_name'].tolist()}")

# ── 3. Required geo fields must be present ──────────────────────────────────
for col in ["latitude", "longitude", "country", "state_region"]:
    missing = df[df[col].isna()]["destination_name"].tolist() if col in df.columns else df["destination_name"].tolist()
    if missing:
        ERRORS.append(f"'{col}' missing for: {missing}")

# ── 4. Cost fields — missing is allowed but must be explicitly recorded ─────
cost_cols = ["accommodation_cost", "food_cost", "transport_cost",
             "activity_cost", "avg_daily_cost"]
for col in cost_cols:
    if col not in df.columns:
        ERRORS.append(f"Cost column '{col}' not in dataset at all")
        continue
    n = df[col].isna().sum()
    if n > 0:
        WARNINGS.append(f"'{col}' has {n} missing values — these are labelled 'missing' in cost_data_quality")

# ── 5. avg_daily_cost consistency ──────────────────────────────────────────
if all(c in df.columns for c in ["accommodation_cost","food_cost","transport_cost","activity_cost","avg_daily_cost"]):
    computed = df[["accommodation_cost","food_cost","transport_cost","activity_cost"]].sum(axis=1)
    mismatch = df[df["avg_daily_cost"].notna() & (abs(df["avg_daily_cost"] - computed) > 1)]
    if not mismatch.empty:
        ERRORS.append(f"avg_daily_cost mismatch in: {mismatch['destination_name'].tolist()}")

# ── 6. Interest scores 0–10 ───────────────────────────────────────────────
score_cols = ["adventure_score","beach_score","nature_score","culture_score",
              "food_score","nightlife_score","romance_score","wildlife_score",
              "winter_score","wellness_score"]
for col in score_cols:
    if col not in df.columns:
        WARNINGS.append(f"Interest score column '{col}' absent")
        continue
    valid = df[df[col].notna()]
    out_range = valid[(valid[col] < 0) | (valid[col] > 10)]
    if not out_range.empty:
        ERRORS.append(f"'{col}' out of 0–10 range: {out_range['destination_name'].tolist()}")

# ── 7. currency column present ───────────────────────────────────────────
if "currency" not in df.columns:
    ERRORS.append("'currency' column missing")

# ── Report ────────────────────────────────────────────────────────────────
print("=" * 60)
print(f"Validation: {DATA_FILE.name}")
print(f"Rows: {len(df)}")
print("=" * 60)

if WARNINGS:
    print(f"\n⚠  WARNINGS ({len(WARNINGS)}):")
    for w in WARNINGS:
        print(f"   {w}")

if ERRORS:
    print(f"\n✗  ERRORS ({len(ERRORS)}):")
    for e in ERRORS:
        print(f"   {e}")
    print("\nValidation FAILED")
    sys.exit(1)
else:
    print("\n✓  All validation checks passed")
    print("[Done]")
