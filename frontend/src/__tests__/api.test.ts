/**
 * Tests for the API service layer (services/api.ts).
 * Mocks SDK client to verify the correct methods and payloads are used.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';

const mockPost = vi.fn();
const mockPostExport = vi.fn();
const mockGet = vi.fn();
const mockSetConfig = vi.fn();

// Mock the SDK client modules before any imports
vi.mock('@/client/client.gen', () => ({
  client: { setConfig: mockSetConfig },
}));

vi.mock('@/client/sdk.gen', () => ({
  TextHunterClient: vi.fn().mockImplementation(() => ({
    postExtract: mockPost,
    postExtractAll: mockPost,
    postGuessRegex: mockPost,
    postExport: mockPostExport,
    getHealth: mockGet,
    getLicenseCheck: mockGet,
    getLicenseClear: mockGet,
    postVisionRenderPage: mockPost,
    postVisionExtractLegend: mockPost,
    postVisionDetectSymbols: mockPost,
    postVisionExport: mockPostExport,
    postConfig: mockPost,
    getConfigs: mockGet,
    deleteConfig: mockPost,
  })),
}));

describe('API service', () => {
  let apiModule: typeof import('@/services/api.ts');

  beforeEach(async () => {
    vi.clearAllMocks();
    apiModule = await import('@/services/api.ts');
  });

  describe('extractMatches', () => {
    it('calls postExtract with the payload', async () => {
      const response = { matches: [], total_count: 0, preview_count: 0 };
      mockPost.mockResolvedValueOnce({ data: response, error: undefined });

      const payload = {
        filenames: ['file.pdf'],
        keyword_regex: '\\d+',
        text_content: { 'file.pdf': { 1: 'text' } },
        file_identifier_regex: null,
      };

      const result = await apiModule.extractMatches(payload);

      expect(mockPost).toHaveBeenCalledWith({ body: payload });
      expect(result).toEqual(response);
    });

    it('throws on error', async () => {
      mockPost.mockResolvedValueOnce({ data: undefined, error: 'HTTP 400: Invalid regex' });

      await expect(apiModule.extractMatches({ filenames: [], keyword_regex: '[bad', text_content: {} } as any))
        .rejects.toThrow('HTTP error: HTTP 400: Invalid regex');
    });
  });

  describe('guessRegex', () => {
    it('calls postGuessRegex with wrapped examples', async () => {
      const response = { pattern: '\\d+', explanation: 'digits', test_results: { '123': true } };
      mockPost.mockResolvedValueOnce({ data: response, error: undefined });

      const result = await apiModule.guessRegex(['123', '456']);

      expect(mockPost).toHaveBeenCalledWith({ body: { examples: ['123', '456'] } });
      expect(result).toEqual(response);
    });
  });

  describe('checkHealth', () => {
    it('calls getHealth', async () => {
      mockGet.mockResolvedValueOnce({ data: { status: 'healthy', timestamp: '2026-01-01' }, error: undefined });

      const result = await apiModule.checkHealth();

      expect(mockGet).toHaveBeenCalled();
      expect(result.status).toBe('healthy');
    });
  });

  describe('exportExcel', () => {
    it('uses native fetch for blob download', async () => {
      const mockFetch = vi.fn().mockResolvedValueOnce({
        ok: true,
        blob: async () => new Blob(['xlsx']),
        headers: new Headers({ 'content-disposition': 'attachment; filename=test.xlsx' }),
      });
      vi.stubGlobal('fetch', mockFetch);

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

      await apiModule.exportExcel([{ source_file: 'f.pdf', page: 1, match_found: 'X', context: '' }] as any);

      // Should use native fetch for blob, not SDK
      expect(mockGet).not.toHaveBeenCalledWith();
    });
  });
});
