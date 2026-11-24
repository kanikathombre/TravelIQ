import sys

sys.stdout.reconfigure(encoding="utf-8")

from pathlib import Path
import pandas as pd


# --------------------------------------------------
# 1. Project paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CANDIDATES_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "india_destination_candidates.csv"
)

CITIES_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "geonames_cities_clean.csv"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "india_destination_geo_master.csv"
)


# --------------------------------------------------
# 2. Load datasets
# --------------------------------------------------

candidates = pd.read_csv(CANDIDATES_PATH)

cities = pd.read_csv(CITIES_PATH)

india_cities = cities[
    cities["country_code"] == "IN"
].copy()


# --------------------------------------------------
# 3. Manual mapping rules
# --------------------------------------------------

manual_mappings = {

    "Kumarakom": {
        "geo_name": "Kumarakom",
        "mapping_type": "destination_area",
        "latitude": 9.617119,
        "longitude": 76.429482
    },

    "Sohra": {
        "geo_name": "Cherrapunjee",
        "mapping_type": "alternate_name"
    },

    "Lakshadweep": {
        "geo_name": "Kavaratti",
        "mapping_type": "representative_location"
    },

    "Chitrakoot": {
        "geo_name": "Chitrakoot Dham",
        "mapping_type": "alternate_name"
    },

    "Kapurthala": {
        "geo_name": "Kapurthala Town",
        "mapping_type": "alternate_name"
    },

    "Bundi": {
        "geo_name": "Būndi",
        "mapping_type": "alternate_name"
    },

    "Mamallapuram": {
        "geo_name": "Mahabalipuram",
        "mapping_type": "alternate_name"
    },

    "Nilgiris": {
        "geo_name": "Udhagamandalam",
        "mapping_type": "destination_region",
        "latitude": 11.4000,
        "longitude": 76.7333
    },

    "Unakoti": {
        "geo_name": "Unakoti",
        "mapping_type": "destination_region",
        "latitude": 24.31661,
        "longitude": 92.06661
    },
}


# --------------------------------------------------
# 4. Build geographic matches
# --------------------------------------------------

exact_matches = []


for _, destination in candidates.iterrows():

    destination_name = destination["destination_name"]

    # --------------------------------------------------
    # Manual mapping
    # --------------------------------------------------

    if destination_name in manual_mappings:

        rule = manual_mappings[destination_name]

        # --------------------------------------------------
        # Case 1: Manual mapping has authoritative
        # coordinates
        # --------------------------------------------------

        if (
            "latitude" in rule
            and "longitude" in rule
        ):

            exact_matches.append({

                "destination_name": destination_name,

                "country": destination["country"],

                "country_code": destination["country_code"],

                "source": destination["source"],

                "source_type": destination["source_type"],

                "geo_name": rule["geo_name"],

                "mapping_type": rule["mapping_type"],

                "latitude": rule["latitude"],

                "longitude": rule["longitude"],

                "population": None,

                "region_code": None,

                "timezone": None,

                "match_status": "mapped"

            })

            continue


        # --------------------------------------------------
        # Case 2: Manual mapping should be found
        # inside GeoNames
        # --------------------------------------------------

        possible = india_cities[
            india_cities["city"].str.lower()
            == rule["geo_name"].lower()
        ]


        # --------------------------------------------------
        # Manual mapping not found
        # --------------------------------------------------

        if possible.empty:

            exact_matches.append({

                "destination_name": destination_name,

                "country": destination["country"],

                "country_code": destination["country_code"],

                "source": destination["source"],

                "source_type": destination["source_type"],

                "geo_name": rule["geo_name"],

                "mapping_type": rule["mapping_type"],

                "latitude": None,

                "longitude": None,

                "population": None,

                "region_code": None,

                "timezone": None,

                "match_status": "needs_review"

            })

        else:

            # If multiple GeoNames records exist,
            # choose the highest-population location.

            row = possible.sort_values(
                "population",
                ascending=False
            ).iloc[0]


            exact_matches.append({

                "destination_name": destination_name,

                "country": destination["country"],

                "country_code": destination["country_code"],

                "source": destination["source"],

                "source_type": destination["source_type"],

                "geo_name": row["city"],

                "mapping_type": rule["mapping_type"],

                "latitude": row["latitude"],

                "longitude": row["longitude"],

                "population": row["population"],

                "region_code": row["region_code"],

                "timezone": row["timezone"],

                "match_status": "mapped"

            })


        continue


    # --------------------------------------------------
    # 5. Normal exact city matching
    # --------------------------------------------------

    possible = india_cities[
        india_cities["city"].str.lower()
        == destination_name.lower()
    ]


    # --------------------------------------------------
    # No exact match
    # --------------------------------------------------

    if possible.empty:

        exact_matches.append({

            "destination_name": destination_name,

            "country": destination["country"],

            "country_code": destination["country_code"],

            "source": destination["source"],

            "source_type": destination["source_type"],

            "geo_name": None,

            "mapping_type": "exact_city",

            "latitude": None,

            "longitude": None,

            "population": None,

            "region_code": None,

            "timezone": None,

            "match_status": "needs_review"

        })


    # --------------------------------------------------
    # Exact match found
    # --------------------------------------------------

    else:

        # If multiple locations have the same name,
        # choose the one with the highest population.

        row = possible.sort_values(
            "population",
            ascending=False
        ).iloc[0]


        exact_matches.append({

            "destination_name": destination_name,

            "country": destination["country"],

            "country_code": destination["country_code"],

            "source": destination["source"],

            "source_type": destination["source_type"],

            "geo_name": row["city"],

            "mapping_type": "exact_city",

            "latitude": row["latitude"],

            "longitude": row["longitude"],

            "population": row["population"],

            "region_code": row["region_code"],

            "timezone": row["timezone"],

            "match_status": "mapped"

        })


# --------------------------------------------------
# 6. Create final DataFrame
# --------------------------------------------------

master = pd.DataFrame(exact_matches)


# --------------------------------------------------
# 7. Data quality checks
# --------------------------------------------------

duplicate_destinations = master[
    master["destination_name"].duplicated(keep=False)
]

missing_coordinates = master[
    master["latitude"].isna()
    | master["longitude"].isna()
]


# --------------------------------------------------
# 8. Save final geographic master
# --------------------------------------------------

master.to_csv(
    OUTPUT_PATH,
    index=False
)


# --------------------------------------------------
# 9. Print summary
# --------------------------------------------------

print("\nIndia destination geographic mapping complete!")

print(
    f"Total destinations: {len(master)}"
)

print(
    f"Mapped: "
    f"{(master['match_status'] == 'mapped').sum()}"
)

print(
    f"Needs review: "
    f"{(master['match_status'] == 'needs_review').sum()}"
)

print(
    f"Duplicate destination names: "
    f"{duplicate_destinations['destination_name'].nunique()}"
)

print(
    f"Missing coordinates: "
    f"{len(missing_coordinates)}"
)


# --------------------------------------------------
# 10. Display mapping results
# --------------------------------------------------

print("\nMapping results:")

print(
    master[
        [
            "destination_name",
            "geo_name",
            "mapping_type",
            "latitude",
            "longitude",
            "match_status"
        ]
    ].to_string(index=False)
)


# --------------------------------------------------
# 11. Display data-quality warnings
# --------------------------------------------------

if not duplicate_destinations.empty:

    print("\nWARNING: Duplicate destinations found:")

    print(
        duplicate_destinations[
            ["destination_name", "geo_name"]
        ].to_string(index=False)
    )


if not missing_coordinates.empty:

    print("\nWARNING: Destinations missing coordinates:")

    print(
        missing_coordinates[
            ["destination_name", "geo_name"]
        ].to_string(index=False)
    )


# --------------------------------------------------
# 12. Output location
# --------------------------------------------------

print("\nSaved to:")

print(OUTPUT_PATH)