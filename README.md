# RolloForge - Bookmark Intelligence for AI Agents

A personal bookmark pipeline that captures URLs from Telegram, auto-scores them based on your priorities, generates actionable reports, and deploys a live dashboard.

**What it does:**
- Paste any URL in Telegram → automatically scraped, scored, and categorized
- Say "bmreport" → get a beautiful HTML report with your top bookmarks
- **NEW**: Live web dashboard at [rolloforge.vercel.app](https://rolloforge.vercel.app)
- Auto-prioritizes based on YOUR criteria (OpenClaw, autoresearch, etc.)

**Works with:** OpenClaw, Claude Code, or any AI agent that can run Python scripts

---

## Quick Start (5 minutes)

### 1. Clone & Setup

```bash
git clone https://github.com/aungminnkhant9400/RolloForge.git
cd RolloForge

# Create Python environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install playwright
playwright install chromium
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

### 3. Test It

```bash
# Generate a sample report
python scripts/generate_report.py

# Check output
open reports/latest_report.html
```

---

## Web Dashboard

RolloForge now includes a **live web dashboard** deployed on Vercel.

### Features
- **Overview**: Stats cards showing total bookmarks by bucket
- **Bookmarks**: Full filtering by bucket, tags, and search
- **Dark mode**: Toggle between light/dark themes
- **Responsive**: Works on desktop and mobile

### Deploy Your Own

1. **Fork this repo** on GitHub
2. **Connect to Vercel**:
   - Go to [vercel.com/new](https://vercel.com/new)
   - Import your forked repo
   - Set **Root Directory**: `web`
   - Set **Build Command**: `npm run data && npm run build`
3. **Deploy** → Your dashboard is live!

### Update Dashboard

The dashboard updates when you push new bookmarks:

```bash
# After adding bookmarks
git add data/bookmarks_raw.json data/analysis_results.json
git commit -m "Add new bookmarks"
git push origin main
```

Vercel auto-deploys on every push.

---

## Integration with OpenClaw

### Telegram Integration (Recommended)

When you send a URL to your OpenClaw agent, it automatically:

1. **Detects the source** (X, GitHub, article)
2. **Scrapes content** (Playwright for X, direct fetch for articles)
3. **Saves bookmark** to `data/bookmarks_raw.json`
4. **Runs AI analysis** → priority score + bucket
5. **Commits & pushes** to GitHub
6. **Triggers deploy** → dashboard updates

**Commands:**
- Paste URL → auto-saved
- "bmreport" → generate HTML report
- "to rolloforge" or "bookmark this" → full workflow (save + analyze + deploy)

### Direct Python Usage

```python
from rolloforge.telegram_ingest import ingest_telegram_bookmark_message
from config.settings import get_settings

settings = get_settings()
message = """
https://x.com/karpathy/status/123

Check out this new agent pattern...
"""

bookmark, analysis, confirmation = ingest_telegram_bookmark_message(message, settings)
print(f"Saved: {bookmark.title}")
print(f"Bucket: {analysis.recommendation_bucket}")
print(f"Priority: {analysis.priority_score}")
```

---

## How It Works

### 1. Bookmark Ingestion

**For X/Twitter URLs:**
- Uses Playwright headless browser
- Navigates to tweet, extracts text + author
- Falls back to placeholder if X blocks (rare)

**For Articles/GitHub:**
- Direct HTTP fetch
- Extracts title, content, author
- Works with most public sites

**Saved to:** `data/bookmarks_raw.json`

### 2. AI Analysis

Analyzes each bookmark:

| Factor | How it's calculated |
|--------|---------------------|
| **Relevance** | Keyword matching against your priority lists |
| **Practical Value** | Code repos=10, tutorials=8, theory=4 |
| **Actionability** | Specific commands=10, vague ideas=4 |
| **Source Credibility** | Tier 1 authors +1.5, Tier 2 +0.5 |
| **Novelty** | First occurrence=8, familiar=4 |
| **Effort** | GPU work -2 (you have resources) |

**Priority Score:**
```
Priority = Worth - 0.5 × Effort
Worth = 0.30×Relevance + 0.25×Practical + 0.20×Actionable + 0.15×Stage + 0.10×Novelty
```

**Bucket Assignment:**
| Bucket | Criteria |
|--------|----------|
| **test_this_week** | Priority ≥6, OpenClaw/autoresearch related |
| **build_later** | Priority ≥3, good but not urgent |
| **archive** | Worth ≥3, reference material |
| **ignore** | Low value |

**Saved to:** `data/analysis_results.json`

### 3. Report Generation

```bash
python scripts/generate_report.py
```

Generates `reports/latest_report.html` with:
- Top 10 priority bookmarks
- Bucket breakdown
- Worth/effort/priority scores
- Direct links to content

### 4. Web Dashboard

- Reads from `data/bookmarks_raw.json` + `data/analysis_results.json`
- React + Next.js frontend
- Static export for fast loading
- Deployed to Vercel

---

## Project Structure

```
RolloForge/
├── ARCHITECTURE.md          # Critical components documentation
├── config/
│   └── settings.py          # Environment config
├── data/
│   ├── bookmarks_raw.json   # All bookmarks (39 total)
│   ├── analysis_results.json # Scoring results
│   └── seen_bookmarks.json  # Track processed
├── reports/
│   ├── latest_report.html   # Current report
│   └── history/             # Old reports
├── rolloforge/
│   ├── models.py            # Data structures
│   ├── scoring.py           # YOUR scoring logic
│   ├── analysis.py          # Analysis pipeline
│   ├── storage.py           # JSON read/write
│   ├── telegram_ingest.py   # Telegram integration
│   └── scrapers/
│       └── x_scraper.py     # X/Twitter scraper (ESSENTIAL)
├── web/                     # Next.js dashboard
│   ├── app/                 # Pages
│   ├── components/          # React components
│   ├── lib/                 # Data loading
│   └── out/                 # Static export
├── scripts/
│   ├── generate_report.py   # Generate HTML report
│   ├── analyze_bookmarks.py # Run AI analysis
│   └── run_pipeline.py      # Full pipeline
├── templates/
│   └── report.html.j2       # Report template
└── README.md                # This file
```

---

## Critical Components

### X/Twitter Scraper (`rolloforge/scrapers/x_scraper.py`)

**ESSENTIAL** - Do not remove. See `ARCHITECTURE.md` for details.

Without this, X bookmarks get placeholder text → low priority scores.

**How it works:**
- Playwright headless browser navigates to tweet
- Extracts tweet text, author, metadata
- Multiple fallback selectors for X's changing HTML
- Blocks images for faster loading

**Test it:**
```bash
python -c "
from rolloforge.scrapers import fetch_x_content_sync
result = fetch_x_content_sync('https://x.com/karpathy/status/123')
print(result['text'][:100])
"
```

---

## Customization

### Change Scoring Priorities

Edit `rolloforge/scoring.py`:

```python
# Your focus areas
OPENCLAW_KEYWORDS = ["your_keyword", "another_keyword"]

# Trusted sources
TIER_1_SOURCES = {"your_trusted_author"}

# Adjust weights
WORTH_WEIGHTS = {
    'relevance': 0.35,  # Make this more important
    'practical_value': 0.20,
    # ...
}
```

### Change Bucket Thresholds

```python
def recommendation_bucket(inputs, worth, priority):
    if priority >= 7:  # Stricter
        return "test_this_week"
    # ...
```

### Custom Dashboard Theme

Edit `web/app/globals.css`:

```css
:root {
  --background: #your-color;
  --accent: #your-accent;
}
```

---

## Usage Examples

### Daily Workflow

1. **Morning**: Check Telegram for bookmarks shared overnight
2. **During day**: Paste interesting URLs → auto-saved & scored
3. **Evening**: Say "bmreport" → review top 10
4. **Check dashboard**: See all bookmarks with filters
5. **Weekend**: Pick from `test_this_week` bucket to implement

### Full Workflow Command

```
You: https://x.com/karpathy/status/123456

Agent: ✓ Bookmarked: X post by @karpathy
       ✓ Analyzed: Priority 6.8, Bucket: test_this_week
       ✓ Committed to Git
       ✓ Deployed to rolloforge.vercel.app
```

### Manual Analysis

```bash
# Analyze new bookmarks
python scripts/analyze_bookmarks.py

# Force re-analyze all
python scripts/analyze_bookmarks.py --force-all
```

---

## Troubleshooting

### X scraper not working

```bash
# Reinstall Playwright
pip install playwright
playwright install chromium

# Test
python -c "from rolloforge.scrapers import fetch_x_content_sync; print(fetch_x_content_sync('https://x.com/karpathy/status/1884329367873197363'))"
```

### Dashboard shows 404

- Check Vercel settings: Root Directory = `web`
- Check Build Command: `npm run data && npm run build`
- Check Output Directory: (leave blank for auto)

### Empty report

```bash
# Check bookmarks exist
wc -l data/bookmarks_raw.json

# Check analysis exists
wc -l data/analysis_results.json

# Regenerate analysis
python scripts/analyze_bookmarks.py --force-all
```

---

## Architecture Notes

See `ARCHITECTURE.md` for:
- Critical components that must not be removed
- Scaling considerations
- Fallback behaviors
- Integration patterns

**Key principle:** Every component has a fallback. If X scraping fails, user can paste text. If AI analysis fails, uses heuristic scoring.

---

## Credits

Built for OpenClaw users who want automated bookmark prioritization.

- **Inspiration**: Karpathy's autoresearch, agent workflow community
- **Stack**: Python, Playwright, Next.js, Vercel
- **License**: MIT

**Questions?** Open an issue or DM on X: [@rollinrollo94](https://x.com/rollinrollo94)