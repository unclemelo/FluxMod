import fluxer
import asyncio
from typing import Optional
import uuid
from datetime import datetime

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

    @commands.Cog.listener()
    async def on_message(self, message: fluxer.Message):
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

    # --- Commands ---

    @commands.group(name="automod", invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def automod_group(self, ctx: commands.Context):
        """AutoMod configuration and management"""
        embed = fluxer.Embed(
            title="🛡️ AutoMod Commands",
            description="Configure automatic moderation for your server",
            color=fluxer.Color.blurple(),
        )
        embed.add_field(
            name="Setup",
            value="`automod setup` - Interactive setup wizard\n"
            "`automod presets` - Apply preset configurations",
            inline=False,
        )
        embed.add_field(
            name="Rules",
            value="`automod rules` - View all rules\n"
            "`automod addrule` - Add a custom rule\n"
            "`automod removerule` - Remove a rule",
            inline=False,
        )
        embed.add_field(
            name="Exemptions",
            value="`automod exempt` - Manage exemptions\n"
            "`automod unexempt` - Remove exemptions",
            inline=False,
        )
        embed.add_field(
            name="Status",
            value="`automod status` - Check current configuration\n"
            "`automod enable/disable` - Toggle AutoMod",
            inline=False,
        )
        await ctx.send(embed=embed)

    @automod_group.command(name="setup")
    @commands.has_permissions(manage_guild=True)
    async def setup_automod(self, ctx: commands.Context):
        """Interactive AutoMod setup wizard"""
        settings = await self.manager.get_guild_settings(ctx.guild.id)

        embed = fluxer.Embed(
            title="🔧 AutoMod Setup",
            description="Select a security preset for your server",
            color=fluxer.Color.brand_green(),
        )

        presets = await self.manager.get_presets()
        for preset_id, preset in presets.items():
            embed.add_field(
                name=f"**{preset.name}**",
                value=f"{preset.description}\n"
                f"*{len(preset.rules)} rules*",
                inline=True,
            )

        embed.set_footer(text="Reply with preset name: lenient, moderate, or strict")
        msg = await ctx.send(embed=embed)

        try:
            response = await self.bot.wait_for(
                "message",
                timeout=120,
                check=lambda m: m.author.id == ctx.author.id and m.channel.id == ctx.channel.id,
            )

            preset_id = response.content.strip().lower()
            if await self.manager.apply_preset(ctx.guild.id, preset_id):
                embed = fluxer.Embed(
                    title="✅ Preset Applied",
                    description=f"Applied **{preset_id.title()}** preset to your server",
                    color=fluxer.Color.brand_green(),
                )
                await ctx.send(embed=embed)
            else:
                await ctx.send("❌ Invalid preset name. Use: lenient, moderate, or strict")

        except asyncio.TimeoutError:
            await ctx.send("⏱️ Setup timeout. Please try again.")

    @automod_group.command(name="presets")
    async def list_presets(self, ctx: commands.Context):
        """View available presets"""
        presets = await self.manager.get_presets()

        embed = fluxer.Embed(
            title="📋 AutoMod Presets",
            description="Available security presets",
            color=fluxer.Color.blurple(),
        )

        for preset_id, preset in presets.items():
            rules_text = "\n".join([f"• {r.name}" for r in preset.rules[:3]])
            if len(preset.rules) > 3:
                rules_text += f"\n• +{len(preset.rules) - 3} more"

            embed.add_field(
                name=f"**{preset.name}** (`{preset_id}`)",
                value=f"{preset.description}\n\n{rules_text}",
                inline=False,
            )

        await ctx.send(embed=embed)

    @automod_group.command(name="rules")
    async def list_rules(self, ctx: commands.Context):
        """View all active rules"""
        settings = await self.manager.get_guild_settings(ctx.guild.id)

        if not settings.rules:
            await ctx.send("❌ No rules configured. Use `automod setup` to get started.")
            return

        embed = fluxer.Embed(
            title="📋 Active Rules",
            description=f"Total: {len(settings.rules)} rules",
            color=fluxer.Color.blurple(),
        )

        for rule in settings.rules[:10]:  # Show first 10
            status = "✅ Enabled" if rule.enabled else "❌ Disabled"
            severity_bar = "🔴" * rule.severity
            action_type = rule.action.type.value.upper()

            embed.add_field(
                name=f"{rule.name} {severity_bar}",
                value=f"ID: `{rule.id}`\n"
                f"Type: {rule.rule_type.value}\n"
                f"Action: **{action_type}**\n"
                f"{status}",
                inline=False,
            )

        if len(settings.rules) > 10:
            embed.set_footer(text=f"+{len(settings.rules) - 10} more rules")

        await ctx.send(embed=embed)

    @automod_group.command(name="status")
    async def automod_status(self, ctx: commands.Context):
        """Check AutoMod status"""
        settings = await self.manager.get_guild_settings(ctx.guild.id)
        log_channel = f"<#{settings.log_channel_id}>" if settings.log_channel_id else "Not set"

        embed = fluxer.Embed(
            title="🛡️ AutoMod Status",
            color=fluxer.Color.brand_green() if settings.enabled else fluxer.Color.brand_red(),
        )

        embed.add_field(
            name="Status",
            value="✅ Enabled" if settings.enabled else "❌ Disabled",
            inline=True,
        )
        embed.add_field(name="Rules", value=str(len(settings.rules)), inline=True)
        embed.add_field(name="Log Channel", value=log_channel, inline=False)
        embed.add_field(name="Exempt Roles", value=str(len(settings.exempt_roles)), inline=True)
        embed.add_field(name="Exempt Users", value=str(len(settings.exempt_users)), inline=True)
        embed.add_field(name="Exempt Channels", value=str(len(settings.exempt_channels)), inline=True)

        await ctx.send(embed=embed)

    @automod_group.command(name="enable")
    @commands.has_permissions(manage_guild=True)
    async def enable_automod(self, ctx: commands.Context):
        """Enable AutoMod for this server"""
        await self.manager.set_enabled(ctx.guild.id, True)
        embed = fluxer.Embed(
            title="✅ AutoMod Enabled",
            color=fluxer.Color.brand_green(),
        )
        await ctx.send(embed=embed)

    @automod_group.command(name="disable")
    @commands.has_permissions(manage_guild=True)
    async def disable_automod(self, ctx: commands.Context):
        """Disable AutoMod for this server"""
        await self.manager.set_enabled(ctx.guild.id, False)
        embed = fluxer.Embed(
            title="❌ AutoMod Disabled",
            color=fluxer.Color.brand_red(),
        )
        await ctx.send(embed=embed)

    @automod_group.command(name="setlogchannel")
    @commands.has_permissions(manage_guild=True)
    async def set_log_channel(self, ctx: commands.Context, channel: fluxer.TextChannel):
        """Set the channel for AutoMod logs"""
        await self.manager.set_log_channel(ctx.guild.id, channel.id)
        embed = fluxer.Embed(
            title="✅ Log Channel Set",
            description=f"AutoMod alerts will be sent to {channel.mention}",
            color=fluxer.Color.brand_green(),
        )
        await ctx.send(embed=embed)

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
