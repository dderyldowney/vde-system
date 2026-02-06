# Plan 33: Sub-Plans Summary (33b-33l)

**Parent Plan**: [Plan 33: Test Suite Remediation](33-comprehensive-test-remediation-plan.md)  
**Created**: 2026-02-06

This document provides a summary of all remaining sub-plans. Each can be expanded into a detailed plan following the template established in [Plan 33a](33a-docker-operations-remediation.md).

---

## Tier 1: Critical Infrastructure

### Plan 33a: Docker Operations ✓ COMPLETED
**Feature**: `tests/features/docker-required/docker-operations.feature`  
**Status**: ✓ COMPLETED (2026-02-06)
**Steps**: 81 implemented, 0 undefined

### Plan 33b: Error Handling and Recovery ✓ COMPLETED
**Feature**: `tests/features/docker-required/error-handling-and-recovery.feature`  
**Status**: ✓ COMPLETED (2026-02-06)
**Steps**: 80 implemented, 0 undefined

**Key Areas**:
- Invalid VM name handling
- Docker daemon not running detection
- Disk space error handling
- Network creation failures
- Container startup timeouts
- SSH connection failures
- Permission denied errors
- Configuration file errors
- Graceful degradation
- Automatic retry logic
- Partial state recovery
- Clear error messages
- Error logging
- Rollback on failure

**Dependencies**: Docker operations, VM lifecycle management

**Estimated Effort**: 8-10 hours

---

### Plan 33c: Daily Development Workflow ✓ COMPLETED
**Feature**: `tests/features/docker-required/daily-development-workflow.feature`  
**Status**: ✓ COMPLETED (2026-02-06)
**Steps**: 38 implemented, 0 undefined

**Key Areas**:
- Getting connection information for a VM
- Restarting a VM with rebuild
- Starting multiple VMs at once
- Creating a new VM for the first time
- Morning setup workflow
- Status checks during development
- Evening cleanup
- Troubleshooting workflows

**Dependencies**: Docker operations, VM lifecycle, SSH configuration

**Estimated Effort**: 6-8 hours

---

## Tier 2: Core User Features

### Plan 33d: Natural Language Commands ✓ COMPLETED
**Feature**: `tests/features/docker-required/natural-language-commands.feature`  
**Status**: ✓ COMPLETED (2026-02-06)
**Steps**: 53 implemented, 0 undefined

**Key Areas**:
- Intent detection (list, create, start, stop, restart, status, connect, help)
- VM name extraction from natural language
- Multiple VM handling
- Rebuild and no-cache flags
- Alias resolution
- Command execution
- Error handling for ambiguous input

**Dependencies**: VDE parser library, VM operations

**Estimated Effort**: 5-7 hours

---

### Plan 33e: SSH and Remote Access
**Feature**: `tests/features/docker-required/ssh-and-remote-access.feature`  
**Priority**: HIGH  
**Undefined Steps**: ~30  
**Scenarios**: 12

**Key Areas**:
- Getting SSH connection information
- VSCode Remote-SSH integration
- SSH key authentication
- Workspace directory access
- Sudo access in containers
- Shell configuration (zsh, oh-my-zsh)
- Editor configuration (neovim, LazyVim)
- File transfers (scp)
- Port forwarding for services
- SSH session persistence

**Dependencies**: SSH configuration, Docker operations

**Estimated Effort**: 5-6 hours

---

### Plan 33f: Multi-Project Workflow
**Feature**: `tests/features/docker-required/multi-project-workflow.feature`  
**Priority**: HIGH  
**Undefined Steps**: ~25  
**Scenarios**: 9

**Key Areas**:
- Setting up web development projects
- Switching between projects
- Microservices architecture setup
- Data science project setup
- Full stack web applications
- Mobile development with backend
- Cleaning up between projects

**Dependencies**: Docker operations, VM lifecycle

**Estimated Effort**: 4-5 hours

---

## Tier 3: Advanced Features

### Plan 33g: SSH Agent Forwarding - VM-to-VM
**Feature**: `tests/features/docker-required/ssh-agent-forwarding-vm-to-vm.feature`  
**Priority**: MEDIUM  
**Undefined Steps**: ~35  
**Scenarios**: 10

**Key Areas**:
- Inter-VM SSH connections
- SSH agent forwarding between VMs
- Key forwarding security
- SCP between VMs
- Remote command execution
- Database access from VMs
- Multi-hop SSH connections
- Private key security

**Dependencies**: SSH agent, Docker networking

**Estimated Effort**: 6-7 hours

---

### Plan 33h: SSH Agent Forwarding - External Git
**Feature**: `tests/features/docker-required/ssh-agent-external-git-operations.feature`  
**Priority**: MEDIUM  
**Undefined Steps**: ~30  
**Scenarios**: 8

**Key Areas**:
- Git clone with SSH
- Git submodule operations
- Multi-account GitHub support
- SSH key forwarding for Git
- Private repository access

**Dependencies**: SSH agent, Git operations

**Estimated Effort**: 5-6 hours

---

### Plan 33i: SSH Agent Automatic Setup
**Feature**: `tests/features/docker-required/ssh-agent-automatic-setup.feature`  
**Priority**: MEDIUM  
**Undefined Steps**: ~25  
**Scenarios**: 12

**Key Areas**:
- Automatic SSH agent startup
- SSH key auto-detection
- Multiple key support
- Silent operation during normal use
- SSH agent restart if not running
- Viewing SSH status
- SSH config auto-generation
- Rebuilding VMs preserves SSH config
- Key generation (ed25519 preferred)
- Public key synchronization
- SSH client compatibility

**Dependencies**: SSH agent, key management

**Estimated Effort**: 4-5 hours

---

### Plan 33j: VM-to-Host Communication
**Feature**: `tests/features/docker-required/ssh-agent-vm-to-host-communication.feature`  
**Priority**: MEDIUM  
**Undefined Steps**: ~20  
**Scenarios**: 10

**Key Areas**:
- SSH from VM to host
- Docker socket access from VMs
- Host file system access
- Host service access
- Host command execution
- Host log access
- Host resource monitoring
- Host network connectivity checks

**Dependencies**: Docker socket mounting, SSH configuration

**Estimated Effort**: 3-4 hours

---

## Tier 4: Productivity Features

### Plan 33k: Productivity Features
**Feature**: `tests/features/docker-required/productivity-features.feature`  
**Priority**: MEDIUM  
**Undefined Steps**: ~20  
**Scenarios**: 8

**Key Areas**:
- Workspace persistence
- Database backups and restores
- Running services in background
- Quick environment switching
- Resource management

**Dependencies**: Docker volumes, VM lifecycle

**Estimated Effort**: 3-4 hours

---

### Plan 33l: Daily Workflow
**Feature**: `tests/features/docker-required/daily-workflow.feature`  
**Priority**: MEDIUM  
**Undefined Steps**: ~15  
**Scenarios**: 6

**Key Areas**:
- Morning setup routine
- Status checks during development
- Evening cleanup routine
- Quick VM switching
- Documentation alignment

**Dependencies**: VM lifecycle, Docker operations

**Estimated Effort**: 2-3 hours

---

## Total Summary

| Tier | Plans | Undefined Steps | Estimated Effort |
|------|-------|-----------------|------------------|
| 1 | 2 (33b-33c) | ~85 | 14-18 hours |
| 2 | 3 (33d-33f) | ~90 | 14-18 hours |
| 3 | 4 (33g-33j) | ~110 | 18-22 hours |
| 4 | 2 (33k-33l) | ~35 | 5-7 hours |
| **Total** | **11** | **~320** | **51-65 hours** |

**Note**: Plan 33a (Docker Operations, ~50 steps, 7.5-9.5 hours) is already created, bringing the grand total to **~370 steps** and **58.5-74.5 hours** across all 12 sub-plans.

## Next Steps

1. **Option A**: Expand each summary into a detailed plan (like 33a)
2. **Option B**: Use this summary as a reference and create detailed plans as needed
3. **Option C**: Start executing Plan 33a and create detailed plans just-in-time

## Template Structure

Each detailed plan should follow the structure of Plan 33a:
- Overview
- Current State
- Phase 1: Discovery & Analysis
- Phase 2: Step Definition Planning
- Phase 3: Implementation (in iterations)
- Phase 4: Validation
- Phase 5: Integration Testing
- Phase 6: Completion
- Estimated Effort
- Risks and Mitigation
- Dependencies
- Next Steps
- References
