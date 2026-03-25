"""Complete bookmark workflow with auto-push.

This module combines scraping, analysis, saving, and git push into one workflow.
"""
import logging
from datetime import datetime, timezone
from typing import Optional, Tuple

from rolloforge.deepseek_analysis import deepseek_analyze_bookmark
from rolloforge.git_auto import git_auto_push
from rolloforge.models import Bookmark, AnalysisResult
from rolloforge.scrapers import fetch_x_content_sync
from rolloforge.storage import (
    load_bookmarks,
    load_analysis_results,
    save_bookmarks,
    upsert_analysis_results,
)
from rolloforge.utils import stable_bookmark_id

LOGGER = logging.getLogger(__name__)


def check_duplicate(url: str) -> Optional[Bookmark]:
    """Check if URL already exists in bookmarks."""
    bookmarks = load_bookmarks()
    for b in bookmarks:
        if b.url == url:
            return b
    return None


def scrape_and_create_bookmark(url: str) -> Optional[Bookmark]:
    """Scrape URL and create bookmark."""
    # Determine source
    url_lower = url.lower()
    if "x.com/" in url_lower or "twitter.com/" in url_lower:
        source = "x"
        # Try to scrape X
        try:
            scraped = fetch_x_content_sync(url)
            if scraped and scraped.get("success"):
                text = scraped["text"]
                author = scraped.get("author", "unknown")
                title = scraped.get("title", text[:80] + "..." if len(text) > 80 else text)
                note = f"Auto-captured from X. Author: @{author}"
                scraped_via = "playwright"
            else:
                # Fallback
                handle = _extract_x_handle(url)
                text = f"Twitter/X post from @{handle}. View on X for full content."
                title = f"Twitter/X post from @{handle}"
                note = "Auto-captured from URL-only message (scraping failed)"
                scraped_via = None
        except Exception as e:
            LOGGER.warning(f"X scraping failed: {e}")
            handle = _extract_x_handle(url)
            text = f"Twitter/X post from @{handle}. View on X for full content."
            title = f"Twitter/X post from @{handle}"
            note = "Auto-captured from URL-only message"
            scraped_via = None
    else:
        source = "article"
        text = f"[URL content not available] {url}"
        title = f"Article from {url.split('/')[2]}"
        note = "Auto-captured from URL-only message"
        scraped_via = None
    
    bookmark_id = stable_bookmark_id(url, text)
    timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    
    bookmark = Bookmark(
        id=bookmark_id,
        source=source,
        url=url,
        text=text,
        title=title,
        note=note,
        created_at=timestamp,
        bookmarked_at=timestamp,
        tags=["general"],  # Will be updated by DeepSeek
        raw_payload={
            "ingestion_channel": "telegram",
            "capture_mode": "url_only",
            "scraped_via": scraped_via,
        },
    )
    
    return bookmark


def _extract_x_handle(url: str) -> str:
    """Extract X handle from URL."""
    try:
        parts = url.split("/")
        if "x.com" in url or "twitter.com" in url:
            for i, part in enumerate(parts):
                if part in ("x.com", "twitter.com") and i + 1 < len(parts):
                    return parts[i + 1]
    except:
        pass
    return "unknown"


def process_bookmark_url(url: str) -> Tuple[bool, str, Optional[Bookmark], Optional[AnalysisResult]]:
    """
    Complete workflow: scrape, analyze, save, push.
    
    Returns:
        (success, message, bookmark, analysis)
    """
    # Check for duplicate
    existing = check_duplicate(url)
    if existing:
        return False, f"DUPLICATE: Already saved - {existing.title[:50]}...", existing, None
    
    # Scrape and create bookmark
    bookmark = scrape_and_create_bookmark(url)
    if not bookmark:
        return False, "Failed to scrape URL", None, None
    
    # Run DeepSeek analysis
    LOGGER.info(f"Running DeepSeek analysis for: {bookmark.title[:50]}...")
    analysis_dict = deepseek_analyze_bookmark(
        text=bookmark.text,
        title=bookmark.title,
        url=bookmark.url
    )
    
    # Update bookmark tags from DeepSeek analysis
    if "tags" in analysis_dict and analysis_dict["tags"]:
        bookmark.tags = analysis_dict["tags"]
        LOGGER.info(f"Tags from DeepSeek: {bookmark.tags}")
    
    # Create AnalysisResult
    from rolloforge.models import ScoringInputs
    
    analysis = AnalysisResult(
        bookmark_id=bookmark.id,
        title=analysis_dict.get("title", bookmark.title),
        summary=analysis_dict.get("summary", ""),
        recommendation_reason=analysis_dict.get("recommendation_reason", ""),
        key_insights=analysis_dict.get("key_insights", []),
        scoring_inputs=ScoringInputs.from_dict(analysis_dict.get("scoring_inputs", {})),
        worth_score=analysis_dict.get("worth_score", 0),
        effort_score=analysis_dict.get("effort_score", 0),
        priority_score=analysis_dict.get("priority_score", 0),
        recommendation_bucket=analysis_dict.get("recommendation_bucket", "archive"),
        analysis_source=analysis_dict.get("analysis_source", "deepseek"),
        analyzed_at=bookmark.bookmarked_at,
    )
    
    # Save bookmark
    bookmarks = load_bookmarks()
    bookmarks.append(bookmark)
    save_bookmarks(bookmarks)
    LOGGER.info(f"Saved bookmark: {bookmark.id}")
    
    # Save analysis
    analyses = load_analysis_results()
    analyses.append(analysis)
    upsert_analysis_results(load_analysis_results(), [analysis])
    LOGGER.info(f"Saved analysis: {analysis.bookmark_id}")
    
    # Sync to web/lib
    try:
        from web.lib.copy_data import main as copy_data
        copy_data()
        LOGGER.info("Synced data to web/lib")
    except Exception as e:
        LOGGER.warning(f"Failed to sync web/lib: {e}")
    
    # Git auto-push
    push_success = git_auto_push(analysis.title or bookmark.title)
    if push_success:
        message = f"✓ Saved: {analysis.title or bookmark.title}\n✓ Bucket: {analysis.recommendation_bucket}\n✓ Priority: {analysis.priority_score}\n✓ Pushed to GitHub"
    else:
        message = f"✓ Saved: {analysis.title or bookmark.title}\n✓ Bucket: {analysis.recommendation_bucket}\n✓ Priority: {analysis.priority_score}\n⚠ Git push failed - manual push needed"
    
    return True, message, bookmark, analysis
