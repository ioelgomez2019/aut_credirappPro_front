"""Load local settings from the repository-root environment file."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env", override=False)

APPIUM_SERVER_URL = os.getenv("APPIUM_SERVER_URL", "").rstrip("/")
ANDROID_DEVICE_UDID = os.getenv("ANDROID_DEVICE_UDID", "")
CONFIGURATION_COMPLETION_TIMEOUT_SECONDS = int(
    os.getenv("CONFIGURATION_COMPLETION_TIMEOUT_SECONDS", "180")
)
REAUTHENTICATION_DASHBOARD_TIMEOUT_SECONDS = int(
    os.getenv("REAUTHENTICATION_DASHBOARD_TIMEOUT_SECONDS", "180")
)
APP_PACKAGE = "com.kata.mobile"
SPLASH_ACTIVITY = "com.kata.mobile.splash.SplashActivity"
LOGIN_ACTIVITY = "com.kata.mobile.login.LoginActivity"
