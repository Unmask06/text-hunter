# TextHunter Desktop App

Native Windows desktop application for hunting and extracting text patterns from PDF documents.

## Download

Download the latest installer from the [Releases page](https://github.com/Unmask06/text-hunter/releases/latest).

## Features

- 📄 **PDF Text Extraction** - Upload and process PDF files with automatic text extraction
- 🔍 **Regex Pattern Matching** - Search for text patterns using custom regex or AI-generated patterns
- 🤖 **Smart Regex Generation** - Generate regex patterns from example strings
- 📊 **Excel Export** - Export extraction results to Excel with context
- 💾 **Local Processing** - All processing happens locally on your machine (no internet required)
- 🚀 **Fast Performance** - High-performance backend with async processing

## Installation

1. Download the latest installer from the [Releases page](https://github.com/Unmask06/text-hunter/releases/latest)
2. Run the installer
3. Launch TextHunter from your Start menu

## Development

### Prerequisites

- Node.js 18+
- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (Python package manager)

### Setup

```bash
# Install all dependencies
npm run install-reqs

# Run in development mode
npm run dev
```

### Build from Source

```bash
# Build production installer
npm run build:desktop
```

Output: `release/TextHunter-0.x.x-setup.exe`

## Architecture

- **Frontend**: Vue 3 + Vite + TypeScript + Tailwind CSS
- **Backend**: Python FastAPI (bundled as PyInstaller sidecar)
- **Desktop Framework**: Electron + electron-builder

See `AGENTS.md` for detailed development instructions.

## License

MIT License
