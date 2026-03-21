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
- Rust (for Tauri)

### Setup

```bash
# Install all dependencies
npm run install-reqs

# Build Python sidecar
npm run build:sidecar-winos

# Run in development mode
npm run tauri dev
```

### Build from Source

```bash
# Build sidecar
npm run build:sidecar-winos

# Build production installer
npm run tauri build
```

Output: `src-tauri/target/release/bundle/nsis/TextHunter_0.1.0_x64-setup.exe`

## Architecture

- **Frontend**: Vue 3 + Vite + TypeScript + Tailwind CSS
- **Backend**: Python FastAPI (bundled as PyInstaller sidecar)
- **Desktop Framework**: Tauri v2 (Rust-based)

See `AGENTS.md` for detailed development instructions.

## License

MIT License
