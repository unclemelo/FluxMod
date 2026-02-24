# AutoMod Developer Reference

## Quick Start

### Using the Manager (Core Storage Layer)
```python
from utils.automod_manager import AutoModManager

manager = AutoModManager()

# Get/Create guild settings
settings = await manager.get_guild_settings(guild_id=123456)

# Save changes
await manager.save_guild_settings(settings)
```

### Using the Dashboard API (Recommended for Web Services)
```python
from utils.automod_dashboard import AutoModDashboardAPI

api = AutoModDashboardAPI()

# Get full configuration
config = await api.get_guild_config(guild_id=123456)

# Create a rule
rule = await api.create_rule(guild_id, {
    "name": "Spam Detection",
    "rule_type": "spam",
    "patterns": ["repeat_threshold:5"],
    "severity": 2
})
```

### Using the Engine (Rule Checking)
```python
from utils.automod_engine import AutoModEngine
from utils.automod_models import GuildAutoModSettings

engine = AutoModEngine()
settings = await manager.get_guild_settings(guild_id)

# Check a message
violated_rule, event = await engine.check_message(
    message_content="SPAM SPAM SPAM",
    user_id=987654,
    guild_id=123456,
    settings=settings
)

if violated_rule:
    print(f"Rule violated: {violated_rule.name}")
    print(f"Event: {event.to_dict()}")
```

## API Reference

### Guild Configuration

**Get Configuration**
```python
config = await api.get_guild_config(guild_id)
# Returns: dict with all settings, rules, exemptions
```

**Update Configuration**
```python
await api.update_guild_config(guild_id, {
    "enabled": True,
    "log_channel_id": 123456,
    "prefix": "[AutoMod]"
})
```

**Reset to Default**
```python
await api.reset_guild_config(guild_id)
```

### Rule Management

**Create Rule**
```python
rule = await api.create_rule(guild_id, {
    "name": "Custom Rule",
    "rule_type": "regex",
    "patterns": ["pattern1", "pattern2"],
    "allowed_patterns": ["exception"],
    "action": {
        "type": "delete",
        "duration_seconds": None,
        "custom_message": None
    },
    "severity": 3
})
# Returns: rule dict with auto-generated ID
```

**List Rules**
```python
rules = await api.list_rules(guild_id, enabled_only=True)
# Returns: list of rule dicts
```

**Update Rule**
```python
rule = await api.update_rule(guild_id, rule_id, {
    "enabled": False,
    "patterns": ["new_pattern"]
})
```

**Toggle Rule**
```python
rule = await api.toggle_rule(guild_id, rule_id)
# Returns: updated rule with enabled flipped
```

**Delete Rule**
```python
deleted = await api.delete_rule(guild_id, rule_id)
# Returns: bool
```

### Presets

**List Presets**
```python
presets = await api.list_presets()
# Returns: [{"id": "lenient", "name": "Lenient", ...}, ...]
```

**Apply Preset**
```python
success = await api.apply_preset(guild_id, "moderate")
# Returns: bool
```

### Exemptions

**Add Exemption**
```python
exemption = await api.add_exemption(
    guild_id=123456,
    entity_id=789012,
    entity_type="role",  # "role", "user", or "channel"
    name="Moderators"
)
```

**Remove Exemption**
```python
removed = await api.remove_exemption(
    guild_id=123456,
    entity_id=789012,
    entity_type="role"
)
```

**Check if Exempt**
```python
is_exempt = await api.is_exempt(guild_id, entity_id, "role")
```

**List Exemptions**
```python
exemptions = await api.list_exemptions(guild_id, "role")
# Returns: list of exemption dicts
```

### Analytics

**Get Guild Statistics**
```python
stats = await api.get_guild_stats(guild_id, days=7)
# Returns: {
#     "total_violations": 42,
#     "violations_by_rule": {"Spam": 20, "Caps": 15, ...},
#     "violations_by_user": {123456: 5, 654321: 3, ...},
#     "violations_by_action": {"delete": 30, "warn": 12},
#     "top_rules": [("Spam", 20), ("Caps", 15)],
#     "top_users": [(123456, 5), (654321, 3)]
# }
```

**Get Events**
```python
events = await api.get_events(
    guild_id=123456,
    limit=100,
    rule_id=None  # optional
)
```

**Get User History**
```python
history = await api.get_user_history(guild_id, user_id, limit=50)
# Returns: last 50 violations by user
```

### Import/Export

**Export Configuration**
```python
export_data = await api.export_guild_config(guild_id)
# Returns: {
#     "settings": {...},
#     "recent_events": [...],
#     "export_timestamp": 1234567890
# }
```

**Import Configuration**
```python
success = await api.import_guild_config(guild_id, export_data)
```

### Validation

**Validate Rule**
```python
is_valid, error = await api.validate_rule(rule_dict)
if not is_valid:
    print(f"Invalid rule: {error}")
```

**Validate Complete Config**
```python
is_valid, error = await api.validate_config(config_dict)
```

## Data Models

### AutoModRule
```python
AutoModRule(
    id: str = "auto-generated",
    name: str = "Rule Name",
    rule_type: RuleType = RuleType.REGEX,
    enabled: bool = True,
    patterns: List[str] = ["pattern1", "pattern2"],
    allowed_patterns: List[str] = ["exception"],
    action: AutoModAction = AutoModAction(ActionType.DELETE),
    severity: int = 1  # 1-5
)
```

### AutoModAction
```python
AutoModAction(
    type: ActionType = ActionType.DELETE,  # see ActionType enum
    duration_seconds: Optional[int] = None,  # for mute/ban
    custom_message: Optional[str] = None  # DM to user
)
```

### ActionType
```python
ActionType.DELETE      # Delete the message
ActionType.WARN        # Delete + log
ActionType.MUTE        # Mute user (requires duration)
ActionType.KICK        # Kick user
ActionType.BAN         # Ban user (requires duration)
```

### RuleType
```python
RuleType.REGEX         # Pattern matching
RuleType.KEYWORD       # Simple keyword matching
RuleType.SPAM         # Repeated content or mentions
RuleType.CAPS         # Excessive capitals
RuleType.MENTIONS     # Mention spam
```

### GuildAutoModSettings
```python
GuildAutoModSettings(
    guild_id: int,
    enabled: bool = True,
    rules: List[AutoModRule] = [],
    exempt_roles: List[ExemptEntity] = [],
    exempt_users: List[ExemptEntity] = [],
    exempt_channels: List[ExemptEntity] = [],
    log_channel_id: Optional[int] = None,
    prefix: str = "[AutoMod]"
)
```

## Example: Building a Dashboard Endpoint

```python
from fastapi import FastAPI, HTTPException
from utils.automod_dashboard import AutoModDashboardAPI

app = FastAPI()
api = AutoModDashboardAPI()

@app.get("/api/guilds/{guild_id}/config")
async def get_config(guild_id: int):
    return await api.get_guild_config(guild_id)

@app.post("/api/guilds/{guild_id}/rules")
async def create_rule(guild_id: int, rule_data: dict):
    try:
        result = await api.create_rule(guild_id, rule_data)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/api/guilds/{guild_id}/rules/{rule_id}")
async def update_rule(guild_id: int, rule_id: str, updates: dict):
    result = await api.update_rule(guild_id, rule_id, updates)
    if not result:
        raise HTTPException(status_code=404, detail="Rule not found")
    return {"success": True, "data": result}

@app.delete("/api/guilds/{guild_id}/rules/{rule_id}")
async def delete_rule(guild_id: int, rule_id: str):
    success = await api.delete_rule(guild_id, rule_id)
    if not success:
        raise HTTPException(status_code=404, detail="Rule not found")
    return {"success": True}

@app.get("/api/guilds/{guild_id}/stats")
async def get_stats(guild_id: int, days: int = 7):
    return await api.get_guild_stats(guild_id, days)

@app.post("/api/guilds/{guild_id}/presets/{preset_id}")
async def apply_preset(guild_id: int, preset_id: str):
    success = await api.apply_preset(guild_id, preset_id)
    if not success:
        raise HTTPException(status_code=404, detail="Preset not found")
    return {"success": True}
```

## Example: Creating a Custom Rule Programmatically

```python
from utils.automod_models import AutoModRule, AutoModAction, ActionType, RuleType

# Create a rule that blocks URLs
url_rule = AutoModRule(
    name="Block URLs",
    rule_type=RuleType.REGEX,
    patterns=[r"https?://\S+", r"www\.\S+"],
    allowed_patterns=[],
    action=AutoModAction(
        type=ActionType.DELETE,
        custom_message="Links are not allowed in this server."
    ),
    severity=2
)

# Save it
manager = AutoModManager()
await manager.add_rule(guild_id=123456, rule=url_rule)
```

## Tips & Best Practices

1. **Always use the Dashboard API** for external services - it's the stable interface
2. **Use presets** for quick setup instead of creating rules manually
3. **Set exemptions** for moderators to avoid catching their messages
4. **Monitor events** for false positives and whitelist as needed
5. **Use severity levels** to tune rule enforcement intensity
6. **Export configs** before major changes as backup
7. **Test rules** on a test server first
8. **Keep patterns simple** - complex regex is harder to maintain

## Troubleshooting

**Rules not triggering?**
- Check if AutoMod is enabled: `api.get_guild_config()`
- Check if rule is enabled: `rule.enabled == True`
- Check if user is exempt: `api.is_exempt()`
- Check if channel is exempt: check `exempt_channels`

**Events not logging?**
- Ensure log_channel_id is set
- Check bot has permission to send in log channel
- Events are stored even if logging fails

**Dashboard can't connect?**
- Check manager is initialized properly
- Check file permissions on `data/automod/` directory
- Check for errors in event log
