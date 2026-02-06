# Plan 33c: Daily Development Workflow Remediation

**Parent Plan**: [Plan 33: Test Suite Remediation](33-comprehensive-test-remediation-plan.md)  
**Priority**: HIGH (Tier 1)  
**Created**: 2026-02-06  
**Status**: Not Started

---

## Overview

This plan addresses the Daily Development Workflow feature, which covers the most common user interactions with VDE. These are the workflows developers use every day to start, stop, check status, and manage their development environments.

**Feature File**: `tests/features/docker-required/daily-development-workflow.feature`

---

## Current State

### Statistics
- **Total Scenarios**: 8
- **Undefined Steps**: ~40
- **Current Pass Rate**: 0% (all scenarios untested)
- **Target Pass Rate**: ≥75% (6/8 scenarios)

### Scenario Categories
1. **Basic Operations** (3 scenarios): Starting environment, checking status, stopping work
2. **Connection Management** (1 scenario): Getting connection information
3. **Advanced Operations** (3 scenarios): Restart with rebuild, multiple VMs, first-time creation
4. **User Guide Integration** (2 scenarios): Tagged for user guide documentation

---

## Phase 1: Discovery & Analysis

### 1.1 Run Feature to Identify Undefined Steps
```bash
cd /Users/dderyldowney/dev
behave tests/features/docker-required/daily-development-workflow.feature --no-capture --format pretty
```

### 1.2 Categorize Undefined Steps

Expected step categories:
- **Environment Setup**: VDE installation, VM configuration
- **VM Operations**: Start, stop, restart, rebuild
- **Status Queries**: List running VMs, connection details
- **Multi-VM Operations**: Starting multiple VMs, network setup
- **Verification**: SSH access, workspace mounting, communication

### 1.3 Identify Required Libraries

Libraries needed:
- `scripts/lib/vde-core` - VM operations
- `scripts/lib/vm-common` - Docker operations
- `scripts/lib/vde-parser` - Natural language parsing
- `scripts/lib/vde-commands` - Safe wrapper functions
- Docker Python SDK - Container operations
- SSH client - Connection verification

---

## Phase 2: Step Definition Planning

### 2.1 Environment Setup Steps

| Step Pattern | Implementation Approach |
|--------------|------------------------|
| `Given I have VDE installed` | Verify VDE scripts exist and are executable |
| `Given I have several VMs running` | Start multiple test VMs |
| `Given I have a Python VM running` | Start Python VM, verify running |
| `Given I have multiple VMs running` | Start 2+ VMs for testing |
| `Given I need a full stack environment` | Set context for multi-VM scenario |
| `Given I want to try a new language` | Set context for new VM creation |

### 2.2 VM Operation Steps

| Step Pattern | Implementation Approach |
|--------------|------------------------|
| `When I request to start my Python development environment` | Execute start command for Python VM |
| `When I ask "what's running?"` | Execute status/list command |
| `When I ask "how do I connect to Python?"` | Execute connection info command |
| `When I request to "stop everything"` | Execute stop all command |
| `When I request to "restart python with rebuild"` | Execute restart with --build flag |
| `When I request to "start python and postgres"` | Execute start command for multiple VMs |
| `When I request to "create a Go VM"` | Execute create/init command for Go |

### 2.3 Verification Steps

| Step Pattern | Implementation Approach |
|--------------|------------------------|
| `Then the Python VM should be started` | Verify container running via docker ps |
| `And SSH access should be available on the configured port` | Test SSH connection |
| `And my workspace directory should be mounted` | Check volume mount in container |
| `Then I should see a list of all running VMs` | Parse output for VM list |
| `And each VM should show its status` | Verify status field for each VM |
| `And the list should include both language and service VMs` | Check VM types in output |
| `Then I should receive SSH connection details` | Verify connection info in output |
| `And the details should include the hostname` | Parse hostname from output |
| `And the details should include the port number` | Parse port from output |
| `And the details should include the username` | Parse username from output |
| `Then all running VMs should be stopped` | Verify no containers running |
| `And no containers should be left running` | Check docker ps output empty |
| `And the operation should complete without errors` | Verify exit code 0 |
| `Then the Python VM should be stopped` | Verify container stopped |
| `And the container should be rebuilt from the Dockerfile` | Check docker build executed |
| `And the Python VM should be started again` | Verify container running |
| `And my workspace should still be mounted` | Check volume mount persists |
| `Then both Python and PostgreSQL VMs should start` | Verify both containers running |
| `And they should be on the same Docker network` | Check network membership |
| `And they should be able to communicate` | Test network connectivity |
| `Then the Go VM configuration should be created` | Verify config files exist |
| `And the Docker image should be built` | Check image exists |
| `And SSH keys should be configured` | Verify SSH config created |
| `And the VM should be ready to start` | Verify VM can be started |

---

## Phase 3: Implementation

### Iteration 1: Basic Operations (Scenarios 1-3)
**Focus**: Starting environment, checking status, stopping work

**Steps to Implement** (~15 steps):
1. VDE installation verification
2. Start Python VM
3. SSH access verification
4. Workspace mount verification
5. List running VMs
6. VM status display
7. Stop all VMs
8. Container cleanup verification

**Validation**:
```bash
behave tests/features/docker-required/daily-development-workflow.feature --tags=@basic-operations
```

### Iteration 2: Connection Management (Scenario 4)
**Focus**: Getting connection information

**Steps to Implement** (~8 steps):
1. Start Python VM
2. Request connection info
3. Parse hostname
4. Parse port number
5. Parse username
6. Verify complete connection details

**Validation**:
```bash
behave tests/features/docker-required/daily-development-workflow.feature:23
```

### Iteration 3: Advanced Operations (Scenarios 5-7)
**Focus**: Restart with rebuild, multiple VMs, first-time creation

**Steps to Implement** (~12 steps):
1. Restart with rebuild flag
2. Verify rebuild execution
3. Verify workspace persistence
4. Start multiple VMs
5. Verify network setup
6. Test inter-VM communication
7. Create new VM
8. Verify configuration creation
9. Verify image build
10. Verify SSH setup

**Validation**:
```bash
behave tests/features/docker-required/daily-development-workflow.feature --tags=@advanced-operations
```

### Iteration 4: Integration & Polish (Scenario 8)
**Focus**: User guide integration, end-to-end workflows

**Steps to Implement** (~5 steps):
1. Complete workflow testing
2. User guide tag verification
3. Documentation alignment
4. Error message polish

**Validation**:
```bash
behave tests/features/docker-required/daily-development-workflow.feature --tags=@user-guide
```

---

## Phase 4: Validation

### 4.1 Run Full Feature Test
```bash
behave tests/features/docker-required/daily-development-workflow.feature --no-capture --format pretty
```

### 4.2 Success Criteria
- ≥6/8 scenarios passing (75%)
- 0 undefined steps
- 0 AmbiguousStep errors
- All @user-guide scenarios passing
- Real Docker operations (no fake tests)

### 4.3 Known Acceptable Failures
Document any scenarios that may fail due to:
- Network timing issues
- Docker resource constraints
- SSH connection delays

---

## Phase 5: Integration Testing

### 5.1 Cross-Feature Testing
Test daily workflow integration with:
- Docker operations (Plan 33a)
- Error handling (Plan 33b)
- SSH configuration (Plan 32)
- Natural language commands (Plan 33d)

### 5.2 Real-World Workflows
Test complete daily workflows:
1. Morning: Start Python + Postgres, check status, connect
2. Midday: Restart with rebuild, verify workspace
3. Evening: Stop everything, verify cleanup
4. New project: Create new VM, configure, start

---

## Phase 6: Completion

### 6.1 Documentation Updates
- Update `USER_GUIDE.md` with daily workflow examples
- Document common workflows in `docs/development-workflows.md`
- Add troubleshooting tips for common issues

### 6.2 Update Master Plan
Update [`plans/33-comprehensive-test-remediation-plan.md`](33-comprehensive-test-remediation-plan.md:1) with:
- Plan 33c status: Complete
- Scenarios passing: X/8
- Lessons learned

### 6.3 Commit Changes
```bash
git add tests/features/steps/daily_workflow_steps.py
git add tests/features/docker-required/daily-development-workflow.feature
git commit -m "feat: implement daily development workflow tests

- Add 40+ step definitions for daily workflows
- Implement start, stop, status operations
- Add connection information retrieval
- Implement restart with rebuild
- Add multi-VM startup support
- Achieve 6/8 scenarios passing (75%)

Refs: Plan 33c"
```

---

## Estimated Effort

| Phase | Estimated Time |
|-------|----------------|
| Phase 1: Discovery & Analysis | 0.5-1 hour |
| Phase 2: Step Definition Planning | 1-1.5 hours |
| Phase 3: Implementation | 3-4 hours |
| Phase 4: Validation | 0.5-1 hour |
| Phase 5: Integration Testing | 0.5-1 hour |
| Phase 6: Completion | 0.5-1 hour |
| **Total** | **6-9.5 hours** |

---

## Risks and Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Network timing issues | Medium | Add appropriate timeouts and retries |
| Docker resource constraints | Medium | Ensure proper cleanup between tests |
| SSH connection delays | Low | Use connection retry logic |
| Multi-VM coordination | Medium | Test network setup thoroughly |

---

## Dependencies

- **Completed**: Plan 33a (Docker Operations) - provides base Docker functionality
- **Completed**: Plan 32 (SSH Configuration) - provides SSH setup
- **Required Libraries**: vde-core, vm-common, vde-parser, vde-commands
- **External**: Docker daemon, SSH client

---

## Next Steps

1. **Start Phase 1**: Run feature to identify all undefined steps
2. **Create step file**: `tests/features/steps/daily_workflow_steps.py`
3. **Implement in iterations**: Follow Phase 3 plan
4. **Validate continuously**: Run tests after each iteration
5. **Update master plan**: Track progress in Plan 33

---

## References

- [Plan 33: Master Remediation Plan](33-comprehensive-test-remediation-plan.md)
- [Plan 33a: Docker Operations](33a-docker-operations-remediation.md) - Dependency
- [Plan 33b: Error Handling](33b-error-handling-recovery-remediation.md) - Related
- [Plan 32: SSH Configuration](32-ssh-configuration-remediation-plan-detailed.md) - Dependency
- [Development Workflows Documentation](../docs/development-workflows.md)
- [User Guide](../USER_GUIDE.md)
