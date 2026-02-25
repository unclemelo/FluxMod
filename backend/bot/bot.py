import fluxer
import os
import asyncio
import pathlib

from utils.log import log
from dotenv import load_dotenv


load_dotenv()
raw_token = os.getenv("TOKEN") or os.getenv("FLUXER_TOKEN")
TOKEN = raw_token.strip() if raw_token else None
BOT_ROOT = pathlib.Path(__file__).parent

intents = fluxer.Intents.default()
intents.message_content = True

client = fluxer.Bot(intents=intents, command_prefix="!", retry_forever=True)


@client.event
async def on_ready():
    log(f"System online as {client.user} ({client.user.id})", "success")


async def load_cogs():
    loaded = []
    failed = []

    cogs_dir = BOT_ROOT / "cogs"

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