"""Step definitions delegate Gherkin behavior to the login Workflow."""

from pytest_bdd import given, parsers, then, when

from modules.inicioSesion.login.inicioSesionWorkflow import InicioSesionWorkflow


@given("el dispositivo Android está disponible")
def dispositivo_android_disponible(inicioSesionWorkflow: InicioSesionWorkflow) -> None:
    inicioSesionWorkflow.verificarDispositivoAndroid()


@when("el usuario abre la aplicación")
def usuario_abre_aplicacion(inicioSesionWorkflow: InicioSesionWorkflow) -> None:
    inicioSesionWorkflow.abrirAplicacion()


@when("se determina el estado de la sesión")
def se_determina_estado_sesion(inicioSesionWorkflow: InicioSesionWorkflow) -> None:
    inicioSesionWorkflow.determinarEstadoSesion()


@then("se muestra la pantalla de inicio de sesión")
def se_muestra_pantalla_inicio_sesion(inicioSesionWorkflow: InicioSesionWorkflow) -> None:
    inicioSesionWorkflow.validarPantallaInicioSesion()


@when(parsers.parse('completa la organización "{organizacion}" si corresponde'))
def usuario_completa_organizacion(
    inicioSesionWorkflow: InicioSesionWorkflow, organizacion: str
) -> None:
    inicioSesionWorkflow.completarOrganizacionSiCorresponde(organizacion)


@when("prepara la reautenticación si corresponde")
def usuario_prepara_reautenticacion(
    inicioSesionWorkflow: InicioSesionWorkflow,
) -> None:
    inicioSesionWorkflow.prepararReautenticacionSiCorresponde()


@when(
    parsers.parse(
        'el usuario ingresa sus credenciales válidas de Microsoft "{usuario}" y "{contrasena}"'
    )
)
def usuario_ingresa_credenciales_microsoft(
    inicioSesionWorkflow: InicioSesionWorkflow, usuario: str, contrasena: str
) -> None:
    inicioSesionWorkflow.ingresarCredencialesMicrosoftSiCorresponde(usuario, contrasena)


@when("continúa al finalizar la configuración si corresponde")
def usuario_continua_configuracion(
    inicioSesionWorkflow: InicioSesionWorkflow,
) -> None:
    inicioSesionWorkflow.continuarDescargaConfiguracionSiCorresponde()


@then("visualiza la pantalla principal")
def usuario_visualiza_pantalla_principal(
    inicioSesionWorkflow: InicioSesionWorkflow,
) -> None:
    inicioSesionWorkflow.validarPantallaPrincipal()
