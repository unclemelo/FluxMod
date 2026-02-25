import fluxer
from fluxer import Cog
from fluxer.checks import has_permission

class KickCog(Cog):
    def __init__(self, bot: fluxer.Bot):
        super().__init__(bot)

    @Cog.command(name="kick")
    @has_permission(fluxer.Permissions.KICK_MEMBERS)   
    async def kick(self, ctx: fluxer.Message):
        embed_usage = fluxer.Embed(
            title="Kick Command Usage",
            description="Usage: `!kick <user_id> [reason]`\nExample: `!kick 123456789012345678 Spamming`",
            color=0xFFA500,
        )

        split = ctx.content.split()
        if len(split) < 2:
            await ctx.reply(embed=embed_usage)
            return
        
        user_id = split[1]

        # Default reason
        reason = "No reason provided"
        if len(split) >= 3:
            reason = split[2]

        if ctx.guild_id is None:
            await ctx.reply("This command can only be used in a server.")
            return
        guild = await self.bot.fetch_guild(str(ctx.guild_id))

        try:
            await guild.kick(int(user_id), reason=reason)
            embed_kick = fluxer.Embed(
                title="User Kicked",
                description=f"User with ID {user_id} has been kicked.\nReason: {reason}",
                color=0xFFA500,
            )
            await ctx.reply(embed=embed_kick)
        except Exception as e:
            embed_error = fluxer.Embed(
                title="Error Kicking User",
                description=f"Failed to kick user with ID {user_id}.\nPlease check with the bot owner for more details.",
                color=0xFF0000,
            )
            await ctx.reply(embed=embed_error)
            print(f"Error kicking user: {e}")

async def setup(bot: fluxer.Bot):
    await bot.add_cog(KickCog(bot))