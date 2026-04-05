/**
 * Persistent storage service for TextHunter.
 *
 * All calls go to the Python backend (/v1/history/*).
 * The backend transparently routes to SQLite (desktop) or
 * Supabase PostgreSQL (web) — the frontend never knows which.
 *
 * httpClient already sets the correct base URL per environment:
 *   Desktop → http://localhost:8000
 *   Web     → /api  or  https://api.xergiz.com/text-hunter
 */
import httpClient from "@/api/client";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface Extraction {
  id?: string;
  name?: string;
  keyword_regex: string;
  file_identifier_regex?: string | null;
  file_count: number;
  match_count: number;
  results?: unknown[];
  created_at?: string;
}

export interface Config {
  id?: string;
  name: string;
  keyword_regex: string;
  file_identifier_regex?: string | null;
  created_at?: string;
}

// ---------------------------------------------------------------------------
// Extractions
// ---------------------------------------------------------------------------

/** Save an extraction run. Returns the new id. */
export async function saveExtraction(
  data: Omit<Extraction, "id" | "created_at">,
): Promise<string | null> {
  try {
    const result = await httpClient.post<{ id: string }>(
      "/v1/history/extractions",
      data,
    );
    return result.id;
  } catch (e) {
    console.error("saveExtraction error:", e);
    return null;
  }
}

/** Load extraction history (last 50, without results array). */
export async function getExtractions(): Promise<Extraction[]> {
  try {
    return await httpClient.get<Extraction[]>("/v1/history/extractions");
  } catch (e) {
    console.error("getExtractions error:", e);
    return [];
  }
}

/** Load a single extraction with its full results. */
export async function getExtractionById(
  id: string,
): Promise<Extraction | null> {
  try {
    return await httpClient.get<Extraction>(`/v1/history/extractions/${id}`);
  } catch (e) {
    console.error("getExtractionById error:", e);
    return null;
  }
}

/** Delete an extraction run. */
export async function deleteExtraction(id: string): Promise<void> {
  try {
    await httpClient.delete(`/v1/history/extractions/${id}`);
  } catch (e) {
    console.error("deleteExtraction error:", e);
  }
}

// ---------------------------------------------------------------------------
// Configs
// ---------------------------------------------------------------------------

/** Save or update a named regex config (upsert by name). */
export async function saveConfig(
  data: Omit<Config, "id" | "created_at">,
): Promise<string | null> {
  try {
    const result = await httpClient.post<{ id: string }>(
      "/v1/history/configs",
      data,
    );
    return result.id;
  } catch (e) {
    console.error("saveConfig error:", e);
    return null;
  }
}

/** Load all saved regex configs. */
export async function getConfigs(): Promise<Config[]> {
  try {
    return await httpClient.get<Config[]>("/v1/history/configs");
  } catch (e) {
    console.error("getConfigs error:", e);
    return [];
  }
}

/** Delete a saved config by id. */
export async function deleteConfig(id: string): Promise<void> {
  try {
    await httpClient.delete(`/v1/history/configs/${id}`);
  } catch (e) {
    console.error("deleteConfig error:", e);
  }
}
