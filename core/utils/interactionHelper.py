"""UI interactions implemented once and shared by Page Objects."""

from collections.abc import Callable
from typing import Any

from selenium.webdriver.remote.webdriver import WebDriver

from config.runnerConfig import EXPLICIT_WAIT_SECONDS
from core.reporting.actionReporter import reportAction
from core.utils.elementHelper import ElementHelper, Locator


class InteractionHelper:
    def __init__(
        self,
        driver: WebDriver,
        elements: ElementHelper | None = None,
        timeout: int = EXPLICIT_WAIT_SECONDS,
    ) -> None:
        self.driver = driver
        self.elements = elements or ElementHelper(driver, timeout)

    def click(self, locator: Locator) -> None:
        with reportAction(self.driver, f"click {locator}"):
            self.elements.waitClickable(locator).click()

    def setText(self, locator: Locator, value: str) -> None:
        with reportAction(self.driver, f"setText {locator}"):
            element = self.elements.waitClickable(locator)
            element.clear()
            element.send_keys(value)

    def clear(self, locator: Locator) -> None:
        with reportAction(self.driver, f"clear {locator}"):
            self.elements.waitVisible(locator).clear()

    def getText(self, locator: Locator) -> str:
        with reportAction(self.driver, f"getText {locator}"):
            return self.elements.waitVisible(locator).text

    def tap(self, x: int, y: int) -> None:
        with reportAction(self.driver, f"tap ({x}, {y})"):
            self.driver.execute_script("mobile: clickGesture", {"x": x, "y": y})

    def longPress(self, x: int, y: int, durationMs: int = 800) -> None:
        with reportAction(self.driver, f"longPress ({x}, {y})"):
            self.driver.execute_script(
                "mobile: longClickGesture",
                {"x": x, "y": y, "duration": durationMs},
            )

    def swipe(
        self,
        startX: int,
        startY: int,
        endX: int,
        endY: int,
        durationMs: int = 500,
    ) -> None:
        with reportAction(self.driver, "swipe"):
            self.driver.execute_script(
                "mobile: swipeGesture",
                {
                    "startX": startX,
                    "startY": startY,
                    "endX": endX,
                    "endY": endY,
                    "duration": durationMs,
                },
            )

    def scroll(self, direction: str = "down", percent: float = 0.75) -> bool:
        with reportAction(self.driver, f"scroll {direction}"):
            size = self.driver.get_window_size()
            return bool(
                self.driver.execute_script(
                    "mobile: scrollGesture",
                    {
                        "left": 0,
                        "top": 0,
                        "width": size["width"],
                        "height": size["height"],
                        "direction": direction,
                        "percent": percent,
                    },
                )
            )

    def waitUntil(
        self, condition: Callable[[WebDriver], Any], timeout: int | None = None
    ) -> Any:
        return self.elements.waitUntil(condition, timeout)
