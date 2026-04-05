/**
 * Unified persistent storage service for TextHunter.
 *
 * Transparent routing based on runtime environment:
 *   Desktop (Tauri) → SQLite  via @tauri-apps/plugin-sql
 *   Web             → Supabase PostgreSQL
 *
 * All exported functions have identical signatures in both modes.
 * Callers never need to know which backend is active.
 *
 * Tables:
 *   texthunter_extractions — saved extraction runs
 *   texthunter_configs     — saved regex configurations
 */
import { supabase, isTauri } from "@/lib/supabase";

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
  results: unknown[]; // array of MatchResult objects
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
// SQLite initialisation (desktop only)
// ---------------------------------------------------------------------------

// eslint-disable-next-line @typescript-eslint/no-explicit-any
let _dbPromise: Promise<any> | null = null;

async function getDb() {
  if (!isTauri) return null;
  if (!_dbPromise) {
    _dbPromise = (async () => {
      const { default: Database } = await import("@tauri-apps/plugin-sql");
      const db = await Database.load("sqlite:texthunter.db");

      await db.execute(`
        CREATE TABLE IF NOT EXISTS texthunter_extractions (
          id                    TEXT PRIMARY KEY,
          name                  TEXT,
          keyword_regex         TEXT NOT NULL,
          file_identifier_regex TEXT,
          file_count            INTEGER NOT NULL DEFAULT 0,
          match_count           INTEGER NOT NULL DEFAULT 0,
          results               TEXT NOT NULL DEFAULT '[]',
          created_at            TEXT NOT NULL DEFAULT (datetime('now'))
        )
      `);

      await db.execute(`
        CREATE TABLE IF NOT EXISTS texthunter_configs (
          id                    TEXT PRIMARY KEY,
          name                  TEXT NOT NULL UNIQUE,
          keyword_regex         TEXT NOT NULL,
          file_identifier_regex TEXT,
          created_at            TEXT NOT NULL DEFAULT (datetime('now'))
        )
      `);

      return db;
    })();
  }
  return _dbPromise;
}

// ---------------------------------------------------------------------------
// Extractions
// ---------------------------------------------------------------------------

/** Save an extraction run. Routes to SQLite (desktop) or Supabase (web). */
export async function saveExtraction(
  data: Omit<Extraction, "id" | "created_at">,
): Promise<string | null> {
  // --- Desktop: SQLite ---
  if (isTauri) {
    const db = await getDb();
    if (!db) return null;
    const id = crypto.randomUUID();
    await db.execute(
      `INSERT INTO texthunter_extractions
         (id, name, keyword_regex, file_identifier_regex, file_count, match_count, results)
       VALUES ($1, $2, $3, $4, $5, $6, $7)`,
      [
        id,
        data.name ?? null,
        data.keyword_regex,
        data.file_identifier_regex ?? null,
        data.file_count,
        data.match_count,
        JSON.stringify(data.results),
      ],
    );
    return id;
  }

  // --- Web: Supabase ---
  if (!supabase) return null;
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

/** Load extraction history (last 50). */
export async function getExtractions(): Promise<Extraction[]> {
  // --- Desktop: SQLite ---
  if (isTauri) {
    const db = await getDb();
    if (!db) return [];
    const rows = await db.select<Extraction[]>(
      `SELECT id, name, keyword_regex, file_identifier_regex,
              file_count, match_count, created_at
       FROM texthunter_extractions
       ORDER BY created_at DESC LIMIT 50`,
    );
    return rows;
  }

  // --- Web: Supabase ---
  if (!supabase) return [];
  const { data, error } = await supabase
    .from("texthunter_extractions")
    .select(
      "id, name, keyword_regex, file_identifier_regex, file_count, match_count, created_at",
    )
    .order("created_at", { ascending: false })
    .limit(50);

  if (error) {
    console.error("getExtractions error:", error.message);
    return [];
  }
  return data as Extraction[];
}

/** Load a single extraction's full results by id. */
export async function getExtractionById(
  id: string,
): Promise<Extraction | null> {
  // --- Desktop: SQLite ---
  if (isTauri) {
    const db = await getDb();
    if (!db) return null;
    const rows = await db.select<Extraction[]>(
      `SELECT * FROM texthunter_extractions WHERE id = $1`,
      [id],
    );
    if (!rows.length) return null;
    const row = rows[0];
    // Parse results JSON string back to array
    return {
      ...row,
      results: typeof row.results === "string" ? JSON.parse(row.results) : row.results,
    };
  }

  // --- Web: Supabase ---
  if (!supabase) return null;
  const { data, error } = await supabase
    .from("texthunter_extractions")
    .select("*")
    .eq("id", id)
    .single();

  if (error) {
    console.error("getExtractionById error:", error.message);
    return null;
  }
  return data as Extraction;
}

/** Delete an extraction run by id. */
export async function deleteExtraction(id: string): Promise<void> {
  // --- Desktop: SQLite ---
  if (isTauri) {
    const db = await getDb();
    if (!db) return;
    await db.execute(
      `DELETE FROM texthunter_extractions WHERE id = $1`,
      [id],
    );
    return;
  }

  // --- Web: Supabase ---
  if (!supabase) return;
  const { error } = await supabase
    .from("texthunter_extractions")
    .delete()
    .eq("id", id);

  if (error) console.error("deleteExtraction error:", error.message);
}

// ---------------------------------------------------------------------------
// Configs
// ---------------------------------------------------------------------------

/** Save or update a named regex config (upsert by name). */
export async function saveConfig(
  data: Omit<Config, "id" | "created_at">,
): Promise<string | null> {
  // --- Desktop: SQLite ---
  if (isTauri) {
    const db = await getDb();
    if (!db) return null;
    // Check if name already exists to return its id; otherwise insert new
    const existing = await db.select<{ id: string }[]>(
      `SELECT id FROM texthunter_configs WHERE name = $1`,
      [data.name],
    );
    if (existing.length) {
      await db.execute(
        `UPDATE texthunter_configs
         SET keyword_regex = $1, file_identifier_regex = $2
         WHERE name = $3`,
        [data.keyword_regex, data.file_identifier_regex ?? null, data.name],
      );
      return existing[0].id;
    }
    const id = crypto.randomUUID();
    await db.execute(
      `INSERT INTO texthunter_configs (id, name, keyword_regex, file_identifier_regex)
       VALUES ($1, $2, $3, $4)`,
      [id, data.name, data.keyword_regex, data.file_identifier_regex ?? null],
    );
    return id;
  }

  // --- Web: Supabase ---
  if (!supabase) return null;
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

/** Load all saved configs. */
export async function getConfigs(): Promise<Config[]> {
  // --- Desktop: SQLite ---
  if (isTauri) {
    const db = await getDb();
    if (!db) return [];
    const rows = await db.select<Config[]>(
      `SELECT id, name, keyword_regex, file_identifier_regex, created_at
       FROM texthunter_configs
       ORDER BY name`,
    );
    return rows;
  }

  // --- Web: Supabase ---
  if (!supabase) return [];
  const { data, error } = await supabase
    .from("texthunter_configs")
    .select("id, name, keyword_regex, file_identifier_regex, created_at")
    .order("name");

  if (error) {
    console.error("getConfigs error:", error.message);
    return [];
  }
  return data as Config[];
}

/** Delete a saved config by id. */
export async function deleteConfig(id: string): Promise<void> {
  // --- Desktop: SQLite ---
  if (isTauri) {
    const db = await getDb();
    if (!db) return;
    await db.execute(`DELETE FROM texthunter_configs WHERE id = $1`, [id]);
    return;
  }

  // --- Web: Supabase ---
  if (!supabase) return;
  const { error } = await supabase
    .from("texthunter_configs")
    .delete()
    .eq("id", id);

  if (error) console.error("deleteConfig error:", error.message);
}
