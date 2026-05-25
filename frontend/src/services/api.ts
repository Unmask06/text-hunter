/**
 * API service layer for communicating with the FastAPI backend.
 */
import httpClient from "@/api/client.ts";
import type { components } from "@/api/schema.ts";

type Schemas = components["schemas"];

/**
 * Extract matches from text content using regex patterns.
 * @param payload - The extraction request payload
 * @param payload.filenames - List of PDF filenames
 * @param payload.keyword_regex - Regex pattern to match
 * @param payload.file_identifier_regex - Optional regex for filename metadata
 * @param payload.text_content - Map of filename -> {page: text}
 */
export async function extractMatches(
  payload: Schemas["ExtractionRequest"],
): Promise<Schemas["ExtractionResponse"]> {
  return httpClient.post<Schemas["ExtractionResponse"]>("/extract", payload);
}

/**
 * Extract all matches (not just preview).
 * @param payload - Same as extractMatches
 */
export async function extractAllMatches(
  payload: Schemas["ExtractionRequest"],
): Promise<Schemas["ExtractionResponse"]> {
  return httpClient.post<Schemas["ExtractionResponse"]>("/extract-all", payload);
}

/**
 * Generate a regex pattern from example strings.
 * @param examples - At least 2 example strings
 */
export async function guessRegex(
  examples: Schemas["RegexGuessRequest"]["examples"],
): Promise<Schemas["RegexGuessResponse"]> {
  return httpClient.post<Schemas["RegexGuessResponse"]>("/guess-regex", { examples });
}

/**
 * Export matches to Excel file.
 * @param matches - List of match results
 * @param includeContext - Whether to include context column
 * @returns File path if desktop (saved to Downloads), null if web (browser download)
 */
export async function exportExcel(
  matches: Schemas["MatchResult"][],
  includeContext = true,
): Promise<void> {
  const { blob, filename } = await httpClient.postBlob("/export", { matches, include_context: includeContext });

  // Use web export utility
  const { exportExcelFile } = await import("@/utils/export.ts");
  await exportExcelFile(blob, filename);
}

/**
 * Check backend health status.
 */
export async function checkHealth(): Promise<{
  status: string;
  timestamp: string;
}> {
  return httpClient.get<{ status: string; timestamp: string }>("/health");
}

// ---------------------------------------------------------------------------
// Vision API — P&ID symbol detection
// ---------------------------------------------------------------------------

export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface SymbolTemplate {
  name: string;
  image_b64: string;
  source_legend_page?: number | null;
}

export interface LegendExtractRequest {
  image_b64: string;
  bounding_boxes?: BoundingBox[] | null;
  symbol_names?: string[] | null;
}

export interface LegendExtractResponse {
  templates: SymbolTemplate[];
  annotated_image_b64: string;
}

export interface RenderPageResponse {
  image_b64: string;
  page: number;
  width: number;
  height: number;
  total_pages: number;
}

export interface SymbolDetectRequest {
  pdf_b64: string;
  templates: SymbolTemplate[];
  dpi?: number;
  threshold?: number;
  scale_range?: [number, number];
  enable_rotation?: boolean;
  nearby_text_radius_px?: number;
  existing_text_content?: Record<string, Record<number, string>> | null;
}

export interface SymbolDetectionResult {
  symbol_name: string;
  page: number;
  bbox: BoundingBox;
  confidence: number;
  associated_tags: string[];
  scale: number;
  angle_deg: number;
}

export interface SymbolDetectResponse {
  results: SymbolDetectionResult[];
  total_count: number;
  pages_processed: number;
  annotated_pages_b64: string[];
}

/**
 * Render a single PDF page to a base64 PNG for the legend annotation canvas.
 */
export async function renderPdfPage(
  pdfB64: string,
  page = 1,
  dpi = 150,
): Promise<RenderPageResponse> {
  return httpClient.post<RenderPageResponse>("/vision/render-page", {
    pdf_b64: pdfB64,
    page,
    dpi,
  });
}

/**
 * Extract symbol templates from a legend page image.
 * Pass bounding_boxes + symbol_names for manual annotation, or omit for auto-segmentation.
 */
export async function extractLegendTemplates(
  payload: LegendExtractRequest,
): Promise<LegendExtractResponse> {
  return httpClient.post<LegendExtractResponse>("/vision/extract-legend", payload);
}

/**
 * Detect symbols across all pages of a target P&ID PDF.
 */
export async function detectSymbols(
  payload: SymbolDetectRequest,
): Promise<SymbolDetectResponse> {
  return httpClient.post<SymbolDetectResponse>("/vision/detect-symbols", payload);
}

/**
 * Export symbol detection results to Excel.
 */
export async function exportVisionResults(
  results: SymbolDetectionResult[],
): Promise<void> {
  const { blob, filename } = await httpClient.postBlob("/vision/export", { results });

  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}

export default httpClient;
