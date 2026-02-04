# Daily Workflow Test Implementation Plan

## Objective
Convert highest-value fake tests to real implementations with subprocess calls to actual VDE commands.

## Phase 1: Core Plan Verification (4-5 hours)

### Priority 1: Intent Detection (3 tests, 1.5 hours)
**Function**: `step_plan_includes_create_intent`, `step_plan_includes_start_intent`, etc.
**Current**: Checks `context.last_intent == 'create_vm'`
**Target**: Call real VDE parser to detect intent

```python
@then('the plan should include the {intent} intent')
def step_plan_includes_intent(context, intent):
    """Verify plan includes the expected intent."""
    # Get input from context (set by WHEN step)
    input_text = getattr(context, 'input_text', '')

    # Call real parser
    result = subprocess.run(
        ['zsh', '-c', f'source {VDE_ROOT}/scripts/lib/vde-parser && detect_intent "{input_text}"'],
        capture_output=True,
        text=True,
        timeout=5
    )

    detected_intent = result.stdout.strip()
    assert detected_intent == intent, f"Expected intent '{intent}', got '{detected_intent}'"
```

### Priority 2: VM Name Extraction (5 tests, 2 hours)
**Functions**: `step_plan_includes_python`, `step_plan_includes_both_pythons`, etc.
**Current**: Checks `'python' in context.plan.get('vms', [])`
**Target**: Call real parser to extract VM names

```python
@then('the plan should include the {vm_name} VM')
def step_plan_includes_vm(context, vm_name):
    """Verify plan includes the expected VM."""
    input_text = getattr(context, 'input_text', '')

    # Call real parser
    result = subprocess.run(
        ['zsh', '-c', f'source {VDE_ROOT}/scripts/lib/vde-parser && extract_vm_names "{input_text}"'],
        capture_output=True,
        text=True,
        timeout=5
    )

    vms = result.stdout.strip().split('\n')
    assert vm_name.lower() in [v.lower() for v in vms], \
        f"Expected VM '{vm_name}' in parsed VMs: {vms}"
```

### Priority 3: VM Validation (2 tests, 30 min)
**Function**: `step_vm_valid_type`
**Current**: Just returns True
**Target**: Check if VM exists in vm-types.conf

```python
@then('the VM should be recognized as a valid VM type')
def step_vm_valid_type(context):
    """Verify VM is a valid type."""
    vm_name = getattr(context, 'target_vm', 'python')
    
    # Check vm-types.conf
    conf_path = VDE_ROOT / "scripts" / "data" / "vm-types.conf"
    with open(conf_path) as f:
        content = f.read()
    
    # VM should appear in config (case-insensitive)
    assert vm_name.lower() in content.lower(), \
        f"VM '{vm_name}' not found in vm-types.conf"
```

## Phase 2: WHEN Step Context Setup (2 hours)

The THEN steps above need input. Implement WHEN steps that set context properly:

```python
@when('I plan to create {vm_names}')
def step_plan_create_vms(context, vm_names):
    """Plan to create VMs - stores input for verification."""
    # Store the natural language input
    context.input_text = f"create {vm_names}"
    # THEN steps will verify the parser can extract this correctly

@when('I plan to start {vm_names}')
def step_plan_start_vms(context, vm_names):
    """Plan to start VMs - stores input for verification."""
    context.input_text = f"start {vm_names}"
```

## Phase 3: Keep Contextual GIVEN Steps (0 hours)

These are acceptable as context-only - they set up user stories, not system state:

```python
@given("I am starting my development day")
def step_starting_development_day(context):
    """User story context - acceptable as context-only."""
    context.workflow_state = 'morning_setup'
    # This is fine - it's not testing VDE, just setting up the scenario
```

**Keep as-is**: 38 contextual GIVEN steps

## Implementation Strategy

### Step 1: Implement Core Helper (30 min)
Create shared parser call function:

```python
def call_vde_parser(function_name, input_text):
    """Call VDE parser function with input."""
    result = subprocess.run(
        ['zsh', '-c', f'source {VDE_ROOT}/scripts/lib/vde-parser && {function_name} "{input_text}"'],
        capture_output=True,
        text=True,
        cwd=VDE_ROOT,
        timeout=5
    )
    return result.stdout.strip(), result.returncode
```

### Step 2: Convert 10 Critical Tests (3 hours)
Focus on tests that verify:
1. Intent detection (3 tests)
2. VM extraction (5 tests)  
3. VM validation (2 tests)

### Step 3: Run Tests & Fix (1 hour)
- Run test suite
- Fix any issues with subprocess calls
- Adjust assertions as needed

### Step 4: Document & Commit (30 min)
- Update audit document with progress
- Commit working implementations

## Success Criteria

### Minimal Success (Phase 1 only)
- 10 real test implementations
- Tests call actual VDE parser
- Tests verify real output
- At least 3-5 scenarios passing

### Target Success (Phases 1-2)
- 15 real test implementations
- WHEN steps properly set context
- THEN steps verify real behavior
- 10+ scenarios passing

### Full Success (All Phases)
- 80 real implementations (keep 38 contextual)
- 68% real test coverage
- 25+ scenarios passing
- Documented patterns for remaining tests

## Estimated Impact

### Before Implementation
- 0/31 scenarios passing
- 118/118 fake tests
- 0% functional verification

### After Phase 1 (4-5 hours)
- 3-5/31 scenarios passing
- 108/118 fake tests remaining  
- 10% functional verification

### After Full Implementation (25-30 hours)
- 20-25/31 scenarios passing
- 38/118 contextual (acceptable)
- 68% functional verification

## Next Steps

1. **Immediate**: Implement Phase 1 core verification (this session if time permits)
2. **Short-term**: Implement Phase 2 context setup
3. **Long-term**: Convert remaining 50 critical THEN steps

## Files to Modify

- `tests/features/steps/daily_workflow_steps.py` - Add real implementations
- `tests/features/steps/documented_workflow_steps.py` - Add WHEN step context
- `tests/features/steps/test_helpers.py` - Add parser helper function (new file)
