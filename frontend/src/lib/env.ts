/** Runtime environment helpers. */

export const isTauri =
  typeof window !== "undefined" &&
  !!(window as unknown as Record<string, unknown>).__TAURI_INTERNALS__;
