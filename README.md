
# FluxMod | [FluxMod Support Guild](https://fluxer.gg/AvLlZRNA)

A modular Fluxer auto-moderation system with independent bot, backend API, and web dashboard.


- **Bot**: Fluxer bot that enforces rules in real-time  
- **Backend**: FastAPI REST API with Fluxer OAuth for rule management  
- **Frontend**: Lightweight web dashboard for managing rules

Project Structure
-----------------

```
FluxMod/
├── backend/             # FastAPI backend (runs on server)
│   ├── api.py
│   ├── .env            # OAuth & config
│   ├── data.json       # JSON store (or swap for database)
│   ├── bot/            # Fluxer bot (runs on server)
│   │   ├── bot.py
│   │   ├── cogs/       # Fluxer command groups
│   │   ├── utils/      # Shared engine, models, manager
│   │   ├── docs/       # Architecture docs
│   │   ├── requirements.txt
│   │   └── README.md
│   ├── requirements.txt
│   └── README.md
├── frontend/            # Web dashboard (self-hosted or cloud)
│   ├── public/index.html        # Landing/login page
│   ├── public/dashboard.html    # Dashboard page
│   ├── public/info.html         # Infomation page
│   ├── public/contributors.html # Contributors page
│   ├── public/404.html          # Not Found page
│   └── README.md
└── README.md           # This file
```

Contributing
------------

Issues and pull requests welcome. Follow repo contribution guidelines.

License
-------

MIT


