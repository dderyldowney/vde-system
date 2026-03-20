# VDE Project Memory

**Last Updated:** 2026-03-20T18:15:00-04:00
**Session Focus:** HARDCODE STREAMLINING - deleted dead files, consolidated SSH steps

---

## Current Status

### Session 47 (2026-03-20) - Hardcore Streamlining Phase 1

**Deleted Dead Code:**
- `tests/features/environment.e2e.py` (237 lines - never loaded by behave)
- `tests/features/environment.integration.py` (237 lines - never loaded by behave)
- `tests/features/environment.unit.py` (237 lines - never loaded by behave)
- `tests/features/steps/ssh_docker_steps.py` (16 lines - dead stub)
- `tests/features/steps/vde_ssh_environment_steps.py` (56 lines - merged into vde_ssh_command_steps.py)

**Total Deleted: 783 lines of dead code**

**Merged:**
- `vde_ssh_environment_steps.py` → `vde_ssh_command_steps.py` (+38 lines consolidated)

**Current State:**
- Step files: 61 files, 22,626 lines
- SSH-related: 10 files, 5,923 lines (BIGGEST consolidation target)
- Helper files: 6 files, 1,207 lines

**Test Results:**
- **Shell compat:** 18/18 passing
- **Python unit tests:** 72/72 passing
- **Core BDD:** 112 scenarios passing

---

## STREAMLINING MASTER PLAN (Priority Order)

### Phase 1: DONE ✅
- [x] Delete dead environment files (3 files, 711 lines)
- [x] Merge duplicate SSH environment steps (1 file, 56 lines)

### Phase 2: Consolidate Helper Libraries (HIGH PRIORITY)
**Target:** 1,207 lines across 6 files
- [ ] Merge `shell_helpers.py` (194 lines) into `docker_helpers.py` (421 lines)
  - Both have duplicate `execute_in_container()`, `_get_vde_root()`, `_run_vde_command()`
  - Keep docker_helpers.py as canonical (more complete implementation)
  - Delete shell_helpers.py, update importers (2 step files)
- [ ] Merge `ssh_helpers.py` (270 lines) into `vm_common.py` or dedicated `ssh_utils.py`
  - SSH-specific helpers used across multiple SSH step files
- [ ] Merge `vm_naming_helpers.py` (116 lines) into `vm_common.py`
  - `get_vm_types()`, `get_vm_display()` used everywhere

### Phase 3: Consolidate SSH Step Files (HIGH PRIORITY)
**Target:** 5,923 lines across 10 files
**Problem:** 167 @given/@when/@then definitions in `ssh_config_steps.py` alone
- [ ] Audit step definitions for duplicates across:
  - `ssh_config_steps.py` (2232 lines, 167 steps)
  - `ssh_connection_steps.py` (317 lines, 28 steps)
  - `ssh_git_steps.py` (980 lines, 76 steps)
  - `ssh_remote_access_steps.py` (533 lines, 44 steps)
  - `ssh_vm_steps.py` (288 lines, 26 steps)
  - `ssh_vm_to_vm_steps.py` (531 lines, 71 steps)
  - `vde_ssh_verification_steps.py` (367 lines, 16 steps)
- [ ] Consolidate by domain:
  - SSH Config: `ssh_config_steps.py` + `ssh_config_verification.py`
  - SSH Connection: `ssh_connection_steps.py` + `ssh_steps.py`
  - SSH VM: `ssh_vm_steps.py` + `ssh_vm_to_vm_steps.py`
  - SSH Git: Keep `ssh_git_steps.py` separate (unique domain)

### Phase 4: Consolidate Test Runners (MEDIUM PRIORITY)
**Target:** 1,223 lines across 5 scripts
- [ ] Merge `run-docker-free-tests.zsh` into `run-full-test-suite.zsh`
  - Both use similar structure, just different test paths
- [ ] Merge `run-docker-required-tests.zsh` into `run-full-test-suite.zsh`
- [ ] Consolidate to: `run-all-tests.zsh` (full), `run-quick-tests.zsh` (docker-free only)

### Phase 5: Audit BDD Features for Redundancy (MEDIUM PRIORITY)
**Target:** 24+ feature files
- [ ] Audit features that test same functionality:
  - `critical-infrastructure.feature` vs `critical-path.feature` (overlap?)
  - `daily-workflow.feature` vs `daily-development.feature` (overlap?)
  - `documented-workflows.feature` vs `documented-development-workflows.feature` (overlap?)
- [ ] Merge or de-duplicate overlapping scenarios

### Phase 6: Eliminate Dead Step Definitions (LOW PRIORITY)
**Target:** Unknown - audit step files for unused definitions
- [ ] Run feature coverage analysis
- [ ] Identify steps defined but never used
- [ ] Delete orphaned step definitions

---

## Session 46 (2026-03-20) - Deleted Dead Code

**Refactored:**
- Deleted 3 never-used environment files (237 lines of dead code)
- Merged `vde_ssh_environment_steps.py` into `vde_ssh_command_steps.py`

---

## Session 45 (2026-03-20) - Fixed TestWithContainer Failures

**Bugs Fixed:**
1. **Corrupted `configs/docker/python/docker-compose.yml`** - Restored from git
2. **Renamed `environment.py:run_vde_command` to `test_vde_command`** - Clarified purpose

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
