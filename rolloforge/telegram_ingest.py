from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Optional

from config.settings import Settings
from rolloforge.analysis import analyze_bookmark, fallback_analysis
from rolloforge.models import AnalysisResult, Bookmark, ScoringInputs
from rolloforge.storage import (
    load_analysis_results,
    load_bookmarks,
    load_known_bookmark_ids,
    load_seen_bookmark_ids,
    merge_bookmarks,
    save_bookmarks,
    save_known_bookmark_ids,
    save_seen_bookmark_ids,
    upsert_analysis_results,
)
from rolloforge.utils import compact_text, stable_bookmark_id, utc_now_iso


# URL detection patterns
URL_PATTERN = re.compile(r"https?://[^\s<>\[\]]+", re.IGNORECASE)
FIELD_PATTERN = re.compile(r"^(url|text|note|tag|source)\s*:\s*(.*)$", re.IGNORECASE)
VALID_SOURCES = {"x", "article", "github", "manual"}
LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class ParsedTelegramBookmark:
    url: str
    text: str
    note: Optional[str]
    tag: str
    source: str
    raw_message: str
    capture_mode: str  # "manual", "url_only", "url_plus_note"


def detect_url(message: str) -> Optional[str]:
    """Extract first URL from message."""
    match = URL_PATTERN.search(message.strip())
    return match.group(0) if match else None


def infer_source_from_url(url: str) -> str:
    lowered = url.lower()
    if "x.com/" in lowered or "twitter.com/" in lowered:
        return "x"
    if "github.com/" in lowered:
        return "github"
    if lowered.startswith("http://") or lowered.startswith("https://"):
        return "article"
    return "manual"


def normalize_tag(tag: str | None) -> str:
    value = (tag or "").strip().lower()
    if not value:
        return "general"
    value = re.sub(r"\s+", "_", value)
    value = re.sub(r"[^a-z0-9_-]", "", value)
    return value or "general"


def normalize_source(source: str | None, url: str) -> str:
    value = (source or "").strip().lower()
    if value in VALID_SOURCES:
        return value
    return infer_source_from_url(url)


def parse_frictionless_url(message: str) -> ParsedTelegramBookmark:
    """Parse a frictionless URL message (plain URL with optional note)."""
    url = detect_url(message)
    if not url:
        raise ValueError("No URL found in message.")

    # Remove the URL from the message to get any additional text
    remaining = message.replace(url, "").strip()
    
    # Check if there's additional text (note)
    text_content = remaining.strip() if remaining.strip() else ""
    
    # Determine capture mode based on whether there's extra content
    if text_content:
        capture_mode = "url_plus_note"
        # Use the additional text as both text and note
        text = text_content
        note = text_content
    else:
        capture_mode = "url_only"
        # For URL-only, use URL as text placeholder
        text = f"[URL content not available] {url}"
        note = "Auto-captured from URL-only message"

    return ParsedTelegramBookmark(
        url=url,
        text=text,
        note=note,
        tag="general",
        source=infer_source_from_url(url),
        raw_message=message.strip(),
        capture_mode=capture_mode,
    )


def parse_telegram_bookmark_message(message: str) -> ParsedTelegramBookmark:
    lines = [line.rstrip() for line in message.strip().splitlines()]
    if not lines:
        raise ValueError("Message is empty.")
    if lines[0].strip().lower() != "/bookmark":
        raise ValueError("Message must start with /bookmark.")

    collected: dict[str, list[str]] = {}
    current_field: str | None = None

    for raw_line in lines[1:]:
        line = raw_line.strip()
        if not line:
            continue
        match = FIELD_PATTERN.match(line)
        if match:
            current_field = match.group(1).lower()
            collected.setdefault(current_field, []).append(match.group(2).strip())
            continue
        if current_field is None:
            raise ValueError(f"Unexpected content before any field: {raw_line}")
        collected.setdefault(current_field, []).append(line)

    url = " ".join(collected.get("url", [])).strip()
    text = "\n".join(collected.get("text", [])).strip()
    note = "\n".join(collected.get("note", [])).strip() or None
    tag = normalize_tag(" ".join(collected.get("tag", [])).strip())
    source = normalize_source(" ".join(collected.get("source", [])).strip() or None, url)

    if not url:
        raise ValueError("URL is required.")
    if not text:
        raise ValueError("Text is required.")

    return ParsedTelegramBookmark(
        url=url,
        text=text,
        note=note,
        tag=tag,
        source=source,
        raw_message=message.strip(),
        capture_mode="manual",
    )


def bookmark_from_parsed_message(parsed: ParsedTelegramBookmark) -> Bookmark:
    bookmark_id = stable_bookmark_id(parsed.url, parsed.text)
    timestamp = utc_now_iso()
    return Bookmark(
        id=bookmark_id,
        source=parsed.source,
        url=parsed.url,
        text=parsed.text,
        note=parsed.note,
        created_at=timestamp,
        bookmarked_at=timestamp,
        tags=[parsed.tag],
        raw_payload={
            "ingestion_channel": "telegram",
            "telegram_message": parsed.raw_message,
            "note": parsed.note,
            "capture_mode": parsed.capture_mode,
        },
    )


def next_action_for_bucket(bucket: str) -> str:
    mapping = {
        "test_this_week": "Run a concrete experiment this week.",
        "build_later": "Keep it in the backlog and revisit after current priorities.",
        "archive": "Store it for reference without active follow-up.",
        "ignore": "Drop it and move on.",
    }
    return mapping.get(bucket, "Review manually.")


def build_failed_analysis_result(bookmark: Bookmark) -> AnalysisResult:
    return AnalysisResult(
        bookmark_id=bookmark.id,
        summary=compact_text(bookmark.text, limit=220),
        recommendation_reason="Analysis failed; bookmark was still saved for later review.",
        key_insights=[
            "Bookmark persisted successfully.",
            "Analysis failed during ingest.",
            "Retry analysis later.",
        ],
        scoring_inputs=ScoringInputs(
            relevance=0,
            practical_value=0,
            actionability=0,
            stage_fit=0,
            novelty=0,
            excitement=0,
            difficulty=0,
            time_cost=0,
        ),
        worth_score=0,
        effort_score=0,
        priority_score=0,
        recommendation_bucket="archive",
        analysis_source="failed",
        confidence="low",
        difficulty_reason="analysis failed",
        next_action="retry analysis later",
        analyzed_at=utc_now_iso(),
    )


def build_low_confidence_analysis_result(bookmark: Bookmark, settings: Settings) -> AnalysisResult:
    """Build analysis result for URL-only bookmarks with low confidence."""
    # Use fallback analysis but mark as low confidence
    payload = fallback_analysis(bookmark, settings.pipeline_stage)
    inputs = ScoringInputs.from_dict(payload.get("scoring_inputs", {}))
    
    # Adjust scores down slightly for low-confidence items
    from rolloforge.scoring import score_analysis
    worth_score, effort_score, priority_score, bucket = score_analysis(inputs)
    priority_score = max(0, priority_score * 0.7)  # Reduce priority for low-confidence
    
    return AnalysisResult(
        bookmark_id=bookmark.id,
        summary=compact_text(str(payload.get("summary", bookmark.text)), limit=220),
        recommendation_reason=compact_text(
            str(payload.get("recommendation_reason", "Low-confidence analysis due to incomplete input.")),
            limit=260,
        ),
        key_insights=payload.get("key_insights", []) + ["Low-confidence: captured from URL only, limited context available."],
        scoring_inputs=inputs,
        worth_score=worth_score,
        effort_score=effort_score,
        priority_score=priority_score,
        recommendation_bucket=bucket,
        analysis_source="fallback_low_confidence",
        confidence="low",
        difficulty_reason="incomplete input",
        next_action="Add more context or re-save with /bookmark for better analysis",
        analyzed_at=utc_now_iso(),
    )


def ingest_telegram_bookmark_message(message: str, settings: Settings) -> tuple[Bookmark, AnalysisResult, dict[str, str | float]]:
    # Try to detect if it's a /bookmark command first
    lines = [line.strip() for line in message.strip().splitlines()]
    is_manual = lines and lines[0].strip().lower() == "/bookmark"
    
    # Try to find a URL in the message
    url = detect_url(message)
    
    if not url:
        raise ValueError("No URL found in message.")
    
    # Parse based on mode
    if is_manual:
        # Full /bookmark format
        parsed = parse_telegram_bookmark_message(message)
    else:
        # Frictionless mode - plain URL with optional note
        parsed = parse_frictionless_url(message)
    
    bookmark = bookmark_from_parsed_message(parsed)

    existing_bookmarks = load_bookmarks()
    merged_bookmarks = merge_bookmarks(existing_bookmarks, [bookmark])
    save_bookmarks(merged_bookmarks)
    save_known_bookmark_ids(load_known_bookmark_ids() | {bookmark.id})

    # Analyze bookmark (DeepSeek removed, uses fallback/LLM)
    try:
        result = analyze_bookmark(bookmark, settings)
        # For url_only mode, mark as low confidence
        if parsed.capture_mode == "url_only":
            result = build_low_confidence_analysis_result(bookmark, settings)
    except Exception:
        LOGGER.exception("Bookmark analysis failed for %s. Saving failed analysis record.", bookmark.id)
        result = build_failed_analysis_result(bookmark)
    
    existing_results = load_analysis_results()
    upsert_analysis_results(existing_results, [result])
    save_seen_bookmark_ids(load_seen_bookmark_ids() | {bookmark.id})

    confirmation = {
        "status": result.analysis_source,
        "source": bookmark.source,
        "capture_mode": parsed.capture_mode,
        "tag": bookmark.tags[0] if bookmark.tags else "general",
        "recommendation": result.recommendation_bucket,
        "priority": result.priority_score,
        "next_action": result.next_action or next_action_for_bucket(result.recommendation_bucket),
    }
    return bookmark, result, confirmation