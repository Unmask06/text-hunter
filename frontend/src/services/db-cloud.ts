/**
 * Cloud DB service — Supabase persistence for web mode.
 *
 * All functions silently no-op on desktop (Tauri), where
 * local IndexedDB (Dexie) is the sole storage layer.
 *
 * Tables (Supabase):
 *   texthunter_extractions — saved extraction runs
 *   texthunter_configs     — saved regex configurations
 */
import { supabase, isTauri } from "@/lib/supabase";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface CloudExtraction {
  id?: string;
  name?: string;
  keyword_regex: string;
  file_identifier_regex?: string | null;
  file_count: number;
  match_count: number;
  results: unknown[]; // array of MatchResult objects
  created_at?: string;
}

export interface CloudConfig {
  id?: string;
  name: string;
  keyword_regex: string;
  file_identifier_regex?: string | null;
  created_at?: string;
}

// ---------------------------------------------------------------------------
// Extractions
// ---------------------------------------------------------------------------

/** Save an extraction run to the cloud. No-op on desktop. */
export async function saveExtraction(
  data: Omit<CloudExtraction, "id" | "created_at">,
): Promise<string | null> {
  if (isTauri || !supabase) return null;

  const { data: row, error } = await supabase
    .from("texthunter_extractions")
    .insert(data)
    .select("id")
    .single();

  if (error) {
    console.error("saveExtraction error:", error.message);
    return null;
  }
  return row.id as string;
}

/** Load the user's extraction history. Returns [] on desktop. */
export async function getExtractions(): Promise<CloudExtraction[]> {
  if (isTauri || !supabase) return [];

  const { data, error } = await supabase
    .from("texthunter_extractions")
    .select("id, name, keyword_regex, file_identifier_regex, file_count, match_count, created_at")
    .order("created_at", { ascending: false })
    .limit(50);

  if (error) {
    console.error("getExtractions error:", error.message);
    return [];
  }
  return data as CloudExtraction[];
}

/** Load a single extraction's full results by id. */
export async function getExtractionById(
  id: string,
): Promise<CloudExtraction | null> {
  if (isTauri || !supabase) return null;

  const { data, error } = await supabase
    .from("texthunter_extractions")
    .select("*")
    .eq("id", id)
    .single();

  if (error) {
    console.error("getExtractionById error:", error.message);
    return null;
  }
  return data as CloudExtraction;
}

/** Delete an extraction run. */
export async function deleteExtraction(id: string): Promise<void> {
  if (isTauri || !supabase) return;

  const { error } = await supabase
    .from("texthunter_extractions")
    .delete()
    .eq("id", id);

  if (error) console.error("deleteExtraction error:", error.message);
}

// ---------------------------------------------------------------------------
// Configs
// ---------------------------------------------------------------------------

/** Save or update a named regex config. No-op on desktop. */
export async function saveConfig(
  data: Omit<CloudConfig, "id" | "created_at">,
): Promise<string | null> {
  if (isTauri || !supabase) return null;

  const { data: row, error } = await supabase
    .from("texthunter_configs")
    .upsert(data, { onConflict: "user_id,name" })
    .select("id")
    .single();

  if (error) {
    console.error("saveConfig error:", error.message);
    return null;
  }
  return row.id as string;
}

/** Load all saved configs for the current user. Returns [] on desktop. */
export async function getConfigs(): Promise<CloudConfig[]> {
  if (isTauri || !supabase) return [];

  const { data, error } = await supabase
    .from("texthunter_configs")
    .select("id, name, keyword_regex, file_identifier_regex, created_at")
    .order("name");

  if (error) {
    console.error("getConfigs error:", error.message);
    return [];
  }
  return data as CloudConfig[];
}

/** Delete a saved config by id. */
export async function deleteConfig(id: string): Promise<void> {
  if (isTauri || !supabase) return;

  const { error } = await supabase
    .from("texthunter_configs")
    .delete()
    .eq("id", id);

  if (error) console.error("deleteConfig error:", error.message);
}
