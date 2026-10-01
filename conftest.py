"""Shared pytest fixtures for the Appium test suite."""

from collections.abc import Generator
from datetime import datetime
from pathlib import Path
import os
import shutil
import sys

import pytest
from appium.webdriver.webdriver import WebDriver

from core.basePage import BasePage
from core.driverFactory import DriverFactory
from modules.inicioSesion.login.inicioSesionPage import InicioSesionPage
from modules.inicioSesion.login.inicioSesionWorkflow import InicioSesionWorkflow

pytest_plugins = ("core.hooks.screenshotHook", "core.reporting.bddReporter")


def pytest_addoption(parser) -> None:
    parser.addoption(
        "--test-type",
        action="store",
        default="funcional",
        help="Test type used to name the timestamped reporting folder.",
    )


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config) -> None:
    testType = config.getoption("--test-type").strip().lower()
    configuredReportDirectory = os.getenv("AUTOMATION_REPORT_DIR")
    if configuredReportDirectory:
        reportDirectory = Path(configuredReportDirectory)
    else:
        reportDirectory = (
            Path("reporting") / f"{testType}_{datetime.now():%Y%m%d_%H%M%S}"
        )
    reportDirectory.mkdir(parents=True, exist_ok=True)
    os.environ["AUTOMATION_REPORT_DIR"] = str(reportDirectory)
    config._automationReportDirectory = reportDirectory

    configuredAllureDirectory = getattr(config.option, "allure_report_dir", None)
    allureDirectory = (
        Path(configuredAllureDirectory)
        if configuredAllureDirectory
        else reportDirectory / "allureResults"
    )
    if not configuredAllureDirectory:
        config.option.allure_report_dir = str(allureDirectory)
    allureDirectory.mkdir(parents=True, exist_ok=True)
    config._automationAllureDirectory = allureDirectory
    config._sharedAllureDirectory = Path("reporting") / "allureResults"


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus) -> None:
    config = session.config
    sourceDirectory = getattr(config, "_automationAllureDirectory", None)
    sharedDirectory = getattr(
        config, "_sharedAllureDirectory", Path("reporting") / "allureResults"
    )
    if sourceDirectory is None:
        return

    try:
        sourceDirectory = Path(sourceDirectory)
        sharedDirectory = Path(sharedDirectory)
        if sourceDirectory.resolve() == sharedDirectory.resolve():
            return
        if not sourceDirectory.is_dir():
            return

        sharedDirectory.mkdir(parents=True, exist_ok=True)
        for resultFile in sourceDirectory.iterdir():
            if resultFile.is_file():
                shutil.copy2(resultFile, sharedDirectory / resultFile.name)
    except OSError as error:
        sys.stderr.write(f"Could not aggregate Allure results: {error}\n")


@pytest.fixture
def driver() -> Generator[WebDriver, None, None]:
    """Create one Appium session for a test and always close it."""
    session = DriverFactory.createDriver()
    try:
        yield session
    finally:
        session.quit()


@pytest.fixture
def basePage(driver: WebDriver) -> BasePage:
    return BasePage(driver)


@pytest.fixture
def inicioSesionPage(driver: WebDriver) -> InicioSesionPage:
    return InicioSesionPage(driver)


@pytest.fixture
def inicioSesionWorkflow(inicioSesionPage: InicioSesionPage) -> InicioSesionWorkflow:
    return InicioSesionWorkflow(inicioSesionPage)
