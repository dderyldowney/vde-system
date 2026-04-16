# ARCHITECTURE 1.3.7 (The Sovereign Baseline)

## 1. Philosophical Pillars (The Way)

- **The Forge**: The Virtual Development Environment (VDE) is a modular, containerized ecosystem designed for secure, reproducible software engineering.
- **The Spine**: The system is built upon four non-negotiable technologies: **Zsh, Git, Docker, and SSH**.
- **The Chronicle**: History is preserved through strict adherence to Conventional Commits and automated GitHub workflows.

## 2. Structural Design (The Armor)

- **Hub**: The host machine, governing orchestration and security.
- **Spokes**: Isolated containers (jails) where hydration and development occur.
- **Bridges**: Secure transversal connections (SSH, socat) between the Hub and Spokes.

## 3. Security posture (The Beskar)

- **Identity Isolation**: Development occurs exclusively as `devuser` within Spokes.
- **Network Segmentation**: Spokes are confined to the `vde-net` bridge with no host-network exposure except via mapped ports.
- **Static Guards**: UAP enforcement and pre-commit hooks verify mandate compliance at every strike.

---
Version: 1.3.7
Status: SOVEREIGN BASELINE CERTIFIED
Identity: The Covert
---
