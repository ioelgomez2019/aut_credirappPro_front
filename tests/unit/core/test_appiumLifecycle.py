"""Unit checks for login session detection and routing without Appium."""

from unittest.mock import Mock, call

import pytest
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)

from config.environment import (
    APP_PACKAGE,
    CONFIGURATION_COMPLETION_TIMEOUT_SECONDS,
    REAUTHENTICATION_DASHBOARD_TIMEOUT_SECONDS,
)
from config.runnerConfig import EXPLICIT_WAIT_SECONDS
from core.basePage import BasePage
from modules.inicioSesion.login.inicioSesionPage import InicioSesionPage
from modules.inicioSesion.login.inicioSesionWorkflow import (
    EstadoSesion,
    InicioSesionWorkflow,
    ResultadoConfiguracion,
)

pytestmark = pytest.mark.unit

SESSION_EXPIRED_MESSAGE = (
    "Su sesión expiró, por seguridad de la cuenta ingrese sus datos nuevamente."
)
SESSION_EXPIRED_ALERT = (
    AppiumBy.XPATH,
    f'//*[@resource-id="android:id/message" and @text="{SESSION_EXPIRED_MESSAGE}"]',
)
SESSION_EXPIRED_ACCEPT_BUTTON = (
    AppiumBy.XPATH,
    '//*[@resource-id="android:id/button1" and @text="ACEPTAR"]',
)


def _mock_login_page(driver: Mock | None = None) -> Mock:
    page = Mock(spec=InicioSesionPage)
    page.driver = driver if driver is not None else Mock()
    for name, locator in vars(InicioSesionPage).items():
        if isinstance(locator, tuple):
            setattr(page, name, locator)
    return page


def _configure_configuration_detection(
    page: Mock, *, calendar_visible: bool = False
) -> None:
    message = Mock()
    message.is_displayed.return_value = True
    message.text = "Prefix Configuración del dispositivo completa. suffix"
    page.driver.find_element.return_value = message
    page.find.side_effect = lambda locator: page.driver.find_element(*locator)
    page.isDisplayed.return_value = calendar_visible
    page.waitUntil.side_effect = lambda condition, timeout: condition(page.driver)


def test_calendar_locators_scope_radio_and_clickable_ok_parent() -> None:
    assert InicioSesionPage.primerRadioCalendario == (
        AppiumBy.XPATH,
        '(//*[@resource-id="com.kata.mobile:id/custom"]//android.widget.RadioButton)[1]',
    )
    assert InicioSesionPage.botonAceptarCalendario == (
        AppiumBy.XPATH,
        '//*[@resource-id="com.kata.mobile:id/custom"]//android.widget.TextView[@text="OK"]/..',
    )


def test_inicio_sesion_page_inherits_base_page_locator_operations() -> None:
    driver = Mock()
    driver.find_element.return_value.is_displayed.return_value = True
    page = InicioSesionPage(driver)

    assert isinstance(page, BasePage)
    assert page.isDisplayed(InicioSesionPage.dialogoSesionExpirada) is True
    driver.find_element.assert_called_once_with(*InicioSesionPage.dialogoSesionExpirada)


def test_inicio_sesion_page_has_no_configuration_orchestration_methods() -> None:
    screen_methods = (
        "esperarCalendarioOConfiguracion",
        "_detectarResultadoConfiguracion",
        "seleccionarCalendario",
        "esperarConfiguracionCompleta",
        "continuarConfiguracion",
    )

    assert all(not hasattr(InicioSesionPage, name) for name in screen_methods)


def test_workflow_uses_one_page_for_driver_and_locator_operations() -> None:
    driver = Mock()
    page = InicioSesionPage(driver)
    page.waitVisible = Mock()
    workflow = InicioSesionWorkflow(page)

    workflow.abrirAplicacion()
    workflow.validarPantallaPrincipal()

    driver.activate_app.assert_called_once_with(APP_PACKAGE)
    page.waitVisible.assert_called_once_with(InicioSesionPage.pantallaPrincipal)


def test_login_workflow_accepts_the_relative_login_activity_name() -> None:
    driver = Mock()
    driver.session_id = "session"
    driver.current_package = APP_PACKAGE
    driver.current_activity = ".login.LoginActivity"
    base_page = _mock_login_page(driver)
    base_page.waitUntil.side_effect = lambda condition: condition(driver)
    workflow = InicioSesionWorkflow(base_page)

    assert workflow.validarPantallaInicioSesion() is True


def test_session_state_starts_unknown_and_is_scoped_to_each_workflow() -> None:
    first = InicioSesionWorkflow(_mock_login_page())
    second = InicioSesionWorkflow(_mock_login_page())

    first.estadoSesion = EstadoSesion.ACTIVE

    assert first.estadoSesion is EstadoSesion.ACTIVE
    assert second.estadoSesion is EstadoSesion.UNKNOWN


def test_open_only_activates_the_app_and_resets_session_state() -> None:
    driver = Mock()
    base_page = _mock_login_page(driver)
    workflow = InicioSesionWorkflow(base_page)
    workflow.estadoSesion = EstadoSesion.ACTIVE

    workflow.abrirAplicacion()

    assert workflow.estadoSesion is EstadoSesion.UNKNOWN
    driver.activate_app.assert_called_once_with(APP_PACKAGE)
    assert base_page.mock_calls == [call.driver.activate_app(APP_PACKAGE)]


@pytest.mark.parametrize(
    ("visible_results", "expected_state", "expected_locators"),
    [
        (
            [False, True],
            EstadoSesion.ACTIVE,
            [SESSION_EXPIRED_ALERT, InicioSesionPage.pantallaPrincipal],
        ),
        (
            [False, False, False, True],
            EstadoSesion.LOGIN_REQUIRED,
            [
                SESSION_EXPIRED_ALERT,
                InicioSesionPage.pantallaPrincipal,
                InicioSesionPage.usuarioSesionActual,
                InicioSesionPage.pantallaOrganizacion,
            ],
        ),
        (
            [False, False, True],
            EstadoSesion.REAUTH_REQUIRED,
            [
                SESSION_EXPIRED_ALERT,
                InicioSesionPage.pantallaPrincipal,
                InicioSesionPage.usuarioSesionActual,
            ],
        ),
    ],
)
def test_session_detection_classifies_each_known_screen(
    visible_results: list[object],
    expected_state: EstadoSesion,
    expected_locators: list[tuple[str, str]],
) -> None:
    driver = Mock()
    base_page = _mock_login_page(driver)
    base_page.isDisplayed.side_effect = visible_results
    base_page.waitUntil.side_effect = lambda condition, timeout: condition(driver)
    workflow = InicioSesionWorkflow(base_page)

    workflow.determinarEstadoSesion()

    assert workflow.estadoSesion is expected_state
    assert base_page.waitUntil.call_count == 1
    assert (
        base_page.waitUntil.call_args.kwargs["timeout"]
        == EXPLICIT_WAIT_SECONDS // 2
    )
    assert base_page.isDisplayed.call_args_list == [
        call(locator) for locator in expected_locators
    ]
    base_page.waitVisible.assert_not_called()


def test_session_detection_returns_and_stores_the_detected_state() -> None:
    driver = Mock()
    base_page = _mock_login_page(driver)
    base_page.isDisplayed.side_effect = [False, True]
    base_page.waitUntil.side_effect = lambda condition, timeout: condition(driver)
    workflow = InicioSesionWorkflow(base_page)

    detected_state = workflow.determinarEstadoSesion()

    assert detected_state is EstadoSesion.ACTIVE
    assert workflow.estadoSesion is detected_state


def test_current_session_anchor_wins_when_tenant_container_is_also_visible() -> None:
    driver = Mock()
    base_page = _mock_login_page(driver)
    base_page.isDisplayed.side_effect = [False, False, True, True]
    base_page.waitUntil.side_effect = lambda condition, timeout: condition(driver)
    workflow = InicioSesionWorkflow(base_page)

    workflow.determinarEstadoSesion()

    assert workflow.estadoSesion is EstadoSesion.REAUTH_REQUIRED
    assert base_page.waitUntil.call_count == 1
    assert base_page.waitUntil.call_args.kwargs["timeout"] == 10
    assert base_page.isDisplayed.call_args_list == [
        call(SESSION_EXPIRED_ALERT),
        call(InicioSesionPage.pantallaPrincipal),
        call(InicioSesionPage.usuarioSesionActual),
    ]
    base_page.waitVisible.assert_not_called()


def test_exact_session_expired_alert_wins_over_every_underlying_screen() -> None:
    driver = Mock()
    base_page = _mock_login_page(driver)
    base_page.isDisplayed.return_value = True
    base_page.waitUntil.side_effect = lambda condition, timeout: condition(driver)
    workflow = InicioSesionWorkflow(base_page)

    workflow.determinarEstadoSesion()

    assert InicioSesionPage.dialogoSesionExpirada == SESSION_EXPIRED_ALERT
    assert workflow.estadoSesion is EstadoSesion.REAUTH_REQUIRED
    base_page.waitUntil.assert_called_once()
    assert base_page.waitUntil.call_args.kwargs["timeout"] == EXPLICIT_WAIT_SECONDS // 2
    base_page.isDisplayed.assert_called_once_with(SESSION_EXPIRED_ALERT)


def test_session_detection_keeps_unknown_when_no_known_screen_is_visible() -> None:
    driver = Mock()
    driver.current_package = APP_PACKAGE
    driver.current_activity = ".unknown.Activity"
    base_page = _mock_login_page(driver)
    base_page.waitUntil.side_effect = TimeoutException()
    workflow = InicioSesionWorkflow(base_page)
    workflow.estadoSesion = EstadoSesion.ACTIVE

    with pytest.raises(
        AssertionError,
        match="package=com.kata.mobile, activity=.unknown.Activity",
    ):
        workflow.determinarEstadoSesion()

    assert workflow.estadoSesion is EstadoSesion.UNKNOWN
    base_page.waitUntil.assert_called_once()
    assert base_page.waitUntil.call_args.kwargs["timeout"] == 10
    base_page.isDisplayed.assert_not_called()
    base_page.waitVisible.assert_not_called()


def test_active_route_skips_optional_actions_and_always_validates_dashboard() -> None:
    base_page = _mock_login_page()
    workflow = InicioSesionWorkflow(base_page)
    workflow.estadoSesion = EstadoSesion.ACTIVE

    workflow.completarOrganizacionSiCorresponde("")
    workflow.prepararReautenticacionSiCorresponde()
    workflow.ingresarCredencialesMicrosoftSiCorresponde("", "")
    workflow.continuarDescargaConfiguracionSiCorresponde()
    workflow.validarPantallaPrincipal()

    base_page.waitVisible.assert_called_once_with(InicioSesionPage.pantallaPrincipal)


def test_organization_submission_uses_base_page_locator_operations() -> None:
    base_page = _mock_login_page()
    workflow = InicioSesionWorkflow(base_page)
    workflow.estadoSesion = EstadoSesion.LOGIN_REQUIRED

    workflow.completarOrganizacionSiCorresponde("test-organization")

    assert base_page.mock_calls == [
        call.waitVisible(InicioSesionPage.pantallaOrganizacion),
        call.setText(InicioSesionPage.campoOrganizacion, "test-organization"),
        call.click(InicioSesionPage.botonContinuar),
    ]


def test_microsoft_credentials_use_base_page_locator_operations() -> None:
    base_page = _mock_login_page()
    workflow = InicioSesionWorkflow(base_page)
    workflow.estadoSesion = EstadoSesion.LOGIN_REQUIRED

    workflow.ingresarCredencialesMicrosoftSiCorresponde(
        "user@example.invalid", "NOT_A_REAL_PASSWORD"
    )

    assert base_page.mock_calls == [
        call.waitVisible(InicioSesionPage.correoMicrosoft),
        call.setText(InicioSesionPage.correoMicrosoft, "user@example.invalid"),
        call.click(InicioSesionPage.botonSiguienteMicrosoft),
        call.waitVisible(InicioSesionPage.contrasenaMicrosoft),
        call.setText(InicioSesionPage.contrasenaMicrosoft, "NOT_A_REAL_PASSWORD"),
        call.click(InicioSesionPage.botonIniciarSesionMicrosoft),
    ]


def test_reauthentication_preparation_uses_base_page_locator_operations() -> None:
    base_page = _mock_login_page()
    base_page.isDisplayed.return_value = True
    workflow = InicioSesionWorkflow(base_page)
    workflow.estadoSesion = EstadoSesion.REAUTH_REQUIRED

    workflow.prepararReautenticacionSiCorresponde()

    assert base_page.mock_calls == [
        call.isDisplayed(InicioSesionPage.dialogoSesionExpirada),
        call.click(InicioSesionPage.botonAceptarSesionExpirada),
        call.waitVisible(InicioSesionPage.usuarioSesionActual),
        call.click(InicioSesionPage.botonReautenticacion),
    ]


def test_reauthentication_passes_instance_specific_locator_to_page_operation() -> None:
    base_page = _mock_login_page()
    instance_locator = ("id", "test:instance-specific-session-expired-dialog")
    base_page.dialogoSesionExpirada = instance_locator
    base_page.isDisplayed.return_value = False
    workflow = InicioSesionWorkflow(base_page)
    workflow.estadoSesion = EstadoSesion.REAUTH_REQUIRED

    workflow.prepararReautenticacionSiCorresponde()

    assert base_page.mock_calls == [
        call.isDisplayed(instance_locator),
        call.waitVisible(InicioSesionPage.usuarioSesionActual),
        call.click(InicioSesionPage.botonReautenticacion),
    ]


def test_configuration_continuation_uses_page_instance_locators_and_generic_operations() -> None:
    driver = Mock()
    page = _mock_login_page(driver)
    calendar_locator = ("id", "instance:calendar-dialog")
    completion_locator = ("id", "instance:configuration-message")
    continue_locator = ("id", "instance:download-continue")
    page.dialogoCalendario = calendar_locator
    page.mensajeConfiguracionCompleta = completion_locator
    page.botonContinuarDescarga = continue_locator
    _configure_configuration_detection(page)
    workflow = InicioSesionWorkflow(page)
    workflow.estadoSesion = EstadoSesion.LOGIN_REQUIRED

    workflow.continuarDescargaConfiguracionSiCorresponde()

    page.waitUntil.assert_called_once()
    assert page.waitUntil.call_args.args[0] == workflow._detectarResultadoConfiguracion
    assert page.waitUntil.call_args.kwargs["timeout"] == (
        CONFIGURATION_COMPLETION_TIMEOUT_SECONDS
    )
    page.isDisplayed.assert_called_once_with(calendar_locator)
    page.find.assert_called_once_with(completion_locator)
    driver.find_element.assert_called_once_with(*completion_locator)
    page.waitText.assert_not_called()
    page.click.assert_called_once_with(continue_locator)


@pytest.mark.parametrize(
    "lookup_error",
    [NoSuchElementException(), StaleElementReferenceException()],
)
def test_configuration_detection_tolerates_missing_or_stale_message_until_timeout(
    lookup_error: Exception,
) -> None:
    driver = Mock()
    page = _mock_login_page(driver)
    page.isDisplayed.return_value = False
    page.find.side_effect = lookup_error

    def wait_until(condition, timeout):
        result = condition(driver)
        if result is None:
            raise TimeoutException()
        return result

    page.waitUntil.side_effect = wait_until
    workflow = InicioSesionWorkflow(page)
    workflow.estadoSesion = EstadoSesion.LOGIN_REQUIRED

    with pytest.raises(AssertionError, match="completed configuration screen"):
        workflow.continuarDescargaConfiguracionSiCorresponde()

    page.find.assert_called_once_with(InicioSesionPage.mensajeConfiguracionCompleta)
    page.click.assert_not_called()


def test_configuration_detection_does_not_swallow_other_lookup_errors() -> None:
    driver = Mock()
    page = _mock_login_page(driver)
    page.isDisplayed.return_value = False
    page.find.side_effect = RuntimeError("unexpected lookup failure")
    page.waitUntil.side_effect = lambda condition, timeout: condition(driver)
    workflow = InicioSesionWorkflow(page)
    workflow.estadoSesion = EstadoSesion.LOGIN_REQUIRED

    with pytest.raises(RuntimeError, match="unexpected lookup failure"):
        workflow.continuarDescargaConfiguracionSiCorresponde()

    page.click.assert_not_called()


def test_configuration_selects_calendar_before_waiting_for_completion(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    base_page = _mock_login_page()
    driver = base_page.driver
    _configure_configuration_detection(base_page, calendar_visible=True)
    monotonic_values = iter([100.0, 110.25])
    monkeypatch.setattr(
        "modules.inicioSesion.login.inicioSesionWorkflow.monotonic",
        lambda: next(monotonic_values),
    )
    workflow = InicioSesionWorkflow(base_page)
    workflow.estadoSesion = EstadoSesion.LOGIN_REQUIRED

    workflow.continuarDescargaConfiguracionSiCorresponde()

    assert base_page.mock_calls == [
        call.waitUntil(
            workflow._detectarResultadoConfiguracion,
            timeout=CONFIGURATION_COMPLETION_TIMEOUT_SECONDS,
        ),
        call.isDisplayed(InicioSesionPage.dialogoCalendario),
        call.click(InicioSesionPage.primerRadioCalendario),
        call.click(InicioSesionPage.botonAceptarCalendario),
        call.waitText(
            InicioSesionPage.mensajeConfiguracionCompleta,
            "Configuración del dispositivo completa.",
            timeout=CONFIGURATION_COMPLETION_TIMEOUT_SECONDS - 10,
        ),
        call.click(InicioSesionPage.botonContinuarDescarga),
    ]
    driver.find_element.assert_not_called()


@pytest.mark.parametrize("state", [EstadoSesion.ACTIVE, EstadoSesion.REAUTH_REQUIRED])
def test_active_and_reauthentication_skip_configuration(state: EstadoSesion) -> None:
    base_page = _mock_login_page()
    workflow = InicioSesionWorkflow(base_page)
    workflow.estadoSesion = state

    workflow.continuarDescargaConfiguracionSiCorresponde()

    base_page.waitUntil.assert_not_called()
    base_page.isDisplayed.assert_not_called()
    base_page.waitText.assert_not_called()
    base_page.click.assert_not_called()


def test_calendar_failure_does_not_click_final_continue() -> None:
    base_page = _mock_login_page()
    base_page.waitUntil.return_value = ResultadoConfiguracion.CALENDARIO
    base_page.click.side_effect = TimeoutException()
    workflow = InicioSesionWorkflow(base_page)
    workflow.estadoSesion = EstadoSesion.LOGIN_REQUIRED

    with pytest.raises(AssertionError, match="calendar selection"):
        workflow.continuarDescargaConfiguracionSiCorresponde()

    base_page.click.assert_called_once_with(InicioSesionPage.primerRadioCalendario)


def test_login_required_route_runs_organization_credentials_and_configuration() -> None:
    base_page = _mock_login_page()
    _configure_configuration_detection(base_page)
    workflow = InicioSesionWorkflow(base_page)
    workflow.estadoSesion = EstadoSesion.LOGIN_REQUIRED

    workflow.completarOrganizacionSiCorresponde("test-organization")
    workflow.prepararReautenticacionSiCorresponde()
    workflow.ingresarCredencialesMicrosoftSiCorresponde(
        "user@example.invalid", "NOT_A_REAL_PASSWORD"
    )
    workflow.continuarDescargaConfiguracionSiCorresponde()
    workflow.validarPantallaPrincipal()

    page_operations = [
        mock_call
        for mock_call in base_page.mock_calls
        if not mock_call[0].startswith("driver.")
    ]
    assert page_operations == [
        call.waitVisible(InicioSesionPage.pantallaOrganizacion),
        call.setText(InicioSesionPage.campoOrganizacion, "test-organization"),
        call.click(InicioSesionPage.botonContinuar),
        call.waitVisible(InicioSesionPage.correoMicrosoft),
        call.setText(InicioSesionPage.correoMicrosoft, "user@example.invalid"),
        call.click(InicioSesionPage.botonSiguienteMicrosoft),
        call.waitVisible(InicioSesionPage.contrasenaMicrosoft),
        call.setText(InicioSesionPage.contrasenaMicrosoft, "NOT_A_REAL_PASSWORD"),
        call.click(InicioSesionPage.botonIniciarSesionMicrosoft),
        call.waitUntil(
            workflow._detectarResultadoConfiguracion,
            timeout=CONFIGURATION_COMPLETION_TIMEOUT_SECONDS,
        ),
        call.isDisplayed(InicioSesionPage.dialogoCalendario),
        call.find(InicioSesionPage.mensajeConfiguracionCompleta),
        call.click(InicioSesionPage.botonContinuarDescarga),
        call.waitVisible(InicioSesionPage.pantallaPrincipal),
    ]


def test_reauthentication_route_prepares_and_enters_microsoft_credentials() -> None:
    base_page = _mock_login_page()
    base_page.isDisplayed.return_value = False
    workflow = InicioSesionWorkflow(base_page)
    workflow.estadoSesion = EstadoSesion.REAUTH_REQUIRED

    workflow.completarOrganizacionSiCorresponde("")
    workflow.prepararReautenticacionSiCorresponde()
    workflow.ingresarCredencialesMicrosoftSiCorresponde(
        "user@example.invalid", "NOT_A_REAL_PASSWORD"
    )
    workflow.continuarDescargaConfiguracionSiCorresponde()
    workflow.validarPantallaPrincipal()

    assert REAUTHENTICATION_DASHBOARD_TIMEOUT_SECONDS == 180
    assert InicioSesionPage.usuarioSesionActual == (
        "id",
        "com.kata.mobile:id/fragmentCurrentSessionUserTextView",
    )
    assert InicioSesionPage.botonReautenticacion == (
        "id",
        "com.kata.mobile:id/fragmentCurrentSessionFloatingActionButton",
    )
    assert base_page.mock_calls == [
        call.isDisplayed(SESSION_EXPIRED_ALERT),
        call.waitVisible(InicioSesionPage.usuarioSesionActual),
        call.click(InicioSesionPage.botonReautenticacion),
        call.waitVisible(InicioSesionPage.correoMicrosoft),
        call.setText(InicioSesionPage.correoMicrosoft, "user@example.invalid"),
        call.click(InicioSesionPage.botonSiguienteMicrosoft),
        call.waitVisible(InicioSesionPage.contrasenaMicrosoft),
        call.setText(InicioSesionPage.contrasenaMicrosoft, "NOT_A_REAL_PASSWORD"),
        call.click(InicioSesionPage.botonIniciarSesionMicrosoft),
        call.waitVisible(
            InicioSesionPage.pantallaPrincipal,
            timeout=REAUTHENTICATION_DASHBOARD_TIMEOUT_SECONDS,
        ),
    ]


def test_expired_session_alert_is_dismissed_before_reauthentication_and_credentials() -> None:
    base_page = _mock_login_page()
    base_page.isDisplayed.return_value = True
    workflow = InicioSesionWorkflow(base_page)
    workflow.estadoSesion = EstadoSesion.REAUTH_REQUIRED

    workflow.prepararReautenticacionSiCorresponde()
    workflow.ingresarCredencialesMicrosoftSiCorresponde(
        "user@example.invalid", "NOT_A_REAL_PASSWORD"
    )

    assert InicioSesionPage.botonAceptarSesionExpirada == SESSION_EXPIRED_ACCEPT_BUTTON
    assert base_page.mock_calls == [
        call.isDisplayed(SESSION_EXPIRED_ALERT),
        call.click(SESSION_EXPIRED_ACCEPT_BUTTON),
        call.waitVisible(InicioSesionPage.usuarioSesionActual),
        call.click(InicioSesionPage.botonReautenticacion),
        call.waitVisible(InicioSesionPage.correoMicrosoft),
        call.setText(InicioSesionPage.correoMicrosoft, "user@example.invalid"),
        call.click(InicioSesionPage.botonSiguienteMicrosoft),
        call.waitVisible(InicioSesionPage.contrasenaMicrosoft),
        call.setText(InicioSesionPage.contrasenaMicrosoft, "NOT_A_REAL_PASSWORD"),
        call.click(InicioSesionPage.botonIniciarSesionMicrosoft),
    ]


@pytest.mark.parametrize(
    ("method_name", "arguments"),
    [
        ("completarOrganizacionSiCorresponde", ("test-organization",)),
        ("prepararReautenticacionSiCorresponde", ()),
        (
            "ingresarCredencialesMicrosoftSiCorresponde",
            ("user@example.invalid", "NOT_A_REAL_PASSWORD"),
        ),
        ("continuarDescargaConfiguracionSiCorresponde", ()),
    ],
)
def test_unknown_state_raises_before_session_dependent_actions(
    method_name: str,
    arguments: tuple[str, ...],
) -> None:
    base_page = _mock_login_page()
    workflow = InicioSesionWorkflow(base_page)

    with pytest.raises(AssertionError, match="determined application session state"):
        getattr(workflow, method_name)(*arguments)

    assert base_page.mock_calls == []


def test_dashboard_validation_runs_even_while_state_is_unknown() -> None:
    base_page = _mock_login_page()
    workflow = InicioSesionWorkflow(base_page)

    workflow.validarPantallaPrincipal()

    base_page.waitVisible.assert_called_once_with(InicioSesionPage.pantallaPrincipal)


def test_configuration_does_not_click_before_final_text_is_reached() -> None:
    driver = Mock()
    driver.current_package = APP_PACKAGE
    driver.current_activity = ".login.download.DownloadActivity"
    base_page = _mock_login_page(driver)
    base_page.waitUntil.side_effect = TimeoutException()
    workflow = InicioSesionWorkflow(base_page)
    workflow.estadoSesion = EstadoSesion.LOGIN_REQUIRED

    with pytest.raises(AssertionError, match="completed configuration screen"):
        workflow.continuarDescargaConfiguracionSiCorresponde()

    base_page.click.assert_not_called()


def test_configuration_does_not_click_when_completion_text_wait_times_out() -> None:
    base_page = _mock_login_page()
    base_page.waitUntil.return_value = ResultadoConfiguracion.CALENDARIO
    base_page.waitText.side_effect = TimeoutException()
    workflow = InicioSesionWorkflow(base_page)
    workflow.estadoSesion = EstadoSesion.LOGIN_REQUIRED

    with pytest.raises(AssertionError, match="completed configuration screen"):
        workflow.continuarDescargaConfiguracionSiCorresponde()

    assert base_page.click.call_args_list == [
        call(InicioSesionPage.primerRadioCalendario),
        call(InicioSesionPage.botonAceptarCalendario),
    ]


def test_reauthentication_does_not_click_when_current_session_anchor_is_missing() -> None:
    driver = Mock()
    driver.current_package = APP_PACKAGE
    driver.current_activity = ".login.LoginActivity"
    base_page = _mock_login_page(driver)
    base_page.isDisplayed.return_value = False
    base_page.waitVisible.side_effect = TimeoutException()
    workflow = InicioSesionWorkflow(base_page)
    workflow.estadoSesion = EstadoSesion.REAUTH_REQUIRED

    with pytest.raises(AssertionError, match="current-session screen"):
        workflow.prepararReautenticacionSiCorresponde()

    base_page.click.assert_not_called()
