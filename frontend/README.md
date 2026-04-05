# TextHunter Frontend

Vue 3 + TypeScript frontend for PDF text pattern extraction.

## Features

- 📄 **PDF Upload & Processing** — Drag-and-drop file upload with progress tracking
- 🔍 **Regex Configuration** — Input custom regex patterns or generate with AI
- 📊 **Results Display** — Interactive table showing extraction results
- 💾 **Local Storage** — IndexedDB storage for PDFs, extracted text, and pattern cache
- ☁️ **Cloud Sync** — Config presets sync to backend (SQLite desktop / Supabase web)
- 🎨 **Modern UI** — Tailwind CSS v4 with dark theme and responsive design

## Tech Stack

- **Vue 3** with Composition API (`<script setup>`)
- **TypeScript** for type safety
- **Vite** for fast development and building
- **Tailwind CSS v4** for styling
- **Native `fetch()`** for API communication (Tauri-compatible)
- **Dexie.js** for IndexedDB
- **PDF.js** for PDF processing

## Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Regenerate API types from backend (backend must be running)
npm run update-api

# Build for production
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── FileList.vue       # PDF file management
│   │   ├── FileUpload.vue     # Drag-and-drop upload
│   │   ├── RegexConfig.vue    # Regex input, AI generation, presets
│   │   └── ResultsTable.vue   # Results display
│   ├── services/
│   │   ├── api.ts             # API service layer
│   │   ├── db.ts              # IndexedDB operations (PDFs, text, patterns)
│   │   └── db-cloud.ts        # Cloud sync for config presets
│   ├── api/
│   │   ├── client.ts          # HTTP client (Tauri-aware, uses fetch)
│   │   └── schema.ts          # Generated TypeScript types from OpenAPI
│   ├── workers/
│   │   └── pdf.worker.js      # PDF text extraction
│   ├── App.vue                # Root component
│   └── main.ts                # App entry point
├── docs/                      # VitePress documentation
├── public/                    # Static assets
├── package.json
├── vite.config.ts
└── tsconfig.json
```

## Key Components

- **FileUpload**: Handles PDF upload with validation and progress
- **FileList**: Displays uploaded PDFs with status and actions
- **RegexConfig**: Regex input form with AI generation and preset management
- **ResultsTable**: Paginated results with export functionality
- **API Client**: Native `fetch()` wrapper — auto-switches URL by environment (Tauri vs web)
- **DB Service**: Dexie.js wrapper for IndexedDB (PDFs, extracted text, pattern cache)
- **DB Cloud Service**: Syncs config presets to backend API

## API Integration

The frontend communicates with the FastAPI backend via REST API. TypeScript types are automatically generated from the OpenAPI schema using `openapi-typescript`.

```bash
# Update API types after backend changes (backend must be running on :8000)
npm run update-api
```

## Storage Flow

```
Desktop:  IndexedDB (local) ←→ Backend SQLite (localhost:8000)
Web:      IndexedDB (local) ←→ Backend Supabase (user-scoped via JWT)
```

## Environment Files

| File | Purpose |
|------|---------|
| `.env.development` | Local web dev — API URL `/api` (proxied to :8000) |
| `.env.production` | Production web — API URL `https://api.xergiz.com/text-hunter` |

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## License

MIT
