# Sovereign Branching Strategy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Codify the Sovereign Branching Strategy. `main` is the stable production branch. `develop` is the primary development branch. All features, modifications, and remediations MUST be performed on feature-named branches branching off `develop`, and then merged back into `develop`.

**Architecture:** Update `VDE_PROTOCOL.md` with a new "Laws of the Forge (Branching)" section. Update the "Quick Start" and "Submitting Changes" sections of `CONTRIBUTING.md` to reflect this workflow.

**Tech Stack:** Markdown documentation updates.

---

### Task 1: Update VDE_PROTOCOL.md

**Files:**
- Modify: `VDE_PROTOCOL.md`

- [ ] **Step 1: Add the Branching Law to VDE_PROTOCOL.md**
Insert a new section detailing the branching strategy before the Git Hooks section.

```markdown
## **VI. THE LAWS OF THE FORGE (BRANCHING)**

The VDE repository strictly enforces a Sovereign Branching Strategy to maintain the purity of the Baseline:

1. **`main` (The Sovereign Baseline):** This is the stable, "production" branch. It represents the certified, immutable releases of the Forge.
2. **`develop` (The Anvil):** This is the primary integration branch for all ongoing development.
3. **Feature Branches (The Strike):** All design, creation, modification, or remediation work MUST be performed on a feature-named branch (e.g., `feat/new-vm-type`, `fix/ssh-bridge`) branching **off of `develop`**.
4. **The Merge:** Once work on a feature branch survives the Trial of the Gauntlet (testing), it is merged **back into `develop`**.
```

### Task 2: Update CONTRIBUTING.md

**Files:**
- Modify: `CONTRIBUTING.md`

- [ ] **Step 1: Update the Quick Start section**
Modify the Quick Start instructions to explicitly use the `develop` branch workflow.

```markdown
## Quick Start

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/vde-system.git`
3. Checkout the development branch: `git checkout develop`
4. Create a feature branch off develop: `git checkout -b feat/your-feature-name`
5. Make your changes
6. Run tests: `make check` (or use the VDE orchestration tools)
7. Commit and push: `git push origin feat/your-feature-name`
8. Open a Pull Request targeting the `develop` branch
```

- [ ] **Step 2: Update Submitting Changes section**
Ensure the PR instructions also reference targeting `develop`.

```markdown
### Submitting Changes

1.  **Branch Naming:** Use clear, descriptive names for your branches (e.g., `feat/add-rust-support`, `fix/port-allocation-bug`, `docs/update-readme`).
2.  **Target Branch:** All Pull Requests MUST target the `develop` branch. PRs targeting `main` will be rejected unless they are official release preparations authorized by the Alor.
3.  **Conventional Commits:** Follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification for all commit messages.
4.  **Testing:** Ensure all relevant tests (especially `@system-spine` if modifying core infrastructure) pass before submitting.
```

### Task 3: Review and Commit

**Files:**
- Execute: Git commands

- [ ] **Step 1: Verify the Markdown formatting**
Review `VDE_PROTOCOL.md` and `CONTRIBUTING.md` to ensure the new sections render correctly and match the document's tone.

- [ ] **Step 2: Commit the changes**
Commit the documentation updates with a Conventional Commits message.
`git commit -m "docs(core): codify Sovereign Branching Strategy in protocol and contributing guides"`