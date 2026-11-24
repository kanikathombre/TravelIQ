"""
destinations.py — /api/destinations router
"""
from __future__ import annotations
import math
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from backend.schemas import DestinationOut
from backend.services import data_service

router = APIRouter(prefix="/api/destinations", tags=["Destinations"])


def _safe_float(v) -> Optional[float]:
    if v is None:
        return None
    try:
        f = float(v)
        return None if math.isnan(f) else f
    except (TypeError, ValueError):
        return None


def _row_to_out(row) -> DestinationOut:
    d = data_service.row_to_dict(row)
    return DestinationOut(
        destination_name=d.get("destination_name", ""),
        country=d.get("country", ""),
        state_region=d.get("state_region", ""),
        destination_type=d.get("destination_type", ""),
        latitude=float(d.get("latitude") or 0),
        longitude=float(d.get("longitude") or 0),
        best_months=str(d.get("best_months") or ""),
        recommended_stay_days=_safe_float(d.get("recommended_stay_days")),
        avg_daily_cost_inr=_safe_float(d.get("avg_daily_cost")),
        accommodation_cost=_safe_float(d.get("accommodation_cost")),
        food_cost=_safe_float(d.get("food_cost")),
        transport_cost=_safe_float(d.get("transport_cost")),
        activity_cost=_safe_float(d.get("activity_cost")),
        currency=str(d.get("currency") or "INR"),
        cost_data_quality=str(d.get("cost_data_quality") or "missing"),
        tourist_rating=_safe_float(d.get("tourist_rating")),
        safety_score=_safe_float(d.get("safety_score")),
        adventure_score=_safe_float(d.get("adventure_score")),
        beach_score=_safe_float(d.get("beach_score")),
        nature_score=_safe_float(d.get("nature_score")),
        culture_score=_safe_float(d.get("culture_score")),
        food_score=_safe_float(d.get("food_score")),
        nightlife_score=_safe_float(d.get("nightlife_score")),
        romance_score=_safe_float(d.get("romance_score")),
        wildlife_score=_safe_float(d.get("wildlife_score")),
        winter_score=_safe_float(d.get("winter_score")),
        wellness_score=_safe_float(d.get("wellness_score")),
        source=d.get("source"),
    )


@router.get("/filters")
def get_filters():
    """Returns available filter options for the search UI."""
    return data_service.get_filter_options()


@router.get("", response_model=list[DestinationOut])
def list_destinations(
    destination_type: Optional[str] = Query(default=None),
    state: Optional[str] = Query(default=None),
    max_daily_cost: Optional[float] = Query(default=None, gt=0),
):
    df = data_service.get_all()
    if destination_type:
        df = df[df["destination_type"].str.contains(destination_type, case=False, na=False)]
    if state:
        df = df[df["state_region"].str.contains(state, case=False, na=False)]
    if max_daily_cost is not None:
        df = df[df["avg_daily_cost"].isna() | (df["avg_daily_cost"] <= max_daily_cost)]
    return [_row_to_out(row) for _, row in df.iterrows()]


@router.get("/{destination_name}", response_model=DestinationOut)
def get_destination(destination_name: str):
    row = data_service.get_by_name(destination_name)
    if row is None:
        raise HTTPException(status_code=404, detail=f"Destination '{destination_name}' not found")
    return _row_to_out(row)
