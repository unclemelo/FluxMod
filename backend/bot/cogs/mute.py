import asyncio

import fluxer
from fluxer import Cog
from fluxer.checks import has_permission
from typing import Any

MUTE_ROLE_ID = 1476584004083720339 # FluxMod Muted Role Only Supported in the current implementation. Ensure this role exists in your server and has the appropriate permissions to restrict sending messages, adding reactions, etc. Adjust the role ID as needed for your server's configuration.

class MuteCog(Cog):
    def __init__(self, bot: fluxer.Bot):
        super().__init__(bot)

    def _resolve_user_id(self, member: Any) -> int | None:
        if isinstance(member, fluxer.GuildMember):
            return member.user.id

        if isinstance(member, int):
            return member

        if isinstance(member, str):
            value = member.strip()

            if value.startswith("<@") and value.endswith(">"):
                value = value[2:-1].replace("!", "")

            if value.isdigit():
                return int(value)

        return None

    # FIXME: Replace with a temp role-based mute system for better reliability and to support older Fluxer API versions. The current timeout-based implementation may not work correctly in all cases, especially if the bot restarts while a user is muted. A role-based system would allow for persistent mutes that survive bot restarts and provide more control over mute durations and permissions.


    @Cog.command(name="mute")
    @has_permission(fluxer.Permissions.MODERATE_MEMBERS)
    async def mute(
        self,
        ctx: fluxer.Message,
        member: Any,
        duration: int = 3600,
        *,
        reason: str = "No reason provided"
    ):
        if ctx.guild_id is None:
            await ctx.reply("This command can only be used in a server.")
            return

        user_id = self._resolve_user_id(member)
        if user_id is None:
            await ctx.reply("Invalid user. Use a mention or user ID.")
            return

        guild = await self.bot.fetch_guild(str(ctx.guild_id))
        member_in_guild = await guild.fetch_member(user_id=user_id)

        hours, remainder = divmod(duration, 3600)
        minutes, seconds = divmod(remainder, 60)

        parts = []
        if hours:
            parts.append(f"{hours}h")
        if minutes:
            parts.append(f"{minutes}m")
        if seconds or not parts:
            parts.append(f"{seconds}s")

        try:
            await member_in_guild.add_role(role_id=MUTE_ROLE_ID, guild_id=int(ctx.guild_id), reason=reason)

            embed = fluxer.Embed(
                title="User Muted",
                description=f"User with ID {user_id} has been muted for {' '.join(parts)}.\nReason: {reason}",
                color=0xFF4500,
            )
            await ctx.reply(embed=embed)

             # Schedule unmute after duration
            async def unmute_after_delay():
                await asyncio.sleep(duration)
                try:
                    await member_in_guild.remove_role(role_id=MUTE_ROLE_ID, guild_id=int(ctx.guild_id), reason="Mute duration expired")
                except Exception as e:
                    print(f"Error auto-unmuting user: {e}")

            # Start the unmute task
            asyncio.create_task(unmute_after_delay())

        except Exception as e:
            await ctx.reply("Failed to mute user.")
            print(f"Error muting user: {e}")

    @Cog.command(name="unmute")
    @has_permission(fluxer.Permissions.MODERATE_MEMBERS)
    async def unmute(
        self,
        ctx: fluxer.Message,
        member: Any,
        *,
        reason: str = "No reason provided"
    ):

        if ctx.guild_id is None:
            await ctx.reply("This command can only be used in a server.")
            return

        user_id = self._resolve_user_id(member)
        if user_id is None:
            await ctx.reply("Invalid user. Use a mention or user ID.")
            return

        guild = await self.bot.fetch_guild(str(ctx.guild_id))
        member_in_guild = await guild.fetch_member(user_id=user_id)

        try:
            await member_in_guild.remove_role(role_id=MUTE_ROLE_ID, guild_id=int(ctx.guild_id), reason=reason)

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