/**
 * Simple HTTP client using native fetch for better Tauri compatibility.
 *
 * URL configuration by environment:
 * - Desktop (Tauri): http://localhost:8000 (sidecar)
 * - Dev (vite): /api (proxied to localhost:8000)
 * - Production: https://api.xergiz.com/text-hunter
 */

// Determine API base URL based on environment
const getBaseUrl = (): string => {
  // Check if running in Tauri desktop app
  const isTauri = typeof window !== 'undefined' && (window as any).__TAURI_INTERNALS__ !== undefined;

  if (isTauri) {
    // Desktop app: direct connection to Python sidecar
    return "http://localhost:8000";
  }

  // Web mode: use environment variable
  // - Dev: /api (proxied by Vite to localhost:8000)
  // - Production: https://api.xergiz.com/text-hunter
  return import.meta.env.VITE_API_URL || "/api";
};

const BASE_URL = getBaseUrl();

export const httpClient = {
  async get<T>(endpoint: string): Promise<T> {
    const url = `${BASE_URL}${endpoint}`;
    console.log(`GET ${url}`);
    const response = await fetch(url, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${await response.text()}`);
    }
    return response.json() as T;
  },

  async post<T>(endpoint: string, data?: unknown): Promise<T> {
    const url = `${BASE_URL}${endpoint}`;
    console.log(`POST ${url}`);
    const response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: data ? JSON.stringify(data) : null,
    });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${await response.text()}`);
    }
    return response.json() as T;
  },

  async postBlob(endpoint: string, data?: unknown): Promise<{ blob: Blob; filename: string }> {
    const url = `${BASE_URL}${endpoint}`;
    console.log(`POST ${url}`);
    const response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: data ? JSON.stringify(data) : null,
    });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${await response.text()}`);
    }

    // Extract filename from Content-Disposition header
    let filename = "extraction_results.xlsx";
    const contentDisposition = response.headers.get("content-disposition");
    if (contentDisposition) {
      const match = contentDisposition.match(/filename=(.+)/);
      if (match && match[1]) {
        filename = match[1];
      }
    }

    const blob = await response.blob();
    return { blob, filename };
  },
};

export default httpClient;

