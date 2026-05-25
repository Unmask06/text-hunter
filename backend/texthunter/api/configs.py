"""Config API routes — saved regex configs.

Auth is optional:
  - Desktop sidecar: no Authorization header → user_id = None → SQLite
  - Web deployment:  Authorization: Bearer <token> → user_id extracted → Supabase
"""

import logging
import os

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from texthunter.core.history import get_storage

logger = logging.getLogger(__name__)

configs_router = APIRouter(tags=["configs"])

_JWT_SECRET = os.environ.get("SUPABASE_JWT_SECRET", "")


async def _get_user_id(authorization: str | None = Header(default=None)) -> str | None:
    """Extract user_id from Supabase Bearer token if present.

    Returns None for desktop mode (no Authorization header).
    Raises 401 if a token is supplied but invalid.
    """
    if not authorization:
        return None  # desktop — no auth required

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401, detail="Authorization must be Bearer token"
        )

    if not _JWT_SECRET:
        logger.error("SUPABASE_JWT_SECRET not configured but a Bearer token was received")
        raise HTTPException(
            status_code=500,
            detail="Server misconfiguration: JWT secret not set",
        )

    from jose import JWTError, jwt

    token = authorization[len("Bearer ") :]
    try:
        payload = jwt.decode(
            token, _JWT_SECRET, algorithms=["HS256"], audience="authenticated"
        )
        return payload.get("sub")
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from exc


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------


class ConfigCreate(BaseModel):
    """Request payload for creating or updating a config."""

    name: str
    keyword_regex: str
    file_identifier_regex: str | None = None


class ConfigResponse(BaseModel):
    """Response payload for a saved config."""

    id: str
    name: str
    keyword_regex: str
    file_identifier_regex: str | None = None
    created_at: str
    modified: str


# ---------------------------------------------------------------------------
# Config routes
# ---------------------------------------------------------------------------


@configs_router.post("/configs", response_model=ConfigResponse, operation_id="post_config")
async def save_config(
    payload: ConfigCreate,
    authorization: str | None = Header(default=None),
):
    """Save or update a named regex config."""
    user_id = await _get_user_id(authorization)
    storage = get_storage()
    new_id = await storage.save_config(payload.model_dump(), user_id=user_id)
    config = await storage.get_config(new_id)
    if config is None:
        raise HTTPException(status_code=500, detail="Config saved but could not be retrieved")
    return config


@configs_router.get("/configs", operation_id="get_configs")
async def list_configs(authorization: str | None = Header(default=None)):
    """List all saved configs for the current user."""
    user_id = await _get_user_id(authorization)
    return await get_storage().get_configs(user_id=user_id)


@configs_router.delete("/configs/{config_id}", status_code=204, operation_id="delete_config")
async def delete_config(
    config_id: str,
    authorization: str | None = Header(default=None),
):
    """Delete a saved config by id."""
    user_id = await _get_user_id(authorization)
    await get_storage().delete_config(config_id, user_id=user_id)
