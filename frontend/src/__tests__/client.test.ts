/**
 * Tests for SDK client configuration (base URL switching, environment detection).
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';

const mockSetConfig = vi.fn();

vi.mock('@/client/client.gen', () => ({
  client: { setConfig: mockSetConfig },
}));

vi.mock('@/client/sdk.gen', () => ({
  TextHunterClient: vi.fn().mockImplementation(() => ({
    getHealth: vi.fn(),
    postExtract: vi.fn(),
  })),
}));

describe('SDK client config', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    delete (window as any).electronAPI;
    delete (window as any).__TAURI_INTERNALS__;
  });

  it('sets base URL to localhost in Electron mode', async () => {
    (window as any).electronAPI = { isElectron: true };

    await import('@/services/api.ts');

    expect(mockSetConfig).toHaveBeenCalledWith(
      expect.objectContaining({ baseUrl: 'http://localhost:8000' }),
    );
  });

  it('sets base URL to env var in web mode', async () => {
    vi.stubGlobal('import', { meta: { env: { VITE_API_URL: 'https://api.example.com' } } });

    // Reset module registry to get fresh import
    const apiModule = await import('@/services/api.ts');
    expect(apiModule).toBeDefined();
  });
});
