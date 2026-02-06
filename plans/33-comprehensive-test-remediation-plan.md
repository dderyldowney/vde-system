# Plan 33: Test Suite Remediation - Master Plan

**Status**: Active  
**Created**: 2026-02-06  
**Priority**: Critical Infrastructure First

## Executive Summary

After completing Plan 32 (SSH Configuration), the VDE test suite (excluding @wip features) has **405 undefined steps** across 220 untested scenarios. This master plan coordinates 12 sub-plans to systematically remediate all undefined steps, prioritizing critical infrastructure first.

## Current State

```
Features: 19 total (4 error, 12 skipped, 15 untested)
Scenarios: 279 total (59 error, 199 skipped, 220 untested)
Steps: 2,442 total (405 undefined, 981 skipped, 1,056 untested)
```

**Completed**: Plan 32 (SSH Configuration) - 108 undefined steps → 0, 22/33 scenarios passing (67%)

## Sub-Plans

Each sub-plan follows the proven 6-phase approach from Plan 32. Sub-plans are organized by priority tier.

### Tier 1: Critical Infrastructure (Highest Priority)

| Plan | Feature | Undefined Steps | Status |
|------|---------|-----------------|--------|
| [33a](33a-docker-operations-remediation.md) | Docker Operations | ~50 | 📋 Ready |
| 33b | Error Handling and Recovery | ~45 | ⏳ Pending |
| 33c | Daily Development Workflow | ~40 | ⏳ Pending |

### Tier 2: Core User Features (High Priority)

| Plan | Feature | Undefined Steps | Status |
|------|---------|-----------------|--------|
| 33d | Natural Language Commands | ~35 | ⏳ Pending |
| 33e | SSH and Remote Access | ~30 | ⏳ Pending |
| 33f | Multi-Project Workflow | ~25 | ⏳ Pending |

### Tier 3: Advanced Features (Medium Priority)

| Plan | Feature | Undefined Steps | Status |
|------|---------|-----------------|--------|
| 33g | SSH Agent Forwarding - VM-to-VM | ~35 | ⏳ Pending |
| 33h | SSH Agent Forwarding - External Git | ~30 | ⏳ Pending |
| 33i | SSH Agent Automatic Setup | ~25 | ⏳ Pending |
| 33j | VM-to-Host Communication | ~20 | ⏳ Pending |

### Tier 4: Productivity Features (Medium Priority)

| Plan | Feature | Undefined Steps | Status |
|------|---------|-----------------|--------|
| 33k | Productivity Features | ~20 | ⏳ Pending |
| 33l | Daily Workflow | ~15 | ⏳ Pending |

## Success Criteria

### Overall Goals
- **Target**: ≥70% scenario pass rate (≥195 of 279 scenarios)
- **Undefined Steps**: 405 → 0
- **Error Scenarios**: 59 → 0

### Per-Feature Requirements
- 0 undefined steps
- 0 AmbiguousStep errors
- ≥80% scenarios passing
- No fake test patterns
- Real Docker/SSH operations

## Execution Strategy

1. **Sequential Execution**: Complete sub-plans in priority order
2. **Independent Work**: Each sub-plan is self-contained
3. **Progress Tracking**: Update this master plan after each sub-plan completion
4. **Validation**: Run full test suite after each tier completion

## Dependencies

- Docker daemon running
- SSH agent available
- VDE base images built
- Port range 2200-2499 available

## Next Steps

1. Execute [Plan 33a: Docker Operations](33a-docker-operations-remediation.md)
2. Update master plan with results
3. Proceed to Plan 33b

## References

- [Plan 32: SSH Configuration](completed/32-ssh-configuration-remediation-plan-detailed.md) (completed)
- [TESTING.md](../docs/TESTING.md)
- [AGENTS.md](../AGENTS.md)
