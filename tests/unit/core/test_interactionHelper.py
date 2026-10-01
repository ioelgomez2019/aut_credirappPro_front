"""Unit checks for common element interactions."""

from unittest.mock import Mock

import pytest

from core.utils.interactionHelper import InteractionHelper

pytestmark = pytest.mark.unit


def test_click_uses_clickable_element() -> None:
    driver = Mock()
    elements = Mock()
    button = Mock()
    elements.waitClickable.return_value = button
    helper = InteractionHelper(driver, elements)

    helper.click(("id", "continue"))

    elements.waitClickable.assert_called_once_with(("id", "continue"))
    button.click.assert_called_once_with()


def test_set_text_clears_before_typing() -> None:
    driver = Mock()
    elements = Mock()
    field = Mock()
    elements.waitClickable.return_value = field
    helper = InteractionHelper(driver, elements)

    helper.setText(("id", "username"), "user")

    elements.waitClickable.assert_called_once_with(("id", "username"))
    field.clear.assert_called_once_with()
    field.send_keys.assert_called_once_with("user")
