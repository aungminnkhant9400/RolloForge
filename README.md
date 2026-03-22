# RolloForge - Bookmark Intelligence for AI Agents

A personal bookmark pipeline that captures URLs from Telegram, auto-scores them based on your priorities, and generates actionable HTML reports.

**What it does:**
- Paste any URL in Telegram → automatically scraped, scored, and categorized
- Say "bmreport" → get a beautiful HTML report with your top bookmarks
- Auto-prioritizes based on YOUR criteria (OpenClaw, autoresearch, etc.)

**Works with:** OpenClaw, Claude Code, or any AI agent that can run Python scripts

---

## Quick Start (5 minutes)

### 1. Clone & Setup

```bash
git clone https://github.com/yourusername/RolloForge.git
cd RolloForge

# Create Python environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Your Scoring Profile

Edit `rolloforge/scoring.py` to match YOUR priorities:

```python
# What content matters to you?
OPENCLAW_KEYWORDS = ["openclaw", "claude code", "agent team"]
AUTORESEARCH_KEYWORDS = ["autoresearch", "optimization"]
TRADING_KEYWORDS = ["trading", "crypto"]

# Who do you trust?
TIER_1_SOURCES = {"karpathy", "gregisenberg"}  # +1.5 credibility
TIER_2_SOURCES = {"aakashgupta", "deedydas"}   # +0.5 credibility

# Adjust scoring weights
WORTH_WEIGHTS = {
    'relevance': 0.30,      # Most important
    'practical_value': 0.25,
    'actionability': 0.20,
    'stage_fit': 0.15,
    'novelty': 0.10,
}
```

### 3. Set Environment Variables

```bash
# Copy template
cp .env.example .env

# Edit .env
PIPELINE_STAGE=building_agents  # Your current focus
```

### 4. Test It

```bash
# Generate a sample report
python scripts/generate_report.py

# Check output
open reports/latest_report.html
```

---

## Integration with OpenClaw

### Option A: Telegram Integration (Recommended)

Add this to your OpenClaw agent's skills:

```python
# In your OpenClaw agent, when user sends a URL:

import subprocess
import json

def save_bookmark(url, text, author="user"):
    \"\"\"Save a bookmark to RolloForge.\"\"\""
    bookmark = {
        "id": f"bookmark_{hash(url) % 100000000}",
        "source": "x" if "x.com" in url else "article",
        "url": url,
        "text": text,
        "author": author,
        "created_at": datetime.now().isoformat(),
        "bookmarked_at": datetime.now().isoformat(),
        "tags": ["openclaw"],
    }
    
    # Load existing
    with open("data/bookmarks_raw.json", "r") as f:
        bookmarks = json.load(f)
    
    bookmarks.append(bookmark)
    
    with open("data/bookmarks_raw.json", "w") as f:
        json.dump(bookmarks, f, indent=2)
    
    return "Bookmark saved"

# When user says "bmreport":
def generate_report():
    result = subprocess.run(
        ["python", "scripts/generate_report.py"],
        capture_output=True,
        text=True,
        cwd="/path/to/RolloForge"
    )
    return result.stdout
```

### Option B: Direct Integration

Modify `telegram_ingest.py` to accept messages from your agent:

```python
# Add to telegram_ingest.py

def ingest_from_agent(url: str, text: str, author: str = "agent") -> dict:
    \"\"\"Ingest a bookmark directly from an AI agent.\"\"\""
    parsed = ParsedTelegramBookmark(
        url=url,
        text=text,
        note=None,
        tag="agent",
        source="agent",
        raw_message=f"From agent: {url}",
        capture_mode="agent_direct"
    )
    
    bookmark = bookmark_from_parsed_message(parsed)
    # ... rest of ingestion logic
    
    return {
        "id": bookmark.id,
        "title": bookmark.title,
        "bucket": analysis.recommendation_bucket
    }
```

---

## How Scoring Works

### 1. Automatic Content Analysis

When you save a bookmark, the system analyzes:

| Factor | How it's calculated |
|--------|---------------------|
| **Relevance** | Keyword matching against your priority lists |
| **Practical Value** | Code repos=10, tutorials=8, theory=4 |
| **Actionability** | Specific commands=10, vague ideas=4 |
| **Source Credibility** | Tier 1 authors +1.5, Tier 2 +0.5 |
| **Novelty** | First occurrence=8, familiar=4 |
| **Effort** | GPU work -2 (you have resources) |

### 2. Priority Score

```
Priority = Worth - 0.5 × Effort

Worth = 0.30×Relevance + 0.25×Practical + 0.20×Actionable + 0.15×Stage + 0.10×Novelty
```

### 3. Bucket Assignment

| Bucket | Criteria |
|--------|----------|
| **test_this_week** | Priority ≥6, OpenClaw/autoresearch related |
| **build_later** | Priority ≥3, good but not urgent |
| **archive** | Worth ≥3, reference material |
| **ignore** | Low value |

---

## Customization Guide

### Change What Gets Prioritized

Edit `scoring.py`:

```python
# Your focus areas (higher = more important)
def calculate_relevance(text, author, tags):
    if "YOUR_KEYWORD" in text:
        return 10.0  # Top priority
    # ... rest of logic

# Trusted sources
TIER_1_SOURCES = {
    "yourfavorite_author",
    "another_trusted_source"
}
```

### Adjust Bucket Thresholds

```python
def recommendation_bucket(inputs, worth, priority):
    # Make it stricter or looser
    if priority >= 7:  # Was 6
        return "test_this_week"
    # ...
```

### Change Report Style

Edit `templates/report.html.j2`:
- Colors, fonts, layout
- What fields to show
- How many bookmarks per report

---

## Project Structure

```
RolloForge/
├── config/
│   └── settings.py          # Environment config
├── data/
│   ├── bookmarks_raw.json   # All bookmarks
│   ├── analysis_results.json # Scoring results
│   └── seen_bookmarks.json  # Track processed
├── reports/
│   ├── latest_report.html   # Current report
│   └── history/             # Old reports (last 2 kept)
├── rolloforge/
│   ├── models.py            # Data structures
│   ├── scoring.py           # YOUR scoring logic
│   ├── analysis.py          # Analysis pipeline
│   ├── storage.py           # JSON read/write
│   └── telegram_ingest.py   # Telegram integration
├── scripts/
│   ├── generate_report.py   # Generate HTML report
│   └── run_pipeline.py      # Full pipeline
├── templates/
│   └── report.html.j2       # Report template
└── README.md                # This file
```

---

## Data Format

### Bookmark Record

```json
{
  "id": "bookmark_abc123",
  "title": "Karpathy on 10 parallel agent windows.",
  "source": "x",
  "url": "https://x.com/karpathy/status/...",
  "text": "Full content...",
  "author": "karpathy",
  "tags": ["openclaw", "agents"],
  "bookmarked_at": "2026-03-21T20:00:00Z",
  "raw_payload": {
    "capture_mode": "url_only",
    "scraped_via": "playwright"
  }
}
```

### Analysis Result

```json
{
  "bookmark_id": "bookmark_abc123",
  "summary": "Karpathy shares 10 insights on agent workflows...",
  "recommendation_reason": "High relevance to OpenClaw build...",
  "scoring_inputs": {
    "relevance": 10.0,
    "practical_value": 8.5,
    "actionability": 9.0,
    "stage_fit": 10.0,
    "novelty": 8.5,
    "difficulty": 4.0,
    "time_cost": 4.0
  },
  "worth_score": 8.88,
  "effort_score": 4.0,
  "priority_score": 6.88,
  "recommendation_bucket": "test_this_week",
  "analyzed_at": "2026-03-21T20:01:00Z"
}
```

---

## Usage Examples

### Daily Workflow

1. **Morning**: Check Telegram for bookmarks shared overnight
2. **During day**: Paste interesting URLs → auto-saved & scored
3. **Evening**: Say "bmreport" → review top 10 in HTML
4. **Weekend**: Pick from `test_this_week` bucket to implement

### Weekly Review

```bash
# Regenerate report with latest analysis
cd RolloForge
python scripts/generate_report.py

# View in browser
open reports/latest_report.html
```

### Finding Old Bookmarks

```bash
# Search by tag
python -c "
import json
with open('data/bookmarks_raw.json') as f:
    bookmarks = json.load(f)
for b in bookmarks:
    if 'autoresearch' in b.get('tags', []):
        print(b['title'])
"
```

---

## Troubleshooting

### Report shows empty

```bash
# Check if bookmarks exist
wc -l data/bookmarks_raw.json

# Check if analysis exists
wc -l data/analysis_results.json
```

### Scoring seems off

1. Check `scoring.py` - are your keywords correct?
2. Verify author names match (case-insensitive)
3. Adjust weights to match your priorities

### Telegram not responding

- Ensure OpenClaw has access to RolloForge directory
- Check that `telegram_ingest.py` is importable
- Verify JSON files are writable

---

## Advanced: Custom Scoring

Want to score based on different criteria? Create your own scorer:

```python
# my_scorer.py
from rolloforge.scoring import ScoringInputs

def my_custom_scorer(bookmark) -> ScoringInputs:
    return ScoringInputs(
        relevance=10.0 if "AI" in bookmark.text else 5.0,
        practical_value=8.0 if "github" in bookmark.url else 4.0,
        actionability=7.0,
        stage_fit=6.0,
        novelty=5.0,
        excitement=8.0,
        difficulty=3.0,
        time_cost=4.0,
    )
```

Then use it in `analysis.py`.

---

## License

MIT - Modify as needed for your own bookmark intelligence system.

---

## Credits

Built for OpenClaw users who want automated bookmark prioritization. Inspired by Karpathy's autoresearch and the agent workflow community.

**Questions?** Open an issue or DM on X: [@yourusername](https://x.com/rollinrollo94)
