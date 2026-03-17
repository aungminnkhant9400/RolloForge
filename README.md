# RolloForge

RolloForge is a personal-use bookmark intelligence pipeline. It captures bookmarks from Telegram (URLs or structured messages), stores them in local JSON files, waits for LLM analysis, computes recommendation scores, and renders a standalone HTML report.

## v1 scope

- No web frontend
- No database
- JSON storage only
- LLM-powered semantic analysis (manual, via Garfis)
- Python scoring and recommendation mapping
- Standalone HTML reporting (last 10 bookmarks)
- Telegram integration via OpenClaw

## Project layout

- `config/settings.py`: environment-driven settings and project paths
- `data/bookmarks_raw.json`: normalized bookmark records
- `data/analysis_results.json`: analysis outputs and scoring results
- `data/seen_bookmarks.json`: known bookmark IDs
- `reports/latest_report.html`: latest standalone report (last 10 bookmarks)
- `reports/history/`: timestamped historical reports (last 2 kept)
- `rolloforge/`: core package modules
- `scripts/`: runnable entry points
- `templates/report.html.j2`: HTML report template

## Setup

1. Create a Python 3.11+ environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and set your pipeline stage:

```bash
PIPELINE_STAGE=idea_validation
```

## How it works

### 1. Capture (Telegram)

**Frictionless mode** (just paste URL):
```
https://x.com/user/status/123456
```

**Structured mode** (full control):
```
/bookmark
URL: https://example.com/post
Text: Article content or description
Note: Why I'm saving this
Tag: agents
Source: article
```

The system saves the bookmark with status `"pending_llm"` and waits for analysis.

### 2. Analysis (LLM - Garfis)

When you share a URL in Telegram:
1. Garfis scrapes the content using Playwright
2. Performs semantic analysis (relevance, practical value, actionability, etc.)
3. Calculates worth_score, effort_score, priority_score
4. Assigns recommendation bucket: `test_this_week`, `build_later`, `archive`, or `ignore`
5. Writes results to `data/analysis_results.json`

**No external APIs** - all analysis done by Garfis directly.

### 3. Report Generation

When you say **"bmreport"**:
1. Generates HTML report at `reports/latest_report.html`
2. Shows only **last 10 bookmarks** (most recent first)
3. Footer displays: *"Showing last 10 of X total bookmarks"*
4. Sends file via Telegram using `telegram-file-sender` skill
5. Keeps only **last 2 reports** in `reports/history/`, deletes older ones

## Commands

### Telegram Workflow

**Paste URL** (any URL in chat):
- Scraped and analyzed silently
- No response unless there's an error

**"bmreport"**:
- Generates and sends HTML report
- Shows stats and last 10 bookmarks

### Manual Scripts

Generate report:
```bash
python scripts/generate_report.py
```

Run full pipeline (if you have X API set up):
```bash
python scripts/run_pipeline.py
```

## JSON contracts

### `data/bookmarks_raw.json`

```json
[
  {
    "id": "bookmark_001",
    "source": "x",
    "url": "https://example.com/post",
    "text": "Bookmark text or URL placeholder",
    "author": "account_name",
    "created_at": "2026-03-14T09:00:00Z",
    "bookmarked_at": "2026-03-16T02:00:00Z",
    "tags": ["agents"],
    "raw_payload": {
      "capture_mode": "url_only"
    }
  }
]
```

### `data/analysis_results.json`

```json
[
  {
    "bookmark_id": "bookmark_001",
    "summary": "Short summary",
    "recommendation_reason": "Why it matters",
    "key_insights": ["Insight 1"],
    "scoring_inputs": {
      "relevance": 7.5,
      "practical_value": 8.0,
      "actionability": 6.5,
      "stage_fit": 8.0,
      "novelty": 5.0,
      "excitement": 6.5,
      "difficulty": 4.0,
      "time_cost": 5.0
    },
    "worth_score": 7.0,
    "effort_score": 4.45,
    "priority_score": 4.33,
    "recommendation_bucket": "build_later",
    "analysis_source": "llm_direct",
    "analyzed_at": "2026-03-17T08:00:00Z"
  }
]
```

## Recommendation Buckets

- **test_this_week**: High priority, act on it now
- **build_later**: Save for future reference
- **archive**: Store but don't actively track
- **ignore**: Drop it

## Differences from Original Design

| Original | Current |
|----------|---------|
| DeepSeek API for analysis | Garfis (LLM) analyzes directly |
| Required `/bookmark` command | Frictionless URL capture works |
| All bookmarks in report | Last 10 only |
| Unlimited report history | Last 2 reports kept |
| Separate analysis step | Analysis happens when URL shared |

## Environment Variables

```bash
# Required
PIPELINE_STAGE=idea_validation  # or prototype, validation, etc.

# Optional - for X API sync (if you want real bookmark sync)
X_CLIENT_ID=
X_CLIENT_SECRET=
X_REDIRECT_URI=
X_USER_ACCESS_TOKEN=
```

No API keys needed for core functionality - Garfis handles all analysis.

## File Sender Skill

The `telegram-file-sender` skill (created separately) allows sending HTML reports directly to Telegram:

```bash
python telegram-file-sender/scripts/send_file.py /path/to/report.html "Optional caption"
```

Requires `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` environment variables.

## License

Personal use. Modify as needed.
