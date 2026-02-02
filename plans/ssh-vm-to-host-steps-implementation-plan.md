# SSH/VM-to-Host Communication Steps Implementation Plan

## Overview
Implement BDD step definitions for the VM-to-Host Communication feature (13 scenarios, 1308 undefined steps).

## Feature File Analysis
**File**: `tests/features/docker-required/ssh-agent-vm-to-host-communication.feature`

### Scenarios (13 total)
1. Executing commands on host from VM
2. Viewing host logs from VM
3. Listing host directories from VM
4. Checking host resource usage from VM
5. Managing host containers from VM
6. Accessing host files from VM
7. Triggering host builds from VM
8. Coordinating multi-VM operations from host
9. Host backup operations from VM
10. Debugging host issues from VM
11. Host network operations from VM
12. Executing custom host scripts from VM

### Missing Step Patterns
All scenarios use these common step patterns that need implementation:
- `I run "to-host <command>"` - Execute command on host via SSH
- `I should see <expected>` - Verify command output
- `the output should show <expected>` - Validate container/list output

## Implementation Steps

### Phase 1: Create New Step File
**File**: `tests/features/steps/vm_to_host_steps.py`

```python
@when('I run "to-host {command}"')
def step_run_to_host(context, command):
    """Execute a command on the host machine from within a VM."""
    # Parse the command (remove 'to-host ' prefix)
    host_command = command.replace('to-host ', '')
    
    # Execute via SSH to host
    result = subprocess.run(
        ['ssh', '-o', 'StrictHostKeyChecking=no', 
         f'user@localhost', host_command],
        capture_output=True, text=True, timeout=30
    )
    
    context.last_command_output = result.stdout
    context.last_command_stderr = result.stderr
    context.last_command_rc = result.returncode
```

### Phase 2: Implement Output Verification Steps
```python
@then('I should see a list of running containers')
def step_verify_containers(context):
    """Verify docker ps output shows containers."""
    assert 'CONTAINER' in context.last_command_output or len(context.last_command_output) > 0


@then('the output should show my host\'s containers')
def step_verify_host_containers(context):
    """Verify containers are from host, not VM."""
    # Host containers typically have specific naming patterns
    output = context.last_command_output
    assert 'python-dev' in output or 'postgres-dev' in output
```

### Phase 3: Implement Resource Monitoring Steps
```python
@then('I should see resource usage for all containers')
def step_verify_resource_usage(context):
    """Verify docker stats shows CPU, memory, I/O."""
    output = context.last_command_output
    assert '%' in output or 'CPU' in output.upper() or 'MEM' in output


@then('I should see CPU, memory, and I/O statistics')
def step_verify_all_stats(context):
    """Verify all stat categories are present."""
    output = context.last_command_output
    # Docker stats shows: CPU %, MEM usage, NET I/O, BLOCK I/O, PIDs
```

### Phase 4: Implement Container Management Steps
```python
@then('the PostgreSQL container should restart')
def step_verify_postgres_restart(context):
    """Verify postgres container is running after restart."""
    result = subprocess.run(
        ['docker', 'inspect', '-f', '{{.State.Running}}', 'postgres-dev'],
        capture_output=True, text=True
    )
    assert result.stdout.strip() == 'true'
```

## Step Definitions to Implement

### GIVEN Steps (Reuse existing)
- `I have Docker installed on my host` → `vm_lifecycle_steps.py:983`
- `I have VMs running with Docker socket access` → `docker_operations_steps.py:64`
- `I have a Python VM running` → `daily_workflow_steps.py:58`
- `I have a Go VM running` → `ssh_vm_steps.py:514`
- `I have multiple VMs running` → `pattern_steps.py:117`
- `I have a management VM running` → `vm_lifecycle_steps.py:852`
- `I have a build VM running` → `vm_lifecycle_steps.py:826`
- `I have a backup VM running` → `vm_lifecycle_steps.py:813`
- `I have a debugging VM running` → `vm_lifecycle_steps.py:845`
- `I have a network VM running` → `vm_lifecycle_steps.py:859`
- `I have a utility VM running` → `vm_lifecycle_steps.py:866`

### WHEN Steps (Need implementation)
1. `I SSH into the {vm_type} VM` → Exists in `ssh_vm_steps.py`
2. `I run "to-host {command}"` → **NEW** - Implement in `vm_to_host_steps.py`

### THEN Steps (Need implementation)
1. `I should see a list of running containers` → **NEW**
2. `the output should show my host's containers` → **NEW**
3. `I should see the host's log output` → **NEW**
4. `the output should update in real-time` → **NEW**
5. `I should see a list of my host's directories` → **NEW**
6. `I should be able to navigate the host filesystem` → **NEW**
7. `I should see resource usage for all containers` → **NEW**
8. `I should see CPU, memory, and I/O statistics` → **NEW**
9. `the PostgreSQL container should restart` → **NEW**
10. `I should be able to verify the restart` → **NEW**
11. `I should see the contents of the host file` → **NEW**
12. `I should be able to use the content in the VM` → **NEW**
13. `the build should execute on my host` → **NEW**
14. `I should see the build output` → **NEW**
15. `I should see the status of the Python VM` → **NEW**
16. `I can make decisions based on the status` → **NEW**
17. `the backup should execute on my host` → **NEW**
18. `my data should be backed up` → **NEW**
19. `I should see the Docker service status` → **NEW**
20. `I can diagnose the issue` → **NEW**
21. `I should see network connectivity results` → **NEW**
22. `I can diagnose network issues` → **NEW**
23. `the script should execute on my host` → **NEW**
24. `the cleanup should be performed` → **NEW**

## Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `tests/features/steps/vm_to_host_steps.py` | Create | New step definitions for VM-to-host |
| `tests/features/steps/ssh_vm_steps.py` | Modify | Add missing SSH steps |
| `tests/features/steps/docker_operations_steps.py` | Modify | Add output verification steps |

## Implementation Order

1. **Week 1, Day 1**: Create `vm_to_host_steps.py` with base structure
2. **Week 1, Day 2**: Implement `I run "to-host {command}"` step
3. **Week 1, Day 3**: Implement container/output verification steps
4. **Week 1, Day 4**: Implement resource monitoring steps
5. **Week 1, Day 5**: Test and debug all implementations

## Prerequisites
- SSH access configured between VMs and host
- Docker socket mounted to VMs (for docker commands)
- SSH keys set up and agent running
- Network connectivity between VMs and host

## Testing Strategy
1. Run behave with tags `@user-guide-connecting` to test only this feature
2. Verify each scenario executes without undefined step errors
3. Validate actual command execution (not just parsing)

## Estimated Effort
- **New step file**: ~100 lines
- **Step implementations**: ~300 lines
- **Testing**: ~2 hours
- **Total**: 1-2 days

## Success Criteria
- 0 undefined steps for this feature
- All 13 scenarios execute without errors
- Real command execution verified (not mocked)
