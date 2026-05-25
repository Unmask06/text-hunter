/**
 * API service layer for communicating with the FastAPI backend.
 * Uses generated Hey API SDK for type-safe API calls.
 */
import { client } from "@/client/client.gen";
import { TextHunterClient } from "@/client/sdk.gen";
import type {
  ExtractionRequest,
  ExtractionResponse,
  RegexGuessRequest,
  RegexGuessResponse,
  ExportRequest,
  MatchResult,
  RenderPageRequest,
  RenderPageResponse,
  LegendExtractRequest,
  LegendExtractResponse,
  SymbolDetectRequest,
  SymbolDetectResponse,
  SymbolDetectionResult,
  SymbolTemplate,
  BoundingBox,
} from "@/client/types.gen";

// Initialize SDK client with environment-aware base URL
const getBaseUrl = (): string => {
  const isElectron = typeof window !== 'undefined' && 
    window.electronAPI !== undefined && 
    window.electronAPI.isElectron === true;

  if (isElectron) {
    return "http://localhost:8000";
  }

  return import.meta.env.VITE_API_URL || "/api";
};

client.setConfig({ baseUrl: getBaseUrl() });

const api = new TextHunterClient();

/**
 * Extract matches from text content using regex patterns.
 * @param payload - The extraction request payload
 */
export async function extractMatches(
  payload: ExtractionRequest,
): Promise<ExtractionResponse> {
  const { data, error } = await api.postExtract({ body: payload });
  if (error) throw new Error(`HTTP error: ${error}`);
  return data!;
}

/**
 * Extract all matches (not just preview).
 * @param payload - Same as extractMatches
 */
export async function extractAllMatches(
  payload: ExtractionRequest,
): Promise<ExtractionResponse> {
  const { data, error } = await api.postExtractAll({ body: payload });
  if (error) throw new Error(`HTTP error: ${error}`);
  return data!;
}

/**
 * Generate a regex pattern from example strings.
 * @param examples - At least 2 example strings
 */
export async function guessRegex(
  examples: RegexGuessRequest["examples"],
): Promise<RegexGuessResponse> {
  const { data, error } = await api.postGuessRegex({ body: { examples } });
  if (error) throw new Error(`HTTP error: ${error}`);
  return data!;
}

/**
 * Export matches to Excel file.
 * @param matches - List of match results
 * @param includeContext - Whether to include context column
 * @returns File path if desktop (saved to Downloads), null if web (browser download)
 */
export async function exportExcel(
  matches: MatchResult[],
  includeContext = true,
): Promise<string | null> {
  const response = await api.postExport({ body: { matches, include_context: includeContext } as ExportRequest });
  if (response.error) throw new Error(`HTTP error: ${response.error}`);
  
  const blob = response.data as unknown as Blob;
  const filename = "extraction_results.xlsx";

  const { exportExcelFile } = await import("@/utils/export.ts");
  return exportExcelFile(blob, filename);
}

/**
 * Check backend health status.
 */
export async function checkHealth(): Promise<{
  status: string;
  timestamp: string;
}> {
  const { data, error } = await api.getHealth();
  if (error) throw new Error(`HTTP error: ${error}`);
  return data as { status: string; timestamp: string };
}

// ---------------------------------------------------------------------------
// Vision API — P&ID symbol detection
// ---------------------------------------------------------------------------

/**
 * Render a single PDF page to a base64 PNG for the legend annotation canvas.
 */
export async function renderPdfPage(
  pdfB64: string,
  page = 1,
  dpi = 150,
): Promise<RenderPageResponse> {
  const { data, error } = await api.postVisionRenderPage({ body: { pdf_b64: pdfB64, page, dpi } as RenderPageRequest });
  if (error) throw new Error(`HTTP error: ${error}`);
  return data!;
}

/**
 * Extract symbol templates from a legend page image.
 * Pass bounding_boxes + symbol_names for manual annotation, or omit for auto-segmentation.
 */
export async function extractLegendTemplates(
  payload: LegendExtractRequest,
): Promise<LegendExtractResponse> {
  const { data, error } = await api.postVisionExtractLegend({ body: payload });
  if (error) throw new Error(`HTTP error: ${error}`);
  return data!;
}

/**
 * Detect symbols across all pages of a target P&ID PDF.
 */
export async function detectSymbols(
  payload: SymbolDetectRequest,
): Promise<SymbolDetectResponse> {
  const { data, error } = await api.postVisionDetectSymbols({ body: payload });
  if (error) throw new Error(`HTTP error: ${error}`);
  return data!;
}

/**
 * Export symbol detection results to Excel.
 */
export async function exportVisionResults(
  results: SymbolDetectionResult[],
): Promise<void> {
  const response = await api.postVisionExport({ body: { results } });
  if (response.error) throw new Error(`HTTP error: ${response.error}`);

  const blob = response.data as unknown as Blob;
  const filename = "symbol_detection_results.xlsx";

  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}

export { api, client };
export default api;
