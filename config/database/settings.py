"""Environment-backed database settings."""

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

DEFAULT_DATABASE_DRIVER = "ODBC Driver 18 for SQL Server"
DEFAULT_COMMAND_TIMEOUT = 120


@dataclass(frozen=True)
class DatabaseSettings:
    server: str
    database: str
    username: str
    password: str = field(repr=False)
    driver: str = DEFAULT_DATABASE_DRIVER
    command_timeout: int = DEFAULT_COMMAND_TIMEOUT

    @classmethod
    def from_environment(cls) -> "DatabaseSettings":
        """Load database settings, preferring values already set by the process."""
        root_env_path = Path(__file__).resolve().parents[2] / ".env"
        load_dotenv(dotenv_path=root_env_path, override=False)

        required_values = {
            "DB_SERVER": os.getenv("DB_SERVER"),
            "DB_NAME": os.getenv("DB_NAME"),
            "DB_USER": os.getenv("DB_USER"),
            "DB_PASSWORD": os.getenv("DB_PASSWORD"),
        }
        missing_names = [
            name
            for name, value in required_values.items()
            if value is None or not value.strip()
        ]
        if missing_names:
            raise ValueError(
                "Missing required database settings: " + ", ".join(missing_names)
            )

        timeout_value = os.getenv(
            "DB_COMMAND_TIMEOUT", str(DEFAULT_COMMAND_TIMEOUT)
        )
        try:
            command_timeout = int(timeout_value)
        except ValueError as error:
            raise ValueError(
                "DB_COMMAND_TIMEOUT must be a positive integer."
            ) from error
        if command_timeout <= 0:
            raise ValueError("DB_COMMAND_TIMEOUT must be a positive integer.")

        driver = os.getenv("DB_DRIVER", DEFAULT_DATABASE_DRIVER).strip()
        return cls(
            server=required_values["DB_SERVER"],
            database=required_values["DB_NAME"],
            username=required_values["DB_USER"],
            password=required_values["DB_PASSWORD"],
            driver=driver or DEFAULT_DATABASE_DRIVER,
            command_timeout=command_timeout,
        )
