"""Capture evidence after every Gherkin step and when a step fails."""

import re

import pytest

from core.reporting.actionReporter import attachScreenshot


def _stepName(step: object) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", str(getattr(step, "name", "step")))


def _driver(request: object) -> object | None:
    node = getattr(request, "node", None)
    return getattr(node, "funcargs", {}).get("driver") if node else None


@pytest.hookimpl(optionalhook=True)
def pytest_bdd_before_scenario(request, feature, scenario):
    try:
        import allure

        allure.dynamic.parent_suite(feature.name)
        allure.dynamic.suite(scenario.name)
        allure.dynamic.feature(feature.name)
    except ImportError:
        pass


@pytest.hookimpl(optionalhook=True)
def pytest_bdd_after_step(request, feature, scenario, step, step_func, step_func_args):
    driver = _driver(request)
    if driver is not None:
        attachScreenshot(driver, f"STEP_{_stepName(step)}")


@pytest.hookimpl(optionalhook=True)
def pytest_bdd_step_error(
    request, feature, scenario, step, step_func, step_func_args, exception
):
    driver = _driver(request)
    if driver is not None:
        attachScreenshot(driver, f"ERROR_STEP_{_stepName(step)}")
