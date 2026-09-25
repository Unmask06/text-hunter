"""Config API routes — saved regex configs."""

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from texthunter.core.history import get_storage

logger = logging.getLogger(__name__)

configs_router = APIRouter(tags=["configs"])


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
async def save_config(payload: ConfigCreate):
    """Save or update a named regex config."""
    storage = get_storage()
    new_id = await storage.save_config(payload.model_dump())
    config = await storage.get_config(new_id)
    if config is None:
        raise HTTPException(status_code=500, detail="Config saved but could not be retrieved")
    return config


@configs_router.get("/configs", response_model=list[ConfigResponse], operation_id="get_configs")
async def list_configs():
    """List all saved configs for the current user."""
    return await get_storage().get_configs()


@configs_router.delete("/configs/{config_id}", status_code=204, operation_id="delete_config")
async def delete_config(config_id: str):
    """Delete a saved config by id."""
    await get_storage().delete_config(config_id)
