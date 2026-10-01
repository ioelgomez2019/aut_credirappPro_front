"""Single entry point for creating an Appium session."""

from appium import webdriver
from appium.webdriver.webdriver import WebDriver

from config.android.capabilities import buildCapabilities
from config.android.devices import ensureAndroidDeviceAvailable
from config.environment import APPIUM_SERVER_URL
from core.appiumServerManager import ensureAppiumServerAvailable


class DriverFactory:
    @staticmethod
    def createDriver() -> WebDriver:
        ensureAppiumServerAvailable()
        ensureAndroidDeviceAvailable()
        return webdriver.Remote(APPIUM_SERVER_URL, options=buildCapabilities())
