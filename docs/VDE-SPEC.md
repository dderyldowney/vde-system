# VDE-SPEC 1.3.7 (The Sovereign Hardening)

**Date**: 2026-04-15
**Status**: SOVEREIGN BASELINE CERTIFIED
**Version**: 1.3.7
**Reference**: ARCHITECTURE 1.3.7 (The Sovereign Baseline)
**Identity**: The Covert

## 1. Absolute Mandates (The Rule Spine)

- **The Four Pillars Gateway**: Before the Proof of Life ritual is ignited, the host environment MUST pass the Four Pillars Gateway verification (`gateway-pillars.feature`). This verifies the presence and basic capability of Zsh, Git, Docker, and SSH. Any failure in this gateway constitutes an immediate **Program Blockade**; no further rituals or implementation work are permitted until the host is compliant.
- **Language of the Tribe (ZSH ONLY)**: All CLI tools, libraries, and jail shells MUST use `#!/usr/bin/env zsh`. `bash` is strictly prohibited. Enforcement is performed via deep content inspection for native parameter expansion `${(` and 1-indexed array usage.
- **The Armorer’s Command (UAP)**: Every action MUST be run under `bin/vde-enforce-uap.zsh`. This sentinel detects "Ghost Zones" (e.g., unauthorized root directories like `conductor/`), enforces shebang purity, and forbids `sleep` calls in favor of deterministic polling.
- **Relative Mandates (CI/CD Purity)**: In non-interactive CI/CD environments, the ZSH purity mandate is strictly enforced to prevent deadlocks. Every automation script MUST explicitly source the `vde_core` library and operate in `VDE_CI_MODE=1` to bypass physical port handshakes where necessary.
- **Born Ready (BTO)**: Every jail MUST be fully functional at image creation. Runtime `apt` calls or network-dependent configurations are prohibited to ensure immutability.
- **Universal Script Parity (USP)**: Every VM entry MUST point to a setup script at `scripts/setup/<alias>-init.zsh`. USP rituals are mandated to "Purge the Ghosts" (`apt-get clean`) to maintain image hygiene.

## 2. Technical Inventory Control (SemVer)

- **Standard**: MAJOR.MINOR.STEP-spN (SemVer 2.0.0 compliant).
- **Major**: Architectural/Doctrine shifts (Manual User decision).
- **Minor**: Feature sets (Manual User decision).
- **Step**: Incremental technical progress (Agent recommendation).
- **spN**: Security patches (Mandatory emergency level).

## 3. The Sovereign Artifact Set (The Tetrad of Truth)

Before any tag is struck, these four files MUST be in perfect agreement with the Forge state:
1. `ARCHITECTURE.md`
2. `TECHNICAL_DEEP_DIVE.md`
3. `RELEASE_NOTES.md`
4. `VDE-SPEC.md` (The Final Arbiter)

## 4. The Heartbeat (Proof of Life)

- **The Contract**: `plans/system-spine-contract.md` defines the absolute lifecycle.
- **Verification**: `init` -> `create` -> `rebuild` -> `start` -> `enter` -> `stop` -> `remove`.
- **Status**: 100% GREEN mandated for Baseline certification.

## 5. Security Laws

- **Rule 12 (Sentinel)**: Pre-commit guards for credentials and Spine health.
- **Least Privilege**: Jail isolation via `vde-net` and `vde_student` identity.
- **Bridge Integrity**: `socat` proxying for SSH agent forwarding without host-path leaks.

---
**Version**: 1.3.7
**Status**: HARDENED
**Reference**: RESOL’NARE 1.3.7
---
