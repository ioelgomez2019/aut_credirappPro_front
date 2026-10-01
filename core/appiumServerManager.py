"""Appium server readiness check using only Python's standard library."""

import json
from urllib.error import URLError
from urllib.request import urlopen

from config.environment import APPIUM_SERVER_URL
from config.runnerConfig import APPIUM_STATUS_TIMEOUT_SECONDS


def ensureAppiumServerAvailable() -> None:
    """Raise a useful error unless Appium's status endpoint reports ready."""
    try:
        with urlopen(
            f"{APPIUM_SERVER_URL}/status",
            timeout=APPIUM_STATUS_TIMEOUT_SECONDS,
        ) as response:
            payload = json.loads(response.read())
    except (OSError, TimeoutError, URLError, json.JSONDecodeError) as error:
        raise RuntimeError(
            f"Appium server is unavailable at {APPIUM_SERVER_URL}."
        ) from error

    if not payload.get("value", {}).get("ready", False):
        raise RuntimeError(f"Appium server is not ready at {APPIUM_SERVER_URL}.")
