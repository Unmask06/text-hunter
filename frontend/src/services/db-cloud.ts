/**
 * Persistent storage service for TextHunter configs.
 *
 * All calls go to the Python backend (/v1/history/*).
 * The backend transparently routes to SQLite (desktop) or
 * Supabase PostgreSQL (web) — the frontend never knows which.
 *
 * Uses generated Hey API SDK for type-safe API calls.
 */
import { api } from "@/services/api";

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
    const { data: result, error } = await api.postConfig({ body: data });
    if (error) {
      console.error(`[db-cloud] saveConfig error: ${error}`);
      return null;
    }
    console.log(`[db-cloud] Saved config "${data.name}" with id: ${result!.id}`);
    return result!.id ?? null;
  } catch (e) {
    console.error("[db-cloud] saveConfig error:", e);
    console.warn("[db-cloud] Backend unreachable — config was NOT saved");
    return null;
  }
}

/** Load all saved regex configs. */
export async function getConfigs(): Promise<Config[]> {
  try {
    const { data, error } = await api.getConfigs();
    if (error) {
      console.error(`[db-cloud] getConfigs error: ${error}`);
      return [];
    }
    console.log(`[db-cloud] Loaded ${data!.length} configs from backend`);
    return data!;
  } catch (e) {
    console.error("[db-cloud] getConfigs error:", e);
    console.warn("[db-cloud] Backend unreachable — presets cannot be loaded");
    return [];
  }
}

/** Delete a saved config by id. */
export async function deleteConfig(id: string): Promise<void> {
  try {
    const { error } = await api.deleteConfig({ path: { config_id: id } });
    if (error) {
      console.error(`[db-cloud] deleteConfig error: ${error}`);
    }
  } catch (e) {
    console.error("[db-cloud] deleteConfig error:", e);
  }
}
