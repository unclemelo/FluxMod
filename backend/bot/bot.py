import fluxer
import os
import asyncio
import pathlib
import json
import urllib.request
import urllib.error
from typing import Optional

from utils.log import log
from dotenv import load_dotenv


load_dotenv()
raw_token = os.getenv("TOKEN") or os.getenv("FLUXER_TOKEN")
TOKEN = raw_token.strip() if raw_token else None
API_BASE_URL = (
    os.getenv("API_BASE_URL")
    or os.getenv("BACKEND_URL")
    or ""
).strip().rstrip("/")
BOT_API_TOKEN = (os.getenv("BOT_API_TOKEN") or "").strip()
BOT_ROOT = pathlib.Path(__file__).parent

intents = fluxer.Intents.default()

client = fluxer.Bot(intents=intents, command_prefix="!", retry_forever=True)


def _metrics_url() -> Optional[str]:
    if not API_BASE_URL:
        return None
    return f"{API_BASE_URL}/api/internal/bot/metrics"


async def report_guild_count_to_api() -> None:
    url = _metrics_url()
    if not url:
        log("Skipping guild count report because API URL is empty", "debug")
        return

    guild_count = len(client.guilds)
    payload = json.dumps({"guild_count": guild_count}).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if BOT_API_TOKEN:
        headers["X-Bot-Token"] = BOT_API_TOKEN

    log(
        f"Reporting guild metrics to API url={url} guild_count={guild_count}",
        "debug",
    )

    def send_request() -> int:
        request = urllib.request.Request(
            url,
            data=payload,
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=8) as response:
            response.read()
            return response.status

    try:
        status = await asyncio.to_thread(send_request)
        log(f"Reported guild count={guild_count} to API (status={status})", "info")
    except urllib.error.HTTPError as error:
        log(f"Guild count report rejected by API (HTTP {error.code})", "warn")
    except Exception as error:
        log(f"Failed to report guild count to API: {error}", "warn")


@client.event
async def on_ready():
    log(f"System online as {client.user} ({client.user.id})", "success")
    log(f"Connected to {len(client.guilds)} guilds.", "info")
    if not API_BASE_URL:
        log("API_BASE_URL/BACKEND_URL is not set; skipping guild count reporting.", "warn")
        return
    await report_guild_count_to_api()


@client.event
async def on_guild_join(guild):
    log(f"Joined guild: {getattr(guild, 'name', 'unknown')} ({guild})", "info")
    await report_guild_count_to_api()



@client.event
async def on_guild_remove(guild):
    log(f"Removed from guild: {getattr(guild, 'name', 'unknown')} ({guild})", "warn")
    await report_guild_count_to_api()


async def load_cogs():
    loaded = []
    failed = []

    cogs_dir = BOT_ROOT / "cogs"
    log(f"Loading cogs from {cogs_dir}", "debug")

    for filename in os.listdir(cogs_dir):
        if filename.endswith(".py"):
            name = filename[:-3]
            if name == "automod":  # Skip automod cog for now since it's not fully ready
                continue
            try:
                await client.load_extension(f"cogs.{name}")
                loaded.append(filename)
            except Exception as e:
                failed.append((filename, str(e)))

    if loaded:
        log("Loaded cogs:", "success")
        for file in loaded:
            log(f"   → {file}", "success")
    if failed:
        log("Failed to load cogs:", "error")
        for file, error in failed:
            log(f"   → {file}: {error}", "error")

async def main():
    log(
        f"Bot startup context api_base_url={API_BASE_URL or 'unset'} token_present={bool(TOKEN)}",
        "debug",
    )
    try:
        await load_cogs()
    except Exception as e:
        log(f"Critical error loading cogs: {e}", "critical")

    if not TOKEN:
        log("Missing bot token. Set TOKEN or FLUXER_TOKEN.", "critical")
        return

    try:
        log(f"Starting...", "info")
        await client.start(TOKEN)
    except KeyboardInterrupt:
        log("Manual shutdown requested (Ctrl+C)", "warn")
        await client.close()
    except Exception as e:
        error_text = str(e)
        if "403" in error_text and "Forbidden" in error_text:
            log(
                "Bot token rejected (403 Forbidden). Use a valid bot token (not OAuth client secret/access token) and re-check Render env FLUXER_TOKEN.",
                "critical",
            )
        log(f"Failed to start bot: {e}", "critical")


if __name__ == "__main__":
    asyncio.run(main())