import fluxer
from fluxer import Cog
from fluxer.checks import has_permission
from datetime import datetime, timedelta, timezone

class MuteCog(Cog):
    def __init__(self, bot: fluxer.Bot):
        super().__init__(bot)


    @Cog.command(name="mute")
    @has_permission(fluxer.Permissions.MODERATE_MEMBERS)
    async def mute(
        self,
        ctx: fluxer.Message,
        user_id: int,
        duration: int = 3600,
        *,
        reason: str = "No reason provided"
    ):
        if ctx.guild_id is None:
            await ctx.reply("This command can only be used in a server.")
            return

        guild = await self.bot.fetch_guild(str(ctx.guild_id))
        member = await guild.fetch_member(int(user_id))

        hours, remainder = divmod(duration, 3600)
        minutes, seconds = divmod(remainder, 60)

        member = await guild.fetch_member(user_id)

        # Create ISO 8601 timestamp
        until_time = datetime.now(timezone.utc) + timedelta(seconds=duration)
        until_iso = until_time.isoformat()

        parts = []
        if hours:
            parts.append(f"{hours}h")
        if minutes:
            parts.append(f"{minutes}m")
        if seconds or not parts:
            parts.append(f"{seconds}s")

        try:
            await member.timeout(until=until_iso, reason=reason, guild_id=int(ctx.guild_id))

            embed = fluxer.Embed(
                title="User Muted",
                description=f"User with ID {user_id} has been muted for {' '.join(parts)}.\nReason: {reason}",
                color=0xFF4500,
            )
            await ctx.reply(embed=embed)

        except Exception as e:
            await ctx.reply("Failed to mute user.")
            print(f"Error muting user: {e}")

    @Cog.command(name="unmute")
    @has_permission(fluxer.Permissions.MODERATE_MEMBERS)
    async def unmute(
        self, 
        ctx: fluxer.Message,
        user_id: int,
        *,
        reason: str = "No reason provided"
    ):
        duration =0

        if ctx.guild_id is None:
            await ctx.reply("This command can only be used in a server.")
            return

        guild = await self.bot.fetch_guild(str(ctx.guild_id))
        member = await guild.fetch_member(int(user_id))

        member = await guild.fetch_member(user_id)

        # Create ISO 8601 timestamp
        until_time = datetime.now(timezone.utc) + timedelta(seconds=duration)
        until_iso = until_time.isoformat()

        try:
            await member.timeout(until=until_iso, reason=reason, guild_id=int(ctx.guild_id))

            embed_unmuted = fluxer.Embed(
                title="User Unmuted",
                description=f"User with ID {user_id} has been unmuted.",
                color=0x32CD32,
            )
            await ctx.reply(embed=embed_unmuted)
        except Exception as e:
            embed_error = fluxer.Embed(
                title="Error Unmuting User",
                description=f"Failed to unmute user with ID {user_id}.\nPlease check with the bot owner for more details.",
                color=0xFF0000,
            )
            await ctx.reply(embed=embed_error)
            print(f"Error unmuting user: {e}")

async def setup(bot: fluxer.Bot):
    await bot.add_cog(MuteCog(bot))