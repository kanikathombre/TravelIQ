"""
recommendation_service.py
=========================
Bridges the FastAPI router and the standalone recommendation engine.
"""
from __future__ import annotations
import sys
from pathlib import Path
from typing import Any

# Make src importable when running from backend directory
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from models.recommendation_engine import RecommendationEngine, UserPreferences

_engine: RecommendationEngine | None = None


def get_engine() -> RecommendationEngine:
    global _engine
    if _engine is None:
        _engine = RecommendationEngine()
    return _engine


def run_recommendations(payload: dict, top_n: int = 20) -> list[Any]:
    engine = get_engine()
    prefs = UserPreferences(
        daily_budget_inr=payload["daily_budget_inr"],
        travel_months=payload["travel_months"],
        trip_duration_days=payload["trip_duration_days"],
        interests=payload.get("interests", []),
        traveler_type=payload.get("traveler_type", "solo"),
        travel_style=payload.get("travel_style", "standard"),
        destination_scope=payload.get("destination_scope", "all"),
        max_total_budget_inr=payload.get("max_total_budget_inr"),
    )
    return engine.recommend(prefs, top_n=top_n)
