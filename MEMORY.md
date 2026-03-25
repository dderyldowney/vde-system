# VDE Project Memory

**Last Updated:** 2026-03-24T16:30:00-04:00
**Mission:** Streamline VDE to minimal code that accomplishes stated goals + validates with tests

---

## PROJECT MISSION (Single Source of Truth)

**VDE** (Virtual Development Environment) enables users to create/manage Docker-based development VMs via natural language commands.

**Target Users:** New users, students with zero-to-minimal knowledge

**Core Capabilities (from VDE-SPEC.md):**
1. Create/Start/Stop/Remove VMs via `vde` command
2. Natural language parsing ("start python", "create go VM")
3. SSH access to VMs
4. Service VMs (PostgreSQL, Redis, etc.)
5. Multi-VM clusters

---

## STREAMLINING MANDATE

### Why We're Doing This
- Current codebase has 20,000+ lines of test step definitions
- Massive duplication: same step definitions repeated 2-3 times
- Goal: **Reduce to essential code + essential tests that validate goals**

### Consolidation Progress

| Phase | Status | Files Removed | Lines Removed |
|-------|--------|---------------|--------------|
| SSH Steps | ✅ Complete | 8 | ~5,900 |
| Test Runners | ✅ Complete | 3 | 680 |
| Duplicate Features | ✅ Complete | 1 | 65 |
| Dead Step Files | ✅ Complete | 50 | ~3,500 |
| Duplicate Helpers | ✅ Complete | 1 | 14 |
| **TOTAL** | | **63** | **~11,000+** |

---

## ESSENTIAL TESTS (Only Keep These)

### Core Validation (MUST PASS)
- `parser.feature` - Natural language parsing works
- `critical-infrastructure.feature` - Spec invariants met
- `ssh-configuration.feature` - SSH config generation works
- Shell compatibility tests - `vde-shell-compat` library works

### Test Execution
```bash
# Quick validation (no Docker)
zsh tests/unit/vde-shell-compat.test.zsh
python3 -m behave tests/features/core-infrastructure/parser.feature -q

# Full core suite (requires Docker)
python3 -m behave tests/features/core-infrastructure/ --tags=@core-suite -q
```

---

## CODE FOOTPRINT

### Lib (Essential Only)
- `vde-parser` - Natural language command parsing
- `vde-shell-compat` - Shell compatibility functions  
- `vde-naming` - VM naming conventions
- `vde-constants` - Error codes, port ranges

### Bin (Entry Points)
- `vde` - Main CLI ( delegates to subcommands)
- Essential: `create-virtual-for`, `start-virtual`, `stop-virtual`, `ssh-vm`

---

## CURRENT TEST STATUS

### Fast Tests (No Docker) - ALL PASSING
| Feature | Scenarios | Status |
|---------|-----------|--------|
| parser | 46 | ✅ PASS |
| critical-infrastructure | 51 | ✅ PASS |
| ssh-configuration | 33 | ✅ PASS |
| error-path | 7 | ✅ PASS |
| documented-workflows | 30 | ✅ PASS |
| vm-metadata | 14 | ✅ PASS |
| vm-lifecycle-management | 13 | ✅ PASS |
| cache-system | 3 | ✅ PASS |
| daily-workflow | 12 | ✅ PASS |
| vm-rebuild | 3 | ✅ PASS |

**BDD Total: 243 scenarios passed, 0 failed, 214 skipped (Docker-required)**
**ZSH Unit Tests: 24/24 files passing, 0 failures**
**Python Unit Tests: 10/10 passed**

### Next Steps
- Focus on fast tests only for CI
- Docker tests run manually with longer timeouts

---

## KEY PRINCIPLES

1. **DRY or DIE**: One function, parameterized. No copy-paste.
2. **Tests Prove Goals**: Every test must validate a stated goal from SPEC.
3. **No Dead Code**: Unused imports, helpers, step files = DELETE.
4. **Minimal Footprint**: If it doesn't help users accomplish goals = REMOVE.

---

## STREAMLINING SNAPSHOT (Session 52)

### Progress
- **~11,000+ lines removed/consolidated** total
- SSH steps: 10 → 2 files
- Test runners: 5 → 2 files  
- Step files: 53 → 5 files (massive reduction: 48 unused files deleted)

### Canonical Functions Added to vm_common.py
- `step_vde_installed` (from 3 copies)
- `step_modified_dockerfile` (from 3 copies)
- `get_container_name` (from 2 copies)
- `get_vm_name` (from 2 copies)

### Restored Step Files (Session 53)
- `documented_workflow_steps.py` - "I am following the documented workflow" step
- `common_steps.py` - common scenario steps
- `vm_metadata_steps.py` - VM metadata assertions

### Test Status (Current)
- parser: 46 ✅
- critical-infrastructure: 51 ✅
- ssh-configuration: 33 ✅
- daily-workflow: 12 ✅
- vm-metadata: 14 ✅
- vm-lifecycle-management: 13 ✅ (fixed intent/flag tests)
- **Total: 169 scenarios passing**

### Test Status
- parser: 46 ✅
- critical-infrastructure: 51 ✅
- ssh-configuration: 33 ✅
- Total: 130 scenarios passing

### Direction
Continue consolidating duplicate helpers/step definitions WITHOUT changing behavior. Focus on:
1. Functions with identical implementations
2. Imports that duplicate vm_common functionality
3. Small step files that could be merged

---

## Recent Changes (Session 49-53)

### Session 49-50
- Consolidated SSH step files: 8 → 2
- Consolidated test runners: 3 → 2  
- Deleted duplicate feature files
- Deleted unused step files (vde_test_helpers, host_access_steps)
- Removed .bak files
- Fixed duplicate `_container_is_running` function
- Consolidated duplicate step functions into vm_common.py:
  - `step_vde_installed` - 3 copies → 1 canonical
  - `step_modified_dockerfile` - 3 copies → 1 canonical
  - `get_container_name/get_vm_name` - 2 copies → 1 canonical
  - `_vm_config_exists` - now uses compose_file_exists from vm_common

### Session 52-53 (Current)
- Deleted 48 unused step files (massive consolidation)
- Deleted test_utilities.py (unused helper)
- Fixed vde-path-utils.test.zsh test (project name assertion)
- All Docker-free tests passing: 130 BDD + 18 shell + 18 unit files
- Test cleanup verified: VMs stopped after scenarios

### Session 54-55 (Tagging & Docker Separation)
- Implemented TAG_SCHEME.md tagging: @parser, @spec, @config, @error-path (fast) vs @vm-lifecycle, @integration, @ssh-access, @networking, @storage, @vm-rebuild (Docker)
- Retagged 32 feature files
- Removed duplicate container_exists from shell_helpers.py
- Removed unused docker_ps_list from vm_common.py
- Removed unused helper functions: get_vm_type, get_port_from_compose, get_container_exit_code, wait_for_container_stopped
- Separated @vm-rebuild from @vm-lifecycle (slow rebuild tests run separately)
- Removed rebuild duplication from vm-full-lifecycle.feature
- Fixed vm-lifecycle.feature: added @parser to parser scenarios

### Session 57 (Current - Test Verification)

- Verified fast tests: 184 passing scenarios
- No failures detected - only skipped (require Docker)
- Confirmed DRY consolidation complete
- @vm-rebuild tests: 3 scenarios (require Docker image rebuild)

### Session 58-59 (VM Lifecycle Complete)

- Updated vm-lifecycle.feature to match VDE's actual workflow
- All step definitions now in place (0 undefined steps)
- Tests use existing steps from vm_rebuild_steps.py (no new duplicates)
- Fast tests: 212 scenarios passing

### Session 60 (Current - Full Non-Docker Test Verification 2026-03-24)

- Ran full non-Docker test suite — all clean
- BDD: 243 passed, 0 failed, 214 skipped (Docker-required), 2m 9s
- ZSH unit tests: 24/24 files, 0 failures
- Python unit tests: 10/10 passed
- Streamlined agents/ directory (legacy agent files deleted)
- Added CLAUDE.md, .claude/ config, tests/run-tests.zsh
- Removed tests/run-tests.sh (bash → zsh migration)

### Fast Tests Status (243 BDD scenarios passing)
- parser: 46 ✅
- critical-infrastructure: 51 ✅
- ssh-configuration: 33 ✅
- error-path: 7 ✅
- documented-workflows: 30 ✅
- vm-metadata: 14 ✅
- vm-lifecycle-management: 13 ✅
- cache-system: 3 ✅
- daily-workflow: 12 ✅
- vm-rebuild: 3 ✅
- (additional features via 14 feature pass)

### VM Lifecycle Feature
- 15 scenarios (start/stop/restart/remove + parser tests)
- All steps defined via vm_rebuild_steps.py
- Requires Docker - run with longer timeout

---
