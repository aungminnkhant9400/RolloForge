# RolloForge - Bookmark Intelligence for AI Agents

A personal bookmark pipeline that captures URLs from Telegram, auto-scores them using AI, and deploys a live dashboard. Built for OpenClaw users who want to stop drowning in saved links.

**What it does:**
- Paste any URL in Telegram → automatically scraped, analyzed, categorized, and pushed to GitHub
- Live web dashboard at [rollo-forge.vercel.app](https://rollo-forge.vercel.app)
- AI-powered scoring based on YOUR priorities (not generic tags)
- Auto-extracts meaningful tags (never "general")
- One-command deploy to Vercel

**Current Stats:** 62 bookmarks | 20 test_this_week | 21 build_later | 14 archive

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
pip install -r requirements.txt
playwright install chromium

# Add your DeepSeek API key
echo "DEEPSEEK_API_KEY=your_key_here" > .env
```

### 2. Deploy Dashboard

1. **Fork this repo** on GitHub
2. **Connect to Vercel**:
   - Go to [vercel.com/new](https://vercel.com/new)
   - Import your forked repo
   - Set **Root Directory**: `web`
   - Set **Build Command**: `npm run data && npm run build`
3. **Deploy** → Your dashboard is live!

---

## How It Works

### The Complete Workflow

When you paste a URL in Telegram:

```
URL → Scrape → DeepSeek Analysis → Save → Git Push → Vercel Deploy
 (2s)    (3s)         (5s)          (1s)      (2s)       (30s)
```

1. **Scrape** - Playwright extracts content from X/Twitter/articles
2. **Check Duplicate** - Skips if URL already saved
3. **DeepSeek Analysis** - AI scores based on your profile:
   - Relevance to your priorities (OpenClaw, trading, etc.)
   - Practical value (code to copy vs theory to read)
   - Actionability (specific steps vs vague ideas)
   - Extracts 2-4 meaningful tags (never "general")
4. **Auto-Save** - Bookmark + analysis to JSON
5. **Git Push** - Auto-commits and pushes to GitHub
6. **Vercel Deploy** - Dashboard updates automatically

### Scoring System

| Factor | Weight | How it works |
|--------|--------|--------------|
| **Relevance** | 30% | Matches your high-priority topics |
| **Practical Value** | 25% | Code repos = high, theory = low |
| **Actionability** | 20% | Specific commands = high |
| **Stage Fit** | 15% | Matches your skill level |
| **Novelty** | 10% | New vs familiar content |

**Formula:**
```
Priority = Worth - (0.5 × Effort)
Worth = weighted sum of factors above
```

### Bucket Assignment

| Bucket | Priority | When to use |
|--------|----------|-------------|
| **test_this_week** | ≥6.0 | Actionable now, high value |
| **build_later** | 4.0-6.0 | Good idea, save for later |
| **archive** | 2.0-4.0 | Reference material |
| **ignore** | <2.0 | Low value, skip it |

---

## Customization

### Your Priority Profile

Edit `rolloforge/deepseek_analysis.py` to change what matters:

```python
HIGH_PRIORITY_TOPICS = [
    "openclaw",
    "multi-agent", 
    "polymarket",
    "trading",
    "stock-analysis"
]

MEDIUM_PRIORITY_TOPICS = [
    "agent-frameworks",
    "llm-optimization",
    "automation"
]

LOW_PRIORITY_TOPICS = [
    "pure-theory",
    "crypto"  # unless trading-related
]

TIER_1_SOURCES = {"karpathy", "gregisenberg"}  # +1.5 credibility
TIER_2_SOURCES = {"aakashgupta", "deedydas"}   # +0.5 credibility
```

### Bucket Thresholds

Change when bookmarks get flagged:

```python
# In rolloforge/deepseek_analysis.py prompt:
"recommendation_bucket": "test_this_week"  # if priority >= 7.0 (stricter)
"recommendation_bucket": "test_this_week"  # if priority >= 5.0 (looser)
```

---

## Project Structure

```
RolloForge/
├── data/
│   ├── bookmarks_raw.json      # All bookmarks (62 total)
│   ├── analysis_results.json   # DeepSeek analyses
│   └── seen_bookmarks.json     # Deduplication
├── rolloforge/
│   ├── deepseek_analysis.py    # AI analysis with DeepSeek
│   ├── git_auto.py             # Auto-commit & push
│   ├── bookmark_workflow.py    # Complete scrape→analyze→save→push
│   └── scrapers/
│       └── x_scraper.py        # X/Twitter scraper (ESSENTIAL)
├── web/                         # Next.js dashboard
│   ├── app/                     # Pages
│   ├── components/              # React components
│   └── lib/                     # Data loading
└── scripts/
    ├── generate_report.py       # HTML report
    └── analyze_bookmarks.py     # Batch analysis
```

---

## Daily Workflow

### Morning
Check dashboard for yesterday's bookmarks: https://rollo-forge.vercel.app

### Throughout Day
Paste URLs in Telegram as you find them:
- Auto-scraped, analyzed, tagged
- Auto-pushed to GitHub
- Dashboard updates in ~30 seconds

### Evening
Review `test_this_week` bucket - pick one to implement tomorrow.

---

## Troubleshooting

### DeepSeek Analysis Failing
```bash
# Check API key
echo $DEEPSEEK_API_KEY

# Test DeepSeek
python -c "
from rolloforge.deepseek_analysis import get_deepseek_client
print('✓' if get_deepseek_client() else '✗ API key missing')
"
```

### Dashboard Not Updating
- GitHub has latest? `git log --oneline -3`
- Vercel build status: Check [vercel.com/dashboard](https://vercel.com/dashboard)
- Hard refresh: Ctrl+F5

### X Scraper Not Working
```bash
# Reinstall Playwright
pip install playwright
playwright install chromium
```

---

## Key Features

- ✓ **Auto-scraping** - X/Twitter, articles, GitHub
- ✓ **Duplicate detection** - Won't save same URL twice
- ✓ **DeepSeek AI analysis** - Personalized scoring, not generic
- ✓ **Smart tagging** - Extracts meaning, never "general"
- ✓ **Auto-git-push** - Commits and pushes after every bookmark
- ✓ **Vercel deploy** - Dashboard auto-updates
- ✓ **Dark mode** - Toggle in dashboard
- ✓ **Editable** - Move bookmarks between buckets in edit mode

---

## Credits

Built for OpenClaw power users.

- **Stack:** Python, DeepSeek, Playwright, Next.js, Vercel
- **License:** MIT
- **Author:** [@rollinrollo94](https://x.com/rollinrollo94)

**Questions?** Open an issue.
