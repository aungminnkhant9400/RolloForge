from __future__ import annotations

from rolloforge.models import ScoringInputs
from rolloforge.utils import clamp_score


def compute_worth_score(inputs: ScoringInputs) -> float:
    score = (
        0.25 * inputs.relevance
        + 0.20 * inputs.practical_value
        + 0.15 * inputs.actionability
        + 0.15 * inputs.stage_fit
        + 0.15 * inputs.novelty
        + 0.10 * inputs.excitement
    )
    return clamp_score(score)


def compute_effort_score(inputs: ScoringInputs) -> float:
    score = 0.55 * inputs.difficulty + 0.45 * inputs.time_cost
    return clamp_score(score)


def compute_priority_score(worth_score: float, effort_score: float) -> float:
    return round(worth_score - 0.6 * effort_score, 2)


def recommendation_bucket(inputs: ScoringInputs, worth_score: float, priority_score: float) -> str:
    if priority_score >= 4.0 and inputs.actionability >= 6 and worth_score >= 6:
        return "test_this_week"
    if priority_score >= 2.5 and worth_score >= 5:
        return "build_later"
    if worth_score >= 3 or priority_score >= 0:
        return "archive"
    return "ignore"


def score_analysis(inputs: ScoringInputs) -> tuple[float, float, float, str]:
    worth_score = compute_worth_score(inputs)
    effort_score = compute_effort_score(inputs)
    priority_score = compute_priority_score(worth_score, effort_score)
    bucket = recommendation_bucket(inputs, worth_score, priority_score)
    return worth_score, effort_score, priority_score, bucket
