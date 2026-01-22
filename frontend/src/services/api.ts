/**
 * API service layer for communicating with the FastAPI backend.
 */
import axios from "axios";

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
 * @param {Object} payload
 * @param {string[]} payload.filenames - List of PDF filenames
 * @param {string} payload.keyword_regex - Regex pattern to match
 * @param {string|null} payload.file_identifier_regex - Optional regex for filename metadata
 * @param {Object} payload.text_content - Map of filename -> {page: text}
 * @returns {Promise<{matches: Array, total_count: number, preview_count: number}>}
 */
export async function extractMatches(payload) {
  const response = await api.post("/extract", payload);
  return response.data;
}

/**
 * Extract all matches (not just preview).
 * @param {Object} payload - Same as extractMatches
 * @returns {Promise<{matches: Array, total_count: number}>}
 */
export async function extractAllMatches(payload) {
  const response = await api.post("/extract-all", payload);
  return response.data;
}

/**
 * Generate a regex pattern from example strings.
 * @param {string[]} examples - At least 2 example strings
 * @returns {Promise<{pattern: string, explanation: string, test_results: Object}>}
 */
export async function guessRegex(examples) {
  const response = await api.post("/guess-regex", { examples });
  return response.data;
}

/**
 * Export matches to Excel file.
 * @param {Array} matches - List of match results
 * @param {boolean} includeContext - Whether to include context column
 * @returns {Promise<Blob>} Excel file blob
 */
export async function exportExcel(matches, includeContext = true) {
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
 * @returns {Promise<{status: string, timestamp: string}>}
 */
export async function checkHealth() {
  const response = await api.get("/health");
  return response.data;
}

export default api;
