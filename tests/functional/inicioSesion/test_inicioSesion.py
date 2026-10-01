"""pytest-bdd entry point for the login smoke feature."""

from pathlib import Path

import pytest
from pytest_bdd import scenarios

# Registra el módulo que contiene las implementaciones de Given, When y Then.
pytest_plugins = ("modules.inicioSesion.login.inicioSesionSteps",)

# Aplica la marca funcional a todos los escenarios generados desde el Feature.
pytestmark = pytest.mark.functional

# Construye la ruta absoluta del archivo Feature asociado a esta prueba.
# __file__ representa este archivo; resolve() obtiene su ruta completa.
# parents[3] sube desde tests/functional/inicioSesion hasta la raíz del proyecto.
FEATURE = (
    Path(__file__).resolve().parents[3]
    / "modules"
    / "inicioSesion"
    / "login"
    / "inicioSesion.feature"
)

# Lee el Feature y genera los tests pytest-bdd a partir de sus escenarios
# y de cada fila definida en sus bloques Examples.
scenarios(str(FEATURE))
