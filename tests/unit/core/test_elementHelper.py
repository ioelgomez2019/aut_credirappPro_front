"""Unit checks for locator lookup behavior."""

from unittest.mock import Mock

import pytest

from core.utils.elementHelper import ElementHelper

pytestmark = pytest.mark.unit


def test_find_and_find_all_forward_the_locator_to_the_driver() -> None:
    driver = Mock()
    element = Mock()
    elements = [Mock(), Mock()]
    driver.find_element.return_value = element
    driver.find_elements.return_value = elements
    helper = ElementHelper(driver)

    assert helper.find(("id", "login")) is element
    assert helper.findAll(("id", "login-list")) == elements
    driver.find_element.assert_called_once_with("id", "login")
    driver.find_elements.assert_called_once_with("id", "login-list")


def test_exists_and_is_displayed_report_current_element_state() -> None:
    driver = Mock()
    driver.find_elements.side_effect = [[], [Mock()]]
    visible_element = Mock()
    visible_element.is_displayed.return_value = True
    driver.find_element.return_value = visible_element
    helper = ElementHelper(driver)

    assert helper.exists(("id", "missing")) is False
    assert helper.exists(("id", "present")) is True
    assert helper.isDisplayed(("id", "present")) is True
