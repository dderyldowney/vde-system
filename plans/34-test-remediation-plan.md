# Plan 34: Test Suite Full Remediation

**Parent Plan**: [Plan 33: Test Suite Remediation](33-comprehensive-test-remediation-plan.md)  
**Created**: 2026-02-07  
**Scope**: Remediate remaining failing scenarios in Plans 33d, 33e, 33f

---

## Executive Summary

After verifying Plans 33a-33f, several issues remain that require remediation:

| Plan | Feature | Passing | Failing | Status |
|------|---------|---------|---------|--------|
| 33d | Natural Language Commands | 10/14 | 4 | Partially Complete |
| 33e | SSH and Remote Access | 2/12 | 10 | Needs Implementation |
| 33f | Multi-Project Workflow | 3/9 | 6 | Needs VM Setup |

---

## Phase 1: Plan 33d Remediation (Natural Language Commands)

### Issue: 4 scenarios failing

**Root Cause**: Complex natural language parsing edge cases not implemented

### Tasks

#### Task 1.1: Fix Alias Resolution
**File**: `tests/features/steps/natural_language_steps.py`  
**Scenario**: "Using aliases instead of canonical names"  
**Issue**: VM alias (nodejs → JavaScript) not resolving

```python
# Current: @then(u'the system should understand I want to create the JavaScript VM')
# Missing: Alias resolution logic in vde-parser
```

**Action**: Verify alias mapping exists in `scripts/data/vm-types.conf`  
**Expected**: `nodejs` should map to `js`

#### Task 1.2: Implement Wildcard Operations
**Scenario**: "Wildcard operations"  
**Issue**: No step definition for wildcard VM selection

**Action**: Add step definition to handle `*` or `all` VM patterns

#### Task 1.3: Implement Troubleshooting Language
**Scenario**: "Troubleshooting language"  
**Issue**: Error handling steps not implemented

**Action**: Add step definitions for error detection and resolution hints

#### Task 1.4: Implement Minimal Typing Commands
**Scenario**: "Minimal typing commands"  
**Issue**: Short-form commands not recognized

**Action**: Add support for abbreviated commands (e.g., `st python` → `start python`)

---

## Phase 2: Plan 33e Remediation (SSH and Remote Access)

### Issue: 10 scenarios errored/failing

**Root Cause**: SSH test infrastructure not properly configured

### Tasks

#### Task 2.1: Configure SSH Environment
**File**: `tests/features/steps/ssh_connection_steps.py`  
**Requirement**: SSH keys must exist for test user

```bash
# Pre-requisite: Generate SSH keys for test environment
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -N "" -C "test@vde"
```

#### Task 2.2: Implement SSH Connection Steps
**Missing Steps**:
- `@when(u'I connect with SSH client')`
- `@when(u'I use VSCode Remote-SSH')`
- `@then(u'multiple SSH connections should work')`

**Action**: Add implementations using subprocess to call `ssh` with proper config

#### Task 2.3: Implement Workspace Access Steps
**Missing Steps**:
- `@then(u'workspace directory should be accessible')`
- `@then(u'I can access project files')`

**Action**: Add step definitions to verify `/workspace` mount in containers

#### Task 2.4: Implement Sudo Access Steps
**Missing Steps**:
- `@then(u'sudo access should work in container')`

**Action**: Add step to verify passwordless sudo is configured

#### Task 2.5: Implement Shell/Editor Config Steps
**Missing Steps**:
- `@then(u'zsh should be configured')`
- `@then(u'neovim should be available')`

**Action**: Add step definitions to verify shell tools exist

---

## Phase 3: Plan 33f Remediation (Multi-Project Workflow)

### Issue: 6 scenarios failing

**Root Cause**: VMs not pre-created before scenario execution

### Tasks

#### Task 3.1: Add VM Requirements to environment.py
**File**: `tests/features/environment.py`

```python
_SCENARIO_REQUIREMENTS = {
    "tests/features/docker-required/multi-project-workflow.feature": {
        "Setting up a web development project": ["js", "nginx"],
        "Switching from web to backend project": ["js", "python", "go"],
        "New Project Setup - Start Development Stack": ["python", "postgres", "redis"],
        "Starting all microservices at once": ["go", "rust", "nginx"],
        "Data science project setup": ["python", "r", "redis"],
        "Mobile development with backend": ["flutter", "go"],
    }
}
```

#### Task 3.2: Verify VM Pre-Creation Hook
**File**: `tests/features/environment.py`  
**Method**: `_setup_scenario_environment()`

**Action**: Ensure hook creates required VMs before each scenario

#### Task 3.3: Fix Path Verification
**File**: `tests/features/steps/multi_project_workflow_steps.py`  
**Issue**: Paths reference wrong directories

```python
# Current: Path(VDE_ROOT) / vm_name
# Should be: Path(VDE_ROOT) / 'configs' / 'docker' / vm_name
```

---

## Phase 4: Cross-Cutting Issues

### Issue 4.1: VDE Script Path Consistency
**Status**: Fixed in Plan 33d  
**File**: `tests/features/steps/natural_language_steps.py`  
**Pattern**: All step files should use `VDE_ROOT / "scripts" / "vde"`

### Issue 4.2: Environment File Consistency
**Status**: Restored from git  
**Files**: `env-files/*.env`  
**Required For**: postgres, redis, rabbitmq, nginx

### Issue 4.3: SSH Agent Forwarding Tests
**Pattern**: Tests requiring SSH agent should check agent status first

```python
def ssh_agent_running():
    """Check if SSH agent is running."""
    result = subprocess.run(
        ["ssh-add", "-l"],
        capture_output=True,
        text=True
    )
    return result.returncode == 0 or "no identities" in result.stderr
```

---

## Implementation Order

### Week 1: Infrastructure Fixes
1. Day 1: Task 3.1-3.3 (Multi-Project VM setup)
2. Day 2: Task 2.1-2.2 (SSH environment)

### Week 2: Step Implementation
3. Day 3-4: Task 2.3-2.5 (SSH connection steps)
4. Day 5: Task 1.1-1.2 (NL alias/wildcard)

### Week 3: Edge Cases
5. Day 6: Task 1.3-1.4 (NL troubleshooting/minimal)
6. Day 7: Integration testing

---

## Estimated Effort

| Phase | Tasks | Days |
|-------|-------|------|
| Phase 1 (33d) | 4 | 2 |
| Phase 2 (33e) | 5 | 3 |
| Phase 3 (33f) | 3 | 1 |
| Phase 4 (Cross-cutting) | 3 | 1 |
| **Total** | **15** | **7** |

---

## Success Criteria

- [ ] Plan 33d: 14/14 scenarios passing
- [ ] Plan 33e: 12/12 scenarios passing
- [ ] Plan 33f: 9/9 scenarios passing
- [ ] All step definitions have real implementations (no fake tests)
- [ ] VM pre-creation works for all required scenarios

---

## Risks and Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| SSH key generation fails | High | Document pre-reqs clearly |
| VM creation timeout | Medium | Increase timeout, use cached images |
| Alias resolution complex | Low | Use existing parser, add tests |

---

## References

- [Plan 33: Test Suite Remediation](33-comprehensive-test-remediation-plan.md)
- [Plan 33 Sub-Plans Summary](33-sub-plans-summary.md)
- [Test Environment Configuration](tests/features/environment.py)
- [SSH Steps Implementation](tests/features/steps/ssh_connection_steps.py)
