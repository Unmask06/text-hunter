/**
 * Web Worker for PDF.js text extraction.
 * Processes PDFs in a background thread to avoid blocking the UI.
 * 
 * P&ID Optimization: Concatenates strings on the same Y-coordinate (±2pt tolerance)
 * to ensure fragmented line numbers are seen as one string.
 */

import * as pdfjsLib from 'pdfjs-dist';

// Configure PDF.js worker
pdfjsLib.GlobalWorkerOptions.workerSrc = new URL(
    'pdfjs-dist/build/pdf.worker.min.mjs',
    import.meta.url
).toString();

const Y_TOLERANCE = 2; // Points tolerance for same-line detection

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
        const textContent = await page.getTextContent();

        // Reconstruct lines using Y-coordinate grouping
        const reconstructedText = reconstructLines(textContent.items);
        pages[pageNum] = reconstructedText;
    }

    return {
        pageCount: pdf.numPages,
        pages,
    };
}

/**
 * Reconstruct text lines from text items.
 * Groups items by Y-coordinate and sorts by X within each line.
 * 
 * @param {Array} items - PDF.js text items with transform coordinates
 * @returns {string} Reconstructed text with proper line breaks
 */
function reconstructLines(items) {
    if (!items || items.length === 0) return '';

    // Group items by Y-coordinate (within tolerance)
    const lineGroups = [];

    for (const item of items) {
        if (!item.str || item.str.trim() === '') continue;

        // Extract Y coordinate from transform matrix [a, b, c, d, x, y]
        const y = item.transform ? item.transform[5] : 0;
        const x = item.transform ? item.transform[4] : 0;

        // Find existing line group within tolerance
        let foundGroup = null;
        for (const group of lineGroups) {
            if (Math.abs(group.y - y) <= Y_TOLERANCE) {
                foundGroup = group;
                break;
            }
        }

        if (foundGroup) {
            foundGroup.items.push({ x, text: item.str });
        } else {
            lineGroups.push({
                y,
                items: [{ x, text: item.str }],
            });
        }
    }

    // Sort groups by Y (descending, as PDF Y increases upward)
    lineGroups.sort((a, b) => b.y - a.y);

    // Sort items within each group by X and join
    const lines = lineGroups.map(group => {
        group.items.sort((a, b) => a.x - b.x);
        return group.items.map(item => item.text).join(' ');
    });

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
