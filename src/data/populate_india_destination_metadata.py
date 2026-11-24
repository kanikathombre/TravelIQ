import pandas as pd
from pathlib import Path


# --------------------------------------------------
# PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "india_destination_master.csv"
)

OUTPUT_FILE = INPUT_FILE


# --------------------------------------------------
# LOAD DATASET
# --------------------------------------------------

df = pd.read_csv(INPUT_FILE)


# --------------------------------------------------
# DESTINATION METADATA
# --------------------------------------------------

metadata = {

    "Hampi": {
        "state_region": "Karnataka",
        "destination_type": "Heritage",
        "best_months": "October-February",
        "recommended_stay_days": 2,
    },

    "Mysuru": {
        "state_region": "Karnataka",
        "destination_type": "Heritage & Culture",
        "best_months": "October-February",
        "recommended_stay_days": 2,
    },

    "Kumarakom": {
        "state_region": "Kerala",
        "destination_type": "Backwaters & Nature",
        "best_months": "October-March",
        "recommended_stay_days": 2,
    },

    "Shillong": {
        "state_region": "Meghalaya",
        "destination_type": "Hill Station & Nature",
        "best_months": "October-April",
        "recommended_stay_days": 3,
    },

    "Sohra": {
        "state_region": "Meghalaya",
        "destination_type": "Nature & Adventure",
        "best_months": "October-April",
        "recommended_stay_days": 2,
    },

    "Jodhpur": {
        "state_region": "Rajasthan",
        "destination_type": "Heritage & Culture",
        "best_months": "October-March",
        "recommended_stay_days": 2,
    },

    "Gangtok": {
        "state_region": "Sikkim",
        "destination_type": "Mountain & Nature",
        "best_months": "March-May; October-mid December",
        "recommended_stay_days": 3,
    },

    "Leh": {
        "state_region": "Ladakh",
        "destination_type": "Mountain & Adventure",
        "best_months": "May-September",
        "recommended_stay_days": 4,
    },

    "Kargil": {
        "state_region": "Ladakh",
        "destination_type": "Mountain & Heritage",
        "best_months": "May-September",
        "recommended_stay_days": 2,
    },

    "Lakshadweep": {
        "state_region": "Lakshadweep",
        "destination_type": "Beach & Island",
        "best_months": "October-March",
        "recommended_stay_days": 4,
    },

    "Puducherry": {
        "state_region": "Puducherry",
        "destination_type": "Beach & Culture",
        "best_months": "October-March",
        "recommended_stay_days": 3,
    },

    "Gwalior": {
        "state_region": "Madhya Pradesh",
        "destination_type": "Heritage & Culture",
        "best_months": "October-March",
        "recommended_stay_days": 2,
    },

    "Chitrakoot": {
        "state_region": "Madhya Pradesh / Uttar Pradesh",
        "destination_type": "Spiritual & Nature",
        "best_months": "October-March",
        "recommended_stay_days": 2,
    },

    "Amritsar": {
        "state_region": "Punjab",
        "destination_type": "Heritage & Culture",
        "best_months": "October-March",
        "recommended_stay_days": 2,
    },

    "Kapurthala": {
        "state_region": "Punjab",
        "destination_type": "Heritage & Culture",
        "best_months": "October-March",
        "recommended_stay_days": 1,
    },

    "Bundi": {
        "state_region": "Rajasthan",
        "destination_type": "Heritage & Culture",
        "best_months": "October-March",
        "recommended_stay_days": 2,
    },

    "Mamallapuram": {
        "state_region": "Tamil Nadu",
        "destination_type": "Heritage & Beach",
        "best_months": "October-March",
        "recommended_stay_days": 2,
    },

    "Nilgiris": {
        "state_region": "Tamil Nadu",
        "destination_type": "Hill Station & Nature",
        "best_months": "October-June",
        "recommended_stay_days": 3,
    },

    "Agartala": {
        "state_region": "Tripura",
        "destination_type": "Culture & Heritage",
        "best_months": "October-March",
        "recommended_stay_days": 2,
    },

    "Unakoti": {
        "state_region": "Tripura",
        "destination_type": "Heritage & Nature",
        "best_months": "October-March",
        "recommended_stay_days": 2,
    },
}


# --------------------------------------------------
# APPLY METADATA
# --------------------------------------------------

for column in [
    "state_region",
    "destination_type",
    "best_months",
]:
    df[column] = df[column].astype("string")


for column in [
    "recommended_stay_days",
]:
    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )


for destination, values in metadata.items():

    mask = df["destination_name"] == destination

    if not mask.any():
        print(f"WARNING: {destination} not found in dataset")
        continue

    for column, value in values.items():
        df.loc[mask, column] = value


# --------------------------------------------------
# VALIDATION
# --------------------------------------------------

required_columns = [
    "state_region",
    "destination_type",
    "best_months",
    "recommended_stay_days",
]


print("\nIndia Destination Metadata Updated!")
print("-" * 50)

print(f"Rows: {len(df)}")

print("\nMissing metadata values:")

for column in required_columns:
    missing = df[column].isna().sum()
    print(f"{column}: {missing}")


print("\nDestination metadata:")
print(
    df[
        [
            "destination_name",
            "state_region",
            "destination_type",
            "best_months",
            "recommended_stay_days",
        ]
    ].to_string(index=False)
)


# --------------------------------------------------
# SAVE
# --------------------------------------------------

df.to_csv(OUTPUT_FILE, index=False)

print("\nSaved to:")
print(OUTPUT_FILE)

print("\n[Done]")