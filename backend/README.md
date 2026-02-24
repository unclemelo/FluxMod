# AutoMod Backend API

FastAPI-based REST API for AutoMod rule management with Fluxer OAuth authentication.

## Endpoints

- `GET /api/me` — get current user
- `GET /api/guilds` — list guilds (authenticated)
- `GET /api/guilds/{guild_id}/rules` — list rules for guild (authenticated)
- `POST /api/guilds/{guild_id}/rules` — create rule (authenticated)
- `PUT /api/rules/{rule_id}` — update rule (authenticated)
- `DELETE /api/rules/{rule_id}` — delete rule (authenticated)
- `GET /login` — OAuth redirect
- `GET /auth` — OAuth callback
- `GET /logout` — clear session

## Local Setup

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# Linux/Mac
source .venv/bin/activate
pip install -r requirements.txt
```

Create `.env` in this directory:

```env
OAUTH_PROVIDER=fluxer
FLUXER_CLIENT_ID=your_client_id
FLUXER_CLIENT_SECRET=your_client_secret
FLUXER_AUTHORIZE_URL=https://api.fluxer.app/v1/oauth2/authorize
FLUXER_TOKEN_URL=https://api.fluxer.app/v1/oauth2/token
FLUXER_API_BASE_URL=https://api.fluxer.app/v1
FLUXER_USER_ENDPOINT=https://api.fluxer.app/v1/oauth2/userinfo
SESSION_SECRET=your_secure_random_secret
OAUTH_REDIRECT_URI=http://127.0.0.1:8000/auth
FRONTEND_URL=http://localhost:3000
ENVIRONMENT=development
# Optional overrides:
# SESSION_SAME_SITE=lax
# SESSION_HTTPS_ONLY=false
```

For production (HTTPS + cross-site frontend), use:

```env
ENVIRONMENT=production
SESSION_SAME_SITE=none
SESSION_HTTPS_ONLY=true
FRONTEND_URL=https://fluxmod.netlify.app
```
SESSION_HTTPS_ONLY=true
```

Start the server:

```bash
uvicorn api:app --reload --host 127.0.0.1 --port 8000
```

Visit http://127.0.0.1:8000/docs for interactive API docs.

## Run bot from backend process (optional)

You can run the Fluxer bot in the same service as the backend.

Set these environment variables:

```env
RUN_BOT_WITH_BACKEND=true
FLUXER_TOKEN=your_bot_token_here
# Optional override:
# BOT_ENTRYPOINT=./bot/bot.py
```

Notes:
- Install bot dependencies in the same environment as backend (`pip install -r bot/requirements.txt`).
- Use a single backend worker when running bot in-process to avoid duplicate bot instances.

## Deployment (Render)

This repository includes a Render blueprint at `render.yaml` (repo root).

### Option A: Blueprint deploy (recommended)

1. Push this repo to GitHub.
2. In Render, choose **New +** → **Blueprint**.
3. Select this repository.
4. Render reads `render.yaml` and creates `automod-backend`.
5. In the service environment settings, fill these required secrets:
    - `FLUXER_CLIENT_ID`
    - `FLUXER_CLIENT_SECRET`
    - `OAUTH_REDIRECT_URI` = `https://<your-render-service>.onrender.com/auth`

### Option B: Manual web service

- Root Directory: `backend`
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn -k uvicorn.workers.UvicornWorker api:app --bind 0.0.0.0:$PORT`

Required environment values:

```env
OAUTH_PROVIDER=fluxer
FLUXER_CLIENT_ID=<from Fluxer>
FLUXER_CLIENT_SECRET=<from Fluxer>
FLUXER_AUTHORIZE_URL=https://api.fluxer.app/v1/oauth2/authorize
FLUXER_TOKEN_URL=https://api.fluxer.app/v1/oauth2/token
FLUXER_API_BASE_URL=https://api.fluxer.app/v1
FLUXER_USER_ENDPOINT=https://api.fluxer.app/v1/oauth2/userinfo
SESSION_SECRET=<long-random-string>
ENVIRONMENT=production
SESSION_SAME_SITE=none
SESSION_HTTPS_ONLY=true
OAUTH_REDIRECT_URI=https://<your-render-service>.onrender.com/auth
FRONTEND_URL=https://fluxmod.netlify.app
```

After deploy, update your Fluxer OAuth app callback URL to match `OAUTH_REDIRECT_URI`.

## Data Storage

Currently uses JSON file (`data.json`) for persistence. For production, replace with:
- PostgreSQL + SQLAlchemy
- MongoDB
- Any other database

## Deployment (Ubuntu)

1. Clone repo, navigate to `backend/` directory
2. Create venv and install deps
3. Configure `.env` with Fluxer credentials
4. Run with gunicorn + nginx:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 api:app
```

Nginx config example:

```nginx
server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Or use systemd service:

```ini
[Unit]
Description=AutoMod Backend API
After=network.target

[Service]
Type=simple
User=automod
WorkingDirectory=/home/automod/AutoMod/backend
Environment="PYTHONUNBUFFERED=1"
ExecStart=/home/automod/AutoMod/backend/.venv/bin/gunicorn -w 4 -b 0.0.0.0:8000 api:app
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable automod-backend
sudo systemctl start automod-backend
```

## CORS

To allow requests from frontend hosted elsewhere, add to `api.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://example.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Update `allow_origins` with your frontend domain.