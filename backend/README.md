# TextHunter Backend

FastAPI backend service for PDF text pattern extraction using regex.

## Features

- 🔍 **Regex-based text extraction** from PDF content
- 🤖 **Smart regex generation** from example strings
- 📊 **Excel export** with extraction results
- 🏥 **Health check** endpoint for monitoring

## Requirements

- Python 3.11+
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

| Method | Endpoint        | Description                              |
| ------ | --------------- | ---------------------------------------- |
| GET    | `/`             | API info and version                     |
| GET    | `/api/health`   | Health check                             |
| POST   | `/api/extract`  | Extract matches (preview, max 10)        |
| POST   | `/api/extract-all` | Extract all matches                   |
| POST   | `/api/guess-regex` | Generate regex from examples          |
| POST   | `/api/export`   | Export matches to Excel                  |

## Development

```bash
# Install dev dependencies
uv sync --group dev

# Run tests
uv run pytest

# Run with auto-reload
uv run python -m texthunter
```

## Project Structure

```
backend/
├── texthunter/
│   ├── __init__.py
│   ├── __main__.py       # Entry point
│   ├── main.py           # FastAPI app configuration
│   ├── routes.py         # API endpoints
│   ├── models.py         # Pydantic models
│   ├── regex_engine.py   # Regex extraction logic
│   └── excel_generator.py # Excel export
├── tests/
├── pyproject.toml
└── README.md
```

## Environment Variables

| Variable            | Default | Description                                    |
| ------------------- | ------- | ---------------------------------------------- |
| `TEXTHUNTER_MOUNTED`| `false` | Set to `true` in production to disable `/api` prefix |

## License

MIT
