# TextHunter Development Notes

## Key Learnings & Troubleshooting Guide

### 1. Tauri v2 HTTP Requests - Using @tauri-apps/plugin-http

**Problem:** Native browser `fetch()` doesn't work for external URLs (like `http://localhost:8000`) in Tauri's webview due to CSP restrictions.

**Solution:** Use Tauri's HTTP plugin for desktop app, native fetch for web.

#### Implementation:

```typescript
// frontend/src/api/client.ts
import { fetch as tauriFetch } from '@tauri-apps/plugin-http';

// Detect Tauri environment
const isTauri = typeof window !== 'undefined' && (window as any).__TAURI_INTERNALS__ !== undefined;

// Use appropriate fetch based on environment
const httpFetch = isTauri ? tauriFetch : window.fetch;

// Use httpFetch for all HTTP calls
const response = await httpFetch(url, { ... });
```

#### Required Setup:

1. **Install the plugin** (already in package.json):
```json
{
  "dependencies": {
    "@tauri-apps/plugin-http": "^2.4.3"
  }
}
```

2. **Add Rust dependency** (`src-tauri/Cargo.toml`):
```toml
[dependencies]
tauri-plugin-http = "2"
```

3. **Initialize plugin** (`src-tauri/src/main.rs`):
```rust
fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_http::init())
        .plugin(tauri_plugin_shell::init())
        // ... rest of config
}
```

4. **Add permissions** (`src-tauri/capabilities/default.json`):
```json
{
  "permissions": [
    "http:default",
    {
      "identifier": "http:default",
      "allow": [
        { "url": "http://localhost:*" },
        { "url": "http://127.0.0.1:*" }
      ]
    }
  ]
}
```

**Important:** The HTTP plugin scope must be configured in capabilities, NOT in tauri.conf.json (the plugin config format in tauri.conf.json is for different plugin types).

---

### 2. CORS Configuration for Tauri

**Problem:** Backend CORS didn't include Tauri-specific origins.

**Solution:** Add Tauri origins to CORS allowlist.

#### Backend Configuration (`backend/texthunter/config/settings.py`):

```python
CORS_ORIGINS: list[str] = [
    "http://localhost:5173",
    "http://localhost:8080",
    "http://127.0.0.1:5173",
    "tauri://localhost",      # Tauri Windows/Linux
    "http://tauri.localhost", # Tauri Windows alternative
    "http://localhost:3000",  # Vite dev server
    "http://localhost:3001",
    "http://localhost:3002",
    "http://localhost:3003",
]
```

Apply in `main.py`:
```python
from texthunter.config.settings import CORS_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,  # Not ["*"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### 3. Environment-Specific API URL Configuration

**Problem:** Different environments need different API base URLs.

**Solution:** Environment detection with fallback.

#### Frontend (`frontend/src/api/client.ts`):

```typescript
const getBaseUrl = (): string => {
  const isTauri = typeof window !== 'undefined' &&
                  (window as any).__TAURI_INTERNALS__ !== undefined;

  if (isTauri) {
    return "http://localhost:8000";  // Direct to sidecar
  }

  return import.meta.env.VITE_API_URL || "/api";  // Web mode
};
```

#### Environment Files:

**`.env.development`:**
```bash
VITE_BASE_PATH=/
VITE_API_URL=/api  # Uses Vite proxy
```

**`.env.production`:**
```bash
VITE_BASE_PATH=/products/text-hunter/
VITE_API_URL=https://api.xergiz.com/text-hunter
```

#### Vite Proxy (`frontend/vite.config.ts`):

```typescript
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, '')
    }
  }
}
```

---

### 4. Detecting Tauri Environment

**Pattern:** Check for `__TAURI_INTERNALS__` global.

```typescript
const isTauri = typeof window !== 'undefined' &&
                (window as any).__TAURI_INTERNALS__ !== undefined;
```

Use this pattern for:
- Choosing HTTP client (Tauri fetch vs native fetch)
- Environment-specific behavior
- Platform-specific features

---

### 5. Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| API shows "Offline" in Tauri app | Native fetch blocked by CSP | Use `@tauri-apps/plugin-http` |
| Web dev server API calls fail | Wrong `.env` file or missing proxy | Check `.env.development` and Vite proxy config |
| "PluginInitialization" error | Wrong plugin config format in tauri.conf.json | Use capabilities for permissions, not tauri.conf.json |
| Port 8000 already in use | Previous sidecar didn't shutdown | Kill process or wait for timeout |
| CORS errors in webview | Missing Tauri origins in CORS | Add `tauri://localhost` to allowlist |

---

### 6. Build Process Overview

```
┌─────────────────────────────────────────────────────────┐
│                   npm run build:desktop                  │
├─────────────────────────────────────────────────────────┤
│ 1. Build sidecar (PyInstaller)                          │
│    backend → src-tauri/bin/api/main-{platform}.exe      │
│                                                         │
│ 2. Build frontend (Vite)                                │
│    frontend/src → frontend/dist                         │
│    Includes docs build (vitepress)                      │
│                                                         │
│ 3. Build Tauri app (Rust)                               │
│    Compiles with embedded sidecar & frontend            │
│    Output: src-tauri/target/release/bundle/             │
└─────────────────────────────────────────────────────────┘
```

---

### 7. Debugging Tips

**Check if running in Tauri:**
```typescript
console.log('Is Tauri:', !!window.__TAURI_INTERNALS__);
```

**Test API connectivity:**
```bash
# Backend directly
curl http://localhost:8000/health

# Web dev proxy
curl http://localhost:3000/api/health

# In Tauri dev tools console
console.log(await fetch('http://localhost:8000/health'))
```

**View Tauri logs:**
- Run `npm run tauri dev` and watch stdout
- Sidecar logs appear with `[tauri]` prefix
- Enable debug: `RUST_LOG=debug npm run tauri dev`

**Check HTTP plugin scope:**
If you see "url not allowed" errors, add to capabilities:
```json
{
  "identifier": "http:default",
  "allow": [{ "url": "http://your-url:*" }]
}
```

---

### 8. Project Structure

```
text-hunter/
├── backend/
│   └── texthunter/
│       ├── main.py              # FastAPI entry point
│       ├── license.py           # License validation
│       ├── api/
│       │   └── routes.py        # API endpoints
│       └── config/
│           └── settings.py      # CORS & config
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── client.ts        # HTTP client (Tauri-aware)
│   │   ├── services/
│   │   │   ├── api.ts           # API service layer
│   │   │   └── license.ts       # License service
│   │   ├── components/
│   │   │   └── LicenseCheck.vue # License validation UI
│   │   └── App.vue              # Main app component
│   ├── .env.development
│   ├── .env.production
│   └── vite.config.ts           # Vite + proxy config
│
└── src-tauri/
    ├── src/
    │   └── main.rs              # Tauri app entry
    ├── capabilities/
    │   └── default.json         # Permissions (HTTP scope)
    ├── Cargo.toml               # Rust dependencies
    └── tauri.conf.json          # Tauri config
```

---

## Recommended Documentation

### Official Documentation

1. **[Tauri v2 Docs](https://v2.tauri.app/)**
   - [Plugin System](https://v2.tauri.app/develop/plugins/)
   - [HTTP Plugin](https://v2.tauri.app/reference/javascript/api/namespacehttp/)
   - [Capabilities & Permissions](https://v2.tauri.app/concepts/security/#permissions)

2. **[Tauri Plugin HTTP](https://github.com/tauri-apps/plugins-workspace/tree/v2/plugins/http)**
   - Source code and examples

3. **[FastAPI Docs](https://fastapi.tiangolo.com/)**
   - CORS middleware setup

4. **[Vite Docs](https://vite.dev/)**
   - [Proxy configuration](https://vite.dev/config/server-options.html#server-proxy)

### Specific Topics

- **Tauri v2 Migration Guide**: https://v2.tauri.app/start/migrate/from-tauri-1/
- **Security Best Practices**: https://v2.tauri.app/concepts/security/
- **Inter-Process Communication**: https://v2.tauri.app/concepts/inter-process-communication/

---

---

## Quick Fix Checklist: "API Offline" in Tauri App

**Symptom:** App shows "API Offline" but `http://localhost:8000` works in browser.

### Step 1: Check Console Error (2 min)

Open DevTools in Tauri app (`Ctrl+Shift+I` or `Cmd+Option+I`):

```
// If you see:
TypeError: Failed to fetch
// or
NotAllowedError: URL not allowed by scope

// → You need @tauri-apps/plugin-http
```

### Step 2: Verify Plugin Installation (1 min)

```bash
# Check package.json
grep "@tauri-apps/plugin-http" package.json

# Should show: "@tauri-apps/plugin-http": "^2.4.3"
```

### Step 3: Check Rust Side (3 min)

**`src-tauri/Cargo.toml`:**
```toml
[dependencies]
tauri-plugin-http = "2"
```

**`src-tauri/src/main.rs`:**
```rust
fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_http::init())  // Must be present
        .plugin(tauri_plugin_shell::init())
        // ...
}
```

### Step 4: Check Capabilities (2 min)

**`src-tauri/capabilities/default.json`:**
```json
{
  "permissions": [
    "http:default",
    {
      "identifier": "http:default",
      "allow": [
        { "url": "http://localhost:*" },
        { "url": "http://127.0.0.1:*" }
      ]
    }
  ]
}
```

### Step 5: Check Frontend HTTP Client (3 min)

**`frontend/src/api/client.ts`:**
```typescript
import { fetch as tauriFetch } from '@tauri-apps/plugin-http';

const isTauri = !!window.__TAURI_INTERNALS__;
const httpFetch = isTauri ? tauriFetch : window.fetch;

// Must use httpFetch, NOT raw fetch
const response = await httpFetch(url, options);
```

### Step 6: Verify Backend CORS (2 min)

**`backend/texthunter/config/settings.py`:**
```python
CORS_ORIGINS = [
    "tauri://localhost",
    "http://tauri.localhost",
    # ... other origins
]
```

### Step 7: Test

```bash
# Restart Tauri dev
npm run tauri dev

# Check console - should see successful API calls
# Check UI - API status should show "Online"
```

---

## Total Time: ~15 minutes if done correctly

**What wasted us 45+ minutes:**
- Wrong plugin config format in `tauri.conf.json` (doesn't apply to HTTP plugin)
- Not checking console error first
- Not verifying all 3 pieces: Rust plugin + Capabilities + TypeScript usage

---

## Quick Reference

### Environment Detection
```typescript
const isTauri = !!window.__TAURI_INTERNALS__;
```

### HTTP Client Pattern
```typescript
import { fetch as tauriFetch } from '@tauri-apps/plugin-http';
const httpFetch = isTauri ? tauriFetch : window.fetch;
await httpFetch(url, options);
```

### Required Files for HTTP Plugin
- `src-tauri/Cargo.toml` - Add dependency
- `src-tauri/src/main.rs` - Initialize plugin
- `src-tauri/capabilities/default.json` - Add permissions + scope
- `frontend/src/api/client.ts` - Use conditional fetch

### CORS Origins to Remember
- `tauri://localhost` - Linux/Windows
- `http://tauri.localhost` - Windows fallback
- `http://localhost:300X` - Vite dev server ports
