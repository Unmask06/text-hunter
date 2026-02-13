# TextHunter

Hunt and extract text patterns from PDF documents using powerful regex tools.

TextHunter is a full-stack web application that allows you to upload PDF files, extract text content, and search for patterns using regular expressions. It features an intuitive Vue.js frontend with IndexedDB storage and a FastAPI backend for high-performance text processing.

## Features

- 📄 **PDF Text Extraction** - Upload and process PDF files with automatic text extraction
- 🔍 **Regex Pattern Matching** - Search for text patterns using custom regex or AI-generated patterns
- 🤖 **Smart Regex Generation** - Generate regex patterns from example strings
- 📊 **Excel Export** - Export extraction results to Excel with context
- 💾 **Local Storage** - Store PDFs and extracted text locally in your browser
- 🚀 **Fast Processing** - High-performance backend with async processing

## Architecture

- **Frontend**: Vue 3 + Vite + TypeScript + Tailwind CSS
- **Backend**: FastAPI + Python 3.11+
- **Storage**: IndexedDB (frontend) + in-memory processing (backend)
- **Deployment**: Ready for containerization and cloud deployment

## Quick Start

### Prerequisites

- Node.js 18+
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended Python package manager)

### Installation & Running

1. **Clone the repository**

   ```bash
   git clone https://github.com/Unmask06/text-hunter.git
   cd text-hunter
   ```

2. **Start the application**

   ```bash
   # Windows PowerShell
   .\launch.ps1
   ```

   This will start both backend (port 8000) and frontend (port 5173) servers.

### Manual Setup

**Backend:**

```bash
cd backend
uv sync
uv run python -m texthunter
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

## Usage

1. Open your browser to `http://localhost:5173`
2. Upload PDF files using the file upload area
3. Wait for text extraction to complete
4. Configure your regex pattern or use the AI regex generator
5. Extract matches and export results to Excel

## Documentation

📚 **Comprehensive documentation is available** for TextHunter, including:
- Overview and target users
- How-to guides with examples
- Oil & Gas industry use cases (line lists, instrument lists, equipment lists)

### Access Documentation

**Development:**
```bash
cd frontend
npm run docs:dev
```
Visit `http://localhost:5173/products/text-hunter/docs/` (or check console for actual port)

**Production Build:**
```bash
cd frontend
npm run docs:build
```

**From the Application:**
Click the "Docs" button in the top-right corner of the TextHunter application.

## API Documentation

The backend provides a REST API with the following endpoints:

- `GET /` - API information
- `GET /health` - Health check
- `POST /extract` - Extract matches (preview)
- `POST /extract-all` - Extract all matches
- `POST /guess-regex` - Generate regex from examples
- `POST /export` - Export to Excel

Full API documentation available at `http://localhost:8000/docs` when running.

## Development

### Backend Development

```bash
cd backend
uv sync --group dev
uv run pytest  # Run tests
```

### Frontend Development

```bash
cd frontend
npm run update-api  # Regenerate TypeScript types from backend
```

## Project Structure

```
text-hunter/
├── backend/                 # FastAPI backend
│   ├── texthunter/
│   │   ├── main.py         # FastAPI app
│   │   ├── routes.py       # API endpoints
│   │   ├── models.py       # Pydantic models
│   │   ├── regex_engine.py # Regex processing
│   │   └── excel_generator.py # Excel export
│   └── tests/              # Backend tests
├── frontend/                # Vue.js frontend
│   ├── src/
│   │   ├── components/     # Vue components
│   │   ├── services/       # API and DB services
│   │   └── types/          # TypeScript types
│   └── public/             # Static assets
├── launch.ps1              # Development launcher
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see individual component licenses for details.
