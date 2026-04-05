# TextHunter Backend

FastAPI backend service for PDF text pattern extraction, P&ID symbol detection, and config management.

## Features

- 🔍 **Regex-based text extraction** from PDF content
- 🤖 **Smart regex generation** from example strings using grex
- 📊 **Excel export** with extraction results and context
- 🏗️ **Config persistence** — save/load regex presets (SQLite desktop / Supabase web)
- 👁️ **P&ID symbol detection** — OpenCV template matching on rendered PDF pages
- 🏥 **Health check** endpoint for monitoring

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (recommended package manager)

## Quick Start

```bash
# Install dependencies
uv sync

# Run the development server
uv run python -m texthunter
```

The API will be available at `http://localhost:8000`.

## API Endpoints

| Method | Endpoint              | Description                          |
| ------ | --------------------- | ------------------------------------ |
| GET    | `/`                   | API info and version                 |
| GET    | `/health`             | Health check                         |
| POST   | `/extract`            | Extract matches (preview, max 10)    |
| POST   | `/extract-all`        | Extract all matches for export       |
| POST   | `/guess-regex`        | Generate regex from examples         |
| POST   | `/export`             | Export matches to Excel              |
| POST   | `/v1/history/configs` | Save a regex config preset           |
| GET    | `/v1/history/configs` | List all saved config presets        |
| DELETE | `/v1/history/configs/{id}` | Delete a config preset        |
| GET    | `/v1/connect`         | Tauri sidecar health check           |
| POST   | `/v1/legend/extract`  | Extract symbol templates from legend |
| POST   | `/v1/symbol/detect`   | Detect symbols in a P&ID PDF         |
| POST   | `/v1/page/render`     | Render a PDF page to image           |
| POST   | `/v1/vision/export`   | Export symbol detections to Excel    |

Full interactive docs at `http://localhost:8000/docs` when running.

## Development

```bash
# Install dev dependencies
uv sync --group dev

# Run tests
uv run pytest

# Lint
uv run ruff check .
```

## Project Structure

```
backend/
├── texthunter/
│   ├── __init__.py
│   ├── __main__.py           # Module entry point
│   ├── main.py               # FastAPI app & CORS config
│   ├── license.py            # License validation
│   ├── api/
│   │   ├── routes.py         # Core API endpoints
│   │   ├── configs.py        # Config preset CRUD
│   │   └── schemas.py        # Pydantic request/response models
│   ├── core/
│   │   ├── regex.py          # Regex extraction and generation
│   │   ├── excel.py          # Excel export with formatting
│   │   ├── history.py        # Config storage (SQLite / Supabase)
│   │   └── vision/           # P&ID symbol detection
│   │       ├── __init__.py
│   │       ├── opencv.py     # OpenCV primitives (matching, contours, annotation)
│   │       └── operations.py # PDF rendering + text association
│   ├── config/
│   │   └── settings.py       # CORS and runtime constants
│   └── utils/                # Shared utilities
├── migrations/
│   └── 001_*.sql             # SQLite migrations (auto-applied on startup)
├── tests/
│   └── test_regex_engine.py  # Unit tests
├── pyproject.toml
└── README.md
```

## Storage

| Environment | Backend | Path |
|-------------|---------|------|
| Desktop | SQLite | `%LOCALAPPDATA%\XergiZ\TextHunter\texthunter.db` |
| Web | Supabase PostgreSQL | User-scoped via JWT |

Migrations in `backend/migrations/*.sql` are auto-applied on startup for SQLite.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `TEXTHUNTER_MOUNTED` | `false` | Set to `true` in production to disable `/api` prefix |
| `SUPABASE_URL` | — | Supabase project URL (web mode) |
| `SUPABASE_SERVICE_KEY` | — | Supabase service role key (web mode) |
| `SUPABASE_JWT_SECRET` | — | JWT secret for token verification (web mode) |

## License

MIT
