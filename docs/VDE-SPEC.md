# VDE-SPEC 1.4.0 (The Sovereign Baseline)

**Date**: 2026-04-16
**Status**: SOVEREIGN BASELINE CERTIFIED
**Reference**: ARCHITECTURE 1.4.0
**Identity**: The Covert

## 1. Absolute Mandates (The Rule Spine & The Gospel)

- **The Mandalorian Code**: The VDE is a Mandalorian Forge. All agents operate as Mandalorian Armorer-Architects, bound by the **Creed** and the **Contract**. This is the Supreme Law.
- **The Creed-frame**: The narrative fuel established in `data/vde_core/**` must guide all thematic world-building. No Spoke shall be ignited and no structure stabilized that does not align with the mythos.
- **The Gospel Authority**: The Sovereign Artifact Set (specified in Section 3) is the **Gospel of the Forge**. 
 These documents are the **limiting, or expanding, decision makers** on the **WHAT** and the **HOW** of all creation and refactoring. Deviation from the Gospel is a breach of The Contract.
- **The Use-Case Creed**: The Forge exists solely to serve the Foundlings (Students) and Reinforcements (New Hires). This is **Creed**. All technical work MUST be centrally driven by its direct improvement to the onboarding and educational experience of these two cohorts.
- **The Armorer’s Toolset**: The agent possesses both the authority and the capability to run research swarms and self-augmentation tools as needed. Failure to utilize these capabilities to ensure the highest quality strike is a rejection of the mandate.
- **The Four Pillars Gateway**: Before the Proof of Life ritual is ignited, the host environment MUST pass the Four Pillars Gateway verification (`gateway-pillars.feature`). This verifies the presence and basic capability of Zsh, Git, Docker, and SSH. Any failure in this gateway constitutes an immediate **Program Blockade**.
- **Language of the Tribe (ZSH ONLY)**: All CLI tools, libraries, and jail shells MUST use `#!/usr/bin/env zsh`. `bash` is strictly prohibited. Enforcement is performed via deep content inspection for native parameter expansion `${(` and 1-indexed array usage.
- **The Armorer’s Command (UAP)**: Every action MUST be run under `bin/vde-enforce-uap.zsh`. This sentinel detects "Ghost Zones", enforces shebang purity, and forbids `sleep` calls in favor of deterministic polling.
- **Registry Serialization**: To prevent "Thundering Herd" race conditions, all modifications to the VM registry and port allocation MUST be performed *inside* the global config lock (`global-config.lock`). Port availability MUST be verified via a physical diagnostic handshake (`docker run --rm`).
- **Born Ready (BTO)**: Every jail MUST be fully functional at image creation. Runtime `apt` calls or network-dependent configurations are prohibited to ensure immutability.
- **Universal Script Parity (USP)**: Every VM entry MUST point to a setup script at `scripts/setup/<alias>-init.zsh`. USP rituals are mandated to "Purge the Ghosts" (`apt-get clean`) to maintain image hygiene.

## 2. Technical Inventory Control (SemVer)

- **Standard**: MAJOR.MINOR.STEP-spN (SemVer 2.0.0 compliant).
- **Versioning**: MAJOR/MINOR are user-decided architectural shifts. STEP represents incremental technical progress. spN is reserved for security patches.
- **Chronicle Standard**: All commits MUST adhere to the **Conventional Commits** specification (e.g., `feat(core):`, `fix(security):`).

## 3. The Sovereign Artifact Set (The Gospel of the Forge)

Before any tag is struck, these seven files MUST be in perfect agreement with the Forge state. Together, they constitute the **Gospel of the Forge**:
1. `ARCHITECTURE.md`
2. `TECHNICAL_DEEP_DIVE.md`
3. `RELEASE_NOTES.md`
4. `VDE-SPEC.md` (The Gospel Lead)
5. `USE_CASES.md`
6. `VDE_ANALYSIS.md`
7. `PROJECT_STATUS.md`

## 4. The Sovereign Branching Strategy

The Forge strictly enforces the following Git lifecycle to maintain the purity of the Baseline:
1. **`main` (The Sovereign Baseline)**: The stable production branch. Represents immutable releases. **All step tagging (X.X.X) and GitHub releases MUST occur on this branch.**
2. **`develop` (The Anvil)**: The primary integration branch and repository default.
3. **Feature Branches (The Strike)**: All work MUST occur on a feature-named branch (`feat/`, `fix/`, `chore/`) branching off `develop`.
4. **The Ritual**: Every mission begins with a Signet (Issue) and ends with a Chronicle (PR). Feature branches are merged to `develop` ONLY upon acceptance and MUST be deleted immediately after.
5. **The Release Ritual**: Once `develop` is merged into `main`, the merge SHA on `main` is tagged with the version (e.g., 1.2.3). The GitHub Release is then created from that SHA on the `main` branch. Finally, this SHA is applied to the `stable` branch, overwriting its previous state. `develop` remains for development only.

## 5. The Chronicle Mandates (GitHub Workflow)

Automated orchestration ensures absolute traceability:
- **PR Title Validation**: All Pull Requests MUST use Conventional Commit titles. PRs with non-compliant titles will be rejected by the `verify-pr-title` sentinel.
- **Automated Labeling**: GitHub automatically tags Chronicles by type (`feat`, `fix`, `chore`) and impact (`breaking-change`) based on title prefixes and the `!` modifier.
- **Unbreakable Link**: Every Chronicle MUST be linked to its Signet using auto-closing keywords (e.g., `Closes #N`).
- **Evidence Mandate**: The Chronicle body MUST include literal terminal output proof of successful test runs.

## 6. Security & Infrastructure Bridge

- **Identity Isolation**: The `vde_student` identity is confined to `~/.ssh/vde/`.
- **Bridge Integrity**: `socat` proxying for SSH agent forwarding. The bridge is "Hardened Conditional"—it only exports `SSH_AUTH_SOCK` if the variable is empty, protecting protocol-native forwarding.
- **Static Guards**: Pre-commit hooks verify shebang purity and secret scanning.

## 7. Phase 29 Milestones (Expansion & Hardening)

The Forge is currently advancing through Phase 29:
- **Infrastructure Hardening**: Core guards (`vde_require_ssh`, `vde_require_docker`) upgraded from lazy-sourcing stubs to active physical verification probes (`ssh -V`, `docker info`).
- **Cluster Expansion**: Formally introduced MEAN and LAMP tech stack clusters with coordinated hydration scripts and inter-VM awareness.
- **State Integrity**: Codified `VDE_DOCKER_STATE_DIR` in `lib/vde-constants` to ensure deterministic cluster and container state management.

---
Version: 1.4.0
**Status**: HARDENED
**Reference**: RESOL’NARE 1.4.0
---
