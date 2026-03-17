# RolloForge

RolloForge is a personal-use bookmark intelligence pipeline for X bookmarks. It syncs bookmark data into local JSON files, analyzes new entries with DeepSeek, computes recommendation scores in Python, and renders a standalone HTML report at `reports/latest_report.html`.

## v1 scope

- No web frontend
- No database
- JSON storage only
- DeepSeek-backed semantic analysis with graceful fallback
- Python scoring and recommendation mapping
- Standalone HTML reporting for all bookmarks

## Project layout

- `config/settings.py`: environment-driven settings and project paths
- `data/bookmarks_raw.json`: normalized bookmark records
- `data/analysis_results.json`: analysis outputs and scoring results
- `data/seen_bookmarks.json`: known synced bookmark IDs plus analyzed bookmark IDs
- `reports/latest_report.html`: latest standalone report
- `reports/history/`: timestamped historical reports
- `rolloforge/`: core package modules
- `scripts/`: runnable entry points
- `templates/report.html.j2`: HTML report template

## Setup

1. Create a Python 3.11+ environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and populate the variables you want to use.

## Real X setup

RolloForge now supports real bookmark sync from the authenticated X user through the X API.

1. Create an X developer app that supports OAuth 2.0 Authorization Code Flow.
2. Configure the app with a redirect URI that exactly matches `X_REDIRECT_URI`.
3. Enable user authentication and request these scopes:
   - `bookmark.read`
   - `tweet.read`
   - `users.read`
   - `offline.access`
4. Copy `.env.example` to `.env`.
5. Put your OAuth app values in:
   - `X_CLIENT_ID`
   - `X_CLIENT_SECRET`
   - `X_REDIRECT_URI`
6. Run the one-time helper:

```bash
python scripts/get_x_user_token.py
```

7. Visit the printed authorization URL.
8. After X redirects back to your redirect URI, copy either:
   - the full callback URL, or
   - just the `code` value
9. Paste that into the script when prompted.
10. The helper will exchange the code for tokens, print a safe token summary, call `GET /2/users/me`, and print:
   - `X_USER_ID=...`
   - a redacted `X_USER_ACCESS_TOKEN` placeholder
11. If `GET /2/users/me` fails, the helper will print the status code, raw response body, and a scope-vs-auth diagnosis.
12. Leave `X_BOOKMARKS_SOURCE_FILE` empty if you want real API sync.

### Exact `.env` values needed for real X sync

Required:

- `X_CLIENT_ID`
- `X_CLIENT_SECRET`
- `X_REDIRECT_URI`
- `X_USER_ACCESS_TOKEN`

Optional but supported:

- `X_USER_ID`
- `X_API_BASE_URL` default: `https://api.x.com/2`
- `X_MAX_RESULTS` default: `100`
- `X_MAX_PAGES` default: `50`
- `X_USER_AGENT`

Local-file mode only:

- `X_BOOKMARKS_SOURCE_FILE`

DeepSeek remains separate:

- `DEEPSEEK_API_KEY`
- `DEEPSEEK_API_BASE`
- `DEEPSEEK_MODEL`
- `DEEPSEEK_TIMEOUT_SECONDS`
- `DEEPSEEK_MAX_RETRIES`
- `PIPELINE_STAGE`

## Run

Use local sample data only:

```bash
python scripts/run_pipeline.py --skip-sync
```

Run the full pipeline with sync enabled:

```bash
python scripts/run_pipeline.py
```

Run the one-time OAuth helper:

```bash
python scripts/get_x_user_token.py
```

Test bookmark sync only without writing files:

```bash
python scripts/sync_x_bookmarks.py --dry-run
```

Run individual steps:

```bash
python scripts/sync_x_bookmarks.py
python scripts/analyze_bookmarks.py
python scripts/generate_report.py
```

## Telegram / OpenClaw workflow

For personal VPS use, OpenClaw can map Telegram commands to local scripts:

- `/bookmark` -> `python scripts/ingest_telegram_bookmark.py`
- `/bmreport` -> `python scripts/bmreport.py`
- `/bmsummary` -> `python scripts/bmsummary.py`

Structured bookmark message format:

```text
/bookmark
URL: https://example.com/post
Text: copied post or article text
Note: why I saved it
Tag: agents
Source: article
```

Rules:

- `URL` is required
- `Text` is required
- `Note` is optional
- `Tag` is optional and defaults to `general`
- `Source` is optional and is inferred from the URL when missing

Telegram bookmark ingestion immediately:

1. saves the raw bookmark to `data/bookmarks_raw.json`
2. analyzes the bookmark immediately
3. upserts the result into `data/analysis_results.json`
4. returns a short confirmation with source, tag, recommendation, priority, and next action

`/bmreport` behavior:

1. generates the HTML report at `reports/latest_report.html`
2. computes summary counts for all recommendation buckets
3. returns summary text plus the report path
4. stays easy for OpenClaw to send as a Telegram document by attaching `reports/latest_report.html`

`/bmsummary` behavior:

- returns only:
  - `total`
  - `test_this_week`
  - `build_later`
  - `archive`
  - `ignore`

## JSON contracts

### `data/bookmarks_raw.json`

```json
[
  {
    "id": "bookmark_001",
    "source": "x",
    "url": "https://example.com/post",
    "text": "Bookmark text",
    "author": "account_name",
    "created_at": "2026-03-14T09:00:00Z",
    "bookmarked_at": "2026-03-16T02:00:00Z",
    "tags": ["agents"],
    "raw_payload": {}
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
    "analysis_source": "deepseek"
  }
]
```

## OpenClaw trigger

OpenClaw can invoke:

```bash
python scripts/run_pipeline.py
```

If OpenClaw exports bookmarks to a local file first, point `X_BOOKMARKS_SOURCE_FILE` at that file and the sync step will normalize and merge it into `data/bookmarks_raw.json`.

For real X syncing, leave `X_BOOKMARKS_SOURCE_FILE` empty and set `X_USER_ACCESS_TOKEN`.

## Troubleshooting

### 403 on `GET /2/users/me`

If `python scripts/get_x_user_token.py` exchanges the code successfully but then gets a 403 from `GET /2/users/me`, the helper now prints:

- the token response summary:
  - `token_type`
  - `expires_in`
  - whether a `refresh_token` exists
  - the granted `scope` field if X returned one
- the exact scopes requested in the authorization URL
- the `/2/users/me` status code
- the raw `/2/users/me` response body
- a short diagnosis of whether the failure looks like missing scope versus a broader auth/app-permission issue

Common causes:

- the X app did not actually grant `users.read`
- the granted scope set is narrower than the requested scope set
- the app or project access level is not allowed to use the endpoint
- the token is valid enough to exchange, but not valid for `/2/users/me`
