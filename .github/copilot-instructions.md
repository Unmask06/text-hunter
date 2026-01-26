# TextHunter — Copilot Instructions

Purpose: help an AI coding agent be immediately productive in this mono-repo (Vue frontend (TypeScript+ Tailwind CSS) + FastAPI backend).

- **Architecture (high-level)**
  - Frontend: Vue 3 + Vite + TypeScript in `frontend/`. UI stores PDFs and extracted text in IndexedDB via `frontend/src/services/db.ts` and talks to the backend via `frontend/src/services/api.ts`.
  - Backend: FastAPI application in `backend/texthunter/` (entrypoint `python -m texthunter`, app in `texthunter/main.py`). Core logic: `regex_engine.py` and `excel_generator.py`. Pydantic models live in `texthunter/models.py`.

- **Dev / run / test commands (explicit)**
  - Frontend dev: run `npm run dev` from `frontend/`.
  - Regenerate TypeScript API types (requires backend running): `npm run update-api` (runs `openapi-typescript` against `http://localhost:8000/openapi.json`). See `frontend/package.json`.
  - Backend (recommended via `uv` wrapper): `uv sync` to install, `uv run python -m texthunter` to run, `uv run pytest` to run tests. The app can also be started with `python -m texthunter` (uses uvicorn reload).

- **Important repo-specific conventions & patterns**
  - Backend endpoints return Pydantic models (routes use `response_model=`). When changing response shapes, update `texthunter/models.py` and re-generate frontend types (`npm run update-api`).
  - `regex_engine.extract_matches()` yields `MatchResult` objects (not plain dicts). When calling from routes, code converts to serializable dicts (see `routes.py` behavior for preview vs full export).
  - `guess_regex()` uses `grex.RegExpBuilder` and validates the generated pattern; it raises `ValueError` for invalid input. Follow that error pattern for client faults (400 via FastAPI `HTTPException`).
  - Excel export produces a BytesIO buffer which the API streams with a `Content-Disposition` header for filename — frontend `exportExcel()` extracts filename from that header.
  - Frontend IndexedDB schema is defined in `frontend/src/services/db.ts` (tables: `pdfs`, `extractedText`). PDF blobs are stored as ArrayBuffers.

- **Integration points / cross-component notes**
  - CORS: `texthunter/main.py` currently allows `http://localhost:5173`. If frontend port/origin changes, update CORS in `main.py`.
  - API base URL is chosen in `frontend/src/services/api.ts` using `import.meta.env.DEV` and assumes backend runs at `http://localhost:8000` during development.
  - Generating TS types: `npm run update-api` requires the backend to expose `/openapi.json` at `http://localhost:8000`. Start backend first.
  - README mismatch: `backend/README.md` lists endpoints prefixed with `/api/*`, but the code exposes routes at top-level (e.g. `/extract`); `TEXTHUNTER_MOUNTED` can be used in production to alter mounting. Prefer reading `texthunter/routes.py` for truth.

- **Testing guidance**
  - Backend unit tests live under `backend/tests/` and exercise `regex_engine` functions (use `pytest`). Tests expect Python 3.11+.
  - When modifying regex logic, keep the existing behavior: `extract_matches()` should raise `ValueError` on invalid regex and yield `MatchResult` objects; `guess_regex()` must require ≥2 examples and return a pattern that `fullmatch`s the inputs.

- **When you change an API shape or add endpoints**
  1. Update/extend `texthunter/models.py` (Pydantic models).
  2. Update `texthunter/routes.py` to expose/serialize new models.
  3. Run the backend and regenerate frontend types: `cd frontend && npm run update-api`.
  4. Adjust frontend API calls in `frontend/src/services/api.ts` and the UI components under `frontend/src/components/`.

- **Key files to inspect (start here)**
  - [Frontend README](../frontend/README.md)
  - [Backend README](../backend/README.md)
