"""License validation module for TextHunter desktop app.

This module handles trial period validation and version checking.
Users get a 3-day trial from first launch, after which a new build is required.
Version is validated against the API to ensure users have the latest release.
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import requests

# Configuration
LICENSE_FILE = Path.home() / ".texthunter" / "license.json"
TRIAL_DURATION_DAYS = 3
VERSION_CACHE_FILE = Path.home() / ".texthunter" / "version_cache.json"

# API endpoint for version checking
VERSION_API_URL = "https://api.xergiz.com/text-hunter/"

# Build-specific seed to prevent simple trial reset
# Change this value when creating a new build to invalidate old trials
BUILD_SEED = "texthunter-build-0.7.0-20260321"

# Hardcoded version for frozen/pyinstaller builds
# This is the source of truth when pyproject.toml is not available
FROZEN_VERSION = "0.7.0"


def get_trial_start_date() -> datetime | None:
    """Get the trial start date from license file or None if not found.

    Returns:
        datetime of trial start or None if no trial has started
    """
    if not LICENSE_FILE.exists():
        return None

    try:
        with open(LICENSE_FILE) as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return None

    trial_start_str = data.get("trial_start")
    if not trial_start_str:
        return None

    return datetime.fromisoformat(trial_start_str)


def get_local_version() -> tuple:
    """Get current app version from pyproject.toml or frozen constant."""
    # In frozen builds (PyInstaller), pyproject.toml is not bundled
    # Check if running as a frozen application
    # PyInstaller sets sys._MEIPASS to the temp extraction folder
    if hasattr(sys, 'frozen') and getattr(sys, 'frozen', False):
        return parse_version(FROZEN_VERSION)

    # Use tomllib (Python 3.11+) instead of tomli to avoid mypyc cache issues
    import tomllib

    pyproject = Path(__file__).parent.parent / "pyproject.toml"
    try:
        with open(pyproject, "rb") as f:
            config = tomllib.load(f)

        version = config["project"]["version"]
        return parse_version(version)
    except FileNotFoundError:
        # Fallback to frozen version if pyproject.toml not found
        return parse_version(FROZEN_VERSION)


def parse_version(version_str: str) -> tuple:
    """Parse version string like '0.7.0' to (0, 7, 0)."""
    version = version_str.lstrip('v')
    try:
        return tuple(map(int, version.split('.')))
    except (ValueError, AttributeError):
        return (0, 0, 0)


def get_latest_version() -> tuple | None:
    """Fetch latest version from API."""
    try:
        response = requests.get(VERSION_API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        version_str = data.get("version", "0.0.0")
        return parse_version(version_str)
    except (requests.RequestException, json.JSONDecodeError, KeyError):
        return None


def save_version_cache(latest_version: tuple):
    """Cache the latest version locally."""
    VERSION_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    cache_data = {
        "latest_version": ".".join(map(str, latest_version)),
        "cached_at": datetime.now().isoformat(),
    }
    with open(VERSION_CACHE_FILE, "w") as f:
        json.dump(cache_data, f, indent=2)


def get_cached_version() -> tuple | None:
    """Get cached latest version if exists."""
    if not VERSION_CACHE_FILE.exists():
        return None
    try:
        with open(VERSION_CACHE_FILE) as f:
            data = json.load(f)
        version_str = data.get("latest_version", "")
        return parse_version(version_str)
    except (json.JSONDecodeError, OSError):
        return None


def start_trial() -> dict:
    """Start a new trial period.

    Creates the license file with the trial start date and build seed.

    Returns:
        dict with trial information
    """
    trial_start = datetime.now()
    trial_end = trial_start + timedelta(days=TRIAL_DURATION_DAYS)

    license_data = {
        "trial_start": trial_start.isoformat(),
        "trial_end": trial_end.isoformat(),
        "build_seed": BUILD_SEED,
        "created_at": datetime.now().isoformat(),
    }

    LICENSE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LICENSE_FILE, "w") as f:
        json.dump(license_data, f, indent=2)

    local_version = get_local_version()
    latest_version = get_latest_version()

    return {
        "valid": True,
        "trial_start": trial_start.strftime("%Y-%m-%d %H:%M"),
        "trial_end": trial_end.strftime("%Y-%m-%d %H:%M"),
        "days_remaining": TRIAL_DURATION_DAYS,
        "local_version": ".".join(map(str, local_version)),
        "latest_version": ".".join(map(str, latest_version)) if latest_version else "unknown",
        "message": f"Trial started. Expires in {TRIAL_DURATION_DAYS} days.",
    }


def validate_license() -> dict:
    """Validate the trial period and check version.

    Checks if:
    1. Trial exists and hasn't expired
    2. Build seed matches (prevents copying license from old builds)
    3. Local version >= latest version from API

    Returns:
        dict with keys:
            - valid: bool - whether trial is active and version is OK
            - message: str - human readable status
            - trial_expired: bool - specifically indicates trial expiration
            - version_mismatch: bool - local version is below latest
            - days_remaining: int - days left in trial
            - trial_end: str - formatted trial end date
    """
    # Check version first
    latest_version = get_latest_version()
    if latest_version:
        save_version_cache(latest_version)
    else:
        latest_version = get_cached_version()

    local_version = get_local_version()
    latest_version_str = ".".join(map(str, latest_version)) if latest_version else "unknown"
    local_version_str = ".".join(map(str, local_version))

    if latest_version and local_version < latest_version:
        # Local version is outdated
        return {
            "valid": False,
            "version_mismatch": True,
            "local_version": local_version_str,
            "latest_version": latest_version_str,
            "message": f"Update required. Your version ({local_version_str}) is outdated. Latest: {latest_version_str}",
        }

    # Check if license file exists
    if not LICENSE_FILE.exists():
        # First run - start trial
        return start_trial()

    # Load existing license
    try:
        with open(LICENSE_FILE) as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        # Corrupted file - restart trial
        return start_trial()

    # Check build seed mismatch (new build required)
    stored_seed = data.get("build_seed", "")
    if stored_seed != BUILD_SEED:
        # Different build - clear old license and start fresh trial
        return start_trial()

    # Check trial expiration
    trial_end_str = data.get("trial_end")
    if not trial_end_str:
        return start_trial()

    trial_end = datetime.fromisoformat(trial_end_str)
    now = datetime.now()

    # Calculate days remaining
    time_remaining = trial_end - now
    days_remaining = max(0, time_remaining.days)

    if now > trial_end:
        # Trial expired
        return {
            "valid": False,
            "trial_expired": True,
            "trial_end": trial_end.strftime("%Y-%m-%d %H:%M"),
            "days_remaining": 0,
            "message": "Trial period expired. Please download a new build of TextHunter.",
        }

    # Trial still active
    return {
        "valid": True,
        "trial_expired": False,
        "trial_start": data.get("trial_start", "").replace("T", " ").split(".")[0],
        "trial_end": trial_end.strftime("%Y-%m-%d %H:%M"),
        "days_remaining": days_remaining,
        "local_version": local_version_str,
        "latest_version": latest_version_str,
        "message": f"Trial active. {days_remaining} day(s) remaining.",
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


def get_trial_info() -> dict:
    """Get current trial information without modifying state.

    Returns:
        dict with trial status information
    """
    result = validate_license()
    return {
        "is_trial": True,
        "trial_duration_days": TRIAL_DURATION_DAYS,
        **result,
    }
