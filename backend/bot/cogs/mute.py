import fluxer
from fluxer import Cog
from fluxer.checks import has_permission

class MuteCog(Cog):
    def __init__(self, bot: fluxer.Bot):
        super().__init__(bot)


    @Cog.command(name="mute")
    @has_permission(fluxer.Permissions.MODERATE_MEMBERS)
    async def mute(self, ctx: fluxer.Message, reason: str = "No reason provided", duration: int = 3600):

        embed_usage = fluxer.Embed(
            title="Mute Command Usage",
            description="Usage: `!mute <user_id> [reason] [duration_in_seconds]`\nExample: `!mute 123456789012345678 Spamming 3600` (mutes for 1 hour)",
            color=0xFF4500,
        )

        split = ctx.content.split()
        if len(split) != 4:
            await ctx.reply(embed=embed_usage)
            return
        
        user_id = split[1]

        if ctx.guild_id is None:
            await ctx.reply("This command can only be used in a server.")
            return
        guild = await self.bot.fetch_guild(str(ctx.guild_id))

        try:
            # Convert duration to a human-readable format
            hours, remainder = divmod(duration, 3600)
            minutes, seconds = divmod(remainder, 60)
            readable_duration = f"{hours}h {minutes}m {seconds}s" if hours else f"{minutes}m {seconds}s" if minutes else f"{seconds}s"
            await guild.timeout(int(user_id), duration=duration, reason=reason)  # Timeout for specified duration

            embed_muted = fluxer.Embed(
                title="User Muted",
                description=f"User with ID {user_id} has been muted for {readable_duration}.\nReason: {reason}",
                color=0xFF4500,
            )
            await ctx.reply(embed=embed_muted)
        except Exception as e:

            embed_error = fluxer.Embed(
                title="Error Muting User",
                description=f"Failed to mute user with ID {user_id}.\nPlease check with the bot owner for more details.",
                color=0xFF0000,
            )
            await ctx.reply(embed=embed_error)
            print(f"Error muting user: {e}")

    @Cog.command(name="unmute")
    @has_permission(fluxer.Permissions.MODERATE_MEMBERS)
    async def unmute(self, ctx: fluxer.Message):

        embed_usage = fluxer.Embed(
            title="Unmute Command Usage",
            description="Usage: `!unmute <user_id>`\nExample: `!unmute 123456789012345678`",
            color=0x32CD32,
        )

        split = ctx.content.split()
        if len(split) != 2:
            await ctx.reply(embed=embed_usage)
            return
        
        user_id = split[1]

        if ctx.guild_id is None:
            await ctx.reply("This command can only be used in a server.")
            return
        guild = await self.bot.fetch_guild(str(ctx.guild_id))

        try:
            await guild.timeout(int(user_id), duration=0)  # Remove timeout

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