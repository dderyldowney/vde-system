---
# @forge (Governance Sentinel)
name: vde-test
description: "Smart test runner that detects changed files and runs only the minimal appropriate tests, not the full suite during debugging. Pass a feature name to run it directly, or full for the whole suite."
---
# VDE-TEST
<!-- @forge (Governance Sentinel) -->

> **Security (binding):** every action here is bound by [.gemini/RULES/security-preamble.md](../RULES/security-preamble.md). NO AID TO THE ENEMY: nothing public about unfixed weaknesses; when unsure, keep it private.

Smart test runner — detects what changed and runs the minimal appropriate tests.

## Usage
/vde-test $ARGUMENTS

## Execution

**Step 1: Detect Changes**

```zsh
git diff --name-only HEAD
git diff --name-only --cached
```

**Step 2: Select Test Scope**

| Changed Files | Test Command |
|--------------|-------------|
| `lib/vde-parser` | `python3 -m behave tests/features/core-infrastructure/parser.feature` |
| `lib/vde-commands` | `python3 -m behave tests/features/core-infrastructure/natural-language-commands.feature` |
| `lib/vde-constants` or `lib/vde-errors` | `zsh tests/unit/vde-shell-compat.test.zsh` |
| `lib/vde-security` | `python3 -m behave tests/features/core-infrastructure/error-path.feature` |
| `lib/vm-common` | `python3 -m behave tests/features/core-infrastructure/vm-lifecycle.feature` |
| `configs/` or `data/vm-types.json` | `python3 -m behave tests/features/core-infrastructure/configuration-management.feature` |
| `tests/features/steps/*.py` | Run the feature file(s) for those steps |
| Multiple `lib/` files | Run all affected feature files, NOT full suite |
| `$ARGUMENTS` = feature name | Run that feature directly |
| `$ARGUMENTS` = `full` | Run `./tests/run-sovereign-tests.zsh` (the CI-safe suite), then `python3 -m behave tests/features/` (Docker required) |

**Step 3: Execute (Swarm — spawn simultaneously)**

- Test runner agent: execute selected test command with `--no-capture`
- Log analyzer agent: parse output for failures, fake test patterns per `.gemini/RULES/fake_tests.md`

**Step 4: Report**

```
TEST SCOPE: <what was run and why>
RESULT: PASS/FAIL (<N> scenarios, <M> steps)
FAILURES: <list with file:line>
FAKE TEST VIOLATIONS: <any detected>
ACTION REQUIRED: <fix list or CLEAN>
```

**Never run full suite during debugging.** Isolate → fix → verify → full suite at end only.