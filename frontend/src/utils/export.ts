/**
 * Export utility for TextHunter desktop app.
 * Handles saving files to Downloads folder and opening files with default application.
 */

import { isTauri } from "@/api/client.ts";
import { path } from "@tauri-apps/api";
import { writeFile } from "@tauri-apps/plugin-fs";
import { open } from "@tauri-apps/plugin-shell";

/** @deprecated Use isTauri from @/api/client.ts directly */
export const isDesktop = isTauri;

/**
 * Save a blob to the Downloads folder.
 * @param filename - Name of the file to save
 * @param blob - The file content as a Blob
 * @returns Full path to the saved file
 */
export async function saveToDownloads(filename: string, blob: Blob): Promise<string> {
  // Get the Downloads directory path
  const downloadPath = await path.join(await path.downloadDir(), filename);

  // Convert blob to Uint8Array for writing
  const data = new Uint8Array(await blob.arrayBuffer());

  // Write the file to Downloads
  await writeFile(downloadPath, data);

  return downloadPath;
}

/**
 * Open a file with the default application.
 * @param filePath - Full path to the file to open
 */
export async function openFile(filePath: string): Promise<void> {
  await open(filePath);
}

/**
 * Export matches to Excel file.
 * On desktop: saves to Downloads folder and returns file path
 * On web: triggers browser download
 *
 * @param blob - The Excel file as a Blob
 * @param filename - The filename to use
 * @returns File path if desktop, null if web
 */
export async function exportExcelFile(blob: Blob, filename: string): Promise<string | null> {
  if (isTauri) {
    // Desktop: save directly to Downloads folder
    return saveToDownloads(filename, blob);
  } else {
    // Web: trigger browser download
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
}
