<!-- @shared-law (Sovereign Artifact Set) -->
# VDE Sovereign Charter: The Law of the Two Projects

This Charter defines the dual-mission architecture of the VDE. It is the foundational covenant that ensures the absolute integrity of the product and its governed evolution.

---

## I. The Sovereign Architecture Definition

The VDE ecosystem is architected as two distinct projects that operate independently but work in hierarchical harmony to ensure the absolute integrity of the product and its development.

### 1. Project 1: The Armor (The VDE Engine Product)
**The Armor** is the physical, student-facing product—the core engine that enables the Virtual Development Environment.

*   **Individual Use**: Providing a robust, isolated, and standardized CLI for "Foundlings" (students) to ignite development Spokes (VMs). It handles container orchestration, network isolation, and workspace management.
*   **Target**: **Specific**. It serves *this* project (VDE) and its specialized container requirements.
*   **Sovereign Dependencies**: It depends **exclusively** on the **Unyielding Tetrad** (zsh, git, docker, ssh).
*   **AI-Blindness**: It is designed to be **AI-unaware** and **Hub-blind**. It must function perfectly without any Project 2 components or `gh` CLI access.
*   **Integrity Gate**: Protected by the **Lightweight Technical Gate** (`bin/vde-check-tetrad.zsh`).

### 2. Project 2: The Forge (Development AI-Governance System)
**The Forge** is the universal development, auditing, and governance rig.

*   **Individual Use**: Enforcing the **Rule Spine** (Mandalorian Creed) and Mandates during the development lifecycle. It owns "GitHub Life," managing Issues, PRs, CI/CD, and release synchronization.
*   **Target**: **Universal**. It serves **"Any Thing"**—tools and protocols that could theoretically serve *any* project (regardless of tech stack) to ensure governed development.
*   **Core Tools**: It uses the **GitHub CLI (`gh`)** as its foundational binary to interact with the Hub. It includes all agent instructions, Forge rules, and CI workflows.
*   **Role**: It acts as the "Architect" that builds the Armor.

---

## II. The Hierarchical Component Outline

*   **VDE Sovereign System**
    *   **Project 1: The Armor (@armor)**
        *   **Code (Binaries)**: `bin/vde`, `bin/ssh-vm`, `bin/vde-init`, `bin/vde-rebuild`, `bin/vde-start`, `bin/vde-stop`, `bin/vde-rm`.
        *   **Code (Libraries)**: `lib/vde-docker`, `lib/vde-ssh`, `lib/vm-lock`, `lib/vde-naming`, `lib/vde-path-utils`, `lib/vde-progress`.
        *   **Docs**: `VDE_INSTALL.md`, `USER_GUIDE.md`, `FOUNDLING_GUIDE.md`.
        *   **Tests**: `tests/unit/*.zsh` (Engine Unit Tests), `tests/features/steps/init_steps.py` (Foundational Steps).
        *   **Rituals**: Engine Ignition (`vde init`), Spoke Smelting (`vde rebuild`), Transversal Bridge (`vde enter`).
    *   **Project 2: The Forge (@forge)**
        *   **Code (Binaries)**: `bin/vde-enforce-uap.zsh`, `bin/paired_update_enforcer`, `bin/cleanup-ports`, `bin/vde-tactical-sweep.zsh`.
        *   **Code (Libraries)**: `lib/vde-audit`, `lib/vde-metrics` (Generic Governance).
        *   **Docs**: `AGENTS.md`, `GEMINI.md`, `docs/GITHUB_LIFECYCLE.md`, `CONTRIBUTING.md`.
        *   **Tests**: CI/CD Workflows, AI-governance validation steps.
        *   **Rituals**: The Signet and Chronicle (GitHub Flow), Code Review Gates, AI-Agent Dispatch.
    *   **The Foundation (@shared-law)**
        *   **Code (Gates)**: `bin/vde-check-tetrad.zsh` (Technical Integrity Gate).
        *   **Code (Libraries)**: `lib/vde-core`, `lib/vde-constants`, `lib/vde-shell-compat`, `lib/vm-common`.
        *   **Data**: `data/vm-types.json`, `data/vm-types.schema.json`.
        *   **Docs**: `SOVEREIGN_CHARTER.md`, `VDE-SPEC.md`, `ARCHITECTURE.md`.
        *   **Tests**: `tests/features/core-infrastructure/*.feature` (Proof of Life, Technical Integrity).

---

## III. How They Work Together (The Symbiotic Covenant)

The relationship is hierarchical: **The Forge builds the Armor.**

1.  **The Foundation Link**: The Forge cannot be lit without the Armor. The Heavy Gate (P2) ALWAYS trips the Technical Gate (P1) first.
2.  **The Shielded Product**: During development, we use the Forge (AI agents, `gh`, CI/CD) to modify the codebase. However, the resulting code (The Armor) is meticulously decoupled so that it remains purely driven by the Tetrad.
3.  **The Decision Rule (Test of the Two Fires)**: Before a strike acts, classify the strike:
    - **Armor Strike (@armor)**: Satisfies a physical runtime requirement for the specific VDE product (Naked Machine Audit).
    - **Forge Strike (@forge)**: Satisfies a universal requirement for governed development, "Any Thing" automation, or AI discipline (Governance Guard Audit).
    - **Shared-Law Strike (@shared-law)**: Modifies the foundational bridge or pillars used by both (Symbiotic Link Audit).

4.  **The Tagging Report**: For EVERY strike, the agent MUST produce an explicit **Tagging Report** listing each touched artifact and its classification. This report is recorded in the permanent Chronicle (PR body) to build an empirical database of architectural ownership.

---

**This is the Way.**
