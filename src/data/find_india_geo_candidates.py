import sys

sys.stdout.reconfigure(encoding="utf-8")

from pathlib import Path
import pandas as pd
from difflib import get_close_matches


# --------------------------------------------------
# Paths
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


# --------------------------------------------------
# Load data
# --------------------------------------------------

candidates = pd.read_csv(CANDIDATES_PATH)

cities = pd.read_csv(CITIES_PATH)

india_cities = cities[
    cities["country_code"] == "IN"
].copy()


# --------------------------------------------------
# Find unmatched destinations
# --------------------------------------------------

unmatched = [
    "Kumarakom",
    "Sohra",
    "Lakshadweep",
    "Chitrakoot",
    "Kapurthala",
    "Bundi",
    "Mamallapuram",
    "Nilgiris",
    "Unakoti",
]


# --------------------------------------------------
# Search for possible matches
# --------------------------------------------------

city_names = india_cities["city"].dropna().unique().tolist()

for destination in unmatched:

    print("\n" + "=" * 60)
    print(f"DESTINATION: {destination}")
    print("=" * 60)

    # Exact case-insensitive search
    exact = india_cities[
        india_cities["city"].str.contains(
            destination,
            case=False,
            na=False,
            regex=False
        )
    ]

    if not exact.empty:
        print("\nPossible direct matches:")
        print(
            exact[
                [
                    "city",
                    "latitude",
                    "longitude",
                    "population",
                    "region_code"
                ]
            ].sort_values(
                "population",
                ascending=False
            ).head(10).to_string(index=False)
        )

    # Fuzzy matches
    fuzzy = get_close_matches(
        destination,
        city_names,
        n=10,
        cutoff=0.45
    )

    print("\nFuzzy matches:")

    if fuzzy:
        for name in fuzzy:
            rows = india_cities[
                india_cities["city"] == name
            ]

            print(
                rows[
                    [
                        "city",
                        "latitude",
                        "longitude",
                        "population",
                        "region_code"
                    ]
                ].to_string(index=False)
            )
    else:
        print("No strong fuzzy matches found.")