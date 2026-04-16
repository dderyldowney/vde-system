# ARCHITECTURE 1.4.0 (The Sovereign Baseline)

## 1. Philosophical Pillars (The Way)

- **The Creed-frame**: The foundational narrative that fuels the Forge. All work is anchored in the Mandalorian and Forge Mythos (`data/vde_core/**`), ensuring our culture and our craft are indistinguishable.
- **The Gospel**: The Sovereign Artifact Set (specified in Section 4) is the absolute authority. These documents are the **limiting, or expanding, decision makers** on the **WHAT** and the **HOW** of all creation and refactoring.
- **The Creed**: The Forge exists solely to serve the **Foundlings** (Students) and **Reinforcements** (New Hires). This is **Creed**. Every technical strike must be centrally driven by its direct improvement to their experience.
- **The Spine**: The system is built upon four non-negotiable technologies: **Zsh, Git, Docker, and SSH**.
- **The Forge**: The Virtual Development Environment (VDE) is a modular, containerized ecosystem designed for secure, reproducible software engineering.
- **The Chronicle**: History is preserved through strict adherence to Conventional Commits and automated GitHub workflows.

## 2. Structural Design (The Armor)

- **Hub**: The host machine, governing orchestration and security.
- **Spokes**: Isolated containers (jails) where hydration and development occur.
- **Bridges**: Secure transversal connections (SSH, socat) between the Hub and Spokes.

## 3. Security posture (The Beskar)

- **Identity Isolation**: Development occurs exclusively as `vde_student` within Spokes.
- **Network Segmentation**: Spokes are confined to the `vde-net` bridge with no host-network exposure except via mapped ports.
- **Static Guards**: UAP enforcement and pre-commit hooks verify mandate compliance at every strike.

## 4. The Sovereign Artifact Set (The Gospel)

The following seven files move as a single artifact set for every Sovereign Baseline. They must be in perfect agreement with the Forge state before any tag is struck:
1. `ARCHITECTURE.md` (The Strategy)
2. `TECHNICAL_DEEP_DIVE.md` (The Mechanics)
3. `RELEASE_NOTES.md` (The Archive)
4. `VDE-SPEC.md` (The Gospel Lead & Version Arbiter)
5. `USE_CASES.md` (The Audit)
6. `VDE_ANALYSIS.md` (The Engineering Verdict)
7. `PROJECT_STATUS.md` (The Living Heartbeat)

## 5. The Release Ritual (The Living Mark)

VDE enforces a strict branch-based release lifecycle to maintain the purity of the Baseline:
1.  **Develop (`develop`)**: The primary integration branch. All work occurs here or on branches originating from it.
2.  **Main (`main`)**: The stable production branch. **All step tagging (X.X.X) and GitHub releases MUST occur on this branch.**
3.  **The Ritual**: Once `develop` is merged into `main`, the merge SHA on `main` is tagged with the version. The GitHub Release is then created from that SHA on the `main` branch.
4.  **The Mirror**: Finally, this SHA is applied to the `stable` branch, overwriting its previous state.
5.  **X.X.X Releases**: Step and milestone releases are applied against `main` only. `develop` remains for development only.

---
Version: 1.4.0
Status: SOVEREIGN BASELINE CERTIFIED
Identity: The Covert
---
