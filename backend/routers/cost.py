"""
cost.py — /api/cost router
"""
from __future__ import annotations
import math
from fastapi import APIRouter, HTTPException
from backend.schemas import CostEstimateRequest, CostBreakdown
from backend.services import data_service

router = APIRouter(prefix="/api/cost", tags=["Cost"])

STYLE_MULTIPLIERS = {"budget": 0.70, "standard": 1.00, "premium": 1.60}


@router.post("/estimate", response_model=CostBreakdown)
def estimate_cost(body: CostEstimateRequest):
    """
    Returns a full cost breakdown for a trip.
    Costs are per-person estimates. Accommodation assumes double occupancy
    (two people sharing one room). Travel-style multipliers are provisional
    assumptions, not calibrated against live booking data.
    """
    row = data_service.get_by_name(body.destination_name)
    if row is None:
        raise HTTPException(404, f"Destination '{body.destination_name}' not found")

    d = data_service.row_to_dict(row)
    warnings: list[str] = []

    def _get(field):
        v = d.get(field)
        if v is None or (isinstance(v, float) and math.isnan(v)):
            warnings.append(f"'{field}' data not available for {body.destination_name}")
            return None
        return float(v)

    mult = STYLE_MULTIPLIERS[body.travel_style]
    accom  = _get("accommodation_cost")
    food   = _get("food_cost")
    trans  = _get("transport_cost")
    activ  = _get("activity_cost")
    daily  = _get("avg_daily_cost")

    # Apply style multiplier
    def apply(v):
        return round(v * mult, 2) if v is not None else None

    daily_pp = apply(daily)
    dest_cost_pp = round(daily_pp * body.trip_duration_days, 2) if daily_pp else None
    intercity = body.intercity_transport_inr

    total_pp: float | None = None
    if dest_cost_pp is not None:
        total_pp = dest_cost_pp + (intercity or 0)
    elif intercity is not None:
        total_pp = intercity
        warnings.append("Destination daily cost unavailable — total includes only intercity transport")

    total_all: float | None = round(total_pp * body.party_size, 2) if total_pp else None

    quality = d.get("cost_data_quality") or "missing"
    if quality == "missing":
        warnings.append("Cost data quality is 'missing' — estimates may be unreliable")

    return CostBreakdown(
        destination_name=body.destination_name,
        trip_duration_days=body.trip_duration_days,
        party_size=body.party_size,
        travel_style=body.travel_style,
        style_multiplier=mult,
        accommodation_cost_per_person_per_day=apply(accom),
        food_cost_per_person_per_day=apply(food),
        transport_cost_per_person_per_day=apply(trans),
        activity_cost_per_person_per_day=apply(activ),
        avg_daily_cost_per_person=daily_pp,
        intercity_transport_total_inr=intercity,
        destination_cost_per_person_total=dest_cost_pp,
        total_trip_cost_per_person=total_pp,
        total_trip_cost_all_party=total_all,
        currency=str(d.get("currency") or "INR"),
        cost_data_quality=quality,
        data_warnings=warnings,
    )
