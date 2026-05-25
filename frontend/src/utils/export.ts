/**
 * Export utility for TextHunter web app.
 * Handles downloading files in browser environments.
 */

/**
 * Open a file URL in browser (web-only, uses window.open).
 * @param url - The URL to open
 */
export function openFile(url: string): void {
  window.open(url, "_blank");
}

/**
 * Export matches to Excel file.
 * Triggers a browser download.
 *
 * @param blob - The Excel file as a Blob
 * @param filename - The filename to use
 */
export async function exportExcelFile(blob: Blob, filename: string): Promise<void> {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}
