"""AutoMod Discord Bot entrypoint."""
import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# TODO: Import and initialize your Discord bot here
# Example:
# import discord
# from discord.ext import commands
# bot = commands.Bot(command_prefix='!')

if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise ValueError("DISCORD_TOKEN env var not set")
    # bot.run(token)
