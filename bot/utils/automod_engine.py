"""
AutoMod Engine - Core logic for checking messages against rules
"""

import re
from typing import List, Tuple, Optional
from datetime import datetime, timedelta
import uuid
from .automod_models import (
    AutoModRule, RuleType, ActionType, AutoModEvent, GuildAutoModSettings
)


class AutoModEngine:
    """Core engine for processing messages against AutoMod rules"""

    def __init__(self):
        self.mention_pattern = re.compile(r"<@!?\d+>")
        self.user_cooldowns = {}  # Track spam per user: {user_id: {guild_id: timestamps}}

    async def check_message(
        self,
        message_content: str,
        user_id: int,
        guild_id: int,
        settings: GuildAutoModSettings,
    ) -> Tuple[Optional[AutoModRule], Optional[AutoModEvent]]:
        """
        Check a message against all enabled rules.
        Returns the violated rule and event if triggered, else (None, None)
        """
        if not settings.enabled:
            return None, None

        # Check each enabled rule in order
        for rule in settings.rules:
            if not rule.enabled:
                continue

            violated, details = await self._check_rule(
                message_content, user_id, guild_id, rule, settings
            )

            if violated:
                event = AutoModEvent(
                    id=str(uuid.uuid4()),
                    guild_id=guild_id,
                    user_id=user_id,
                    rule_id=rule.id,
                    rule_name=rule.name,
                    action_taken=rule.action.type.value,
                    timestamp=int(datetime.now().timestamp()),
                    message_content=message_content[:100],  # Store first 100 chars
                    reason=details,
                )
                return rule, event

        return None, None

    async def _check_rule(
        self,
        message_content: str,
        user_id: int,
        guild_id: int,
        rule: AutoModRule,
        settings: GuildAutoModSettings,
    ) -> Tuple[bool, Optional[str]]:
        """Check if a rule is violated"""

        if rule.rule_type == RuleType.REGEX:
            return self._check_regex_rule(message_content, rule)

        elif rule.rule_type == RuleType.KEYWORD:
            return self._check_keyword_rule(message_content, rule)

        elif rule.rule_type == RuleType.SPAM:
            return await self._check_spam_rule(message_content, user_id, guild_id, rule)

        elif rule.rule_type == RuleType.CAPS:
            return self._check_caps_rule(message_content, rule)

        elif rule.rule_type == RuleType.MENTIONS:
            return self._check_mentions_rule(message_content, rule)

        return False, None

    def _check_regex_rule(self, content: str, rule: AutoModRule) -> Tuple[bool, Optional[str]]:
        """Check regex patterns"""
        for pattern in rule.patterns:
            try:
                if re.search(pattern, content, re.IGNORECASE):
                    # Check whitelist
                    violated = True
                    for allowed in rule.allowed_patterns:
                        if re.search(allowed, content, re.IGNORECASE):
                            violated = False
                            break
                    
                    if violated:
                        return True, f"Matched regex: {pattern[:50]}"
            except re.error:
                continue
        return False, None

    def _check_keyword_rule(self, content: str, rule: AutoModRule) -> Tuple[bool, Optional[str]]:
        """Check keyword patterns"""
        content_lower = content.lower()
        
        for keyword in rule.patterns:
            if keyword.lower() in content_lower:
                # Check whitelist
                violated = True
                for allowed in rule.allowed_patterns:
                    if allowed.lower() in content_lower:
                        violated = False
                        break
                
                if violated:
                    return True, f"Contained keyword: {keyword}"
        
        return False, None

    async def _check_spam_rule(
        self, content: str, user_id: int, guild_id: int, rule: AutoModRule
    ) -> Tuple[bool, Optional[str]]:
        """Check spam patterns (repeat threshold, mention spam, etc.)"""
        
        # Parse spam rule parameters from patterns
        for param in rule.patterns:
            if param.startswith("repeat_threshold:"):
                threshold = int(param.split(":")[1])
                
                # Count repeated characters
                consecutive_count = 1
                for i in range(1, len(content)):
                    if content[i].lower() == content[i - 1].lower():
                        consecutive_count += 1
                        if consecutive_count >= threshold:
                            return True, f"Repeated characters exceed {threshold}"
                    else:
                        consecutive_count = 1
        
        return False, None

    def _check_caps_rule(self, content: str, rule: AutoModRule) -> Tuple[bool, Optional[str]]:
        """Check excessive capitals"""
        
        # Parse caps rule parameters
        for param in rule.patterns:
            if param.startswith("percentage:"):
                percentage = int(param.split(":")[1])
                
                # Calculate uppercase percentage
                letters = sum(1 for c in content if c.isalpha())
                if letters < 5:  # Ignore very short messages
                    return False, None
                
                caps = sum(1 for c in content if c.isupper())
                cap_percentage = (caps / letters) * 100
                
                if cap_percentage >= percentage:
                    return True, f"Excessive capitals: {cap_percentage:.1f}%"
        
        return False, None

    def _check_mentions_rule(self, content: str, rule: AutoModRule) -> Tuple[bool, Optional[str]]:
        """Check mention spam"""
        
        # Count mentions
        mentions = self.mention_pattern.findall(content)
        
        # Parse mention rule parameters
        for param in rule.patterns:
            if param.startswith("count:"):
                threshold = int(param.split(":")[1])
                if len(mentions) >= threshold:
                    return True, f"Mention count exceeds {threshold}"
        
        return False, None

    def clear_cooldowns(self, user_id: int) -> None:
        """Clear cooldowns for a user"""
        if user_id in self.user_cooldowns:
            del self.user_cooldowns[user_id]

    @staticmethod
    def format_message(
        action: ActionType,
        rule_name: str,
        reason: str,
        prefix: str = "[AutoMod]"
    ) -> str:
        """Format a message for logging an AutoMod action"""
        action_text = {
            ActionType.DELETE: "🗑️ Message deleted",
            ActionType.WARN: "⚠️ Warning issued",
            ActionType.MUTE: "🔇 User muted",
            ActionType.KICK: "👢 User kicked",
            ActionType.BAN: "🔨 User banned",
        }.get(action, "Action taken")
        
        return f"{prefix} {action_text}\n**Rule:** {rule_name}\n**Reason:** {reason}"
