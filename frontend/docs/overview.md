# Overview

TextHunter is a specialized tool designed for extracting structured data from PDF documents using powerful regex pattern matching. It's particularly tailored for Oil & Gas industry professionals who work with technical documentation.

## Who Is This For?

TextHunter is built for **Oil & Gas engineers, designers, and data managers** who need to extract information from technical documents. It is particularly valuable for professionals working with AutoCAD-based drafting systems who need to extract data from PDF exports of technical drawings.

## Key Features

### 🔍 Pattern Recognition
Extract specific patterns from your PDFs using regular expressions. Perfect for identifying:
- Line numbers (e.g., "12-AB-1234-A1B")
- Instrument tags (e.g., "FT-101", "PCV-2345")
- Equipment tags (e.g., "P-101A", "V-2301")
- Any custom pattern in your documentation

### 📊 Structured Output
Export your extracted data directly to Excel spreadsheets, making it easy to:
- Import into your engineering databases
- Share with team members
- Create master equipment lists
- Generate line lists from P&IDs

### 💾 Local Processing
All PDF processing happens locally in your browser:
- No need to upload sensitive documents to external servers
- Fast processing without network delays
- Complete data privacy

### 🤖 AI-Powered Regex Generation
Not familiar with regex? No problem! Provide a few examples of the pattern you're looking for, and TextHunter will generate the regex pattern for you.

## OCR Support

::: warning Coming Soon
Built-in OCR (Optical Character Recognition) support for scanned PDFs is currently under development and will be available in a future release. For now, TextHunter works best with text-based PDFs.
:::

## System Requirements

- Modern web browser (Chrome, Firefox, Edge, Safari)
- Backend server (Python 3.11+) for regex processing
- No special hardware requirements

## Getting Started

Continue to the [How to Use](/how-to-use) guide to start extracting data from your PDFs.
