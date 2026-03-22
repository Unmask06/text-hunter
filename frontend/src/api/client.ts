/**
 * Simple HTTP client using Tauri's fetch for desktop compatibility.
 *
 * URL configuration by environment:
 * - Desktop (Tauri): http://localhost:8000 (sidecar)
 * - Dev (vite): /api (proxied to localhost:8000)
 * - Production: https://api.xergiz.com/text-hunter
 */
import { fetch as tauriFetch } from '@tauri-apps/plugin-http';

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

// Use Tauri fetch in desktop app, native fetch in web
const useTauriFetch = typeof window !== 'undefined' && (window as any).__TAURI_INTERNALS__ !== undefined;
const httpFetch = useTauriFetch ? tauriFetch : window.fetch.bind(window);

/** Returns true for network-level errors that are worth retrying. */
function isRetryable(error: unknown): boolean {
  if (!(error instanceof Error)) return false;
  // Network errors (no connection, DNS failure, sidecar not ready yet)
  const msg = error.message.toLowerCase();
  return (
    msg.includes('network') ||
    msg.includes('failed to fetch') ||
    msg.includes('connection refused') ||
    msg.includes('econnrefused') ||
    msg.includes('load failed')
  );
}

/** Retry a fetch call up to maxRetries times with exponential backoff. */
async function withRetry<T>(fn: () => Promise<T>, maxRetries = 3): Promise<T> {
  let lastError: unknown;
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;
      if (!isRetryable(error) || attempt === maxRetries) break;
      const delay = Math.pow(2, attempt) * 500; // 500ms, 1s, 2s
      await new Promise((resolve) => setTimeout(resolve, delay));
    }
  }
  throw lastError;
}

export const httpClient = {
  async get<T>(endpoint: string): Promise<T> {
    const url = `${BASE_URL}${endpoint}`;
    console.log(`GET ${url}`);
    return withRetry(async () => {
      const response = await httpFetch(url, {
        method: "GET",
        headers: { "Content-Type": "application/json" },
      });
      console.log(`Response status: ${response.status}`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${await response.text()}`);
      }
      return response.json() as T;
    });
  },

  async post<T>(endpoint: string, data?: unknown): Promise<T> {
    const url = `${BASE_URL}${endpoint}`;
    console.log(`POST ${url}`);
    return withRetry(async () => {
      const response = await httpFetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: data ? JSON.stringify(data) : null,
      });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${await response.text()}`);
      }
      return response.json() as T;
    });
  },

  async postBlob(endpoint: string, data?: unknown): Promise<{ blob: Blob; filename: string }> {
    const url = `${BASE_URL}${endpoint}`;
    console.log(`POST ${url}`);
    return withRetry(async () => {
      const response = await httpFetch(url, {
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
    });
  },
};

export default httpClient;
