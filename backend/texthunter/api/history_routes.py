"""History API routes — extraction runs and saved regex configs.

Auth is optional:
  - Desktop sidecar: no Authorization header → user_id = None → SQLite
  - Web deployment:  Authorization: Bearer <token> → user_id extracted → Supabase
"""

import logging
import os
from typing import Any

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from texthunter.core.history import get_storage

logger = logging.getLogger(__name__)

history_router = APIRouter(tags=["history"])

_JWT_SECRET = os.environ.get("SUPABASE_JWT_SECRET", "")


async def _get_user_id(authorization: str | None = Header(default=None)) -> str | None:
    """Extract user_id from Supabase Bearer token if present.

    Returns None for desktop mode (no Authorization header).
    Raises 401 if a token is supplied but invalid.
    """
    if not authorization:
        return None  # desktop — no auth required

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization must be Bearer token")

    if not _JWT_SECRET:
        logger.warning("SUPABASE_JWT_SECRET not configured — skipping JWT verification")
        return None

    from jose import JWTError, jwt

    token = authorization[len("Bearer "):]
    try:
        payload = jwt.decode(token, _JWT_SECRET, algorithms=["HS256"], audience="authenticated")
        return payload.get("sub")
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from exc


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------


class ExtractionCreate(BaseModel):
    name: str | None = None
    keyword_regex: str
    file_identifier_regex: str | None = None
    file_count: int = 0
    match_count: int = 0
    results: list[Any] = []


class ConfigCreate(BaseModel):
    name: str
    keyword_regex: str
    file_identifier_regex: str | None = None


# ---------------------------------------------------------------------------
# Extraction routes
# ---------------------------------------------------------------------------


@history_router.post("/extractions")
async def save_extraction(
    payload: ExtractionCreate,
    authorization: str | None = Header(default=None),
):
    user_id = await _get_user_id(authorization)
    new_id = await get_storage().save_extraction(payload.model_dump(), user_id=user_id)
    return {"id": new_id}


@history_router.get("/extractions")
async def list_extractions(authorization: str | None = Header(default=None)):
    user_id = await _get_user_id(authorization)
    return await get_storage().get_extractions(user_id=user_id)


@history_router.get("/extractions/{extraction_id}")
async def get_extraction(
    extraction_id: str,
    authorization: str | None = Header(default=None),
):
    user_id = await _get_user_id(authorization)
    row = await get_storage().get_extraction_by_id(extraction_id, user_id=user_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Extraction not found")
    return row


@history_router.delete("/extractions/{extraction_id}", status_code=204)
async def delete_extraction(
    extraction_id: str,
    authorization: str | None = Header(default=None),
):
    user_id = await _get_user_id(authorization)
    await get_storage().delete_extraction(extraction_id, user_id=user_id)


# ---------------------------------------------------------------------------
# Config routes
# ---------------------------------------------------------------------------


@history_router.post("/configs")
async def save_config(
    payload: ConfigCreate,
    authorization: str | None = Header(default=None),
):
    user_id = await _get_user_id(authorization)
    new_id = await get_storage().save_config(payload.model_dump(), user_id=user_id)
    return {"id": new_id}


@history_router.get("/configs")
async def list_configs(authorization: str | None = Header(default=None)):
    user_id = await _get_user_id(authorization)
    return await get_storage().get_configs(user_id=user_id)


@history_router.delete("/configs/{config_id}", status_code=204)
async def delete_config(
    config_id: str,
    authorization: str | None = Header(default=None),
):
    user_id = await _get_user_id(authorization)
    await get_storage().delete_config(config_id, user_id=user_id)
