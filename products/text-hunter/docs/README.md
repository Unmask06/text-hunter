# TextHunter Documentation

This directory contains the VitePress-based documentation for TextHunter.

## Overview

The documentation provides comprehensive guides for using TextHunter, specifically tailored for Oil & Gas industry professionals working with technical documents like P&IDs, line lists, instrument lists, and equipment lists.

## Documentation Structure

- **Overview** (`overview.md`) - Introduction to TextHunter, target users, and key features
- **How to Use** (`how-to-use.md`) - Step-by-step guide for extracting data from PDFs
- **Use Cases** (`use-cases.md`) - Industry-specific examples for Oil & Gas applications

## Development

### Prerequisites

- Node.js 18+
- npm or yarn

### Install Dependencies

```bash
npm install
```

### Run Development Server

```bash
npm run dev
```

The documentation will be available at `http://localhost:5173/`

### Build for Production

```bash
npm run build
```

The built documentation will be in `../../../dist/products/text-hunter/docs/`

### Preview Production Build

```bash
npm run preview
```

## Configuration

The documentation is configured using VitePress in `.vitepress/config.mjs`:

- **No GitHub link**: Social links are disabled as requested
- **Default theme**: Uses VitePress default theme
- **Launch App link**: Navigation includes link to open the main application
- **Custom navigation**: Organized into Getting Started and Applications sections

## Integration with Main App

The main TextHunter application (`frontend/src/App.vue`) includes a "Docs" button in the header that opens this documentation in a new tab.

## Key Features for Oil & Gas Industry

The documentation emphasizes:

- **Target Users**: Engineers and designers using AutoCAD (not SPPID)
- **Line List Generation**: Extracting line numbers from P&IDs and isometric drawings
- **Instrument List Extraction**: Creating instrument indexes from technical drawings
- **Equipment List Generation**: Building comprehensive equipment lists
- **Common Patterns**: Regex patterns for line numbers, instrument tags, equipment tags, and valves
- **OCR Notice**: Documentation mentions that built-in OCR is coming soon

## Contributing

When updating the documentation:

1. Edit the relevant `.md` files
2. Test locally with `npm run dev`
3. Verify all links work correctly
4. Build and test the production version
5. Commit changes with descriptive messages

## Notes

- Documentation opens in a new tab when accessed from the main app
- The "Launch App" button in the docs links back to `http://localhost:5173` (adjust for production)
- All external links use `target="_blank"` and `rel="noopener"` for security
