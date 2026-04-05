"""Unified config storage for TextHunter.

Selects backend at startup based on environment:
  - SUPABASE_SERVICE_KEY set  →  SupabaseStorage (web deployment)
  - SUPABASE_SERVICE_KEY absent →  SQLiteStorage  (desktop sidecar)

Both classes expose the same async interface so routes are backend-agnostic.
"""

from __future__ import annotations

import logging
import os
import uuid
from pathlib import Path

import aiosqlite

logger = logging.getLogger(__name__)


def _get_db_path() -> Path:
    r"""Return the SQLite DB path.

    Desktop: %LOCALAPPDATA%\XergiZ\TextHunter\texthunter.db
    Fallback (non-Windows or missing env): ~/.texthunter/texthunter.db
    """
    local_appdata = os.environ.get("LOCALAPPDATA")
    if local_appdata:
        return Path(local_appdata) / "XergiZ" / "TextHunter" / "texthunter.db"
    return Path.home() / ".texthunter" / "texthunter.db"


def _get_desktop_user_id() -> str | None:
    """Get user_id for desktop mode from %USERNAME% environment variable."""
    return os.environ.get("USERNAME")


DB_PATH = _get_db_path()
MIGRATIONS_DIR = Path(__file__).parent.parent.parent / "migrations"


class SQLiteStorage:
    """Local SQLite storage — used by the desktop sidecar."""

    def __init__(self, db_path: Path = DB_PATH) -> None:
        """Initialize with path to SQLite database file."""
        self._db_path = db_path

    async def init(self) -> None:
        """Create tables and apply migrations."""
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS texthunter_configs (
                    id                    TEXT PRIMARY KEY,
                    user_id               TEXT,
                    name                  TEXT NOT NULL,
                    keyword_regex         TEXT NOT NULL,
                    file_identifier_regex TEXT,
                    created_at            TEXT NOT NULL DEFAULT (datetime('now')),
                    modified              TEXT NOT NULL DEFAULT (datetime('now')),
                    UNIQUE(user_id, name)
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS _migrations (
                    filename TEXT PRIMARY KEY,
                    applied_at TEXT NOT NULL DEFAULT (datetime('now'))
                )
            """)
            await db.commit()
        await self._apply_migrations()
        logger.info("SQLite DB initialised at %s", self._db_path)

    async def _apply_migrations(self) -> None:
        """Apply SQL migrations from migrations/ directory."""
        if not MIGRATIONS_DIR.exists():
            return

        sql_files = sorted(MIGRATIONS_DIR.glob("*.sql"))
        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            for sql_file in sql_files:
                async with db.execute(
                    "SELECT 1 FROM _migrations WHERE filename = ?", (sql_file.name,)
                ) as cursor:
                    row = await cursor.fetchone()
                    if row is not None:
                        logger.debug(
                            "Migration %s already applied, skipping", sql_file.name
                        )
                        continue

                logger.info("Applying migration %s", sql_file.name)
                with open(sql_file, "r") as f:
                    sql = f.read()
                await db.executescript(sql)
                await db.execute(
                    "INSERT INTO _migrations (filename) VALUES (?)", (sql_file.name,)
                )
                await db.commit()

    async def save_config(self, data: dict, user_id: str | None = None) -> str:
        """Save or update a config. Upserts by (user_id, name)."""
        # For desktop mode, get user_id from %USERNAME%
        if user_id is None:
            user_id = _get_desktop_user_id()

        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            query = "SELECT id FROM texthunter_configs WHERE name = ? AND user_id IS ?"
            async with db.execute(query, (data["name"], user_id)) as cursor:
                existing = await cursor.fetchone()

            if existing:
                await db.execute(
                    """UPDATE texthunter_configs
                       SET keyword_regex = ?, file_identifier_regex = ?,
                           modified = datetime('now')
                       WHERE id = ?""",
                    (
                        data["keyword_regex"],
                        data.get("file_identifier_regex"),
                        existing["id"],
                    ),
                )
                await db.commit()
                return existing["id"]

            new_id = str(uuid.uuid4())
            await db.execute(
                """INSERT INTO texthunter_configs
                   (id, user_id, name, keyword_regex, file_identifier_regex)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    new_id,
                    user_id,
                    data["name"],
                    data["keyword_regex"],
                    data.get("file_identifier_regex"),
                ),
            )
            await db.commit()
        return new_id

    async def get_configs(self, user_id: str | None = None) -> list[dict]:
        """List all configs for the given user (or all if user_id is None)."""
        # For desktop mode, get user_id from %USERNAME%
        if user_id is None:
            user_id = _get_desktop_user_id()

        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                """SELECT id, name, keyword_regex, file_identifier_regex,
                          created_at, modified
                   FROM texthunter_configs
                   WHERE user_id IS ?
                   ORDER BY name""",
                (user_id,),
            ) as cursor:
                rows = await cursor.fetchall()
        return [dict(r) for r in rows]

    async def delete_config(self, config_id: str, user_id: str | None = None) -> None:
        """Delete a config by id, scoped to user_id."""
        # For desktop mode, get user_id from %USERNAME%
        if user_id is None:
            user_id = _get_desktop_user_id()

        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                "DELETE FROM texthunter_configs WHERE id = ? AND user_id IS ?",
                (config_id, user_id),
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
        """Initialize Supabase client with URL and service key."""
        from supabase import create_client

        self._client = create_client(supabase_url, service_key)
        logger.info("SupabaseStorage initialised (url=%s)", supabase_url)

    async def init(self) -> None:
        """No-op — tables managed via migrations."""

    async def save_config(self, data: dict, user_id: str | None = None) -> str:
        """Save or update a config. Upserts by (user_id, name)."""
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
        """List all configs for the given user."""
        result = (
            self._client.table("texthunter_configs")
            .select("id,name,keyword_regex,file_identifier_regex,created_at,modified")
            .eq("user_id", user_id)
            .order("name")
            .execute()
        )
        return result.data

    async def delete_config(self, config_id: str, user_id: str | None = None) -> None:
        """Delete a config by id, scoped to user_id."""
        self._client.table("texthunter_configs").delete().eq("id", config_id).eq(
            "user_id", user_id
        ).execute()


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
