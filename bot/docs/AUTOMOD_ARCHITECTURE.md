# AutoMod Recoded Architecture

## Overview

The AutoMod system has been completely rebuilt to support scaling to online dashboards and databases. The architecture is modular and designed for easy migration from JSON storage to any backend database.

## Architecture Layers

### 1. **Data Models** (`utils/automod_models.py`)
Pure data classes that represent AutoMod concepts. No logic, only data structure and serialization.

**Key Classes:**
- `AutoModRule` - Individual moderation rule
- `GuildAutoModSettings` - Guild configuration
- `AutoModAction` - Action to take on violation
- `AutoModEvent` - Logged event for analytics
- `ExemptEntity` - Exempt role/user/channel
- `AutoModPreset` - Pre-configured rule set

**Benefits:**
- Database-agnostic (can be stored anywhere)
- Full serialization support (`to_dict()` / `from_dict()`)
- Clean API for dashboard consumption

### 2. **Manager/Repository** (`utils/automod_manager.py`)
Abstraction layer for storage and retrieval. All database operations go through here.

**Current Implementation:** JSON files (easily swappable)

**Key Methods:**
- `get_guild_settings()` - Retrieve guild config
- `save_guild_settings()` - Persist changes
- `add_rule()`, `remove_rule()`, `update_rule()` - Rule management
- `apply_preset()` - Quick configuration
- `log_event()` - Store violation events
- `get_events()` - Retrieve analytics

**Migration Path:**
To switch to PostgreSQL/MongoDB/etc:
1. Create new implementation class
2. Keep same method signatures
3. Replace instantiation in cogs/automod.py

### 3. **Engine** (`utils/automod_engine.py`)
Core business logic for checking messages against rules.

**Features:**
- Async message checking
- Multiple rule types: REGEX, KEYWORD, SPAM, CAPS, MENTIONS
- Whitelist support
- Event generation with details

**No storage concerns** - Pure logic layer

### 4. **Fluxer Cog** (`cogs/automod.py`)
Bot integration layer. Commands and event listeners.

**Features:**
- Message monitoring
- User-friendly commands
- Interactive setup wizard
- Status reporting

### 5. **Dashboard API** (`utils/automod_dashboard.py`)
REST-like interface independent of the bot. Perfect for web services.

**Key Features:**
- CRUD operations on all settings
- Rule management
- Exemption management
- Analytics endpoints
- Data import/export
- Configuration validation

## Data Flow

### Checking a Message
```
Message arrives
    ↓
AutoModCog.on_message()
    ↓
AutoModEngine.check_message()
    ↓
Check against enabled rules
    ↓
If violation: Log event + Take action
```

### Updating Settings
```
Dashboard API / Command
    ↓
AutoModManager (storage layer)
    ↓
Serialize to JSON / Database
    ↓
On next message check, use updated settings
```

## File Structure

```
Flux-Nari/
├── cogs/
│   └── automod.py              # Fluxer bot integration
├── utils/
│   ├── automod_models.py       # Data classes
│   ├── automod_manager.py      # Storage abstraction
│   ├── automod_engine.py       # Rule checking logic
│   └── automod_dashboard.py    # Dashboard API
├── data/
│   └── automod/
│       ├── guilds/             # Guild configs (one file per guild)
│       ├── presets.json        # Preset definitions
│       └── events.json         # Event log
```

## Usage Examples

### From Bot
```python
# Command handling automatically uses manager
await ctx.send("AutoMod settings updated!")
```

### From Dashboard
```python
from utils.automod_dashboard import AutoModDashboardAPI

api = AutoModDashboardAPI()

# Get guild config
config = await api.get_guild_config(guild_id=123456)

# Create a rule
rule = await api.create_rule(guild_id=123456, rule_data={
    "name": "Spam Filter",
    "rule_type": "spam",
    "patterns": ["repeat_threshold:3"],
    ...
})

# Get analytics
stats = await api.get_guild_stats(guild_id=123456, days=7)
```

## Scaling to Database

### Step 1: Create Database Manager
```python
class AutoModDatabaseManager(AutoModManager):
    def __init__(self, db_connection):
        self.db = db_connection
    
    async def get_guild_settings(self, guild_id: int):
        # Query database instead of JSON
        result = await self.db.query("SELECT * FROM guild_settings WHERE guild_id = ?", guild_id)
        return GuildAutoModSettings.from_dict(result)
```

### Step 2: Update Instantiation
```python
# In cogs/automod.py
if USE_DATABASE:
    self.manager = AutoModDatabaseManager(db)
else:
    self.manager = AutoModManager()  # Current JSON version
```

### Step 3: Done!
No other changes needed. All layers use the manager abstraction.

## Scaling to Dashboard

### Using FastAPI Example
```python
from fastapi import FastAPI, HTTPException
from utils.automod_dashboard import AutoModDashboardAPI

app = FastAPI()
api = AutoModDashboardAPI()

@app.get("/guilds/{guild_id}/config")
async def get_config(guild_id: int):
    return await api.get_guild_config(guild_id)

@app.post("/guilds/{guild_id}/rules")
async def create_rule(guild_id: int, rule: dict):
    return await api.create_rule(guild_id, rule)

@app.get("/guilds/{guild_id}/stats")
async def get_stats(guild_id: int):
    return await api.get_guild_stats(guild_id)
```

## Rule Types

### REGEX
Pattern matching with optional whitelist
```json
{
  "rule_type": "regex",
  "patterns": ["bad.*word", "another_pattern"],
  "allowed_patterns": ["badger"]
}
```

### KEYWORD
Keyword filtering
```json
{
  "rule_type": "keyword",
  "patterns": ["badword1", "badword2"],
  "allowed_patterns": ["badger_mule"]
}
```

### SPAM
Repeated characters or mentions
```json
{
  "rule_type": "spam",
  "patterns": ["repeat_threshold:5", "mention_count:3"]
}
```

### CAPS
Excessive capitalization
```json
{
  "rule_type": "caps",
  "patterns": ["percentage:70"]
}
```

### MENTIONS
Mention spam detection
```json
{
  "rule_type": "mentions",
  "patterns": ["count:5"]
}
```

## Presets

Default presets (easily customizable):
- **Lenient** - Basic spam and obvious violations
- **Moderate** - Balanced protection (recommended)
- **Strict** - Heavy moderation with warnings

Presets are stored in `data/automod/presets.json`. Edit to customize.

## Features

✅ Message monitoring and enforcement
✅ Multiple rule types and conditions
✅ Whitelisting support
✅ Preset configurations
✅ Exemption management (roles, users, channels)
✅ Event logging and analytics
✅ User-friendly commands
✅ Dashboard-ready API
✅ Database-agnostic architecture
✅ Import/export configurations
✅ Async operations throughout

## Future Enhancements

- [ ] User reputation system
- [ ] Machine learning-based content detection
- [ ] Real-time analytics dashboard
- [ ] Custom rule builder UI
- [ ] Appeal system for false positives
- [ ] Integration with external services
- [ ] Advanced filtering (phishing, spam links, etc.)
