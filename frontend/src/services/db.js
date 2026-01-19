/**
 * Dexie.js database configuration for IndexedDB storage.
 * Stores PDF files and extracted text locally in the browser.
 */
import Dexie from 'dexie';

/** @type {Dexie} */
export const db = new Dexie('TextExtractorDB');

// Define database schema
db.version(1).stores({
    // PDF files stored as blobs
    pdfs: '++id, name, size, status, pageCount, uploadedAt',
    // Extracted text content per page
    extractedText: '++id, pdfId, pageNo, text',
});

/**
 * PDF file status enum
 */
export const FileStatus = {
    PENDING: 'pending',
    PROCESSING: 'processing',
    READY: 'ready',
    ERROR: 'error',
};

/**
 * Add a PDF file to the database
 * @param {File} file - The PDF file to add
 * @returns {Promise<number>} The ID of the added record
 */
export async function addPdfFile(file) {
    const arrayBuffer = await file.arrayBuffer();

    return db.pdfs.add({
        name: file.name,
        size: file.size,
        blob: arrayBuffer,
        status: FileStatus.PENDING,
        pageCount: 0,
        uploadedAt: new Date().toISOString(),
    });
}

/**
 * Update the status of a PDF file
 * @param {number} id - The PDF record ID
 * @param {string} status - The new status
 * @param {Object} [extra] - Additional fields to update
 */
export async function updatePdfStatus(id, status, extra = {}) {
    return db.pdfs.update(id, { status, ...extra });
}

/**
 * Get all PDF files
 * @returns {Promise<Array>}
 */
export async function getAllPdfs() {
    return db.pdfs.toArray();
}

/**
 * Get a PDF file by ID
 * @param {number} id
 * @returns {Promise<Object>}
 */
export async function getPdfById(id) {
    return db.pdfs.get(id);
}

/**
 * Delete a PDF and its extracted text
 * @param {number} id
 */
export async function deletePdf(id) {
    await db.extractedText.where('pdfId').equals(id).delete();
    await db.pdfs.delete(id);
}

/**
 * Store extracted text for a PDF page
 * @param {number} pdfId
 * @param {number} pageNo
 * @param {string} text
 */
export async function storeExtractedText(pdfId, pageNo, text) {
    return db.extractedText.add({ pdfId, pageNo, text });
}

/**
 * Get all extracted text for a PDF
 * @param {number} pdfId
 * @returns {Promise<Object>} Map of pageNo -> text
 */
export async function getExtractedTextForPdf(pdfId) {
    const records = await db.extractedText.where('pdfId').equals(pdfId).toArray();
    const textMap = {};
    for (const record of records) {
        textMap[record.pageNo] = record.text;
    }
    return textMap;
}

/**
 * Get all extracted text from all ready PDFs
 * @returns {Promise<Object>} Map of filename -> {pageNo: text}
 */
export async function getAllExtractedText() {
    const pdfs = await db.pdfs.where('status').equals(FileStatus.READY).toArray();
    const result = {};

    for (const pdf of pdfs) {
        result[pdf.name] = await getExtractedTextForPdf(pdf.id);
    }

    return result;
}

/**
 * Clear all data from the database
 */
export async function clearAllData() {
    await db.extractedText.clear();
    await db.pdfs.clear();
}

export default db;
