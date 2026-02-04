# Phase 1: Critical Infrastructure Implementation Plan

**Date:** 2026-02-04
**Project:** VDE (Virtual Development Environment)
**Scope:** Critical Infrastructure - VM Naming, Lifecycle, Docker Helpers, Templates

---

## Current State Assessment

| Component | Lines | Status | Gap |
|-----------|-------|--------|-----|
| `docker_helpers.py` | 258 | ✅ Well Implemented | verify_container_stopped() missing |
| `template_steps.py` | 159 | ⚠️ Partial | Missing YAML validation, escape handling |
| `vm_lifecycle_steps.py` | 37 | ❌ Minimal | Only 1 step defined (of ~15 needed) |
| VM Naming Convention | N/A | ❌ Not Addressed | Tests use "python" vs "python-dev" |

---

## Task 1.1: VM Naming Convention Fix (CRITICAL - Blocker)

**Priority:** P0 | **Estimated Steps to Add:** ~15 | **Blocks:** All VM tests

### Root Cause
- Tests reference `VM "python"` but containers are named `python-dev`
- Service VMs (postgres, redis, nginx) don't need suffix
- Language VMs (python, rust, go) need `-dev` suffix

### Files to Modify
1. `tests/features/steps/vm_lifecycle_steps.py`
2. `tests/features/steps/vm_common.py` (helper imports)

### Implementation

```python
# Add to vm_lifecycle_steps.py or create vm_naming_helpers.py

SERVICE_VMS = {'postgres', 'redis', 'mongodb', 'mysql', 'nginx', 'rabbitmq', 'couchdb'}

def _get_container_name(vm_name: str) -> str:
    """Convert VM name to container name."""
    if vm_name in SERVICE_VMS:
        return vm_name
    return f"{vm_name}-dev"

def _get_vm_name(container_name: str) -> str:
    """Convert container name back to VM name."""
    if container_name in SERVICE_VMS:
        return container_name
    return container_name.replace('-dev', '')
```

### Steps to Implement
- [ ] Create `_get_container_name()` helper function
- [ ] Create `_get_vm_name()` helper function
- [ ] Update `step_vm_running()` to use normalized names
- [ ] Add unit tests for naming helpers
- [ ] Verify with actual container names

---

## Task 1.2: VM Lifecycle Steps Complete

**Priority:** P0 | **Estimated Steps:** ~15 | **Blocks:** All VM lifecycle tests

### Missing Steps in `vm_lifecycle_steps.py`

```gherkin
# GIVEN steps
Given VM "{vm}" is running          # ✅ EXISTS (line 30)
Given VM "{vm}" is stopped           # ❌ MISSING
Given VM "{vm}" does not exist       # ❌ MISSING

# WHEN steps
When I create VM "{vm}"              # ❌ MISSING
When I create VM "{vm}" with port {port}  # ❌ MISSING
When I start VM "{vm}"               # ❌ MISSING
When I stop VM "{vm}"               # ❌ MISSING
When I restart VM "{vm}"            # ❌ MISSING
When I delete VM "{vm}"             # ❌ MISSING
When I rebuild VM "{vm}"            # ❌ MISSING

# THEN steps
Then VM "{vm}" should be running     # ❌ MISSING
Then VM "{vm}" should be stopped    # ❌ MISSING
Then VM "{vm}" should not exist     # ❌ MISSING
Then VM "{vm}" should have port {port}  # ❌ MISSING
```

### Implementation Strategy

```python
# vm_lifecycle_steps.py additions

@given('VM "{vm}" is stopped')
def step_vm_stopped(context, vm):
    """Ensure VM is stopped."""
    container_name = _get_container_name(vm)
    # Stop container if running
    result = subprocess.run(
        ['docker', 'stop', container_name],
        capture_output=True, timeout=10
    )

@given('VM "{vm}" does not exist')
def step_vm_not_exists(context, vm):
    """Ensure VM doesn't exist."""
    container_name = _get_container_name(vm)
    # Remove container if exists
    subprocess.run(
        ['docker', 'rm', '-f', container_name],
        capture_output=True
    )

@when('I create VM "{vm}"')
def step_create_vm(context, vm):
    """Create VM using VDE command."""
    result = run_vde_command(['create-virtual', vm])
    context.vm_created = result.returncode == 0

@when('I start VM "{vm}"')
def step_start_vm(context, vm):
    """Start VM using VDE command."""
    result = run_vde_command(['start-virtual', vm])
    context.vm_started = result.returncode == 0

@then('VM "{vm}" should be running')
def step_vm_should_be_running(context, vm):
    """Verify VM is running."""
    container_name = _get_container_name(vm)
    info = verify_container_running(container_name)
    context.vm_status = info.get('Status', '')
```

---

## Task 1.3: Docker Verification Helpers Complete

**Priority:** P0 | **Estimated Functions:** ~3 | **Blocks:** All container tests

### Missing from `docker_helpers.py`

| Function | Status | Purpose |
|----------|--------|---------|
| `verify_container_stopped()` | ❌ MISSING | Check container is not running |
| `verify_container_exits()` | ❌ MISSING | Check container exited |
| `cleanup_test_container()` | ❌ MISSING | Safely remove test containers |

### Implementation

```python
# docker_helpers.py additions

def verify_container_stopped(container_name: str) -> bool:
    """Verify container is not running (stopped or removed)."""
    result = subprocess.run(
        ['docker', 'ps', '--filter', f'name={container_name}', '--format', '{{json .}}'],
        capture_output=True, text=True, timeout=10
    )
    return not result.stdout.strip()

def cleanup_test_container(container_name: str) -> bool:
    """Safely remove a test container."""
    try:
        subprocess.run(
            ['docker', 'rm', '-f', container_name],
            capture_output=True, timeout=10
        )
        return True
    except subprocess.CalledProcessError:
        return False
```

---

## Task 1.4: Template Steps Complete

**Priority:** P0 | **Estimated Steps:** ~10 | **Blocks:** Template tests

### Missing THEN Steps in `template_steps.py`

```gherkin
# Already implemented:
Then rendered output should contain "{value}"              # ✅ Line 125
Then rendered output should NOT contain "{value}"         # ✅ Line 132
Then rendered output should contain "{mapping}" port mapping  # ✅ Line 139
Then rendered output should contain SSH_AUTH_SOCK mapping   # ✅ Line 146
Then rendered output should contain public-ssh-keys volume  # ✅ Line 154

# MISSING:
Then rendered template should be valid YAML                # ❌ MISSING
Then rendered template should be valid JSON                # ❌ MISSING
Then rendered output should escape special characters      # ❌ MISSING
Then rendered output should NOT escape "{value}"           # ❌ MISSING
Then container restart policy should be "{policy}"         # ❌ MISSING
Then container should expose port {port}                   # ❌ MISSING
Then template should include install command               # ❌ MISSING
Then template user should be "{user}"                      # ❌ MISSING
```

### Implementation

```python
# template_steps.py additions

@then('rendered template should be valid YAML')
def step_valid_yaml(context):
    """Verify rendered output is valid YAML."""
    rendered = getattr(context, 'rendered_output', '')
    if HAS_YAML:
        try:
            yaml.safe_load(rendered)
        except yaml.YAMLError as e:
            raise AssertionError(f"Rendered output is not valid YAML: {e}")
    else:
        # Basic syntax check without PyYAML
        assert ': ' in rendered, "Expected YAML key-value format"

@then('container restart policy should be "{policy}"')
def step_restart_policy(context, policy):
    """Verify container restart policy in rendered output."""
    rendered = getattr(context, 'rendered_output', '')
    assert f'restart: {policy}' in rendered, \
        f"Expected restart policy '{policy}'"

@then('container should expose port {port}')
def step_expose_port(context, port):
    """Verify port exposure in rendered output."""
    rendered = getattr(context, 'rendered_output', '')
    assert f'"{port}":' in rendered or f'{port}:' in rendered, \
        f"Expected port {port} to be exposed"

@then('template user should be "{user}"')
def step_template_user(context, user):
    """Verify user in rendered template."""
    rendered = getattr(context, 'rendered_output', '')
    assert f'user: {user}' in rendered, \
        f"Expected user '{user}' in template"
```

---

## Task 1.5: Port Management Steps

**Priority:** P1 | **Estimated Steps:** ~8 | **Blocks:** Port allocation tests

### New File: `tests/features/steps/port_management_steps.py`

```python
"""
BDD Step definitions for Port Management.
"""
from behave import given, then, when
import subprocess

@given('port {port} is available')
def step_port_available(context, port):
    """Verify port is not in use."""
    result = subprocess.run(
        ['lsof', '-i', f':{port}'],
        capture_output=True, text=True
    )
    context.port_available = result.returncode != 0

@then('port {port} should be available for allocation')
def step_port_allocatable(context, port):
    """Verify port can be allocated."""
    # Check port registry or Docker port ranges
    context.port_allocatable = True  # Implement actual check

@when('I allocate port {port} for VM "{vm}"')
def step_allocate_port(context, port, vm):
    """Allocate port for VM."""
    # Update port registry
    pass

@then('VM "{vm}" should have port {port} mapped')
def step_vm_port_mapped(context, vm, port):
    """Verify VM has port mapped."""
    from docker_helpers import get_container_port
    mapped_port = get_container_port(f'{vm}-dev', int(port))
    assert mapped_port == int(port), f"Expected port {port}"
```

---

## Task 1.6: SSH Key Management Steps

**Priority:** P1 | **Estimated Steps:** ~10 | **Blocks:** SSH tests

### New File: `tests/features/steps/ssh_steps.py`

```python
"""
BDD Step definitions for SSH Key Management.
"""
from behave import given, then, when
import subprocess
import os

@given('SSH agent is running')
def step_ssh_agent_running(context):
    """Verify SSH agent is available."""
    result = subprocess.run(
        ['ssh-add', '-l'],
        capture_output=True, text=True
    )
    context.ssh_agent_running = result.returncode == 0 or 'no identities' in result.stderr

@then('available SSH keys should be loaded into agent')
def step_ssh_keys_loaded(context):
    """Verify SSH keys are loaded."""
    result = subprocess.run(
        ['ssh-add', '-l'],
        capture_output=True, text=True
    )
    has_keys = result.returncode == 0
    assert has_keys, "No SSH keys loaded in agent"

@then('public key "{key_name}" should be available')
def step_public_key_available(context, key_name):
    """Verify public key file exists."""
    key_path = os.path.expanduser(f'~/.ssh/{key_name}')
    assert os.path.exists(key_path), f"Public key {key_name} not found"
```

---

## Implementation Order

```
Phase 1: Critical Infrastructure (Week 1)
├── Task 1.1: VM Naming Convention Fix (P0) - START HERE
├── Task 1.2: VM Lifecycle Steps Complete (P0)
├── Task 1.3: Docker Verification Helpers Complete (P0)
├── Task 1.4: Template Steps Complete (P0)
├── Task 1.5: Port Management Steps (P1)
└── Task 1.6: SSH Key Management Steps (P1)
```

---

## Success Criteria - Phase 1 Complete When

- [ ] VM naming convention implemented (`_get_container_name()` helper)
- [ ] All 15+ VM lifecycle steps defined
- [ ] Docker helpers complete (verify_container_stopped, cleanup)
- [ ] Template verification steps complete (YAML validation, restart policy)
- [ ] Port management steps implemented
- [ ] SSH key management steps implemented
- [ ] 500+ scenarios execute without undefined steps
- [ ] All docker-required tests pass (or fail with expected errors)

---

## Files Created/Modified

| File | Action | Lines |
|------|--------|-------|
| `tests/features/steps/vm_naming_helpers.py` | Create | ~30 |
| `tests/features/steps/vm_lifecycle_steps.py` | Modify | +120 |
| `tests/features/steps/docker_helpers.py` | Modify | +40 |
| `tests/features/steps/template_steps.py` | Modify | +50 |
| `tests/features/steps/port_management_steps.py` | Create | ~80 |
| `tests/features/steps/ssh_steps.py` | Create | ~100 |

---

## Testing Strategy

1. **Unit Tests**: Test each helper function in isolation
2. **Integration Tests**: Run full docker-required test suite
3. **Regression Tests**: Verify docker-free tests still pass

---

*Plan generated: 2026-02-04*
