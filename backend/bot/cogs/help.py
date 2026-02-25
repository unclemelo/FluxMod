import fluxer
from fluxer import Cog

class HelpCog(Cog):
    def __init__(self, bot: fluxer.Bot):
        super().__init__(bot)

    @Cog.command(name="help")
    async def help(self, ctx: fluxer.Message):
        embed_help = fluxer.Embed(
            title="AutoMod Bot Help",
            description=(
                "Here are the available commands:\n\n"
                "**Moderation Commands:**\n"
                "`!ban <user_id> [reason]` - Ban a user from the server.\n"
                "`!kick <user_id> [reason]` - Kick a user from the server.\n"
                "`!mute <user_id> [reason] [duration_in_seconds]` - Mute a user for a specified duration.\n"
                "`!unmute <user_id>` - Unmute a user.\n\n"
                "**AutoMod Configuration Commands:**\n"
                "`!automod enable` - Enable AutoMod in the server.\n"
                "`!automod disable` - Disable AutoMod in the server.\n"
                "`!automod set [rule] [parameters]` - Configure AutoMod rules (e.g., set word blacklist).\n\n"
                "For more detailed information on each command, please refer to the documentation or contact the bot owner."
            ),
            color=0x00BFFF,
        )

        dev_note = fluxer.Embed(
            title="Developer Note",
            description=(
                "This help command is a basic implementation. For a more comprehensive and user-friendly help system, consider implementing a paginated help menu or using reactions for navigation.\n\nAutomod is currently disabled until further notice due to ongoing development and testing. Please stay tuned for updates!"
            ),
            color=0xFF69B4,
        )
        await ctx.reply(embeds=[embed_help, dev_note])

async def setup(bot: fluxer.Bot):
    await bot.add_cog(HelpCog(bot))