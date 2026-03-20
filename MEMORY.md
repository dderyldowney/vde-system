# VDE Project Memory

**Last Updated:** 2026-03-20T20:00:00-04:00
**Session Focus:** SSH Step Consolidation + DRY Mandate

---

## MANDATORY REQUIREMENTS

### DRY Principle (HARDCORE)
- **ALL code and tests MUST follow DRY** - No duplicate logic, no copy-paste
- ONE generalized function with parameters, not multiple nearly-identical functions
- When consolidating code, **ELIMINATE duplicates - don't preserve them**
- See `.kilocode/rules/dry_requirement.md` for full protocol

### Code Review (MANDATORY)
- All code changes MUST be reviewed before commit
- See Phase 4 workflow in `.kilocode/rules/workflow.md`

### Agent Files (MANDATORY)
- Read `agents/*.md` files at session start for your role
- Coder, Tester, Planner, Reviewer, Scout all have specific DRY guidance

---

## Current Status

### Session 48 (2026-03-20) - SSH Step Consolidation + DRY

**Consolidated (REVERSED from plan):**
- Merged `docker_helpers.py` (421 lines) INTO `shell_helpers.py` (194 lines)
- Deleted `docker_helpers.py` (duplicate implementations)
- Deleted `vm_naming_helpers.py` (116 lines - merged into shell_helpers)
- Unified `execute_in_container()` with `use_shell` parameter to handle both shell and raw modes
- Updated importers: `vm_docker_service_steps.py`, `ssh_steps.py`
- Renamed `test_docker_helpers.py` → `test_shell_helpers.py`

**Key Principle Applied:**
- ONE generalized function with parameters, not multiple nearly-identical functions
- `execute_in_container(container, cmd, use_shell=True/False)` handles both shell and raw modes

**Test Results:**
- **Shell compat:** 18/18 passing
- **Python unit tests:** 54/54 passing
- **Core BDD:** 46 scenarios passing (parser.feature)

---

## STREAMLINING MASTER PLAN (Updated)

### Phase 1: DONE ✅
- [x] Delete dead environment files (3 files, 711 lines) - Session 47
- [x] Merge duplicate SSH environment steps (1 file, 56 lines) - Session 47

### Phase 2: DONE ✅ (REVERSED - merged INTO shell_helpers)
- [x] Consolidate `shell_helpers.py` + `docker_helpers.py` + `vm_naming_helpers.py`
- [x] Unified `execute_in_container()` with `use_shell` parameter
- Deleted: `docker_helpers.py`, `vm_naming_helpers.py`

### Phase 3: Consolidate SSH Step Files (HIGH PRIORITY - 5,923 lines) ✅ COMPLETE
**Target:** 5,923 lines across 10 files
**Solution:** 2-file consolidation + 1 shared helpers file

**Consolidated Files:**
- `ssh_core_steps.py` (2,543 lines) - SSH infrastructure
  - Sources: ssh_config_steps.py + ssh_steps.py + vde_ssh_verification_steps.py
- `ssh_service_steps.py` (2,500 lines) - SSH services/connections
  - Sources: ssh_connection + ssh_remote_access + ssh_vm + ssh_vm_to_vm + ssh_git

**Deleted Files:**
- ssh_config_steps.py, ssh_steps.py, vde_ssh_verification_steps.py
- ssh_connection_steps.py, ssh_remote_access_steps.py, ssh_vm_steps.py
- ssh_vm_to_vm_steps.py, ssh_git_steps.py

**Key Fix:** Fixed duplicate function names that broke step registration

**Test Results:** 33 SSH config scenarios passing

### Phase 4: Consolidate Test Runners (COMPLETE ✅)
**Target:** 1,223 lines across 5 scripts → 2 consolidated files
- [x] Merged `run-docker-free-tests.zsh` + `run-docker-required-tests.zsh` + `run-full-test-suite.zsh`
- [x] Created `run-all-tests.zsh` (full suite, 225 lines)
- [x] Created `run-quick-tests.zsh` (docker-free only, 107 lines)
- [x] Deleted old files (680 lines removed)
- **Kept:** `run-all-known-tests.zsh` (different purpose - shell-based unit tests)

### Phase 5: Audit BDD Features for Redundancy (COMPLETE ✅)
**Target:** 34 feature files audited
- [x] Audited all 34 feature files
- [x] Found: `daily-development` + `daily-development-workflow` are COMPLEMENTARY (parser vs integration tests)
- [x] Found: `critical-infrastructure` + `critical-path` are DIFFERENT (function tests vs compose tests)
- [x] Found: `documented-workflows` + `documented-development-workflows` are DUPLICATES
- [x] Deleted: `documented-development-workflows.feature` (duplicate)
- **Net: 1 file deleted (65 lines removed)**

### Phase 6: Eliminate Dead Step Definitions (PARTIAL ✅)
**Target:** 52 step files audited
- [x] Verified all step files load without import errors
- [x] No critical orphan files found
- [x] Step files with few definitions reviewed (host_access_steps.py - helper functions)
- **Note:** Full dead-step elimination requires complex usage analysis (deferred)

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
