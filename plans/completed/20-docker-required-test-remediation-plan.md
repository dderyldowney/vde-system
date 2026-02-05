# Docker-Required Test Remediation Plan

**Date:** 2026-02-04
**Project:** VDE (Virtual Development Environment)
**Scope:** All docker-required BDD features with non-passing or missing scenarios/steps
**Status**: SUPERSEDED - Key deliverables implemented
**Superseded By**: New plan for remaining 899 undefined steps
**Completed**: 2026-02-05

---

## ⚠️ SUPERSEDED

This plan has been **superseded** as of 2026-02-05.

### Key Accomplishments (COMPLETED):
- **VM Naming Convention**: Language VMs use `{name}-dev` format (service VMs no suffix)
- **Helper File**: `tests/features/steps/vm_naming_helpers.py` ✓
- **Docker Operations**: 14/14 scenarios passing ✓
- **Test Harness**: `step_given_vm_exists()` auto-creates VMs ✓
- **Environment Files**: `python.env`, `postgres.env` created ✓
- **Cleanup Hook**: `after_feature()` implemented ✓

### Remaining Work (Deferred):
- **899 undefined steps** across docker-required features (infrastructure-dependent)
- See `plans/completed/28-docker-required-test-remediation-tracking.md` for tracking

---

## Executive Summary

The full test suite analysis reveals significant gaps in docker-required test coverage:

| Metric | Count |
|--------|-------|
| Total Scenarios | ~146 |
| Passed | 277 |
| Failed | 23 |
| Undefined | 112+ |
| Error | 133+ |
| **Undefined Steps** | **946+** |

## Critical Infrastructure Dependencies (Priority 0)

These foundational step definitions block other tests from executing. Fixing these first will enable the most test coverage gain.

### 1. VM Naming Convention Issues (~100+ undefined/failing steps)
**Blocking:** All VM lifecycle and verification tests

**Root Cause:** VM names in test steps use incomplete format:
- `VM "python"` instead of `VM "python-dev"`
- `VM "rust"` instead of `VM "rust-dev"`
- `VM "go"` instead of `VM "go-dev"`

**Impact:** Container verification fails because containers are named `{name}-dev` but tests look for `{name}`

**Fix Required:**
- Update all `vm_lifecycle_steps.py` to use full `{name}-dev` format
- Update `docker_helpers.py` to append `-dev` for language VMs
- Update `vm_common` library to generate correct container names

### 2. VM Lifecycle Operations (~60 undefined steps)
**Blocking:** Template System, Collaboration Workflow, Daily Workflow, Multi-Project Workflow

**Root Cause:** Steps like `I create VM "python" with SSH port "2200"` and `VM "python" should be running" have no implementations.

**Impact:** 200+ scenarios depend on these operations.

### 3. Docker Verification Helpers (~40 undefined steps)
**Blocking:** All docker-required tests that verify container state

**Root Cause:** Steps like `container should be running` and `container should be stopped` have no implementations.

**Impact:** 500+ scenarios need container verification.

### 4. Template System (~70 undefined steps)
**Blocking:** Configuration Management, VM Lifecycle Management

**Root Cause:** Steps like `rendered output should contain "user: devuser"` have partial implementations.

**Impact:** 150+ scenarios need template verification.

### 5. SSH Key Management (~50 undefined steps)
**Blocking:** All SSH-related tests

**Root Cause:** Steps like `available SSH keys should be loaded into agent` have incomplete implementations.

**Impact:** 100+ scenarios depend on SSH functionality.

### 5. Port Management (~30 undefined steps)
**Blocking:** VM Creation, Network Configuration

**Root Cause:** Steps like `port should be available for allocation` have no implementations.

**Impact:** 80+ scenarios need port operations.

---

## Current Test Status by Feature

### ✅ Pass Features (Working)
1. **Cache System** - All scenarios passing
2. **SSH Agent Automatic Setup** - All scenarios passing
3. **SSH Configuration** - All scenarios passing
4. **SSH Agent Forwarding VM-to-VM** - All scenarios passing
5. **SSH Agent External Git Operations** - All scenarios passing
6. **SSH Agent VM-to-Host Communication** - All scenarios passing
7. **SSH and Remote Access** - All scenarios passing
8. **VM Information and Discovery** - Partial implementation

### ⚠️ Failed Features (Need Fixes)
1. **Collaboration Workflow** - Multiple scenarios failing
2. **Daily Development Workflow** - Multiple undefined steps
3. **Configuration Management** - Multiple undefined/error scenarios
4. **Daily Workflow** - Multiple undefined/error scenarios
5. **Docker and Container Management** - Multiple undefined steps
6. **Docker Operations** - Multiple undefined/error scenarios
7. **Error Handling and Recovery** - Multiple undefined steps
8. **Installation Setup** - Partial implementation
9. **Multi-Project Workflow** - Multiple undefined steps
10. **Natural Language Commands** - Multiple undefined steps
11. **Port Management** - Multiple undefined steps
12. **Productivity Features** - Multiple undefined steps
13. **SSH Agent External Git Operations** - Partial
14. **SSH Agent Forwarding VM-to-VM** - Partial
15. **SSH Configuration** - Partial
16. **SSH VM to Host Communication** - Multiple undefined/error scenarios
17. **Team Collaboration and Maintenance** - Multiple undefined steps
18. **Template System** - Multiple undefined steps
19. **VM Lifecycle** - Multiple undefined/error scenarios
20. **VM Lifecycle Management** - Multiple undefined steps
21. **VM State Awareness** - Multiple undefined steps

---

## Critical Issues Identified

### 1. Template System (~70 undefined steps)
**Feature:** `tests/features/docker-required/template-system.feature`

Missing step definitions for:
- Render language VM template
- Render service VM template
- Handle multiple service ports
- Escape special characters in template values
- Template includes SSH agent forwarding
- Template includes public keys volume
- Template uses correct network
- Template sets correct restart policy
- Template configures user correctly
- Template exposes SSH port
- Template includes install command
- Handle missing template gracefully

### 2. VM Information and Discovery (~40 undefined steps)
**Feature:** `tests/features/docker-free/vm-information-and-discovery.feature`

Missing step definitions for:
- Listing all available VMs
- Listing only language VMs
- Listing only service VMs
- Getting detailed information about a specific VM
- Checking if a VM exists
- Discovering VMs by alias
- Understanding VM categories

### 3. VM Lifecycle Management (~60 undefined steps)
**Feature:** `tests/features/docker-required/vm-lifecycle-management.feature`

Missing step definitions for:
- Creating a new VM
- Creating multiple VMs at once
- Starting a created VM
- Starting multiple VMs
- Checking VM status
- Stopping a running VM
- Stopping multiple VMs
- Restarting a VM
- Restarting with rebuild
- Deleting a VM
- Rebuilding after code changes
- Upgrading a VM
- Migrating to a new VDE version

### 4. VM State Awareness (~50 undefined steps)
**Feature:** `tests/features/docker-required/vm-state-awareness.feature`

Missing step definitions for:
- Starting an already running VM
- Stopping an already stopped VM
- Creating an existing VM
- Restarting a stopped VM
- Status shows mixed states
- Smart start of already running VMs
- Smart start with mixed states
- Querying specific VM status
- Preventing duplicate operations
- State persistence information
- Waiting for VM to be ready
- Notifying about background operations
- State change notifications
- Batch operation state awareness

### 5. Collaboration Workflow (~200 undefined steps)
**Feature:** `tests/features/docker-required/collaboration-workflow.feature`

Missing step definitions for:
- Team collaboration scenarios
- Project sharing
- Environment reproducibility
- Multi-developer workflows

### 6. Configuration Management (~80 undefined steps)
**Feature:** `tests/features/docker-required/configuration-management.feature`

Missing step definitions for:
- Environment variable configuration
- Local overrides
- Configuration validation
- Migration handling

### 7. Productivity Features (~100 undefined steps)
**Feature:** `tests/features/docker-required/productivity-features.feature`

Missing step definitions for:
- Developer productivity features
- Quick commands
- Workflow automation

### 8. Docker and Container Management (~80 undefined steps)
**Feature:** `tests/features/docker-required/docker-and-container-management.feature`

Missing step definitions for:
- Container lifecycle verification
- Network configuration
- Volume management
- Health check verification

### 9. Error Handling and Recovery (~60 undefined steps)
**Feature:** `tests/features/docker-required/error-handling-and-recovery.feature`

Missing step definitions for:
- Error detection and reporting
- Recovery mechanisms
- Graceful degradation

---

## Remediation Priorities

### Phase 1: Critical Infrastructure - VM NAMING FIRST (Week 1)

| Priority | Feature | Steps | Blocking | Effort |
|----------|---------|-------|----------|--------|
| **P0** | **VM Naming Convention Fix** | ~100 | **All tests** | **High** |
| P0 | Docker Verification Helpers | ~40 | All docker tests | High |
| P0 | VM Lifecycle Operations | ~60 | 200+ scenarios | High |
| P0 | Port Management | ~30 | 80+ scenarios | Medium |
| P0 | Template System | ~70 | 150+ scenarios | High |
| P0 | SSH Key Management | ~50 | 100+ scenarios | Medium |

**CRITICAL: VM Naming Convention Fix Required First**
```
# Tests use: "python" | # Containers are named: "python-dev"
Tests use: "rust"      Containers are named: "rust-dev"
Tests use: "go"         Containers are named: "go-dev"

Fix: Create helper _get_container_name() to append "-dev" for language VMs
```

### Phase 2: User Experience (Week 2)

| Priority | Feature | Steps | Effort |
|----------|---------|-------|--------|
| P1 | Daily Workflow | ~100 | Medium |
| P1 | Collaboration Workflow | ~200 | High |
| P1 | Configuration Management | ~80 | Medium |

### Phase 3: Advanced Features (Week 3)

| Priority | Feature | Steps | Effort |
|----------|---------|-------|--------|
| P2 | Error Handling and Recovery | ~60 | Medium |
| P2 | Debugging and Troubleshooting | ~50 | Medium |
| P2 | Team Collaboration | ~40 | Low |

---

## Implementation Strategy

### Priority 0: Critical Infrastructure (Week 1)

These foundational steps enable the most test coverage. Complete in this order:

#### 1. Fix VM Naming Convention
**File:** `tests/features/steps/vm_lifecycle_steps.py` (fix first!)

**Problem:** Tests use `VM "python"` but containers are named `python-dev`

**Fix:** Create helper function to normalize VM names:

```python
def _get_container_name(vm_name):
    """Convert VM name to container name (append -dev for language VMs)."""
    # Service VMs: postgres, redis, nginx → no suffix
    # Language VMs: python, rust, go → python-dev, rust-dev, go-dev
    service_vms = {'postgres', 'redis', 'mongodb', 'mysql', 'nginx', 'rabbitmq', 'couchdb'}
    if vm_name in service_vms:
        return vm_name
    return f"{vm_name}-dev"

def verify_vm_running(context, vm_name):
    """Verify VM is running using normalized container name."""
    container_name = _get_container_name(vm_name)
    return verify_container_running(container_name)
```

#### 2. Docker Verification Helpers
**File:** `tests/features/steps/docker_helpers.py` (extend)

```python
# Missing functions to add:
def verify_container_running(container_name):
    """Verify container is running using docker ps."""
    result = subprocess.run(
        ['docker', 'ps', '--format', '{{.Names}}'],
        capture_output=True, text=True
    )
    return container_name in result.stdout

def verify_container_stopped(container_name):
    """Verify container is stopped."""
    result = subprocess.run(
        ['docker', 'ps', '-a', '--format', '{{.Names}}'],
        capture_output=True, text=True
    )
    return container_name not in result.stdout
```

#### 3. VM Lifecycle Steps
**File:** `tests/features/steps/vm_lifecycle_steps.py` (extend)

Missing high-priority steps:
- `Given VM "{vm}" is running` → use verify_vm_running helper
- `When I create VM "{vm}" with SSH port "{port}"` → call create-virtual-for
- `Then VM "{vm}" should be running` → use verify_vm_running helper

#### 4. Port Management Steps
**File:** `tests/features/steps/port_management_steps.py` (extend)

Missing high-priority steps:
- `Given port {port} is available` → check port not in use
- `Then port {port} should be available for allocation` → verify registry

#### 5. Template Verification
**File:** `tests/features/steps/template_steps.py` (complete)

Missing high-priority steps:
- `Then rendered output should contain "user: devuser"` → verify output
- `Then rendered template should be valid YAML` → parse YAML

### Priority 1: User Experience Features (Week 2)

Once infrastructure is stable, implement user-facing scenarios:
- Daily Workflow scenarios
- Collaboration Workflow scenarios
- Productivity Features scenarios

### Priority 2: Advanced Features (Week 3)

Complete remaining edge cases:
- Error Handling scenarios
- Debugging scenarios
- Team Collaboration scenarios

---

## Files to Modify

### Step Definition Files to Complete
1. `tests/features/steps/template_steps.py`
2. `tests/features/steps/vm_lifecycle_steps.py`
3. `tests/features/steps/vm_state_steps.py` (new)
4. `tests/features/steps/config_steps.py`
5. `tests/features/steps/docker_steps.py`
6. `tests/features/steps/error_handling_steps.py`

### New Files to Create
1. `tests/features/steps/productivity_steps.py`
2. `tests/features/steps/collaboration_steps.py`
3. `tests/features/steps/multi_project_steps.py`

### Helper Files to Extend
1. `tests/features/steps/docker_helpers.py`
2. `tests/features/steps/shell_helpers.py`
3. `tests/features/steps/test_utilities.py`

---

## Testing Approach

### Unit Tests for Step Definitions
Each new step definition should have:
- Basic functionality test
- Error handling test
- Edge case test

### Integration Tests
- Run full docker-required test suite
- Verify all scenarios execute without undefined steps
- Confirm expected behavior matches actual

### Regression Testing
- Run all docker-free tests to ensure no regressions
- Verify SSH tests still pass
- Confirm cache system tests remain green

---

## Success Criteria

### Phase 1: Infrastructure Foundation (Week 1) ✅ COMPLETE WHEN:
- [ ] VM naming convention fixed (all language VMs use `{name}-dev` format)
- [ ] Docker verification helpers implemented (verify_container_running, verify_container_stopped)
- [ ] VM lifecycle steps implemented (create, start, stop, restart)
- [ ] Port management steps implemented (allocate, verify)
- [ ] Template verification steps completed
- [ ] 500+ scenarios can execute (previously blocked by undefined steps)

**Critical VM Naming Fix:**
```python
# Service VMs (no suffix): postgres, redis, nginx, mongodb, mysql, rabbitmq, couchdb
# Language VMs (append -dev): python → python-dev, rust → rust-dev, go → go-dev
```

### Phase 2: User Experience (Week 2) ✅ COMPLETE WHEN:
- [ ] Daily Workflow scenarios have <5% undefined steps
- [ ] Collaboration Workflow scenarios have <5% undefined steps
- [ ] Configuration Management scenarios have <5% undefined steps
- [ ] 200+ additional scenarios can execute

### Phase 3: Advanced Features (Week 3) ✅ COMPLETE WHEN:
- [ ] Error Handling scenarios have <5% undefined steps
- [ ] Debugging scenarios have <5% undefined steps
- [ ] All features have <5% undefined steps

### Full Remediation Complete
- [ ] Zero undefined steps across all docker-required features
- [ ] Zero failing scenarios (except expected failures)
- [ ] All user guide scenarios pass

---

## Estimated Effort

| Phase | Effort | Timeline |
|-------|--------|----------|
| Phase 1 | 40 hours | Week 1 |
| Phase 2 | 60 hours | Week 2 |
| Phase 3 | 40 hours | Week 3 |
| **Total** | **~140 hours** | **3 weeks** |

---

## Dependencies

### External Dependencies
- Docker daemon running
- SSH access configured
- All VDE scripts functional

### Internal Dependencies
- `vde-core` library functions
- `vm-common` library functions
- `vde-commands` wrapper functions
- `vde-parser` natural language parser

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Tests require Docker | Skip non-Docker tests during development |
| Long execution time | Use parallel test execution |
| Complex state management | Add cleanup utilities |
| Environment-specific failures | Add environment detection |

---

## References

- **Existing Documentation:** `TESTING_TODO.md`
- **Completed Work:** `plans/completed/docker-required-test-remediation-tracking.md`
- **Phase 1 Detail:** [`plans/phase1-critical-infrastructure-implementation-plan.md`](plans/phase1-critical-infrastructure-implementation-plan.md)
- **Test Framework:** `run-tests.zsh`
- **Step Definitions:** `tests/features/steps/`

---

## Phase 1 Progress (2026-02-04)

### Completed Tasks
- ✅ VM Naming Convention Helpers (`vm_naming_helpers.py`)
- ✅ Docker Verification Helpers - `verify_container_stopped()` added
- ✅ Template Steps - YAML validation, restart policy, port exposure added
- ✅ Port Management Steps - New file created
- ✅ SSH Key Management Steps - New file created

### Files Modified/Created
| File | Action | Status |
|------|--------|--------|
| `tests/features/steps/vm_naming_helpers.py` | Created | ✅ |
| `tests/features/steps/docker_helpers.py` | Modified | ✅ |
| `tests/features/steps/template_steps.py` | Modified | ✅ |
| `tests/features/steps/port_management_steps.py` | Created | ✅ |
| `tests/features/steps/ssh_steps.py` | Created | ✅ |
| `tests/features/steps/vm_lifecycle_steps.py` | Removed | ⚠️ Conflicts |

---

## Final Status

### Completed (from Plan 20 scope):
- VM Naming Convention Helpers ✓
- Docker Verification Helpers ✓
- Template Steps ✓
- Port Management Steps ✓
- SSH Key Management Steps ✓
- Docker Operations Tests: 14/14 passing ✓

### Deferred to New Plan:
- Remaining 899 undefined steps across all docker-required features
- Full implementation of VM Lifecycle Management
- Full implementation of VM State Awareness
- Full implementation of Error Handling

---

## Next Steps

1. **Immediate:** Create new plan for remaining 899 undefined steps
2. **Short-term:** Target high-frequency undefined steps (>3 scenarios)
3. **Medium-term:** Complete all docker-required feature implementations
4. **Long-term:** Zero undefined steps across docker-required features

---

*Plan generated: 2026-02-04*
*Last updated: 2026-02-05*
*Moved to plans/completed: 2026-02-05*
