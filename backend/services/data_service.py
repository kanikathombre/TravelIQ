"""
data_service.py
===============
Loads and caches destination data from CSV.
Provides typed access for routers and the recommendation service.
"""
from __future__ import annotations
import math
from pathlib import Path
from typing import Optional
import pandas as pd

_DATA_PATH = (
    Path(__file__).resolve().parents[2]
    / "data" / "processed" / "destinations_enriched.csv"
)

_df: Optional[pd.DataFrame] = None


def _load() -> pd.DataFrame:
    global _df
    if _df is None:
        _df = pd.read_csv(_DATA_PATH)
        print(f"[DataService] Loaded {len(_df)} destinations")
    return _df


def get_all() -> pd.DataFrame:
    return _load().copy()


def get_by_name(name: str) -> Optional[pd.Series]:
    df = _load()
    match = df[df["destination_name"].str.lower() == name.lower()]
    if match.empty:
        return None
    return match.iloc[0]


def get_filter_options() -> dict:
    df = _load()
    types  = sorted(df["destination_type"].dropna().unique().tolist())
    states = sorted(df["state_region"].dropna().unique().tolist())
    return {"destination_types": types, "states": states, "interests": [
        "adventure", "beach", "nature", "culture", "food",
        "nightlife", "romance", "wildlife", "winter", "wellness",
    ]}


def _nan_to_none(v):
    if v is None:
        return None
    try:
        if math.isnan(float(v)):
            return None
    except (TypeError, ValueError):
        pass
    return v


def row_to_dict(row: pd.Series) -> dict:
    d = row.to_dict()
    return {k: _nan_to_none(v) for k, v in d.items()}
