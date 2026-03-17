from __future__ import annotations

import logging
import re
from dataclasses import dataclass

from config.settings import Settings
from rolloforge.analysis import analyze_bookmark
from rolloforge.deepseek_client import DeepSeekClient
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


FIELD_PATTERN = re.compile(r"^(url|text|note|tag|source)\s*:\s*(.*)$", re.IGNORECASE)
VALID_SOURCES = {"x", "article", "github", "manual"}
LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class ParsedTelegramBookmark:
    url: str
    text: str
    note: str | None
    tag: str
    source: str
    raw_message: str


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


def ingest_telegram_bookmark_message(message: str, settings: Settings) -> tuple[Bookmark, AnalysisResult, dict[str, str | float]]:
    parsed = parse_telegram_bookmark_message(message)
    bookmark = bookmark_from_parsed_message(parsed)

    existing_bookmarks = load_bookmarks()
    merged_bookmarks = merge_bookmarks(existing_bookmarks, [bookmark])
    save_bookmarks(merged_bookmarks)
    save_known_bookmark_ids(load_known_bookmark_ids() | {bookmark.id})

    client = DeepSeekClient(settings)
    try:
        result = analyze_bookmark(bookmark, client, settings)
    except Exception:
        LOGGER.exception("Bookmark analysis failed for %s. Saving failed analysis record.", bookmark.id)
        result = build_failed_analysis_result(bookmark)
    existing_results = load_analysis_results()
    upsert_analysis_results(existing_results, [result])
    save_seen_bookmark_ids(load_seen_bookmark_ids() | {bookmark.id})

    confirmation = {
        "status": result.analysis_source,
        "source": bookmark.source,
        "tag": bookmark.tags[0] if bookmark.tags else "general",
        "recommendation": result.recommendation_bucket,
        "priority": result.priority_score,
        "next_action": result.next_action or next_action_for_bucket(result.recommendation_bucket),
    }
    return bookmark, result, confirmation
