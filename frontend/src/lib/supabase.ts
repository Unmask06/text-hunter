/**
 * Supabase client — web mode only.
 *
 * On desktop (Tauri) this module exports null; all DB operations
 * should no-op when isTauri is true.
 *
 * On web, text-hunter uses the SAME Supabase project as xergiz.com.
 * Because both run on the same domain, the user's Supabase session
 * (stored in localStorage by xergiz after OTP login) is automatically
 * available here — no second login required.
 */
import { createClient, type SupabaseClient } from "@supabase/supabase-js";

export const isTauri =
  typeof window !== "undefined" &&
  (window as unknown as Record<string, unknown>).__TAURI_INTERNALS__ !==
    undefined;

let _supabase: SupabaseClient | null = null;

if (!isTauri) {
  const url = import.meta.env.VITE_SUPABASE_URL as string;
  const key = import.meta.env.VITE_SUPABASE_ANON_KEY as string;

  if (url && key) {
    _supabase = createClient(url, key, {
      auth: { persistSession: true, autoRefreshToken: true },
    });
  } else {
    console.warn("Supabase env vars not set — cloud DB features disabled");
  }
}

export const supabase = _supabase;
