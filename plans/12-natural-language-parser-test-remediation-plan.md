# Natural-Language-Parser Test Remediation Plan

## Overview
Fix pre-existing bugs in `natural-language-parser.feature` test suite.

## Test Failures

| Scenario | Line | Status | Issue |
|----------|------|--------|-------|
| Validate plan lines - Valid lines | 117 | FAILED | Step checks `context.nl_intent` which is never set |
| Handle empty input | 123 | ERRORED | Step crashes - likely context variable issue |
| Reject empty input gracefully | 148 | FAILED | Context variable issue |

## Root Causes

### Issue 1: step_plan_lines_valid checks wrong context variable
**Location**: `tests/features/steps/natural_language_steps.py:340-345`

**Problem**: The step definition checks `context.nl_intent` but plan validation scenarios populate `context.plan` instead.

**Current Code**:
```python
@then("all plan lines should be valid")
def step_plan_lines_valid(context):
    """Verify all plan lines are valid."""
    actual_intent = getattr(context, 'nl_intent', None)
    valid_intents = ['start_vm', 'stop_vm', 'restart_vm', 'create_vm', 'status', 'connect', 'help', 'list_vms', 'list_languages', 'list_services']
    assert actual_intent in valid_intents, f"Invalid intent detected: {actual_intent}"
```

**Fix**: Update to validate each line in `context.plan` using `_validate_plan_line()`.

### Issue 2 & 3: Empty input handling
**Problem**: Empty input scenarios crash or fail due to context variable not being properly set.

## Remediation Steps

### Step 1: Fix step_plan_lines_valid
Modify `tests/features/steps/natural_language_steps.py`:

```python
@then("all plan lines should be valid")
def step_plan_lines_valid(context):
    """Verify all plan lines are valid."""
    plan = getattr(context, 'plan', [])
    for line in plan:
        assert _validate_plan_line(line), f"Invalid plan line: {line}"
```

### Step 2: Verify empty input behavior
1. Run parser with empty input to check behavior
2. Update test expectation or parser as needed

### Step 3: Fix any undefined steps
Identify and implement missing step definitions referenced by failing scenarios.

## Files to Modify
- `tests/features/steps/natural_language_steps.py` - Fix step definitions

## Verification
Run tests after each fix:
```bash
VDE_TEST_MODE=1 behave tests/features/docker-free/natural-language-parser.feature
```

## Expected Outcome
- All 47 scenarios should pass
- 3 currently failing/erroring scenarios will be fixed
