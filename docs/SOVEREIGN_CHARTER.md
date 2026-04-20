# VDE Sovereign Charter: The Law of the Two Projects

This Charter defines the dual-mission architecture of the VDE. It is the foundational covenant that ensures the absolute integrity of the product and its governed evolution.

---

## I. The Sovereign Architecture Definition

The VDE ecosystem is architected as two distinct projects that operate independently but work in hierarchical harmony to ensure the absolute integrity of the product and its development.

### 1. Project 1: The Armor (The VDE Engine Product)
**The Armor** is the student-facing product—the core engine that enables the Virtual Development Environment.

*   **Individual Use**: Providing a robust, isolated, and standardized CLI for "Foundlings" (students) to ignite development Spokes (VMs). It handles container orchestration, network isolation, and workspace management.
*   **Sovereign Dependencies**: It depends **exclusively** on the **Unyielding Tetrad** (zsh, git, docker, ssh).
*   **AI-Blindness**: It is designed to be **AI-unaware**. It does not know about GitHub, the `gh` CLI, or any AI governance rules. It must function perfectly in a "naked" environment with only the Tetrad present.
*   **Integrity Gate**: Protected by the **Lightweight Technical Gate** (`bin/vde-check-tetrad.zsh`), which verifies the physical environment before ignition.

### 2. Project 2: The Forge (The Development AI-Governance System)
**The Forge** is the development rig—the system used to build, audit, and evolve The Armor.

*   **Individual Use**: Enforcing the **Rule Spine** (Mandalorian Creed) and Mandates during the development lifecycle. It owns "GitHub Life," managing Issues, PRs, CI/CD, and release synchronization.
*   **Core Tools**: It uses the **GitHub CLI (`gh`)** as its foundational binary to interact with the Hub. It includes all agent instructions (`AGENTS.md`), Forge rules (`.gemini/`), and CI workflows.
*   **Role**: It acts as the "Architect" that builds the Armor. While it is mandatory for our governed development process, it is entirely optional for the student running the Armor.
*   **Integrity Gate**: Protected by the **Heavy Governance Gate** (`bin/vde-enforce-uap.zsh`), which performs deep audits of ZSH purity, mandate compliance, and structural governance.

---

## II. How They Work Together as a "System"

The relationship is hierarchical: **The Forge builds the Armor.**

1.  **The Foundation Link**: The Forge cannot be lit without the Armor. The Heavy Gate (P2) always trips the Technical Gate (P1) first. You cannot have AI-governance on an environment that doesn't have the 4 Pillars (Tetrad) active.
2.  **The Shielded Product**: During development, we use the Forge (AI agents, `gh`, CI/CD) to modify the codebase. However, the resulting code (The Armor) is meticulously decoupled so that it remains purely driven by the Tetrad, unaware of the complex Forge machinery that created it.
3.  **The Dual-Gate Flow**:
    *   **Student Usage**: Only the **Light Gate** is tripped. The system is fast, technical, and simple.
    *   **Developer Usage**: Every action trips the **Heavy Gate**. The system is rigorous, audited, and compliant with the Creed.
4.  **The Strike Loop**: Every change follows the Forge's **Ritual of the Signet and Chronicle** (Issue -> PR), ensuring that the Armor's evolution is documented, tested via real-time atomic audits, and certified green by the Hub's CI sensors.

---

## III. The Charter of the Two Fires (Mythos)

This is the codified Creed of the Forge, defining the relationship between the Beskar and the Armorer.

- **Project 1 (The Armor)**: The Beskar itself. It is the shield that protects the Foundling. It must be strong, pure, and independent. If the Armorer falls, the Armor must still hold the line. It answers only to the **Four Pillars of the Ancestors**.
- **Project 2 (The Forge)**: The Armorer, the Tools, and the Fire. It is the ritual by which the Armor is shaped. It answers to the **Rule Spine** and the **Sovereign Mandates**. It speaks through the **Hub** to certify that every plate is forged in truth.
- **The Symbiotic Covenant**: The Forge cannot burn without the Four Pillars. Every ritual of the Forge first honors the Armor. The Armor is the product of the Forge, but once forged, it stands alone, unburdened by the memory of the tools that made it.

---

**This is the Way.**
