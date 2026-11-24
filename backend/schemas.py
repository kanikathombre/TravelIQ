# Pydantic schemas for TravelIQ API
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class UserPreferencesRequest(BaseModel):
    daily_budget_inr: float = Field(..., gt=0, description="Per-person per-day budget in INR")
    travel_months: list[int] = Field(..., description="Month numbers 1–12")
    trip_duration_days: int = Field(..., ge=1, le=365)
    interests: list[str] = Field(default_factory=list)
    traveler_type: str = Field(default="solo")
    travel_style: str = Field(default="standard")
    destination_scope: str = Field(default="all")
    max_total_budget_inr: Optional[float] = Field(default=None, gt=0)

    @field_validator("travel_months")
    @classmethod
    def validate_months(cls, v):
        for m in v:
            if not 1 <= m <= 12:
                raise ValueError(f"Month {m} out of range 1–12")
        return v

    @field_validator("traveler_type")
    @classmethod
    def validate_traveler(cls, v):
        allowed = {"solo", "couple", "family", "friends"}
        if v.lower() not in allowed:
            raise ValueError(f"traveler_type must be one of {allowed}")
        return v.lower()

    @field_validator("travel_style")
    @classmethod
    def validate_style(cls, v):
        allowed = {"budget", "standard", "premium"}
        if v.lower() not in allowed:
            raise ValueError(f"travel_style must be one of {allowed}")
        return v.lower()

    @field_validator("destination_scope")
    @classmethod
    def validate_scope(cls, v):
        allowed = {"all", "india", "international"}
        if v.lower() not in allowed:
            raise ValueError(f"destination_scope must be one of {allowed}")
        return v.lower()


class ComponentScoreOut(BaseModel):
    value: Optional[float]
    explanation: str
    weight: float


class RecommendationOut(BaseModel):
    destination_name: str
    country: str
    state_region: str
    destination_type: str
    latitude: float
    longitude: float
    best_months: str
    recommended_stay_days: Optional[float]
    avg_daily_cost_inr: Optional[float]
    estimated_total_cost_inr: Optional[float]
    currency: str
    overall_score: Optional[float]
    components: dict[str, ComponentScoreOut]
    explanations: list[str]
    data_warnings: list[str]
    interest_scores: dict[str, float]


class RecommendationResponse(BaseModel):
    query_summary: str
    count: int
    results: list[RecommendationOut]
    system_note: str = (
        "Scores are produced by a content-based weighted recommendation system. "
        "They are not trained model predictions. Missing data is reported in data_warnings."
    )


class CostEstimateRequest(BaseModel):
    destination_name: str
    trip_duration_days: int = Field(..., ge=1)
    travel_style: str = Field(default="standard")
    party_size: int = Field(default=1, ge=1, le=20)
    intercity_transport_inr: Optional[float] = Field(default=None, ge=0)

    @field_validator("travel_style")
    @classmethod
    def validate_style(cls, v):
        allowed = {"budget", "standard", "premium"}
        if v.lower() not in allowed:
            raise ValueError(f"travel_style must be one of {allowed}")
        return v.lower()


class CostBreakdown(BaseModel):
    destination_name: str
    trip_duration_days: int
    party_size: int
    travel_style: str
    style_multiplier: float
    accommodation_cost_per_person_per_day: Optional[float]
    food_cost_per_person_per_day: Optional[float]
    transport_cost_per_person_per_day: Optional[float]
    activity_cost_per_person_per_day: Optional[float]
    avg_daily_cost_per_person: Optional[float]
    intercity_transport_total_inr: Optional[float]
    destination_cost_per_person_total: Optional[float]
    total_trip_cost_per_person: Optional[float]
    total_trip_cost_all_party: Optional[float]
    currency: str
    cost_data_quality: str
    data_warnings: list[str]
    methodology_note: str = (
        "Accommodation assumes double occupancy. Costs are mid-range estimates "
        "for the standard travel style. Style multipliers (budget: 0.70×, "
        "standard: 1.00×, premium: 1.60×) are provisional assumptions — "
        "not calibrated against live booking data."
    )


class DestinationOut(BaseModel):
    destination_name: str
    country: str
    state_region: str
    destination_type: str
    latitude: float
    longitude: float
    best_months: str
    recommended_stay_days: Optional[float]
    avg_daily_cost_inr: Optional[float]
    accommodation_cost: Optional[float]
    food_cost: Optional[float]
    transport_cost: Optional[float]
    activity_cost: Optional[float]
    currency: str
    cost_data_quality: Optional[str]
    tourist_rating: Optional[float]
    safety_score: Optional[float]
    adventure_score: Optional[float]
    beach_score: Optional[float]
    nature_score: Optional[float]
    culture_score: Optional[float]
    food_score: Optional[float]
    nightlife_score: Optional[float]
    romance_score: Optional[float]
    wildlife_score: Optional[float]
    winter_score: Optional[float]
    wellness_score: Optional[float]
    source: Optional[str]


class AnalyticsOverview(BaseModel):
    total_destinations: int
    total_countries: int
    total_states: int
    destination_type_counts: dict[str, int]
    cost_data_coverage_pct: float
    interest_data_coverage_pct: float


class CostAnalytics(BaseModel):
    avg_accommodation_cost: Optional[float]
    avg_food_cost: Optional[float]
    avg_transport_cost: Optional[float]
    avg_activity_cost: Optional[float]
    avg_daily_cost: Optional[float]
    min_daily_cost: Optional[float]
    max_daily_cost: Optional[float]
    destinations_with_cost_data: int
    destinations_missing_cost_data: int
    data_note: str = "All costs in INR, per person per day, mid-range standard style"


class SeasonalityMonth(BaseModel):
    month: str
    month_num: int
    destination_count: int


class SeasonalityAnalytics(BaseModel):
    monthly_counts: list[SeasonalityMonth]
    note: str = "Each destination may be counted in multiple months"
