# VDE-SPEC 1.3.1 (The Sovereign Evolution) (The Sovereign Evolution)

## 1. Absolute Mandates (The Rule Spine)

- **Language of the Tribe (ZSH ONLY)**: All CLI tools, libraries, and jail shells MUST use `#!/usr/bin/env zsh`. `bash` is strictly prohibited. Enforcement is performed via deep content inspection for native parameter expansion `${(` and 1-indexed array usage.
- **The Armorer’s Command (UAP)**: Every action MUST be run under `bin/vde-enforce-uap.zsh`. This sentinel detects "Ghost Zones" (e.g., unauthorized root directories like `conductor/`), enforces shebang purity, and forbids `sleep` calls in favor of deterministic polling.
- **Relative Mandates (CI/CD Purity)**: In non-interactive CI/CD environments, the ZSH purity mandate is strictly enforced to prevent deadlocks. Every automation script MUST explicitly source the `vde_core` library and operate in `VDE_CI_MODE=1` to bypass physical port handshakes where necessary.
- **Born Ready (BTO)**: Every jail MUST be fully functional at image creation. Runtime `apt` calls or network-dependent configurations are prohibited to ensure immutability.
- **Universal Script Parity (USP)**: Every VM entry MUST point to a setup script at `scripts/setup/<alias>-init.zsh`. USP rituals are mandated to "Purge the Ghosts" (`apt-get clean`) to maintain image hygiene.
- **The Beskar Vault (Data Authority)**: `data/vm-types.json` and `data/vm-types.conf` are the sole sources of truth. Data integrity is maintained via the **8-Field Standard**: `type|name|aliases|display_name|pkgs|custom_cmd|service_port|ssh_port`.
- **Ignition Sync (Pre-Flight)**: The CLI performs a timestamp audit at ignition. If source files are newer than the cache, a re-smelt via pure ZSH parsing is mandatory before any VM strike.
- **The 3-VM Concurrent Limit**: Parallel ignition and stress operations are strictly limited to a maximum of 3 concurrent VMs to preserve system breath.
- **The Rule of One (Versioning)**: This document is the SOLE authority for the project version. The current version defined here is the **Sovereign Baseline**. In case of any discrepancy, this file wins all arguments without appeal.

## 2. Architecture (The Hub-and-Spoke Model)

VDE adheres to a three-tier inheritance model:
1.  **The Hub (`vde-base`)**: Defines Identity (`devuser`), Shell (`Zsh`), and the core Security layer.
2.  **The Spoke (`scripts/setup/`)**: USP rituals that hydrate the environment at build-time.
3.  **The Jail (Container)**: The immutable running process, bridged to the Hub via the Sovereign Bridge.

## 3. The Trial of the Gauntlet (TDD Mandate)

No functional code shall be committed until its purpose is defined by a failing test:
1.  **The Red Gauntlet**: A physical, failing test file MUST exist on disk.
2.  **The Green Victory**: Minimal implementation to satisfy the test.
3.  **The Refiner's Fire**: Refactoring occurs only under a Green light.

## 4. Directory Structure

VDE adheres to a strict layout to ensure portability and zero-host dependency:
- `bin/`: The primary CLI orchestrators (`vde`, `vde-enforce-uap.zsh`).
- `lib/`: The core ZSH libraries (Tetrad components: Core, Docker, SSH, Security).
- `data/`: The Beskar Source (`vm-types.conf`) and persistent Spoke data.
- `scripts/setup/`: The USP rituals for Spoke hydration.
- `plans/`: Authorized staging area for temporary artifacts and diagnostic logs.
- `docs/`: Technical specifications and release archives.

## 5. The Sovereign Artifact Set Mandate

When a Sovereign Baseline release is cut, the following documents MUST move as a single artifact set and be updated to match the implementation reality before tagging: `ARCHITECTURE.md`, `Technical-Deep-Dive.md`, `RELEASE_NOTES.md`, and `VDE-SPEC.md`. If the system changes in a way the current spec cannot describe, the spec MUST be rewritten to maintain perfect agreement.

---

- **Identity Key**: All SSH operations MUST use the `vde_student` identity located in `~/.ssh/vde/`.
- **Sovereign Bridge**: SSH Agent forwarding is established via `socat` UNIX-proxying, mapping the Hub socket to `~/.ssh/vde/agent.sock` inside the jail.
- **Workspace Mapping**: `/home/devuser/workspace` maps to `projects/<alias>/` on the Hub.

---
Version: 1.3.1
Reference: ARCHITECTURE 1.3.1 (The Sovereign Baseline)
---
