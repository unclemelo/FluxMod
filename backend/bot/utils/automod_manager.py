"""
AutoMod Manager - Handles storage and retrieval of AutoMod settings
Abstracted to support database migration and dashboard integration
"""

import json
import os
import asyncio
from pathlib import Path
from typing import Dict, Optional, List
from .automod_models import GuildAutoModSettings, AutoModPreset, AutoModEvent, AutoModRule, ActionType, RuleType, ExemptEntity, AutoModAction


class AutoModManager:
    """
    Manager for AutoMod settings storage and retrieval.
    Designed for easy migration to database backends.
    """

    def __init__(self, data_dir: str = "data/automod"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.guild_settings_dir = self.data_dir / "guilds"
        self.guild_settings_dir.mkdir(exist_ok=True)
        self.presets_file = self.data_dir / "presets.json"
        self.events_file = self.data_dir / "events.json"
        self._lock = asyncio.Lock()

        # Initialize presets if they don't exist
        if not self.presets_file.exists():
            asyncio.create_task(self._init_default_presets())

    async def _init_default_presets(self) -> None:
        """Initialize default presets"""
        default_presets = {
            "lenient": AutoModPreset(
                id="lenient",
                name="Lenient",
                description="Basic spam and obvious profanity detection",
                rules=[
                    AutoModRule(
                        id="lenient_spam",
                        name="Spam Detection",
                        rule_type=RuleType.SPAM,
                        patterns=["repeat_threshold:10"],
                        action=AutoModAction(ActionType.DELETE),
                        severity=1,
                    )
                ]
            ),
            "moderate": AutoModPreset(
                id="moderate",
                name="Moderate",
                description="Balanced protection with common rules",
                rules=[
                    AutoModRule(
                        id="moderate_spam",
                        name="Spam Detection",
                        rule_type=RuleType.SPAM,
                        patterns=["repeat_threshold:5"],
                        action=AutoModAction(ActionType.DELETE),
                        severity=2,
                    ),
                    AutoModRule(
                        id="moderate_caps",
                        name="Excessive Caps",
                        rule_type=RuleType.CAPS,
                        patterns=["percentage:70"],
                        action=AutoModAction(ActionType.DELETE),
                        severity=2,
                    ),
                ]
            ),
            "strict": AutoModPreset(
                id="strict",
                name="Strict",
                description="Heavy moderation with warnings and mutes",
                rules=[
                    AutoModRule(
                        id="strict_spam",
                        name="Spam Detection",
                        rule_type=RuleType.SPAM,
                        patterns=["repeat_threshold:3"],
                        action=AutoModAction(ActionType.WARN),
                        severity=4,
                    ),
                    AutoModRule(
                        id="strict_caps",
                        name="Excessive Caps",
                        rule_type=RuleType.CAPS,
                        patterns=["percentage:50"],
                        action=AutoModAction(ActionType.WARN),
                        severity=3,
                    ),
                    AutoModRule(
                        id="strict_mentions",
                        name="Mention Spam",
                        rule_type=RuleType.MENTIONS,
                        patterns=["count:5"],
                        action=AutoModAction(ActionType.MUTE, duration_seconds=3600),
                        severity=4,
                    ),
                ]
            ),
        }
        await self.save_presets(default_presets)

    # --- Guild Settings Operations ---

    async def get_guild_settings(self, guild_id: int) -> GuildAutoModSettings:
        """Get settings for a guild, create default if not exists"""
        async with self._lock:
            settings_file = self.guild_settings_dir / f"{guild_id}.json"
            if settings_file.exists():
                with open(settings_file, "r") as f:
                    data = json.load(f)
                    return GuildAutoModSettings.from_dict(data)
            # Return default settings for new guild
            return GuildAutoModSettings(guild_id=guild_id)

    async def save_guild_settings(self, settings: GuildAutoModSettings) -> None:
        """Save guild settings"""
        async with self._lock:
            settings_file = self.guild_settings_dir / f"{settings.guild_id}.json"
            with open(settings_file, "w") as f:
                json.dump(settings.to_dict(), f, indent=2)

    async def delete_guild_settings(self, guild_id: int) -> bool:
        """Delete all settings for a guild"""
        async with self._lock:
            settings_file = self.guild_settings_dir / f"{guild_id}.json"
            if settings_file.exists():
                settings_file.unlink()
                return True
            return False

    async def list_guild_settings(self) -> List[int]:
        """List all configured guild IDs"""
        guild_ids = []
        for file in self.guild_settings_dir.glob("*.json"):
            try:
                guild_id = int(file.stem)
                guild_ids.append(guild_id)
            except ValueError:
                pass
        return guild_ids

    # --- Rule Operations ---

    async def add_rule(self, guild_id: int, rule: AutoModRule) -> None:
        """Add a rule to a guild"""
        settings = await self.get_guild_settings(guild_id)
        settings.add_rule(rule)
        await self.save_guild_settings(settings)

    async def remove_rule(self, guild_id: int, rule_id: str) -> bool:
        """Remove a rule from a guild"""
        settings = await self.get_guild_settings(guild_id)
        removed = settings.remove_rule(rule_id)
        if removed:
            await self.save_guild_settings(settings)
        return removed

    async def update_rule(self, guild_id: int, rule: AutoModRule) -> None:
        """Update an existing rule"""
        settings = await self.get_guild_settings(guild_id)
        settings.add_rule(rule)
        await self.save_guild_settings(settings)

    async def get_rule(self, guild_id: int, rule_id: str) -> Optional[AutoModRule]:
        """Get a specific rule"""
        settings = await self.get_guild_settings(guild_id)
        return settings.get_rule(rule_id)

    async def get_rules(self, guild_id: int, enabled_only: bool = True) -> List[AutoModRule]:
        """Get all rules for a guild"""
        settings = await self.get_guild_settings(guild_id)
        if enabled_only:
            return [r for r in settings.rules if r.enabled]
        return settings.rules

    # --- Exemption Operations ---

    async def add_exempt_entity(self, guild_id: int, entity_id: int, entity_type: str, name: str = "") -> None:
        """Add an exempt entity (role, user, or channel)"""
        settings = await self.get_guild_settings(guild_id)
        entity = ExemptEntity(id=entity_id, type=entity_type, name=name)
        
        if entity_type == "role":
            if not any(e.id == entity_id for e in settings.exempt_roles):
                settings.exempt_roles.append(entity)
        elif entity_type == "user":
            if not any(e.id == entity_id for e in settings.exempt_users):
                settings.exempt_users.append(entity)
        elif entity_type == "channel":
            if not any(e.id == entity_id for e in settings.exempt_channels):
                settings.exempt_channels.append(entity)
        
        await self.save_guild_settings(settings)

    async def remove_exempt_entity(self, guild_id: int, entity_id: int, entity_type: str) -> bool:
        """Remove an exempt entity"""
        settings = await self.get_guild_settings(guild_id)
        
        if entity_type == "role":
            original_len = len(settings.exempt_roles)
            settings.exempt_roles = [e for e in settings.exempt_roles if e.id != entity_id]
            removed = len(settings.exempt_roles) < original_len
        elif entity_type == "user":
            original_len = len(settings.exempt_users)
            settings.exempt_users = [e for e in settings.exempt_users if e.id != entity_id]
            removed = len(settings.exempt_users) < original_len
        elif entity_type == "channel":
            original_len = len(settings.exempt_channels)
            settings.exempt_channels = [e for e in settings.exempt_channels if e.id != entity_id]
            removed = len(settings.exempt_channels) < original_len
        else:
            removed = False
        
        if removed:
            await self.save_guild_settings(settings)
        return removed

    async def get_exempt_entities(self, guild_id: int, entity_type: str) -> List[ExemptEntity]:
        """Get all exempt entities of a type"""
        settings = await self.get_guild_settings(guild_id)
        if entity_type == "role":
            return settings.exempt_roles
        elif entity_type == "user":
            return settings.exempt_users
        elif entity_type == "channel":
            return settings.exempt_channels
        return []

    async def is_exempt(self, guild_id: int, entity_id: int, entity_type: str) -> bool:
        """Check if an entity is exempt"""
        settings = await self.get_guild_settings(guild_id)
        return settings.is_exempt(entity_id, entity_type)

    # --- Preset Operations ---

    async def get_presets(self) -> Dict[str, AutoModPreset]:
        """Get all available presets"""
        async with self._lock:
            if not self.presets_file.exists():
                return {}
            with open(self.presets_file, "r") as f:
                data = json.load(f)
                return {
                    preset_id: AutoModPreset.from_dict(preset_data)
                    for preset_id, preset_data in data.items()
                }

    async def get_preset(self, preset_id: str) -> Optional[AutoModPreset]:
        """Get a specific preset"""
        presets = await self.get_presets()
        return presets.get(preset_id)

    async def save_presets(self, presets: Dict[str, AutoModPreset]) -> None:
        """Save presets"""
        async with self._lock:
            data = {
                preset_id: preset.to_dict()
                for preset_id, preset in presets.items()
            }
            with open(self.presets_file, "w") as f:
                json.dump(data, f, indent=2)

    async def apply_preset(self, guild_id: int, preset_id: str) -> bool:
        """Apply a preset to a guild"""
        preset = await self.get_preset(preset_id)
        if not preset:
            return False
        
        settings = await self.get_guild_settings(guild_id)
        settings.rules = [
            AutoModRule(
                id=f"{preset_id}_{rule.id}",
                name=rule.name,
                rule_type=rule.rule_type,
                patterns=rule.patterns,
                allowed_patterns=rule.allowed_patterns,
                action=rule.action,
                severity=rule.severity,
            )
            for rule in preset.rules
        ]
        await self.save_guild_settings(settings)
        return True

    # --- Settings Operations ---

    async def set_log_channel(self, guild_id: int, channel_id: int) -> None:
        """Set the log channel for a guild"""
        settings = await self.get_guild_settings(guild_id)
        settings.log_channel_id = channel_id
        await self.save_guild_settings(settings)

    async def get_log_channel(self, guild_id: int) -> Optional[int]:
        """Get the log channel ID for a guild"""
        settings = await self.get_guild_settings(guild_id)
        return settings.log_channel_id

    async def set_enabled(self, guild_id: int, enabled: bool) -> None:
        """Enable or disable AutoMod for a guild"""
        settings = await self.get_guild_settings(guild_id)
        settings.enabled = enabled
        await self.save_guild_settings(settings)

    # --- Event Logging (for analytics/dashboard) ---

    async def log_event(self, event: AutoModEvent) -> None:
        """Log an AutoMod event"""
        async with self._lock:
            events = []
            if self.events_file.exists():
                with open(self.events_file, "r") as f:
                    events = json.load(f)
            
            events.append(event.to_dict())
            
            # Keep only last 10000 events per guild to prevent file bloat
            max_events = 50000
            if len(events) > max_events:
                events = events[-max_events:]
            
            with open(self.events_file, "w") as f:
                json.dump(events, f)

    async def get_events(self, guild_id: Optional[int] = None, limit: int = 100) -> List[AutoModEvent]:
        """Get logged events, optionally filtered by guild"""
        async with self._lock:
            if not self.events_file.exists():
                return []
            
            with open(self.events_file, "r") as f:
                events_data = json.load(f)
            
            events = [AutoModEvent.from_dict(e) for e in events_data]
            
            if guild_id:
                events = [e for e in events if e.guild_id == guild_id]
            
            return events[-limit:]

    async def get_events_for_rule(self, guild_id: int, rule_id: str, limit: int = 100) -> List[AutoModEvent]:
        """Get events for a specific rule"""
        events = await self.get_events(guild_id, limit=limit * 5)
        return [e for e in events if e.rule_id == rule_id][-limit:]
