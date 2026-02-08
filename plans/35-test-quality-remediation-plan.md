# Plan 35: Test Quality Remediation

**Created**: 2026-02-08
**Scope**: Eliminate placeholder tests, add missing unit tests, improve test verification quality
**Status**: IMPLEMENTED

---

## Executive Summary

An audit of the VDE test suite revealed systemic quality issues that undermine test reliability. The test suite has **478 BDD scenarios** and **4 unit test files**, but contains **27 `assert True` placeholders** and **65 `pass` stubs** in step definitions — tests that always pass regardless of actual behavior. Additionally, 6 of 15 core shell libraries (~2,300 lines, ~127 functions) have zero dedicated unit tests, and no security-focused tests exist.

This plan addresses remediation across 5 phases, ordered by impact.

---

## Phase 1: Eliminate Placeholder Tests (Critical)

**Goal**: Replace all `assert True` and `pass` stubs with real verification logic.
**Impact**: Eliminates false-passing tests that mask real bugs.

### 1.1: Replace `assert True` Placeholders (27 occurrences, 9 files)

| File | Occurrences | Action |
|------|-------------|--------|
| `tests/features/steps/vm_to_host_steps.py` | Multiple | Replace with subprocess Docker/SSH checks |
| `tests/features/steps/network_and_resource_steps.py` | Multiple | Replace with `docker network inspect` assertions |
| `tests/features/steps/ssh_agent_steps.py` | Multiple | Replace with `ssh-add -l` / key file checks |
| `tests/features/steps/error_handling_steps.py` | Multiple | Replace with exit code and stderr assertions |
| `tests/features/steps/collaboration_steps.py` | Multiple | Replace with config file verification |
| `tests/features/steps/debugging_steps.py` | Multiple | Replace with log file/output assertions |
| `tests/features/steps/productivity_steps.py` | Multiple | Replace with command output verification |
| `tests/features/steps/maintenance_steps.py` | Multiple | Replace with state file checks |
| `tests/features/steps/port_management_steps.py` | Multiple | Replace with port binding verification |

**Pattern to fix**:
```python
# BEFORE (placeholder)
@then('the VM should be accessible from the host')
def step_vm_accessible(context):
    assert True

# AFTER (real verification)
@then('the VM should be accessible from the host')
def step_vm_accessible(context):
    result = subprocess.run(
        ['docker', 'exec', context.vm_name, 'echo', 'accessible'],
        capture_output=True, text=True, timeout=10
    )
    assert result.returncode == 0, f"VM not accessible: {result.stderr}"
```

### 1.2: Implement `pass` Stub Steps (65 occurrences)

Same files as above, plus additional step definition files. Each `pass` in a `@then` decorator must be replaced with actual state verification.

**Priority order**: `@then` steps first (verification), then `@when` steps (actions), then `@given` steps (preconditions).

### 1.3: Replace Context-Flag-Only Steps

Several steps set context flags without performing real operations:
```python
# BEFORE (flag-only)
@given('I need to check what\'s running on my host')
def step_need_check_host(context):
    context.needs_host_check = True

# AFTER (real precondition)
@given('I need to check what\'s running on my host')
def step_need_check_host(context):
    result = subprocess.run(['docker', 'ps', '--format', '{{.Names}}'],
                            capture_output=True, text=True)
    assert result.returncode == 0, "Docker not available"
    context.running_containers = result.stdout.strip().split('\n')
```

**Success Criteria**:
- [ ] Zero `assert True` in step definitions
- [ ] Zero `pass` stubs in `@then` decorated steps
- [ ] All `@when` steps execute real commands
- [ ] `make test-docker-free` still passes
- [ ] `make test-docker-required` still passes

---

## Phase 2: Unit Tests for Untested Shell Libraries (High)

**Goal**: Add dedicated unit tests for 6 core libraries with no test coverage.
**Impact**: Covers ~2,300 lines / ~127 functions with fast-running tests.

### 2.1: `vde-progress` (451 lines, 20 functions)

**File to create**: `tests/unit/test_vde_progress.sh` (or Python wrapper)
**Functions to test**:
- Progress bar rendering at various percentages
- Spinner animation states
- Multi-step progress tracking
- Terminal width handling / edge cases
- Color output vs no-color mode

### 2.2: `vde-health` (392 lines, 6 functions)

**File to create**: `tests/unit/test_vde_health.sh`
**Functions to test**:
- Health check for running containers
- Health check for stopped containers
- Health check when Docker is unavailable
- Aggregate health status reporting
- Health check timeout handling

### 2.3: `vde-metrics` (330 lines, 19 functions)

**File to create**: `tests/unit/test_vde_metrics.sh`
**Functions to test**:
- Metric collection (CPU, memory, disk)
- Metric formatting and display
- Metric history/trend calculation
- Edge cases: missing data, overflow values

### 2.4: `vde-audit` (360 lines, 18 functions)

**File to create**: `tests/unit/test_vde_audit.sh`
**Functions to test**:
- Audit log creation and rotation
- Event recording with timestamps
- Audit trail querying/filtering
- File permission checks on audit logs

### 2.5: `vde-errors` (316 lines, 21 functions)

**File to create**: `tests/unit/test_vde_errors.sh`
**Functions to test**:
- Error code mapping
- Error message formatting
- Error recovery suggestions
- Stack trace capture
- Exit code propagation

### 2.6: `vde-log` (468 lines, 25 functions)

**File to create**: `tests/unit/test_vde_log.sh`
**Functions to test**:
- Log level filtering (debug, info, warn, error)
- Log file rotation
- Structured log output (JSON mode)
- Log destination routing (file, stderr, syslog)
- Timestamp formatting

**Success Criteria**:
- [ ] Each library has a dedicated test file
- [ ] At least 80% function coverage per library
- [ ] All tests pass in CI (add to `make test-unit`)
- [ ] Tests run without Docker dependency

---

## Phase 3: Security Test Suite (High)

**Goal**: Add security-focused tests for command injection, path traversal, and permission issues.
**Impact**: Prevents security regressions in a tool that manages Docker containers and SSH keys.

### 3.1: Command Injection Tests

**File to create**: `tests/security/test_command_injection.sh`
**Scenarios**:
- VM names containing shell metacharacters: `; rm -rf /`, `$(whoami)`, `` `id` ``
- Template values with injection payloads
- Config values with pipe/redirect characters
- SSH key paths with spaces and special characters

### 3.2: Path Traversal Tests

**File to create**: `tests/security/test_path_traversal.sh`
**Scenarios**:
- VM names containing `../` sequences
- Template include paths outside allowed directory
- Config file references with absolute paths
- Symlink following in config directories

### 3.3: Permission and Privilege Tests

**File to create**: `tests/security/test_permissions.sh`
**Scenarios**:
- SSH key file permissions (should be 600/700)
- Docker socket access validation
- Config file ownership checks
- Temporary file creation permissions

**Success Criteria**:
- [ ] All injection payloads are properly sanitized or rejected
- [ ] Path traversal attempts are blocked
- [ ] File permissions are correctly enforced
- [ ] Security tests added to CI pipeline
- [ ] Add `make test-security` target to Makefile

---

## Phase 4: Error Path and Negative Testing (Medium)

**Goal**: Add scenarios for failure modes not currently tested.
**Impact**: Catches edge-case regressions and improves error handling.

### 4.1: Malformed Input Tests

**Add to existing BDD features or create new feature files**:
- Corrupted Docker Compose YAML
- Invalid VM type names
- Empty/missing configuration files
- Truncated state files

### 4.2: Resource Exhaustion Tests

- Disk full during VM creation (mock via tmpfs)
- Port exhaustion (all ports in range allocated)
- Maximum container limit reached

### 4.3: Concurrent Operation Tests

- Two `vde create` commands for same VM simultaneously
- `vde stop` during `vde create`
- Config modification during VM startup

### 4.4: Network Failure Tests

- Docker registry unreachable during pull
- DNS resolution failure
- SSH connection timeout to VM

**Success Criteria**:
- [ ] At least 10 new negative test scenarios
- [ ] All error paths produce clear error messages
- [ ] No unhandled exceptions or silent failures
- [ ] Error scenarios documented in feature files

---

## Phase 5: Performance Benchmarks (Medium)

**Goal**: Establish baseline performance metrics to detect regressions.
**Impact**: Prevents latency regressions in CI.

### 5.1: Benchmark Suite

**File to create**: `tests/performance/benchmark_suite.sh`
**Metrics**:
- VM startup time (target: < 30s for standard VMs)
- Natural language parser response time (target: < 500ms)
- Template rendering time (target: < 1s)
- Config file load time (target: < 100ms)
- Cache hit vs miss performance delta

### 5.2: CI Integration

- Add `make test-benchmark` target
- Store results as CI artifacts for trend tracking
- Alert on > 20% regression from baseline

**Success Criteria**:
- [ ] Baseline measurements recorded for all metrics
- [ ] Benchmark suite runs in CI
- [ ] Regression threshold alerts configured

---

## Implementation Order and Estimates

| Phase | Description | Priority | Files Changed | New Files |
|-------|-------------|----------|---------------|-----------|
| 1 | Eliminate placeholders | Critical | ~9 step files | 0 |
| 2 | Shell library unit tests | High | Makefile, CI | 6 test files |
| 3 | Security test suite | High | Makefile, CI | 3 test files |
| 4 | Error path testing | Medium | Feature files, step files | 1-2 feature files |
| 5 | Performance benchmarks | Medium | Makefile, CI | 1 benchmark file |

**Recommended execution**: Phases 1-3 in parallel (independent), Phase 4 after Phase 1, Phase 5 independent.

---

## Verification

After each phase, run:
```bash
make test-docker-free    # Fast verification
make test-unit           # Unit tests
make lint                # No regressions
make test-docker-required  # Full integration (Phase 1 changes)
```

---

## Related Plans

- [Plan 33: Comprehensive Test Remediation](33-comprehensive-test-remediation-plan.md) — Prior remediation effort for specific features
- [Plan 34: Test Suite Full Remediation](34-test-remediation-plan.md) — Remediation of 33d/33e/33f failures
