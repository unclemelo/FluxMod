import fluxer
import os
import asyncio

from utils.log import log
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = fluxer.Intents.default()
intents.message_content = True

client = fluxer.Bot(intents=intents, command_prefix="!", retry_forever=True)


@client.event
async def on_ready():
    log(f"System online as {client.user} ({client.user.id})", "success")


async def load_cogs():
    loaded = []
    failed = []

    for filename in os.listdir("cogs"):
        if filename.endswith(".py"):
            name = filename[:-3]
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

    try:
        log(f"Starting...", "info")
        await client.start(TOKEN)
    except KeyboardInterrupt:
        log("Manual shutdown requested (Ctrl+C)", "warn")
        await client.close()
    except Exception as e:
        log(f"Failed to start bot: {e}", "critical")


if __name__ == "__main__":
    asyncio.run(main())