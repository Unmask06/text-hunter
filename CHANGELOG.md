# Changelog

All notable changes to TextHunter are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- License validation system to control distribution
- GitHub releases API integration for version checking
- Offline grace period (3 days) for users without internet
- License caching (7 days) to minimize API calls
- New `/v1/license/check` and `/v1/license/clear` API endpoints
- LicenseCheck Vue component for validation UI
- Environment variable support for GitHub PAT (`GITHUB_PAT`)

### Technical
- New module: `backend/texthunter/license.py` for license logic
- New service: `frontend/src/services/license.ts` for API client
- New component: `frontend/src/components/LicenseCheck.vue` for UI
- Added `requests` and `tomli` dependencies to backend

## [0.7.0] - 2026-03-21

### Added
- Native Windows desktop application using Tauri v2
- PyInstaller sidecar bundling for Python FastAPI backend
- NSIS installer and portable ZIP distribution options
- GitHub Actions workflow for automated desktop builds and releases
- New `build:desktop` and `build:web` npm scripts for environment-specific builds
- Desktop app documentation (`DESKTOP-README.md` and `AGENTS.md`)

### Changed
- HTTP client switched from axios to native fetch for Tauri CORS compatibility
- API base URL now environment-aware (desktop: `localhost:8000`, web: `/api`)
- CORS configuration updated to support desktop sidecar mode
- Base path configuration now uses `VITE_BASE_PATH` environment variable
- Refactored API client layer with new `httpClient` module

### Fixed
- Removed circular dependency in `pyproject.toml`
- Dynamic version naming in README and release artifacts

### Technical
- Moved PyInstaller to dev dependencies
- Added Tauri API bindings for desktop integration
- Enhanced build configuration for multi-platform support

---

## [0.6.0] - Previous Release

### Added
- PDF text extraction with marked content support
- Regex pattern matching and AI-powered regex generation
- Excel export functionality
- Vue 3 frontend with IndexedDB storage
- FastAPI backend with async processing
