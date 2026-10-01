"""Thin shared facade for UI element and interaction helpers."""

from collections.abc import Callable
from typing import Any

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from core.utils.controlsHelper import ControlsHelper
from core.utils.elementHelper import ElementHelper, Locator
from core.utils.interactionHelper import InteractionHelper


class BasePage:
    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver
        self._elements = ElementHelper(driver)
        self._interactions = InteractionHelper(driver, self._elements)
        self._controls = ControlsHelper(self._elements, self._interactions)

    def find(self, locator: Locator) -> WebElement:
        return self._elements.find(locator)

    def findAll(self, locator: Locator) -> list[WebElement]:
        return self._elements.findAll(locator)

    def waitVisible(self, locator: Locator, timeout: int | None = None) -> WebElement:
        return self._elements.waitVisible(locator, timeout)

    def waitText(self, locator: Locator, text: str, timeout: int | None = None) -> bool:
        return self._elements.waitText(locator, text, timeout)

    def waitClickable(self, locator: Locator) -> WebElement:
        return self._elements.waitClickable(locator)

    def exists(self, locator: Locator) -> bool:
        return self._elements.exists(locator)

    def isDisplayed(self, locator: Locator) -> bool:
        return self._elements.isDisplayed(locator)

    def click(self, locator: Locator) -> None:
        self._interactions.click(locator)

    def setText(self, locator: Locator, value: str) -> None:
        self._interactions.setText(locator, value)

    def clear(self, locator: Locator) -> None:
        self._interactions.clear(locator)

    def getText(self, locator: Locator) -> str:
        return self._interactions.getText(locator)

    def tap(self, x: int, y: int) -> None:
        self._interactions.tap(x, y)

    def longPress(self, x: int, y: int, durationMs: int = 800) -> None:
        self._interactions.longPress(x, y, durationMs)

    def swipe(
        self,
        startX: int,
        startY: int,
        endX: int,
        endY: int,
        durationMs: int = 500,
    ) -> None:
        self._interactions.swipe(startX, startY, endX, endY, durationMs)

    def scroll(self, direction: str = "down", percent: float = 0.75) -> bool:
        return self._interactions.scroll(direction, percent)

    def waitUntil(
        self, condition: Callable[[WebDriver], Any], timeout: int | None = None
    ) -> Any:
        return self._interactions.waitUntil(condition, timeout)

    def setChecked(self, locator: Locator, checked: bool) -> bool:
        return self._controls.setChecked(locator, checked)

    def selectListItem(self, locator: Locator) -> None:
        self._controls.selectListItem(locator)

    def selectComboOption(self, combo: Locator, option: Locator) -> None:
        self._controls.selectComboOption(combo, option)
