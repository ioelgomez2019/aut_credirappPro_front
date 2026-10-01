"""Save and attach a screenshot when a test fails and a driver session exists."""

import logging
import os
import re
from pathlib import Path

import pytest

logger = logging.getLogger(__name__)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[object]):
    outcome = yield
    report = outcome.get_result()
    if not report.failed:
        return

    driver = item.funcargs.get("driver")
    if driver is None:
        return

    output_dir = Path(os.getenv("AUTOMATION_REPORT_DIR", "reporting")) / "screenshots"
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = re.sub(r"[^A-Za-z0-9_.-]+", "_", item.nodeid).strip("._") or "failed-test"
    screenshot = output_dir / f"{filename}.png"

    try:
        if not driver.save_screenshot(str(screenshot)):
            return
        try:
            import allure

            allure.attach.file(
                str(screenshot),
                name=filename,
                attachment_type=allure.attachment_type.PNG,
            )
        except ImportError:
            logger.debug("Allure is unavailable; screenshot remains at %s", screenshot)
    except Exception:
        logger.exception("Could not capture failure screenshot for %s", item.nodeid)
