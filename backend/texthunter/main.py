"""TextHunter API - FastAPI application for PDF text pattern extraction."""

import logging
import sys
from importlib.metadata import version

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from texthunter.routes import router

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

# Allow CORS for Vue frontend (assuming runs on port 5173 by default)
origins: list[str] = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://xergiz.com",
    "https://www.xergiz.com",
    "https://api.xergiz.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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


def run_server(host: str = "0.0.0.0", port: int = 8000) -> None:
    """Run the TextHunter API server."""
    uvicorn.run("texthunter.main:app", host=host, port=port, reload=True)


if __name__ == "__main__":
    run_server()
