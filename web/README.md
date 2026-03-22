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

This dashboard is automatically deployed to Vercel when you push to GitHub.

URL: https://rolloforge.vercel.app
