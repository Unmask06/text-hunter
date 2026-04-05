# Agent Instructions for TextHunter

## Project Overview

**Windows Desktop App** + **Web App** for PDF text pattern extraction.

| Layer | Tech |
|-------|------|
| Frontend | Vue 3 + Vite + TypeScript + Tailwind CSS v4 |
| Backend | Python FastAPI sidecar (PyInstaller bundled) |
| Desktop | Tauri v2 (Rust) |
| Storage (desktop) | SQLite (`~/.texthunter/texthunter.db`) |
| Storage (web) | Supabase PostgreSQL (user-scoped) |
| Storage (frontend) | IndexedDB via Dexie.js (PDFs, text, pattern cache) |
| Package Manager | npm (frontend), uv (Python) |
| Linter/Formatter | Biome (frontend), Ruff (Python) |

## Key Commands

```bash
# Install all deps (Node + Python)
npm run install-reqs

# Desktop dev mode (Tauri window with hot reload)
npm run tauri dev

# Frontend + backend separately (no Tauri)
npm run dev:all

# Build Python sidecar (MUST run before any tauri build)
npm run build:sidecar-winos

# Full desktop build (NSIS installer + portable)
npm run build:desktop

# Web build (deploys to xergiz.com/products/text-hunter/)
npm run build:web

# Regenerate TypeScript API types from OpenAPI spec
cd frontend && npm run update-api
```

## Critical Rules

1. **Always rebuild sidecar after Python changes**: `npm run build:sidecar-winos`
2. **Build order**: sidecar → `npm run build` → `npm run tauri build`
3. **Use native `fetch()` in frontend**, never axios (Tauri CORS incompatible)
4. **Kill ports 3000/8000** before `tauri dev`
5. **All commands use npm** (not bun/pnpm/yarn)

## Architecture

### Backend (`backend/texthunter/`)
- Entry: `main.py` (FastAPI on port 8000)
- Routes: `api/routes.py` (core API), `api/configs.py` (config CRUD)
- Storage: `core/history.py` — dual backend (SQLite for desktop, Supabase for web)
- Configs table: `texthunter_configs` (id, user_id, name, keyword_regex, file_identifier_regex, created_at, modified)
- **No extractions table** — extraction results handled by frontend IndexedDB
- Migrations: `backend/migrations/*.sql` — auto-applied on startup for SQLite

### Frontend (`frontend/src/`)
- API client: `api/client.ts` — auto-switches URL by environment (Tauri vs web)
- IndexedDB: `services/db.ts` — stores PDFs, extracted text, pattern cache
- Cloud sync: `services/db-cloud.ts` — syncs configs to backend
- RegexConfig.vue — uses both IndexedDB (local cache) + db-cloud.ts (backend sync)
- VitePress docs built as part of every build

### Tauri (`src-tauri/`)
- Config: `tauri.conf.json`
- Sidecar binary: `bin/api/main.exe`
- Rust entry: `src/main.rs` (sidecar lifecycle management)

### Storage Flow
```
Desktop:  Frontend IndexedDB ←→ Backend SQLite (localhost:8000)
Web:      Frontend IndexedDB ←→ Backend Supabase (user-scoped via JWT)
```

## Testing

```bash
# Desktop app (recommended)
npm run tauri dev

# Backend standalone
cd backend && uv run python -m texthunter

# Frontend standalone (proxies API to :8000)
cd frontend && npm run dev

# Backend tests
cd backend && uv run pytest

# Lint + typecheck
cd backend && uv run ruff check .
cd frontend && npx biome check src/
```

## Common Issues

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: texthunter` | Rebuild sidecar: `npm run build:sidecar-winos` |
| Sidecar not found | Verify `src-tauri/bin/api/main.exe` exists |
| Port 8000/3000 in use | Kill processes before `tauri dev` |
| API offline in frontend | Must use `fetch()`, not axios |
| `texthunter_configs` UNIQUE constraint | Unique on `(user_id, name)`, not just `name` |

## Version

Synced across `backend/pyproject.toml` and `src-tauri/tauri.conf.json`. Current: `0.7.0`
