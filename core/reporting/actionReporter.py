"""Attach Appium actions and screenshots to Allure when reporting is enabled."""

from contextlib import contextmanager
from datetime import datetime
import os
from pathlib import Path
import re
from collections.abc import Iterator


def _reportDirectory() -> Path:
    return Path(os.getenv("AUTOMATION_REPORT_DIR", "reporting"))


def _safeName(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("._") or "action"


def attachScreenshot(driver: object, name: str) -> None:
    try:
        screenshotBytes = driver.get_screenshot_as_png()
    except Exception:
        return
    if not isinstance(screenshotBytes, bytes):
        return

    screenshotDirectory = _reportDirectory() / "screenshots"
    screenshotDirectory.mkdir(parents=True, exist_ok=True)
    filename = f"{datetime.now():%Y%m%d_%H%M%S_%f}_{_safeName(name)}.png"
    screenshot = screenshotDirectory / filename
    screenshot.write_bytes(screenshotBytes)

    try:
        import allure

        allure.attach(
            screenshotBytes,
            name=name,
            attachment_type=allure.attachment_type.PNG,
        )
    except ImportError:
        pass


@contextmanager
def reportAction(driver: object, name: str) -> Iterator[None]:
    try:
        import allure
    except ImportError:
        yield
        return

    with allure.step(name):
        try:
            yield
        except Exception:
            attachScreenshot(driver, f"ERROR_{name}")
            raise
        else:
            attachScreenshot(driver, name)
