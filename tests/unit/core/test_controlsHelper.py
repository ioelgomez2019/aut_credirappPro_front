"""Unit checks for common control operations."""

from unittest.mock import Mock

import pytest

from core.utils.controlsHelper import ControlsHelper

pytestmark = pytest.mark.unit


def test_set_checked_clicks_only_when_state_differs() -> None:
    element = Mock()
    element.is_selected.side_effect = [False, True]
    elements = Mock()
    elements.waitVisible.return_value = element
    interactions = Mock()
    helper = ControlsHelper(elements, interactions)

    assert helper.setChecked(("id", "enabled"), True) is True

    interactions.click.assert_called_once_with(("id", "enabled"))
