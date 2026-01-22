/**
 * API service layer for communicating with the FastAPI backend.
 */
import axios from "axios";
import type { components } from "@/types/api.ts";

type Schemas = components["schemas"];

// Base URL: localhost for dev, api.xergiz.com for production
const API_BASE_URL = import.meta.env.DEV
  ? "http://localhost:8000"
  : "https://api.xergiz.com/text-hunter";

const api = axios.create({
  baseURL: `${API_BASE_URL}`,
  headers: {
    "Content-Type": "application/json",
  },
});

console.log(API_BASE_URL);

/**
 * Extract matches from text content using regex patterns.
 * @param payload - The extraction request payload
 * @param payload.filenames - List of PDF filenames
 * @param payload.keyword_regex - Regex pattern to match
 * @param payload.file_identifier_regex - Optional regex for filename metadata
 * @param payload.text_content - Map of filename -> {page: text}
 */
export async function extractMatches(payload:Schemas["ExtractionRequest"]): Promise<Schemas["ExtractionResponse"]> {
  const response = await api.post("/extract", payload);
  return response.data;
}

/**
 * Extract all matches (not just preview).
 * @param payload - Same as extractMatches
 */
export async function extractAllMatches(
  payload: Schemas["ExtractionRequest"],
): Promise<Schemas["ExtractionResponse"]> {
  const response = await api.post("/extract-all", payload);
  return response.data;
}

/**
 * Generate a regex pattern from example strings.
 * @param examples - At least 2 example strings
 */
export async function guessRegex(
  examples: Schemas["RegexGuessRequest"]["examples"],
): Promise<Schemas["RegexGuessResponse"]> {
  const response = await api.post("/guess-regex", { examples });
  return response.data;
}

/**
 * Export matches to Excel file.
 * @param matches - List of match results
 * @param includeContext - Whether to include context column
 */
export async function exportExcel(
  matches: Schemas["MatchResult"][],
  includeContext = true,
): Promise<Blob> {
  const response = await api.post(
    "/export",
    { matches, include_context: includeContext },
    { responseType: "blob" },
  );

  // Extract filename from Content-Disposition header
  const contentDisposition = response.headers["content-disposition"];
  let filename = "extraction_results.xlsx";
  if (contentDisposition) {
    const match = contentDisposition.match(/filename=(.+)/);
    if (match) {
      filename = match[1];
    }
  }

  // Trigger download
  const url = window.URL.createObjectURL(response.data);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);

  return response.data;
}

/**
 * Check backend health status.
 */
export async function checkHealth(): Promise<{
  status: string;
  timestamp: string;
}> {
  const response = await api.get("/health");
  return response.data;
}

export default api;
