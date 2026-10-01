"""Small, locator-driven operations for common Android controls."""

from core.utils.elementHelper import ElementHelper, Locator
from core.utils.interactionHelper import InteractionHelper


class ControlsHelper:
    def __init__(self, elements: ElementHelper, interactions: InteractionHelper) -> None:
        self.elements = elements
        self.interactions = interactions

    def setChecked(self, locator: Locator, checked: bool) -> bool:
        element = self.elements.waitVisible(locator)
        if element.is_selected() != checked:
            self.interactions.click(locator)
        return self.elements.waitVisible(locator).is_selected()

    def selectListItem(self, locator: Locator) -> None:
        self.interactions.click(locator)

    def selectComboOption(self, combo: Locator, option: Locator) -> None:
        self.interactions.click(combo)
        self.interactions.click(option)

    # Date pickers need the app's actual widget and date-format contract before a generic action is safe.
