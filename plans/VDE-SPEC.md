# VDE-SPEC v1.3.0 (The Sovereign Evolution)

## 1. Absolute Mandates (The Rule Spine)

- **Language of the Tribe (ZSH ONLY)**: All CLI tools, libraries, and jail shells MUST use `#!/usr/bin/env zsh`. `bash` is strictly prohibited.
- **The Armorer’s Command (UAP)**: Every action MUST be run under `bin/vde-enforce-uap.zsh`. No action is permitted without this spine.
- **Born Ready (BTO)**: Every jail MUST be fully functional at image creation. Runtime `apt` calls or network-dependent configurations are prohibited.
- **Universal Script Parity (USP)**: Every VM entry MUST point to a setup script at `scripts/setup/<alias>-init.zsh`. Inline logic is prohibited.
- **The Beskar Vault (Data Authority)**: `data/vm-types.json` and `data/vm-types.conf` are the sole sources of truth. Data integrity is maintained via the **8-Field Standard**: `type|name|aliases|display_name|pkgs|custom_cmd|service_port|ssh_port`.
- **Ignition Sync (Pre-Flight)**: The CLI MUST perform a timestamp audit at ignition. If source files are newer than the cache, a re-smelt is mandatory.
- **The 3-VM Concurrent Limit**: Parallel ignition and stress operations are strictly limited to a maximum of 3 concurrent VMs.
- **The Rule of One (Versioning)**: This document is the SOLE authority for the project version. The current version defined here is known as the **Sovereign Baseline**. In case of any discrepancy or conflict, the version recorded in this file wins all arguments and serves as the absolute state of truth.

## 2. Architecture (The Hub-and-Spoke Model)

VDE adheres to the three-tier inheritance model detailed in `docs/ARCHITECTURE.md`:
1.  **The Hub (`vde-base`)**: Defines Identity (devuser), Shell (Zsh), and Core Security.
2.  **The Spoke (`scripts/setup/`)**: USP rituals that hydrate the environment at build-time.
3.  **The Jail (Container)**: The immutable running process.

## 3. The Trial of the Gauntlet (TDD Mandate)

All implementation strikes MUST follow the **Red-Green-Refactor** law codified in Section 14 of `.gemini/instructions.md`:
1.  **The Red Gauntlet**: A physical, failing test file MUST exist before implementation.
2.  **The Green Victory**: Implementation must be minimal, solving only what the test demands.
3.  **The Refiner's Fire**: Refactoring occurs only under a Green light.

## 4. Directory Structure

- `bin/`: CLI entry points and UAP enforcement.
- `lib/`: Shared Zsh libraries.
- `data/`: Core VM types and configs.
- `docs/`: Technical specifications and user manuals.
- `scripts/`: USP initialization rituals.
- `plans/`: Staging and diagnostic logs.

## 5. The Sovereign Artifact Set Mandate

VDE adheres to a strict directory layout to ensure portability and zero-host dependency:
- `bin/`: The primary CLI orchestrators (`vde`, `vde-enforce-uap.zsh`).
- `lib/`: The core ZSH libraries (Tetrad components).
- `data/`: The Beskar Source (`vm-types.conf`) and persistent Spoke data.
- `scripts/setup/`: The USP rituals for Spoke hydration.
- `projects/`: The Hub-to-Jail workspace mappings.
- `.cache/`: High-speed runtime archives.
- `.locks/`: FIFO Ticket-based concurrency gates.

## 5. The Sovereign Artifact Set Mandate

When a Sovereign Baseline release is cut, the following documents MUST be updated to match the new reality before tagging is allowed: `ARCHITECTURE.md`, `TECHNICAL_DEEP_DIVE.md`, `RELEASE_NOTES.md`, and `VDE-SPEC.md`. These four files move as a single artifact set for every Sovereign Baseline. If the system changes in a way the current spec cannot describe, the spec must be rewritten so that the implementation and `VDE-SPEC.md` are again in perfect agreement.

---

- **Identity Key**: All SSH operations MUST use the `vde_student` identity.
- **Workspace Mapping**: `/home/devuser/workspace` maps to `projects/<name>/`.
- **Data Persistence**: Databases and services map to `data/<name>/`.

---
Version: 1.3.0
Reference: ARCHITECTURE v1.3.0 (The Sovereign Baseline)
---
