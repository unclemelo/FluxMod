from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Literal
import uuid
import json
import pathlib
import os
import subprocess
import sys
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth
from dotenv import load_dotenv

ROOT = pathlib.Path(__file__).parent
DATA_FILE = ROOT / "data.json"

# Load .env from the backend directory
load_dotenv(dotenv_path=str(ROOT / ".env"))

app = FastAPI(title="AutoMod Backend API")

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",                      # Local dev
        "https://fluxmod-frontend.onrender.com",      # Production frontend on Render
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth / session configuration
SESSION_SECRET = os.getenv("SESSION_SECRET") or "melobytesarebestbytes"
OAUTH_REDIRECT_URI = os.getenv("OAUTH_REDIRECT_URI") or "http://127.0.0.1:8000/auth"
IS_PRODUCTION = os.getenv("ENVIRONMENT") == "production"
SESSION_SAME_SITE: Literal["lax", "strict", "none"] = os.getenv("SESSION_SAME_SITE", "none" if IS_PRODUCTION else "lax").lower() # type: ignore
SESSION_HTTPS_ONLY = os.getenv("SESSION_HTTPS_ONLY", str(IS_PRODUCTION)).lower() == "true"
FRONTEND_URL = os.getenv("FRONTEND_URL") or "http://localhost:3000"

# Add session middleware.
# - Production cross-site OAuth requires SameSite=None + Secure cookies.
# - Local HTTP development works best with SameSite=Lax and non-secure cookies.
app.add_middleware(
    SessionMiddleware, 
    secret_key=SESSION_SECRET,
    same_site=SESSION_SAME_SITE,
    https_only=SESSION_HTTPS_ONLY,
)

OAUTH_PROVIDER = os.getenv("OAUTH_PROVIDER", "fluxer").lower()
oauth = OAuth()
BOT_PROCESS = None

if OAUTH_PROVIDER == "fluxer":
    # Fluxer requires these env vars to be set by the deployer
    FLUXER_CLIENT_ID = os.getenv("FLUXER_CLIENT_ID")
    FLUXER_CLIENT_SECRET = os.getenv("FLUXER_CLIENT_SECRET")
    FLUXER_AUTHORIZE_URL = os.getenv("FLUXER_AUTHORIZE_URL")
    FLUXER_TOKEN_URL = os.getenv("FLUXER_TOKEN_URL")
    FLUXER_API_BASE_URL = os.getenv("FLUXER_API_BASE_URL")
    FLUXER_SCOPE = os.getenv("FLUXER_SCOPE", "identify guilds")
    oauth.register(
        name="fluxer",
        client_id=FLUXER_CLIENT_ID,
        client_secret=FLUXER_CLIENT_SECRET,
        access_token_url=FLUXER_TOKEN_URL,
        authorize_url=FLUXER_AUTHORIZE_URL,
        api_base_url=FLUXER_API_BASE_URL,
        scope=FLUXER_SCOPE,  # Set scope directly, not in client_kwargs
    )

def require_user(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="authentication required")
    return user


class Rule(BaseModel):
    id: str
    guild_id: str
    name: str
    pattern: str
    action: str
    threshold: int = Field(1, ge=1)
    enabled: bool = True


class RuleCreate(BaseModel):
    name: str
    pattern: str
    action: str
    threshold: int = Field(1, ge=1)
    enabled: bool = True


def load_data() -> dict:
    if not DATA_FILE.exists():
        return {"guilds": {}, "rules": []}
    return json.loads(DATA_FILE.read_text())


def save_data(data: dict) -> None:
    DATA_FILE.write_text(json.dumps(data, indent=2))


@app.on_event("startup")
def ensure_data_file():
    if not DATA_FILE.exists():
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        save_data({"guilds": {}, "rules": []})


@app.on_event("startup")
def start_bot_with_backend():
    global BOT_PROCESS

    run_bot = os.getenv("RUN_BOT_WITH_BACKEND", "false").lower() == "true"
    if not run_bot:
        return

    worker_id = os.getenv("GUNICORN_WORKER_ID")
    if worker_id and worker_id != "1":
        print(f"[BOT] Skipping bot startup in worker {worker_id}")
        return

    bot_entry = pathlib.Path(
        os.getenv("BOT_ENTRYPOINT") or str(ROOT / "bot" / "bot.py")
    ).resolve()

    if not bot_entry.exists():
        print(f"[BOT] Bot entrypoint not found: {bot_entry}")
        return

    env = os.environ.copy()
    if not env.get("TOKEN") and env.get("FLUXER_TOKEN"):
        env["TOKEN"] = env["FLUXER_TOKEN"]

    try:
        BOT_PROCESS = subprocess.Popen(
            [sys.executable, str(bot_entry)],
            cwd=str(bot_entry.parent),
            env=env,
        )
        print(f"[BOT] Started bot process pid={BOT_PROCESS.pid}")
    except Exception as e:
        BOT_PROCESS = None
        print(f"[BOT] Failed to start bot: {e}")


@app.on_event("shutdown")
def stop_bot_with_backend():
    global BOT_PROCESS

    if BOT_PROCESS is None:
        return

    if BOT_PROCESS.poll() is None:
        BOT_PROCESS.terminate()
        try:
            BOT_PROCESS.wait(timeout=10)
        except Exception:
            BOT_PROCESS.kill()
    BOT_PROCESS = None


@app.get("/login")
async def login(request: Request):
    redirect_uri = OAUTH_REDIRECT_URI
    client = oauth.create_client(OAUTH_PROVIDER)
    # Generate and store state in session explicitly
    import secrets
    state = secrets.token_urlsafe(32)
    request.session["oauth_state"] = state
    print(f"[LOGIN] Generated state: {state}")
    print(f"[LOGIN] redirect_uri: {redirect_uri}")
    print(f"[LOGIN] Client config: client_id={client.client_id}, scope={FLUXER_SCOPE}")
    return await client.authorize_redirect(request, redirect_uri, state=state, scope=FLUXER_SCOPE)


@app.get("/auth")
async def auth(request: Request):
    client = oauth.create_client(OAUTH_PROVIDER)
    
    # Debug: print incoming state and stored state
    incoming_state = request.query_params.get("state")
    stored_state = request.session.get("oauth_state")
    print(f"[AUTH] Incoming state: {incoming_state}")
    print(f"[AUTH] Stored state: {stored_state}")
    print(f"[AUTH] Session contents: {dict(request.session)}")
    
    try:
        # Attempt token exchange - authlib will validate state
        token = await client.authorize_access_token(request)
    except Exception as e:
        print(f"[AUTH] authorize_access_token failed: {e}")
        # Try manual token exchange if state validation fails
        code = request.query_params.get("code")
        state = request.query_params.get("state")
        
        if not code:
            raise HTTPException(status_code=400, detail="Missing authorization code")
        
        print(f"[AUTH] Attempting manual token exchange with code={code}, state={state}")
        
        # Manually exchange code for token (bypasses state validation issues)
        import httpx
        async with httpx.AsyncClient() as http_client:
            token_response = await http_client.post(
                os.getenv("FLUXER_TOKEN_URL"), #type: ignore
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": OAUTH_REDIRECT_URI,
                    "client_id": os.getenv("FLUXER_CLIENT_ID"),
                    "client_secret": os.getenv("FLUXER_CLIENT_SECRET"),
                }
            )
            if token_response.status_code != 200:
                raise HTTPException(status_code=500, detail=f"Token exchange failed: {token_response.text}")
            token = token_response.json()
            print(f"[AUTH] Manual token exchange succeeded: {token}")
    
    # Fetch user/profile; provider-specific endpoints may differ
    if OAUTH_PROVIDER == "fluxer":
        user_endpoint = os.getenv("FLUXER_USER_ENDPOINT")
        if not user_endpoint:
            raise HTTPException(status_code=500, detail="FLUXER_USER_ENDPOINT not configured")
        resp = await client.get(user_endpoint, token=token)
        profile = resp.json()
        # store profile generically
        request.session["user"] = {"id": profile.get("sub") or profile.get("id"), "username": profile.get("name") or profile.get("preferred_username")}
    else:
        resp = await client.get("/users/@me", token=token)
        profile = resp.json()
        request.session["user"] = {"id": profile.get("id"), "username": profile.get("username"), "discriminator": profile.get("discriminator")}
    
    # Redirect to frontend with the session cookie included
    response = RedirectResponse(url=FRONTEND_URL, status_code=302)
    return response


@app.get("/logout")
def logout(request: Request):
    request.session.pop("user", None)
    return {"detail": "logged out"}


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/api/public/stats")
def public_stats():
    """Return non-sensitive public stats for the landing page."""
    data = load_data()
    guild_count = len(data.get("guilds", {}))
    return {"protected_guilds": guild_count}


@app.get("/api/me")
def get_user(user=Depends(require_user)):
    """Return current logged-in user."""
    return user


@app.get("/api/guilds")
def list_guilds(user=Depends(require_user)):
    """List known guilds with basic metadata."""
    data = load_data()
    guilds = []
    for gid, info in data.get("guilds", {}).items():
        count = sum(1 for r in data.get("rules", []) if r["guild_id"] == gid)
        guilds.append({"id": gid, "name": info.get("name"), "rule_count": count})
    return guilds


@app.get("/api/guilds/{guild_id}/rules", response_model=List[Rule])
def list_rules(guild_id: str, user=Depends(require_user)):
    """Return all rules for a guild."""
    data = load_data()
    return [Rule(**r) for r in data.get("rules", []) if r["guild_id"] == guild_id]


@app.post("/api/guilds/{guild_id}/rules", response_model=Rule, status_code=201)
def create_rule(guild_id: str, payload: RuleCreate, user=Depends(require_user)):
    """Create a new rule for a guild."""
    data = load_data()
    guilds = data.setdefault("guilds", {})
    if guild_id not in guilds:
        guilds[guild_id] = {"name": None}
    rule = Rule(id=str(uuid.uuid4()), guild_id=guild_id, **payload.dict())
    data.setdefault("rules", []).append(rule.dict())
    save_data(data)
    return rule


@app.put("/api/rules/{rule_id}", response_model=Rule)
def update_rule(rule_id: str, payload: RuleCreate, user=Depends(require_user)):
    """Update an existing rule by id."""
    data = load_data()
    rules = data.get("rules", [])
    for i, r in enumerate(rules):
        if r["id"] == rule_id:
            updated = {**r, **payload.dict()}
            rules[i] = updated
            save_data(data)
            return Rule(**updated)
    raise HTTPException(status_code=404, detail="rule not found")


@app.delete("/api/rules/{rule_id}", status_code=204)
def delete_rule(rule_id: str, user=Depends(require_user)):
    """Delete a rule by id."""
    data = load_data()
    rules = data.get("rules", [])
    for i, r in enumerate(rules):
        if r["id"] == rule_id:
            rules.pop(i)
            save_data(data)
            return
    raise HTTPException(status_code=404, detail="rule not found")


if __name__ == "__main__":
    import uvicorn

    # Run the app object directly so the script works whether invoked from
    # the repository root or from inside the `backend/` directory.
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
