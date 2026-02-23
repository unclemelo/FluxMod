# AutoMod Bot

Discord bot component for AutoMod. Handles moderation commands and event listening.

## Structure

- `bot.py` — bot entrypoint and initialization
- `cogs/` — Discord Cogs (command groups, event handlers)
- `utils/` — shared utility modules (engine, manager, models, dashboard)
- `docs/` — architecture and developer reference

## Setup

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# Linux/Mac
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Set environment variables (create `.env` in this directory):

```env
DISCORD_TOKEN=your_bot_token_here
BACKEND_API_URL=http://localhost:8000
```

## Run

```bash
python bot.py
```

## Development

- Add new commands or listeners in `cogs/automod.py`
- Extend rule engine in `utils/automod_engine.py`
- Implement data models in `utils/automod_models.py`

## Deployment (Ubuntu)

1. Clone repo, navigate to `bot/` directory
2. Create venv and install deps
3. Configure `.env` with Discord token and backend URL
4. Run with systemd service or pm2 supervisor

Example systemd service (`/etc/systemd/system/automod-bot.service`):

```ini
[Unit]
Description=AutoMod Discord Bot
After=network.target

[Service]
Type=simple
User=automod
WorkingDirectory=/home/automod/AutoMod/bot
Environment="PYTHONUNBUFFERED=1"
ExecStart=/home/automod/AutoMod/bot/.venv/bin/python bot.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then run:
```bash
sudo systemctl daemon-reload
sudo systemctl enable automod-bot
sudo systemctl start automod-bot
```
