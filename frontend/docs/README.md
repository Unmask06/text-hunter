# TextHunter Documentation

Welcome to the TextHunter documentation! This guide will help you extract structured data from your PDF documents using powerful regex pattern matching.

## What is TextHunter?

TextHunter is a specialized tool designed for **Oil & Gas industry professionals** who need to extract information from technical documents such as:

- Process and Instrumentation Diagrams (P&IDs)
- Line Lists
- Instrument Lists
- Equipment Lists
- Isometric Drawings
- General Arrangement Drawings

## Who Should Use TextHunter?

TextHunter is perfect for:

- **Engineers and Designers** working with AutoCAD-based drawings (not SPPID)
- **Project Teams** needing to extract data from PDF exports of technical drawings
- **Data Managers** who want to avoid manual data entry from drawings
- **Anyone** working with Oil & Gas technical documentation

## Quick Start

1. **Upload Your PDFs**: Drop your PDF files into the application or click to browse
2. **Configure Your Pattern**: Define the text pattern you're looking for (e.g., line numbers, instrument tags)
3. **Extract Matches**: Run the extraction to find all matching patterns
4. **Export to Excel**: Download your results as an Excel spreadsheet

## Documentation Sections

### 📖 [Overview](./overview.md)
Learn about TextHunter's features, architecture, and target users. Understand what makes TextHunter ideal for Oil & Gas workflows.

### 🎯 [How to Use](./how-to-use.md)
Step-by-step guide to using TextHunter:
- Uploading PDF files
- Creating regex patterns (manual or AI-generated)
- Extracting matches
- Exporting to Excel
- Tips and troubleshooting

### 🛢️ [Use Cases](./use-cases.md)
Real-world examples for Oil & Gas applications:
- **Line List Generation**: Extract line numbers from P&IDs
- **Instrument List Extraction**: Build instrument indexes
- **Equipment List Generation**: Create master equipment lists
- Common regex patterns for Oil & Gas naming conventions

## Common Patterns

Here are some commonly used regex patterns for Oil & Gas documentation:

**Line Numbers** (e.g., 12-AB-1234-A1B):
```regex
\d{2}-[A-Z]{2,3}-\d{4}-[A-Z]\d[A-Z]?
```

**Instrument Tags** (e.g., FT-101, PCV-2345A):
```regex
[A-Z]{2,3}-\d{3,4}[A-Z]?
```

**Equipment Tags** (e.g., P-101A, V-2301):
```regex
[A-Z]{1,2}-\d{3,4}[A-Z]?
```

## Need Help?

- **Not familiar with regex?** Use the AI Regex Generator in the application - just provide examples of what you're looking for
- **Questions about specific patterns?** Check the [Use Cases](./use-cases.md) section for industry-specific examples
- **Having issues?** See the troubleshooting section in [How to Use](./how-to-use.md)

## Coming Soon

🔍 **Built-in OCR support** for scanned PDFs is currently under development and will be available in a future release.

---

**Ready to get started?** Click the "Launch App" button in the navigation to open TextHunter, or continue reading the [Overview](./overview.md) to learn more.

