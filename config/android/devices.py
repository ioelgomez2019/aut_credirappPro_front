"""ADB preflight for the configured Android target."""

import subprocess

from config.environment import ANDROID_DEVICE_UDID
from config.runnerConfig import ADB_COMMAND_TIMEOUT_SECONDS


def ensureAndroidDeviceAvailable() -> None:
    """Raise a useful error unless ADB reports the configured device as ready."""
    try:
        result = subprocess.run(
            ["adb", "-s", ANDROID_DEVICE_UDID, "get-state"],
            capture_output=True,
            text=True,
            timeout=ADB_COMMAND_TIMEOUT_SECONDS,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise RuntimeError(
            f"Unable to query Android device {ANDROID_DEVICE_UDID!r} with ADB."
        ) from error

    if result.returncode != 0 or result.stdout.strip() != "device":
        detail = result.stderr.strip() or result.stdout.strip() or "no device state returned"
        raise RuntimeError(
            f"Android device {ANDROID_DEVICE_UDID!r} is not available: {detail}"
        )
