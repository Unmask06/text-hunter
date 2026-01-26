# TextHunter Frontend

Vue 3 + TypeScript frontend for PDF text pattern extraction.

## Features

- 📄 **PDF Upload & Processing** - Drag-and-drop file upload with progress tracking
- 🔍 **Regex Configuration** - Input custom regex patterns or generate with AI
- 📊 **Results Display** - Interactive table showing extraction results
- 💾 **Local Storage** - IndexedDB storage for PDFs and extracted text
- 🎨 **Modern UI** - Tailwind CSS with dark theme and responsive design
- ⚡ **Fast Processing** - Web Workers for PDF text extraction

## Tech Stack

- **Vue 3** with Composition API
- **TypeScript** for type safety
- **Vite** for fast development and building
- **Tailwind CSS** for styling
- **Axios** for API communication
- **Dexie.js** for IndexedDB
- **PDF.js** for PDF processing

## Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Regenerate API types from backend
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
│   ├── components/        # Vue components
│   │   ├── FileList.vue   # PDF file management
│   │   ├── FileUpload.vue # Drag-and-drop upload
│   │   ├── RegexConfig.vue # Regex input & generation
│   │   └── ResultsTable.vue # Results display
│   ├── services/          # Business logic
│   │   ├── api.ts         # Backend API client
│   │   └── db.ts          # IndexedDB operations
│   ├── types/             # TypeScript definitions
│   │   └── api.ts         # Generated API types
│   ├── workers/           # Web Workers
│   │   └── pdf.worker.js  # PDF text extraction
│   ├── App.vue            # Root component
│   └── main.ts            # App entry point
├── public/                # Static assets
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── tsconfig.json
```

## Key Components

- **FileUpload**: Handles PDF upload with validation and progress
- **FileList**: Displays uploaded PDFs with status and actions
- **RegexConfig**: Regex input form with AI generation feature
- **ResultsTable**: Paginated results with export functionality
- **API Service**: Axios client for backend communication
- **DB Service**: Dexie.js wrapper for IndexedDB operations

## API Integration

The frontend communicates with the FastAPI backend via REST API. TypeScript types are automatically generated from the OpenAPI schema using `openapi-typescript`.

```bash
# Update API types after backend changes
npm run update-api
```

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Development Notes

- Uses Vue 3 `<script setup>` syntax
- IndexedDB stores PDF blobs and extracted text locally
- Web Workers handle PDF processing to avoid blocking UI
- CORS configured for local development (port 5173)

## License

MIT
