import pandas as pd
import zipfile
from pathlib import Path


# ============================================
# TRAVELIQ - GeoNames Data Pipeline
# ============================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "cities500.zip"
PROCESSED_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "geonames_cities_clean.csv"


# GeoNames column names
GEONAMES_COLUMNS = [
    "geoname_id",
    "name",
    "ascii_name",
    "alternate_names",
    "latitude",
    "longitude",
    "feature_class",
    "feature_code",
    "country_code",
    "cc2",
    "admin1_code",
    "admin2_code",
    "admin3_code",
    "admin4_code",
    "population",
    "elevation",
    "dem",
    "timezone",
    "modification_date"
]


print("TRAVELIQ - GeoNames Data Pipeline")
print("=" * 45)


# --------------------------------------------
# 1. Check raw dataset
# --------------------------------------------

if not RAW_DATA_PATH.exists():
    raise FileNotFoundError(
        f"GeoNames dataset not found: {RAW_DATA_PATH}"
    )

print(f"Raw dataset found: {RAW_DATA_PATH}")


# --------------------------------------------
# 2. Load GeoNames dataset
# --------------------------------------------

with zipfile.ZipFile(RAW_DATA_PATH, "r") as zip_file:

    txt_file = zip_file.namelist()[0]

    with zip_file.open(txt_file) as file:

        df = pd.read_csv(
            file,
            sep="\t",
            header=None,
            names=GEONAMES_COLUMNS,
            low_memory=False
        )


print(f"\nOriginal rows: {len(df):,}")


# --------------------------------------------
# 3. Keep only populated places
# --------------------------------------------

df = df[df["feature_class"] == "P"].copy()

print(f"Rows after keeping populated places: {len(df):,}")


# --------------------------------------------
# 4. Remove rows without essential fields
# --------------------------------------------

df = df.dropna(
    subset=[
        "geoname_id",
        "name",
        "country_code",
        "latitude",
        "longitude"
    ]
)

print(f"Rows after removing incomplete records: {len(df):,}")


# --------------------------------------------
# 5. Keep useful columns
# --------------------------------------------

df = df[
    [
        "geoname_id",
        "name",
        "ascii_name",
        "latitude",
        "longitude",
        "country_code",
        "admin1_code",
        "population",
        "timezone"
    ]
].copy()


# --------------------------------------------
# 6. Rename columns
# --------------------------------------------

df = df.rename(
    columns={
        "geoname_id": "geoname_id",
        "name": "city",
        "ascii_name": "city_ascii",
        "country_code": "country_code",
        "admin1_code": "region_code"
    }
)


# --------------------------------------------
# 7. Remove duplicate cities
# --------------------------------------------

df = df.drop_duplicates(
    subset=["city", "country_code", "latitude", "longitude"]
)


# --------------------------------------------
# 8. Sort data
# --------------------------------------------

df = df.sort_values(
    by=["country_code", "city"]
).reset_index(drop=True)


# --------------------------------------------
# 9. Save cleaned dataset
# --------------------------------------------

PROCESSED_DATA_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

df.to_csv(
    PROCESSED_DATA_PATH,
    index=False
)


# --------------------------------------------
# 10. Final report
# --------------------------------------------

print("\nCleaning complete!")
print("-" * 45)

print(f"Final rows: {len(df):,}")
print(f"Final columns: {len(df.columns)}")

print("\nColumns:")
print(df.columns.tolist())

print("\nMissing values:")
print(df.isnull().sum())

print("\nFirst 5 rows:")
print(df.head())

print("\nSaved to:")
print(PROCESSED_DATA_PATH)