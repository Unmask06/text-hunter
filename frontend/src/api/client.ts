/**
 * Simple HTTP client using Tauri's fetch for desktop compatibility.
 *
 * URL configuration by environment:
 * - Desktop (Tauri): http://localhost:8000 (sidecar)
 * - Dev (vite): /api (proxied to localhost:8000)
 * - Production: https://api.xergiz.com/text-hunter
 */
import { fetch as tauriFetch } from '@tauri-apps/plugin-http';

export const isTauri = typeof window !== 'undefined' && (window as any).__TAURI_INTERNALS__ !== undefined;

const getBaseUrl = (): string => {
  if (isTauri) {
    return 'http://localhost:8000';
  }
  return import.meta.env.VITE_API_URL || '/api';
};

const BASE_URL = getBaseUrl();

const httpFetch = isTauri ? tauriFetch : window.fetch.bind(window);

function isRetryable(error: unknown): boolean {
  if (!(error instanceof Error)) return false;
  const msg = error.message.toLowerCase();
  return (
    msg.includes('network') ||
    msg.includes('failed to fetch') ||
    msg.includes('connection refused') ||
    msg.includes('econnrefused') ||
    msg.includes('load failed')
  );
}

async function withRetry<T>(fn: () => Promise<T>, maxRetries = 3): Promise<T> {
  let lastError: unknown;
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;
      if (!isRetryable(error) || attempt === maxRetries) break;
      const delay = Math.pow(2, attempt) * 500;
      await new Promise((resolve) => setTimeout(resolve, delay));
    }
  }
  throw lastError;
}

export const httpClient = {
  async get<T>(endpoint: string): Promise<T> {
    const url = \\\\;
    return withRetry(async () => {
      const response = await httpFetch(url, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });
      if (!response.ok) {
        throw new Error(\HTTP \: \\);
      }
      return response.json() as T;
    });
  },

  async post<T>(endpoint: string, data?: unknown): Promise<T> {
    const url = \\\\;
    return withRetry(async () => {
      const response = await httpFetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: data ? JSON.stringify(data) : null,
      });
      if (!response.ok) {
        throw new Error(\HTTP \: \\);
      }
      return response.json() as T;
    });
  },

  async postBlob(endpoint: string, data?: unknown): Promise<{ blob: Blob; filename: string }> {
    const url = \\\\;
    return withRetry(async () => {
      const response = await httpFetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: data ? JSON.stringify(data) : null,
      });
      if (!response.ok) {
        throw new Error(\HTTP \: \\);
      }
      let filename = 'extraction_results.xlsx';
      const contentDisposition = response.headers.get('content-disposition');
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

  async delete(endpoint: string): Promise<void> {
    const url = \\\\;
    const response = await httpFetch(url, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
    });
    if (!response.ok && response.status !== 204) {
      throw new Error(\HTTP \: \\);
    }
  },
};

export default httpClient;
