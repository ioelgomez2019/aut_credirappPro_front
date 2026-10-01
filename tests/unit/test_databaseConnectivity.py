"""Unit checks for database settings and ODBC connection creation."""

import importlib
import importlib.util
import shutil
import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import Mock

import pytest

from config.database.settings import DatabaseSettings

pytestmark = pytest.mark.unit


def test_environment_loader_reads_isolated_root_dotenv_and_preserves_process_precedence(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    isolated_root = tmp_path / "isolated-project"
    isolated_config = isolated_root / "config"
    isolated_config.mkdir(parents=True)
    package_init = isolated_config / "__init__.py"
    package_init.write_text("", encoding="utf-8")
    environment_path = isolated_config / "environment.py"
    source_path = (
        Path(__file__).resolve().parents[2]
        / "config"
        / "environment.py"
    )
    shutil.copyfile(source_path, environment_path)
    (isolated_root / ".env").write_text(
        "APPIUM_SERVER_URL=http://appium.example.invalid:4739/\n"
        "ANDROID_DEVICE_UDID=dotenv-device\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("APPIUM_SERVER_URL", raising=False)
    monkeypatch.setenv("ANDROID_DEVICE_UDID", "process-device")

    package_spec = importlib.util.spec_from_file_location(
        "config",
        package_init,
        submodule_search_locations=[str(isolated_config)],
    )
    assert package_spec is not None and package_spec.loader is not None
    isolated_package = importlib.util.module_from_spec(package_spec)
    monkeypatch.setitem(sys.modules, "config", isolated_package)
    package_spec.loader.exec_module(isolated_package)
    monkeypatch.delitem(sys.modules, "config.environment", raising=False)

    environment = importlib.import_module("config.environment")

    assert environment.APPIUM_SERVER_URL == "http://appium.example.invalid:4739"
    assert environment.ANDROID_DEVICE_UDID == "process-device"


def test_from_environment_reads_os_values_and_applies_defaults(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    isolated_root = tmp_path / "isolated-database-settings"
    isolated_settings_dir = isolated_root / "config" / "database"
    isolated_settings_dir.mkdir(parents=True)
    settings_path = isolated_settings_dir / "settings.py"
    source_path = (
        Path(__file__).resolve().parents[2]
        / "config"
        / "database"
        / "settings.py"
    )
    shutil.copyfile(source_path, settings_path)
    (isolated_root / ".env").write_text("", encoding="utf-8")
    spec = importlib.util.spec_from_file_location(
        "isolated_database_settings",
        settings_path,
    )
    assert spec is not None and spec.loader is not None
    isolated_settings = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, spec.name, isolated_settings)
    spec.loader.exec_module(isolated_settings)

    values = {
        "DB_SERVER": r"test-server\test-instance",
        "DB_NAME": "test_database",
        "DB_USER": "test_user",
        "DB_PASSWORD": "unit-test-only-placeholder",
    }
    optional_names = ("DB_DRIVER", "DB_COMMAND_TIMEOUT")

    for name in (*values, *optional_names):
        monkeypatch.delenv(name, raising=False)
    for name, value in values.items():
        monkeypatch.setenv(name, value)

    settings = isolated_settings.DatabaseSettings.from_environment()

    assert settings.server == values["DB_SERVER"]
    assert settings.database == values["DB_NAME"]
    assert settings.username == values["DB_USER"]
    assert settings.password == values["DB_PASSWORD"]
    assert settings.driver == "ODBC Driver 18 for SQL Server"
    assert settings.command_timeout == 120


def test_from_environment_rejects_blank_required_settings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    values = {
        "DB_SERVER": "",
        "DB_NAME": "test_database",
        "DB_USER": "test_user",
        "DB_PASSWORD": "unit-test-only-placeholder",
        "DB_COMMAND_TIMEOUT": "30",
    }
    for name, value in values.items():
        monkeypatch.setenv(name, value)

    with pytest.raises(ValueError, match="DB_SERVER"):
        DatabaseSettings.from_environment()


def test_from_environment_repr_does_not_disclose_password(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    values = {
        "DB_SERVER": r"test-server\test-instance",
        "DB_NAME": "test_database",
        "DB_USER": "test_user",
        "DB_PASSWORD": "unit-test-only-placeholder",
    }
    for name, value in values.items():
        monkeypatch.setenv(name, value)
    settings = DatabaseSettings.from_environment()

    if "password=" in repr(settings):
        pytest.fail("DatabaseSettings repr must not expose the password field.")


@pytest.mark.parametrize("timeout_value", ["not-a-number", "0", "-1"])
def test_from_environment_rejects_invalid_command_timeout(
    monkeypatch: pytest.MonkeyPatch,
    timeout_value: str,
) -> None:
    values = {
        "DB_SERVER": r"test-server\test-instance",
        "DB_NAME": "test_database",
        "DB_USER": "test_user",
        "DB_PASSWORD": "unit-test-only-placeholder",
        "DB_COMMAND_TIMEOUT": timeout_value,
    }
    for name, value in values.items():
        monkeypatch.setenv(name, value)

    with pytest.raises(
        ValueError,
        match="DB_COMMAND_TIMEOUT must be a positive integer",
    ):
        DatabaseSettings.from_environment()


def test_connect_database_escapes_odbc_values_and_applies_query_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    values = {
        "DB_SERVER": r"test-server\test-instance;Encrypt=no",
        "DB_NAME": "test_database",
        "DB_USER": "test_user",
        "DB_PASSWORD": "unit-test-only-}placeholder",
        "DB_DRIVER": "ODBC Driver 18 for SQL Server",
        "DB_COMMAND_TIMEOUT": "47",
    }
    for name, value in values.items():
        monkeypatch.setenv(name, value)
    settings = DatabaseSettings.from_environment()

    monkeypatch.delitem(sys.modules, "config.database.connection", raising=False)
    monkeypatch.setitem(sys.modules, "pyodbc", None)
    connection_module = importlib.import_module("config.database.connection")
    connection = Mock()
    odbc_driver = ModuleType("pyodbc")
    odbc_driver.connect = Mock(return_value=connection)
    monkeypatch.setitem(sys.modules, "pyodbc", odbc_driver)

    result = connection_module.connect_database(settings)

    assert result is connection
    odbc_driver.connect.assert_called_once_with(
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER={test-server\\test-instance;Encrypt=no};"
        "DATABASE={test_database};UID={test_user};"
        "PWD={unit-test-only-}}placeholder}"
    )
    assert connection.timeout == 47
