"""License validation module for TextHunter desktop app.

This module handles version validation by checking against GitHub releases
to control distribution until a full licensing system is implemented.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

import requests
import tomli

# Configuration
LICENSE_FILE = Path.home() / ".texthunter" / "license.json"
CACHE_DURATION_DAYS = 7
GRACE_PERIOD_DAYS = 3
GITHUB_PAT = os.getenv("GITHUB_PAT", "")
REPO_OWNER = "Unmask06"
REPO_NAME = "text-hunter"


def get_cached_license() -> dict | None:
    """Load cached license if exists and not expired.

    Returns:
        dict with license data or None if not cached/expired
    """
    if not LICENSE_FILE.exists():
        return None

    try:
        with open(LICENSE_FILE) as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return None

    cached_at = datetime.fromisoformat(data.get("cached_at", ""))
    if datetime.now() - cached_at > timedelta(days=CACHE_DURATION_DAYS):
        return None  # Cache expired

    return data


def get_grace_period_license() -> dict | None:
    """Get license during grace period when offline.

    Returns:
        dict with license data or None if grace period expired
    """
    if not LICENSE_FILE.exists():
        return None

    try:
        with open(LICENSE_FILE) as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return None

    expires_at = datetime.fromisoformat(data.get("expires_at", ""))
    if not expires_at:
        return None

    grace_end = expires_at + timedelta(days=GRACE_PERIOD_DAYS)

    if datetime.now() <= grace_end:
        return data

    return None


def fetch_latest_release() -> dict:
    """Fetch latest release from GitHub API.

    Returns:
        dict with release information

    Raises:
        requests.RequestException: If API call fails
    """
    headers = {"Authorization": f"Bearer {GITHUB_PAT}"} if GITHUB_PAT else {}
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/latest"

    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    return response.json()


def parse_version(tag: str) -> tuple[int, int, int]:
    """Parse version tag like 'v0.7.0' to tuple (0, 7, 0).

    Args:
        tag: Version string from GitHub releases

    Returns:
        Tuple of (major, minor, patch) version numbers
    """
    version = tag.lstrip('v')
    parts = version.split('.')
    return (
        int(parts[0]) if len(parts) > 0 else 0,
        int(parts[1]) if len(parts) > 1 else 0,
        int(parts[2]) if len(parts) > 2 else 0,
    )


def get_local_version() -> tuple[int, int, int]:
    """Get current app version from pyproject.toml.

    Returns:
        Tuple of (major, minor, patch) version numbers
    """
    pyproject = Path(__file__).parent.parent / "pyproject.toml"
    with open(pyproject, "rb") as f:
        config = tomli.load(f)

    version_str = config["project"]["version"]
    return parse_version(version_str)


def save_license(data: dict) -> None:
    """Save license data to file.

    Args:
        data: License data to persist
    """
    LICENSE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LICENSE_FILE, "w") as f:
        json.dump(data, f, indent=2)


def validate_license() -> dict:
    """Validate license by checking GitHub releases.

    This function:
    1. Checks for cached license (valid for 7 days)
    2. If expired/missing, fetches latest release from GitHub
    3. Compares local version with latest release
    4. Caches result for future use
    5. Handles offline scenarios with grace period

    Returns:
        dict with keys:
            - valid: bool - whether license is valid
            - message: str - human readable status
            - cached: bool - whether result is from cache
            - offline: bool - whether operating in offline mode
            - details: dict - full license details
    """
    # Check cache first
    cached = get_cached_license()
    if cached and cached.get("valid"):
        return {
            "valid": True,
            "cached": True,
            "message": "License validated from cache",
            "details": cached
        }

    # Fetch latest release
    try:
        release = fetch_latest_release()
        latest_version = parse_version(release["tag_name"])
        current_version = get_local_version()

        # Compare versions: user must have >= latest release version
        is_valid = current_version >= latest_version

        # Build license data
        license_data = {
            "valid": is_valid,
            "local_version": ".".join(map(str, current_version)),
            "latest_version": ".".join(map(str, latest_version)),
            "cached_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(days=CACHE_DURATION_DAYS)).isoformat(),
            "release_url": release.get("html_url", ""),
            "release_name": release.get("name", "")
        }
        save_license(license_data)

        if not is_valid:
            return {
                "valid": False,
                "message": "Update required. Please download the latest version from GitHub releases.",
                "details": license_data
            }

        return {
            "valid": True,
            "message": "License validated successfully",
            "details": license_data
        }

    except requests.RequestException as e:
        # Offline - check grace period
        grace_license = get_grace_period_license()
        if grace_license and grace_license.get("valid"):
            return {
                "valid": True,
                "cached": True,
                "offline": True,
                "message": "Offline mode - using grace period",
                "details": grace_license
            }

        return {
            "valid": False,
            "offline": True,
            "message": f"Cannot validate license. Please check your internet connection. ({str(e)})"
        }
    except Exception as e:
        return {
            "valid": False,
            "message": f"License validation error: {str(e)}"
        }


def clear_license() -> dict:
    """Clear cached license file.

    Returns:
        dict with status message
    """
    if LICENSE_FILE.exists():
        try:
            LICENSE_FILE.unlink()
            return {"message": "License cleared successfully", "success": True}
        except OSError as e:
            return {"message": f"Failed to clear license: {str(e)}", "success": False}

    return {"message": "No license file found", "success": True}
