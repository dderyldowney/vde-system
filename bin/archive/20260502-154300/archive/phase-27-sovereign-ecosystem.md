# Implementation Plan: VDE Phase 27 — The Sovereign Ecosystem (Sovereign Verification)
<!-- @shared-law (Forge Component) -->

**Version**: 2.1.0 (Hardened)
**Objective**: Hardening and Empirical Verification of the "Sovereign Bridges" (Docker Socket & SSH Agent Forwarding).

## 1. Reevaluation: The Equal Metrics (v2.1.0)
The success of Phase 27 is measured by the absolute alignment of the following two metrics:
- **Metric A (Codebase)**: `scripts/vde-entrypoint.zsh` must contain idempotent, deterministic logic for GID mapping and identity forwarding.
- **Metric B (Testing Suite)**: `tests/features/core-infrastructure/system-spine.feature` must provide direct empirical evidence of these bridges working under real container ignition.

## 2. Background & Motivation
The "Sovereign Audit" (April 2026) revealed that core bridge logic is already present but lacks verified fidelity. The test suite was pruned of ~24,000 lines of redundant code to prioritize high-signal empirical evidence. Phase 27 will transition the VDE from "implemented" to "certified sovereign."

## 3. Sovereign Bridge Hardening

### Bridge 1: Docker Socket Sovereignty
- **Current State**: GID detection and `chmod 666` are implemented.
- **Hardening Logic**:
    - Ensure `groupadd` and `usermod` calls are idempotent (ignore "already exists" errors).
    - Verify `docker-ce-cli` is present in `vde-base`.
- **Empirical Proof**: 
    - Scenario: `Sovereign Docker Socket Access`
    - Check: `vde exec python docker ps` returns valid container list without `sudo`.

### Bridge 2: SSH Agent Forwarding
- **Current State**: Symlinking to `/run/host-services/ssh-auth.sock` is implemented for macOS.
- **Hardening Logic**:
    - Validate symlink health at ignition.
    - Standardize `SSH_AUTH_SOCK` in `vde_ssh_agent_setup`.
- **Empirical Proof**:
    - Scenario: `SSH Agent Forwarding Verification`
    - Check: `vde enter python "ssh-add -l"` returns host-loaded keys.

## 4. Phased Implementation

### Phase 27.1: Idempotency Hardening (The Forge)
- [ ] Audit `scripts/vde-entrypoint.zsh` for structural hardening.
- [ ] Update `lib/vde-ssh` to unify socket discovery.
- [ ] Ensure all commands run under `bin/vde-enforce-uap.zsh`.

### Phase 27.2: Empirical Proof (The Shield)
- [x] Add Sovereign Bridge scenarios to `system-spine.feature`.
- [x] Implement high-fidelity steps in `system_spine_steps.py`.
- [x] Run `behave` and verify RED -> GREEN state.
- [x] Harden Atomic Handshake against Darwin kernel lag (Dynamic identity + 3s Strike Timeout).
- [x] Harden Sovereign Bridges (Docker socket access + SSH Agent persistent bridge via .zshenv).
- [x] Physical Handshake Verification (Fail-fast check for host SSH socket).

## 5. Verification
- **Suite**: `system-spine.feature` (High Fidelity).
- **Metric**: 100% Pass Rate; 0 "pink" tests.
- **Performance**: Ignition Speed < 4.5s.
