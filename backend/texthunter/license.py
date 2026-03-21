"""License validation module for TextHunter desktop app.

This module handles trial period validation.
Users get a 3-day trial from first launch, after which a new build is required.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
LICENSE_FILE = Path.home() / ".texthunter" / "license.json"
TRIAL_DURATION_DAYS = 3

# Build-specific seed to prevent simple trial reset
# Change this value when creating a new build to invalidate old trials
BUILD_SEED = "texthunter-build-0.7.0-20260321"


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

    return {
        "valid": True,
        "trial_start": trial_start.strftime("%Y-%m-%d %H:%M"),
        "trial_end": trial_end.strftime("%Y-%m-%d %H:%M"),
        "days_remaining": TRIAL_DURATION_DAYS,
        "message": f"Trial started. Expires in {TRIAL_DURATION_DAYS} days.",
    }


def validate_license() -> dict:
    """Validate the trial period.

    Checks if:
    1. Trial exists and hasn't expired
    2. Build seed matches (prevents copying license from old builds)

    Returns:
        dict with keys:
            - valid: bool - whether trial is active
            - message: str - human readable status
            - trial_expired: bool - specifically indicates trial expiration
            - days_remaining: int - days left in trial
            - trial_end: str - formatted trial end date
    """
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
