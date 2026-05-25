/// <reference types="vite/client" />

interface Window {
  __TAURI_INTERNALS__?: unknown;
  electronAPI?: {
    isElectron: boolean;
    [key: string]: unknown;
  };
}
