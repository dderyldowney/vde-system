# Remediation Plan: VDE v2.1.0 Sovereign Verification

## Paired Update Policy
This file is part of a paired update set with [session_handover.md](./session_handover.md). Both files must be updated together to maintain synchronization between accomplishments and outstanding debt.

## High-Priority Architectural Debt
- **Sovereign Bridge Hardening**: Core logic exists in `scripts/vde-entrypoint.zsh` but requires idempotency hardening and empirical verification.
- **USP Finalization**: Ensure 100% of registered VM types follow the hardened USP pattern (set -e, apt-get clean, rm -rf lists).
- **Test Suite Modernization**: The suite has been condensed; any new tests MUST follow the high-fidelity empirical pattern established in `system-spine.feature`.

## Remediation Goals
- **Sovereign Verification**:
    - Verify Docker Socket bridge (non-root access).
    - Verify SSH Agent Forwarding bridge (host identity visibility).
- **Idempotency Hardening**:
    - Harden `scripts/vde-entrypoint.zsh` to handle existing groups/users gracefully.
    - Ensure `bin/vde-enforce-uap.zsh` remains the supreme audit authority.
- **Equal Metrics Alignment**:
    - Align codebase implementation with testing scenarios as equal indicators of system health.

## Task Tracking
- [X] Sovereign Audit (v2.1.0)
- [X] Condensed Test Suite (Pruned 24k lines)
- [X] Implementation of Core Bridge Logic
- [ ] Harden `vde-entrypoint.zsh` idempotency
- [ ] Add Sovereign scenarios to `system-spine.feature`
- [ ] Complete empirical verification of bridges

See ./session_handover.md
