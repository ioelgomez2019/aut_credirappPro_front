"""Functional orchestration for Katamobile login and session reuse."""

from enum import Enum, auto
from math import ceil
from time import monotonic

from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.remote.webdriver import WebDriver

from config.environment import (
    ANDROID_DEVICE_UDID,
    CONFIGURATION_COMPLETION_TIMEOUT_SECONDS,
    APP_PACKAGE,
    LOGIN_ACTIVITY,
    REAUTHENTICATION_DASHBOARD_TIMEOUT_SECONDS,
)
from config.runnerConfig import EXPLICIT_WAIT_SECONDS
from modules.inicioSesion.login.inicioSesionPage import InicioSesionPage


class EstadoSesion(Enum):
    # Todavía no se ha detectado qué pantalla muestra la aplicación.
    UNKNOWN = auto()
    # La sesión ya está activa y el dashboard es visible.
    ACTIVE = auto()
    # No hay sesión iniciada; se debe completar organización y Microsoft.
    LOGIN_REQUIRED = auto()
    # La sesión anterior expiró; se requiere autenticación Microsoft nuevamente.
    REAUTH_REQUIRED = auto()


class ResultadoConfiguracion(Enum):
    CALENDARIO = auto()
    CONFIGURACION_COMPLETA = auto()


class InicioSesionWorkflow:
    def __init__(self, pageInicioSesion: InicioSesionPage) -> None:
        self._page = pageInicioSesion
        self.driver = pageInicioSesion.driver
        self.estadoSesion = EstadoSesion.UNKNOWN

    # ======================================================
    # Private Methods
    # ======================================================
    def _detectarResultadoConfiguracion(
        self, _driver: WebDriver
    ) -> ResultadoConfiguracion | None:
        if self._page.isDisplayed(self._page.dialogoCalendario):
            return ResultadoConfiguracion.CALENDARIO
        try:
            mensaje = self._page.find(self._page.mensajeConfiguracionCompleta)
            if (
                mensaje.is_displayed()
                and "Configuración del dispositivo completa." in mensaje.text
            ):
                return ResultadoConfiguracion.CONFIGURACION_COMPLETA
        except (NoSuchElementException, StaleElementReferenceException):
            return None
        return None

    def _esperarCalendarioOConfiguracion(
        self, timeout: int
    ) -> ResultadoConfiguracion:
        return self._page.waitUntil(
            self._detectarResultadoConfiguracion,
            timeout=timeout,
        )

    def _seleccionarCalendario(self) -> None:
        self._page.click(self._page.primerRadioCalendario)
        self._page.click(self._page.botonAceptarCalendario)

    def _esperarConfiguracionCompleta(self, timeout: int) -> None:
        self._page.waitText(
            self._page.mensajeConfiguracionCompleta,
            "Configuración del dispositivo completa.",
            timeout=timeout,
        )

    def _continuarConfiguracion(self) -> None:
        self._page.click(self._page.botonContinuarDescarga)

    def _detectarEstadoVisible(self, _driver: WebDriver) -> EstadoSesion | None:
        if self._page.isDisplayed(self._page.dialogoSesionExpirada):
            return EstadoSesion.REAUTH_REQUIRED
        if self._page.isDisplayed(self._page.pantallaPrincipal):
            return EstadoSesion.ACTIVE
        if self._page.isDisplayed(self._page.usuarioSesionActual):
            return EstadoSesion.REAUTH_REQUIRED
        if self._page.isDisplayed(self._page.pantallaOrganizacion):
            return EstadoSesion.LOGIN_REQUIRED
        return None

    def _detectarEstadoSesion(self) -> EstadoSesion:
        try:
            return self._page.waitUntil(
                self._detectarEstadoVisible, timeout=EXPLICIT_WAIT_SECONDS // 2
            )
        except TimeoutException as exc:
            raise self._unexpectedState(
                "exact session-expired alert, main screen, Organization screen, "
                "or current-session screen"
            ) from exc

    def _requires(self, *states: EstadoSesion) -> bool:
        if self.estadoSesion is EstadoSesion.UNKNOWN:
            raise self._unexpectedState(
                "determined application session state before session-dependent actions"
            )
        return self.estadoSesion in states

    def _unexpectedState(self, expected: str) -> AssertionError:
        return AssertionError(
            f"Expected {expected}; current state: "
            f"package={self.driver.current_package}, "
            f"activity={self.driver.current_activity}. "
            "Login success has not been verified."
        )

    def _isLoginActivity(self, driver: WebDriver) -> bool:
        activity = driver.current_activity
        expected_relative = LOGIN_ACTIVITY.removeprefix(APP_PACKAGE)
        return (
            driver.current_package == APP_PACKAGE
            and activity in {LOGIN_ACTIVITY, expected_relative}
        )

    # ======================================================
    # Public Methods
    # ======================================================
    def verificarDispositivoAndroid(self) -> None:
        if not self.driver.session_id:
            raise AssertionError(
                f"No active Appium session for Android device {ANDROID_DEVICE_UDID}."
            )

    def abrirAplicacion(self) -> None:
        self.estadoSesion = EstadoSesion.UNKNOWN
        self.driver.activate_app(APP_PACKAGE)

    def determinarEstadoSesion(self) -> EstadoSesion:
        self.estadoSesion = EstadoSesion.UNKNOWN
        detected_state = self._detectarEstadoSesion()
        self.estadoSesion = detected_state
        return detected_state

    def ingresarCredencialesMicrosoftSiCorresponde(
        self, usuario: str, contrasena: str
    ) -> None:
        if not self._requires(
            EstadoSesion.LOGIN_REQUIRED, EstadoSesion.REAUTH_REQUIRED
        ):
            return
        if not usuario.strip() or not contrasena:
            raise ValueError("Microsoft username and password are required for login.")

        try:
            self._page.waitVisible(self._page.correoMicrosoft)
            self._page.setText(self._page.correoMicrosoft, usuario)
            self._page.click(self._page.botonSiguienteMicrosoft)
        except TimeoutException as exc:
            raise self._unexpectedState("Microsoft email screen and Next button") from exc

        try:
            self._page.waitVisible(self._page.contrasenaMicrosoft)
            self._page.setText(self._page.contrasenaMicrosoft, contrasena)
            self._page.click(self._page.botonIniciarSesionMicrosoft)
        except TimeoutException as exc:
            raise self._unexpectedState("Microsoft password screen and Sign in button") from exc

    def completarOrganizacionSiCorresponde(self, organizacion: str) -> None:
        if not self._requires(EstadoSesion.LOGIN_REQUIRED):
            return
        if not organizacion.strip():
            raise ValueError("Organization is required for a fresh login.")

        try:
            self._page.waitVisible(self._page.pantallaOrganizacion)
            self._page.setText(self._page.campoOrganizacion, organizacion)
            self._page.click(self._page.botonContinuar)
        except TimeoutException as exc:
            raise self._unexpectedState("Organization screen and Continue button") from exc

    def prepararReautenticacionSiCorresponde(self) -> None:
        if not self._requires(EstadoSesion.REAUTH_REQUIRED):
            return
        try:
            if self._page.isDisplayed(self._page.dialogoSesionExpirada):
                self._page.click(self._page.botonAceptarSesionExpirada)
            self._page.waitVisible(self._page.usuarioSesionActual)
            self._page.click(self._page.botonReautenticacion)
        except TimeoutException as exc:
            raise self._unexpectedState(
                "current-session screen and reauthentication button"
            ) from exc

    def continuarDescargaConfiguracionSiCorresponde(self) -> None:
        if not self._requires(EstadoSesion.LOGIN_REQUIRED):
            return
        deadline = monotonic() + CONFIGURATION_COMPLETION_TIMEOUT_SECONDS
        try:
            resultado = self._esperarCalendarioOConfiguracion(
                timeout=CONFIGURATION_COMPLETION_TIMEOUT_SECONDS
            )
            if resultado is ResultadoConfiguracion.CALENDARIO:
                self._seleccionarCalendario()
                remaining_timeout = max(1, ceil(deadline - monotonic()))
                self._esperarConfiguracionCompleta(timeout=remaining_timeout)
            elif resultado is not ResultadoConfiguracion.CONFIGURACION_COMPLETA:
                raise AssertionError("Unknown configuration result.")
            self._continuarConfiguracion()
        except TimeoutException as exc:
            raise self._unexpectedState(
                "calendar selection or completed configuration screen and Continue button"
            ) from exc

    def validarPantallaPrincipal(self) -> None:
        try:
            if self.estadoSesion is EstadoSesion.REAUTH_REQUIRED:
                self._page.waitVisible(
                    self._page.pantallaPrincipal,
                    timeout=REAUTHENTICATION_DASHBOARD_TIMEOUT_SECONDS,
                )
            else:
                self._page.waitVisible(self._page.pantallaPrincipal)
        except TimeoutException as exc:
            raise self._unexpectedState("main screen") from exc

    def validarPantallaInicioSesion(self) -> bool:
        return bool(self._page.waitUntil(self._isLoginActivity))
