# Synchronize Sovereign Artifact Set Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Formally add `PROJECT_STATUS.md` to the Sovereign Artifact Set, synchronize it with the current 1.4.0 baseline, and codify the Sovereign Release Law.

**Architecture:** Update `docs/VDE-SPEC.md` to redefine the Sovereign Artifact Set and codify the Release Law. Synchronize `PROJECT_STATUS.md`, `docs/ARCHITECTURE.md`, `docs/Technical-Deep-Dive.md`, and `AGENTS.md` to reflect these mandates.

**Tech Stack:** Zsh, GitHub CLI, Conventional Commits.

---

### Task 1: Formalize PROJECT_STATUS.md in the Gospel

**Files:**
- Modify: `docs/VDE-SPEC.md`

- [ ] **Step 1: Update Sovereign Artifact Set definition**
    - Add `PROJECT_STATUS.md` to the list in Section 3.
    - Update the count from six to seven files.

---

### Task 2: Synchronize PROJECT_STATUS.md

**Files:**
- Modify: `PROJECT_STATUS.md`

- [ ] **Step 1: Update Date and Test Fidelity**
    - Change date to `2026-04-15`.
    - Update Behave BDD steps count to `245 Steps`.

---

### Task 3: Codify the Sovereign Release Law

**Files:**
- Modify: `docs/VDE-SPEC.md`
- Modify: `docs/ARCHITECTURE.md`
- Modify: `docs/Technical-Deep-Dive.md`
- Modify: `AGENTS.md`

- [ ] **Step 1: Update VDE-SPEC Section 4 (Branching Strategy)**
    - Explicitly state that step tagging and GitHub releases are *always* applied on the `main` branch.
    - Document the flow: `develop` -> `main` -> Tag/Release on `main` -> Overwrite `stable`.

- [ ] **Step 2: Update ARCHITECTURE.md**
    - Update artifact count to 7.
    - Include `PROJECT_STATUS.md`.
    - Add Section 5 for the Release Ritual.

- [ ] **Step 3: Update Technical-Deep-Dive.md**
    - Update artifact count to 7.
    - Add Section 8 for the Release Ritual mechanics.

- [ ] **Step 4: Update AGENTS.md**
    - Add Mandate 17 to Section 2 (STRICT Core Mandates).

---

### Task 4: Audit and Finalize

- [ ] **Step 1: Run Sovereign Audit**
    - Command: `bin/vde-enforce-uap.zsh`
- [ ] **Step 2: Request Code Review**
    - Dispatch `code-reviewer`.
- [ ] **Step 3: Commit and Link**
    - Commit message: `feat(docs): add PROJECT_STATUS.md to Gospel and codify Release Law`
    - PR body includes `Closes #78`.
