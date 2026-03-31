# VDE Priority Remediation Plan (FINAL v2)
**Generated:** 2026-03-16
**Status:** Phase 1 - Planning (Awaiting Approval)

---

## Executive Summary

**Root Cause Analysis:**
- **13 undefined steps** → Wording mismatches with existing steps → Add multiple decorators
- **2 variable reference bugs** → Undefined `result` variable in assertions
- **9 VM-to-Host failures** → Context flags instead of real verification
- **6 SSH Remote failures** → Missing VM startup + empty assertions

**Solution Approach:**
1. Add multiple decorators to EXISTING step functions (no new alias file)
2. Fix variable reference bugs
3. Replace context flags with real verification

---

## Phase 1: Add Multiple Decorators (P0)

### 1.1 Approach: Decorator Stacking

Instead of creating a new file, add multiple `@given`/`@when`/`@then` decorators to existing functions. 

### 1.2 Verified Mapping

**File: `tests/features/steps/ssh_core_steps.py`**

| Function | Current Decorators | Add Decorator |
|------|---------|---------------|
| `step_ssh_agent_is_running` (L537) | `@given("the SSH agent is running")`<br>`@given("SSH agent is running")` | (Already exists) |
| `step_ssh_keys_loaded` (L781) | `@then("available SSH keys should be loaded into agent")` | `@given("my keys are loaded in the agent")`<br>`@given("keys are loaded into agent")` |
| `step_no_ssh_keys_in_vde` (L471) | `@given("no SSH keys exist in ~/.ssh/vde/")` | `@given("I do not have any SSH keys")` |
| `step_ssh_vde_contains_keys` (L99) | `@given("~/.ssh/vde/ contains SSH keys")` | `@given("I have SSH keys of different types in VDE")` |

**File: `tests/features/steps/post_install_verification_steps.py`**

| Function | Current Decorators | Add Decorator |
|------|---------|---------------|
| `step_impl` (L43) | (Verify existing step for cloning) | `@given("I have just cloned VDE")`<br>`@given("I have cloned the VDE repository to ~/dev")` |

**File: `tests/features/steps/documented_workflow_steps.py`**

| Function | Current Decorators | Add Decorator |
|------|---------|---------------|
| `step_vde_installed` (L67) | `@given("I have VDE configured")`<br>`@given("I have VDE installed")` | (Already exists) |
| `step_new_to_vde` (L74) | `@given("I am new to VDE")` | `@given("I am a new VDE user")` |

**File: `tests/features/steps/docker_management_steps.py`**

| Function | Current Decorators | Add Decorator |
|------|---------|---------------|
| `step_have_multiple_vms_running` (L843) | `@given("I have multiple VMs running")` | `@given("I have several VMs running")` |
| `step_have_several_created` (Check L170 context) | (Identify creation step) | `@given("I have created multiple VMs")`<br>`@given("I have created VMs before")`<br>`@given("I have created several VMs")` |

**File: `tests/features/steps/vm_to_host_steps.py`**

| Function | Current Decorators | Add Decorator |
|------|---------|---------------|
| `step_ssh_into_vm_tohost` (L34) | `@when('I SSH into the {vm_name} VM for VM-to-Host')` | `@given("I am connected to a VM")`<br>`@given("I am connected via SSH")` |

**File: `tests/features/steps/critical_steps.py`**

| Function | Current Decorators | Add Decorator |
|------|---------|---------------|
| `step_run_vde_cli` (L128) | `@when('I run VDE command "{command}"')` | `@when("I create a VM")`<br>`@when("I create a new language VM")` |

### 1.3 New Steps Required

Only **ONE** truly new step is needed:

**File: `tests/features/steps/ssh_remote_access_steps.py`** (ADD)

```python
@given('I have a running VM with SSH configured')
def step_running_vm_with_ssh(context):
    """Ensure a VM is running with SSH configured."""
    if not container_exists('python'):
        run_vde_command('start python', context=context)
        wait_for_container('python', timeout=60)
    ssh_config = Path.home() / '.ssh' / 'vde' / 'config'
    context.ssh_configured = ssh_config.exists()
    context.current_vm = 'python'
```

---

## Phase 2: Fix Variable Reference Bugs (P0)

### 2.1 Issues Found

**File: `tests/features/steps/vm_to_host_steps.py`**

| Line | Function | Bug | Fix |
|------|----------|-----|-----|
| 306 | `step_see_host_containers` | `result.returncode` undefined | Use `context` attribute |
| 364 | `step_postgres_restarted` | `result.returncode` undefined | Use `context` attribute |

### 2.2 Fixes

**Line 302-307:**
```python
# BEFORE:
@then('the output should show my host\'s containers')
def step_see_host_containers(context):
    """Verify host containers are shown."""
    output = getattr(context, 'tohost_output', '')
    assert 'container' in output.lower() or result.returncode == 0, \
        "Output should show host containers"

# AFTER:
@then('the output should show my host\'s containers')
def step_see_host_containers(context):
    """Verify host containers are shown."""
    output = getattr(context, 'tohost_output', '')
    tohost_result = getattr(context, 'tohost_result', False)
    assert tohost_result or 'CONTAINER' in output.upper() or 'NAMES' in output, \
        f"Output should show host containers. Got: {output[:200]}"
```

**Line 360-365:**
```python
# BEFORE:
@then('the PostgreSQL container should restart')
def step_postgres_restarted(context):
    """Verify PostgreSQL restarted."""
    output = getattr(context, 'tohost_restart_output', '')
    assert 'postgres' in output.lower() or 'restarted' in output.lower() or result.returncode == 0, \
        "PostgreSQL should restart"

# AFTER:
@then('the PostgreSQL container should restart')
def step_postgres_restarted(context):
    """Verify PostgreSQL restarted."""
    output = getattr(context, 'tohost_restart_output', '')
    tohost_result = getattr(context, 'tohost_restart_result', False)
    assert tohost_result or 'postgres' in output.lower() or 'restarted' in output.lower(), \
        f"PostgreSQL restart verification failed. Output: {output[:200]}"
```

---

## Phase 3: Fix Empty Assertions (P1)

### 3.1 Issues

**File: `tests/features/steps/ssh_remote_access_steps.py`**

| Line | Function | Issue |
|------|----------|-------|
| 73-74 | `step_have_zsh_shell` | Assertion without descriptive error |
| ~180 | `step_lazyvim_available` | Checks non-existent path |

### 3.2 Fixes

**Line 68-75:**
```python
# BEFORE:
@then('I should have a zsh shell')
def step_have_zsh_shell(context):
    """Verify zsh shell is available via SSH."""
    vm_name = getattr(context, 'connected_vm', 'python')
    result = run_vde_command(f'exec {vm_name} "echo $SHELL"', context=context)
    if result.returncode == 0:
        assert 'zsh' in result.stdout, f"Expected zsh shell, got: {result.stdout}"
    context.zsh_shell_available = True

# AFTER:
@then('I should have a zsh shell')
def step_have_zsh_shell(context):
    """Verify zsh shell is available via SSH."""
    vm_name = getattr(context, 'connected_vm', 'python')
    result = run_vde_command(f'exec {vm_name} "echo $SHELL"', context=context)
    assert result.returncode == 0, f"Failed to get shell from {vm_name}: {result.stderr}"
    assert 'zsh' in result.stdout, f"Expected zsh in {vm_name}, got: {result.stdout.strip()}"
    context.zsh_shell_available = True
```

---

## Phase 4: VM Startup Logic (P1)

### 4.1 Issue

`pattern_steps.py:step_have_several_vms_running` checks but doesn't start VMs.

### 4.2 Fix

**File: `tests/features/steps/pattern_steps.py`** (Line 61-67)

```python
# BEFORE:
@given('I have several VMs running')
def step_have_several_vms_running(context):
    running = docker_ps()
    vde_running = [c for c in running if c.startswith("vde-")]
    context.num_vms_running = len(vde_running)
    context.running_vms = {c.replace("vde-", "") for c in vde_running}

# AFTER:
@given('I have several VMs running')
@given('I have multiple VMs running')  # Additional pattern
def step_have_several_vms_running(context):
    """Ensure multiple VMs are running (start if needed)."""
    running = docker_ps()
    vde_running = [c for c in running if c.startswith("vde-")]
    
    if len(vde_running) < 2:
        run_vde_command('start python go', context=context)
        wait_for_container('python', timeout=60)
        wait_for_container('go', timeout=60)
        running = docker_ps()
        vde_running = [c for c in running if c.startswith("vde-")]
    
    context.num_vms_running = len(vde_running)
    context.running_vms = {c.replace("vde-", "") for c in vde_running}
    assert len(vde_running) >= 2, f"Expected 2+ VMs, found {len(vde_running)}"
```

---

## Implementation Summary

### Files Modified (NO NEW FILES)

| File | Decorators Added | Lines Modified |
|------|------------------|----------------|
| `ssh_config_steps.py` | 4 | 4 |
| `installation_steps.py` | 1 | 1 |
| `documented_workflow_steps.py` | 2 | 2 |
| `pattern_steps.py` | 1 + logic | 15 |
| `vm_lifecycle_steps.py` | 2 | 2 |
| `ssh_connection_steps.py` | 1 | 1 |
| `ssh_remote_access_steps.py` | 1 + new step | 15 |
| `debugging_and_port_steps.py` | 1 | 1 |
| `vm_to_host_steps.py` | Bug fixes | 10 |

### Total Changes

| Category | Count |
|----------|-------|
| Decorators Added | 13 |
| Bug Fixes | 2 |
| New Steps | 1 |
| Logic Improvements | 3 |
| **Total Lines Changed** | ~50 |

---

## Exact Changes by File

### ssh_config_steps.py (4 decorators)

```python
# Line 566 - Add decorator ABOVE existing
@given('the SSH agent is running')
@given('SSH agent is running')
def step_ssh_agent_is_running(context):

# Line 583 - Add decorator ABOVE existing
@given('my keys are loaded in the agent')
@given('keys are loaded into agent')
def step_keys_loaded_into_agent(context):

# Line 504 - Add decorator ABOVE existing
@given('I do not have any SSH keys')
@given('no SSH keys exist in ~/.ssh/vde/')
def step_no_ssh_keys_in_vde(context):

# Line 50 - Add decorator ABOVE existing
@given('I have SSH keys of different types in VDE')
@given('~/.ssh/vde/ contains SSH keys')
def step_ssh_vde_contains_keys(context):
```

### installation_steps.py (1 decorator)

```python
# Line 43
@given('I have just cloned VDE')
@given('I have cloned the VDE repository to ~/dev')
def step_cloned_vde_repo(context):
```

### documented_workflow_steps.py (2 decorators)

```python
# Line 57
@given("I have VDE configured")
@given("I have VDE installed")
def step_vde_installed(context):

# Line 64
@given("I am a new VDE user")
@given("I am new to VDE")
def step_new_to_vde(context):
```

### pattern_steps.py (1 decorator + logic)

```python
# Line 61
@given('I have multiple VMs running')
@given('I have several VMs running')
def step_have_several_vms_running(context):
    """Ensure multiple VMs are running (start if needed)."""
    running = docker_ps()
    vde_running = [c for c in running if c.startswith("vde-")]
    
    if len(vde_running) < 2:
        run_vde_command('start python go', context=context)
        wait_for_container('python', timeout=60)
        wait_for_container('go', timeout=60)
        running = docker_ps()
        vde_running = [c for c in running if c.startswith("vde-")]
    
    context.num_vms_running = len(vde_running)
    context.running_vms = {c.replace("vde-", "") for c in vde_running}
    assert len(vde_running) >= 2, f"Expected 2+ VMs, found {len(vde_running)}"
```

### vm_lifecycle_steps.py (2 decorators)

```python
# Line 80
@given("I have created multiple VMs")
@given("I have created VMs before")
@given("I have created several VMs")
def step_have_several_created(context):
```

### ssh_connection_steps.py (1 decorator)

```python
# Line 33
@given("I have configured SSH through VDE")
@given("I have set up SSH keys")
def step_have_ssh_keys(context):
```

### ssh_remote_access_steps.py (1 decorator + 1 new step)

```python
# Line 31 - Add decorator
@given('I am connected to a VM')
@given('I am connected via SSH')
def step_connected_via_ssh(context):

# ADD NEW STEP after line 75:
@given('I have a running VM with SSH configured')
def step_running_vm_with_ssh(context):
    """Ensure a VM is running with SSH configured."""
    if not container_exists('python'):
        run_vde_command('start python', context=context)
        wait_for_container('python', timeout=60)
    ssh_config = Path.home() / '.ssh' / 'vde' / 'config'
    context.ssh_configured = ssh_config.exists()
    context.current_vm = 'python'
```

### debugging_and_port_steps.py (1 decorator)

```python
# Line 332
@given('I create a VM')
@when('I create a new language VM')
def step_create_new_language_vm(context):
```

### vm_to_host_steps.py (2 bug fixes)

```python
# Line 302-307 - Fix undefined 'result'
@then('the output should show my host\'s containers')
def step_see_host_containers(context):
    output = getattr(context, 'tohost_output', '')
    tohost_result = getattr(context, 'tohost_result', False)
    assert tohost_result or 'CONTAINER' in output.upper() or 'NAMES' in output, \
        f"Output should show host containers. Got: {output[:200]}"

# Line 360-365 - Fix undefined 'result'
@then('the PostgreSQL container should restart')
def step_postgres_restarted(context):
    output = getattr(context, 'tohost_restart_output', '')
    tohost_result = getattr(context, 'tohost_restart_result', False)
    assert tohost_result or 'postgres' in output.lower() or 'restarted' in output.lower(), \
        f"PostgreSQL restart verification failed. Output: {output[:200]}"
```

---

## Test Verification Commands

```bash
# After Phase 1 & 2:
behave tests/features/docker-required/ssh-agent-automatic-setup.feature -q
behave tests/features/docker-required/ssh-agent-forwarding-vm-to-vm.feature -q

# After Phase 3 & 4:
behave tests/features/docker-required/ssh-and-remote-access.feature -q
behave tests/features/docker-required/ssh-agent-vm-to-host-communication.feature -q

# Final validation:
./tests/run-full-test-suite.zsh
```

---

## Phase 5: Refactor Feature Files (P0) ✅ COMPLETE

**Goal:** Eliminate all direct script/Docker calls in `.feature` files to reflect the User's perspective.

Refactored all features to use canonical `When I run VDE command "vde <cmd>"` pattern.

---

## Phase 6: Step Definition Hardening (P0) ✅ COMPLETE

**Goal:** Ensure step definitions reflect the user's interaction with the canonical `vde` CLI.

Standardized generic runner in `critical_steps.py` and resolved all `AmbiguousStep` conflicts.

---

## Phase 7: Sync Workspace Plans (P0)

**Goal:** Maintain global visibility of remediation strategies.

1.  **Paired Linkage:** `session_handover_remediation.md` is updated.
2.  **Step Mapping:** `MISSING_STEPS_PLAN.md` updated with `VDE command` wording.

---

## Success Criteria

| Metric | Target |
|--------|--------|
| Direct Script/Docker Calls in Gherkin | **0** |
| Undefined Steps | **0** |
| Tautological (Fake) Tests | **0** |
| Core Test Pass Rate | **100%** |

---

**END OF PLAN**

**Key Improvement:** No new files needed. All changes are additive decorators to existing functions + 2 bug fixes.
