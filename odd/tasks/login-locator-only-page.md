# Locator-Only Login Page

## Objective
Keep `InicioSesionPage`'s class body limited to locator declarations, inherit generic UI operations from `BasePage`, and have `InicioSesionWorkflow` use the same login Page instance for both inherited operations and locator access, with private helpers grouped separately from public methods.

## Problem and rationale
The user prefers no screen-action wrappers in `InicioSesionPage`. The selected design makes `InicioSesionPage` inherit `BasePage`, so its class body declares locators while instances reuse generic visibility, wait, text-entry, and click methods. Workflow owns routing and action order and calls inherited operations with locator attributes accessed on that same Page instance, for example `self._page.isDisplayed(self._page.dialogoSesionExpirada)`. `BasePage.click` already accepts a `Locator` tuple and handles clickability before clicking.

## Scope and constraints
- Keep only UI locator declarations in the `InicioSesionPage` class body; inherit from `BasePage` without adding wrappers or overrides.
- Inject one `InicioSesionPage` instance into `InicioSesionWorkflow`; use inherited generic operations and its single underlying driver reference.
- Use the Workflow's single `_page` reference for both inherited operations and locator attributes; do not introduce a separate `self.page` or class-level locator access.
- Keep underscore-prefixed Workflow helpers under the `Private Methods` section and public Workflow methods under `Public Methods`.
- Keep application/activity configuration in `config.environment`.
- Preserve Workflow public methods, BDD Steps, session-state precedence, UI action order, timeout behavior, and existing exception translation.
- Preserve all pre-existing unstaged work, especially the current Workflow and lifecycle-test changes.
- Keep this login correction local and unstaged; no commits, pushes, branch changes, remote access, or Appium/device flows. Preserve the already-staged `config/environment.py` removal from the separate, explicitly approved environment migration; do not alter its index state. Do not toggle RDD.
- TDD remains enabled from the user's explicit choice for this ongoing login Workflow migration; use Python 3.12.

## Authorized files
- `modules/inicioSesion/login/inicioSesionPage.py`
- `modules/inicioSesion/login/inicioSesionWorkflow.py`
- `conftest.py`
- `tests/unit/core/test_appiumLifecycle.py`
- `odd/tasks/login-locator-only-page.md`

## Route and trigger
- Route: delegated direct, one writer.
- Trigger evidence: the migration coordinates Page, Workflow, fixture construction, and public-interface tests across four non-trivial files; preparation and implementation belong with one writer.
- ODD-03 route: delegated direct, one writer. Trigger evidence: Workflow and its regression tests are two non-trivial files, and reading the tests prepares the implementation.
- ODD-04 route: direct inline. Trigger evidence: this is an already-understood mechanical reordering within one file, with no behavior change or test-design work.
- ODD-05 route: delegated direct, one writer. Trigger evidence: removing screen-specific methods from Page, moving their orchestration into Workflow, and updating public-Workflow regression tests spans three non-trivial files.

## Acceptance criteria
- `InicioSesionPage` declares only locators and inherits generic operations from `BasePage` without screen-specific wrappers or overrides.
- Calendar/configuration orchestration lives in Workflow; Page contains only locators while inheriting `BasePage` operations.
- Workflow receives one Page instance and calls its inherited generic operations with Page locators; `BasePage` needs no new button-object abstraction.
- Workflow uses the same Page instance for method and locator lookup (for example, `self._page.isDisplayed(self._page.dialogoSesionExpirada)`).
- Underscore-prefixed helper methods are grouped beneath `Private Methods`; public entry points remain beneath `Public Methods`.
- Session-state routing and all existing login behavior remain unchanged; public Workflow entry points used by BDD Steps remain stable.
- Unit tests exercise public Workflow methods and verify the appropriate BasePage operations/locators.
- Focused tests pass under Python 3.12; no device run is performed.

## Applicable checks
- `py -3.12 -m pytest tests/unit/core/test_appiumLifecycle.py tests/unit/core/test_interactionHelper.py -q`
- Parent spot-check: rerun the focused command once before delivery.
- `git diff --check`
- Runtime device flow: N/A; no device session is authorized for this local refactor.

## Progress
- [x] ODD-01 Convert the login Page to a locator catalog, rewire Workflow and fixtures to use BasePage, update public-interface regressions test-first, and verify the behavior-preserving migration.
- [x] ODD-02 Make `InicioSesionPage` inherit `BasePage`, inject that Page into Workflow, and update public-interface tests test-first while preserving the locator-only class body and behavior.
- [x] ODD-03 Use the injected Page instance consistently for inherited operations and locator access; remove the partial mismatched references and add regression coverage without changing login behavior.
- [x] ODD-04 Move private Workflow helpers beneath `Private Methods` and keep public entry points grouped beneath `Public Methods`, without changing behavior.
- [x] ODD-05 Move calendar/configuration orchestration out of `InicioSesionPage` into `InicioSesionWorkflow`; update tests to exercise the Workflow contract while preserving state gating, ordering, timeouts, and failure behavior.

## Verification evidence
- Baseline before this task: `py -3.12 -m pytest tests/unit/core/test_appiumLifecycle.py -q` — 21 passed.
- TDD source: explicit user selection for the ongoing login Workflow migration; runner: Python 3.12.
- RED/GREEN vertical slices (each focused target was run with `py -3.12 -m pytest tests/unit/core/test_appiumLifecycle.py::<test_name> -q`; each immediate GREEN result was `1 passed`):
  - `test_dashboard_validation_runs_even_while_state_is_unknown`: RED on missing `waitMainScreen` from the BasePage mock; GREEN after switching Workflow to `waitVisible(locator)`.
  - `test_exact_session_expired_alert_wins_over_every_underlying_screen`: RED on missing `waitUntilScreenDetected`; GREEN after routing session detection through BasePage `waitUntil` / `isDisplayed`.
  - `test_login_workflow_accepts_the_relative_login_activity_name`: RED on missing `waitUntilScreenDetected`; GREEN after using BasePage `waitUntil` and environment constants.
  - `test_organization_submission_uses_base_page_locator_operations`: RED on missing `waitOrganization`; GREEN after using BasePage wait, set, and click with Page locators.
  - `test_microsoft_credentials_use_base_page_locator_operations`: RED on missing `waitMicrosoftEmail`; GREEN after using BasePage wait, set, and click operations.
  - `test_reauthentication_preparation_uses_base_page_locator_operations`: RED on missing `isSessionExpiredVisible`; GREEN after using BasePage visibility, wait, and click operations.
  - `test_configuration_continuation_uses_base_page_locator_operations`: RED on missing `waitConfigurationComplete`; GREEN after using BasePage `waitText` and `click`.
- Final focused verification: `py -3.12 -m pytest tests/unit/core/test_appiumLifecycle.py tests/unit/core/test_interactionHelper.py -q` — 27 passed.
- `git diff --check` — exit 0; no whitespace errors (Git emitted only working-copy LF-to-CRLF warnings).
- ODD-01 parent structural readback: passed; Page was locator-only, Workflow used BasePage operations, fixtures injected BasePage directly, and BDD Steps remained unchanged.
- Parent spot-check: `py -3.12 -m pytest tests/unit/core/test_appiumLifecycle.py tests/unit/core/test_interactionHelper.py -q` — 27 passed.
- Parent `git diff --check` — exit 0; existing working-copy line-ending warnings only.
- Parent RDD status: on by default; global and clone-local settings are unset. `gentle-ai review assess --cwd . --json` exited 1 because the untracked task document requires explicit inventory, so the candidate is treated as high/unassessable. OpenCode V2 review transport is unavailable; no review was started and no receipt is claimed.
- The skill registry files `.atl/skill-registry.md` and `.atl/.skill-registry.cache.json` are now modified outside this task's authorized file scope; they were left untouched. The index is empty and HEAD remains `40dc078`; no commit or push occurred.
- Device/Appium verification: not run by explicit scope.
- ODD-01 initially used direct BasePage injection; the user subsequently selected Page inheritance. ODD-02 supersedes only that construction choice and preserves ODD-01's completed behavior/tests.
- ODD-02 Page inheritance tracer: `py -3.12 -m pytest tests/unit/core/test_appiumLifecycle.py::test_inicio_sesion_page_inherits_base_page_locator_operations -q` — RED with `TypeError: InicioSesionPage() takes no arguments`; after subclassing `BasePage`, GREEN with 1 passed. The test instantiates the real Page and calls inherited `isDisplayed` with the session-expired locator.
- ODD-02 Workflow tracer: `py -3.12 -m pytest tests/unit/core/test_appiumLifecycle.py::test_workflow_uses_one_page_for_driver_and_locator_operations -q` — RED with missing `basePage` constructor argument; after switching Workflow to one Page and obtaining its driver from `page.driver`, GREEN with 1 passed.
- ODD-02 final verification first attempt: `py -3.12 -m pytest tests/unit/core/test_appiumLifecycle.py tests/unit/core/test_interactionHelper.py -q` — 1 failed, 28 passed because the open-app test expected no mock calls even though `activate_app` correctly runs through the Page's driver. The assertion was corrected to expect that driver call.
- ODD-02 final focused verification rerun: `py -3.12 -m pytest tests/unit/core/test_appiumLifecycle.py tests/unit/core/test_interactionHelper.py -q` — 29 passed.
- ODD-02 implementation readback: `InicioSesionPage` inherits `BasePage` and its class body contains only locators; Workflow accepts one Page, invokes inherited methods through `_pageInicioSesion`, and uses `page.driver` as its sole driver source. The workflow fixture constructs/injects that Page; environment constants remain in `config.environment`. BasePage/helpers and `inicioSesionSteps.py` were not changed.
- ODD-02 `git diff --check` — exit 0; Git emitted working-copy LF-to-CRLF warnings only.
- CodeGraph lookup attempted before source inspection; `codegraph status` exited 1 because no project index was available. Per the CLI's availability message, no index was initialized; targeted filesystem inspection was used as fallback.
- ODD-02 parent structural readback: passed; Page inheritance, locator-only declarations, single Page injection, fixture construction, and the Page-owned driver source match the selected design.
- ODD-02 parent spot-check: `py -3.12 -m pytest tests/unit/core/test_appiumLifecycle.py tests/unit/core/test_interactionHelper.py -q` — 29 passed, exit 0.
- ODD-02 `git diff --check`: exit 0; Git emitted working-copy LF-to-CRLF warnings only. The task document and its Engram mirror were synchronized and read back.
- No review actor, device run, or review receipt was produced; native OpenCode V2 review transport remains unavailable.
- ODD-02 changes remain local and unstaged; the pre-existing `.atl` registry modifications were left untouched.
- ODD-03 scope was explicitly authorized by the user after ODD-02: the intended expression uses the same Page instance for both the inherited method and locator (`self._page.isDisplayed(self._page.dialogoSesionExpirada)`). The current Workflow contains partial edits with a mismatched `self.page` reference and leftover `_pageInicioSesion` references; preserve the requested design while making the Workflow coherent and syntactically valid.
- ODD-03 public-Workflow regression: `py -3.12 -m pytest tests/unit/core/test_appiumLifecycle.py::test_reauthentication_passes_instance_specific_locator_to_page_operation -q` — RED exited 1 during `conftest.py` import because `inicioSesionWorkflow.py:42` contained `return EstadoSesion.REAUTH_REQUIRED{}`; Python reported `SyntaxError: invalid syntax` at `{}`. The test did not collect or reach an assertion.
- ODD-03 same tracer after implementation: `py -3.12 -m pytest tests/unit/core/test_appiumLifecycle.py::test_reauthentication_passes_instance_specific_locator_to_page_operation -q` — GREEN, 1 passed. The public reauthentication method passed the Page instance's overridden session-expired locator into `isDisplayed`.
- ODD-03 final focused verification: `py -3.12 -m pytest tests/unit/core/test_appiumLifecycle.py tests/unit/core/test_interactionHelper.py -q` — 30 passed.
- ODD-03 `git diff --check` — exit 0; Git emitted only working-copy LF-to-CRLF warnings.
- ODD-03 implementation readback: every Workflow Page operation and locator argument uses the same `self._page`; `self.driver` is still sourced from that Page's `driver`. The invalid return syntax, mismatched `self.page`, old `_pageInicioSesion` references, and obsolete commented call were removed. Workflow public methods, configuration, timeouts, exception translation, and BDD flow were not changed.
- ODD-03 parent structural readback: passed; every inherited operation and locator lookup uses `_page`, with no class-level locator references or separate Page field. The added test proves an instance-specific locator is passed through the public reauthentication method.
- ODD-03 parent spot-check: `py -3.12 -m pytest tests/unit/core/test_appiumLifecycle.py tests/unit/core/test_interactionHelper.py -q` — 30 passed, exit 0.
- ODD-03 parent `git diff --check`: exit 0; only working-copy LF-to-CRLF warnings.
- CodeGraph fallback for ODD-03: `.codegraph/` exists but `codegraph status` and `codegraph explore` reported that no index is available. Per the CLI message, no index was created; targeted filesystem inspection was used after the CodeGraph attempt failed.
- Limitations: no device/Appium flow or broader test suite was run, per scope. The focused tests do not claim device-runtime verification.
- ODD-04 structural readback: `_requires`, `_unexpectedState`, and `_isLoginActivity` are under `Private Methods`; `validarPantallaInicioSesion` remains under `Public Methods`. Only method order changed.
- ODD-04 focused verification: `py -3.12 -m pytest tests/unit/core/test_appiumLifecycle.py tests/unit/core/test_interactionHelper.py -q` — 30 passed, exit 0.
- ODD-04 parent spot-check: the same focused command — 30 passed, exit 0.
- ODD-04 parent `git diff --check`: exit 0; only working-copy LF-to-CRLF warnings.
- During ODD-04 closeout, an out-of-scope change to the default Android device identifier in `config/environment.py` was detected and left untouched. The focused test command was rerun afterward; 30 tests passed.
- ODD-05 exploration confirmed the Page currently contains five calendar/configuration methods plus the `ResultadoConfiguracion` enum; the Workflow's public `continuarDescargaConfiguracionSiCorresponde` delegates to them. The BDD Step calls the stable Workflow method, so Steps and fixtures need no change.
- ODD-05 must preserve calendar-first detection, radio-then-OK order, completion substring check, remaining-time deadline, timeout translation, narrow missing/stale-element handling, and session-state gating. Use the same `self._page` for inherited generic actions and instance locators.
- ODD-05 implementation readback: `InicioSesionPage` now contains locator declarations only and inherits `BasePage`; `ResultadoConfiguracion` and all five calendar/configuration helpers are in Workflow, with orchestration helpers private. The public `continuarDescargaConfiguracionSiCorresponde` and BDD caller remain unchanged; every UI operation and locator comes from the same `self._page` instance.
- ODD-05 TDD: two focused regressions failed before the implementation and passed after it (2 passed). Final writer run and parent spot-check of `py -3.12 -m pytest tests/unit/core/test_appiumLifecycle.py tests/unit/core/test_interactionHelper.py -q`: 40 passed on each run.
- ODD-05 target-file `git diff --check` and the preserved staged environment deletion's cached diff check passed. Repository-wide `git diff --check` returns 2 because the already-dirty, out-of-scope `modules/inicioSesion/login/inicioSesion.feature` has trailing whitespace and a blank line at EOF (line 23); it was left untouched.
- ODD-05 parent cleanup: removed the `.codegraph/` index created by the delegated worker; it was absent before this task. No Appium/device run occurred.
- ODD-05 RDD status is on by default. Native assessment returned high/unassessable because untracked paths require an inventory declaration. OpenCode V2 review transport is unavailable; no review lifecycle was started and no receipt is claimed.

## Delivery
- Forecast: one cohesive local architecture refactor, below the approximate 400-line planning heuristic; refine against the final diff.
- Strategy: `ask-on-risk` default; no PR or commit is authorized.
- Branch: `feat/session-expired-dialog-reauth`.
- Commit: intentionally omitted by explicit user instruction; changes remain unstaged and local.
- Rollback boundary: reverse only the locator-only Page / BasePage-backed Workflow / fixture and focused-test migration; preserve the earlier expired-session and session-detection work.

## Next step
ODD-05 implementation and applicable focused checks are complete. Keep its changes local and unstaged; preserve the separate staged environment-file deletion. Do not commit, push, or run device flows. Native review remains unavailable/unclaimed.
