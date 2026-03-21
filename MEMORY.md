# VDE Project Memory

**Last Updated:** 2026-03-20T21:00:00-04:00
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
| Dead Step Files | ✅ Complete | 2 | 286 |
| Duplicate Helpers | ✅ Complete | 1 | 14 |
| **TOTAL** | | **15** | **~7,000+** |

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
| parser (46 scenarios) | ✅ PASS |
| critical-infrastructure (51 scenarios) | ✅ PASS |
| ssh-configuration (33 scenarios) | ✅ PASS |
| shell-compat (18 tests) | ✅ PASS |

---

## KEY PRINCIPLES

1. **DRY or DIE**: One function, parameterized. No copy-paste.
2. **Tests Prove Goals**: Every test must validate a stated goal from SPEC.
3. **No Dead Code**: Unused imports, helpers, step files = DELETE.
4. **Minimal Footprint**: If it doesn't help users accomplish goals = REMOVE.

---

## STREAMLINING SNAPSHOT (Session 50)

### Progress
- **~7,500+ lines removed/consolidated** total
- SSH steps: 10 → 2 files
- Test runners: 5 → 2 files  
- Step files: 53 → 51 files

### Canonical Functions Added to vm_common.py
- `step_vde_installed` (from 3 copies)
- `step_modified_dockerfile` (from 3 copies)
- `get_container_name` (from 2 copies)
- `get_vm_name` (from 2 copies)

### Remaining Duplicate Step Functions (Different Implementations - OK)
- `step_python_vm_running` - 2 files (different logic)
- `step_ssh_agent_running` - 2 files (different logic)
- `step_new_to_vde` - 2 files (slightly different context)
- `step_no_vms_running` - 2 files

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

## Recent Changes (Session 49-50)

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

---

## What To Eliminate Next

1. **Duplicate step definitions** - `step_vde_installed` appears 3 times
2. **Duplicate helper functions** - Same functions in multiple files
3. **Redundant features** - Features testing same thing
4. **Unused bin scripts** - Scripts never called by tests
