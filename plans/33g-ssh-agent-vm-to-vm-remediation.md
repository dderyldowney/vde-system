# Plan 33g: SSH Agent Forwarding - VM-to-VM Remediation

**Parent Plan**: [Plan 33: Test Suite Remediation](33-comprehensive-test-remediation-plan.md)  
**Priority**: MEDIUM (Tier 3)  
**Created**: 2026-02-06  
**Status**: ✅ Implemented

---

## Overview

This plan addresses SSH Agent Forwarding for VM-to-VM communication, enabling secure inter-VM SSH connections without exposing private keys.

**Feature File**: `tests/features/docker-required/ssh-agent-forwarding-vm-to-vm.feature`

---

## Current State

### Statistics
- **Total Scenarios**: 10
- **Undefined Steps**: ~35
- **Current Pass Rate**: 0% (all scenarios untested)
- **Target Pass Rate**: ≥70% (7/10 scenarios)

### Key Areas
- Inter-VM SSH connections
- SSH agent forwarding between VMs
- Key forwarding security
- SCP between VMs
- Remote command execution
- Database access from VMs
- Multi-hop SSH connections
- Private key security

---

## Phase 3: Implementation Iterations

### Iteration 1: Basic VM-to-VM SSH (3 scenarios)
**Steps**: ~10 - Inter-VM connections, agent forwarding

### Iteration 2: Secure Operations (3 scenarios)
**Steps**: ~10 - Key security, SCP, remote commands

### Iteration 3: Advanced Features (4 scenarios)
**Steps**: ~15 - Database access, multi-hop, security verification

---

## Estimated Effort

**Total**: 6-7 hours

---

## Dependencies

- **Completed**: Plan 32 (SSH Configuration)
- **Related**: Plans 33a (Docker Operations), 33i (SSH Agent Setup)

---

## References

- [SSH Configuration](../docs/ssh-configuration.md)
- [Security Documentation](../SECURITY.md)
