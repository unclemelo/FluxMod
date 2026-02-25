import fluxer
from fluxer import Cog
from fluxer.checks import has_permission

class BanCog(Cog):
    def __init__(self, bot: fluxer.Bot):
        super().__init__(bot)

    @Cog.command(name="ban")
    @has_permission(fluxer.Permissions.BAN_MEMBERS)
    async def ban(self, ctx: fluxer.Message, reason: str = "No reason provided"):

        embed_usage = fluxer.Embed(
            title="Ban Command Usage",
            description="Usage: `!ban <user_id> [reason]`\nExample: `!ban 123456789012345678 Spamming`",
            color=0xFF0000,
        )

        split = ctx.content.split()
        if len(split) != 3:
            await ctx.reply(embed=embed_usage)
            return
        
        user_id = split[1]

        if ctx.guild_id is None:
            await ctx.reply("This command can only be used in a server.")
            return
        guild = await self.bot.fetch_guild(str(ctx.guild_id))

        try:
            embed_ban = fluxer.Embed(
                title="User Banned",
                description=f"User with ID {user_id} has been banned.\nReason: {reason}",
                color=0xFF0000,
            )
            await guild.ban(int(user_id), reason=reason)
            await ctx.reply(embed=embed_ban)
        except Exception as e:
            embed_error = fluxer.Embed(
                title="Error Banning User",
                description=f"Failed to ban user with ID {user_id}.\nPlease check with the bot owner for more details.",
                color=0xFF0000,
            )
            await ctx.reply(embed=embed_error)
            print(f"Error banning user: {e}")
            
async def setup(bot: fluxer.Bot):
    await bot.add_cog(BanCog(bot))