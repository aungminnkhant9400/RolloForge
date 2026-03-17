from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import get_settings
from rolloforge.analysis import analyze_pending_bookmarks
from rolloforge.deepseek_client import DeepSeekClient
from rolloforge.reporting import generate_report
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
from rolloforge.x_client import XBookmarkClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the full RolloForge pipeline.")
    parser.add_argument("--skip-sync", action="store_true", help="Skip bookmark sync and analyze existing local JSON only.")
    parser.add_argument("--source-file", help="Optional local JSON file to import for the sync step.")
    parser.add_argument("--limit", type=int, help="Optional max number of bookmarks to analyze in this run.")
    parser.add_argument("--force-all", action="store_true", help="Re-analyze all bookmarks instead of only unseen ones.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    settings = get_settings()

    bookmarks = load_bookmarks()
    if not args.skip_sync:
        x_client = XBookmarkClient(settings)
        logging.info("X auth config present: %s", x_client.auth_summary())
        known_before = load_known_bookmark_ids()
        synced, mode = x_client.fetch_bookmarks(source_file=args.source_file)
        new_ids = {bookmark.id for bookmark in synced} - {bookmark.id for bookmark in bookmarks}
        bookmarks = merge_bookmarks(bookmarks, synced)
        save_bookmarks(bookmarks)
        save_known_bookmark_ids(known_before | {bookmark.id for bookmark in bookmarks})
        logging.info("Sync mode resolved to: %s", mode)
        logging.info("Fetched %s bookmark(s).", len(synced))
        logging.info("New bookmarks stored: %s", len(new_ids))
        logging.info("Sync step complete with %s stored bookmark(s).", len(bookmarks))

    deepseek_client = DeepSeekClient(settings)
    seen_ids = set() if args.force_all else load_seen_bookmark_ids()
    existing_results = load_analysis_results()
    new_results = analyze_pending_bookmarks(
        bookmarks=bookmarks,
        existing_ids=seen_ids,
        client=deepseek_client,
        settings=settings,
        limit=args.limit,
        force_all=args.force_all,
    )
    all_results = upsert_analysis_results(existing_results, new_results)
    save_seen_bookmark_ids({result.bookmark_id for result in all_results})

    report_path = generate_report(bookmarks, all_results)
    logging.info("Pipeline complete. Report written to %s", report_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
