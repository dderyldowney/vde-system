# Session Handover — Docker Feature Stack

**Mission:** Validate core Docker infrastructure, then stack Docker-tagged features one by one.
**Rule:** Nothing Docker works if core capabilities are not properly implemented first.

---

## CURRENT FOCUS (2026-03-26)

### Docker Feature Stack Order

| # | Feature | Scenarios | Step Defs | Status |
|---|---------|-----------|-----------|--------|
| 1 | `critical-path.feature` (2 docker scenarios) | 2 | ✅ exist | **START HERE** |
| 2 | `vm-lifecycle.feature` (docker scenarios) | 10 | ✅ exist | Next |
| 3 | `vm-rebuild.feature` | 4 | ✅ exist | Next |
| 4 | `docker-operations.feature` | 12 | ❌ 121 undefined | Write step defs |
| 5 | `vm-full-lifecycle.feature` | 1 | ❌ 16 undefined | Write step defs |
| 6 | `docker-management.feature` | 11 | ❌ undefined | Write step defs |
| 7 | `configuration-management.feature` | 5 | ❌ unknown | Write step defs |
| 8 | `productivity.feature` | 4 | ❌ unknown | Write step defs |

### Next Action
Run `critical-path.feature` docker scenarios with Docker available:
```zsh
python3 -m behave tests/features/core-infrastructure/critical-path.feature -q
```
Expected: 12 pass (already passing), 2 docker scenarios should pass too.

---

## FAST TEST BASELINE (2026-03-26)

```
Fast tests (--tags="not @integration"): 268 passed / 0 failed / 0 errors / 187 skipped
Runtime: ~2 minutes
ZSH unit tests: 24/24 passing
Python unit tests: 10/10 passing
```

Do not regress this baseline.

---

## DOCKER FEATURE ANALYSIS

### Features with step defs (Tier 0 — just needs Docker running)

**`critical-path.feature`** — 2 docker scenarios
- `vde start python` → container `vde-python` should be running
- `vde stop python` → container `vde-python` should not be running
- Steps: `critical_steps.py` lines 148, 311, 319, 331
- Run: `python3 -m behave tests/features/core-infrastructure/critical-path.feature -q`

**`vm-lifecycle.feature`** — 10 docker scenarios
- start/stop/restart/remove VMs
- Steps: `vm_rebuild_steps.py`
- Run: `python3 -m behave tests/features/core-infrastructure/vm-lifecycle.feature --tags="@vm-lifecycle" -q`

**`vm-rebuild.feature`** — 4 docker scenarios
- `vde start python --rebuild`, `--no-cache`, rust/go rebuilds
- Steps: `vm_rebuild_steps.py`
- Run: `python3 -m behave tests/features/core-infrastructure/vm-rebuild.feature --tags="@vm-rebuild" -q`

### Features needing step defs (Tier 1)

**`docker-operations.feature`** — 12 scenarios (121 undefined steps)
- Build image, start/stop/restart container, error handling, status check
- container naming convention, volume mounts, env vars
- Key step patterns to implement: `docker-compose build`, `docker-compose up -d`, `docker-compose down`

**`vm-full-lifecycle.feature`** — 1 large scenario (16 undefined steps)
- Full E2E: create → start → SSH → stop → start again → remove
- Missing: SSH assertions + `SSH config entry should be preserved`

**`docker-management.feature`** — 11 scenarios
- Network creation, port allocation, service ports, volumes, data persistence
- Resource limits, health monitoring, cleanup, multi-stage builds, isolation, logs

**`configuration-management.feature`** — 5 scenarios
- Custom install commands, service ports, multiple ports, display names, aliases

**`productivity.feature`** — 4 scenarios
- Data persistence, clean state, backups, background services

---

## STEP DEF STRATEGY (when writing new ones)

- All new step defs go in an appropriate existing file (no new files unless no fit)
- Docker operations (build/run/stop) → extend `vm_rebuild_steps.py` or `vm_common.py`
- Container assertions → `critical_steps.py` already has container running/not-running checks
- No duplicate step patterns — check existing files before writing

---

## Previous: BDD Fast-Suite Cleanup (2026-03-26)

Added `@integration` tag to 6 features missing it:
- `vm-lifecycle.feature`, `vm-full-lifecycle.feature`, `vm-rebuild.feature`
- `configuration-management.feature`, `productivity.feature`, `vde-ssh-commands.feature`

Result: Fast baseline improved 205 → 268 passed, 41 errors → 0, runtime 14-17 min → ~2 min
