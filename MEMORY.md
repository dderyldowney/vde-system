# VDE Project Memory

**Last Updated:** 2026-03-23T16:38:00-04:00
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

| Test | Status |
|------|--------|
| Core features (parser, critical-infra, ssh-config, error-path) | ✅ 137 PASS |
| cache-system.feature | ✅ 3 PASS (simplified) |
| @parser features (145 scenarios) | ✅ ALL PASS |
| @vm-lifecycle | Next Session focus |
| @integration | Next Session focus |

**Total: 145 @parser scenarios passing**

### New Tagging Scheme
- Fast tests: @parser, @spec, @config, @error-path (no Docker)
- Integration: @integration, @vm-lifecycle, @vm-rebuild, @ssh-access, @networking, @storage
- behave.ini updated: default runs `(@parser or @spec or @config or @error-path) and not wip`

**Essential Tests:** 259+ scenarios + 18 shell tests passing

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

### Next Session Focus: vm-rebuild.feature

- Focus on: `tests/features/core-infrastructure/vm-rebuild.feature`
- 3 scenarios tagged with @vm-rebuild
- Requires Docker for image rebuild tests

---
