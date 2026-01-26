# TextHunter Backend

FastAPI backend service for PDF text pattern extraction using regex.

## Features

- 🔍 **Regex-based text extraction** from PDF content
- 🤖 **Smart regex generation** from example strings using grex
- 📊 **Excel export** with extraction results and context
- 🏥 **Health check** endpoint for monitoring
- 📋 **Pydantic models** for type-safe API responses

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

| Method | Endpoint       | Description                       |
| ------ | -------------- | --------------------------------- |
| GET    | `/`            | API info and version              |
| GET    | `/health`      | Health check                      |
| POST   | `/extract`     | Extract matches (preview, max 10) |
| POST   | `/extract-all` | Extract all matches for export    |
| POST   | `/guess-regex` | Generate regex from examples      |
| POST   | `/export`      | Export matches to Excel           |

## Development

```bash
# Install dev dependencies
uv sync --group dev

# Run tests
uv run pytest

# Run with auto-reload (default when using python -m)
uv run python -m texthunter
```

## Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=texthunter
```

## Project Structure

```
backend/
├── texthunter/
│   ├── __init__.py
│   ├── __main__.py       # Module entry point
│   ├── main.py           # FastAPI app & CORS config
│   ├── routes.py         # API endpoints with error handling
│   ├── models.py         # Pydantic request/response models
│   ├── regex_engine.py   # Core regex extraction logic
│   └── excel_generator.py # Excel export with formatting
├── tests/
│   └── test_regex_engine.py # Unit tests
├── pyproject.toml        # Dependencies & project config
├── uv.lock              # Lock file
└── README.md
```

## Key Components

- **regex_engine.py**: Core logic for pattern matching and regex generation
- **excel_generator.py**: Pandas-based Excel export with styling
- **routes.py**: FastAPI routes with proper error handling
- **models.py**: Type-safe API models using Pydantic

## Environment Variables

| Variable             | Default | Description                                          |
| -------------------- | ------- | ---------------------------------------------------- |
| `TEXTHUNTER_MOUNTED` | `false` | Set to `true` in production to disable `/api` prefix |

## License

MIT
