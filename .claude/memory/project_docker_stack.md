---
name: VDE Docker feature stack plan
description: Ordered plan to get all Docker-tagged BDD features passing, feature by feature
type: project
---

All 8 features complete as of 2026-03-28. O-8 (productivity.feature) done.

**Why:** Consolidation is complete (268 fast tests clean). Goal is enabling all 233 @integration Docker scenarios.

**Ordered stack:**

1. `critical-path.feature` — ✅ 14/14 (O-1)
2. `vm-lifecycle.feature` — ✅ 15/15 (O-2)
3. `vm-rebuild.feature` — ✅ 8/8 (O-3)
4. `docker-operations.feature` — ✅ 12/12 (O-4, e88416b)
5. `vm-full-lifecycle.feature` — ✅ 1/1 25/25 steps (O-5, 25381d6)
6. `docker-management.feature` — ✅ 13/13 (O-6, 82b46db)
7. `configuration-management.feature` — ✅ 23/23 (O-7, 0116a1a)
8. `productivity.feature` — ✅ 4/4 (O-8)

**How to apply:**
- Work feature by feature. Do not skip ahead.
- Run each feature in isolation before moving to the next.
- Do not regress the fast baseline (268 passed / 0 errors).
- New step defs go in existing files (no new step files unless no fit exists).
- All docker state checks via `vde ps -q` (running) or `vde ps --all -q` (any state).
