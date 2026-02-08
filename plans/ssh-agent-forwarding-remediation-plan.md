# SSH Agent Forwarding VM-to-VM Feature Remediation Plan

## Problem Analysis

The `ssh-agent-forwarding-vm-to-vm.feature` has 14 erroring scenarios due to **step definition mismatch**. The feature file uses steps without the "for VM-to-VM" suffix, but the step definitions in `ssh_vm_to_vm_steps.py` include this suffix.

### Root Cause
| Feature File Step | Existing Step Definition | Match? |
|-----------------|-------------------------|--------|
| `Given I have SSH keys configured on my host` | `@given('I have SSH keys configured on my host for VM-to-VM')` | ❌ Suffix mismatch |
| `And the SSH agent is running` | `@given('the SSH agent is running for VM-to-VM')` | ❌ Suffix mismatch |
| `And my keys are loaded in the agent` | `@given('my keys are loaded in the agent for VM-to-VM')` | ❌ Suffix mismatch |

## Implementation Steps

### Step 1: Create Alias Step Definitions (No Code Changes Required)
Add step definition aliases without the "for VM-to-VM" suffix that delegate to existing implementations.

**File**: `tests/features/steps/ssh_vm_to_vm_steps.py`

**Changes Needed**:
```python
# Alias for existing step - no functionality change needed
@given('I have SSH keys configured on my host')
def step_ssh_keys_configured_alias(context):
    """Alias for VM-to-VM SSH keys check."""
    step_have_ssh_keys_configured(context)

@given('the SSH agent is running')
def step_ssh_agent_running_alias(context):
    """Alias for SSH agent check."""
    step_ssh_agent_running(context)

@given('my keys are loaded in the agent')
def step_keys_loaded_alias(context):
    """Alias for keys loaded check."""
    step_keys_loaded_in_agent(context)
```

### Step 2: Add Missing WHEN/THEN Step Aliases

**Aliases for WHEN steps**:
```python
@when('I SSH into the {vm_type} VM')
def step_ssh_into_vm_alias(context, vm_type):
    step_ssh_into_vm(context, vm_type)

@when('I run "ssh {target_vm}" from within the {source_vm} VM')
def step_run_ssh_from_vm_alias(context, target_vm, source_vm):
    step_run_ssh_from_vm(context, target_vm, source_vm)

@when('I create a {vm_type} VM')
def step_create_vm_alias(context, vm_type):
    """Create a VM for testing."""
    run_vde_command(['create', vm_type])
```

### Step 3: Add Aliases for THEN Verification Steps

**Aliases for THEN steps**:
```python
@then('I should connect to the {vm_type} VM')
def step_connect_vm_alias(context, vm_type):
    step_connect_to_vm(context, vm_type)

@then('authentication should use my host\'s SSH keys')
def step_auth_host_keys_alias(context):
    step_auth_uses_host_keys(context)
```

### Step 4: Add Missing VM Lifecycle Steps

**Steps for VM creation/management**:
```python
@given('I create a {vm_type} VM for my {purpose}')
def step_create_vm_for_purpose(context, vm_type, purpose):
    """Create a VM with specific purpose."""
    run_vde_command(['create', vm_type])

@given('I have {vm_type} VM running as a {role}')
def step_have_vm_as_role(context, vm_type, role):
    """Ensure VM is running with specific role."""
    step_have_vm_running(context, vm_type)
```

## Files Modified

| File | Change Type | Lines |
|------|------------|-------|
| `tests/features/steps/ssh_vm_to_vm_steps.py` | Add alias step definitions | +50-80 lines |

## Estimated Effort

- **Step 1-3**: 2-3 hours (straightforward alias additions)
- **Step 4**: 1-2 hours (verify VM lifecycle integration)
- **Testing**: 1 hour (run feature to verify all steps match)

**Total Estimated**: 4-6 hours

## Verification Command

```bash
behave --dry-run tests/features/docker-required/ssh-agent-forwarding-vm-to-vm.feature
```

Expected result: All steps should show file references (no "None")

## Risk Assessment

**Low Risk**: Adding aliases doesn't change existing functionality. Only risk is step definition conflicts if feature file is updated to use both forms.

## Alternative Approach

Instead of adding aliases, could modify the feature file to use the existing step names with "for VM-to-VM" suffix. This would require:
- Updating 10+ scenario definitions in the feature file
- Less code change but more documentation change

**Recommendation**: Use alias approach to maintain feature file readability.
