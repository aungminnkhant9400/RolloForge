from __future__ import annotations

import logging
from typing import Any

from config.settings import Settings
from rolloforge.deepseek_client import DeepSeekClient
from rolloforge.models import AnalysisResult, Bookmark, ScoringInputs
from rolloforge.scoring import score_analysis
from rolloforge.utils import compact_text, safe_list, utc_now_iso


LOGGER = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a bookmark intelligence analyst. "
    "Return only valid JSON with grounded assessments and numeric scores from 0 to 10."
)


def build_user_prompt(bookmark: Bookmark, stage: str) -> str:
    note = bookmark.note or str(bookmark.raw_payload.get("note", "")).strip() or "none"
    return f"""
Analyze this saved bookmark for a solo builder pipeline.

Current stage: {stage}

Bookmark:
- ID: {bookmark.id}
- Source: {bookmark.source}
- URL: {bookmark.url}
- Author: {bookmark.author or "unknown"}
- Text: {bookmark.text}
- Note: {note}
- Tags: {", ".join(bookmark.tags) if bookmark.tags else "none"}

Return JSON with this shape:
{{
  "summary": "short summary",
  "recommendation_reason": "why this matters now",
  "key_insights": ["insight 1", "insight 2", "insight 3"],
  "scoring_inputs": {{
    "relevance": 0-10,
    "practical_value": 0-10,
    "actionability": 0-10,
    "stage_fit": 0-10,
    "novelty": 0-10,
    "excitement": 0-10,
    "difficulty": 0-10,
    "time_cost": 0-10
  }}
}}
""".strip()


def _keyword_score(text: str, keywords: list[str], base: float = 3.5, bonus: float = 1.2) -> float:
    lowered = text.lower()
    matches = sum(1 for keyword in keywords if keyword in lowered)
    return round(min(10.0, base + matches * bonus), 2)


def fallback_scoring_inputs(bookmark: Bookmark, stage: str) -> ScoringInputs:
    note = bookmark.note or str(bookmark.raw_payload.get("note", "")).strip()
    text = f"{bookmark.text} {note} {' '.join(bookmark.tags)} {bookmark.url} {bookmark.source}".lower()
    relevance = _keyword_score(text, ["agent", "llm", "eval", "automation", "workflow", "memory", "prompt"], base=4.2)
    practical_value = _keyword_score(text, ["github", "repo", "example", "guide", "benchmark", "case study"], base=3.8)
    actionability = _keyword_score(text, ["how to", "practical", "workflow", "template", "eval", "build"], base=3.6)
    stage_fit = _keyword_score(f"{text} {stage.lower()}", [stage.lower(), "validation", "prototype", "product"], base=4.0)
    novelty = _keyword_score(text, ["new", "novel", "breakthrough", "research", "paper"], base=3.7, bonus=1.0)
    excitement = _keyword_score(text, ["strong", "promising", "interesting", "candidate", "useful"], base=3.5, bonus=0.9)
    difficulty = _keyword_score(text, ["paper", "research", "benchmark", "architecture", "multi-agent"], base=3.2, bonus=1.1)
    time_cost = _keyword_score(text, ["long", "paper", "benchmark", "framework", "orchestration"], base=3.0, bonus=1.0)
    return ScoringInputs(
        relevance=relevance,
        practical_value=practical_value,
        actionability=actionability,
        stage_fit=stage_fit,
        novelty=novelty,
        excitement=excitement,
        difficulty=difficulty,
        time_cost=time_cost,
    )


def fallback_analysis(bookmark: Bookmark, stage: str) -> dict[str, Any]:
    inputs = fallback_scoring_inputs(bookmark, stage)
    focus = "near-term experiment" if inputs.actionability >= 6 else "reference material"
    note = bookmark.note or str(bookmark.raw_payload.get("note", "")).strip()
    note_hint = f"Saved note: {compact_text(note, 70)}" if note else "No saved note provided."
    return {
        "summary": compact_text(bookmark.text, limit=120),
        "recommendation_reason": f"This looks like {focus} for the current {stage} stage.",
        "key_insights": [
            f"Author/source: {bookmark.author or 'unknown'}",
            f"Primary signal: {bookmark.tags[0] if bookmark.tags else 'general bookmark'}",
            note_hint,
            "Fallback analysis used because DeepSeek output was unavailable.",
        ],
        "scoring_inputs": inputs.to_dict(),
    }


def normalize_analysis_payload(bookmark: Bookmark, payload: dict[str, Any], analysis_source: str) -> AnalysisResult:
    inputs = ScoringInputs.from_dict(payload.get("scoring_inputs", {}))
    worth_score, effort_score, priority_score, bucket = score_analysis(inputs)
    return AnalysisResult(
        bookmark_id=bookmark.id,
        summary=compact_text(str(payload.get("summary", bookmark.text)), limit=220),
        recommendation_reason=compact_text(
            str(payload.get("recommendation_reason", "No recommendation rationale supplied.")),
            limit=260,
        ),
        key_insights=safe_list(payload.get("key_insights"))[:5],
        scoring_inputs=inputs,
        worth_score=worth_score,
        effort_score=effort_score,
        priority_score=priority_score,
        recommendation_bucket=bucket,
        analysis_source=analysis_source,
        analyzed_at=utc_now_iso(),
    )


def analyze_bookmark(bookmark: Bookmark, client: DeepSeekClient, settings: Settings) -> AnalysisResult:
    payload = client.request_json(SYSTEM_PROMPT, build_user_prompt(bookmark, settings.pipeline_stage))
    if payload is None:
        payload = fallback_analysis(bookmark, settings.pipeline_stage)
        source = "fallback"
    else:
        source = "deepseek"
    return normalize_analysis_payload(bookmark, payload, analysis_source=source)


def analyze_pending_bookmarks(
    bookmarks: list[Bookmark],
    existing_ids: set[str],
    client: DeepSeekClient,
    settings: Settings,
    limit: int | None = None,
    force_all: bool = False,
) -> list[AnalysisResult]:
    pending = bookmarks if force_all else [bookmark for bookmark in bookmarks if bookmark.id not in existing_ids]
    if limit is not None:
        pending = pending[:limit]
    LOGGER.info("Preparing analysis for %s bookmark(s).", len(pending))
    return [analyze_bookmark(bookmark, client, settings) for bookmark in pending]
