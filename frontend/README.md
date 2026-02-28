# FluxMod Frontend

React frontend (Vite) with route-based pages in `src/pages` and static assets in `public/`.

## Features

- OAuth login (Fluxer)
- Separate landing/login page and dashboard page
- View guilds and rules
- Create, update, delete rules
- Simple, lightweight UI

## Setup

1. Install dependencies: `npm install`
2. Run locally: `npm run dev`
3. Build for production: `npm run build`
4. Serve built output from `dist/`

## Configuration

The dashboard prompts for the backend URL on first load:
- Example: `http://localhost:8000` (local dev)
- Example: `https://api.example.com` (production)

The URL is stored in `localStorage` for convenience.

## Development

- `src/pages/` — React JSX pages (`/`, `/dashboard`, `/info`, `/contributors`)
- `src/components/` — shared React UI components
- `public/` — static assets and legacy compatibility files
- `dist/` — Vite production build output (do not edit manually)
- `dist-legacy/` — optional Parcel legacy output

### Local dev (React)

```bash
npm install
npm run dev
```

### Production build (React)

```bash
npm run build
```

### Legacy pages (optional during migration)

```bash
npm run legacy:dev
npm run legacy:build
```

## Deployment Options

### GitHub Pages

1. Push repo to GitHub
2. Enable GitHub Pages in repo settings
3. Point to `frontend/` directory
4. Update backend URL when prompted

### Render

1. Connect repo to Render
2. Set base directory to `frontend/`
3. Build command: `npm run build`
4. Publish directory: `dist`
5. Deploy and update backend URL

### Simple Static Host

Upload contents of `dist/` to any static host (AWS S3, Azure Blob Storage, etc).

## API Integration

The frontend calls these endpoints on the backend:

- `GET /api/me` — check if logged in
- `GET /api/guilds` — list guilds
- `GET /api/guilds/{guild_id}/rules` — list rules for a guild
- `POST /api/guilds/{guild_id}/rules` — create rule
- `GET /login` — OAuth redirect
- `POST /logout` — clear session

All endpoints require authentication except `/login`.
