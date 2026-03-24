import json
from datetime import datetime, timezone

# Load existing analysis
with open('data/analysis_results.json', 'r') as f:
    results = json.load(f)

# Find and update the CodexBar bookmark
for r in results:
    if r['bookmark_id'] == 'bookmark_dfb2d77d033e':
        r['summary'] = "CodexBar 0.19.0 - macOS menu bar app for monitoring Claude Code/Codex API usage. Tracks token resets, subscription history, and provides usage alerts to avoid hitting limits."
        r['recommendation_reason'] = "Quality-of-life utility if you frequently hit Claude Code token limits. Menu bar convenience with usage charts and reset time tracking. Not critical but prevents workflow interruptions."
        r['key_insights'] = [
            "Alibaba Coding Plan support added",
            "Subscription history charts for usage patterns",
            "Cursor IDE dashboard integration",
            "Codex code-review reset time tracking",
            "Prevents token limit surprises during work"
        ]
        r['scoring_inputs'] = {
            'relevance': 7.0,
            'practical_value': 8.0,
            'actionability': 9.0,
            'stage_fit': 8.0,
            'novelty': 6.0,
            'excitement': 6.0,
            'difficulty': 2.0,
            'time_cost': 1.0
        }
        r['worth_score'] = 7.5
        r['effort_score'] = 1.5
        r['priority_score'] = 7.5
        r['recommendation_bucket'] = 'build_later'
        r['analysis_source'] = 'garfis_manual'
        r['analyzed_at'] = datetime.now(timezone.utc).isoformat()
        print(f"Updated: {r['bookmark_id']}")
        break

# Save back
with open('data/analysis_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print("Analysis updated!")
