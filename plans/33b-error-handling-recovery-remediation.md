# Plan 33b: Error Handling and Recovery Remediation

**Parent Plan**: [Plan 33: Test Suite Remediation](33-comprehensive-test-remediation-plan.md)  
**Priority**: CRITICAL (Tier 1)  
**Created**: 2026-02-06  
**Status**: Not Started

---

## Overview

This plan addresses the Error Handling and Recovery feature, which is critical infrastructure for VDE's reliability and user experience. The feature ensures graceful error handling, clear error messages, automatic recovery, and proper cleanup across all VDE operations.

**Feature File**: `tests/features/docker-required/error-handling-and-recovery.feature`

---

## Current State

### Statistics
- **Total Scenarios**: 15
- **Undefined Steps**: ~45
- **Current Pass Rate**: 0% (all scenarios untested)
- **Target Pass Rate**: ≥80% (12/15 scenarios)

### Scenario Categories
1. **Error Detection** (5 scenarios): Invalid VM names, Docker daemon, disk space, network failures, build failures
2. **Error Recovery** (4 scenarios): Timeouts, SSH failures, permission errors, config errors
3. **Graceful Degradation** (3 scenarios): Multi-VM failures, automatic retry, partial state recovery
4. **Error Communication** (3 scenarios): Clear messages, error logging, rollback on failure

---

## Phase 1: Discovery & Analysis

### 1.1 Run Feature to Identify Undefined Steps
```bash
cd /Users/dderyldowney/dev
behave tests/features/docker-required/error-handling-and-recovery.feature --no-capture --format pretty
```

### 1.2 Categorize Undefined Steps

Expected step categories:
- **Error Simulation**: Steps that trigger specific error conditions
- **Error Detection**: Steps that verify VDE detects errors
- **Error Messages**: Steps that validate error message content
- **Recovery Actions**: Steps that verify automatic recovery
- **State Verification**: Steps that check system state after errors

### 1.3 Identify Required Libraries

Libraries needed:
- `scripts/lib/vde-errors` - Error message generation
- `scripts/lib/vde-log` - Error logging
- `scripts/lib/vde-core` - VM operations
- `scripts/lib/vm-common` - Docker operations
- Docker Python SDK - Container operations
- Subprocess - Command execution

---

## Phase 2: Step Definition Planning

### 2.1 Error Simulation Steps

| Step Pattern | Implementation Approach |
|--------------|------------------------|
| `Given I try to use a VM that doesn't exist` | Set context.vm_name to non-existent VM |
| `Given Docker is not available` | Mock Docker availability check or stop Docker |
| `Given my disk is nearly full` | Mock disk space check |
| `Given the Docker network can't be created` | Mock network creation failure |
| `Given a VM build fails` | Use invalid Dockerfile or mock build failure |
| `Given a container takes too long to start` | Mock timeout condition |
| `Given a container is running but SSH fails` | Start container, block SSH port |
| `Given I don't have permission for an operation` | Mock permission check |
| `Given a docker-compose.yml is malformed` | Create invalid compose file |
| `Given one VM fails to start` | Configure one VM to fail |
| `Given a transient error occurs` | Mock retryable error |
| `Given an operation is interrupted` | Simulate partial state |
| `Given any error occurs` | Generic error trigger |
| `Given an error occurs` | Generic error trigger |
| `Given an operation fails partway through` | Simulate partial completion |

### 2.2 Error Detection Steps

| Step Pattern | Implementation Approach |
|--------------|------------------------|
| `Then I should receive a clear error message` | Verify error message in output |
| `Then VDE should detect the conflict` | Check port conflict detection |
| `Then I should receive a helpful error` | Verify error message quality |
| `Then VDE should detect the issue` | Check disk space detection |
| `Then VDE should report the specific error` | Verify error specificity |
| `Then I should see what went wrong` | Check error details |
| `Then it should report the issue` | Verify timeout reporting |
| `Then VDE should diagnose the problem` | Check SSH diagnostics |
| `Then it should explain the permission issue` | Verify permission error message |
| `Then VDE should detect the error` | Check config validation |
| `Then VDE should detect it's retryable` | Check retry logic |
| `Then VDE should detect partial state` | Check state detection |
| `Then the failure is detected` | Verify failure detection |

### 2.3 Error Message Validation Steps

| Step Pattern | Implementation Approach |
|--------------|------------------------|
| `And the error should explain what went wrong` | Parse error message for explanation |
| `And suggest valid VM names` | Check for VM name suggestions |
| `And the error should explain Docker is required` | Verify Docker requirement message |
| `And suggest how to fix it` | Check for remediation steps |
| `And warn me before starting` | Verify warning message |
| `And suggest cleaning up` | Check cleanup suggestions |
| `And suggest troubleshooting steps` | Verify troubleshooting guidance |
| `And get suggestions for fixing it` | Check fix suggestions |
| `And show the container logs` | Verify log output |
| `And verify the SSH port is correct` | Check SSH port validation |
| `And show the specific problem` | Verify problem details |
| `And suggest how to fix the configuration` | Check config fix suggestions |
| `And explain what went wrong` | Verify explanation |
| `And suggest next steps` | Check next step guidance |

### 2.4 Recovery Action Steps

| Step Pattern | Implementation Approach |
|--------------|------------------------|
| `And allocate an available port` | Verify port reallocation |
| `And offer to retry` | Check retry option |
| `And be able to retry after fixing` | Test retry functionality |
| `And offer to check the status` | Verify status check option |
| `And check if SSH is running` | Test SSH status check |
| `And offer to retry with proper permissions` | Check permission retry |
| `Then it should automatically retry` | Verify automatic retry |
| `And limit the number of retries` | Check retry limit |
| `And report if all retries fail` | Verify final failure report |
| `And complete the operation` | Check operation completion |
| `And not duplicate work` | Verify idempotency |
| `Then VDE should clean up partial state` | Check cleanup actions |
| `And return to a consistent state` | Verify state consistency |
| `And allow me to retry cleanly` | Test clean retry |

### 2.5 State Verification Steps

| Step Pattern | Implementation Approach |
|--------------|------------------------|
| `And continue with the operation` | Verify operation continues |
| `Then other VMs should continue` | Check multi-VM isolation |
| `And I should be notified of the failure` | Verify failure notification |
| `And successful VMs should be listed` | Check success list |
| `Then the error should be logged` | Verify log file creation |
| `And the error should have sufficient detail for debugging` | Check log detail |
| `And I can find it in the logs directory` | Verify log location |
| `Then it should be in plain language` | Check message clarity |

---

## Phase 3: Implementation

### Iteration 1: Error Detection (Scenarios 1-5)
**Focus**: Invalid VM names, Docker daemon, disk space, network failures, build failures

**Steps to Implement** (~15 steps):
1. VM existence validation
2. Docker availability check
3. Disk space detection
4. Network creation error handling
5. Build failure detection
6. Error message generation
7. Suggestion generation

**Validation**:
```bash
behave tests/features/docker-required/error-handling-and-recovery.feature --tags=@error-detection
```

### Iteration 2: Error Recovery (Scenarios 6-9)
**Focus**: Timeouts, SSH failures, permission errors, config errors

**Steps to Implement** (~12 steps):
1. Timeout detection
2. SSH diagnostics
3. Permission checking
4. Config validation
5. Log output capture
6. Status checking
7. Retry mechanisms

**Validation**:
```bash
behave tests/features/docker-required/error-handling-and-recovery.feature --tags=@error-recovery
```

### Iteration 3: Graceful Degradation (Scenarios 10-12)
**Focus**: Multi-VM failures, automatic retry, partial state recovery

**Steps to Implement** (~10 steps):
1. Multi-VM isolation
2. Failure notification
3. Success tracking
4. Automatic retry logic
5. Retry limits
6. Partial state detection
7. Idempotent operations

**Validation**:
```bash
behave tests/features/docker-required/error-handling-and-recovery.feature --tags=@graceful-degradation
```

### Iteration 4: Error Communication (Scenarios 13-15)
**Focus**: Clear messages, error logging, rollback on failure

**Steps to Implement** (~8 steps):
1. Plain language messages
2. Error explanation
3. Next step suggestions
4. Error logging
5. Log detail capture
6. Log file location
7. Cleanup on failure
8. State consistency

**Validation**:
```bash
behave tests/features/docker-required/error-handling-and-recovery.feature --tags=@error-communication
```

---

## Phase 4: Validation

### 4.1 Run Full Feature Test
```bash
behave tests/features/docker-required/error-handling-and-recovery.feature --no-capture --format pretty
```

### 4.2 Success Criteria
- ≥12/15 scenarios passing (80%)
- 0 undefined steps
- 0 AmbiguousStep errors
- All error messages are clear and actionable
- All recovery mechanisms work correctly

### 4.3 Known Acceptable Failures
Document any scenarios that may fail due to:
- Environment-specific issues
- Docker version differences
- Timing-dependent behavior

---

## Phase 5: Integration Testing

### 5.1 Cross-Feature Testing
Test error handling integration with:
- Docker operations
- VM lifecycle management
- SSH configuration
- Multi-VM workflows

### 5.2 Real-World Scenarios
Test common error scenarios:
1. Start VM when Docker is stopped
2. Create VM with insufficient disk space
3. Start multiple VMs with one failing
4. Recover from interrupted operations
5. Handle network connectivity issues

---

## Phase 6: Completion

### 6.1 Documentation Updates
- Update `docs/troubleshooting.md` with error scenarios
- Document error codes and messages
- Add recovery procedures

### 6.2 Update Master Plan
Update [`plans/33-comprehensive-test-remediation-plan.md`](33-comprehensive-test-remediation-plan.md:1) with:
- Plan 33b status: Complete
- Scenarios passing: X/15
- Lessons learned

### 6.3 Commit Changes
```bash
git add tests/features/steps/error_handling_steps.py
git add tests/features/docker-required/error-handling-and-recovery.feature
git commit -m "feat: implement error handling and recovery tests

- Add 45+ step definitions for error scenarios
- Implement error detection and recovery
- Add graceful degradation support
- Implement error logging and rollback
- Achieve 12/15 scenarios passing (80%)

Refs: Plan 33b"
```

---

## Estimated Effort

| Phase | Estimated Time |
|-------|----------------|
| Phase 1: Discovery & Analysis | 1-1.5 hours |
| Phase 2: Step Definition Planning | 1.5-2 hours |
| Phase 3: Implementation | 4-5 hours |
| Phase 4: Validation | 0.5-1 hour |
| Phase 5: Integration Testing | 0.5-1 hour |
| Phase 6: Completion | 0.5-1 hour |
| **Total** | **8-11.5 hours** |

---

## Risks and Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Error simulation complexity | High | Use mocking for hard-to-simulate errors |
| Docker state interference | Medium | Ensure proper cleanup between tests |
| Timing-dependent failures | Medium | Use retries and timeouts appropriately |
| Environment-specific errors | Low | Document acceptable failures |

---

## Dependencies

- **Completed**: Plan 33a (Docker Operations) - provides base Docker functionality
- **Required Libraries**: vde-errors, vde-log, vde-core, vm-common
- **External**: Docker daemon, disk space, network connectivity

---

## Next Steps

1. **Start Phase 1**: Run feature to identify all undefined steps
2. **Create step file**: `tests/features/steps/error_handling_steps.py`
3. **Implement in iterations**: Follow Phase 3 plan
4. **Validate continuously**: Run tests after each iteration
5. **Update master plan**: Track progress in Plan 33

---

## References

- [Plan 33: Master Remediation Plan](33-comprehensive-test-remediation-plan.md)
- [Plan 33a: Docker Operations](33a-docker-operations-remediation.md) - Template and dependency
- [VDE Error Library](../scripts/lib/vde-errors)
- [VDE Log Library](../scripts/lib/vde-log)
- [Troubleshooting Documentation](../docs/troubleshooting.md)
