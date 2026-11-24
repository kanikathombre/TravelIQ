"""
recommendation_engine.py
=========================
Content-based, explainable travel destination recommendation system.

This is NOT a trained machine learning predictive model.
It is a weighted scoring system with documented, configurable weights.
Scores are computed deterministically from user preferences and
destination attributes.  Each component is explainable and auditable.

Scoring components (weights total 1.0)
----------------------------------------
  budget_fit      0.30  How well the destination's daily cost fits budget
  interest_match  0.30  Cosine similarity between user interests and dest scores
  seasonal_fit    0.20  Proportion of requested travel months that are "best"
  duration_fit    0.10  How well trip length matches recommended stay
  traveler_fit    0.10  Bonus for traveler-type / dest-type affinity

Score range: 0–100 (higher = better match).

Missing data policy
--------------------
- If a destination is missing cost data, budget_fit = None (not 0, not 100).
  The destination is still returned with a data-quality warning.
- If a destination is missing seasonal data, seasonal_fit = None.
- Unavailable components are excluded from the weighted average and a
  warning flag is returned with the result.

Budget tiers (travel style multipliers)
-----------------------------------------
These are provisional assumptions documented in cost-methodology.md:
  budget   → 0.70× of avg_daily_cost (dormitory / street food tier)
  standard → 1.00× (mid-range; default)
  premium  → 1.60× (boutique hotels, sit-down restaurants)
Multipliers are labelled as provisional; not calibrated against booking data.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional
import numpy as np
import pandas as pd
from pathlib import Path

# ---------------------------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------------------------

WEIGHTS = {
    "budget_fit":     0.30,
    "interest_match": 0.30,
    "seasonal_fit":   0.20,
    "duration_fit":   0.10,
    "traveler_fit":   0.10,
}
assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9, "Weights must sum to 1"

TRAVEL_STYLE_MULTIPLIER = {
    "budget":   0.70,
    "standard": 1.00,
    "premium":  1.60,
}

# Provisional affinity map: traveler_type → destination_type keywords that
# receive a +1 bonus (max bonus capped at 1.0 normalised to 0–1).
TRAVELER_AFFINITY: dict[str, list[str]] = {
    "solo":    ["adventure", "heritage", "culture", "mountain", "backpacker"],
    "couple":  ["romance", "backwaters", "beach", "island", "hill station"],
    "family":  ["nature", "wildlife", "heritage", "culture", "hill station"],
    "friends": ["adventure", "beach", "nightlife", "mountain", "food"],
}

INTEREST_COLUMNS = [
    "adventure_score", "beach_score", "nature_score", "culture_score",
    "food_score", "nightlife_score", "romance_score", "wildlife_score",
    "winter_score", "wellness_score",
]

INTEREST_KEYS = [c.replace("_score", "") for c in INTEREST_COLUMNS]

MONTH_MAP = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
}
MONTH_ABBREV = {
    "jan": "january", "feb": "february", "mar": "march", "apr": "april",
    "may": "may", "jun": "june", "jul": "july", "aug": "august",
    "sep": "september", "oct": "october", "nov": "november", "dec": "december",
    "mid december": "december",
}

# ---------------------------------------------------------------------------
# DATA MODELS
# ---------------------------------------------------------------------------

@dataclass
class UserPreferences:
    """All user inputs that drive the recommendation."""
    daily_budget_inr: float          # per person per day in INR
    travel_months: list[int]         # e.g. [11, 12, 1] for Nov–Jan
    trip_duration_days: int          # e.g. 7
    interests: list[str]             # e.g. ["adventure", "nature"]
    traveler_type: str               # solo | couple | family | friends
    travel_style: str                # budget | standard | premium
    destination_scope: str = "all"   # all | india | international
    max_total_budget_inr: Optional[float] = None  # optional hard ceiling

@dataclass
class ComponentScore:
    value: Optional[float]           # 0–1, or None if unavailable
    explanation: str
    weight: float

@dataclass
class RecommendationResult:
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
    overall_score: Optional[float]   # 0–100; None if too many components missing
    components: dict[str, ComponentScore]
    explanations: list[str]
    data_warnings: list[str]
    interest_scores: dict[str, float]

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def _parse_best_months(raw: str) -> set[int]:
    """Parse a best_months string like 'October-March; May-June' → set of month ints."""
    if not raw or (isinstance(raw, float) and math.isnan(raw)):
        return set()
    months: set[int] = set()
    for part in str(raw).replace(";", ",").split(","):
        part = part.strip().lower()
        if "-" in part:
            tokens = [t.strip() for t in part.split("-", 1)]
            start = MONTH_ABBREV.get(tokens[0], tokens[0])
            end   = MONTH_ABBREV.get(tokens[1], tokens[1])
            s_idx = MONTH_MAP.get(start)
            e_idx = MONTH_MAP.get(end)
            if s_idx and e_idx:
                if s_idx <= e_idx:
                    months.update(range(s_idx, e_idx + 1))
                else:  # cross-year (e.g. Oct–Mar)
                    months.update(range(s_idx, 13))
                    months.update(range(1, e_idx + 1))
        else:
            clean = MONTH_ABBREV.get(part, part)
            idx = MONTH_MAP.get(clean)
            if idx:
                months.add(idx)
    return months


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity between two non-negative vectors. Returns 0 if either is zero."""
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def _budget_fit(daily_cost: Optional[float], budget: float,
                style: str) -> tuple[Optional[float], str]:
    """
    Returns a 0–1 score reflecting how affordable the destination is.
    Uses a smooth decay rather than a hard cutoff so near-budget
    destinations still appear in results with a lower score.
    """
    if daily_cost is None or (isinstance(daily_cost, float) and math.isnan(daily_cost)):
        return None, "Cost data unavailable — budget fit cannot be assessed"
    multiplier = TRAVEL_STYLE_MULTIPLIER.get(style, 1.0)
    effective_cost = daily_cost * multiplier
    ratio = effective_cost / max(budget, 1)
    # score = 1 when ratio = 0, 0.5 at ratio = 1, 0 at ratio ≥ 2
    score = max(0.0, 1.0 - 0.5 * ratio)
    pct_of_budget = round(ratio * 100, 1)
    return score, f"Estimated daily cost is {pct_of_budget}% of your budget (style: {style})"


def _interest_match(user_interests: list[str],
                    dest_row: pd.Series) -> tuple[Optional[float], str, dict[str, float]]:
    """Cosine similarity between user interest vector and destination interest profile."""
    dest_vec = np.array([
        float(dest_row.get(col, 0) or 0) for col in INTEREST_COLUMNS
    ])
    # Build user vector: 1 for each interest the user selected (equal weight)
    user_vec = np.zeros(len(INTEREST_KEYS))
    matched = []
    for i, key in enumerate(INTEREST_KEYS):
        if key in user_interests:
            user_vec[i] = 1.0
            matched.append(key)

    if not matched or dest_vec.max() == 0:
        return None, "Interest match could not be computed (no interest data)", {}

    sim = _cosine_similarity(user_vec, dest_vec)
    interest_dict = {k: float(dest_row.get(f"{k}_score", 0) or 0) for k in INTEREST_KEYS}
    explanation = (
        f"Matched interests: {', '.join(matched) if matched else 'none'}; "
        f"similarity score {sim:.2f}"
    )
    return sim, explanation, interest_dict


def _seasonal_fit(best_months_raw: str, travel_months: list[int]) -> tuple[Optional[float], str]:
    """Fraction of user's travel months that overlap with destination's best months."""
    if not best_months_raw or (isinstance(best_months_raw, float) and math.isnan(best_months_raw)):
        return None, "Seasonal data unavailable"
    if not travel_months:
        return None, "No travel months specified"
    best = _parse_best_months(best_months_raw)
    if not best:
        return None, "Could not parse best_months data"
    overlap = len(set(travel_months) & best)
    total   = len(set(travel_months))
    score   = overlap / total
    return score, f"{overlap}/{total} of your travel months are in the best season"


def _duration_fit(stay_days: Optional[float], trip_days: int) -> tuple[float, str]:
    """How well the trip length matches the recommended stay."""
    if stay_days is None or (isinstance(stay_days, float) and math.isnan(stay_days)):
        return 0.5, "Recommended stay data unavailable — neutral score applied"
    ratio = trip_days / max(stay_days, 1)
    # Peaked at ratio = 1, decays on either side
    score = max(0.0, 1.0 - abs(ratio - 1.0) * 0.5)
    direction = "short" if trip_days < stay_days else "long" if trip_days > stay_days else "ideal"
    return score, f"Your {trip_days}-day trip vs recommended {int(stay_days)} days ({direction})"


def _traveler_fit(traveler_type: str, dest_type: str) -> tuple[float, str]:
    """Keyword affinity between traveler type and destination type string."""
    if not dest_type:
        return 0.5, "Destination type unavailable"
    affinity_words = TRAVELER_AFFINITY.get(traveler_type.lower(), [])
    dest_lower = dest_type.lower()
    hits = sum(1 for w in affinity_words if w in dest_lower)
    score = min(1.0, hits / max(len(affinity_words), 1))
    if hits > 0:
        msg = f"{traveler_type.title()} traveller affinity with {dest_type}"
    else:
        msg = f"Limited {traveler_type.title()} affinity with {dest_type}"
    return score, msg

# ---------------------------------------------------------------------------
# MAIN ENGINE
# ---------------------------------------------------------------------------

class RecommendationEngine:
    """
    Loads destination data and scores destinations against user preferences.
    This is a content-based recommendation system using weighted scoring.
    It is explainable and auditable, not a trained predictive model.
    """

    def __init__(self, data_path: Optional[Path] = None):
        if data_path is None:
            data_path = (
                Path(__file__).resolve().parents[2]
                / "data" / "processed" / "destinations_enriched.csv"
            )
        self.df = pd.read_csv(data_path)
        print(f"[RecommendationEngine] Loaded {len(self.df)} destinations")

    def recommend(
        self,
        prefs: UserPreferences,
        top_n: int = 20,
    ) -> list[RecommendationResult]:
        results: list[RecommendationResult] = []

        for _, row in self.df.iterrows():
            result = self._score_destination(row, prefs)
            if result is not None:
                results.append(result)

        # Sort: destinations with a score first (descending), then unscored ones
        scored   = sorted([r for r in results if r.overall_score is not None],
                          key=lambda r: r.overall_score, reverse=True)
        unscored = [r for r in results if r.overall_score is None]

        return (scored + unscored)[:top_n]

    def _score_destination(
        self, row: pd.Series, prefs: UserPreferences
    ) -> Optional[RecommendationResult]:
        dest = row["destination_name"]
        warnings: list[str] = []
        explanations: list[str] = []

        # ── Budget fit ─────────────────────────────────────────────────────
        daily_cost = row.get("avg_daily_cost")
        if isinstance(daily_cost, float) and math.isnan(daily_cost):
            daily_cost = None
        bf_val, bf_exp = _budget_fit(daily_cost, prefs.daily_budget_inr, prefs.travel_style)
        if bf_val is None:
            warnings.append(f"{dest}: Cost data missing — budget fit not assessed")
        budget_comp = ComponentScore(bf_val, bf_exp, WEIGHTS["budget_fit"])

        # ── Interest match ─────────────────────────────────────────────────
        im_val, im_exp, interest_dict = _interest_match(prefs.interests, row)
        if im_val is None:
            warnings.append(f"{dest}: Interest data missing")
        interest_comp = ComponentScore(im_val, im_exp, WEIGHTS["interest_match"])

        # ── Seasonal fit ───────────────────────────────────────────────────
        sf_val, sf_exp = _seasonal_fit(
            row.get("best_months", ""), prefs.travel_months
        )
        if sf_val is None:
            warnings.append(f"{dest}: Seasonal data missing or unspecified")
        seasonal_comp = ComponentScore(sf_val, sf_exp, WEIGHTS["seasonal_fit"])

        # ── Duration fit ───────────────────────────────────────────────────
        stay = row.get("recommended_stay_days")
        if isinstance(stay, float) and math.isnan(stay):
            stay = None
        df_val, df_exp = _duration_fit(stay, prefs.trip_duration_days)
        duration_comp = ComponentScore(df_val, df_exp, WEIGHTS["duration_fit"])

        # ── Traveler fit ───────────────────────────────────────────────────
        tf_val, tf_exp = _traveler_fit(
            prefs.traveler_type, str(row.get("destination_type", ""))
        )
        traveler_comp = ComponentScore(tf_val, tf_exp, WEIGHTS["traveler_fit"])

        # ── Weighted overall score ─────────────────────────────────────────
        components = {
            "budget_fit":     budget_comp,
            "interest_match": interest_comp,
            "seasonal_fit":   seasonal_comp,
            "duration_fit":   duration_comp,
            "traveler_fit":   traveler_comp,
        }
        available = [(c, WEIGHTS[k]) for k, c in components.items() if c.value is not None]
        if len(available) >= 2:  # need at least 2 components for a meaningful score
            total_weight = sum(w for _, w in available)
            overall_raw  = sum(c.value * w for c, w in available) / total_weight
            overall_score = round(overall_raw * 100, 1)
        else:
            overall_score = None
            warnings.append(f"{dest}: Too few data components — overall score not computed")

        # ── Explanations ───────────────────────────────────────────────────
        if bf_val is not None:
            explanations.append(bf_exp)
        if im_val is not None:
            explanations.append(im_exp)
        if sf_val is not None:
            explanations.append(sf_exp)
        explanations.append(df_exp)
        explanations.append(tf_exp)

        # ── Hard budget ceiling (optional) ────────────────────────────────
        if prefs.max_total_budget_inr and daily_cost:
            multiplier = TRAVEL_STYLE_MULTIPLIER.get(prefs.travel_style, 1.0)
            total_est  = daily_cost * multiplier * prefs.trip_duration_days
            if total_est > prefs.max_total_budget_inr * 1.1:  # 10% tolerance
                return None  # Hard filter out

        # ── Cost estimate ─────────────────────────────────────────────────
        if daily_cost:
            mult = TRAVEL_STYLE_MULTIPLIER.get(prefs.travel_style, 1.0)
            total_cost = daily_cost * mult * prefs.trip_duration_days
        else:
            total_cost = None

        return RecommendationResult(
            destination_name=dest,
            country=str(row.get("country", "")),
            state_region=str(row.get("state_region", "")),
            destination_type=str(row.get("destination_type", "")),
            latitude=float(row.get("latitude", 0)),
            longitude=float(row.get("longitude", 0)),
            best_months=str(row.get("best_months", "")),
            recommended_stay_days=stay,
            avg_daily_cost_inr=daily_cost,
            estimated_total_cost_inr=total_cost,
            currency=str(row.get("currency", "INR")),
            overall_score=overall_score,
            components=components,
            explanations=explanations,
            data_warnings=warnings,
            interest_scores=interest_dict,
        )


# ---------------------------------------------------------------------------
# QUICK SMOKE-TEST
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    engine = RecommendationEngine()

    prefs = UserPreferences(
        daily_budget_inr=2500,
        travel_months=[11, 12, 1],
        trip_duration_days=5,
        interests=["heritage", "culture", "food"],
        traveler_type="couple",
        travel_style="standard",
    )

    results = engine.recommend(prefs, top_n=5)
    print(f"\nTop {len(results)} recommendations:")
    for i, r in enumerate(results, 1):
        score_str = f"{r.overall_score:.1f}" if r.overall_score else "N/A"
        cost_str  = f"₹{r.avg_daily_cost_inr:,.0f}/day" if r.avg_daily_cost_inr else "No cost data"
        print(f"  {i}. {r.destination_name} ({r.state_region}) — score: {score_str} — {cost_str}")
        for exp in r.explanations[:2]:
            print(f"       → {exp}")
        if r.data_warnings:
            for w in r.data_warnings:
                print(f"       ⚠ {w}")
