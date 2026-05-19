/**
 * Tests for the HTTP client (retry logic, error handling, environment detection).
 * The Tauri plugin import is mocked so tests run in jsdom without a Tauri runtime.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';

// Mock @tauri-apps/plugin-http before importing client
vi.mock('@tauri-apps/plugin-http', () => ({
  fetch: vi.fn(),
}));

// Mock import.meta.env
vi.stubGlobal('import', { meta: { env: { VITE_API_URL: '/api' } } });

describe('httpClient', () => {
  let mockFetch: ReturnType<typeof vi.fn>;

  beforeEach(async () => {
    vi.resetModules();
    // Ensure we're in web mode (no Tauri internals)
    delete (window as any).__TAURI_INTERNALS__;

    mockFetch = vi.fn();
    vi.stubGlobal('fetch', mockFetch);
  });

  describe('GET', () => {
    it('returns parsed JSON on success', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ status: 'healthy', timestamp: '2026-01-01' }),
      });

      const { httpClient } = await import('@/api/client.ts');
      const result = await httpClient.get('/health');
      expect(result).toEqual({ status: 'healthy', timestamp: '2026-01-01' });
    });

    it('throws on non-ok response', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        text: async () => 'Not Found',
      });

      const { httpClient } = await import('@/api/client.ts');
      await expect(httpClient.get('/missing')).rejects.toThrow('HTTP 404');
    });

    it('retries on network error and succeeds on second attempt', async () => {
      const networkError = new Error('Failed to fetch');
      mockFetch
        .mockRejectedValueOnce(networkError)
        .mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => ({ status: 'healthy' }),
        });

      const { httpClient } = await import('@/api/client.ts');
      const result = await httpClient.get('/health');
      expect(result).toEqual({ status: 'healthy' });
      expect(mockFetch).toHaveBeenCalledTimes(2);
    });

    it('does not retry on HTTP 4xx errors', async () => {
      mockFetch.mockResolvedValue({
        ok: false,
        status: 400,
        text: async () => 'Bad Request',
      });

      const { httpClient } = await import('@/api/client.ts');
      await expect(httpClient.get('/extract')).rejects.toThrow('HTTP 400');
      // Called only once — 4xx is not retryable
      expect(mockFetch).toHaveBeenCalledTimes(1);
    });

    it('throws after exhausting all retries', async () => {
      const networkError = new Error('connection refused');
      mockFetch.mockRejectedValue(networkError);

      const { httpClient } = await import('@/api/client.ts');
      await expect(httpClient.get('/health')).rejects.toThrow('connection refused');
      // Initial attempt + 3 retries = 4 calls
      expect(mockFetch).toHaveBeenCalledTimes(4);
    });
  });

  describe('POST', () => {
    it('sends JSON body and returns parsed response', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ matches: [], total_count: 0, preview_count: 0 }),
      });

      const { httpClient } = await import('@/api/client.ts');
      const result = await httpClient.post('/extract', { keyword_regex: '\\d+' });

      expect(result).toEqual({ matches: [], total_count: 0, preview_count: 0 });
      const callBody = JSON.parse((mockFetch.mock.calls[0] as any[])[1].body);
      expect(callBody.keyword_regex).toBe('\\d+');
    });

    it('throws on non-ok response', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 422,
        text: async () => 'Unprocessable Entity',
      });

      const { httpClient } = await import('@/api/client.ts');
      await expect(httpClient.post('/extract', {})).rejects.toThrow('HTTP 422');
    });
  });

  describe('postBlob', () => {
    it('extracts filename from Content-Disposition header', async () => {
      const fakeBlob = new Blob(['data'], { type: 'application/octet-stream' });
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        headers: {
          get: (name: string) =>
            name === 'content-disposition'
              ? 'attachment; filename=results_20260101.xlsx'
              : null,
        },
        blob: async () => fakeBlob,
      });

      const { httpClient } = await import('@/api/client.ts');
      const { blob, filename } = await httpClient.postBlob('/export', { matches: [] });

      expect(filename).toBe('results_20260101.xlsx');
      expect(blob).toBe(fakeBlob);
    });

    it('uses default filename when header is absent', async () => {
      const fakeBlob = new Blob(['data']);
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        headers: { get: () => null },
        blob: async () => fakeBlob,
      });

      const { httpClient } = await import('@/api/client.ts');
      const { filename } = await httpClient.postBlob('/export', {});
      expect(filename).toBe('extraction_results.xlsx');
    });
  });
});
