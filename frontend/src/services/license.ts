/**
 * License service for TextHunter desktop app.
 * Handles version validation to control distribution.
 */

import { api } from "@/services/api.ts";

export interface LicenseDetails {
  valid: boolean;
  local_version: string;
  latest_version: string;
  cached_at: string;
  expires_at: string;
  release_url?: string;
  release_name?: string;
}

export interface LicenseStatus {
  valid: boolean;
  message: string;
  cached?: boolean;
  offline?: boolean;
  details?: LicenseDetails;
}

/**
 * Check license validity with the backend.
 * The backend will check cache first, then GitHub API if needed.
 */
export async function checkLicense(): Promise<LicenseStatus> {
  const { data, error } = await api.getLicenseCheck();
  if (error) throw new Error(`HTTP error: ${error}`);
  return data as LicenseStatus;
}

/**
 * Clear cached license (useful for testing).
 */
export async function clearLicense(): Promise<void> {
  const { data, error } = await api.getLicenseClear();
  if (error) throw new Error(`HTTP error: ${error}`);
  return data as void;
}
