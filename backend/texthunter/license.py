"""Version validation module for TextHunter desktop app.

Checks the local app version against the latest version from the external API.
If local version >= latest, access is granted. Otherwise, update is required.
"""

import json
import sys
from pathlib import Path

import requests

# API endpoint for version checking
VERSION_API_URL = "https://api.xergiz.com/text-hunter"

# Hardcoded version for frozen/pyinstaller builds
# Update this when creating a new build
FROZEN_VERSION = "0.7.0"


def get_local_version() -> tuple:
    """Get current app version from pyproject.toml or frozen constant."""
    if hasattr(sys, "frozen") and getattr(sys, "frozen", False):
        return parse_version(FROZEN_VERSION)

    import tomllib

    pyproject = Path(__file__).parent.parent / "pyproject.toml"
    try:
        with open(pyproject, "rb") as f:
            config = tomllib.load(f)
        version = config["project"]["version"]
        return parse_version(version)
    except FileNotFoundError:
        return parse_version(FROZEN_VERSION)


def parse_version(version_str: str) -> tuple:
    """Parse version string like '0.7.0' to (0, 7, 0)."""
    version = version_str.lstrip("v")
    try:
        return tuple(map(int, version.split(".")))
    except (ValueError, AttributeError):
        return (0, 0, 0)


def get_latest_version() -> tuple | None:
    """Fetch latest version from external API."""
    try:
        response = requests.get(VERSION_API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        version_str = data.get("version", "0.0.0")
        return parse_version(version_str)
    except (requests.RequestException, json.JSONDecodeError, KeyError):
        return None


def validate_license() -> dict:
    """Validate local version against the external API.

    Returns a LicenseStatus-compatible dict:
        - valid: bool
        - message: str
        - offline: bool
        - details: dict
    """
    local_version = get_local_version()
    local_version_str = ".".join(map(str, local_version))

    latest_version = get_latest_version()

    if latest_version is None:
        # Offline — allow access
        return {
            "valid": True,
            "message": f"Offline mode. v{local_version_str}",
            "offline": True,
            "details": {
                "valid": True,
                "local_version": local_version_str,
                "latest_version": None,
                "cached_at": "",
                "expires_at": "",
            },
        }

    latest_version_str = ".".join(map(str, latest_version))

    if local_version < latest_version:
        return {
            "valid": False,
            "message": f"Update required. Your version ({local_version_str}) is outdated. Please download v{latest_version_str}.",
            "offline": False,
            "details": {
                "valid": False,
                "local_version": local_version_str,
                "latest_version": latest_version_str,
                "cached_at": "",
                "expires_at": "",
            },
        }

    return {
        "valid": True,
        "message": f"v{local_version_str}",
        "offline": False,
        "details": {
            "valid": True,
            "local_version": local_version_str,
            "latest_version": latest_version_str,
            "cached_at": "",
            "expires_at": "",
        },
    }


def clear_license() -> dict:
    """Clear cached license state (for testing).

    Returns:
        dict with status message

    """
    return {"message": "License cache cleared", "status": "success"}
