Debug failing tests or runtime errors in VDE using a parallel swarm.

## Usage
/vde-debug $ARGUMENTS

`$ARGUMENTS` = error description, failing test name, or log snippet.

## Execution

**Step 1: Classify Failure Type**

From `$ARGUMENTS`, determine:
- **Zsh library error** → trace the dependency chain: `vde-constants → vde-shell-compat → vde-errors → vde-log → vde-naming → vde-security → vde-core → vm-common → vde-commands → vde-parser`
- **BDD test failure** → Python/Behave traceback
- **Docker runtime error** → container logs
- **SSH error** → `~/.ssh/vde/config` and `lib/vde-ssh`

**Step 2: Debug Swarm (spawn simultaneously)**

- Scout agent: find the failing file, trace dependency chain, check `git log` for last working state
- Log analyzer agent: parse error output, identify root cause pattern
- Spec checker agent: verify expected behavior against `docs/VDE-SPEC.md`

**Step 3: Isolate and Reproduce**

Run ONLY the failing test — never the full suite:

```zsh
# BDD failure
python3 -m behave tests/features/core-infrastructure/<feature>.feature --no-capture

# Zsh unit failure
zsh tests/unit/<libname>.test.zsh

# With tag isolation
python3 -m behave tests/features/core-infrastructure/<feature>.feature --tags=@<tag> --no-capture
```

**Step 4: Root Cause Report**

```
FAILURE TYPE: <Zsh|Python|Docker|SSH>
FILE: <path:line>
DEPENDENCY CHAIN: <if Zsh, trace from upstream root>
SPEC REFERENCE: <docs/VDE-SPEC.md section>
ROOT CAUSE: <exact explanation>
FIX: <specific minimal change>
VERIFICATION: <exact command to confirm fix>
```

Present fix plan. Follow Phase 1 → Phase 2 rule: get approval before implementing.