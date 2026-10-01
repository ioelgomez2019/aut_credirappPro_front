"""Explicit-wait and lookup operations shared by Page Objects."""

from collections.abc import Callable
from typing import TypeAlias, Any

from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as conditions
from selenium.webdriver.support.ui import WebDriverWait

from config.runnerConfig import EXPLICIT_WAIT_SECONDS

Locator: TypeAlias = tuple[str, str]


class ElementHelper:
    def __init__(self, driver: WebDriver, timeout: int = EXPLICIT_WAIT_SECONDS) -> None:
        self.driver = driver
        self.timeout = timeout

    def find(self, locator: Locator) -> WebElement:
        return self.driver.find_element(*locator)

    def findAll(self, locator: Locator) -> list[WebElement]:
        return self.driver.find_elements(*locator)

    def waitVisible(self, locator: Locator, timeout: int | None = None) -> WebElement:
        waitTimeout = self.timeout if timeout is None else timeout
        return WebDriverWait(self.driver, waitTimeout).until(
            conditions.visibility_of_element_located(locator)
        )

    def waitText(
        self, locator: Locator, text: str, timeout: int | None = None
    ) -> bool:
        waitTimeout = self.timeout if timeout is None else timeout
        return bool(
            WebDriverWait(self.driver, waitTimeout).until(
                conditions.text_to_be_present_in_element(locator, text)
            )
        )

    def waitClickable(self, locator: Locator) -> WebElement:
        return WebDriverWait(self.driver, self.timeout).until(
            conditions.element_to_be_clickable(locator)
        )

    def exists(self, locator: Locator) -> bool:
        return bool(self.driver.find_elements(*locator))

    def isDisplayed(self, locator: Locator) -> bool:
        try:
            return self.find(locator).is_displayed()
        except (NoSuchElementException, StaleElementReferenceException):
            return False

    def waitUntil(
        self, condition: Callable[[WebDriver], Any], timeout: int | None = None
    ) -> Any:
        waitTimeout = self.timeout if timeout is None else timeout
        return WebDriverWait(self.driver, waitTimeout).until(condition)
