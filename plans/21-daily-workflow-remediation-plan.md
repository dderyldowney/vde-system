# Plan 21: Daily Workflow Remediation Plan

**Created**: 2026-02-04
**Previous Commit**: 590be53 - test: fix docker-operations BDD tests
**Status**: docker-operations complete (14/14 scenarios passing)
**Last Updated**: 2026-02-04 (integrated findings from Plans 08, 11, 16, 18, 20)

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

### Phase 1.2: Run Docker-Required Tests (Non-Integration)
- **Objective**: Run docker-required tests that don't need full infrastructure
- **Steps**:
  1. Execute `behave tests/features/docker-required/ --exclude-tags=@integration`
  2. Verify docker-operations.feature still passes (baseline: 14/14)
  3. Identify other passing docker-required features
  4. Run fake test scanner: `./run-fake-test-scan.zsh`
- **Reference**: Plan 18 yume-guardian status: CLEAN (0 violations)
- **Exit Criteria**: docker-operations baseline maintained, fake test scan complete

### Phase 1.3: Integration Test Preparation
- **Objective**: Document integration test requirements
- **Steps**:
  1. List all `@integration` tagged scenarios
  2. Document infrastructure requirements for each
  3. Create infrastructure setup checklist
- **Exit Criteria**: Integration test inventory complete

---

## Workstream 2: Remaining Undefined Steps Implementation

### Phase 2.1: Inventory Undefined Steps
- **Objective**: Catalog all undefined steps across features
- **Steps**:
  1. Execute `behave tests/features/ --dry-run` to list undefined steps
  2. Group undefined steps by feature file
  3. Prioritize by frequency (most common first)
  4. Compare with Plan 11 baseline: ~1003 undefined steps (reduced from ~1990, 49% improvement)
- **Reference**: Step files already created from Plan 11:
   - `productivity_steps.py`, `debugging_steps.py`, `config_steps.py`
   - `daily_workflow_steps.py`, `ssh_agent_steps.py`, `ssh_git_steps.py`
   - `team_collaboration_steps.py`, `template_steps.py`
- **Exit Criteria**: Undefined step inventory with counts

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
  2. Categorize violations by type
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

### Phase 3.5: Final Guardian Verification
- **Objective**: Run yume-guardian to verify clean audit
- **Steps**:
  1. Execute yume-guardian on all test files
  2. Fix any remaining violations
  3. Re-run until CLEAN status achieved
- **Exit Criteria**: yume-guardian returns CLEAN

---

## Success Criteria

| Metric | Target | Current |
|--------|--------|---------|
| docker-operations scenarios | 14/14 passing | 14/14 ✓ |
| Full test suite | All passing | TBD |
| Undefined steps | 0 | TBD |
| Fake test violations | 0 | TBD |
| yume-guardian status | CLEAN | TBD |

---

## Dependencies

- Docker daemon running (for docker-required tests)
- All VDE scripts executable
- Python 3.8+ with behave installed
- **Pre-flight check**: Run `./run-fake-test-scan.zsh` before Phase 3.1
- **VM naming helpers**: `tests/features/steps/vm_naming_helpers.py` (from Plan 20)

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Integration tests require full infrastructure | Document requirements, phase integration testing separately |
| Too many undefined steps | Prioritize by frequency, focus on high-impact steps |
| Fake test conversions break functionality | Test each conversion individually, maintain baseline |

## Next Steps After This Plan

1. Complete all phases in this plan
2. Update DAILY_WORKFLOW_STATUS.md with final metrics
3. Create follow-up plan for remaining technical debt
4. Archive this plan upon completion
