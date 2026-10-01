"""Locator declarations for the Katamobile login flow."""

from appium.webdriver.common.appiumby import AppiumBy

from core.basePage import BasePage


class InicioSesionPage(BasePage):
    dialogoSesionExpirada = (
        AppiumBy.XPATH,
        '//*[@resource-id="android:id/message" and @text="Su sesión expiró, '
        'por seguridad de la cuenta ingrese sus datos nuevamente."]',
    )
    botonAceptarSesionExpirada = (
        AppiumBy.XPATH,
        '//*[@resource-id="android:id/button1" and @text="ACEPTAR"]',
    )
    pantallaOrganizacion = (AppiumBy.ID, "com.kata.mobile:id/fragmentTenantConstraintLayout")
    campoOrganizacion = (AppiumBy.ID, "com.kata.mobile:id/fragmentTenantTextInputEditText")
    botonContinuar = (AppiumBy.ID, "com.kata.mobile:id/fragmentTenantContinueButton")
    usuarioSesionActual = (
        AppiumBy.ID,
        "com.kata.mobile:id/fragmentCurrentSessionUserTextView",
    )
    botonReautenticacion = (
        AppiumBy.ID,
        "com.kata.mobile:id/fragmentCurrentSessionFloatingActionButton",
    )
    correoMicrosoft = (AppiumBy.XPATH, '//android.widget.EditText[@resource-id="i0116"]')
    botonSiguienteMicrosoft = (
        AppiumBy.XPATH,
        '//android.widget.Button[@resource-id="idSIButton9" and @text="Siguiente"]',
    )
    contrasenaMicrosoft = (AppiumBy.XPATH, '//android.widget.EditText[@resource-id="i0118"]')
    botonIniciarSesionMicrosoft = (
        AppiumBy.XPATH,
        '//android.widget.Button[@resource-id="idSIButton9" and @text="Iniciar sesión"]',
    )
    dialogoCalendario = (AppiumBy.ID, "com.kata.mobile:id/custom")
    primerRadioCalendario = (
        AppiumBy.XPATH,
        '(//*[@resource-id="com.kata.mobile:id/custom"]//android.widget.RadioButton)[1]',
    )
    botonAceptarCalendario = (
        AppiumBy.XPATH,
        '//*[@resource-id="com.kata.mobile:id/custom"]//android.widget.TextView[@text="OK"]/..',
    )
    mensajeConfiguracionCompleta = (
        AppiumBy.ID,
        "com.kata.mobile:id/activityDownloadMessageTextView",
    )
    botonContinuarDescarga = (
        AppiumBy.ID,
        "com.kata.mobile:id/activityDownloadContinueButton",
    )
    pantallaPrincipal = (
        AppiumBy.ID,
        "com.kata.mobile:id/activityOrdersCoordinatorLayout",
    )
