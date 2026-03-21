/**
 * License service for TextHunter desktop app.
 * Handles version validation to control distribution.
 */

import httpClient from "@/api/client.ts";

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
  return httpClient.get<LicenseStatus>("/v1/license/check");
}

/**
 * Clear cached license (useful for testing).
 */
export async function clearLicense(): Promise<void> {
  return httpClient.get("/v1/license/clear");
}
