# Plan 33e: SSH and Remote Access Remediation

**Feature**: `tests/features/docker-required/ssh-and-remote-access.feature`  
**Created**: 2026-02-06  
**Updated**: 2026-02-07  
**Status**: ⚠️ PARTIAL - See Plan 34 for remaining work

---

## Summary

This plan addresses the implementation of SSH and remote access tests for VDE. Users should be able to access VMs via SSH, configure VSCode Remote-SSH, and manage remote development workflows.

---

## Current Status (2026-02-07)

### Test Results
- **Total Scenarios**: ~12
- **Passing**: 2
- **Errored/Failing**: 9
- **Steps**: Many undefined

### Issues Identified
- SSH connection steps not fully implemented
- VSCode Remote-SSH configuration steps missing
- Workspace directory access verification incomplete
- Sudo access verification not implemented
- Shell/editor configuration checks not implemented

### Root Causes
1. Steps reference non-existent step definitions
2. VM prerequisites not set up before scenarios
3. SSH infrastructure not mocked/configured for tests
4. File system paths not properly parameterized

---

## Original Plan Content

### Overview

This plan implements step definitions for testing VDE's SSH and remote access capabilities. These tests verify that users can:
- Connect to VMs via SSH
- Configure VSCode Remote-SSH
- Access workspace directories
- Execute commands in remote containers

### Scope

#### SSH Connection Tests
- Get SSH connection information for a VM
- Connect to a VM via SSH
- Execute commands in a VM via SSH
- Transfer files to/from a VM
- Port forwarding for services

#### VSCode Remote-SSH Tests
- Configure VSCode Remote-SSH for a VM
- Open a workspace in VSCode on a VM
- Use VSCode extensions in a remote container

#### Workspace Access Tests
- Access workspace directory from host
- Sync files between host and VM
- Mount host directories in VM

### Phase 1: Discovery & Analysis

1. **Analyze Feature File**
   - Document all scenarios and their Gherkin steps
   - Identify dependencies on other step libraries
   - Map each step to potential implementation patterns

2. **Survey Existing Libraries**
   - `scripts/lib/vde-commands` - SSH command wrappers
   - `scripts/lib/vm-common` - VM operations
   - Identify available functions for SSH operations

3. **Identify Patterns**
   - Steps that call SSH functions directly
   - Steps that verify SSH configuration
   - Steps that test actual SSH connections

### Phase 2: Step Definition Planning

#### Pattern 1: SSH Connection
```python
@when('I get SSH connection information for "{vm_name}"')
def get_ssh_info(context, vm_name):
    info = vde_commands.get_ssh_connection(vm_name)
    context.ssh_info = info
```

#### Pattern 2: SSH Execution
```python
@when('I execute "{command}" via SSH in "{vm_name}"')
def ssh_execute(context, command, vm_name):
    result = vde_commands.ssh_exec(vm_name, command)
    context.ssh_result = result
```

#### Pattern 3: VSCode Configuration
```python
@when('I configure VSCode Remote-SSH for "{vm_name}"')
def configure_vscode_ssh(context, vm_name):
    config = vde_commands.generate_vscode_ssh_config(vm_name)
    context.vscode_config = config
```

### Phase 3: Implementation

#### Iteration 1: Basic SSH Operations
1. Get SSH connection information
2. Verify SSH connection
3. Execute basic commands

#### Iteration 2: File Operations
1. Transfer files to VM
2. Transfer files from VM
3. Verify file sync

#### Iteration 3: VSCode Integration
1. Generate VSCode SSH config
2. Verify workspace mounting
3. Test extension compatibility

### Phase 4: Validation

1. Run behave tests for ssh-and-remote-access feature
2. Verify each scenario passes
3. Document any edge cases that need special handling

### Phase 5: Integration Testing

1. Test SSH operations with actual VMs
2. Verify VSCode Remote-SSH integration
3. Test file sync capabilities

---

## Remaining Work (Plan 34)

### Task 2.1: Implement SSH Connection Steps
**Issue**: Step definitions for SSH operations missing  
**Action**: Implement steps in `ssh_connection_steps.py`

### Task 2.2: Implement VSCode Remote-SSH Steps
**Issue**: VSCode configuration steps not implemented  
**Action**: Add step definitions for VSCode SSH config

### Task 2.3: Implement Workspace Access Steps
**Issue**: Workspace directory verification incomplete  
**Action**: Add steps to verify workspace access

### Task 2.4: Implement Sudo Access Verification
**Issue**: Sudo verification not implemented  
**Action**: Add steps to verify sudo access in containers

### Task 2.5: Implement Shell/Editor Configuration
**Issue**: Shell and editor checks missing  
**Action**: Add steps to verify zsh, neovim, LazyVim setup

---

## References

- [Feature File](tests/features/docker-required/ssh-and-remote-access.feature)
- [Step Definitions](tests/features/steps/ssh_connection_steps.py)
- [VDE Commands Library](scripts/lib/vde-commands)
- [Plan 34: Full Remediation](34-test-remediation-plan.md)
