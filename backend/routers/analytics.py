"""
analytics.py — /api/analytics router
"""
from __future__ import annotations
import math
from fastapi import APIRouter
from backend.schemas import AnalyticsOverview, CostAnalytics, SeasonalityAnalytics, SeasonalityMonth
from backend.services import data_service

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

MONTH_ABBREV = {
    "jan": "january","feb": "february","mar": "march","apr": "april",
    "may": "may","jun": "june","jul": "july","aug": "august",
    "sep": "september","oct": "october","nov": "november","dec": "december",
    "mid december": "december",
}
MONTH_MAP = {k: v for v, k in enumerate(
    ["january","february","march","april","may","june",
     "july","august","september","october","november","december"], start=1
)}


def _parse_months(raw: str) -> set[int]:
    if not raw or (isinstance(raw, float) and math.isnan(raw)):
        return set()
    months: set[int] = set()
    for part in str(raw).replace(";", ",").split(","):
        part = part.strip().lower()
        if "-" in part:
            tokens = [t.strip() for t in part.split("-", 1)]
            s = MONTH_ABBREV.get(tokens[0], tokens[0])
            e = MONTH_ABBREV.get(tokens[1], tokens[1])
            si, ei = MONTH_MAP.get(s), MONTH_MAP.get(e)
            if si and ei:
                if si <= ei:
                    months.update(range(si, ei + 1))
                else:
                    months.update(range(si, 13))
                    months.update(range(1, ei + 1))
        else:
            clean = MONTH_ABBREV.get(part, part)
            idx = MONTH_MAP.get(clean)
            if idx:
                months.add(idx)
    return months


@router.get("/overview", response_model=AnalyticsOverview)
def overview():
    df = data_service.get_all()
    cost_cols = ["accommodation_cost","food_cost","transport_cost","activity_cost"]
    has_cost = df[cost_cols].notna().all(axis=1).sum()
    score_cols = ["adventure_score","beach_score","nature_score","culture_score"]
    has_scores = df[score_cols].notna().all(axis=1).sum()
    type_counts = df["destination_type"].value_counts().to_dict()
    return AnalyticsOverview(
        total_destinations=len(df),
        total_countries=df["country"].nunique(),
        total_states=df["state_region"].nunique(),
        destination_type_counts=type_counts,
        cost_data_coverage_pct=round(has_cost / len(df) * 100, 1),
        interest_data_coverage_pct=round(has_scores / len(df) * 100, 1),
    )


@router.get("/costs", response_model=CostAnalytics)
def costs():
    df = data_service.get_all()
    def safe_mean(col):
        v = df[col].dropna()
        return round(float(v.mean()), 2) if len(v) else None
    return CostAnalytics(
        avg_accommodation_cost=safe_mean("accommodation_cost"),
        avg_food_cost=safe_mean("food_cost"),
        avg_transport_cost=safe_mean("transport_cost"),
        avg_activity_cost=safe_mean("activity_cost"),
        avg_daily_cost=safe_mean("avg_daily_cost"),
        min_daily_cost=round(float(df["avg_daily_cost"].min()), 2) if df["avg_daily_cost"].notna().any() else None,
        max_daily_cost=round(float(df["avg_daily_cost"].max()), 2) if df["avg_daily_cost"].notna().any() else None,
        destinations_with_cost_data=int(df["avg_daily_cost"].notna().sum()),
        destinations_missing_cost_data=int(df["avg_daily_cost"].isna().sum()),
    )


@router.get("/seasonality", response_model=SeasonalityAnalytics)
def seasonality():
    df = data_service.get_all()
    counts: dict[int, int] = {}
    for _, row in df.iterrows():
        for m in _parse_months(row.get("best_months", "")):
            counts[m] = counts.get(m, 0) + 1
    MONTH_NAMES = ["January","February","March","April","May","June",
                   "July","August","September","October","November","December"]
    monthly = [
        SeasonalityMonth(month=MONTH_NAMES[m-1], month_num=m, destination_count=counts.get(m,0))
        for m in range(1, 13)
    ]
    return SeasonalityAnalytics(monthly_counts=monthly)
