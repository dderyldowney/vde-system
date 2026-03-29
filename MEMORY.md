# VDE Project Memory

**Last Updated:** 2026-03-29T00:00:00-04:00
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

## RECENT ACHIEVEMENTS (Wave 4)
- **Resolved Systemic Debt**: Consolidated VM loaders, host-path resolvers, and SSH port extractors into canonical helpers in `vm_common.py`.
- **Standardized Infrastructure**: Aligned timeouts and standardized imports across 10+ BDD step definition files.
- **Fixed Port Allocation**: Refactored `find_available_port` to find first available port instead of max+1, preventing range exhaustion in tests.
- **Protected Forever Ports**: Shortened auto-allocation range to 2200-2289, reserving 2290-2299 for manual/test VMs.
- **Unified Command Enforcement**: Refactored all test steps to exclusively use the canonical `vde` entry point, ensuring only `bin/vde` calls underlying scripts or Docker.
- **Stable Green State**: 268+ fast tests and full integration features passing consistently.

---

## CURRENT FOCUS: Docker Feature Stack

**Goal:** Validate core Docker infrastructure first, then stack Docker-tagged features on top one by one.
**Rule:** Nothing Docker works if core capabilities are not properly implemented.

### Feature Order (easiest → hardest)

| # | Feature | Scenarios | Step Defs | Status |
|---|---------|-----------|-----------|--------|
| 1 | `critical-path.feature` | 14 | ✅ | ✅ 14/14 PASSING |
| 2 | `vm-lifecycle.feature` | 15 | ✅ | ✅ RESOLVED |
| 3 | `vm-rebuild.feature` | 8 | ✅ | ✅ 8/8 PASSING |
| 4 | `docker-operations.feature` | 12 | ✅ | ✅ 12/12 PASSING |
| 5 | `vm-full-lifecycle.feature` | 1 | ✅ | ✅ 1/1 PASSING |
| 6 | `docker-management.feature` | 13 | ✅ | ✅ 0 undefined |
| 7 | `configuration-management.feature` | 20 | ❌ | NEXT |
| 8 | `productivity.feature` | 4 | ❌ | PENDING |

### Phase 0 Progress (2026-03-27)
- **O-1 through O-6:** ✅ Complete
- **Next:** O-7 configuration-management.feature (write step defs)

---

## FAST TEST BASELINE (2026-03-27)

```
Fast tests (--tags="not @integration"): 268 passed / 0 failed / 187 skipped
Runtime: ~2.5 minutes
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

## STEP DEFS STATUS

### Existing step files (tests/features/steps/)
- `critical_steps.py` — critical-path, port range, container start/stop assertions (VDE CLI only)
- `vm_rebuild_steps.py` — vm-lifecycle, vm-rebuild, vm-full-lifecycle step defs (VDE CLI only)
- `ssh_core_steps.py` — SSH config and access steps + O-5 full-lifecycle SSH steps
- `docker_operations_steps.py` — docker-operations step defs (VDE CLI only)
- `docker_management_steps.py` — docker-management 52 step defs (VDE CLI only) [NEW O-6]
- `vm_common.py` — shared helpers (run_vde_command, get_compose_file, etc.)
- `parser_steps.py` — parser/intent steps
- `common_steps.py` — shared scenario setup
- `documented_workflow_steps.py` — workflow steps
- `vm_metadata_steps.py` — VM metadata assertions
- `cache_system_steps.py` — cache steps
- `port_management_steps.py` — port steps
- `shell_helpers.py` — shell exec helpers
- `ssh_helpers.py` — SSH connection helpers

### Needs step defs written
- `configuration-management.feature` — 20 scenarios (NEXT: O-7)
- `productivity.feature` — 4 scenarios (O-8)

---

## KEY PRINCIPLES

1. **DRY or DIE**: One function, parameterized. No copy-paste.
2. **Tests Prove Goals**: Every test must validate a stated goal from SPEC.
3. **No Dead Code**: Unused imports, helpers, step files = DELETE.
4. **Minimal Footprint**: If it doesn't help users accomplish goals = REMOVE.
5. **Core First**: Validate infrastructure before stacking features on top.
6. **No Direct Docker Calls**: Step files must use `bin/vde` CLI — not `docker` subprocess calls.
