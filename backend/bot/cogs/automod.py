import fluxer
from fluxer import Cog


from utils.automod_manager import AutoModManager
from utils.automod_engine import AutoModEngine
from utils.automod_models import (
    GuildAutoModSettings,
    AutoModRule,
    AutoModAction,
    RuleType,
    ActionType,
    ExemptEntity,
)


class AutoModCog(Cog):
    """AutoMod management commands and event handlers"""

    def __init__(self, bot: fluxer.Bot):
        self.bot = bot
        self.manager = AutoModManager()
        self.engine = AutoModEngine()

    # --- Event Listeners ---

    @Cog.listener()
    async def on_message(self, message):
        """Check messages for AutoMod violations"""
        
        # Don't check bot messages or DMs
        if message.author.bot or not message.guild:
            return

        # Get guild settings
        settings = await self.manager.get_guild_settings(message.guild.id)

        if not settings.enabled:
            return

        # Check against rules
        violated_rule, event = await self.engine.check_message(
            message.content,
            message.author.id,
            message.guild.id,
            settings,
        )

        if violated_rule and event:
            # Log the event
            await self.manager.log_event(event)

            # Take action
            await self._take_action(
                message,
                violated_rule,
                event,
                settings,
            )

    # --- Action Handler ---

    async def _take_action(
        self,
        message: fluxer.Message,
        rule: AutoModRule,
        event,
        settings: GuildAutoModSettings,
    ):
        """Execute the action specified by a rule"""

        action = rule.action

        # Delete message
        if action.type in [ActionType.DELETE, ActionType.WARN]:
            try:
                await message.delete()
            except:
                pass

        # Send log message
        if settings.log_channel_id:
            try:
                log_channel = await self.bot.fetch_channel(settings.log_channel_id)
                message_text = self.engine.format_message(
                    action.type, rule.name, event.reason or "Rule triggered"
                )
                
                embed = fluxer.Embed(
                    title="AutoMod Action Taken",
                    description=message_text,
                    color=fluxer.Color.brand_red(),
                )
                embed.add_field(name="User", value=f"<@{event.user_id}>", inline=True)
                embed.add_field(name="Severity", value="🔴" * rule.severity, inline=True)
                embed.set_footer(text=f"Event ID: {event.id}")
                
                await log_channel.send(embed=embed)
            except:
                pass

        # Send warning to user if configured
        if action.custom_message:
            try:
                await message.author.send(action.custom_message)
            except:
                pass


async def setup(bot: fluxer.Bot):
    """Load the AutoMod cog"""
    await bot.add_cog(AutoModCog(bot))
