# Agent Instructions for TextHunter Desktop App

## Project Overview

**Windows Desktop Application** built with:
- **Frontend**: Vue 3 + Vite + TypeScript + Tailwind CSS
- **Backend**: Python FastAPI sidecar (PyInstaller bundled)
- **Build**: PyInstaller for Python, Tauri CLI for NSIS bundling
- **Package Manager**: npm (frontend), uv (Python)
- **HTTP Client**: Native `fetch()` API (axios incompatible with Tauri CORS)
- **Target**: Windows x64 (NSIS installer + portable ZIP)

## Key Commands

### Development
```bash
# Install all dependencies (Node + Python)
npm run install-reqs

# Run desktop app in development mode
npm run tauri dev

# Run frontend and backend separately for testing
npm run dev:all
```

### Building
```bash
# Build Python sidecar (required before tauri build)
npm run build:sidecar-winos

# Build Windows desktop app (NSIS installer + portable)
npm run build:desktop
```

## Deployment

### Windows Desktop (Primary)
| Mode | API URL | Build Command |
|------|---------|---------------|
| **Development** | `http://localhost:8000` | `npm run tauri dev` |
| **Production** | `http://localhost:8000` (bundled sidecar) | `npm run build:desktop` |

### Web Production (Secondary - xergiz.com)
| Mode | Base Path | API URL | Build Command |
|------|-----------|---------|---------------|
| **Web** | `/products/text-hunter/` | `https://api.xergiz.com/text-hunter` | `npm run build:web` |

Environment files:
- `.env.development` - Local web dev
- `.env.production` - Production web deployment

## Development Guidelines

### Python Sidecar
- Main entry: `backend/texthunter/main.py`
- API runs on port `8000` (desktop mode)
- Always rebuild sidecar after Python changes: `npm run build:sidecar-winos`
- PyInstaller bundles all dependencies into single executable

### Frontend (Vue + Vite)
- Source: `frontend/src/` directory
- Dev server runs on port `3000`
- API client uses native `fetch()` for Tauri CORS compatibility
- Three modes:
  - **Desktop**: Direct `localhost:8000` (sidecar)
  - **Web Dev**: `/api` proxy to `localhost:8000`
  - **Web Production**: `/api` relative path (deployed at `/products/text-hunter/`)

### Tauri Configuration
- Config: `src-tauri/tauri.conf.json`
- Sidecar path: `src-tauri/bin/api/main.exe`
- Rust main: `src-tauri/src/main.rs`
- Icons: `src-tauri/icons/` (Windows: `.ico`, `.png`)

## Important Notes

1. **Sidecar rebuild required**: After any Python code change, run `npm run build:sidecar-winos`
2. **Port conflicts**: Kill processes on ports 3000 and 8000 before running dev
3. **Build order**: Always build sidecar BEFORE running `tauri build` or `npm run build:desktop`
4. **Use npm**: All commands use npm (not bun/pnpm)
5. **Environment switching**: API client automatically switches URLs based on environment (Tauri vs web)

## Common Issues

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: texthunter` | Rebuild sidecar with `npm run build:sidecar-winos` |
| Sidecar not starting | Check `src-tauri/bin/api/` has `main.exe` |
| Port 8000/3000 in use | Kill processes before `tauri dev` |
| Build fails with permission error | Check `src-tauri/capabilities/default.json` has correct permissions |
| API offline in frontend | Ensure using native `fetch()` not axios (CORS issue with Tauri) |

## File Structure

```
text-hunter/
├── frontend/                    # Vue.js frontend
│   ├── src/
│   │   ├── components/         # Vue components
│   │   ├── services/           # API and DB services
│   │   └── api/                # API client and types
│   └── dist/                   # Built frontend (for Tauri)
├── backend/                     # Python sidecar
│   ├── texthunter/             # Python package
│   │   ├── main.py             # FastAPI entry point (sidecar mode)
│   │   ├── api/                # API routes
│   │   ├── core/               # Business logic
│   │   └── config/             # Settings
│   └── .venv/                  # Python virtual environment
├── src-tauri/
│   ├── bin/api/                # Compiled sidecar executable
│   ├── icons/                  # App icons (auto-generated)
│   ├── src/main.rs             # Tauri Rust entry (sidecar management)
│   ├── capabilities/           # Tauri permissions
│   ├── tauri.conf.json         # Tauri configuration
│   └── target/release/bundle/  # Built installers
├── public/                      # Static assets (app icon source)
├── package.json                 # npm scripts
└── AGENTS.md                    # This file
```

## Build Outputs

### Windows Desktop (`npm run build:desktop`)
- **NSIS Installer**: `src-tauri/target/release/bundle/nsis/TextHunter_<version>_x64-setup.exe`
- **Portable EXE**: `src-tauri/target/release/TextHunter.exe`
- **Portable ZIP**: `TextHunter-portable-<version>.zip` (contains EXE + sidecar)

### Web Production (`npm run build:web`)
- **Output**: `frontend/dist/` → deploy to `xergiz.com/products/text-hunter/`

## Version Sync

Desktop app version syncs with web app version from `backend/pyproject.toml`:
```toml
[project]
version = "0.6.0"  # This version is used for desktop app
```

Update version in one place to sync across web and desktop.

## Testing

### Test Desktop App (Recommended)
```bash
npm run tauri dev
# Opens native window with embedded frontend + sidecar
```

### Test Sidecar Independently
```bash
cd backend
uv run python -m texthunter
# Should start on http://localhost:8000
```

### Test Frontend Independently
```bash
cd frontend
npm run dev
# Opens at http://localhost:3000
# API requests proxy to localhost:8000
```

### Build Full Desktop App
```bash
npm run build:desktop
# Creates NSIS installer and portable ZIP in src-tauri/target/release/bundle/
```
