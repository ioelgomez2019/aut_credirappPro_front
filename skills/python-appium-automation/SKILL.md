---
name: python-appium-automation
description: "Trigger: Python, Appium, Page/Workflow, locator, button names, function decomposition. Apply this repository's automation conventions to coding and review."
license: Apache-2.0
metadata:
  author: repository-maintainers
  version: "1.0"
---

## Activation Contract
Activate for this repository's Python/Appium coding or review involving Page/Workflow, locators, button names, or function decomposition.

## Hard Rules
- Keep `*Page` classes as locator catalogs; inherit cross-screen behavior from `BasePage`, with no screen-action wrappers.
- Let Workflow own most orchestration, state/branch decisions, and UI action order. Inject one Page instance for both locator reads and generic Page operations.
- Keep reusable waits/interactions in `BasePage`/helpers. Catch narrow exceptions with actionable diagnostics. Preserve behavior/APIs unless authorized; Workflow tests must prove order, gating, and error translation.
- Use lower camelCase for methods/variables; start methods with infinitive actions. Use PascalCase classes, no `cls` prefix. Prefix locator attributes with semantic types (`btn`, `txt`, `rdo`, `lbl`, etc.) and descriptive camelCase. Follow repository Python syntax, comments, indentation, and descriptive names; avoid Hungarian prefixes. Do not mass-rename APIs unless in scope.
- Put focused private helpers before public entry points. Split functions when multiple stages or decisions hide behavior. Group by cohesion, not line count; avoid one-line helper sprawl.
- Treat these C#-only constructs in supplied .NET guidance as inapplicable to Python/Appium: `cls...` class prefixes, Hungarian type prefixes, stored procedure APIs, `.cs` naming, and MessageBox rules.

## Decision Gates
| Concern | Owner/action |
|---|---|
| Locator declaration | Page |
| Screen decisions/action order | Workflow |
| Reusable waits/interactions | `BasePage`/helpers |
| Long function | Split hidden stages/decisions, not by line count |

## Execution Steps
1. Read the target Page/Workflow and `BasePage` patterns.
2. Assign concerns to their proper owners; preserve names/APIs unless authorized.
3. Make a cohesive change; update focused Workflow tests.
4. Check behavior, exceptions, diagnostics, naming, and results.

## Output Contract
Report changed components, behavior/API impact, checks, and gaps.

## References
- `modules/inicioSesion/login/inicioSesionPage.py` — locator-only Page example.
- `modules/inicioSesion/login/inicioSesionWorkflow.py` — Workflow orchestration example.
- `core/basePage.py` — generic Page operations.
- `odd/tasks/python-appium-automation-standards.md` — repository task scope and selected conventions.
