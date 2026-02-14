"""TextHunter API - FastAPI application for PDF text pattern extraction."""

import logging
import sys
from importlib.metadata import version

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from texthunter.api.routes import router
from texthunter.config.settings import CORS_ORIGINS

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)

# Set third-party loggers to WARNING to reduce noise
logging.getLogger("uvicorn").setLevel(logging.INFO)
logging.getLogger("uvicorn.access").setLevel(logging.INFO)
logging.getLogger("watchfiles").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="TextHunter API",
    description="Hunt and extract text patterns from PDF documents",
    version=version("texthunter"),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)

logger.info("TextHunter API initialized")


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint with API info."""
    logger.debug("Root endpoint accessed")
    return {
        "name": "TextHunter API",
        "version": version("texthunter"),
        "docs": "/docs",
    }


def run_server() -> None:
    """Run the TextHunter API server."""
    uvicorn.run("texthunter.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    run_server()
