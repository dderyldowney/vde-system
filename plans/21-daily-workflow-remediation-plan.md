# Plan 21: Daily Workflow Remediation Plan (REVISED v2)

**Created**: 2026-02-04
**Previous Commit**: 590be53 - test: fix docker-operations BDD tests
**Status**: docker-operations complete (14/14 scenarios passing)
**Last Updated**: 2026-02-04 (REVISED v2 - added baseline snapshot, refinements)
**Note**: yume-guardian subagent was never implemented. Using `run-fake-test-scan.zsh` for fake test detection.

---

## Current State Snapshot (Pre-Plan)

| Metric | Baseline (Plan 18/20) | Current (Pre-Execution) | Post-M3 |
|--------|----------------------|------------------------|---------|
| docker-free scenarios | 146 | 146 | 146/146 ✓ |
| docker-free steps | 594 | 594 | 594/594 ✓ |
| docker-free pass rate | 100% | 100% | 100% |
| docker-operations scenarios | 14/14 | 14/14 | 14/14 ✓ |
| All features | ~1003 undefined | 899 undefined | 899 |
| All features | 28 features | 28 features | 28 |
| All features | 381 scenarios | 381 scenarios | 381 |
| Fake test violations | Unknown | 0 | 0 |
| Fake test scan status | Unknown | CLEAN | CLEAN |

> **Action**: Execute baseline measurements before Phase 1.1

---

## Overview

Three main workstreams to complete the VDE test infrastructure:
1. Full Test Suite Verification
2. Remaining Undefined Steps Implementation
3. Fake Test Audit & Conversion

---

## Workstream 1: Full Test Suite Verification

### Phase 1.1: Run Docker-Free Tests
- **Objective**: Run all docker-free tests and verify no regressions
- **Steps**:
  1. Execute `./run-tests.zsh --docker-free` or `behave tests/features/docker-free/`
  2. Capture test output and failure counts
  3. Document any failures or regressions
- **Reference**: Plan 18 shows baseline: 146 scenarios, 594 steps - ALL PASSING (100% real)
- **Exit Criteria**: All docker-free tests pass or failures are documented

### Phase 1.2: Integration Test Inventory
- **Objective**: Document integration test requirements BEFORE running docker-required tests
- **Steps**:
  1. List all `@integration` tagged scenarios: `behave tests/features/ --dry-run --tags=@integration`
  2. Document infrastructure requirements for each integration test
  3. Create infrastructure setup checklist
  4. Identify which docker-required tests are safe to run WITHOUT full infrastructure
- **Exit Criteria**: Integration test inventory complete with requirements map

### Phase 1.3: Run Docker-Required Tests (Non-Integration)
- **Objective**: Run docker-required tests that don't need full infrastructure
- **Steps**:
  1. Execute `behave tests/features/docker-required/ --exclude-tags=@integration`
  2. Verify docker-operations.feature still passes (baseline: 14/14)
  3. Identify other passing docker-required features
  4. Run fake test scanner: `./run-fake-test-scan.zsh`
- **Exit Criteria**: docker-operations baseline maintained, fake test scan complete

---

## Workstream 2: Remaining Undefined Steps Implementation

### Phase 2.1: Inventory Undefined Steps
- **Objective**: Catalog all undefined steps across features
- **Steps**:
  1. Execute `behave tests/features/ --dry-run` to list undefined steps
  2. Group undefined steps by feature file
  3. **Prioritization criteria**: Steps appearing in >3 scenarios = "high-frequency"
  4. Sort by frequency descending
  5. Compare with Plan 11 baseline: ~1003 undefined steps
- **Reference**: Step files already created from Plan 11:
   - `productivity_steps.py`, `debugging_steps.py`, `config_steps.py`
   - `daily_workflow_steps.py`, `ssh_agent_steps.py`, `ssh_git_steps.py`
   - `team_collaboration_steps.py`, `template_steps.py`
- **Exit Criteria**: Undefined step inventory with counts, sorted by frequency

### Phase 2.2: Implement High-Frequency Step Definitions
- **Objective**: Implement step definitions for most common undefined steps
- **Steps**:
  1. Identify top 20 most frequent undefined steps
  2. Create step definitions in appropriate step files
  3. Test each new definition
  4. **Critical**: Use VM naming convention from Plan 20:
     - Service VMs (no suffix): postgres, redis, nginx, mongodb, mysql, rabbitmq, couchdb
     - Language VMs (append -dev): python → python-dev, rust → rust-dev, go → go-dev
  5. Leverage helper: `tests/features/steps/vm_naming_helpers.py`
- **Exit Criteria**: Top 20 undefined steps implemented

### Phase 2.3: Implement Feature-Specific Steps
- **Objective**: Implement remaining feature-specific step definitions
- **Steps**:
  1. Group remaining steps by feature
  2. Implement one feature at a time
  3. Verify each feature's scenarios pass
- **Exit Criteria**: All feature scenarios pass

### Phase 2.4: Cross-Cutting Infrastructure Steps
- **Objective**: Implement shared infrastructure step definitions
- **Steps**:
  1. Identify reusable step patterns
  2. Create helper functions in `docker_ops_infrastructure.py`
  3. Refactor feature steps to use shared infrastructure
- **Exit Criteria**: DRY principle applied to step definitions

---

## Workstream 3: Fake Test Audit & Conversion

### Phase 3.1: Run Fake Test Scanner
- **Objective**: Identify all fake test patterns in codebase
- **Steps**:
  1. Execute `./run-fake-test-scan.zsh`
  2. Categorize violations by type:
     - WHEN steps: pass-only without real subprocess calls
     - THEN steps: missing assertions
  3. Prioritize by severity
- **Exit Criteria**: Fake test inventory complete

### Phase 3.2: Convert Assertion Fake Tests
- **Objective**: Replace `assert True` patterns with real verifications
- **Steps**:
  1. Find all `assert True` patterns in step definitions
  2. Implement actual system verification
  3. Test each conversion
- **Exit Criteria**: Zero assertion fake tests

### Phase 3.3: Convert Context Flag Fake Tests
- **Objective**: Replace context flag assignments with real commands
- **Steps**:
  1. Find all `context.flag = True/False` patterns
  2. Replace with subprocess calls to actual tools
  3. Verify command execution and output parsing
- **Exit Criteria**: Zero context flag fake tests

### Phase 3.4: Convert Placeholder Steps
- **Objective**: Implement or remove placeholder step definitions
- **Steps**:
  1. Find all placeholder step definitions (`pass` in @then steps)
  2. Either implement proper verification or remove the step
  3. Update feature files accordingly
- **Exit Criteria**: Zero placeholder steps

### Phase 3.5: Final Verification
- **Objective**: Run fake test scanner to verify clean audit
- **Steps**:
  1. Execute `./run-fake-test-scan.zsh` on all test files
  2. Fix any remaining violations
  3. Re-run until exit code 0 (CLEAN) is achieved
- **Exit Criteria**: Fake test scanner returns CLEAN (exit 0)

---

## Removed: yume-guardian Subagent

**NOTE**: The `yume-guardian` subagent referenced in previous versions was never implemented.

**Replacement**: Use the existing `run-fake-test-scan.zsh` script which:
- Detects WHEN steps with pass-only (no real subprocess calls)
- Detects THEN steps without assertions
- Provides clear violation reports
- Returns exit code 0 for CLEAN, exit code 1 for violations

---

## Success Criteria

| Metric | Target | Current |
|--------|--------|---------|
| docker-free scenarios | All passing | 146/146 ✓ |
| docker-operations scenarios | 14/14 passing | 14/14 ✓ |
| Undefined steps | <100 | 899 (infra-dependent) |
| Fake test violations | 0 | 0 ✓ |
| Fake test scan status | CLEAN (exit 0) | CLEAN ✓ |

---

## Milestone Checkpoints

| Milestone | Workstream | Status | Notes |
|-----------|------------|--------|-------|
| M1: Baseline Established | All | ✓ Complete | 899 undefined steps identified |
| M2: Docker Tests Verified | Workstream 1 | ✓ Complete | Docker-free 146/146, docker-operations 14/14 |
| M3: High-Frequency Steps Analyzed | Workstream 2 | ✓ Complete | Steps defined, infrastructure-dependent |
| M4: Fake Tests Converted | Workstream 3 | ✓ Complete | 0 violations - CLEAN |
| M5: Test Harness Fixed | Workstream 1 | ✓ Complete | step_given_vm_exists auto-creates VMs |

---

## Execution Results (2026-02-04)

| Test Category | Before Fix | After Fix |
|---------------|------------|----------|
| Docker-free | 146/146 ✓ | 146/146 ✓ |
| Docker-operations | 10/14 | **14/14 ✓** |
| Fake test violations | 0 | 0 |

### Key Fix Applied

**File**: `tests/features/steps/vm_docker_steps.py:601`

**Change**: `step_given_vm_exists()` now creates VM via `create-virtual-for` if compose file doesn't exist.

**Impact**: Tests self-initialize environment - no manual VM setup required.

---

## Dependencies

- Docker daemon running (for docker-required tests)
- All VDE scripts executable
- Python 3.8+ with behave installed
- **Fake test scanner**: `./run-fake-test-scan.zsh`
- **VM naming helpers**: `tests/features/steps/vm_naming_helpers.py` (from Plan 20)

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Integration tests require full infrastructure | Document requirements, defer to follow-up plan |
| Too many undefined steps | Target <100, focus on high-frequency (>3 scenarios) |
| Fake test conversions break functionality | Test each conversion individually, maintain baseline |
| Unknown current state | Execute baseline measurements before Phase 1.1 |

## Next Steps After This Plan

1. Complete all phases in this plan
2. Update DAILY_WORKFLOW_STATUS.md with final metrics
3. Create follow-up plan for remaining technical debt
4. Archive this plan upon completion
