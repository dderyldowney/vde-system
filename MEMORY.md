# VDE Project Memory

**Last Updated:** 2026-03-26T00:00:00-04:00
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

## CURRENT FOCUS: Docker Feature Stack (Session 64+)

**Goal:** Validate core Docker infrastructure first, then stack Docker-tagged features on top one by one.
**Rule:** Nothing Docker works if core capabilities are not properly implemented.

### Feature Order (easiest → hardest)

| # | Feature | Scenarios | Step Defs | Docker Need |
|---|---------|-----------|-----------|-------------|
| 1 | `critical-path.feature` (docker scenarios) | 2 | ✅ All exist | start/stop only |
| 2 | `vm-lifecycle.feature` (docker scenarios) | 10 | ✅ All exist | start/stop/restart/remove |
| 3 | `vm-rebuild.feature` | 4 | ✅ All exist | build + --rebuild flag |
| 4 | `docker-operations.feature` | 12 | ❌ 121 undefined | build/start/stop/status |
| 5 | `vm-full-lifecycle.feature` | 1 | ❌ 16 undefined | full E2E happy path |
| 6 | `docker-management.feature` | 11 | ❌ 121 undefined | network/ports/volumes |
| 7 | `configuration-management.feature` | 5 | ❌ unknown | custom installs/ports |
| 8 | `productivity.feature` | 4 | ❌ unknown | persistence/backup |

### Current Position
- Starting at #1: `critical-path.feature` — zero code to write, just needs Docker running

---

## FAST TEST BASELINE (2026-03-26)

```
Fast tests (--tags="not @integration"): 268 passed / 0 failed / 0 errors / 187 skipped
Runtime: ~2 minutes
ZSH unit tests: 24/24 passing
Python unit tests: 10/10 passing
```

**Run fast tests:**
```zsh
python3 -m behave tests/features/core-infrastructure/ --tags="not @integration" -q
```

**Run specific docker feature (needs Docker):**
```zsh
python3 -m behave tests/features/core-infrastructure/critical-path.feature -q
python3 -m behave tests/features/core-infrastructure/vm-lifecycle.feature --tags="@vm-lifecycle" -q
python3 -m behave tests/features/core-infrastructure/vm-rebuild.feature --tags="@vm-rebuild" -q
```

---

## STEP DEFS STATUS

### Existing step files (tests/features/steps/)
- `critical_steps.py` — critical-path, port range, container start/stop assertions
- `vm_rebuild_steps.py` — vm-lifecycle, vm-rebuild step defs
- `vm_common.py` — shared helpers (container checks, wait_for_container, etc.)
- `parser_steps.py` — parser/intent steps
- `ssh_core_steps.py` — SSH config and access steps
- `common_steps.py` — shared scenario setup
- `documented_workflow_steps.py` — workflow step
- `vm_metadata_steps.py` — VM metadata assertions
- `cache_system_steps.py` — cache steps
- `port_management_steps.py` — port steps
- `shell_helpers.py` — shell exec helpers
- `ssh_helpers.py` — SSH connection helpers

### Needs step defs written
- `docker-operations.feature` — 121 undefined steps (build/start/stop/status/naming/volumes/env)
- `vm-full-lifecycle.feature` — 16 undefined steps (SSH + remove + workspace)
- `docker-management.feature` — 11 scenarios (network/ports/persistence/health/logs)

---

## CONSOLIDATION COMPLETE (Sessions 49-63)

- **~11,000+ lines removed**: SSH steps, test runners, dead step files, duplicate helpers
- **63 files deleted**
- **Fast suite clean**: 268 passed, 0 errors, 0 failures
- **Tagging scheme**: @parser/@spec/@config/@error-path (fast) vs @integration (Docker)

---

## KEY PRINCIPLES

1. **DRY or DIE**: One function, parameterized. No copy-paste.
2. **Tests Prove Goals**: Every test must validate a stated goal from SPEC.
3. **No Dead Code**: Unused imports, helpers, step files = DELETE.
4. **Minimal Footprint**: If it doesn't help users accomplish goals = REMOVE.
5. **Core First**: Validate infrastructure before stacking features on top.
