import pandas as pd
from pathlib import Path


# --------------------------------------------------
# PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = BASE_DIR / "data" / "processed" / "india_destination_geo_master.csv"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "india_destination_master.csv"


# --------------------------------------------------
# LOAD GEOGRAPHIC MASTER
# --------------------------------------------------

df = pd.read_csv(INPUT_FILE)


# --------------------------------------------------
# ADD TRAVELIQ DESTINATION FIELDS
# --------------------------------------------------

new_columns = {
    "state_region": pd.NA,
    "destination_type": pd.NA,
    "tourist_rating": pd.NA,
    "safety_score": pd.NA,
    "avg_daily_cost": pd.NA,
    "accommodation_cost": pd.NA,
    "food_cost": pd.NA,
    "transport_cost": pd.NA,
    "activity_cost": pd.NA,
    "best_months": pd.NA,
    "recommended_stay_days": pd.NA,
    "currency": "INR",
    "visa_requirement": "Not applicable",

    # Interest scores
    "adventure_score": pd.NA,
    "beach_score": pd.NA,
    "nature_score": pd.NA,
    "culture_score": pd.NA,
    "food_score": pd.NA,
    "nightlife_score": pd.NA,
    "romance_score": pd.NA,
    "wildlife_score": pd.NA,
    "winter_score": pd.NA,
    "wellness_score": pd.NA,
}


for column, default_value in new_columns.items():
    df[column] = default_value


# --------------------------------------------------
# REORDER COLUMNS
# --------------------------------------------------

column_order = [
    "destination_name",
    "country",
    "country_code",
    "state_region",
    "geo_name",
    "mapping_type",
    "latitude",
    "longitude",

    "destination_type",

    "tourist_rating",
    "safety_score",

    "avg_daily_cost",
    "accommodation_cost",
    "food_cost",
    "transport_cost",
    "activity_cost",

    "best_months",
    "recommended_stay_days",

    "currency",
    "visa_requirement",

    "adventure_score",
    "beach_score",
    "nature_score",
    "culture_score",
    "food_score",
    "nightlife_score",
    "romance_score",
    "wildlife_score",
    "winter_score",
    "wellness_score",

    "source",
    "source_type",
    "match_status",
]


df = df[column_order]


# --------------------------------------------------
# SAVE
# --------------------------------------------------

df.to_csv(OUTPUT_FILE, index=False)


# --------------------------------------------------
# VALIDATION
# --------------------------------------------------

print("\nIndia Destination Master Dataset Created!")
print("-" * 50)

print(f"Rows: {len(df)}")
print(f"Columns: {len(df.columns)}")

print("\nDestination names:")
print(df["destination_name"].to_string(index=False))

print("\nMissing coordinates:")
print(
    df[["latitude", "longitude"]]
    .isna()
    .any(axis=1)
    .sum()
)

print("\nSaved to:")
print(OUTPUT_FILE)

print("\n[Done]")