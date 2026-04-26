# GLOBAL PATH PURIFICATION Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enforce relative path derivation for `VDE_ROOT_DIR` across all VDE scripts and libraries to ensure absolute portability.

**Architecture:** Update `bin/` scripts to derive root via `${0:h:h}` and `lib/` files via `${(%):-%x:h:h}`. Ensure all derivations are exported.

**Tech Stack:** Zsh-native path expansion.

---

### Task 1: Update `bin/` scripts

**Files:**
- Modify: All files in `bin/` that define `VDE_ROOT_DIR`.
- Common targets: `bin/vde`, `bin/vde-poll`, `bin/list-vms`, etc.

- [ ] **Step 1: Identify all files in `bin/` using scalar/relative `VDE_ROOT_DIR` definitions.**
- [ ] **Step 2: Surgically update each file to use `VDE_ROOT_DIR="${0:h:h}"` and `export VDE_ROOT_DIR`.**
- [ ] **Step 3: Verify that Mandate 24 tags are preserved on Line 2 or 3.**
- [ ] **Step 4: Commit changes.**

### Task 2: Update `lib/` files

**Files:**
- Modify: All files in `lib/` that define `VDE_ROOT_DIR`.
- Key target: `lib/vm-common`, `lib/vde-root`, etc.

- [ ] **Step 1: Identify all files in `lib/` using scalar/relative `VDE_ROOT_DIR` definitions.**
- [ ] **Step 2: Surgically update each file to use `VDE_ROOT_DIR="${(%):-%x:h:h}"` inside the `-z "${VDE_ROOT_DIR:-}"` block.**
- [ ] **Step 3: Ensure `export VDE_ROOT_DIR` is present.**
- [ ] **Step 4: Verify Mandate 24 tags.**
- [ ] **Step 5: Commit changes.**

### Task 3: Fix `plans/scripts/test_fifo.zsh`

**Files:**
- Modify: `plans/scripts/test_fifo.zsh`

- [ ] **Step 1: Locate absolute path leaks (source "/[U]sers/dderyldowney/VDE/lib/...")**
- [ ] **Step 2: Replace with `${VDE_ROOT_DIR}/lib/...` or relative sourcing.**
- [ ] **Step 3: Commit changes.**

### Task 4: Final Validation

- [ ] **Step 1: Run `bin/vde-enforce-uap.zsh` to ensure no absolute path leaks remain.**
- [ ] **Step 2: Run Proof of Life test.**
- [ ] **Step 3: Verify portability by running `bin/vde` from outside the project root.**
- [ ] **Step 4: Run all tests.**
