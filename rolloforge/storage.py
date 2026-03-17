from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from config.settings import ANALYSIS_RESULTS_PATH, BOOKMARKS_RAW_PATH, SEEN_BOOKMARKS_PATH
from rolloforge.models import AnalysisResult, Bookmark
from rolloforge.utils import ensure_parent, utc_now_iso


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as handle:
        try:
            return json.load(handle)
        except json.JSONDecodeError:
            return default


def write_json(path: Path, payload: Any) -> None:
    ensure_parent(path)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def load_bookmarks(path: Path = BOOKMARKS_RAW_PATH) -> list[Bookmark]:
    raw_items = load_json(path, default=[])
    bookmarks = [Bookmark.from_dict(item) for item in raw_items if isinstance(item, dict)]
    return [bookmark for bookmark in bookmarks if bookmark.id and bookmark.url]


def save_bookmarks(bookmarks: Iterable[Bookmark], path: Path = BOOKMARKS_RAW_PATH) -> None:
    write_json(path, [bookmark.to_dict() for bookmark in bookmarks])


def merge_bookmarks(existing: Iterable[Bookmark], incoming: Iterable[Bookmark]) -> list[Bookmark]:
    merged: dict[str, Bookmark] = {bookmark.id: bookmark for bookmark in existing}
    for bookmark in incoming:
        merged[bookmark.id] = bookmark
    return sorted(
        merged.values(),
        key=lambda item: item.bookmarked_at or item.created_at or "",
        reverse=True,
    )


def load_analysis_results(path: Path = ANALYSIS_RESULTS_PATH) -> list[AnalysisResult]:
    raw_items = load_json(path, default=[])
    return [AnalysisResult.from_dict(item) for item in raw_items if isinstance(item, dict) and item.get("bookmark_id")]


def save_analysis_results(results: Iterable[AnalysisResult], path: Path = ANALYSIS_RESULTS_PATH) -> None:
    write_json(path, [result.to_dict() for result in results])


def upsert_analysis_results(
    existing: Iterable[AnalysisResult],
    new_results: Iterable[AnalysisResult],
    path: Path = ANALYSIS_RESULTS_PATH,
) -> list[AnalysisResult]:
    merged: dict[str, AnalysisResult] = {result.bookmark_id: result for result in existing}
    for result in new_results:
        merged[result.bookmark_id] = result
    ordered = sorted(merged.values(), key=lambda item: item.priority_score, reverse=True)
    save_analysis_results(ordered, path=path)
    return ordered


def _load_seen_payload(path: Path = SEEN_BOOKMARKS_PATH) -> dict[str, Any]:
    payload = load_json(path, default={"bookmark_ids": [], "analyzed_bookmark_ids": []})
    if not isinstance(payload, dict):
        return {"bookmark_ids": [], "analyzed_bookmark_ids": []}
    payload.setdefault("bookmark_ids", [])
    payload.setdefault("analyzed_bookmark_ids", [])
    return payload


def load_known_bookmark_ids(path: Path = SEEN_BOOKMARKS_PATH) -> set[str]:
    payload = _load_seen_payload(path)
    bookmark_ids = payload.get("bookmark_ids", []) if isinstance(payload, dict) else []
    return {str(item).strip() for item in bookmark_ids if str(item).strip()}


def save_known_bookmark_ids(bookmark_ids: Iterable[str], path: Path = SEEN_BOOKMARKS_PATH) -> None:
    payload = _load_seen_payload(path)
    payload["bookmark_ids"] = sorted({str(item).strip() for item in bookmark_ids if str(item).strip()})
    payload["updated_at"] = utc_now_iso()
    write_json(path, payload)


def load_seen_bookmark_ids(path: Path = SEEN_BOOKMARKS_PATH) -> set[str]:
    payload = _load_seen_payload(path)
    bookmark_ids = payload.get("analyzed_bookmark_ids", []) if isinstance(payload, dict) else []
    return {str(item).strip() for item in bookmark_ids if str(item).strip()}


def save_seen_bookmark_ids(bookmark_ids: Iterable[str], path: Path = SEEN_BOOKMARKS_PATH) -> None:
    payload = _load_seen_payload(path)
    payload["analyzed_bookmark_ids"] = sorted({str(item).strip() for item in bookmark_ids if str(item).strip()})
    payload["updated_at"] = utc_now_iso()
    write_json(
        path,
        payload,
    )
