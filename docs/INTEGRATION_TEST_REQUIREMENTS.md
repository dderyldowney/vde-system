# Integration Test Requirements

**Authoritative Document** - Keep this file current at all times

**Last Updated**: 2026-02-04
**Status**: Phase 1 Complete

---

## Overview

Integration tests require full Docker infrastructure to run. This document catalogs all integration test requirements, categorizes tests by infrastructure needs, and provides execution guidelines.

## Test Categories

### Category A: Docker-Free Tests (No Infrastructure)
**Location**: `tests/features/docker-free/`
**Requirements**: None - these tests verify configuration, parsing, and non-Docker behavior
**Execution**: `./run-tests.zsh --docker-free` or `behave tests/features/docker-free/`

| Feature | Scenarios | Status |
|---------|-----------|--------|
| Cache System | 13 | ✓ PASS |
| Documented Development Workflows | 31 | ✓ PASS |
| Multi-Project Workflow | 5 | ✓ PASS |
| Shell Compatibility | 41 | ✓ PASS |
| SSH Agent Configuration | 30 | ✓ PASS |
| VM Information | 11 | ✓ PASS |
| VDE Home Path | 15 | ✓ PASS |
| **TOTAL** | **146** | **✓ PASS (100%)** |

### Category B: Docker-Required Tests (Docker Daemon)
**Location**: `tests/features/docker-required/`
**Requirements**: Docker daemon running, Docker Compose v2+
**Tag**: `@requires-docker-host`
**Execution**: `behave tests/features/docker-required/ --tags=@requires-docker-host`

| Feature | Scenarios | Status | Notes |
|---------|-----------|--------|-------|
| Docker Operations | 14 | ✓ PASS | Baseline verified |
| Daily Workflow | TBD | - | Needs VM lifecycle steps |
| SSH Agent Forwarding | TBD | - | Needs SSH setup |
| Team Collaboration | TBD | - | Needs multi-VM setup |
| Error Handling | TBD | - | Needs error injection |
| **TOTAL (defined)** | **14+** | **✓ PASS** | |

### Category C: Full Integration Tests (Complete Infrastructure)
**Location**: `tests/features/docker-required/`
**Requirements**: All 27 VM configurations, port ranges 2200-2299, 2400-2499
**Tag**: `@integration`
**Execution**: `behave tests/features/ --tags=@integration`

These tests verify:
- Multi-VM orchestration
- Data persistence across restarts
- Team configuration sharing
- Cross-VM networking

## Infrastructure Requirements

### Minimum (Category A + B)
```bash
# Verify Docker is available
docker --version  # Must return version info

# Verify compose files exist
ls configs/docker/*/docker-compose.yml  # Must list 27+ files
```

### Full Integration (Category C)
```bash
# All requirements above PLUS:
# - Ports 2200-2299 available (language VMs)
# - Ports 2400-2499 available (service VMs)
# - Data directories initialized (data/postgres, data/redis, etc.)
# - SSH keys configured (public-ssh-keys/)
```

## Test Execution Matrix

| Scenario | Command | Expected Result |
|----------|---------|-----------------|
| Docker-free only | `./run-tests.zsh --docker-free` | 146 scenarios pass |
| Docker-required | `behave tests/features/docker-required/` | 14+ scenarios pass |
| Fake test scan | `./run-fake-test-scan.zsh` | 0 violations (CLEAN) |
| Parser tests | `./run-vde-parser-tests.zsh` | All pass |
| All tests | `./run-tests.zsh` | Combined result |

## Undefined Steps Status

| Metric | Count | Notes |
|--------|-------|-------|
| Undefined steps | 899 | Priority for Phase 2 |
| Errored scenarios | 97 | Need step definitions |
| Untested scenarios | 235 | Ready for execution |

## Maintaining This Document

### When Adding New Tests
1. Add test to appropriate category
2. Update requirements section
3. Update execution matrix
4. Commit with message: `docs: update integration test requirements`

### After Infrastructure Changes
1. Verify requirements still valid
2. Update execution commands if needed
3. Re-run baseline tests
4. Document any new prerequisites

### After Test Execution
1. Update status column
2. Note any failures
3. Track remediation actions

## Related Documents

- `plans/21-daily-workflow-remediation-plan.md` - Implementation roadmap
- `docs/TESTING.md` - General testing guidelines
- `docs/DAILY_WORKFLOW_STATUS.md` - Current test status
- `tests/features/steps/README.md` - Step definition patterns
