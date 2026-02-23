"""
AutoMod Data Models
Designed for scalability to database and dashboard integration
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from enum import Enum
import json


class ActionType(Enum):
    """Types of actions AutoMod can take"""
    DELETE = "delete"
    WARN = "warn"
    MUTE = "mute"
    KICK = "kick"
    BAN = "ban"


class RuleType(Enum):
    """Types of AutoMod rules"""
    REGEX = "regex"
    KEYWORD = "keyword"
    SPAM = "spam"
    CAPS = "caps"
    MENTIONS = "mentions"


@dataclass
class AutoModAction:
    """Represents an action to take when a rule is violated"""
    type: ActionType
    duration_seconds: Optional[int] = None  # For mute/ban duration
    custom_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "duration_seconds": self.duration_seconds,
            "custom_message": self.custom_message,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AutoModAction":
        return cls(
            type=ActionType(data["type"]),
            duration_seconds=data.get("duration_seconds"),
            custom_message=data.get("custom_message"),
        )


@dataclass
class AutoModRule:
    """Represents a single AutoMod rule"""
    id: str
    name: str
    rule_type: RuleType
    enabled: bool = True
    patterns: List[str] = field(default_factory=list)  # Regex patterns or keywords
    allowed_patterns: List[str] = field(default_factory=list)  # Whitelist patterns
    action: AutoModAction = field(default_factory=lambda: AutoModAction(ActionType.DELETE))
    severity: int = 1  # 1-5 for dashboard filtering

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "rule_type": self.rule_type.value,
            "enabled": self.enabled,
            "patterns": self.patterns,
            "allowed_patterns": self.allowed_patterns,
            "action": self.action.to_dict(),
            "severity": self.severity,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AutoModRule":
        return cls(
            id=data["id"],
            name=data["name"],
            rule_type=RuleType(data["rule_type"]),
            enabled=data.get("enabled", True),
            patterns=data.get("patterns", []),
            allowed_patterns=data.get("allowed_patterns", []),
            action=AutoModAction.from_dict(data.get("action", {})),
            severity=data.get("severity", 1),
        )


@dataclass
class ExemptEntity:
    """Represents an exempt role, user, or channel"""
    id: int
    type: str  # "role", "user", "channel"
    name: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "type": self.type, "name": self.name}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExemptEntity":
        return cls(
            id=data["id"],
            type=data["type"],
            name=data.get("name", ""),
        )


@dataclass
class GuildAutoModSettings:
    """Guild-specific AutoMod configuration"""
    guild_id: int
    enabled: bool = True
    rules: List[AutoModRule] = field(default_factory=list)
    exempt_roles: List[ExemptEntity] = field(default_factory=list)
    exempt_users: List[ExemptEntity] = field(default_factory=list)
    exempt_channels: List[ExemptEntity] = field(default_factory=list)
    log_channel_id: Optional[int] = None
    prefix: str = "[AutoMod]"

    def get_rule(self, rule_id: str) -> Optional[AutoModRule]:
        """Get a rule by ID"""
        return next((r for r in self.rules if r.id == rule_id), None)

    def add_rule(self, rule: AutoModRule) -> None:
        """Add or update a rule"""
        existing = self.get_rule(rule.id)
        if existing:
            self.rules.remove(existing)
        self.rules.append(rule)

    def remove_rule(self, rule_id: str) -> bool:
        """Remove a rule by ID"""
        rule = self.get_rule(rule_id)
        if rule:
            self.rules.remove(rule)
            return True
        return False

    def is_exempt(self, entity_id: int, entity_type: str) -> bool:
        """Check if an entity (role, user, channel) is exempt"""
        if entity_type == "role":
            return any(e.id == entity_id for e in self.exempt_roles)
        elif entity_type == "user":
            return any(e.id == entity_id for e in self.exempt_users)
        elif entity_type == "channel":
            return any(e.id == entity_id for e in self.exempt_channels)
        return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "guild_id": self.guild_id,
            "enabled": self.enabled,
            "rules": [r.to_dict() for r in self.rules],
            "exempt_roles": [e.to_dict() for e in self.exempt_roles],
            "exempt_users": [e.to_dict() for e in self.exempt_users],
            "exempt_channels": [e.to_dict() for e in self.exempt_channels],
            "log_channel_id": self.log_channel_id,
            "prefix": self.prefix,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GuildAutoModSettings":
        return cls(
            guild_id=data["guild_id"],
            enabled=data.get("enabled", True),
            rules=[AutoModRule.from_dict(r) for r in data.get("rules", [])],
            exempt_roles=[ExemptEntity.from_dict(e) for e in data.get("exempt_roles", [])],
            exempt_users=[ExemptEntity.from_dict(e) for e in data.get("exempt_users", [])],
            exempt_channels=[ExemptEntity.from_dict(e) for e in data.get("exempt_channels", [])],
            log_channel_id=data.get("log_channel_id"),
            prefix=data.get("prefix", "[AutoMod]"),
        )


@dataclass
class AutoModPreset:
    """Pre-configured AutoMod preset for quick setup"""
    id: str
    name: str
    description: str
    rules: List[AutoModRule] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "rules": [r.to_dict() for r in self.rules],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AutoModPreset":
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            rules=[AutoModRule.from_dict(r) for r in data.get("rules", [])],
        )


@dataclass
class AutoModEvent:
    """Logged AutoMod event (for dashboard history/analytics)"""
    id: str
    guild_id: int
    user_id: int
    rule_id: str
    rule_name: str
    action_taken: str
    timestamp: int  # Unix timestamp
    message_content: Optional[str] = None
    reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AutoModEvent":
        return cls(**data)
