"""
Unified history storage for TextHunter.

Selects backend at startup based on environment:
  - SUPABASE_SERVICE_KEY set  →  SupabaseStorage (web deployment)
  - SUPABASE_SERVICE_KEY absent →  SQLiteStorage  (desktop sidecar)

Both classes expose the same async interface so routes are backend-agnostic.
"""

from __future__ import annotations

import json
import logging
import os
import uuid
from pathlib import Path

import aiosqlite

logger = logging.getLogger(__name__)

# Reuse existing app-data directory (same location as license.json)
DB_PATH = Path.home() / ".texthunter" / "texthunter.db"

# ---------------------------------------------------------------------------
# SQLite backend
# ---------------------------------------------------------------------------

class SQLiteStorage:
    """Local SQLite storage — used by the desktop sidecar."""

    def __init__(self, db_path: Path = DB_PATH) -> None:
        self._db_path = db_path

    async def init(self) -> None:
        """Create tables if they don't exist."""
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute("""
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
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS texthunter_configs (
                    id                    TEXT PRIMARY KEY,
                    name                  TEXT NOT NULL UNIQUE,
                    keyword_regex         TEXT NOT NULL,
                    file_identifier_regex TEXT,
                    created_at            TEXT NOT NULL DEFAULT (datetime('now'))
                )
            """)
            await db.commit()
        logger.info("SQLite DB initialised at %s", self._db_path)

    # --- Extractions ---

    async def save_extraction(self, data: dict, user_id: str | None = None) -> str:
        new_id = str(uuid.uuid4())
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                """INSERT INTO texthunter_extractions
                   (id, name, keyword_regex, file_identifier_regex,
                    file_count, match_count, results)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    new_id,
                    data.get("name"),
                    data["keyword_regex"],
                    data.get("file_identifier_regex"),
                    data.get("file_count", 0),
                    data.get("match_count", 0),
                    json.dumps(data.get("results", [])),
                ),
            )
            await db.commit()
        return new_id

    async def get_extractions(self, user_id: str | None = None) -> list[dict]:
        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                """SELECT id, name, keyword_regex, file_identifier_regex,
                          file_count, match_count, created_at
                   FROM texthunter_extractions
                   ORDER BY created_at DESC LIMIT 50"""
            ) as cursor:
                rows = await cursor.fetchall()
        return [dict(r) for r in rows]

    async def get_extraction_by_id(self, extraction_id: str, user_id: str | None = None) -> dict | None:
        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM texthunter_extractions WHERE id = ?", (extraction_id,)
            ) as cursor:
                row = await cursor.fetchone()
        if row is None:
            return None
        result = dict(row)
        result["results"] = json.loads(result["results"])
        return result

    async def delete_extraction(self, extraction_id: str, user_id: str | None = None) -> None:
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                "DELETE FROM texthunter_extractions WHERE id = ?", (extraction_id,)
            )
            await db.commit()

    # --- Configs ---

    async def save_config(self, data: dict, user_id: str | None = None) -> str:
        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT id FROM texthunter_configs WHERE name = ?", (data["name"],)
            ) as cursor:
                existing = await cursor.fetchone()

            if existing:
                await db.execute(
                    """UPDATE texthunter_configs
                       SET keyword_regex = ?, file_identifier_regex = ?
                       WHERE name = ?""",
                    (data["keyword_regex"], data.get("file_identifier_regex"), data["name"]),
                )
                await db.commit()
                return existing["id"]

            new_id = str(uuid.uuid4())
            await db.execute(
                """INSERT INTO texthunter_configs
                   (id, name, keyword_regex, file_identifier_regex)
                   VALUES (?, ?, ?, ?)""",
                (new_id, data["name"], data["keyword_regex"], data.get("file_identifier_regex")),
            )
            await db.commit()
        return new_id

    async def get_configs(self, user_id: str | None = None) -> list[dict]:
        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                """SELECT id, name, keyword_regex, file_identifier_regex, created_at
                   FROM texthunter_configs ORDER BY name"""
            ) as cursor:
                rows = await cursor.fetchall()
        return [dict(r) for r in rows]

    async def delete_config(self, config_id: str, user_id: str | None = None) -> None:
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                "DELETE FROM texthunter_configs WHERE id = ?", (config_id,)
            )
            await db.commit()


# ---------------------------------------------------------------------------
# Supabase backend
# ---------------------------------------------------------------------------

class SupabaseStorage:
    """Server-side Supabase storage — used by the web deployment.

    Uses the service role key so it can write on behalf of any user.
    Every write/read is scoped explicitly by user_id.
    """

    def __init__(self, supabase_url: str, service_key: str) -> None:
        from supabase import create_client  # imported lazily — not installed on desktop
        self._client = create_client(supabase_url, service_key)
        logger.info("SupabaseStorage initialised (url=%s)", supabase_url)

    async def init(self) -> None:
        """No-op — tables managed via migrations."""

    # --- Extractions ---

    async def save_extraction(self, data: dict, user_id: str | None = None) -> str:
        payload = {
            "user_id": user_id,
            "name": data.get("name"),
            "keyword_regex": data["keyword_regex"],
            "file_identifier_regex": data.get("file_identifier_regex"),
            "file_count": data.get("file_count", 0),
            "match_count": data.get("match_count", 0),
            "results": data.get("results", []),
        }
        result = self._client.table("texthunter_extractions").insert(payload).execute()
        return result.data[0]["id"]

    async def get_extractions(self, user_id: str | None = None) -> list[dict]:
        result = (
            self._client.table("texthunter_extractions")
            .select("id,name,keyword_regex,file_identifier_regex,file_count,match_count,created_at")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(50)
            .execute()
        )
        return result.data

    async def get_extraction_by_id(self, extraction_id: str, user_id: str | None = None) -> dict | None:
        result = (
            self._client.table("texthunter_extractions")
            .select("*")
            .eq("id", extraction_id)
            .eq("user_id", user_id)
            .single()
            .execute()
        )
        return result.data

    async def delete_extraction(self, extraction_id: str, user_id: str | None = None) -> None:
        self._client.table("texthunter_extractions").delete().eq("id", extraction_id).eq("user_id", user_id).execute()

    # --- Configs ---

    async def save_config(self, data: dict, user_id: str | None = None) -> str:
        payload = {
            "user_id": user_id,
            "name": data["name"],
            "keyword_regex": data["keyword_regex"],
            "file_identifier_regex": data.get("file_identifier_regex"),
        }
        result = (
            self._client.table("texthunter_configs")
            .upsert(payload, on_conflict="user_id,name")
            .execute()
        )
        return result.data[0]["id"]

    async def get_configs(self, user_id: str | None = None) -> list[dict]:
        result = (
            self._client.table("texthunter_configs")
            .select("id,name,keyword_regex,file_identifier_regex,created_at")
            .eq("user_id", user_id)
            .order("name")
            .execute()
        )
        return result.data

    async def delete_config(self, config_id: str, user_id: str | None = None) -> None:
        self._client.table("texthunter_configs").delete().eq("id", config_id).eq("user_id", user_id).execute()


# ---------------------------------------------------------------------------
# Factory + module-level singleton
# ---------------------------------------------------------------------------

_storage: SQLiteStorage | SupabaseStorage | None = None


def get_storage() -> SQLiteStorage | SupabaseStorage:
    """Return the active storage backend (must call init_storage first)."""
    if _storage is None:
        raise RuntimeError("Storage not initialised — call init_storage() at startup")
    return _storage


async def init_storage() -> None:
    """Initialise the appropriate storage backend and run schema setup."""
    global _storage

    supabase_url = os.environ.get("SUPABASE_URL", "")
    service_key = os.environ.get("SUPABASE_SERVICE_KEY", "")

    if supabase_url and service_key:
        logger.info("Using Supabase storage backend")
        _storage = SupabaseStorage(supabase_url, service_key)
    else:
        logger.info("Using SQLite storage backend")
        _storage = SQLiteStorage()

    await _storage.init()
