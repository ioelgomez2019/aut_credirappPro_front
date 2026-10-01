# README: Real Project Architecture in Spanish

## Objective
Expand the root README in professional Spanish with an accurate map of the current AutomationCredirappPro repository, its implemented login automation, setup, execution, reporting, and unfinished scaffolds.

## User decisions
- Write the README in Spanish.
- Use the supplied tree only as a formatting example; document the real repository and its actual layer boundaries.

## Scope and constraints
- Rewrite only `README.md`; preserve the already-staged local environment-configuration changes and all other repository/index state.
- Distinguish implemented code from placeholders/skipped tests; do not claim device-runtime success from static or unit evidence.
- Do not read local environment secrets, include credentials, change application code, run tests/Appium/device flows, stage, commit, push, or access remotes.
- The README is a Spanish human-facing artifact; the task record remains English.

## Route and trigger
- Route: delegated direct, one mapper followed by one README writer.
- Trigger evidence: the architecture spans more than four files and the existing README content needs repository-wide context before editing.

## Acceptance criteria
- The README explains the real pytest → feature → Steps → Workflow → Page → BasePage/helpers → Appium path and the driver/reporting lifecycle.
- The directory tree reflects actual paths and marks campaigns, E2E, repositories, services, and data stores as scaffolding where appropriate.
- It retains accurate Python/Appium/device, local configuration, test, Allure, and Jenkins instructions, including already-staged README content.
- It links to the project coding skill and avoids secrets, unsupported behavior claims, and invented packages.
- No application source or staged state is changed.

## Tasks
- [x] README-01: Map current repository structure and verify architecture claims against source paths.
- [x] README-02: Rewrite the root README in Spanish using the evidence-backed map.
- [x] README-03: Read back the README, verify paths/commands and staged-change preservation, and record remaining limitations.

## Verification
- The delegated architecture map distinguished the implemented login slice from campaigns/E2E and persistence/integration scaffolds; it did not inspect secret-bearing configuration or Gherkin values.
- Read back the Spanish README, including the actual login feature, Steps, Workflow, Page, and functional-test file paths. It documents pytest-BDD → Steps → Workflow → Page → BasePage/helpers → Appium, driver/reporting lifecycle, local setup, test scopes, Allure, Jenkins, and the project skill.
- Parent spot-check: `git diff --check -- README.md` and `git diff --cached --check -- README.md` both exited 0 (Git emitted only its LF-to-CRLF working-copy warning).
- Parent path spot-check passed for the paths shown in the README tree; pytest markers, `runTests.ps1`, and Jenkins commands were read back against their source configuration.
- The pre-existing staged README diff is unchanged; the Spanish rewrite is only a worktree delta. Other staged/uncommitted repository changes remain intact.
- Removed the writer-created `.codegraph/` directory; `config/environmentExample.py` remains present. No application source, source tests, Appium, or device flows were run.

## Delivery
- Do not stage, commit, or push without explicit authorization.
- Rollback boundary: revert only the README rewrite while preserving the pre-existing staged README and repository changes.

## Next step
README rewrite and structural verification are complete. Keep the rewrite local and unstaged; do not commit or push without explicit authorization.
