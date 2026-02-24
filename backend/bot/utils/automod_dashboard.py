"""
AutoMod Dashboard API Helper
Provides REST-like interface for dashboard integration
Can be used by web services to manage AutoMod without Fluxer bot
"""

from typing import Dict, List, Optional, Any
import uuid
from datetime import datetime, timedelta
from .automod_manager import AutoModManager
from .automod_models import (
    GuildAutoModSettings,
    AutoModRule,
    AutoModAction,
    ActionType,
    RuleType,
    ExemptEntity,
    AutoModEvent,
)


class AutoModDashboardAPI:
    """
    Dashboard-friendly API for AutoMod management.
    Designed to be called from web services or FastAPI.
    """

    def __init__(self):
        self.manager = AutoModManager()

    # --- Guild Settings ---

    async def get_guild_config(self, guild_id: int) -> Dict[str, Any]:
        """Get complete guild configuration as JSON"""
        settings = await self.manager.get_guild_settings(guild_id)
        return settings.to_dict()

    async def update_guild_config(self, guild_id: int, config: Dict[str, Any]) -> Dict[str, Any]:
        """Update guild configuration from JSON"""
        settings = GuildAutoModSettings.from_dict({**config, "guild_id": guild_id})
        await self.manager.save_guild_settings(settings)
        return settings.to_dict()

    async def reset_guild_config(self, guild_id: int) -> bool:
        """Reset guild to default configuration"""
        return await self.manager.delete_guild_settings(guild_id)

    # --- Rule Management ---

    async def create_rule(self, guild_id: int, rule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new rule"""
        rule_data["id"] = str(uuid.uuid4())
        rule = AutoModRule.from_dict(rule_data)
        await self.manager.add_rule(guild_id, rule)
        return rule.to_dict()

    async def update_rule(self, guild_id: int, rule_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing rule"""
        rule = await self.manager.get_rule(guild_id, rule_id)
        if not rule:
            return None

        # Apply updates
        rule_dict = rule.to_dict()
        rule_dict.update(updates)
        rule = AutoModRule.from_dict(rule_dict)

        await self.manager.update_rule(guild_id, rule)
        return rule.to_dict()

    async def delete_rule(self, guild_id: int, rule_id: str) -> bool:
        """Delete a rule"""
        return await self.manager.remove_rule(guild_id, rule_id)

    async def get_rule(self, guild_id: int, rule_id: str) -> Optional[Dict[str, Any]]:
        """Get a single rule"""
        rule = await self.manager.get_rule(guild_id, rule_id)
        return rule.to_dict() if rule else None

    async def list_rules(self, guild_id: int, enabled_only: bool = False) -> List[Dict[str, Any]]:
        """List all rules for a guild"""
        rules = await self.manager.get_rules(guild_id, enabled_only=enabled_only)
        return [r.to_dict() for r in rules]

    async def toggle_rule(self, guild_id: int, rule_id: str) -> Optional[Dict[str, Any]]:
        """Toggle a rule on/off"""
        rule = await self.manager.get_rule(guild_id, rule_id)
        if not rule:
            return None

        rule.enabled = not rule.enabled
        await self.manager.update_rule(guild_id, rule)
        return rule.to_dict()

    # --- Presets ---

    async def list_presets(self) -> List[Dict[str, Any]]:
        """List all available presets"""
        presets = await self.manager.get_presets()
        return [p.to_dict() for p in presets.values()]

    async def get_preset(self, preset_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific preset"""
        preset = await self.manager.get_preset(preset_id)
        return preset.to_dict() if preset else None

    async def apply_preset(self, guild_id: int, preset_id: str) -> bool:
        """Apply a preset to a guild"""
        return await self.manager.apply_preset(guild_id, preset_id)

    # --- Exemptions ---

    async def add_exemption(
        self, guild_id: int, entity_id: int, entity_type: str, name: str = ""
    ) -> Dict[str, Any]:
        """Add an exemption"""
        await self.manager.add_exempt_entity(guild_id, entity_id, entity_type, name)
        entity = ExemptEntity(id=entity_id, type=entity_type, name=name)
        return entity.to_dict()

    async def remove_exemption(self, guild_id: int, entity_id: int, entity_type: str) -> bool:
        """Remove an exemption"""
        return await self.manager.remove_exempt_entity(guild_id, entity_id, entity_type)

    async def list_exemptions(self, guild_id: int, entity_type: str) -> List[Dict[str, Any]]:
        """List exemptions by type (role, user, channel)"""
        entities = await self.manager.get_exempt_entities(guild_id, entity_type)
        return [e.to_dict() for e in entities]

    async def is_exempt(self, guild_id: int, entity_id: int, entity_type: str) -> bool:
        """Check if entity is exempt"""
        return await self.manager.is_exempt(guild_id, entity_id, entity_type)

    # --- Settings ---

    async def set_log_channel(self, guild_id: int, channel_id: int) -> bool:
        """Set log channel"""
        await self.manager.set_log_channel(guild_id, channel_id)
        return True

    async def get_log_channel(self, guild_id: int) -> Optional[int]:
        """Get log channel"""
        return await self.manager.get_log_channel(guild_id)

    async def set_enabled(self, guild_id: int, enabled: bool) -> bool:
        """Enable/disable AutoMod"""
        await self.manager.set_enabled(guild_id, enabled)
        return True

    # --- Analytics & History ---

    async def get_guild_stats(self, guild_id: int, days: int = 7) -> Dict[str, Any]:
        """Get statistics for a guild"""
        events = await self.manager.get_events(guild_id, limit=10000)

        # Filter by date range
        cutoff_time = datetime.now().timestamp() - (days * 86400)
        recent_events = [e for e in events if e.timestamp >= cutoff_time]

        # Calculate stats
        stats = {
            "total_violations": len(recent_events),
            "violations_by_rule": {},
            "violations_by_user": {},
            "violations_by_action": {},
            "top_rules": [],
            "top_users": [],
        }

        for event in recent_events:
            # By rule
            stats["violations_by_rule"][event.rule_name] = (
                stats["violations_by_rule"].get(event.rule_name, 0) + 1
            )

            # By user
            stats["violations_by_user"][event.user_id] = (
                stats["violations_by_user"].get(event.user_id, 0) + 1
            )

            # By action
            stats["violations_by_action"][event.action_taken] = (
                stats["violations_by_action"].get(event.action_taken, 0) + 1
            )

        # Get top violators
        stats["top_rules"] = sorted(
            stats["violations_by_rule"].items(), key=lambda x: x[1], reverse=True
        )[:5]
        stats["top_users"] = sorted(
            stats["violations_by_user"].items(), key=lambda x: x[1], reverse=True
        )[:5]

        return stats

    async def get_events(
        self, guild_id: Optional[int] = None, limit: int = 100, rule_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get events"""
        if rule_id and guild_id:
            events = await self.manager.get_events_for_rule(guild_id, rule_id, limit)
        else:
            events = await self.manager.get_events(guild_id, limit)

        return [e.to_dict() for e in events]

    async def get_user_history(self, guild_id: int, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get violation history for a user"""
        events = await self.manager.get_events(guild_id, limit=limit * 5)
        user_events = [e for e in events if e.user_id == user_id][-limit:]
        return [e.to_dict() for e in user_events]

    # --- Bulk Operations ---

    async def export_guild_config(self, guild_id: int) -> Dict[str, Any]:
        """Export complete guild configuration"""
        settings = await self.manager.get_guild_settings(guild_id)
        events = await self.manager.get_events(guild_id, limit=1000)

        return {
            "settings": settings.to_dict(),
            "recent_events": [e.to_dict() for e in events],
            "export_timestamp": int(datetime.now().timestamp()),
        }

    async def import_guild_config(self, guild_id: int, config_data: Dict[str, Any]) -> bool:
        """Import guild configuration"""
        settings_data = config_data.get("settings", {})
        settings_data["guild_id"] = guild_id
        settings = GuildAutoModSettings.from_dict(settings_data)
        await self.manager.save_guild_settings(settings)
        return True

    # --- Validation ---

    async def validate_rule(self, rule_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate rule configuration"""
        try:
            AutoModRule.from_dict(rule_data)
            return True, None
        except Exception as e:
            return False, str(e)

    async def validate_config(self, config_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate complete configuration"""
        try:
            GuildAutoModSettings.from_dict(config_data)
            return True, None
        except Exception as e:
            return False, str(e)
