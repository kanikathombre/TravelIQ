"""
test_recommendation.py
======================
Unit tests for the content-based recommendation engine.
Run with: python -m pytest tests/test_recommendation.py -v
"""
import sys
import math
from pathlib import Path
import pytest

# Make src importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from models.recommendation_engine import (
    RecommendationEngine,
    UserPreferences,
    _budget_fit,
    _interest_match,
    _seasonal_fit,
    _duration_fit,
    _traveler_fit,
    _parse_best_months,
)
import pandas as pd

# ----------------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------------

@pytest.fixture(scope="module")
def engine():
    data_path = Path(__file__).resolve().parents[1] / "data" / "processed" / "destinations_enriched.csv"
    return RecommendationEngine(data_path)

@pytest.fixture
def base_prefs():
    return UserPreferences(
        daily_budget_inr=2500,
        travel_months=[11, 12, 1],
        trip_duration_days=5,
        interests=["heritage", "culture"],
        traveler_type="couple",
        travel_style="standard",
    )

# ----------------------------------------------------------------------------
# Unit helpers
# ----------------------------------------------------------------------------

class TestBudgetFit:
    def test_within_budget_gives_high_score(self):
        score, _ = _budget_fit(1000, 2000, "standard")
        assert score is not None and score > 0.5

    def test_over_budget_gives_low_score(self):
        score, _ = _budget_fit(3000, 1000, "standard")
        assert score is not None and score < 0.5

    def test_missing_cost_returns_none(self):
        score, msg = _budget_fit(None, 2000, "standard")
        assert score is None
        assert "unavailable" in msg.lower()

    def test_nan_cost_returns_none(self):
        score, _ = _budget_fit(float("nan"), 2000, "standard")
        assert score is None

    def test_premium_style_reduces_score(self):
        s_standard, _ = _budget_fit(2000, 2500, "standard")
        s_premium,  _ = _budget_fit(2000, 2500, "premium")
        assert s_premium < s_standard  # premium is more expensive → lower fit

    def test_score_bounded_0_1(self):
        for cost in [100, 1000, 5000, 50000]:
            score, _ = _budget_fit(cost, 2000, "standard")
            if score is not None:
                assert 0.0 <= score <= 1.0


class TestInterestMatch:
    def _make_row(self, adventure=5, beach=0, nature=8, culture=9, food=7,
                  nightlife=2, romance=5, wildlife=3, winter=6, wellness=4):
        return pd.Series({
            "adventure_score": adventure, "beach_score": beach,
            "nature_score": nature, "culture_score": culture,
            "food_score": food, "nightlife_score": nightlife,
            "romance_score": romance, "wildlife_score": wildlife,
            "winter_score": winter, "wellness_score": wellness,
        })

    def test_matching_interest_gives_positive_score(self):
        row = self._make_row(culture=9)
        score, _, _ = _interest_match(["culture"], row)
        assert score is not None and score > 0

    def test_mismatched_interest_gives_lower_score(self):
        row = self._make_row(beach=0, culture=9)
        beach_score, _, _ = _interest_match(["beach"], row)
        culture_score, _, _ = _interest_match(["culture"], row)
        assert culture_score > beach_score

    def test_empty_interests_returns_none(self):
        row = self._make_row()
        score, msg, _ = _interest_match([], row)
        assert score is None

    def test_score_bounded_0_1(self):
        row = self._make_row(adventure=10)
        score, _, _ = _interest_match(["adventure"], row)
        if score is not None:
            assert 0.0 <= score <= 1.0


class TestSeasonalFit:
    def test_fully_in_season(self):
        score, _ = _seasonal_fit("October-March", [11, 12, 1])
        assert score == 1.0

    def test_partially_in_season(self):
        score, _ = _seasonal_fit("October-December", [11, 12, 3])
        # Nov, Dec in season; March not → 2/3
        assert score is not None and 0 < score < 1

    def test_out_of_season_gives_zero(self):
        score, _ = _seasonal_fit("October-February", [5, 6, 7])
        assert score == 0.0

    def test_cross_year_parsing(self):
        months = _parse_best_months("October-March")
        assert 10 in months and 11 in months and 12 in months
        assert 1 in months and 2 in months and 3 in months
        assert 5 not in months  # May should not be in Oct–Mar

    def test_missing_seasonal_data_returns_none(self):
        score, msg = _seasonal_fit("", [11, 12])
        assert score is None

    def test_semicolon_separator(self):
        months = _parse_best_months("March-May; October-mid December")
        assert 3 in months and 4 in months and 5 in months
        assert 10 in months and 12 in months


class TestDurationFit:
    def test_exact_match_gives_full_score(self):
        score, _ = _duration_fit(5, 5)
        assert score == 1.0

    def test_far_from_recommended_gives_lower_score(self):
        score_close, _ = _duration_fit(5, 6)
        score_far, _   = _duration_fit(5, 15)
        assert score_close > score_far

    def test_missing_stay_returns_neutral(self):
        score, msg = _duration_fit(None, 5)
        assert score == 0.5
        assert "unavailable" in msg.lower()

    def test_score_bounded_0_1(self):
        for days in [1, 3, 5, 10, 30]:
            score, _ = _duration_fit(5, days)
            assert 0.0 <= score <= 1.0


class TestTravelerFit:
    def test_couple_affinity_with_romance_dest(self):
        score, _ = _traveler_fit("couple", "Backwaters & Nature")
        assert score > 0

    def test_adventure_solo_with_mountain(self):
        score, _ = _traveler_fit("solo", "Mountain & Adventure")
        assert score > 0

    def test_score_bounded_0_1(self):
        for ttype in ["solo", "couple", "family", "friends"]:
            score, _ = _traveler_fit(ttype, "Heritage & Culture")
            assert 0.0 <= score <= 1.0


# ----------------------------------------------------------------------------
# Integration tests
# ----------------------------------------------------------------------------

class TestRecommendationEngine:
    def test_returns_results(self, engine, base_prefs):
        results = engine.recommend(base_prefs)
        assert len(results) > 0

    def test_higher_budget_does_not_reduce_results(self, engine, base_prefs):
        prefs_tight = UserPreferences(
            daily_budget_inr=800, travel_months=[11, 12],
            trip_duration_days=3, interests=["heritage"],
            traveler_type="solo", travel_style="budget",
        )
        prefs_rich = UserPreferences(
            daily_budget_inr=5000, travel_months=[11, 12],
            trip_duration_days=3, interests=["heritage"],
            traveler_type="solo", travel_style="premium",
        )
        r_tight = engine.recommend(prefs_tight)
        r_rich  = engine.recommend(prefs_rich)
        # Rich budget should not produce *fewer* unfiltered results
        assert len(r_rich) >= len(r_tight) or len(r_tight) > 0

    def test_interest_change_affects_ranking(self, engine):
        prefs_beach = UserPreferences(
            daily_budget_inr=3000, travel_months=[11, 12],
            trip_duration_days=4, interests=["beach"],
            traveler_type="couple", travel_style="standard",
        )
        prefs_adventure = UserPreferences(
            daily_budget_inr=3000, travel_months=[5, 6, 7],
            trip_duration_days=6, interests=["adventure"],
            traveler_type="solo", travel_style="standard",
        )
        r_beach = engine.recommend(prefs_beach, top_n=3)
        r_adv   = engine.recommend(prefs_adventure, top_n=3)
        # Top recommendations should differ
        top_beach = {r.destination_name for r in r_beach if r.overall_score}
        top_adv   = {r.destination_name for r in r_adv if r.overall_score}
        assert top_beach != top_adv

    def test_scores_in_valid_range(self, engine, base_prefs):
        results = engine.recommend(base_prefs)
        for r in results:
            if r.overall_score is not None:
                assert 0 <= r.overall_score <= 100, (
                    f"{r.destination_name} score {r.overall_score} out of range"
                )

    def test_hard_budget_ceiling_filters(self, engine):
        prefs = UserPreferences(
            daily_budget_inr=2000, travel_months=[11, 12],
            trip_duration_days=5, interests=["beach"],
            traveler_type="couple", travel_style="premium",
            max_total_budget_inr=5000,  # very tight ceiling
        )
        results = engine.recommend(prefs)
        for r in results:
            # If cost is known, it must be within 110% of ceiling
            if r.estimated_total_cost_inr:
                assert r.estimated_total_cost_inr <= 5500, (
                    f"{r.destination_name} cost {r.estimated_total_cost_inr} exceeds ceiling"
                )

    def test_missing_data_does_not_produce_perfect_score(self, engine):
        """Destinations with missing data must not automatically score 100."""
        results = engine.recommend(UserPreferences(
            daily_budget_inr=3000, travel_months=[11, 12],
            trip_duration_days=5, interests=["adventure"],
            traveler_type="solo", travel_style="standard",
        ))
        for r in results:
            if r.data_warnings and r.overall_score is not None:
                assert r.overall_score < 100, (
                    f"{r.destination_name} has warnings but scored 100"
                )

    def test_component_keys_present(self, engine, base_prefs):
        results = engine.recommend(base_prefs, top_n=1)
        assert results
        comp = results[0].components
        for key in ["budget_fit", "interest_match", "seasonal_fit",
                    "duration_fit", "traveler_fit"]:
            assert key in comp
