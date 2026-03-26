# VDE Project Memory

**Last Updated:** 2026-03-26T13:00:00-04:00
**Mission:** Ensure core Docker infrastructure is working and passing, then stack Docker features one by one

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

## CURRENT FOCUS: Docker Feature Stack (Session 65)

**Goal:** Validate core Docker infrastructure first, then stack Docker-tagged features on top one by one.
**Rule:** Nothing Docker works if core capabilities are not properly implemented.

### Feature Order (easiest → hardest)

| # | Feature | Scenarios | Step Defs | Status |
|---|---------|-----------|-----------|--------|
| 1 | `critical-path.feature` | 14 | ✅ | ✅ 14/14 PASSING |
| 2 | `vm-lifecycle.feature` | 15 | ✅ | ✅ RESOLVED |
| 3 | `vm-rebuild.feature` | 8 | ✅ | ✅ 8/8 PASSING |
| 4 | `docker-operations.feature` | 12 | ❌ 68 undefined | Write step defs |

### Phase 0 Progress (2026-03-26)
- **Phase O-1:** critical-path.feature ✅ Complete
- **Phase O-2:** vm-lifecycle.feature ✅ Complete  
- **Phase O-3:** vm-rebuild.feature ✅ Complete
- **Next:** O-4 docker-operations.feature (write step defs)

---

## FAST TEST BASELINE (2026-03-26)

```
Fast tests (--tags="not @integration"): 262 passed / 0 failed / 0 errors
Runtime: ~2 minutes
```

---

## Future: Config Directory Reordering

**Proposed:** Move from `configs/docker/{python,postgres,...}` to:
- `configs/docker/languages/{python,rust,...}`
- `configs/docker/services/{postgres,redis,...}`

**Required changes (when implemented):**
- All bin/* scripts using CONFIGS_DIR path construction
- All test step definitions checking config paths
- docker-compose template generation (vde-templates)
- Update CONFIGS_DIR default and path construction logic

---

## CHANGES MADE THIS SESSION (2026-03-26)

### vm_rebuild_steps.py — full rewrite
- Removed all direct `docker` subprocess calls
- `_container_exists()` → `vde ps --all -q`
- `_container_running()` → `vde ps -q`
- `_stop_vm()` → `vde stop {vm_name}`
- `_stop_and_remove_vm()` → `vde stop` + `vde remove`
- `step_no_vms_running` → `vde ps -q` empty check
- Fixed hardcoded step decorators: `restart python` → `restart {vm_name}`, `start python --rebuild` → `start {vm_name} --rebuild`
- Added missing `Given VM types are loaded from configuration` step
- Set `context.vm_name` in restart step
- Fixed `step_fresh_container` (RestartCount=0 is correct for VDE restart — creates new container)
- `step_config_still_exists` now actually asserts compose_file.exists()

### critical_steps.py
- `container "vde-python" is running` → uses `_vde_cli("ps -q")` instead of `docker ps`
- `the Docker network X should exist` → uses `_vde_cli("networks")` instead of `docker network inspect`
- `the Docker network X should be a bridge network` → parses `vde networks` output

### vde-errors (lib)
- `vde_error_vm_not_found` → message now "Unknown VM: '{name}'" (was "VM '{name}' not found") — matches VDE-SPEC.md §10 error table

### bin/remove-virtual (fix)
- Fixed config directory lookup: `resolve_vm_name("python")` returns "vde-python" but configs are at `configs/docker/python/`, not `configs/docker/vde-python/`
- Added `CONFIG_NAME="${VM_NAME#vde-}"` to strip prefix before path construction
- Also fixed logs directory path in remove-virtual

---

## STEP DEFS STATUS

### Existing step files (tests/features/steps/)
- `critical_steps.py` — critical-path, port range, container start/stop assertions (VDE CLI only)
- `vm_rebuild_steps.py` — vm-lifecycle, vm-rebuild step defs (VDE CLI only)
- `vm_common.py` — shared helpers (run_vde_command, get_compose_file, etc.)
- `parser_steps.py` — parser/intent steps
- `ssh_core_steps.py` — SSH config and access steps
- `common_steps.py` — shared scenario setup
- `documented_workflow_steps.py` — workflow steps
- `vm_metadata_steps.py` — VM metadata assertions
- `cache_system_steps.py` — cache steps
- `port_management_steps.py` — port steps
- `shell_helpers.py` — shell exec helpers
- `ssh_helpers.py` — SSH connection helpers

### Needs step defs written
- `docker-operations.feature` — 12 scenarios, 121 undefined steps
- `vm-full-lifecycle.feature` — 1 scenario, 16 undefined steps
- `docker-management.feature` — 11 scenarios
- `configuration-management.feature` — 5 scenarios
- `productivity.feature` — 4 scenarios

---

## KEY PRINCIPLES

1. **DRY or DIE**: One function, parameterized. No copy-paste.
2. **Tests Prove Goals**: Every test must validate a stated goal from SPEC.
3. **No Dead Code**: Unused imports, helpers, step files = DELETE.
4. **Minimal Footprint**: If it doesn't help users accomplish goals = REMOVE.
5. **Core First**: Validate infrastructure before stacking features on top.
6. **No Direct Docker Calls**: Step files must use `bin/vde` CLI — not `docker` subprocess calls.
