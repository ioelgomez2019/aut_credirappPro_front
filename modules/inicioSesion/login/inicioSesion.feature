Feature: Inicio de sesión

  @loguin @funcional @smoke
  Scenario Outline: Completar el inicio de sesión para la organización <organizacion>
    Given el dispositivo Android está disponible
    When el usuario abre la aplicación
    And se determina el estado de la sesión
    And completa la organización "<organizacion>" si corresponde
    And prepara la reautenticación si corresponde
    And el usuario ingresa sus credenciales válidas de Microsoft "<usuario>" y "<contrasena>"
    And continúa al finalizar la configuración si corresponde
    Then visualiza la pantalla principal

    @adn
    Examples:
      | organizacion | usuario                 | contrasena               |
      | andesqa      | laliaga@craclasadev.com | Test#1234                |

    @jefeoficina
    Examples: Jefe de oficina
      | organizacion | usuario                 | contrasena               |
      | andesqa      | laliaga@craclasadev.com | Test#1234                |
  