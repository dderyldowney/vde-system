# Docker-Free BDD Undefined Steps Remediation Plan

## Summary
Remediate 14 undefined step definitions in docker-free BDD tests.

## Current Status (2026-02-02)
| Feature | Undefined Steps | Status |
|---------|-----------------|--------|
| Shell Compatibility Layer | 9 | In Progress |
| VM Information and Discovery | 5 | In Progress |
| **Total** | **14** | |

## Undefined Steps Analysis

### Shell Compatibility Layer (9 steps)

| # | Location | Step | Priority |
|---|----------|------|----------|
| 1 | shell-compat.feature:33 | Given associative array with keys "foo", "bar", "baz" | High |
| 2 | shell-compat.feature:39 | Given associative array with key "foo" | High |
| 3 | shell-compat.feature:46 | Given associative array with key "foo" | High |
| 4 | shell-compat.feature:51 | Given associative array with multiple entries | High |
| 5 | shell-compat.feature:97 | When I set key "empty_value" to an empty value | Medium |
| 6 | shell-compat.feature:122 | And I set key "temp1" to value "value1" | Medium |
| 7 | shell-compat.feature:133 | And I set key "config" to value "original" | Medium |
| 8 | shell-compat.feature:141 | And I set key "existing" to value "present" | Medium |
| 9 | shell-compat.feature:151 | Then array should remain empty | Low |

### VM Information and Discovery (5 steps)

| # | Location | Step | Priority |
|---|----------|------|----------|
| 10 | vm-info.feature:19 | Then I should not see service VMs | High |
| 11 | vm-info.feature:25 | Then I should see only service VMs | High |
| 12 | vm-info.feature:38 | Given I want to verify a VM type before using it | Medium |
| 13 | vm-info.feature:44 | Given I know a VM by an alias but not its canonical name | Medium |
| 14 | vm-info.feature:50 | Given I am new to VDE | Low |

## Remediation Plan

### Phase 1: Shell Compatibility Steps (shell_compat_steps.py)

Add the following step definitions:

```python
@given('associative array with keys "{keys}"')
def step_associative_array_with_keys(context, keys):
    key_list = [k.strip().strip('"') for k in keys.split(',')]
    # Implementation to create associative array with specified keys

@given('associative array with key "{key}"')
def step_associative_array_with_key(context, key):
    # Implementation to create associative array with single key

@given('associative array with multiple entries')
def step_associative_array_multiple_entries(context):
    # Implementation to create array with multiple entries

@when('I set key "{key}" to an empty value')
def step_set_empty_value(context, key):
    # Implementation to set empty string value

@when('I set key "{key}" to value "{value}"')
def step_set_key_value(context, key, value):
    # Implementation to set key-value pair (reused across multiple steps)

@then('array should remain empty')
def step_array_empty(context):
    # Implementation to verify array is empty
```

### Phase 2: VM Information Steps (vm_info_steps.py)

Add the following step definitions:

```python
@then('I should not see service VMs')
def step_no_service_vms(context):
    # Verify only language VMs are listed

@then('I should see only service VMs')
def step_only_service_vms(context):
    # Verify only service VMs are listed

@given('I want to verify a VM type before using it')
def step_verify_vm_type(context):
    # Precondition for verification scenario

@given('I know a VM by an alias but not its canonical name')
def step_alias_knowledge(context):
    # Precondition for alias discovery scenario

@given('I am new to VDE')
def step_new_user(context):
    # Precondition for new user scenario
```

## Files to Modify

| File | Changes |
|------|---------|
| `tests/features/steps/shell_compat_steps.py` | Add 6 step definitions |
| `tests/features/steps/vm_info_steps.py` | Add 5 step definitions (new file if needed) |

## Execution

```bash
# Run docker-free BDD tests to verify
./tests/run-docker-free-tests.zsh

# Verify undefined steps reduced to 0
behave tests/features/docker-free/ --format json -o tests/behave-results-docker-free.json
```

## Expected Outcome

After remediation:
- **Passed**: 379+ (all current passing + newly defined)
- **Failed**: 46 (existing failures, not related to undefined steps)
- **Undefined**: 0
- **Error**: 33 (scenario-level errors from undefined steps)
