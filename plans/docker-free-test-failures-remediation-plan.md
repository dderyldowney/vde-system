# Docker-Free BDD Test Failures Remediation Plan

## Summary
Diagnose and fix remaining test failures in docker-free BDD tests after undefined steps remediation.

## Current Status (2026-02-02)

### Failing Scenarios (4 total)

| # | Feature | Scenario | Root Cause | Severity |
|---|---------|----------|------------|----------|
| 1 | shell-compatibility.feature:32 | Iterate over associative array keys | `context.expected_keys` never set in test | Medium |
| 2 | vm-information-and-discovery.feature:15 | Listing only language VMs | VM filtering logic incomplete | Medium |
| 3 | vm-information-and-discovery.feature:22 | Listing only service VMs | VM filtering logic incomplete | Medium |
| 4 | vm-information-and-discovery.feature:37 | Checking if a VM exists | Alias resolution returns wrong value | Medium |

### Errored Scenarios (2 total)

| # | Feature | Scenario | Root Cause | Severity |
|---|---------|----------|------------|----------|
| 5 | vm-information-and-discovery.feature:7 | Listing all available VMs | `step_vde_installed` raises exception | High |
| 6 | vm-information-and-discovery.feature:29 | Getting detailed information about a specific VM | `step_request_vm_info` raises exception | High |

## Root Cause Analysis

### 1. Iterate over associative array keys (shell-compat.feature:32)

**Error:** `ASSERT FAILED: Expected keys [], got ['foo', 'baz', 'bar']`

**Cause:** The step `step_all_keys_returned` checks `context.expected_keys` which is never set in the scenario. The scenario should either:
- Set `context.expected_keys = ['foo', 'bar', 'baz']` before the Then step, OR
- The step should check that keys are returned (not specific order)

**Fix:** Update `step_all_keys_returned` to accept expected keys as parameter or check for key existence.

### 2-4. VM Listing Scenarios (vm-info.feature:15, 22, 37)

**Error:** Scenarios fail because VM list output doesn't match expected format

**Cause:** Steps read from `vm-types.conf` but the filtering logic assumes specific output format. The actual vm-types.conf format may differ from expected.

**Fix:** 
- Update `step_should_not_see_service_vms` to properly parse vm-types.conf
- Update `step_should_see_only_service_vms` to properly parse vm-types.conf
- Update `step_check_vm_exists` to properly resolve aliases

### 5-6. Errored Scenarios (vm-info.feature:7, 29)

**Error:** `step_vde_installed` and `step_request_vm_info` raise exceptions

**Cause:** These steps require actual VDE installation and call subprocess commands that fail when VDE is not installed.

**Fix:** 
- Mock the subprocess calls for testing without VDE
- Or mark these scenarios as requiring VDE installation

## Remediation Plan

### Phase 1: Fix Shell Compatibility Test

**File:** `tests/features/steps/shell_compat_steps.py`

```python
@then('all keys should be returned')
def step_all_keys_returned(context):
    """All keys should be returned - verify keys are present regardless of order."""
    actual_keys = getattr(context, 'all_keys', [])
    # Verify we got the expected number of keys (3 for the test scenario)
    expected_count = 3  # foo, bar, baz
    assert len(actual_keys) == expected_count, \
        f"Expected {expected_count} keys, got {len(actual_keys)}: {actual_keys}"
    # Verify all expected keys are present
    expected = {'foo', 'bar', 'baz'}
    actual = set(actual_keys)
    assert actual == expected, f"Expected keys {expected}, got {actual}"
```

### Phase 2: Fix VM Listing Tests

**File:** `tests/features/steps/vm_info_steps.py`

Update steps to properly parse vm-types.conf format. Need to check actual format:

```bash
cat scripts/data/vm-types.conf | head -20
```

### Phase 3: Handle Errored Scenarios

Option A: Mock subprocess calls for unit testing
Option B: Skip tests that require VDE installation

## Files to Modify

| File | Changes |
|------|---------|
| `tests/features/steps/shell_compat_steps.py` | Fix `step_all_keys_returned` |
| `tests/features/steps/vm_info_steps.py` | Fix VM listing and alias resolution |
| `tests/features/steps/vm_status_steps.py` | Handle missing VDE gracefully |

## Execution

```bash
# Run failing scenarios to verify
behave tests/features/docker-free/shell-compatibility.feature:32
behave tests/features/docker-free/vm-information-and-discovery.feature:15
behave tests/features/docker-free/vm-information-and-discovery.feature:22
behave tests/features/docker-free/vm-information-and-discovery.feature:37

# Run errored scenarios
behave tests/features/docker-free/vm-information-and-discovery.feature:7
behave tests/features/docker-free/vm-information-and-discovery.feature:29
```

## Expected Outcome

After remediation:
- **Passed**: 26+ (all current passing + newly fixed)
- **Failed**: 0
- **Errored**: 0 (or marked as VDE-required)
- **Undefined**: 0
