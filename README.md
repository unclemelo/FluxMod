
# AutoMod

A modular Discord auto-moderation system with independent bot, backend API, and web dashboard.

[![Netlify Status](https://api.netlify.com/api/v1/badges/54357230-e98a-4ee1-890e-8fe059637adb/deploy-status)](https://app.netlify.com/projects/fluxmod/deploys)

- **Bot**: Discord bot that enforces rules in real-time  
- **Backend**: FastAPI REST API with Fluxer OAuth for rule management  
- **Frontend**: Lightweight web dashboard for managing rules

Table of Contents
- Project Structure
- Quick Start
- Deployment
- Architecture
- Configuration
- Development
- Contributing
- License

Project Structure
-----------------

```
AutoMod/
├── bot/                  # Discord bot (runs on server)
│   ├── bot.py
│   ├── cogs/            # Discord command groups
│   ├── utils/           # Shared engine, models, manager
│   ├── docs/            # Architecture docs
│   ├── requirements.txt
│   └── README.md
├── backend/             # FastAPI backend (runs on server)
│   ├── api.py
│   ├── .env            # OAuth & config
│   ├── data.json       # JSON store (or swap for database)
│   ├── requirements.txt
│   └── README.md
├── frontend/            # Web dashboard (self-hosted or cloud)
│   ├── index.html      # Standalone HTML app
│   └── README.md
└── README.md           # This file
```

Quick Start
-----------

### Local Development

Run all three components locally for testing:

**Terminal 1 — Bot:**
```bash
cd bot
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# Linux/Mac
source .venv/bin/activate
pip install -r requirements.txt
python bot.py
```

**Terminal 2 — Backend:**
```bash
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# Create .env with Fluxer credentials (see backend/README.md)
python -m uvicorn api:app --reload --host 127.0.0.1 --port 8000
```

**Terminal 3 — Frontend:**
```bash
cd frontend
# Any HTTP server works
python -m http.server 3000
# or: npx http-server on port 3000
```

Frontend will prompt for backend URL: `http://127.0.0.1:8000`

Deployment
----------

### Bot (Ubuntu Server)

```bash
cd bot
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure
echo "DISCORD_TOKEN=your_token" > .env
echo "BACKEND_API_URL=http://localhost:8000" >> .env

# Run with systemd (see bot/README.md for full config)
```

### Backend (Ubuntu Server)

```bash
cd backend
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure with Fluxer OAuth
cat > .env << EOF
OAUTH_PROVIDER=fluxer
FLUXER_CLIENT_ID=xxx
FLUXER_CLIENT_SECRET=xxx
FLUXER_AUTHORIZE_URL=https://api.fluxer.app/v1/oauth2/authorize
FLUXER_TOKEN_URL=https://api.fluxer.app/v1/oauth2/token
FLUXER_API_BASE_URL=https://api.fluxer.app/v1
FLUXER_USER_ENDPOINT=https://api.fluxer.app/v1/oauth2/userinfo
SESSION_SECRET=$(head -c 32 /dev/urandom | base64)
OAUTH_REDIRECT_URI=https://api.example.com/auth
EOF

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 api:app
```

See backend/README.md for nginx + systemd config.

### Frontend (Any Static Host)

The frontend is a single `index.html` — deploy anywhere:

- **GitHub Pages**: Push to repo, enable in settings  
- **Vercel**: Deploy `frontend/` directory  
- **Netlify**: Connect repo  
- **AWS S3 + CloudFront**: Upload files  
- **Cloudflare Pages**: Connect repo  
- **Shared hosting**: FTP upload

On first visit, enter backend API URL (e.g., `https://api.example.com`). Stored in localStorage.

Update `allow_origins` in `backend/api.py` if frontend is on a different domain.

Architecture
------------

- **Bot** fetches rules from backend API and enforces them in Discord/Fluxer
- **Backend** manages rules, guilds, and user sessions; handles OAuth
- **Frontend** calls backend API; users login via Fluxer OAuth

```
User → Frontend (OAuth) → Backend (Fluxer) → Session established
        ↓
     Frontend calls /api/guilds, /api/rules (authenticated)
        ↓
     Bot fetches rules from Backend and enforces them
```

Configuration
-------------

See individual component READMEs:
- `bot/README.md` — Discord token, backend URL
- `backend/README.md` — Fluxer OAuth, session secret, database setup
- `frontend/README.md` — Backend API URL (configured at runtime)

Development
-----------

- Modify rules: `bot/utils/automod_engine.py` and `backend/api.py`
- Update models: `bot/utils/automod_models.py`
- Add Discord commands: `bot/cogs/automod.py`
- Improve dashboard: `frontend/index.html`

Run tests and linters before submitting PRs.

Contributing
------------

Issues and pull requests welcome. Follow repo contribution guidelines.

License
-------

MIT


