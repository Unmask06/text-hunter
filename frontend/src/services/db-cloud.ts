/**
 * Persistent storage service for TextHunter configs.
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

export interface Config {
  id?: string;
  name: string;
  keyword_regex: string;
  file_identifier_regex?: string | null;
  created_at?: string;
  modified?: string;
}

// ---------------------------------------------------------------------------
// Configs
// ---------------------------------------------------------------------------

/** Save or update a named regex config (upsert by name). */
export async function saveConfig(
  data: Omit<Config, "id" | "created_at" | "modified">,
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
