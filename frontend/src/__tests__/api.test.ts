/**
 * Tests for the API service layer (services/api.ts).
 * Mocks httpClient to verify the correct endpoints and payloads are used.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';

// Mock the HTTP client module
vi.mock('@/api/client.ts', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    postBlob: vi.fn(),
  },
}));

// Mock @tauri-apps/plugin-http to prevent import errors
vi.mock('@tauri-apps/plugin-http', () => ({ fetch: vi.fn() }));

describe('API service', () => {
  let mockClient: { get: ReturnType<typeof vi.fn>; post: ReturnType<typeof vi.fn>; postBlob: ReturnType<typeof vi.fn> };

  beforeEach(async () => {
    const clientModule = await import('@/api/client.ts');
    mockClient = clientModule.default as any;
    vi.clearAllMocks();
  });

  describe('extractMatches', () => {
    it('calls POST /extract with the payload', async () => {
      const response = { matches: [], total_count: 0, preview_count: 0 };
      mockClient.post.mockResolvedValueOnce(response);

      const { extractMatches } = await import('@/services/api.ts');
      const payload: any = {
        filenames: ['file.pdf'],
        keyword_regex: '\\d+',
        text_content: { 'file.pdf': { 1: 'text' } },
      };

      const result = await extractMatches(payload);

      expect(mockClient.post).toHaveBeenCalledWith('/extract', payload);
      expect(result).toEqual(response);
    });

    it('propagates errors from httpClient', async () => {
      mockClient.post.mockRejectedValueOnce(new Error('HTTP 400: Invalid regex'));

      const { extractMatches } = await import('@/services/api.ts');
      await expect(extractMatches({ filenames: [], keyword_regex: '[bad', text_content: {} } as any))
        .rejects.toThrow('HTTP 400: Invalid regex');
    });
  });

  describe('guessRegex', () => {
    it('calls POST /guess-regex with wrapped examples', async () => {
      const response = { pattern: '\\d+', explanation: 'digits', test_results: { '123': true } };
      mockClient.post.mockResolvedValueOnce(response);

      const { guessRegex } = await import('@/services/api.ts');
      const result = await guessRegex(['123', '456']);

      expect(mockClient.post).toHaveBeenCalledWith('/guess-regex', { examples: ['123', '456'] });
      expect(result).toEqual(response);
    });
  });

  describe('checkHealth', () => {
    it('calls GET /health', async () => {
      mockClient.get.mockResolvedValueOnce({ status: 'healthy', timestamp: '2026-01-01' });

      const { checkHealth } = await import('@/services/api.ts');
      const result = await checkHealth();

      expect(mockClient.get).toHaveBeenCalledWith('/health');
      expect(result.status).toBe('healthy');
    });
  });

  describe('exportExcel', () => {
    it('calls postBlob /export and triggers a download', async () => {
      const fakeBlob = new Blob(['xlsx']);
      mockClient.postBlob.mockResolvedValueOnce({ blob: fakeBlob, filename: 'out.xlsx' });

      // Stub DOM APIs used for the download trigger
      const createObjectURLSpy = vi.fn().mockReturnValue('blob:mock');
      const revokeObjectURLSpy = vi.fn();
      vi.stubGlobal('URL', { createObjectURL: createObjectURLSpy, revokeObjectURL: revokeObjectURLSpy });

      const clickSpy = vi.fn();
      vi.spyOn(document, 'createElement').mockReturnValueOnce({
        href: '',
        download: '',
        click: clickSpy,
      } as any);
      vi.spyOn(document.body, 'appendChild').mockImplementation(() => null as any);
      vi.spyOn(document.body, 'removeChild').mockImplementation(() => null as any);

      const { exportExcel } = await import('@/services/api.ts');
      await exportExcel([{ source_file: 'f.pdf', page: 1, match_found: 'X', context: '' }] as any);

      expect(mockClient.postBlob).toHaveBeenCalledWith('/export', {
        matches: expect.any(Array),
        include_context: true,
      });
      expect(clickSpy).toHaveBeenCalled();
    });
  });
});
