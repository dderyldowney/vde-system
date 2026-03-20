# VDE Project Memory

**Last Updated:** 2026-03-20T17:40:00-04:00
**Session Focus:** Fixed corrupted docker-compose.yml and renamed environment.py's run_vde_command to test_vde_command

---

## Current Status

### Session 45 (2026-03-20) - Fixed TestWithContainer Failures

**Bugs Fixed:**

1. **Corrupted `configs/docker/python/docker-compose.yml`** - Root cause of flaky TestWithContainer tests
   - File was truncated to 4 lines (only ports section)
   - Restored from git: `git checkout HEAD -- configs/docker/python/docker-compose.yml`

2. **Renamed `environment.py:run_vde_command` to `test_vde_command`**
   - There are 6 different `run_vde_command` implementations in the project causing confusion
   - `vm_common.py` has the main implementation; `environment.py` had a duplicate with different defaults
   - Renamed to clarify testing-specific function

**Test Results:**
- **Shell compat:** 18/18 passing
- **Python unit tests:** 72/72 passing (including TestWithContainer - 20/20)
- **Parser/intent BDD:** 58/58 passing

**Files Modified:**
- `configs/docker/python/docker-compose.yml` - restored from git
- `tests/features/environment.py` - renamed `run_vde_command` to `test_vde_command`

---

## Session 44 (2026-03-20) - Fixed Test Isolation in documented-workflows.feature

**Bug Fixed:**
- `_assoc_get()` in `lib/vde-shell-compat:138` failed on empty string keys
- Root cause: `[[ -v array[key] ]]` doesn't work when key is empty in zsh
- Fixed using `${array[key]-}` parameter expansion to detect existence

**Test Results:**
- **Shell compat:** 18/18 passing (was 17/18)

---

## SSH Config Drift

- `configs/ssh/config` has uncommitted changes (zig removed, test VMs added)
- To sync: `cp configs/ssh/config ~/.ssh/vde/config`

---

## Current Status

### Session 41 - Parser & Test Fixes (2026-03-19)

**Fixed Issues:**

1. **Added `@core-suite` tag** to 8 features that were being skipped:
   - cache-system.feature
   - documented-workflows.feature
   - documented-development-workflows.feature
   - multi-project.feature
   - vm-discovery.feature
   - vm-metadata.feature
   - vm-lifecycle-management.feature
   - natural-language-commands.feature

2. **Fixed `VMs should include` step** in `parser_steps.py`:
   - Now loads aliases from `vm-types.conf`
   - Resolves "postgresql" → "vde-postgres" properly
   - Added `_load_vm_aliases()` and `_resolve_alias()` functions

3. **Updated parser** (`lib/vde-parser`) to recognize new patterns:
   - Added `*check*` → status intent
   - Added `*"use "*` → create_vm intent
   - Added `*"add new"*|*"add-vm-type"*` etc. → add_vm_type intent
   - Added `*"remove"*|*"destroy"*|*"delete"*` → remove_vm intent (new)

4. **Updated tests** to use correct expected intents:
   - "remove ruby" expects "remove_vm" not "remove"
   - "add-vm-type foobar" instead of "add foobar" for add_vm_type intent

### Test Run Results
```
4 features passed, 0 failed, 0 skipped
58 scenarios passed, 0 failed, 0 skipped
245 steps passed, 0 failed, 0 skipped
Took 0min 35.724s
```

---

## Session History

### Session 41 (2026-03-19) - Parser Fixes
- Fixed `@core-suite` tag missing on 8 features
- Fixed `VMs should include` alias resolution in parser_steps.py
- Added new intents to parser: status (check), create_vm (use), remove_vm (remove/destroy)
- 58 scenarios now passing across documented-workflows, daily-workflow, daily-development, multi-project

### Session 40 (2026-03-19) - VM Naming Clarification
- Confirmed with user: VM names are `vde-{name}` format
- Parser step `VMs should include` already normalizes aliases
- Feature files using aliases (python, go, postgres) are correct

### Session 39 (2026-03-19) - Undefined Step Remediation
- Created `collaboration_steps.py` with 7 step definitions
- collaboration.feature: 0 undefined steps, 7 real test failures

### Session 38 (2026-03-19) - Test Infrastructure
- Fixed VDE_ROOT_DIR portability
- Fixed port registry directory handling
- Created rebuild tag and configuration

### Session 37 (2026-03-18) - SSH Test Remediation
- Fixed ssh_helpers.py for VDE isolated SSH agent
- Fixed ssh-agent-forwarding-vm-to-vm.feature contradictory Background

---

## Portability Architecture

**Design Principle:**
- `VDE_ROOT_DIR` - wherever user cloned the project (portable)
- `VDE_SSH_DIR="$HOME/.ssh/vde"` - SSH operations (always in $HOME)

---

## VM Naming Convention (Critical)

**Actual VM names** (Docker containers, SSH hosts): `vde-python`, `vde-go`, `vde-postgres`, etc.
**Aliases** (user input shortcuts): `python`, `go`, `postgres`, `postgresql`, etc.

**Parser normalizes automatically** - `VMs should include "python"` step accepts both and normalizes internally.

---

## Fake Test Prohibition Reminder

**CRITICAL**: All step definitions must:
- Perform REAL verification (file checks, command execution, container state)
- NO `assert True` without real checks
- NO `or True` patterns
- NO `pass` statements
- NO placeholder implementations
