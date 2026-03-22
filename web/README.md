# RolloForge Web Dashboard

A responsive web dashboard for viewing and filtering your RolloForge bookmarks.

## Features

- **Overview Tab**: Stats cards and recent bookmarks
- **Bookmarks Tab**: Full filtering by bucket and tags, plus search
- **Responsive Design**: Works on phone and desktop
- **No Backend**: Reads directly from JSON files

## Local Development

```bash
cd web
npm install
npm run dev
```

Open http://localhost:3000

## Build for Production

```bash
cd web
npm run build
```

Static files output to `web/dist/`

## Data Source

The dashboard reads from:
- `../data/bookmarks_raw.json`
- `../data/analysis_results.json`

## Deployment

### Option 1: Vercel Dashboard (Recommended)

1. Go to https://vercel.com/new
2. Import your GitHub repo
3. **Important**: Set "Root Directory" to `web` in project settings
4. Deploy

### Option 2: Vercel CLI

```bash
npm i -g vercel
vercel --cwd web
```

URL: https://rolloforge.vercel.app
