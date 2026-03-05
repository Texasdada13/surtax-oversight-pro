# Surtax Oversight Pro

Unified government contract and surtax oversight dashboard for Marion County, Florida. Consolidates three separate Flask applications into a single, comprehensive tool.

## Features

- **Dual View System**: Toggle between Surtax Oversight and Contract Management views
- **Persona System**: Committee Member (simplified) vs District Staff (full analytics)
- **27+ Dashboard Pages**: Surtax projects, contracts, monitoring, financials, documents, tools
- **Analytics Engine**: EVM forecasting, health scoring, risk assessment, procurement benchmarking (Coupa 2025)
- **AI-Powered Chat**: Claude API integration for intelligent Q&A about portfolio data
- **Meeting Mode**: Full-screen presentation mode with key stats for committee meetings
- **Public Portal**: Read-only transparency portal for public access
- **Compliance Dashboard**: Insurance, bonding, board approval monitoring
- **Geographic Map**: Leaflet.js project map with health-colored markers

## Quick Start

```bash
# Clone
git clone https://github.com/Texasdada13/surtax-oversight-pro.git
cd surtax-oversight-pro

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your settings (SECRET_KEY, optional ANTHROPIC_API_KEY)

# Initialize database and generate sample data
python scripts/init_db.py
python scripts/generate_sample_data.py

# Or migrate from existing apps (if you have the source databases):
# python scripts/migrate_from_existing.py
# python scripts/verify_data.py

# Run
python run.py --debug
```

Visit `http://127.0.0.1:5847/`

## Project Structure

```
surtax-oversight-pro/
├── run.py                     # Entry point
├── config/
│   ├── personas.py            # Persona & view mode configuration
│   ├── default.yaml           # App configuration
│   └── counties/marion.yaml   # County-specific config
├── app/
│   ├── __init__.py            # App factory
│   ├── config.py              # Config loader
│   ├── database.py            # Request-scoped SQLite
│   ├── models/schema.sql      # 22-table unified schema
│   ├── services/
│   │   ├── executive_analytics.py  # EVM forecasting, risk scoring
│   │   ├── scoring_engine.py       # Health scoring, alert generation
│   │   ├── benchmarking.py         # Coupa 2025 KPI benchmarks
│   │   ├── ai_chat.py             # Claude API integration
│   │   ├── ai_insights.py         # Rule-based insights
│   │   └── stats.py               # Statistics service
│   ├── routes/
│   │   ├── surtax.py        # Surtax projects, schools, concerns
│   │   ├── contracts.py     # Contract dashboard, detail, vendors
│   │   ├── monitoring.py    # Risk, watchlist, audit trail, alerts
│   │   ├── financials.py    # Budget, analytics, benchmarking
│   │   ├── documents.py     # Library, minutes, annual report
│   │   ├── tools.py         # Meeting mode, compliance, map, portal
│   │   └── api.py           # JSON endpoints, persona switching
│   └── templates/            # 39 Jinja2 templates (Tailwind + Alpine.js)
├── scripts/
│   ├── init_db.py
│   ├── generate_sample_data.py
│   ├── migrate_from_existing.py
│   └── verify_data.py
└── data/
    └── surtax_pro.db
```

## Source Applications

This project consolidates:

| Source | Contribution |
|--------|-------------|
| **contract-oversight-system** | EVM analytics, scoring engine, benchmarking, 296 contracts |
| **florida-school-surtax-oversight** | App factory pattern, YAML config, service architecture |
| **surtax-oversight-dashboard** | Persona system, meeting mode, enhanced templates, project phases |

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Yes | Flask session secret |
| `ANTHROPIC_API_KEY` | No | Enables AI-powered chat |
| `SURTAX_COUNTY` | No | County name (default: marion) |

### Claude AI Chat

Set `ANTHROPIC_API_KEY` in `.env` to enable AI-powered Q&A. The chat service injects portfolio data context into each request, enabling questions like:
- "What is the overall budget status?"
- "Which projects are delayed and by how much?"
- "Summarize vendor performance"

Without the API key, the chat falls back to a helpful message.

## Tech Stack

- **Backend**: Flask 3.x, SQLite, Python 3.10+
- **Frontend**: Tailwind CSS (CDN), Alpine.js
- **Analytics**: Custom EVM engine, Coupa 2025 benchmarks
- **AI**: Anthropic Claude API (optional)
- **Maps**: Leaflet.js + OpenStreetMap

## License

Proprietary - Patriot Tech Systems Consulting LLC
