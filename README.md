# AutomationCredirappPro

Suite de automatización de interfaz Android para Katamobile, construida con Python 3.12, Appium, UiAutomator2, pytest y pytest-bdd. La porción funcional implementada se concentra en el inicio de sesión; campañas y el recorrido E2E siguen pendientes. La estructura actual es modular y orientada a pruebas con Page y Workflow; no constituye una arquitectura Clean o Hexagonal completa.

## Estado y alcance

- **Implementado:** flujo de inicio de sesión con detección de estado, navegación condicional y validaciones de pantalla; utilidades compartidas de interacción y espera.
- **Pendiente:** comportamiento de campañas y recorrido E2E. Sus pruebas funcionales y E2E están marcadas como omitidas.
- **Sin capas de negocio completas:** `repositories/`, `services/`, `config/database/` y `stores/` contienen archivos iniciales, pero aún no implementan persistencia, integración ni contratos de datos de negocio.
- **Evidencia:** el código y las pruebas unitarias simuladas describen la implementación; no demuestran por sí solos una ejecución exitosa en un dispositivo real.

## Estructura del repositorio

```text
.
├── config/
│   ├── android/                         # Capacidades y comprobación previa del dispositivo
│   ├── database/                        # Esqueleto de configuración/conexión
│   ├── environment.py                    # Carga configuración del .env raíz
│   └── runnerConfig.py                  # Esperas y tiempos de espera
├── core/
│   ├── appiumServerManager.py           # Comprobación de disponibilidad de Appium
│   ├── basePage.py                      # Operaciones comunes de interfaz
│   ├── driverFactory.py                 # Creación de sesiones Appium
│   ├── components/                      # Reservado; sin componentes transversales implementados
│   ├── constants/                       # Reservado; sin catálogo transversal implementado
│   ├── hooks/                           # Ciclo de vida y capturas de pantalla
│   ├── reporting/                       # Informes BDD y adjuntos
│   └── utils/                           # Búsqueda de elementos e interacciones reutilizables
├── modules/
│   ├── inicioSesion/
│   │   └── login/
│   │       ├── inicioSesion.feature      # Escenarios BDD
│   │       ├── inicioSesionSteps.py      # Enlace entre Gherkin y Workflow
│   │       ├── inicioSesionWorkflow.py   # Orquestación del inicio de sesión
│   │       └── inicioSesionPage.py       # Catálogo de localizadores
│   └── campañas/                         # Estructura inicial; comportamiento pendiente
├── flows/e2e/                            # Esqueleto del recorrido E2E; prueba omitida
├── repositories/                         # Archivos iniciales, sin persistencia de negocio
├── services/                             # Archivos iniciales, sin integración de negocio
├── stores/
│   ├── files/README.md                   # Área de almacenamiento documentada, pendiente
│   └── regions/README.md                 # Área de almacenamiento documentada, pendiente
├── tests/
│   ├── functional/
│   │   ├── inicioSesion/
│   │   │   └── test_inicioSesion.py      # Entrada pytest-bdd
│   │   └── campañas/                     # Pruebas marcadas como omitidas
│   ├── unit/core/                        # Pruebas unitarias con dependencias simuladas
│   └── e2e/                              # Prueba inicial marcada como omitida
├── scripts/
│   ├── runTests.ps1                      # Ejecución con carpeta de resultados fechada
│   └── serveAllure.ps1                   # Generación y servicio local del informe Allure
├── testedApps/README.md                  # Requisito de instalación externa de Katamobile
├── skills/python-appium-automation/SKILL.md # Convenciones de Page y Workflow
├── reporting/                            # Salida generada; resultados e informes
├── conftest.py                           # Fixtures pytest y configuración de informes
├── pytest.ini                            # Descubrimiento y marcas de pytest
├── pyproject.toml                         # Metadatos, requisito de Python y dependencias
├── requirements.txt                      # Dependencias Python
└── Jenkinsfile                            # Pipeline de CI
```

La aplicación Katamobile no está incluida en el repositorio: `testedApps/README.md` indica que debe estar instalada en el dispositivo de destino. No se incluye el APK.

## Diseño y responsabilidades

El recorrido principal es:

`pytest` → `tests/functional/inicioSesion/test_inicioSesion.py` → `modules/inicioSesion/login/inicioSesion.feature` y `inicioSesionSteps.py` → `InicioSesionWorkflow` → `InicioSesionPage` → `BasePage` y `core/utils/` → Appium.

- **pytest y pytest-bdd:** el archivo de prueba carga el Feature y registra las definiciones de pasos.
- **Steps:** conectan los pasos BDD con el Workflow, sin asumir la coordinación de la interfaz.
- **Workflow:** decide el estado visible, las ramas de navegación y el orden de las acciones.
- **Page:** `InicioSesionPage` hereda de `BasePage` y declara localizadores; el Page no es dueño de la secuencia del flujo.
- **BasePage y utilidades:** concentran búsqueda de elementos, esperas, interacciones y controles genéricos reutilizables.
- **Sesión Android:** `conftest.py` solicita una sesión a `DriverFactory`. La fábrica comprueba el estado de Appium y la disponibilidad del dispositivo mediante ADB, crea una sesión Android/UiAutomator2 y la fixture siempre la cierra al terminar la prueba.
- **Hooks e informes:** `core/hooks/` y `core/reporting/` gestionan capturas y adjuntos BDD. Los resultados generados se guardan bajo `reporting/`.

## Flujo de inicio de sesión

El Workflow contempla la pantalla de organización, autenticación de Microsoft, reautenticación cuando la sesión expiró, configuración/calendario opcional y validación de la pantalla principal. Las credenciales no se documentan aquí.

La existencia de estas ramas en el código no equivale a una comprobación en dispositivo de cada una. Las pruebas unitarias disponibles simulan dependencias; para validar el comportamiento real se necesita ejecutar las pruebas con Appium, ADB, un dispositivo configurado y Katamobile ya instalada.

## Requisitos y configuración en Windows

Se necesita:

- Python **3.12** (el proyecto declara `>=3.12,<3.13`).
- Appium Server **3.x**, con el controlador UiAutomator2 instalado en el entorno anfitrión.
- Android SDK Platform Tools (`adb`) disponible en `PATH`.
- Un emulador Android activo o un dispositivo conectado cuyo identificador local corresponda a `ANDROID_DEVICE_UDID`.
- Katamobile instalada previamente en ese destino.

Android Studio no es requisito para ejecutar las pruebas. Git y Jenkins se usan para control de versiones y CI.

Desde la raíz del repositorio, usar Python 3.12 para crear el entorno virtual e instalar las dependencias. El proyecto requiere Python `>=3.12,<3.13`; un entorno virtual no instala Python. Si el comando de verificación no encuentra Python 3.12, instalá Python 3.12.x antes de continuar:

```powershell
py -3.12 --version
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

No hace falta activar el entorno ni cambiar de carpeta: los comandos de prueba usan directamente el Python de `.venv`. Si preferís escribir `python`, podés activar el entorno en cada terminal nueva con `& .\.venv\Scripts\Activate.ps1`. No uses `py -3.12 -m pytest` para estas pruebas: ese comando puede ejecutar el Python global en vez del entorno del proyecto.

En una copia nueva, crear el archivo local de configuración a partir de la plantilla:

```powershell
Copy-Item .env.example .env
```

La aplicación importa `config.environment` directamente; ese loader está versionado y carga el `.env` explícito de la raíz del repositorio. El archivo `.env` está ignorado por Git y contiene los valores locales de `APPIUM_SERVER_URL`, `ANDROID_DEVICE_UDID` y la configuración de base de datos. Las variables ya definidas en el proceso tienen precedencia sobre los valores de `.env`. `.env` contiene configuración y se carga automáticamente; no es el entorno de Python ni se activa. No compartas el archivo local ni agregues credenciales reales a `.env.example`.

Iniciar o conectar el dispositivo configurado y comprobar que ADB lo detecte:

```powershell
adb devices
```

El identificador configurado debe aparecer con el estado `device`. En el entorno anfitrión, iniciar Appium 3 con UiAutomator2:

```powershell
appium --address 0.0.0.0 --port 4723 --allow-cors --use-plugins=inspector
```

La sesión de prueba se conecta al endpoint definido en `APPIUM_SERVER_URL` y comprueba su ruta `/status` antes de crear la sesión Android.

## Ejecutar pruebas

Prueba enfocada de inicio de sesión y selección por marca:

```powershell
.\.venv\Scripts\python.exe -m pytest -m "funcional and adn"
.\.venv\Scripts\python.exe -m pytest tests/functional/inicioSesion/test_inicioSesion.py -v
.\.venv\Scripts\python.exe -m pytest -m smoke -v
.\.venv\Scripts\python.exe -m pytest -m functional
.\.venv\Scripts\python.exe -m pytest -m unit
.\.venv\Scripts\python.exe -m pytest -m e2e
```

`pytest -m functional` incluye la entrada del inicio de sesión y las pruebas de campañas, que están omitidas. `pytest -m unit` ejecuta las pruebas unitarias aisladas; no necesita una sesión Android. `pytest -m e2e` selecciona actualmente un esqueleto omitido, no un recorrido E2E implementado. La ejecución completa con `pytest` también incluye el flujo funcional y requiere Appium, ADB, un dispositivo y la aplicación instalada.

Para crear una carpeta fechada y conservar resultados por ejecución:

```powershell
.\scripts\runTests.ps1 -TestType funcional
```

El script usa `-TestType` tanto como filtro `pytest -m` como prefijo de la carpeta. El ejemplo conserva la marca `funcional` registrada en `pytest.ini`; para seleccionar pruebas marcadas `functional`, se puede indicar `-TestType functional`. Cada ejecución produce `reporting/<marca>_YYYYMMDD_HHMMSS/` con resultados Allure; las carpetas generadas están ignoradas por Git.

## Allure e informes generados

pytest escribe resultados Allure en:

```powershell
.\.venv\Scripts\python.exe -m pytest --alluredir=reporting/allureResults
```

Con la herramienta de línea de comandos de Allure instalada, consultar o generar un informe:

```powershell
allure.cmd serve reporting/allureResults
allure.cmd generate reporting/allureResults --clean -o reporting/allureReport
```

El complemento `allure-pytest-bdd` figura entre las dependencias Python; la CLI de Allure se instala por separado. Para mantener un informe local acumulado, iniciar el servidor en una terminal y ejecutar pruebas en otra:

```powershell
.\scripts\serveAllure.ps1
.\scripts\runTests.ps1 -TestType funcional
```

El informe se sirve en `http://127.0.0.1:8080/`. `runTests.ps1` crea resultados por ejecución y los acumula en `reporting/allureResults/`; `serveAllure.ps1` vuelve a generar el informe acumulado en `reporting/allureReport/`. Los hooks guardan capturas de los pasos BDD y de los errores en `screenshots/` dentro de la carpeta fechada de esa ejecución, y las adjuntan a Allure cuando hay una sesión y el complemento está disponible. `reporting/logs/` es una ubicación ignorada por Git para registros si se configura su escritura.

## Jenkins

`Jenkinsfile` crea un entorno virtual con Python 3.12 en agentes Windows o Unix, instala `requirements.txt`, ejecuta `pytest -m smoke` y publica JUnit XML. Declara como artefactos `reporting/allureResults/**` y `reporting/screenshots/**`. Las capturas se escriben bajo `AUTOMATION_REPORT_DIR/screenshots` (por defecto, dentro de una carpeta fechada), por lo que el patrón fijo de capturas de Jenkins puede no coincidir con la ubicación generada. El loader `config.environment` está versionado; el agente debe proporcionar `APPIUM_SERVER_URL` y `ANDROID_DEVICE_UDID` en su entorno de proceso o en un `.env` local. Jenkins **no** instala ni inicia Appium, no configura ADB o el dispositivo y no instala Katamobile: esos requisitos deben estar disponibles previamente en el agente.

## Convenciones de automatización

Las convenciones completas están en [`skills/python-appium-automation/SKILL.md`](skills/python-appium-automation/SKILL.md). En síntesis: mantener las clases Page como catálogos de localizadores; dejar la orquestación, las decisiones de estado y el orden de acciones en Workflow; reutilizar esperas e interacciones desde `BasePage` y `core/utils/`; dividir funciones largas según sus etapas o decisiones cohesivas; usar métodos en `camelCase` y prefijos semánticos de localizador como `btn` y `txt`.
#   a u t _ c r e d i r a p p P r o _ f r o n t  
 