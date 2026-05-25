/**
 * Export utility for TextHunter desktop app.
 * Handles downloading files in browser and desktop environments.
 */

const isElectron = typeof window !== 'undefined' &&
  window.electronAPI !== undefined &&
  window.electronAPI.isElectron === true;

/**
 * Open a file URL in browser (web-only, uses window.open).
 * @param url - The URL to open
 */
export function openFile(url: string): void {
  window.open(url, "_blank");
}

/**
 * Export matches to Excel file.
 * On desktop: triggers browser download via blob URL
 * On web: triggers browser download via blob URL
 *
 * @param blob - The Excel file as a Blob
 * @param filename - The filename to use
 * @returns null (always, for API compatibility)
 */
export async function exportExcelFile(blob: Blob, filename: string): Promise<string | null> {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
  return null;
}
