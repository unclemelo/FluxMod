# AutoMod Frontend

[![Netlify Status](https://api.netlify.com/api/v1/badges/54357230-e98a-4ee1-890e-8fe059637adb/deploy-status)](https://app.netlify.com/projects/fluxmod/deploys)

Static dashboard for managing AutoMod rules and settings. Hosted independently from the backend.

## Deploy Status

- Netlify project: https://app.netlify.com/projects/fluxmod/deploys
- Badge above shows the latest production deploy state.

## Features

- OAuth login (Fluxer)
- View guilds and rules
- Create, update, delete rules
- Simple, lightweight UI

## Setup

1. Copy all files from this directory to your web host
2. Update the backend URL in `index.html` or when prompted on first load
3. Deploy (e.g. GitHub Pages, Netlify, or a static host)

## Configuration

The dashboard prompts for the backend URL on first load:
- Example: `http://localhost:8000` (local dev)
- Example: `https://api.example.com` (production)

The URL is stored in `localStorage` for convenience.

## Development

- `public/index.html` — source entry page
- `public/JS/` — source JavaScript modules
- `public/Styles/styles.css` — source stylesheet
- `dist/` — generated build output (do not edit manually)
- Uses Parcel for local development and production builds
- Works in any modern browser

### Local dev

```bash
npm install
npm run dev
```

### Production build

```bash
npm run build
```

## Deployment Options

### GitHub Pages

1. Push repo to GitHub
2. Enable GitHub Pages in repo settings
3. Point to `frontend/` directory
4. Update backend URL when prompted

### Netlify

1. Connect repo to Netlify
2. Set base directory to `frontend/`
3. Build command: `npm run build`
4. Publish directory: `dist`
5. Deploy and update backend URL

### Simple Static Host

Upload `index.html` and any static assets to any static host (AWS S3, Azure Blob Storage, etc).

## API Integration

The frontend calls these endpoints on the backend:

- `GET /api/me` — check if logged in
- `GET /api/guilds` — list guilds
- `GET /api/guilds/{guild_id}/rules` — list rules for a guild
- `POST /api/guilds/{guild_id}/rules` — create rule
- `GET /login` — OAuth redirect
- `POST /logout` — clear session

All endpoints require authentication except `/login`.
