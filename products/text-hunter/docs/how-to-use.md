# How to Use

This guide will walk you through the process of extracting data from your PDF documents using TextHunter.

## Step 1: Upload Your PDF Files

1. Click the **Upload PDF** button or drag and drop PDF files into the upload area
2. Multiple files can be uploaded at once
3. Each file will be automatically processed to extract text content
4. Wait for the status to change from "Processing" to "Ready"

::: tip File Processing
The application extracts text from each page of your PDF and stores it locally in your browser's IndexedDB. This process happens once per file, and the extracted text is cached for future use.
:::

## Step 2: Configure Your Pattern

TextHunter offers two ways to define the pattern you're looking for:

### Option A: Manual Regex Pattern

If you're familiar with regular expressions, you can enter your pattern directly:

**Example patterns:**
```regex
# Line numbers (e.g., 12-AB-1234-A1B)
\d{2}-[A-Z]{2}-\d{4}-[A-Z]\d[A-Z]

# Instrument tags (e.g., FT-101, PCV-2345)
[A-Z]{2,3}-\d{3,4}[A-Z]?

# Equipment tags (e.g., P-101A, V-2301)
[A-Z]-\d{3,4}[A-Z]?
```

### Option B: AI Regex Generation

If you're not comfortable with regex, let the AI generate it for you:

1. Click the **AI Regex Generator** button
2. Provide at least 2 example strings that match your desired pattern
3. Click **Generate Pattern**
4. Review and use the generated regex pattern

**Example:**
```
Input examples:
- FT-101
- PT-2345
- LT-401A

Generated pattern: [A-Z]{2,3}-\d{3,4}[A-Z]?
```

### Optional: File Identifier Pattern

If you want to extract additional context (like drawing numbers or sheet names) from the PDF filenames, you can add a file identifier regex pattern.

## Step 3: Extract Matches

1. Click the **Extract** button
2. The application will search all uploaded PDFs for your pattern
3. Preview the first 10 matches in the results table
4. Review the matched text, page numbers, and line numbers

::: info Performance
For large documents, TextHunter shows a preview of 10 matches. All matches are processed in the background for export.
:::

## Step 4: Export to Excel

Once you're satisfied with the results:

1. Click the **Export to Excel** button in the header
2. An Excel file will be downloaded with the following columns:
   - **Match**: The extracted text
   - **Filename**: Source PDF file
   - **Page**: Page number where the match was found
   - **Line**: Line number within the page
   - **Context**: Surrounding text for context

## Tips for Best Results

### 📄 PDF Quality
- **Best**: Text-based PDFs (created from CAD software exports)
- **Good**: High-quality scanned PDFs with clear text
- **Poor**: Low-resolution scans or handwritten documents

::: warning OCR Coming Soon
For scanned PDFs, built-in OCR support is planned for a future release. Currently, you may need to use external OCR tools first.
:::

### 🎯 Pattern Design

**Start Simple**: Begin with a basic pattern and refine it based on results

**Use Examples**: The AI regex generator works best when you provide diverse examples

**Test Incrementally**: Upload a sample PDF first to test your pattern before processing large batches

### 🔄 Workflow Integration

**Drawing Reviews**: Extract all instruments from P&IDs to verify against instrument index

**Line List Generation**: Pull all line numbers from isometric drawings

**Equipment Tracking**: Create equipment lists from general arrangement drawings

**Data Validation**: Cross-check extracted data against existing databases

## Common Patterns for Oil & Gas

### Line Numbers
```regex
# Format: XX-XXX-XXXX-XXX
\d{2}-[A-Z]{2,3}-\d{4}-[A-Z]\d[A-Z]?

# Variations:
# 12-AB-1234-A1B
# 24-PW-5678-C2D
```

### Instrument Tags
```regex
# Format: XX-XXX or XXX-XXX
[A-Z]{2,3}-\d{3,4}[A-Z]?

# Examples:
# FT-101, PT-2345, LT-401A
# TCV-5678B, PDT-9012
```

### Equipment Tags
```regex
# Format: X-XXX[X]
[A-Z]{1,2}-\d{3,4}[A-Z]?

# Examples:
# P-101A, V-2301, E-4501B
# C-789, T-1234
```

### Valve Tags
```regex
# Format: XXX-XXXX
[A-Z]{2,3}-\d{4}

# Examples:
# HV-1234, CV-5678, BDV-9012
```

## Troubleshooting

### No Matches Found
- Verify your PDF contains searchable text (not just images)
- Check your regex pattern is correct
- Try the AI generator with actual examples from your PDF

### Too Many Matches
- Make your regex pattern more specific
- Add context requirements (e.g., require specific prefixes)
- Use word boundaries (\b) in your pattern

### Incorrect Matches
- Review the preview results
- Refine your regex pattern to exclude false positives
- Consider adding lookahead or lookbehind assertions

### Slow Processing
- Upload fewer files at once
- Process large PDFs individually
- Ensure your backend server is running and accessible

## Need Help?

If you encounter issues or need assistance with pattern creation, refer to the [Use Cases](/use-cases) section for industry-specific examples.
