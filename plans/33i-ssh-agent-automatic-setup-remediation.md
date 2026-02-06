# Plan 33i: SSH Agent Automatic Setup Remediation

**Parent Plan**: [Plan 33: Test Suite Remediation](33-comprehensive-test-remediation-plan.md)  
**Priority**: MEDIUM (Tier 3)  
**Created**: 2026-02-06  
**Status**: Not Started

---

## Overview

This plan addresses SSH Agent Automatic Setup, ensuring SSH agents start automatically, detect keys, and configure themselves without user intervention.

**Feature File**: `tests/features/docker-required/ssh-agent-automatic-setup.feature`

---

## Current State

### Statistics
- **Total Scenarios**: 12
- **Undefined Steps**: ~25
- **Current Pass Rate**: 0% (all scenarios untested)
- **Target Pass Rate**: ≥75% (9/12 scenarios)

### Key Areas
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

---

## Phase 3: Implementation Iterations

### Iteration 1: Automatic Startup (4 scenarios)
**Steps**: ~8 - Agent startup, key detection

### Iteration 2: Configuration Management (4 scenarios)
**Steps**: ~9 - Config generation, preservation, multiple keys

### Iteration 3: Key Management (4 scenarios)
**Steps**: ~8 - Key generation, sync, compatibility

---

## Estimated Effort

**Total**: 4-5 hours

---

## Dependencies

- **Completed**: Plan 32 (SSH Configuration)
- **Related**: Plans 33g, 33h (SSH Agent Forwarding)

---

## References

- [SSH Configuration](../docs/ssh-configuration.md)
