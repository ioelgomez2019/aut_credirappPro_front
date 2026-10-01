"""UiAutomator2 capabilities for the installed Katamobile application."""

from appium.options.android import UiAutomator2Options

from config.environment import (
    ANDROID_DEVICE_UDID,
    APP_PACKAGE,
    SPLASH_ACTIVITY,
)


def buildCapabilities() -> UiAutomator2Options:
    options = UiAutomator2Options()
    options.load_capabilities(
        {
            "platformName": "Android",
            "automationName": "UiAutomator2",
            "udid": ANDROID_DEVICE_UDID,
            "appPackage": APP_PACKAGE,
            "appActivity": SPLASH_ACTIVITY,
            "appWaitActivity": "*",
            "noReset": True,
            "autoGrantPermissions": True,
        }
    )
    return options
