/**
 * Dexie.js database configuration for IndexedDB storage.
 * Stores PDF files and extracted text locally in the browser.
 */
import { Dexie, type EntityTable } from "dexie";

export interface PdfRecord {
  id?: number;
  name: string;
  size: number;
  blob: ArrayBuffer;
  status: string;
  pageCount: number;
  uploadedAt: string;
}

export interface ExtractedTextRecord {
  id?: number;
  pdfId: number;
  pageNo: number;
  text: string;
}

// Define the Database Class
class TextHunterDatabase extends Dexie {
  // We use EntityTable to link our Interfaces to the Table names
  pdfs!: EntityTable<PdfRecord, "id">;
  extractedText!: EntityTable<ExtractedTextRecord, "id">;

  constructor() {
    super("TextExtractorDB");
    this.version(1).stores({
      pdfs: "++id, name, status", // Only index fields you plan to filter by
      extractedText: "++id, pdfId",
    });
  }
}

export const db = new TextHunterDatabase();

/**
 * PDF file status enum
 */
export const FileStatus = {
  PENDING: "pending",
  PROCESSING: "processing",
  READY: "ready",
  ERROR: "error",
};

/**
 * Add a PDF file to the database
 * @param file - The PDF file to add
 * @returns The ID of the added record
 */
export async function addPdfFile(file: File): Promise<number> {
  const arrayBuffer = await file.arrayBuffer();

  return (await db.pdfs.add({
    name: file.name,
    size: file.size,
    blob: arrayBuffer,
    status: FileStatus.PENDING,
    pageCount: 0,
    uploadedAt: new Date().toISOString(),
  })) as number;
}

/**
 * Update the status of a PDF file
 * @param {number} id - The PDF record ID
 * @param {string} status - The new status
 * @param {Object} [extra] - Additional fields to update
 */
export async function updatePdfStatus(
  id: number,
  status: string,
  extra: object = {},
): Promise<number> {
  return (await db.pdfs.update(id, { status, ...extra })) as number;
}

/**
 * Get all PDF files
 * @returns List of all PDF records
 */
export async function getAllPdfs(): Promise<PdfRecord[]> {
  return db.pdfs.toArray();
}

/**
 * Get a PDF file by ID
 * @param id - The PDF record ID
 * @returns The PDF record or undefined if not found
 */
export async function getPdfById(id: number): Promise<PdfRecord | undefined> {
  return db.pdfs.get(id);
}

/**
 * Delete a PDF and its extracted text
 * @param {number} id
 */
export async function deletePdf(id: number): Promise<void> {
  await db.extractedText.where("pdfId").equals(id).delete();
  await db.pdfs.delete(id);
}

/**
 * Store extracted text for a PDF page
 * @param {number} pdfId
 * @param {number} pageNo
 * @param {string} text
 */
export async function storeExtractedText(
  pdfId: number,
  pageNo: number,
  text: string,
): Promise<number> {
  return (await db.extractedText.add({ pdfId, pageNo, text })) as number;
}

/**
 * Get all extracted text for a PDF
 * @param pdfId - The PDF record ID
 * @returns Map of page number to text content
 */
export async function getExtractedTextForPdf(
  pdfId: number,
): Promise<Record<number, string>> {
  const records = await db.extractedText.where("pdfId").equals(pdfId).toArray();
  const textMap: Record<number, string> = {};
  for (const record of records) {
    textMap[record.pageNo] = record.text;
  }
  return textMap;
}

/**
 * Get all extracted text from all ready PDFs
 * @returns Map of filename to extracted text by page number
 */
export async function getAllExtractedText(): Promise<
  Record<string, Record<number, string>>
> {
  const pdfs = await db.pdfs.where("status").equals(FileStatus.READY).toArray();
  const result: Record<string, Record<number, string>> = {};

  for (const pdf of pdfs) {
    if (pdf.id !== undefined) {
      result[pdf.name] = await getExtractedTextForPdf(pdf.id);
    }
  }

  return result;
}

/**
 * Clear all data from the database
 */
export async function clearAllData(): Promise<void> {
  await db.extractedText.clear();
  await db.pdfs.clear();
}

export default db;
