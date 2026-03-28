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
): Promise<string | null> {
  const { blob, filename } = await httpClient.postBlob("/export", { matches, include_context: includeContext });

  // Use desktop/web export utility
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
  return httpClient.get<{ status: string; timestamp: string }>("/health");
}

export default httpClient;
