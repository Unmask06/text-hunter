/**
 * HTTP client for TextHunter.
 * 
 * URL configuration by environment:
 * - Desktop (Electron): http://localhost:8000 (sidecar)
 * - Dev (vite): /api (proxied to localhost:8000)
 * - Production: https://api.xergiz.com/text-hunter
 */

const getBaseUrl = (): string => {
  const isElectron = typeof window !== 'undefined' && 
    window.electronAPI !== undefined && 
    window.electronAPI.isElectron === true;

  if (isElectron) {
    return "http://localhost:8000";
  }

  return import.meta.env.VITE_API_URL || "/api";
};

const BASE_URL = getBaseUrl();

export const httpClient = {
  async get<T>(endpoint: string): Promise<T> {
    const url = `${BASE_URL}${endpoint}`;
    console.log(`GET ${url}`);
    try {
      const response = await fetch(url, {
        method: "GET",
        headers: { "Content-Type": "application/json" },
      });
      console.log(`Response status: ${response.status}`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${await response.text()}`);
      }
      return response.json() as T;
    } catch (error) {
      console.error(`HTTP GET error:`, error);
      throw error;
    }
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