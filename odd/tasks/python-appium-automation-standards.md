# Python Appium Automation Standards Skill

## Objective
Create a project-scoped agent skill that preserves the selected Page/Workflow architecture and naming conventions for Python Appium automation.

## User decisions
- Skill scope: this repository only.
- Adapt the supplied C#/.NET naming guidance to Python: retain camelCase methods, semantic UI locator prefixes such as `btn`, and the Page/Workflow responsibilities; do not impose C# class/type prefixes or C#-only stored-procedure/MessageBox rules on Python.

## Scope and constraints
- Add one reusable `SKILL.md` under the repository's `skills/` directory and a concise root `AGENTS.md` pointer.
- Update the generated skill registry without discarding its existing staged or unstaged content; mirror the refreshed registry to Engram.
- Preserve all pre-existing repository/index changes. Do not change application source, stage files, commit, push, access remotes, or run Appium/device flows.
- Generated technical artifacts use English.

## Route and trigger
- Route: delegated direct, one writer for the skill and agent pointer.
- Trigger evidence: creating two non-trivial agent-facing files and reading existing architecture/style material to prepare them.

## Acceptance criteria
- The skill activates for Python/Appium/Page/Workflow implementation and names its scope precisely.
- It places locators in Page classes, flow decisions and orchestration in Workflow, and recommends focused private helpers for long/multi-responsibility functions.
- It defines the user's adapted Python naming rules, including `btn` locator names, without importing C#-only syntax or Hungarian type prefixes.
- The root `AGENTS.md` points to the skill with an explicit activation condition.
- Registry and Engram mirror include the exact skill path; existing index state is preserved.
- Markdown/frontmatter and referenced paths are checked; no device flow or source tests are needed for this documentation-only change.

## Tasks
- [x] SKILL-01: Write the project skill and root agent pointer; read both back and validate the instruction contract.
- [x] SKILL-02: Register the project skill, synchronize the full registry to Engram, and verify repository/index state.

## Verification
- Read back the new skill and root pointer. The skill has required YAML frontmatter, the prescribed section order, a 155-character description, and four resolving repository-relative references; its body is below the 1,000-token hard limit.
- `gentle-ai skill-registry refresh --force` — success; 155 skills indexed, including `python-appium-automation` with project scope and exact path.
- Registry refresh metadata recorded in Engram under topic `skill-registry`; the full task document mirrored under `odd/python-appium-automation-standards/tasks`; both read back.
- Removed the writer-created `.codegraph/` artifacts and restored `.gitignore` and `config/environmentExample.py` worktrees to their pre-delegation staged state. Existing staged content remains staged; new skill files and this task document remain unstaged/untracked.
- No application source, device/Appium flow, or source tests were run.

## Delivery
- Changes remain local; no stage, commit, or push is authorized.
- Rollback boundary: remove only the new project skill/pointer/task document and its registry/memory entry, preserving all pre-existing repository changes.

## Next step
Skill creation and registration are complete. Keep changes local and unstaged; do not commit or push without explicit authorization.
