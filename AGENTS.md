# Agent Instructions for TextHunter Desktop App

## Project Overview

**Windows Desktop Application** built with:
- **Frontend**: Vue 3 + Vite + TypeScript + Tailwind CSS
- **Backend**: Python FastAPI sidecar (PyInstaller bundled)
- **Desktop**: Electron + electron-builder
- **Build**: PyInstaller for Python, electron-builder for NSIS bundling
- **Package Manager**: npm (frontend), uv (Python)
- **HTTP Client**: Native `fetch()` API
- **Auto-Update**: electron-updater with GitHub Releases
- **Target**: Windows x64 (NSIS installer + portable EXE)

## Key Commands

### Development
```bash
# Install all dependencies (Node + Python)
npm run install-reqs

# Run desktop app in development mode (Electron + frontend + sidecar)
npm run dev

# Run frontend and backend separately for testing
npm run dev:all

# Run sidecar only
npm run dev:sidecar
```

### Building
```bash
# Build Python sidecar (required before electron build)
npm run build:sidecar-winos

# Build Windows desktop app (NSIS installer + portable)
npm run build:desktop

# Build frontend only
npm run build:frontend

# Build Electron app only (after sidecar + frontend)
npm run build:electron
```

## Deployment

### Windows Desktop (Primary)
| Mode | API URL | Build Command |
|------|---------|---------------|
| **Development** | `http://localhost:8000` | `npm run dev` |
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
- Output: `backend/dist/main.exe`

### Frontend (Vue + Vite)
- Source: `frontend/src/` directory
- Dev server runs on port `3000`
- API client uses native `fetch()` (works in Electron without CORS issues)
- Three modes:
  - **Desktop (Electron)**: Direct `localhost:8000` (sidecar)
  - **Web Dev**: `/api` proxy to `localhost:8000`
  - **Web Production**: `/api` relative path (deployed at `/products/text-hunter/`)

### Electron Main Process
- Main entry: `electron/main.ts`
- Preload script: `electron/preload.ts`
- Responsibilities:
  - Spawn Python sidecar on app ready
  - Kill sidecar on app quit
  - IPC handlers for sidecar control
  - Auto-update with `electron-updater`
- Detection: `window.electronAPI.isElectron === true`

### electron-builder Configuration
- Config: `electron-builder.yml`
- Sidecar bundled via `extraResources`
- Icons: `build/icons/icon.ico`
- Auto-update from GitHub Releases

## Important Notes

1. **Sidecar rebuild required**: After any Python code change, run `npm run build:sidecar-winos`
2. **Port conflicts**: Kill processes on ports 3000 and 8000 before running dev
3. **Build order**: Always build sidecar THEN frontend THEN electron
4. **Use npm**: All commands use npm (not bun/pnpm)
5. **Environment switching**: API client automatically switches URLs based on `window.electronAPI`

## Auto-Update Setup

### GitHub Releases
1. Create a new release on GitHub with tag `v0.x.x`
2. Upload NSIS installer and portable EXE to release
3. electron-builder auto-generates `latest.yml` metadata
4. Users get auto-update notifications

### Release Workflow
```bash
# 1. Update version in backend/pyproject.toml
# 2. Update version in package.json and electron-builder.yml
# 3. Build desktop app
npm run build:desktop

# 4. Create GitHub release with files:
#    - release/TextHunter-0.x.x-setup.exe
#    - release/TextHunter-0.x.x-Portable.exe
#    - release/latest.yml
```

## Common Issues

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: texthunter` | Rebuild sidecar with `npm run build:sidecar-winos` |
| Sidecar not starting | Check `backend/dist/main.exe` exists |
| Port 8000/3000 in use | Kill processes before `npm run dev` |
| Electron window blank | Check frontend built: `npm run build:frontend` |
| Auto-update not working | Ensure GitHub release has `latest.yml` file |

## File Structure

```
text-hunter/
├── frontend/                    # Vue.js frontend
│   ├── src/
│   │   ├── components/         # Vue components
│   │   ├── services/           # API and DB services
│   │   └── api/                # API client and types
│   └── dist/                   # Built frontend (for Electron)
├── backend/                     # Python sidecar
│   ├── texthunter/             # Python package
│   │   ├── main.py             # FastAPI entry point (sidecar mode)
│   │   ├── api/                # API routes
│   │   ├── core/               # Business logic
│   │   └── config/             # Settings
│   ├── dist/                   # PyInstaller output (main.exe)
│   └── .venv/                  # Python virtual environment
├── electron/                    # Electron main process
│   ├── main.ts                 # Main process (sidecar spawn, window mgmt)
│   ├── preload.ts              # Context bridge for IPC
│   ├── tsconfig.json           # TypeScript config
│   └── electron-env.d.ts       # Type declarations
├── build/                       # Build resources
│   └── icons/                  # App icons (icon.ico, icon.png)
├── release/                     # Build output directory
│   ├── TextHunter-0.x.x-setup.exe  # NSIS installer
│   ├── TextHunter-0.x.x-Portable.exe  # Portable EXE
│   └── latest.yml              # Auto-update metadata
├── electron-builder.yml         # Build configuration
├── package.json                 # npm scripts
└── AGENTS.md                    # This file
```

## Build Outputs

### Windows Desktop (`npm run build:desktop`)
- **NSIS Installer**: `release/TextHunter-0.7.0-setup.exe`
- **Portable EXE**: `release/TextHunter-0.7.0-Portable.exe`
- **Auto-update metadata**: `release/latest.yml`

### Web Production (`npm run build:web`)
- **Output**: `frontend/dist/` → deploy to `xergiz.com/products/text-hunter/`

## Version Sync

Desktop app version from `package.json`:
```json
{
  "version": "0.7.0"
}
```

Also update in `electron-builder.yml`:
```yaml
version: 0.7.0
```

## Testing

### Test Desktop App (Recommended)
```bash
npm run dev
# Opens Electron window with embedded frontend + sidecar
```

### Test Sidecar Independently
```bash
npm run dev:sidecar
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
# Creates NSIS installer and portable EXE in release/
```

### Verify Auto-Update
1. Check `release/latest.yml` exists after build
2. Ensure GitHub release has matching version
3. Test by running older version and checking for update notification