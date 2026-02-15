# Test Suite Remediation Plan

**Created:** 2026-02-13  
**Status:** Draft - Awaiting User Approval  
**Goal:** Increase test pass rate from 79.6% to 95%+ by fixing failing tests and implementing undefined steps

---

## Executive Summary

The VDE test suite has:
- **324 total scenarios**
- **258 passing (79.6%)**
- **65 failing**
- **1 errored**
- **366 undefined steps** (documentation-only scenarios without step definitions)

This plan breaks down remediation into prioritized, actionable steps.

---

## Problem Analysis

### Root Causes Identified (from PROJECT_STATUS.md)

1. **Shell Compatibility** - Previously fixed (zsh vs bash)
2. **Timing Issues** - Container health checks not deterministic
3. **Port Collision Handling** - Re-allocation logic incomplete
4. **Multi-VM Coordination** - SSH config merging brittle
5. **Network Resolution** - Inter-container networking unreliable
6. **State Preservation** - VM state not correctly tracked across operations

### Test Categories by Priority

| Priority | Category | Files | Impact |
|----------|----------|-------|--------|
| P0 | Docker Operations | docker-operations.feature | Blocking |
| P0 | VM Lifecycle | vm-lifecycle.feature | Blocking |
| P1 | Port Management | port-management.feature | High |
| P1 | SSH Configuration | ssh-configuration.feature | High |
| P1 | Multi-Project Workflow | multi-project-workflow.feature | High |
| P2 | Team Collaboration | team-collaboration.feature | Medium |
| P2 | Error Handling | error-handling-and-recovery.feature | Medium |
| P2 | Health Monitoring | debugging-troubleshooting.feature | Medium |

---

## Step-by-Step Implementation Plan

### Phase 1: Environment & Core Infrastructure

#### Step 1.1: Fix Docker Operations Tests
- [ ] **1.1.1** Run `behave tests/features/docker-required/docker-operations.feature --dry-run` to identify undefined steps
- [ ] **1.1.2** Review docker_lifecycle_steps.py for existing implementations
- [ ] **1.1.3** Implement missing step definitions for `docker-compose.yml` location/parsing
- [ ] **1.1.4** Fix container creation timeout (currently too short for build)
- [ ] **1.1.5** Verify docker-operations tests pass

#### Step 1.2: Fix VM Lifecycle Tests
- [ ] **1.2.1** Run `behave tests/features/docker-required/vm-lifecycle.feature --dry-run` 
- [ ] **1.2.2** Review vm_creation_steps.py and vm_operations_steps.py
- [ ] **1.2.3** Implement missing start/stop/remove step definitions
- [ ] **1.2.4** Add state verification steps (running vs stopped)
- [ ] **1.2.5** Verify vm-lifecycle tests pass

### Phase 2: High Priority Integrations

#### Step 2.1: Fix Port Management Tests
- [ ] **2.1.1** Analyze port-management.feature scenarios
- [ ] **2.1.2** Review port_management_steps.py
- [ ] **2.1.3** Implement port collision detection step definitions
- [ ] **2.1.4** Add re-allocation logic (2200 → 2201) verification
- [ ] **2.1.5** Verify port-conflict handling scenario passes

#### Step 2.2: Fix SSH Configuration Tests
- [ ] **2.2.1** Analyze ssh-configuration.feature scenarios
- [ ] **2.2.2** Review ssh_config_steps.py
- [ ] **2.2.3** Implement SSH config merging step definitions
- [ ] **2.2.4** Add multi-developer sync verification
- [ ] **2.2.5** Verify ssh-configuration tests pass

#### Step 2.3: Fix Multi-Project Workflow Tests
- [ ] **2.3.1** Analyze multi-project-workflow.feature scenarios
- [ ] **2.3.2** Review multi_project_workflow_steps.py
- [ ] **2.3.3** Implement simultaneous SSH access steps
- [ ] **2.3.4** Add project switching verification
- [ ] **2.3.5** Verify multi-project tests pass

### Phase 3: Service Integration

#### Step 3.1: Fix Database Connectivity Tests
- [ ] **3.1.1** Analyze configuration-management.feature for service port tests
- [ ] **3.1.2** Implement PostgreSQL connectivity verification (port 2400)
- [ ] **3.1.3** Implement Redis connectivity verification
- [ ] **3.1.4** Fix inter-container network resolution (vde-net)
- [ ] **3.1.5** Verify service connectivity tests pass

#### Step 3.2: Fix Data Persistence Tests
- [ ] **3.2.1** Review data persistence scenarios
- [ ] **3.2.2** Implement volume verification step definitions
- [ ] **3.2.3** Add data retention verification after restart
- [ ] **3.2.4** Verify persistence tests pass

### Phase 4: Error Handling & Recovery

#### Step 4.1: Fix Error Path Tests
- [ ] **4.1.1** Run `behave tests/features/docker-free/error-path-testing.feature --dry-run`
- [ ] **4.1.2** Verify error_path_steps.py implementations are correct
- [ ] **4.1.3** Add "Solution" and "Suggestions" to error messages
- [ ] **4.1.4** Verify error-path tests pass

#### Step 4.2: Fix Recovery Tests
- [ ] **4.2.1** Analyze error-handling-and-recovery.feature
- [ ] **4.2.2** Review crash_recovery_steps.py
- [ ] **4.2.3** Implement disk space warning verification
- [ ] **4.2.4** Implement network failure recovery steps
- [ ] **4.2.5** Verify recovery tests pass

### Phase 5: Team Collaboration

#### Step 5.1: Fix Team Workflow Tests
- [ ] **5.1.1** Analyze team-collaboration-and-maintenance.feature
- [ ] **5.1.2** Review team_collaboration_steps.py
- [ ] **5.1.3** Implement shared config sync verification
- [ ] **5.1.4** Add multi-developer conflict resolution steps
- [ ] **5.1.5** Verify team collaboration tests pass

### Phase 6: Health Monitoring

#### Step 6.1: Fix Container Health Checks
- [ ] **6.1.1** Analyze debugging-troubleshooting.feature for health scenarios
- [ ] **6.1.2** Implement deterministic container readiness checks
- [ ] **6.1.3** Add retry logic with backoff for health status
- [ ] **6.1.4** Verify health monitoring tests pass

### Phase 7: Final Verification

#### Step 7.1: Run Full Test Suite
- [ ] **7.1.1** Run `behave tests/features/docker-free/` - all should pass
- [ ] **7.1.2** Run `behave tests/features/docker-required/` - target 95%+ pass rate
- [ ] **7.1.3** Generate behave JSON results
- [ ] **7.1.4** Update PROJECT_STATUS.md with final statistics

---

## Implementation Notes

### Key Technical Decisions

1. **Step Definition Pattern**: Use parameterized steps with `{param}` syntax
2. **Timeout Strategy**: Increase timeouts for Docker operations (120s for create)
3. **State Management**: Use context.vms dict to track created VMs for cleanup
4. **Error Messages**: Include "Solution:" and "Suggestions:" in all error outputs

### Files to Modify

| File | Purpose |
|------|---------|
| `tests/features/steps/*.py` | Add/modify step definitions |
| `scripts/lib/vde-errors.sh` | Enhance error messages |
| `scripts/lib/vm-common.sh` | Fix port allocation logic |
| `scripts/lib/vde-core.sh` | Add health check functions |

### Testing Strategy

1. Each step includes verification before moving to next
2. Run feature file after each sub-step
3. Commit after each P0-P1 phase completion

---

## Success Criteria

- [ ] 95%+ pass rate on docker-free tests
- [ ] 95%+ pass rate on docker-required tests  
- [ ] Zero undefined steps (all scenarios have step definitions)
- [ ] All error messages include actionable suggestions

---

## Next Steps (After Approval)

1. Switch to Code mode
2. Execute Phase 1.1: Start with docker-operations feature
3. Verify each sub-step completes before proceeding
4. Report progress after each phase

---

**Plan Version:** 1.0  
**Approval Required:** Yes - User must approve before Phase 2 begins
