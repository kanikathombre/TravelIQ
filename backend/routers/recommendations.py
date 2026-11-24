"""
recommendations.py — /api/recommendations router
"""
from __future__ import annotations
from fastapi import APIRouter
from backend.schemas import (
    UserPreferencesRequest, RecommendationResponse, RecommendationOut, ComponentScoreOut
)
from backend.services import recommendation_service

router = APIRouter(prefix="/api/recommendations", tags=["Recommendations"])


@router.post("", response_model=RecommendationResponse)
def get_recommendations(body: UserPreferencesRequest, top_n: int = 20):
    """
    Returns a ranked list of destinations matching user preferences.
    Uses a content-based weighted scoring system (not a trained predictive model).
    Missing data is reported in data_warnings — not treated as a perfect match.
    """
    results = recommendation_service.run_recommendations(body.model_dump(), top_n=top_n)

    out_list = []
    for r in results:
        comps = {
            k: ComponentScoreOut(
                value=c.value, explanation=c.explanation, weight=c.weight
            )
            for k, c in r.components.items()
        }
        out_list.append(RecommendationOut(
            destination_name=r.destination_name,
            country=r.country,
            state_region=r.state_region,
            destination_type=r.destination_type,
            latitude=r.latitude,
            longitude=r.longitude,
            best_months=r.best_months,
            recommended_stay_days=r.recommended_stay_days,
            avg_daily_cost_inr=r.avg_daily_cost_inr,
            estimated_total_cost_inr=r.estimated_total_cost_inr,
            currency=r.currency,
            overall_score=r.overall_score,
            components=comps,
            explanations=r.explanations,
            data_warnings=r.data_warnings,
            interest_scores=r.interest_scores,
        ))

    months_str = ", ".join(
        ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"][m-1]
        for m in body.travel_months
    )
    summary = (
        f"{body.traveler_type.title()} traveller, ₹{body.daily_budget_inr:,.0f}/day budget, "
        f"{body.trip_duration_days} days, {months_str}, "
        f"interests: {', '.join(body.interests) or 'any'}"
    )

    return RecommendationResponse(
        query_summary=summary,
        count=len(out_list),
        results=out_list,
    )
