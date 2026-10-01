"""Unit checks for Appium readiness handling."""

import json
from unittest.mock import MagicMock, patch

import pytest

from core.appiumServerManager import ensureAppiumServerAvailable

pytestmark = pytest.mark.unit


def test_server_status_must_report_ready() -> None:
    response = MagicMock()
    response.__enter__.return_value.read.return_value = json.dumps(
        {"value": {"ready": True}}
    ).encode()

    with patch("core.appiumServerManager.urlopen", return_value=response):
        ensureAppiumServerAvailable()


def test_server_not_ready_raises_a_clear_error() -> None:
    response = MagicMock()
    response.__enter__.return_value.read.return_value = json.dumps(
        {"value": {"ready": False}}
    ).encode()

    with patch("core.appiumServerManager.urlopen", return_value=response):
        with pytest.raises(RuntimeError, match="not ready"):
            ensureAppiumServerAvailable()
