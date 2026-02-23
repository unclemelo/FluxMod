# AutoMod Frontend

Static dashboard for managing AutoMod rules and settings. Hosted independently from the backend.

## Features

- OAuth login (Fluxer)
- View guilds and rules
- Create, update, delete rules
- Simple, lightweight UI

## Setup

1. Copy all files from this directory to your web host
2. Update the backend URL in `index.html` or when prompted on first load
3. Deploy (e.g. GitHub Pages, Vercel, Netlify, or a static host)

## Configuration

The dashboard prompts for the backend URL on first load:
- Example: `http://localhost:8000` (local dev)
- Example: `https://api.example.com` (production)

The URL is stored in `localStorage` for convenience.

## Development

- `index.html` — complete dashboard page
- No build process or dependencies required
- Works in any modern browser

## Deployment Options

### GitHub Pages

1. Push repo to GitHub
2. Enable GitHub Pages in repo settings
3. Point to `frontend/` directory
4. Update backend URL when prompted

### Vercel / Netlify

1. Connect repo to Vercel/Netlify
2. Set build root to `frontend/`
3. Deploy
4. Update backend URL

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
