# Database Connectivity

## Objective
Implement validated database settings and a lazy ODBC connection factory, with strict-TDD unit coverage through the approved public seams. Keep `.env.example` safe and never make a real database connection as part of this task.

## Problem and rationale
At task start, `config/database/settings.py` and `config/database/connection.py` were stubs and the dependency declarations lacked `pyodbc` and `python-dotenv`. The task implemented the settings and factory; a later, separate `local-environment-config` follow-up established the root `.env` loader for local configuration. Production credentials remain externally injected.

## Scope and constraints
- Implement `DatabaseSettings.from_environment()` to load and validate database settings, and `connect_database(settings)` to create and return the ODBC connection.
- Add `pyodbc` and `python-dotenv` to the project dependency declarations. The database task requested loading the ignored root `.env` for local development; the loader was implemented later in `local-environment-config.md`. Production secrets are injected externally.
- Add a root `.env.example` containing safe placeholders only. The original database task did not create a local `.env`; the later `local-environment-config` task did. Keep `.env` ignored.
- Add unit tests for the approved public seams. Mock only the external ODBC driver; do not mock internal database modules or collaborators.
- Do not connect to any database or server, or add a real database/integration test. No network access is authorized.
- Treat the database password previously exposed in chat as compromised. The user must rotate it before any real connection. Never copy its value into a file, task document, prompt, log, memory, or response.
- Confirm database/authentication assumptions in code without recording environment values.
- The original database task excluded Appium migration and edits to `config/environment.py` / `config/environmentExample.py`. Those configuration changes were later completed separately in `local-environment-config.md`.
- Preserve all existing staged and unstaged work. Do not stage, commit, switch branches, push, or perform remote operations; the parent owns any later task-scoped commit decision.

## Accepted design and assumptions
- Approved test seams: public `DatabaseSettings.from_environment()` for settings acquisition/validation and `connect_database(settings)` for connection creation.
- `pyodbc.connect` is the only mocked external seam in unit tests. Tests must exercise the public functions and verify observable configuration/connection behavior without a server.
- Local settings come from environment variables populated from the ignored root `.env`; the `.env.example` and settings must use one consistent variable contract. CI/production values are injected outside the repository.
- `DB_COMMAND_TIMEOUT` is a query timeout: set the returned connection's `.timeout` after connecting. Do not pass it as `pyodbc.connect(timeout=...)`, which is a login timeout.
- Do not expose settings or credentials in logs or exception messages. No live database or authentication verification was performed.

## Route and TDD
- Route: delegated direct, one writer.
- Mandatory delegation trigger evidence: the behavior coordinates database settings, a connection factory, dependency declarations, a safe environment template, and public-seam unit tests; one writer keeps the interface and strict-TDD slices consistent while preserving unrelated work.
- TDD mode: strict.
- TDD source: explicit user selection in this session.
- Test runner: `py -3.12 -m pytest tests/unit -q`.
- Work one public seam and one behavior at a time: establish a failing test, implement the minimum to pass, and repeat. Do not perform a real database test.

## Acceptance criteria
- `DatabaseSettings.from_environment()` validates required database configuration and reports invalid or missing settings without disclosing secret values.
- `connect_database(settings)` builds the SQL Server ODBC connection using the supplied settings and returns the result from the ODBC driver; its unit tests mock only `pyodbc.connect`.
- Unit tests cover settings validation and connection creation through the two approved public seams; no test contacts a server or database.
- `pyodbc` and `python-dotenv` are declared project dependencies.
- Root `.env.example` contains safe placeholders only, and root `.env` remains ignored.
- Appium configuration migration was outside ODD-DB-01 and was completed separately in `local-environment-config.md`.
- `py -3.12 -m pytest tests/unit -q` passes after implementation; no real database test or connection is performed.
- The exposed password is rotated by the user before any future real connection; its value is absent from repository artifacts and logs.

## Applicable checks
- Historical first full run: `py -3.12 -m pytest tests/unit -q` — 1 failed, 51 passed because the initial connection test could not import unavailable `pyodbc`; no package was installed. After the lazy-import/mock-module correction, the writer's run and an independent parent run of the same command each passed (53 tests, exit 0).
- Scoped `git diff --check` passed. `git diff --cached --check` reported pre-existing whitespace at `modules/inicioSesion/login/inicioSesion.feature:23`; it was left unchanged.
- The parent verified `.env` is ignored and `.env.example` and `config/environment.py` are not ignored. The writer reported `.env.example` contains safe placeholders. The parent did not read `.env`.
- Confirm unit tests mock only the ODBC driver and that no database/network connection is attempted.
- Runtime/database verification: N/A; no database or server connection is authorized.

## Progress and evidence
- [x] ODD-DB-01 Implement validated environment-backed settings, the ODBC connection factory, safe dependency/template updates, and public-seam unit tests under strict TDD.
- Added the database settings and connection implementations, declared `pyodbc` and `python-dotenv` in `pyproject.toml` and `requirements.txt`, added a safe-placeholder root `.env.example`, and added public-seam unit tests. No local `.env` was created by this task; it was added later by the separate local-environment-config task.
- TDD settings tracer: the valid-settings test first failed during collection because `DatabaseSettings` was absent; after implementation it passed (1 passed).
- TDD required-setting tracer: the blank `DB_SERVER` test first failed because no `ValueError` was raised; after validation it passed (1 passed).
- TDD timeout tracer: the invalid-timeout cases first failed (3 failed: non-integer diagnostic mismatch, zero accepted, and negative accepted); after validation all passed (3 passed).
- TDD secret-representation tracer: the test first failed because the dataclass representation exposed the password field; after excluding that field from `repr`, it passed (1 passed).
- TDD connection tracer, historical first attempt: collection first failed because `connect_database` was absent; after implementation, the test then failed with `ModuleNotFoundError` because `pyodbc` was unavailable. No dependency was installed.
- Follow-up TDD corrected the import boundary by lazily importing `pyodbc` and testing the factory with a mocked module. The connection test passed without installing the driver or contacting a database. The returned connection receives the query timeout; `DB_COMMAND_TIMEOUT` defaults to 120.
- Current implementation: `DatabaseSettings.from_environment()` validates required settings and a positive timeout, and excludes the password from `repr`. `connect_database(settings)` escapes ODBC string values, lazily imports `pyodbc`, and applies the query timeout to the returned connection.
- The original full-run result of 1 failed/51 passed is historical. The writer and independent parent each ran `py -3.12 -m pytest tests/unit -q` and got 53 passed (exit 0). No database, server, or external connection was made.
- `.gitignore` ignores `.env`; `.env.example` and `config/environment.py` are not ignored. The writer reported `.env.example` contains safe placeholders. A root `.env` now exists from the separate local-environment-config task; the parent deliberately did not read it. The writer reported its `DB_PASSWORD` blank.
- Scoped `git diff --check` passed. The cached check's pre-existing whitespace at `modules/inicioSesion/login/inicioSesion.feature:23` was not changed.

## Delivery
- Initial authored-line forecast: approximately 120–180 changed lines across settings, connection creation, dependency/template updates, and focused tests; refine against the implementation diff.
- Strategy: `ask-on-risk`; pause for parent direction if scope or forecast materially expands. No chained slice is currently forecast.
- No implementation files were staged or committed; no push, branch switch, or remote operation was performed. The workspace still contains pre-existing unrelated staged and unstaged user changes, left untouched. This documentation follow-up also was not staged or committed.

## Next step
ODD-DB-01 implementation and unit verification are complete. No database connection was made. Parent readback and the Engram mirror are handled by the parent after this reconciliation; any future real connection requires separate authorization and a rotated password.
