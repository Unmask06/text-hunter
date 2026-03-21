"""TextHunter API - FastAPI application for PDF text pattern extraction."""

import asyncio
import logging
import os
import signal
import sys
import threading
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

# Fixed port for desktop app
PORT_API = 8000

server_instance = None

app = FastAPI(
    title="TextHunter API",
    description="Hunt and extract text patterns from PDF documents",
    version=version("texthunter"),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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


from texthunter.license import validate_license, clear_license

@app.get("/v1/connect")
async def connect() -> dict:
    """Connection endpoint for Tauri sidecar."""
    return {
        "message": f"Connected to TextHunter API on port {PORT_API}",
        "data": {
            "port": PORT_API,
            "pid": os.getpid(),
            "host": f"http://localhost:{PORT_API}",
        },
    }


@app.get("/v1/license/check")
async def check_license() -> dict:
    """Check and validate license against GitHub releases.

    Returns:
        dict with license validation status
    """
    return validate_license()


@app.get("/v1/license/clear")
async def clear_license_endpoint() -> dict:
    """Clear cached license (for testing).

    Returns:
        dict with status message
    """
    return clear_license()


def kill_process():
    """Force shutdown the sidecar process."""
    os.kill(os.getpid(), signal.SIGINT)


def start_api_server(**kwargs):
    """Start the API server programmatically."""
    global server_instance
    port = kwargs.get("port", PORT_API)
    try:
        if server_instance is None:
            logger.info(f"Starting API server on port {port}...")
            config = uvicorn.Config(app, host="localhost", port=port, log_level="info")
            server_instance = uvicorn.Server(config)
            asyncio.run(server_instance.serve())
        else:
            logger.error("Server instance already running")
    except Exception as e:
        logger.error(f"Error starting API server: {e}")


def stdin_loop():
    """Handle stdin for sidecar shutdown commands."""
    logger.info("Waiting for commands...")
    while True:
        user_input = sys.stdin.readline().strip()
        match user_input:
            case "sidecar shutdown":
                logger.info("Received 'sidecar shutdown' command")
                kill_process()
            case _:
                logger.info(f"Invalid command [{user_input}]. Try again.")


def start_input_thread():
    """Start stdin input loop in a separate thread."""
    try:
        input_thread = threading.Thread(target=stdin_loop)
        input_thread.daemon = True
        input_thread.start()
    except Exception as e:
        logger.error(f"Failed to start input handler: {e}")


def run_server() -> None:
    """Run the TextHunter API server."""
    uvicorn.run("texthunter.main:app", host="localhost", port=PORT_API, reload=False)


if __name__ == "__main__":
    start_input_thread()
    start_api_server()
