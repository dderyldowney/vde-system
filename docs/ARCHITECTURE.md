# ARCHITECTURE 1.3.7 (The Sovereign Baseline)

## 1. Philosophical Pillars (The Way)

- **The Gospel**: The Sovereign Artifact Set (specified in Section 4) is the absolute authority. These documents are the primary decision-makers on the WHAT and the HOW of all creation and refactoring.
- **The Creed**: The Forge exists solely to serve the **Foundlings** (Students) and **Reinforcements** (New Hires). Every technical strike must be centrally driven by its direct improvement to their experience.
- **The Spine**: The system is built upon four non-negotiable technologies: **Zsh, Git, Docker, and SSH**.
- **The Forge**: The Virtual Development Environment (VDE) is a modular, containerized ecosystem designed for secure, reproducible software engineering.
- **The Chronicle**: History is preserved through strict adherence to Conventional Commits and automated GitHub workflows.

## 2. Structural Design (The Armor)

- **Hub**: The host machine, governing orchestration and security.
- **Spokes**: Isolated containers (jails) where hydration and development occur.
- **Bridges**: Secure transversal connections (SSH, socat) between the Hub and Spokes.

## 3. Security posture (The Beskar)

- **Identity Isolation**: Development occurs exclusively as `devuser` within Spokes.
- **Network Segmentation**: Spokes are confined to the `vde-net` bridge with no host-network exposure except via mapped ports.
- **Static Guards**: UAP enforcement and pre-commit hooks verify mandate compliance at every strike.

## 4. The Sovereign Artifact Set (The Gospel)

The following six files move as a single artifact set for every Sovereign Baseline. They must be in perfect agreement with the Forge state before any tag is struck:
1. `ARCHITECTURE.md` (The Strategy)
2. `TECHNICAL_DEEP_DIVE.md` (The Mechanics)
3. `RELEASE_NOTES.md` (The Archive)
4. `VDE-SPEC.md` (The Gospel Lead & Version Arbiter)
5. `USE_CASES.md` (The Audit)
6. `VDE_ANALYSIS.md` (The Engineering Verdict)

---
Version: 1.3.7
Status: SOVEREIGN BASELINE CERTIFIED
Identity: The Covert
---
