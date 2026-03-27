# Remediation Plan: Docker Feature Stack

## Related Handovers
- Session Handover: see ../session_handover.md

## Overview

All streamlining and infrastructure phases are complete. The current work is validating and enabling
the Docker-dependent feature suite, working from easiest to hardest. Each phase unlocks the next.

---

## Active: Phase O — Docker Feature Stack (2026-03-26+)

**Goal:** Get all Docker-tagged BDD features passing, one by one, starting with zero-code-needed wins.

### Rule
Core infrastructure must pass before stacking features on top of it.
Do not skip ahead. Fix failures before proceeding to next feature.

### Phase O Steps

| Step | Feature | Action | Status |
|------|---------|--------|--------|
| O-1 | `critical-path.feature` | Run with Docker, verify 2 docker scenarios pass | ✅ Complete |
| O-2 | `vm-lifecycle.feature` | Run with Docker, verify 10 docker scenarios pass | ✅ Complete |
| O-3 | `vm-rebuild.feature` | Run with Docker, verify 4 rebuild scenarios pass | ✅ Complete |
| O-4 | `docker-operations.feature` | Fixed 2 bugs — 12/12 pass | ✅ Complete (e88416b) |
| O-5 | `vm-full-lifecycle.feature` | Wrote 16 step defs — 1/1 pass | ✅ Complete (25381d6) |
| O-6 | `docker-management.feature` | Write step defs for 11 scenarios | Pending |
| O-7 | `configuration-management.feature` | Write step defs for 5 scenarios | Pending |
| O-8 | `productivity.feature` | Write step defs for 4 scenarios | Pending |

### Success Criteria
- Each feature passes before moving to the next
- Fast baseline (268 passed) does not regress
- No fake tests: all assertions are real Docker state checks

---

## All Previous Phases: COMPLETE

| Phase | Description | Date |
|-------|-------------|------|
| A | Baseline verification and scoping | Complete |
| B | Hot-path optimizations and parser hygiene | Complete |
| C | Docker safety, labeling, and isolation hardening | Complete |
| D | Test suite alignment (integration and Behave) | Complete |
| E | Validation, observability, and documentation | Complete |
| F | Test infrastructure hardening | 2026-03-09 |
| G | VM lifecycle promotion + zig removal | 2026-03-09 |
| H | Test infrastructure fixes | 2026-03-11 |
| I | Cache-system fix | 2026-03-22 |
| J | VM rebuild feature implementation | 2026-03-23 |
| K | VM lifecycle feature update | 2026-03-24 |
| L | Supervisor fake test fixes | 2026-03-24 |
| M | Test infrastructure & agent orchestration | 2026-03-25 |
| N | BDD fast-suite cleanup | 2026-03-26 |
| O | Docker feature stack (vm-lifecycle fix, remove-virtual fix) | 2026-03-26 |
| P | Config directory reordering (configs/docker/{python,postgres} -> configs/docker/languages/{python,...} + configs/docker/services/{postgres,...}) | Future |

## Future: Config Directory Reordering

**Proposed:** Move from `configs/docker/{python,rust,postgres,...}` to:
- `configs/docker/languages/{python,rust,...}`
- `configs/docker/services/{postgres,redis,...}`

**Required changes:**
- All bin/* scripts using CONFIGS_DIR path construction
- All test step definitions checking config paths
- docker-compose template generation (vde-templates)
- Update CONFIGS_DIR default and path construction logic

**Note:** Coordinate with user before implementing.

---

## Paired Update Policy
- This plan is the paired companion to `../session_handover.md`.
- Updates must be synchronized; maintain cross-links and same scope.
