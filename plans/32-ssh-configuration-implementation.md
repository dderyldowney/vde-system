# Plan 32: SSH Configuration Remediation - Detailed Implementation

## Executive Summary

**Feature:** `tests/features/docker-required/ssh-configuration.feature`  
**Scope:** 28 scenarios, ~108 undefined steps, 7 errors  
**Goal:** Consolidate SSH steps, implement missing definitions, fix errors

---

## Phase 1: Audit & Identify Missing Steps

### Step Files to Audit
| File | SSH Steps Count | Status |
|------|-----------------|--------|
| `ssh_config_steps.py` | ~50 | Has many, needs ~30 more |
| `ssh_config_verification_steps.py` | ~5 | Merge into ssh_config_steps.py |
| `ssh_known_hosts_steps.py` | ~6 | Merge into ssh_config_steps.py |
| `ssh_connection_steps.py` | ~3 | Merge into ssh_config_steps.py |
| `pattern_steps.py` | ~4 | Remove SSH-specific steps |
| `vde_ssh_verification_steps.py` | ~10 | Keep separate (VDE-specific) |

---

## Phase 2: Missing GIVEN Steps (Add to ssh_config_steps.py)

### SSH Agent & Keys
```python
@given('SSH agent is running and keys are loaded')
def step_agent_running_keys_loaded(context):
    """Ensure SSH agent is running and has keys loaded."""
    # Verify agent running
    # Verify keys loaded via ssh-add -l

@given('~/.ssh/ contains SSH keys')
def step_ssh_contains_keys(context):
    """Verify ~/.ssh/ directory contains key files."""
    # Check for id_ed25519, id_rsa, etc.

@given('both "id_ed25519" and "id_rsa" keys exist')
def step_both_key_types_exist(context):
    """Ensure both key types exist for preference testing."""
    # Create both if missing

@given('SSH agent is running')
def step_ssh_agent_running(context):
    """Ensure SSH agent is running."""
    # Start agent if not running

@given('keys are loaded into agent')
def step_keys_loaded(context):
    """Ensure keys are loaded into agent."""
    # ssh-add if needed
```

### VM & Port Setup
```python
@given('VM "{vm_name}" is allocated port "{port}"')
def step_vm_allocated_port(context, vm_name, port):
    """VM is allocated a specific port (not yet created)."""
    # Store context for later VM creation

@given('multiple processes try to update SSH config simultaneously')
def step_multiple_processes(context):
    """Setup for concurrent update testing."""
    # Store original config state

@given('SSH config file exists')
def step_ssh_config_exists(context):
    """SSH config file exists for testing."""
    # Ensure ~/.ssh/config exists

@given('SSH agent is not running')
def step_agent_not_running(context):
    """Ensure SSH agent is not running."""
    # Kill agent if running
```

### Known Hosts Setup
```python
@given('~/.ssh/known_hosts contains entry for "[localhost]:{port}"')
def step_known_hosts_localhost_port(context, port):
    """Add localhost port entry to known_hosts."""
    # Format: [localhost]:2200 ssh-ed25519 ...

@given('~/.ssh/known_hosts contains "[::1]:{port}"')
def step_known_hosts_ipv6_port(context, port):
    """Add IPv6 localhost entry to known_hosts."""
    # Format: [::1]:2200 ssh-ed25519 ...

@given('~/.ssh/known_hosts contains "{hostname}" hostname entry')
def step_known_hosts_hostname(context, hostname):
    """Add hostname entry to known_hosts."""
    # Format: hostname ssh-ed25519 ...

@given('~/.ssh/known_hosts had old entry for "[localhost]:{port}"')
def step_known_hosts_old_entry(context, port):
    """Setup for testing entry replacement."""
    # Store original state

@given('~/.ssh/known_hosts exists with content')
def step_known_hosts_with_content(context):
    """known_hosts exists with test content."""
    # Ensure file exists with entries
```

### User Config Setup
```python
@given('~/.ssh/config contains "Host github.com"')
def step_config_has_github(context):
    """SSH config contains GitHub entry."""
    # Add if missing

@given('~/.ssh/config contains "Host myserver"')
def step_config_has_myserver(context):
    """SSH config contains myserver entry."""
    # Add if missing

@given('~/.ssh/config contains "Host *"')
def step_config_has_wildcard(context):
    """SSH config contains wildcard host."""
    # Add if missing

@given('~/.ssh/config contains "User myuser"')
def step_config_has_user(context):
    """SSH config contains user setting."""
    # Add if missing

@given('~/.ssh/config contains "IdentityFile ~/.ssh/mykey"')
def step_config_has_identity(context):
    """SSH config contains identity file."""
    # Add if missing

@given('~/.ssh/config contains python-dev configuration')
def step_config_has_python_dev(context):
    """SSH config contains python-dev entry."""
    # Add full entry if missing

@given('~/.ssh/config contains "    Port 2200" under python-dev')
def step_config_has_python_port(context):
    """SSH config has port under python-dev."""
    # Add if missing
```

---

## Phase 3: Missing WHEN Steps (Add to ssh_config_steps.py)

### Detection Commands
```python
@when('detect_ssh_keys runs')
def step_run_detect_keys(context):
    """Run SSH key detection."""
    # Execute key detection logic

@when('primary SSH key is requested')
def step_request_primary_key(context):
    """Request primary SSH key selection."""
    # Get preferred key

@when('merge_ssh_config_entry starts but is interrupted')
def step_merge_interrupted(context):
    """Simulate interrupted merge operation."""
    # Store state before/after

@when('new SSH entry is merged')
def step_new_entry_merged(context):
    """Perform SSH config merge."""
    # Execute merge logic
```

### VM Operations
```python
@when('I remove VM for SSH cleanup "{vm_name}"')
def step_remove_vm_ssh_cleanup(context, vm_name):
    """Remove VM with SSH cleanup."""
    # Run remove command

@when('I create VM "{vm_name}" with SSH port "{port}"')
def step_create_vm_with_port(context, vm_name, port):
    """Create VM with specific SSH port."""
    # Run create command

@when('multiple processes try to add SSH entries simultaneously')
def step_multiple_add_entries(context):
    """Simulate concurrent SSH entry addition."""
    # Test atomicity
```

---

## Phase 4: Missing THEN Steps (Add to ssh_config_steps.py)

### Permission & Directory
```python
@then('directory should have correct permissions')
def step_correct_permissions(context):
    """Verify SSH directory has correct permissions (700)."""
    # Check mode 0o700

@then('~/.ssh/config should have permissions "600"')
def step_config_permissions_600(context):
    """Verify SSH config has 600 permissions."""
    # Check mode 0o600
```

### Config Content Verification
```python
@then('~/.ssh/config should still contain "Host github.com"')
def step_still_has_github(context):
    """Verify GitHub entry preserved."""
    # Check config content

@then('~/.ssh/config should still contain "Host myserver"')
def step_still_has_myserver(context):
    """Verify myserver entry preserved."""
    # Check config content

@then('new "Host {vm_name}-dev" entry should be appended to end')
def step_entry_appended(context, vm_name):
    """Verify new entry appended to config."""
    # Check end of config

@then('existing entries should be unchanged')
def step_existing_unchanged(context):
    """Verify existing entries preserved."""
    # Compare before/after

@then('new entry should be added with proper formatting')
def step_proper_formatting(context):
    """Verify new entry has proper format."""
    # Check indentation, spacing
```

### Backup Verification
```python
@then('backup file should exist at "backup/ssh/config.backup.YYYYMMDD_HHMMSS"')
def step_backup_exists(context):
    """Verify backup file created."""
    # Check backup directory

@then('backup should contain original config content')
def step_backup_has_content(context):
    """Verify backup has original content."""
    # Compare with original

@then('backup timestamp should be before modification')
def step_backup_timestamp(context):
    """Verify backup timestamp is valid."""
    # Check timestamp ordering

@then('known_hosts backup file should exist at "~/.ssh/known_hosts.vde-backup"')
def step_known_hosts_backup(context):
    """Verify known_hosts backup created."""
    # Check backup file

@then('backup should contain original content')
def step_known_hosts_backup_content(context):
    """Verify known_hosts backup has content."""
    # Compare with original
```

### Known Hosts Verification
```python
@then('~/.ssh/known_hosts should NOT contain entry for "[localhost]:{port}"')
def step_known_hosts_no_localhost_port(context, port):
    """Verify localhost port entry removed."""
    # Check known_hosts content

@then('~/.ssh/known_hosts should NOT contain entry for "[::1]:{port}"')
def step_known_hosts_no_ipv6_port(context, port):
    """Verify IPv6 entry removed."""
    # Check known_hosts content

@then('~/.ssh/known_hosts should NOT contain "{hostname}" entry')
def step_known_hosts_no_hostname(context, hostname):
    """Verify hostname entry removed."""
    # Check known_hosts content

@then('~/.ssh/known_hosts should still contain "[localhost]:{port}"')
def step_known_hosts_still_has(context, port):
    """Verify other entries preserved."""
    # Check known_hosts content
```

### Merged Entry Verification
```python
@then('merged entry should contain "Host {vm_name}-dev"')
def step_merged_has_host(context, vm_name):
    """Verify merged entry has Host."""
    # Check merged content

@then('merged entry should contain "HostName localhost"')
def step_merged_has_hostname(context):
    """Verify merged entry has HostName."""
    # Check merged content

@then('merged entry should contain "User devuser"')
def step_merged_has_user(context):
    """Verify merged entry has User."""
    # Check merged content

@then('merged entry should contain "StrictHostKeyChecking no"')
def step_merged_has_strict(context):
    """Verify merged entry has StrictHostKeyChecking."""
    # Check merged content

@then('merged entry should contain "IdentityFile" pointing to detected key')
def step_merged_has_identity(context):
    """Verify merged entry has IdentityFile."""
    # Check identity file path
```

### Atomicity & Validity
```python
@then('config file should be valid')
def step_config_valid(context):
    """Verify SSH config is valid."""
    # Parse and validate

@then('SSH config should either be original or fully updated')
def step_config_atomic(context):
    """Verify atomic update (no partial writes)."""
    # Check for corruption

@then('original config should be preserved in backup')
def step_backup_preserved(context):
    """Verify backup has original."""
    # Compare with original

@then('no known_hosts file should be created')
def step_no_known_hosts_created(context):
    """Verify no spurious known_hosts creation."""
    # Check file doesn't exist

@then('all VM entries should be present')
def step_all_entries_present(context):
    """Verify no entries lost in concurrent access."""
    # Check all entries exist

@then('no entries should be lost')
def step_no_entries_lost(context):
    """Verify no data loss in concurrent access."""
    # Compare before/after
```

### User Entry Preservation
```python
@then("user's entries should be preserved")
def step_user_entries_preserved(context):
    """Verify user entries preserved after cleanup."""
    # Check github.com, myserver, etc.

@then("user's \"Host github.com\" entry should be preserved")
def step_github_preserved(context):
    """Verify GitHub entry preserved."""
    # Check config content
```

---

## Phase 5: Consolidate Files

### Files to Merge INTO `ssh_config_steps.py`:
1. `ssh_config_verification_steps.py` - Remove file, copy steps
2. `ssh_known_hosts_steps.py` - Remove file, copy steps
3. `ssh_connection_steps.py` - Remove SSH-specific steps

### Files to UPDATE:
1. `pattern_steps.py` - Remove SSH-specific steps, keep generic

---

## Phase 6: Error Fixes (7 Error Scenarios)

### Common Errors to Fix:
1. **AmbiguousStep** - Remove duplicate step definitions
2. **Setup failures** - Fix container creation/teardown
3. **Path issues** - Use consistent `~/.ssh/vde/` paths
4. **Permission errors** - Ensure proper file modes
5. **Timeout issues** - Increase timeouts for Docker operations

---

## Test Execution Plan

```bash
# Step 1: Dry run to verify undefined steps count
python3 -m behave tests/features/docker-required/ssh-configuration.feature --dry-run

# Step 2: Run tests to identify errors
python3 -m behave tests/features/docker-required/ssh-configuration.feature -v 2>&1 | head -100

# Step 3: Check for AmbiguousStep
python3 -m behave tests/features/docker-required/ssh-configuration.feature 2>&1 | grep -i ambiguous

# Step 4: Full test run
python3 -m behave tests/features/docker-required/ssh-configuration.feature
```

---

## Expected Outcome

| Metric | Before | After |
|--------|--------|-------|
| Undefined Steps | 108 | 0 |
| Error Scenarios | 7 | 0 |
| Passing Scenarios | ~10 | 28 |
| Step Files | 10+ | 3 (consolidated) |
