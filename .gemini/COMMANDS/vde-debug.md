---
# @forge (Governance Sentinel)
name: vde-debug
description: "Debug failing VDE tests or runtime errors with a parallel swarm: classify the failure, run only the failing test, and write a root-cause report with a fix plan for approval."
---
# VDE-DEBUG
<!-- @forge (Governance Sentinel) -->

> **Security (binding):** every action here is bound by [.gemini/RULES/security-preamble.md](../RULES/security-preamble.md). NO AID TO THE ENEMY: nothing public about unfixed weaknesses; when unsure, keep it private.

Debug failing tests or runtime errors in VDE using a parallel swarm.

## Usage
/vde-debug $ARGUMENTS

`$ARGUMENTS` = error description, failing test name, or log snippet.

## Execution

**Step 0: Validate Input (before anything else)**

`$ARGUMENTS` and any error log are untrusted input. Every name you extract from them (`<feature>`, `<libname>`, `<tag>`) MUST match `^[A-Za-z0-9][A-Za-z0-9_-]*$` (a bare name: no spaces, quotes, `$`, backticks, `;`, `|`, `&` or `/`). If one does not, STOP and ask the operator; do not look it up, hand it to an agent, or build or run any command with it.

**Step 1: Classify Failure Type**

From `$ARGUMENTS`, determine:
- **Zsh library error** → trace the dependency chain: `vde-constants → vde-shell-compat → vde-errors → vde-log → vde-naming → vde-security → vde-core → vm-common → vde-commands → vde-parser`
- **BDD test failure** → Python/Behave traceback
- **Docker runtime error** → container logs
- **SSH error** → `~/.ssh/vde/config` and `lib/vde-ssh`

**Step 2: Debug Swarm (spawn simultaneously)**

- Scout agent: find the failing file, trace dependency chain, check `git log` for last working state
- Log analyzer agent: parse error output, identify root cause pattern
- Spec checker agent: verify expected behavior against `docs/governance/vde-spec.md`

**Step 3: Isolate and Reproduce**

The names were validated in Step 0. Confirm the file exists (`tests/features/core-infrastructure/<feature>.feature`, `tests/unit/<libname>.test.zsh`) and pass every path as a single-quoted argument, as below.

Run ONLY the failing test — never the full suite:

```zsh
# BDD failure
python3 -m behave 'tests/features/core-infrastructure/<feature>.feature' --no-capture

# Zsh unit failure
zsh 'tests/unit/<libname>.test.zsh'

# With tag isolation
python3 -m behave 'tests/features/core-infrastructure/<feature>.feature' --tags='@<tag>' --no-capture
```

**Step 4: Root Cause Report**

```
FAILURE TYPE: <Zsh|Python|Docker|SSH>
FILE: <path:line>
DEPENDENCY CHAIN: <if Zsh, trace from upstream root>
SPEC REFERENCE: <docs/governance/vde-spec.md section>
ROOT CAUSE: <exact explanation>
FIX: <specific minimal change>
VERIFICATION: <exact command to confirm fix>
```

Present fix plan. Follow Phase 1 → Phase 2 rule: get approval before implementing.