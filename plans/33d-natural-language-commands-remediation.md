# Plan 33d: Natural Language Commands Remediation

**Feature**: `tests/features/docker-required/natural-language-commands.feature`  
**Created**: 2026-02-06  
**Updated**: 2026-02-07  
**Status**: ⚠️ PARTIAL - See Plan 34 for remaining work

---

## Summary

This plan addresses the implementation of natural language command parsing tests for VDE. Users should be able to interact with VDE using conversational commands like "start python" or "what's currently running?"

---

## Current Status (2026-02-07)

### Test Results
- **Total Scenarios**: 14
- **Passing**: 10
- **Failing**: 4
- **Steps**: 53 implemented

### Fixed Issues
- ✅ Corrected `vde` script path from `VDE_ROOT/vde` to `VDE_ROOT/scripts/vde` in `natural_language_steps.py`

### Failing Scenarios
1. "Using aliases instead of canonical names" - Alias resolution not working
2. "Wildcard operations" - Wildcard pattern not supported
3. "Troubleshooting language" - Error handling steps missing
4. "Minimal typing commands" - Short-form commands not recognized

---

## Original Plan Content

### Overview

This plan implements step definitions for testing VDE's natural language command parsing capabilities. These tests verify that users can interact with VDE using conversational commands.

### Current State

Initial analysis shows that natural language command tests exist in `tests/features/docker-required/natural-language-commands.feature` but many steps are undefined or improperly implemented.

### Scope

#### Intent Detection Tests
- `list_vms` intent (list VMs, list running VMs)
- `list_langs` intent (what languages, show languages)
- `list_svcs` intent (what services, show services)
- `create_vm` intent (create VM, create a VM)
- `start_vm` intent (start VM, launch VM)
- `stop_vm` intent (stop VM, shutdown VM)
- `restart_vm` intent (restart VM, reboot VM)
- `rebuild_vm` intent (rebuild VM)
- `status` intent (show status, what's running)
- `connect` intent (connect to VM, SSH into VM)
- `help` intent (help me, what can I do)

#### Entity Extraction Tests
- VM name extraction from natural language
- Multiple VM handling (comma-separated, "and" conjunction)
- Alias resolution (nodejs → JavaScript, js → JavaScript)
- Pipe-delimited VM lists (python|rust)

### Phase 1: Discovery & Analysis

1. **Analyze Feature File**
   - Document all scenarios and their Gherkin steps
   - Identify dependencies between scenarios
   - Map each step to potential implementation patterns

2. **Survey Existing Libraries**
   - `scripts/lib/vde-parser` - Main parsing library
   - `scripts/lib/vde-commands` - Command execution
   - Identify available functions for intent detection

3. **Identify Patterns**
   - Steps that call parser functions directly
   - Steps that verify parser output
   - Steps that test actual command execution

### Phase 2: Step Definition Planning

#### Pattern 1: Direct Parser Verification
```python
@when('I parse "{command}"')
def parse_command(context, command):
    result = vde_parser.parse(command)
    context.parsed = result
```

#### Pattern 2: Intent Verification
```python
@then('the intent should be "{expected_intent}"')
def verify_intent(context, expected_intent):
    assert context.parsed.intent == expected_intent
```

#### Pattern 3: Entity Verification
```python
@then('VMs should include "{vm_name}"')
def verify_vm_in_result(context, vm_name):
    assert vm_name in context.parsed.entities
```

### Phase 3: Implementation

#### Iteration 1: Basic Intent Detection
1. `list_vms` intent detection
2. `create_vm` intent detection
3. `start_vm` intent detection
4. `stop_vm` intent detection

#### Iteration 2: Advanced Operations
1. `restart_vm` intent detection
2. `rebuild_vm` intent detection
3. `status` intent detection
4. `connect` intent detection

#### Iteration 3: Complex Scenarios
1. Multiple VM names in single command
2. Alias resolution
3. Error handling for invalid input

### Phase 4: Validation

1. Run behave tests for natural-language-commands feature
2. Verify each scenario passes
3. Document any edge cases that need special handling

### Phase 5: Integration Testing

1. Test natural language commands with actual VM operations
2. Verify parser integrates with command execution
3. Test error scenarios and recovery

---

## Remaining Work (Plan 34)

### Task 1.1: Fix Alias Resolution
**Issue**: VM alias (nodejs → JavaScript) not resolving  
**File**: `tests/features/steps/natural_language_steps.py`

### Task 1.2: Implement Wildcard Operations
**Issue**: No step definition for wildcard VM selection  
**Action**: Add step definition to handle `*` or `all` VM patterns

### Task 1.3: Implement Troubleshooting Language
**Issue**: Error handling steps not implemented  
**Action**: Add step definitions for error detection

### Task 1.4: Implement Minimal Typing Commands
**Issue**: Short-form commands not recognized  
**Action**: Add support for abbreviated commands

---

## References

- [Feature File](tests/features/docker-required/natural-language-commands.feature)
- [Step Definitions](tests/features/steps/natural_language_steps.py)
- [VDE Parser Library](scripts/lib/vde-parser)
- [Plan 34: Full Remediation](34-test-remediation-plan.md)
