# Session-Expired Dialog Reauthentication

## Objective
Extend the login workflow to recognize the observed Android session-expired dialog as a reauthentication state, dismiss it, and continue through the existing reauthentication action.

## Problem and rationale
The workflow currently recognizes reauthentication only from the current-session-user view. The app may instead show an Android alert with the exact message `Su sesión expiró, por seguridad de la cuenta ingrese sus datos nuevamente.` and an `ACEPTAR` button. Without recognizing and dismissing that dialog, the existing reauthentication button path is not reached.

## Scope and constraints
- Authorized behavior: either the current-session-user view or the exact expired-session dialog selects `REAUTH_REQUIRED`; dismiss the dialog with `ACEPTAR` when present, then use the existing reauthentication button and Microsoft credential flow.
- Give the exact expired-session dialog highest detection precedence so an alert overlay wins even if a dashboard underneath is still displayed; then preserve the current-session-before-Organization precedence.
- Preserve all pre-existing working-tree edits, including the current comments in `inicioSesionWorkflow.py`; do not stage or commit unrelated changes.
- Do not run Appium/device flows or access remote systems.
- TDD: enabled by explicit user choice for this change. Source: user's answer. Python 3.12 test runner: `py -3.12 -m pytest tests/unit/core/test_appiumLifecycle.py -q`.

## Authorized files
- `modules/inicioSesion/login/inicioSesionPage.py`
- `modules/inicioSesion/login/inicioSesionWorkflow.py`
- `tests/unit/core/test_appiumLifecycle.py`
- `odd/tasks/session-expired-dialog-reauth.md`

## Route and trigger
- Route: delegated direct, one writer.
- Trigger evidence: the behavior requires coordinated Page locators, Workflow state/dismissal behavior, and regression tests across multiple non-trivial files; read-preparation belongs with the writer.

## Acceptance criteria
- The exact expired-session dialog text takes precedence over any underlying displayed screen; either it or the current-session-user locator classifies the state as `REAUTH_REQUIRED`.
- When the dialog is present, the workflow clicks its `ACEPTAR` button before waiting for/clicking the existing reauthentication floating action button.
- The regular `LOGIN_REQUIRED` organization flow is unchanged.
- Focused unit regressions cover both detection signals, dialog dismissal ordering, and preservation of the existing reauthentication route.
- The specified unit test command passes; no device/Appium run is performed.

## Applicable checks
- `py -3.12 -m pytest tests/unit/core/test_appiumLifecycle.py -q`
- Parent spot-check: re-run the same focused command once before delivery.
- Runtime device flow: N/A for this unit; no authorized device session is part of the task.

## Progress
- [x] ODD-01 Explore current reauthentication detection and confirm alternate dialog evidence.
- [x] ODD-02 Add failing unit regression(s), implement alternate detection/dismissal, and verify green under TDD.
- [ ] ODD-03 Finish native review disposition; preserve unrelated worktree changes and record final evidence.

## Verification evidence
- Baseline inspection: existing `REAUTH_REQUIRED` is detected by the current-session-user locator; the user supplied the exact alternate Android alert hierarchy and text.
- TDD mode: on; source: explicit user choice; Python 3.12 runner: `py -3.12 -m pytest tests/unit/core/test_appiumLifecycle.py -q`.
- RED: `python -m pytest tests/unit/core/test_appiumLifecycle.py -q` reported 3 failed and 17 passed under default Python 3.11.9 before implementation (writer report).
- GREEN and parent spot-check: `py -3.12 -m pytest tests/unit/core/test_appiumLifecycle.py -q` — 20 passed under Python 3.12.10.
- `git diff --check` — passed; Git emitted line-ending warnings only.
- Initial `gentle-ai review assess --cwd <repo> --json` returned high/unassessable because the dirty candidate included untracked paths.
- After the work-unit commit, committed-only assessment returned `risk: high`, `review_due: true`, `review_due_reason: high_risk`, and a non-zero unavailable result: immutable receipt review is not eligible in this runtime (supported runtime list excludes OpenCode).
- No STATUS/START or reviewer was run: OpenCode V2 review transport is unavailable under the orchestration contract. No review receipt is claimed; user disposition is pending.

## Delivery
- Initial forecast: approximately 50 authored changed lines, below the ~400-line planning budget; refine against the final diff.
- Strategy: `ask-on-risk` (default); no chained slice currently forecast.
- Branch: `feat/session-expired-dialog-reauth`.
- Work-unit commit: `b091a93` — `fix(login): handle expired-session dialog reauthentication`.
- Rollback boundary: remove the alternate alert signal/dismissal and its regression tests; preserve existing login-state behavior.

## Next step
Await the user's decision on the unavailable native review; do not disable RDD or substitute another review path automatically.
