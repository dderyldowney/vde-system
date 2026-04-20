# Proposal: The Tightened Mark (Architectural Classification)

## I. The Decision Rule (The Pyramid Peak)

Before a strike acts, it must determine its lineage using the **Test of the Two Fires**. This decision rule sits at the top of the pyramid:

**The Test of the Two Fires:**
1.  **Does this artifact serve "Any Thing" or govern the development process?** If the component enforces rules, interacts with GitHub, directs AI agents, or provides generic automation that could theoretically serve *any* project (even those without Docker, Git, SSH, or Zsh), it belongs to **Project 2 (The Forge)**. Tag: `@forge`.
2.  **Is this artifact a physical runtime requirement for the specific VDE product?** If the component is directly responsible for orchestrating containers, managing SSH bridges, or handling the specific lifecycle of VDE Spokes, and it must operate in a completely "AI-blind" and "Hub-blind" environment, it belongs to **Project 1 (The Armor)**. Tag: `@armor`.
3.  **Is this artifact the foundational bridge between the two?** If the component defines the core constants, the absolute technical gates, or the rigid data structures required for the Armor to run *and* the Forge to audit, it is the shared foundation. Tag: `@shared-law`.

---

## II. The Sovereign Enumeration

**Project 1: The Armor (The VDE Engine Product)**
The Armor is the physical, student-facing Virtual Development Environment engine. It is a specialized product built upon the Unyielding Tetrad (Zsh, Git, Docker, SSH) dedicated exclusively to the creation, orchestration, and transversal access of containerized Spokes. It is strictly "AI-blind" and "Hub-blind," possessing only the logic necessary to execute its specific physical runtime duties without any external governance dependencies.

**Project 2: The Forge (Development AI-Governance System)**
The Forge is the universal development, auditing, and governance rig. It manages the entire GitHub lifecycle (Issues, PRs, CI/CD), enforces the Rule Spine for AI agents, and provides generic automation capabilities. The Forge encompasses "Any Thing" logic—tools and protocols that do not serve the specific VDE container orchestration, but rather serve the development process itself, making it adaptable to any project regardless of its underlying technology stack.

---

## III. The Hierarchical Component Outline

*   **VDE Sovereign System**
    *   **Project 1: The Armor (`@armor`)**
        *   **Code (Binaries)**: `bin/vde`, `bin/ssh-vm`, `bin/vde-init`, `bin/vde-rebuild`, `bin/vde-start`, `bin/vde-stop`, `bin/vde-rm`
        *   **Code (Libraries)**: `lib/vde-docker`, `lib/vde-ssh`, `lib/vm-lock`, `lib/vde-naming`, `lib/vde-path-utils`, `lib/vde-progress`
        *   **Docs**: `VDE_INSTALL.md`, `USER_GUIDE.md`, `FOUNDLING_GUIDE.md`
        *   **Tests**: `tests/unit/*.zsh` (All unit tests verifying Engine-specific library functions) and foundational step definitions (`tests/features/steps/init_steps.py`, etc.)
        *   **Rituals**: Engine Ignition (`vde init`), Spoke Smelting (`vde rebuild`), Transversal Bridge (`vde enter`)
    *   **Project 2: The Forge (`@forge`)**
        *   **Code (Binaries)**: `bin/vde-enforce-uap.zsh`, `bin/paired_update_enforcer`, `bin/cleanup-ports`, generic utility scripts (`bin/vde-tactical-sweep.zsh`)
        *   **Code (Libraries)**: `lib/vde-audit`, `lib/vde-metrics` (Generic governance/reporting tools that serve "Any Thing" development visibility)
        *   **Docs**: `AGENTS.md`, `gemini.md`, `docs/GITHUB_LIFECYCLE.md`, `CONTRIBUTING.md`
        *   **Tests**: CI/CD configuration files, AI-governance validation steps.
        *   **Rituals**: The Signet and Chronicle (GitHub Flow), Code Review Gates, AI-Agent Dispatch
    *   **The Foundation (`@shared-law`)**
        *   **Code (Gates)**: `bin/vde-check-tetrad.zsh` (Technical Integrity Gate)
        *   **Code (Libraries)**: `lib/vde-core`, `lib/vde-constants`, `lib/vde-shell-compat`, `lib/vm-common`
        *   **Data**: `data/vm-types.json`, `data/vm-types.schema.json`
        *   **Docs**: `SOVEREIGN_CHARTER.md`, `VDE-SPEC.md`, `ARCHITECTURE.md`
        *   **Tests**: `tests/features/core-infrastructure/*.feature` (Proof of Life, Technical Integrity), Integration step definitions linking abstract functions to execution state.
