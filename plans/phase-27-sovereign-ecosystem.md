# Implementation Plan: VDE Phase 27 — The Sovereign Ecosystem

**Version**: 2.1.0 (Target)
**Objective**: Achieve full feature parity for complex networking and testing scenarios, specifically unblocking the 23 failing/undefined BDD features and resolving VM-to-Host/VM-to-VM communication gaps.

## Background & Motivation
Phase 26 ("The Forge Hardening") successfully stabilized the core CLI and deterministic ignition. However, `PROJECT_STATUS.md` and `tests/TEST_STATUS_REPORT.md` reveal significant gaps in "Sovereign" features where VMs must interact with the host or each other via SSH Agent forwarding and Docker socket access. Additionally, 127 BDD steps remain undefined, preventing full verification of these advanced features.

## Scope & Impact
- **BDD Completion**: Implement 127 undefined steps across 23 scenarios.
- **VM-to-Host Sovereignty**: Fix failures in listing host directories, resource usage, and container management from within a VM.
- **VM-to-VM Networking**: Enable and verify SSH Agent forwarding for seamless VM-to-VM communication.
- **Workflow Hardening**: Improve "Shared Configs" and "Syncing" reliability to 100%.

## Key Files & Context
- `tests/features/steps/`: Location for new Python step definitions.
- `lib/vde-ssh`: Core SSH and agent management logic.
- `configs/ssh/`: SSH configuration templates for forwarding.
- `bin/vde-exec`: Entry point for cross-VM command execution.

## Proposed Solution (Phase 27)

### 1. BDD Step Definition Strike (Unblocking Verification)
- **Feature: SSH Agent Automatic Setup** (12 scenarios): Implement steps for agent detection, ed25519 key generation, and auto-loading.
- **Feature: SSH Agent Forwarding VM-to-VM** (10 scenarios): Implement steps for VM-to-VM SSH and SCP workflows.
- **Feature: SSH and Remote Access**: Define SCP file transfer steps.

### 2. VM-to-Host Communication Fix (The Docker Socket Bridge)
- **Diagnosis**: Identify why Docker socket access is failing (likely permission or mount path issues on Darwin/macOS).
- **Hardening (The Atomic Handshake)**:
    - Implement a ZSH-native entrypoint ritual in `vde-base` to detect the `docker.sock` GID at runtime.
    - Dynamically add `devuser` to the host's Docker GID within the container to ensure non-root socket access without `chmod 777`.
- **Validation**: Verify host directory listing and resource usage from VM via `vde-core` probes.

### 3. VM-to-VM SSH Agent Forwarding (The Trust Bridge)
- **macOS Adaptation**: Transition from manual `$SSH_AUTH_SOCK` mounting to the canonical `/run/host-services/ssh-auth.sock` bridge for Darwin hosts.
- **Implementation**: Harden `vde_ssh_agent_setup` and `vde_ssh_bridge` to ensure `ForwardAgent yes` is correctly applied and verified across container boundaries.
- **Testing**: Use the new BDD steps to confirm seamless hopping between `vde-python` and `vde-postgres` while maintaining host-identity.

## Implementation Plan (Phased)

### Phase 27.0: Bootstrap & Sovereignty Audit (The Ritual)
- [ ] **Reload Instructions**: Re-read `.gemini/instructions.md` and `docs/VDE-SPEC.md` to ensure v2.0.9 mandates are active.
- [ ] **Sovereign Audit**: Execute `bin/vde-enforce-uap.zsh` to verify system integrity.
- [ ] **Ignition Sync**: Run `bin/vde-rebuild-cache` to ensure the Registry is synchronized.

### Phase 27.1: Testing Infrastructure (The Foundation)
- [ ] Create `tests/features/steps/ssh_agent_steps.py`.
- [ ] Create `tests/features/steps/vm_communication_steps.py`.
- [ ] Verify that 23 previously undefined scenarios now attempt execution (RED state).

### Phase 27.2: Networking & Sovereignty (The Strike)
- [ ] Fix `docker.sock` permissions and volume mounting in `lib/vm-common`.
- [ ] Implement `vde_verify_agent_forwarding` in `lib/vde-ssh`.
- [ ] Update `vde-base.Dockerfile` if necessary to support advanced host-probing tools.

### Phase 27.3: Workflow Hardening & Verification (The Shield)
- [ ] Audit `bin/vde-sync-version` for edge cases in multi-user environments.
- [ ] Run full `behave` suite (Docker-Required).
- [ ] Target: 100% Pass Rate on all existing features.

## Verification & Testing
- **BDD**: `behave tests/features/docker-required/` must show 0 undefined steps.
- **Performance**: `bin/vde-health` must confirm Canonical Ignition Speed < 4.0s.
- **Security**: Audit `docker.sock` access to ensure it's limited to authorized operations.

## Migration & Rollback
- **Migration**: Update `MEMORY.md` to reflect v2.1.0 status.
- **Rollback**: Standard git revert of logic changes; image caches can be purged via `vde-images prune`.
