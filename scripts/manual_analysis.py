"""Manual analysis workflow - AI reads and analyzes bookmarks directly.

This replaces the auto-scoring with real LLM analysis by Garfis.
"""
import json
from datetime import datetime, timezone
from rolloforge.scrapers import fetch_x_content_sync
from rolloforge.telegram_ingest import parse_frictionless_url, bookmark_from_parsed_message, _generate_title
from rolloforge.storage import load_bookmarks, save_bookmarks, load_analysis_results, upsert_analysis_results


def save_and_analyze_bookmark(url: str, manual_analysis: dict = None) -> dict:
    """
    Save bookmark with manual AI analysis from Garfis.
    
    Args:
        url: The URL to bookmark
        manual_analysis: Dict with keys: summary, priority_score, bucket, key_insights, recommendation_reason
    
    Returns:
        dict with bookmark and analysis info
    """
    # Scrape content
    scraped = fetch_x_content_sync(url)
    
    # Create message for parsing
    message = url
    if scraped['success'] and scraped['text']:
        message = f"{url}\n\n{scraped['text'][:500]}"
    
    # Parse and create bookmark
    parsed = parse_frictionless_url(message)
    bookmark = bookmark_from_parsed_message(parsed)
    
    # Override title if scraped
    if scraped['success']:
        bookmark.text = scraped['text']
        bookmark.title = scraped.get('title') or _generate_title(scraped['text'])
        bookmark.author = scraped.get('author')
    
    # Save bookmark
    bookmarks = load_bookmarks()
    bookmarks.insert(0, bookmark)
    save_bookmarks(bookmarks)
    
    # Create analysis from manual input or auto-analysis
    if manual_analysis:
        analysis = {
            "bookmark_id": bookmark.id,
            "summary": manual_analysis.get('summary', 'Pending analysis'),
            "recommendation_reason": manual_analysis.get('recommendation_reason', ''),
            "key_insights": manual_analysis.get('key_insights', []),
            "scoring_inputs": {
                "relevance": manual_analysis.get('relevance', 5.0),
                "practical_value": manual_analysis.get('practical_value', 5.0),
                "actionability": manual_analysis.get('actionability', 5.0),
                "stage_fit": manual_analysis.get('stage_fit', 5.0),
                "novelty": manual_analysis.get('novelty', 5.0),
                "excitement": manual_analysis.get('excitement', 5.0),
                "difficulty": manual_analysis.get('difficulty', 5.0),
                "time_cost": manual_analysis.get('time_cost', 5.0),
            },
            "worth_score": manual_analysis.get('worth_score', 5.0),
            "effort_score": manual_analysis.get('effort_score', 5.0),
            "priority_score": manual_analysis.get('priority_score', 5.0),
            "recommendation_bucket": manual_analysis.get('bucket', 'archive'),
            "analysis_source": "garfis_manual",
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
        }
    else:
        # Placeholder - waiting for Garfis analysis
        analysis = {
            "bookmark_id": bookmark.id,
            "summary": "[PENDING GARFIS ANALYSIS] " + bookmark.text[:100],
            "recommendation_reason": "Awaiting manual analysis by Garfis",
            "key_insights": ["Scraped successfully", f"Content: {len(bookmark.text)} chars"],
            "scoring_inputs": {"relevance": 0, "practical_value": 0, "actionability": 0, "stage_fit": 0, "novelty": 0, "excitement": 0, "difficulty": 0, "time_cost": 0},
            "worth_score": 0.0,
            "effort_score": 0.0,
            "priority_score": 0.0,
            "recommendation_bucket": "pending",
            "analysis_source": "pending_garfis",
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
        }
    
    # Save analysis
    existing = load_analysis_results()
    existing = [a for a in existing if a.bookmark_id != bookmark.id]
    
    # Convert AnalysisResult objects to dicts if needed
    existing_dicts = []
    for a in existing:
        if hasattr(a, 'to_dict'):
            existing_dicts.append(a.to_dict())
        elif isinstance(a, dict):
            existing_dicts.append(a)
        else:
            # Convert AnalysisResult object manually
            existing_dicts.append({
                'bookmark_id': a.bookmark_id,
                'summary': a.summary,
                'recommendation_reason': a.recommendation_reason,
                'key_insights': a.key_insights,
                'scoring_inputs': {
                    'relevance': a.scoring_inputs.relevance,
                    'practical_value': a.scoring_inputs.practical_value,
                    'actionability': a.scoring_inputs.actionability,
                    'stage_fit': a.scoring_inputs.stage_fit,
                    'novelty': a.scoring_inputs.novelty,
                    'excitement': a.scoring_inputs.excitement,
                    'difficulty': a.scoring_inputs.difficulty,
                    'time_cost': a.scoring_inputs.time_cost,
                },
                'worth_score': a.worth_score,
                'effort_score': a.effort_score,
                'priority_score': a.priority_score,
                'recommendation_bucket': a.recommendation_bucket,
                'analysis_source': a.analysis_source,
                'analyzed_at': a.analyzed_at,
            })
    
    existing_dicts.append(analysis)
    
    with open('data/analysis_results.json', 'w') as f:
        json.dump(existing_dicts, f, indent=2)
    
    return {
        "bookmark_id": bookmark.id,
        "title": bookmark.title,
        "text_preview": bookmark.text[:200],
        "total_bookmarks": len(bookmarks),
        "analysis": analysis
    }


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        url = sys.argv[1]
        result = save_and_analyze_bookmark(url)
        print(json.dumps(result, indent=2))
    else:
        print("Usage: python manual_analysis.py <url>")