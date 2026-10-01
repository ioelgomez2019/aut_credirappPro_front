"""Create SQL Server connections through the configured ODBC driver."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pyodbc

from config.database.settings import DatabaseSettings


def _format_odbc_value(value: str) -> str:
    """Brace an ODBC value and escape closing braces within it."""
    return "{" + value.replace("}", "}}") + "}"


def connect_database(settings: DatabaseSettings) -> pyodbc.Connection:
    """Open a database connection and set its query timeout."""
    import pyodbc

    connection_string = ";".join(
        (
            f"DRIVER={_format_odbc_value(settings.driver)}",
            f"SERVER={_format_odbc_value(settings.server)}",
            f"DATABASE={_format_odbc_value(settings.database)}",
            f"UID={_format_odbc_value(settings.username)}",
            f"PWD={_format_odbc_value(settings.password)}",
        )
    )
    connection = pyodbc.connect(connection_string)
    connection.timeout = settings.command_timeout
    return connection
