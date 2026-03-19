/**
 * Web Worker for PDF.js text extraction.
 * Processes PDFs in a background thread to avoid blocking the UI.
 * 
 * P&ID Optimization: Uses PDF Marked Content to preserve CAD text groups.
 * CAD software (AutoCAD, etc.) exports related text as marked content groups,
 * ensuring fragmented line numbers like "PI2143" are extracted as a single string.
 * 
 * Text grouping is based SOLELY on PDF marked content boundaries - no coordinate
 * based grouping is applied. This matches how PDF viewers handle text selection.
 */

import * as pdfjsLib from 'pdfjs-dist';

// Configure PDF.js worker
pdfjsLib.GlobalWorkerOptions.workerSrc = new URL(
    'pdfjs-dist/build/pdf.worker.min.mjs',
    import.meta.url
).toString();

/**
 * Extract text from a PDF ArrayBuffer.
 * @param {ArrayBuffer} pdfData - The PDF file data
 * @returns {Promise<{pageCount: number, pages: Object}>}
 */
async function extractTextFromPdf(pdfData) {
    const pdf = await pdfjsLib.getDocument({ data: pdfData }).promise;
    const pages = {};

    for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
        const page = await pdf.getPage(pageNum);
        
        // Enable marked content extraction to preserve CAD text groups
        const textContent = await page.getTextContent({
            includeMarkedContent: true
        });

        // Extract text respecting marked content boundaries only
        const extractedText = extractTextWithMarkedContent(textContent.items);
        pages[pageNum] = extractedText;
    }

    return {
        pageCount: pdf.numPages,
        pages,
    };
}

/**
 * Extract text preserving CAD marked content groups.
 * 
 * CAD software exports related text as marked content groups:
 *   /Tag BMC          <- Begin Marked Content
 *     (PI) Tj         <- Text "PI"
 *     5 0 Td          <- Move position
 *     (2143) Tj       <- Text "2143"
 *   EMC               <- End Marked Content
 * 
 * This function respects these boundaries EXACTLY as defined in the PDF.
 * NO coordinate-based grouping is applied.
 * 
 * @param {Array} items - PDF.js text items and marked content markers
 * @returns {string} Extracted text with proper grouping
 */
function extractTextWithMarkedContent(items) {
    if (!items || items.length === 0) return '';

    const lines = [];
    let currentLineParts = [];
    let markedContentStack = [];
    let lastY = null;
    // Y-tolerance for line breaks: separates distinct text elements (headers, footers)
    // while keeping visually grouped text (like line numbers) together.
    // Higher tolerance (5) prevents false line breaks within same visual line.
    const Y_TOLERANCE = 5;

    for (const item of items) {
        // Handle marked content begin
        if (item.type === 'beginMarkedContent' || item.type === 'beginMarkedContentProps') {
            markedContentStack.push({
                id: item.id,
                textParts: []
            });
            continue;
        }

        // Handle marked content end
        if (item.type === 'endMarkedContent') {
            if (markedContentStack.length > 0) {
                const group = markedContentStack.pop();
                const groupText = group.textParts.join('');
                
                if (markedContentStack.length === 0) {
                    // Top-level group completed - add as a single unit
                    if (groupText.trim()) {
                        currentLineParts.push(groupText);
                    }
                } else {
                    // Nested group - add to parent
                    const parentGroup = markedContentStack[markedContentStack.length - 1];
                    parentGroup.textParts.push(groupText);
                }
            }
            continue;
        }

        // Skip non-text items
        if (!item.str || item.str.trim() === '') continue;

        // Process text item
        if (markedContentStack.length > 0) {
            // Inside a marked content group - collect text without adding spaces
            const currentGroup = markedContentStack[markedContentStack.length - 1];
            currentGroup.textParts.push(item.str);
        } else {
            // Outside marked content - treat each text item as separate
            // Use Y-coordinate ONLY for line breaks, NOT for grouping
            const y = item.transform ? item.transform[5] : 0;

            // Start a new line if Y coordinate changes significantly
            if (lastY !== null && Math.abs(y - lastY) > Y_TOLERANCE) {
                if (currentLineParts.length > 0) {
                    lines.push(currentLineParts.join(' '));
                    currentLineParts = [];
                }
            }

            currentLineParts.push(item.str);
            lastY = y;
        }
    }

    // Handle unclosed marked content (malformed PDF)
    if (markedContentStack.length > 0) {
        while (markedContentStack.length > 0) {
            const group = markedContentStack.pop();
            const groupText = group.textParts.join('');
            if (groupText.trim()) {
                currentLineParts.push(groupText);
            }
        }
    }

    // Commit remaining content
    if (currentLineParts.length > 0) {
        lines.push(currentLineParts.join(' '));
    }

    return lines.join('\n');
}

// Handle messages from main thread
self.onmessage = async function (event) {
    const { type, pdfId, pdfData } = event.data;

    if (type === 'extract') {
        try {
            self.postMessage({ type: 'progress', pdfId, status: 'processing' });

            const result = await extractTextFromPdf(pdfData);

            self.postMessage({
                type: 'complete',
                pdfId,
                pageCount: result.pageCount,
                pages: result.pages,
            });
        } catch (error) {
            self.postMessage({
                type: 'error',
                pdfId,
                error: error.message,
            });
        }
    }
};
