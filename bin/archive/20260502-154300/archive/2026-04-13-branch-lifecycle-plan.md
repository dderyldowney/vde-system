# Sovereign Branching Lifecycle Implementation Plan
<!-- @shared-law (Forge Component) -->

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refine the Sovereign Branching Strategy to explicitly state that feature branches are merged into `develop` *only* when the feature's code is formally accepted, and that the feature branch MUST be deleted immediately following the merge.

**Architecture:** Update the "Laws of the Forge (Branching)" section in `VDE_PROTOCOL.md` and the "Pull Request Process" section in `CONTRIBUTING.md` to reflect these final lifecycle stages.

**Tech Stack:** Markdown documentation updates.

---

### Task 1: Refine VDE_PROTOCOL.md

**Files:**
- Modify: `VDE_PROTOCOL.md`

- [ ] **Step 1: Update the Branching Law in VDE_PROTOCOL.md**
Modify item 4 ("The Merge") to include the acceptance and deletion mandates.

```markdown
4. **The Merge & Deletion:** Once a feature branch survives the Trial of the Gauntlet (testing) and the code is formally **accepted**, it is merged back into `develop`. Immediately following a successful merge, the feature branch **MUST be deleted** to keep the Forge lean and prevent history corruption.
```

### Task 2: Refine CONTRIBUTING.md

**Files:**
- Modify: `CONTRIBUTING.md`

- [ ] **Step 1: Update the Pull Request Process**
Add a new item to the end of the "Pull Request Process" list to explicitly instruct contributors on post-merge branch deletion.

```markdown
### Pull Request Process
1.  **Branch Naming:** Use clear, descriptive names for your branches (e.g., `feat/add-rust-support`, `fix/port-allocation-bug`, `docs/update-readme`).
2.  **Target Branch:** All Pull Requests MUST target the `develop` branch. PRs targeting `main` will be rejected unless they are official release preparations authorized by the Alor.
3.  **Keep PRs focused:** One feature or fix per PR.
4.  **Update documentation:** Include doc changes in the PR.
5.  **Add tests:** Ensure all relevant tests (especially `@system-spine` if modifying core infrastructure) pass before submitting.
6.  **Describe changes:** Explain what and why in PR description.
7.  **Link issues:** Reference related issues with `Fixes #123` or `Relates to #123`.
8.  **Respond to feedback:** Address review comments promptly.
9.  **Post-Merge Cleanup:** Once your PR is formally accepted and merged into `develop`, you MUST delete your feature branch.
```

### Task 3: Review and Commit

**Files:**
- Execute: Git commands

- [ ] **Step 1: Commit the changes**
Commit the documentation updates with a Conventional Commits message.
`git commit -m "docs(core): refine branching strategy with acceptance and deletion laws"`