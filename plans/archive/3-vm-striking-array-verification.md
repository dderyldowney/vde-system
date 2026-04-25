# 3-VM Striking Array Verification Implementation Plan
<!-- @shared-law (Forge Component) -->

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Finalize the 3-VM Striking Array Verification for VDE 2.0.6, including a clean sweep, concurrency testing, and documentation updates.

**Architecture:** Use `bin/vde-enforce-uap.zsh` to orchestrate commands, ensuring ZSH compliance and strict data registry adherence.

**Tech Stack:** ZSH, Behave, Docker, VDE Orchestrator.

---

### Task 1: Clean Sweep

**Files:**
- Modify: `.cache/port-registry/*` (Delete)
- Modify: `.locks/vms/*` (Delete)

- [ ] **Step 1: Shutdown all VMs**
Run: `bin/vde-enforce-uap.zsh bin/shutdown-all all -f`
Expected: All running VDE containers are terminated.

- [ ] **Step 2: Clear port registry cache**
Run: `rm -rf .cache/port-registry/*`
Expected: Registry is empty.

- [ ] **Step 3: Clear VM locks**
Run: `rm -rf .locks/vms/*`
Expected: No stale locks remain.

### Task 2: Live Fire Exercise

**Files:**
- Test: `tests/features/core-infrastructure/concurrency-stress.feature`

- [ ] **Step 1: Run concurrency stress test**
Run: `bin/vde-enforce-uap.zsh behave tests/features/core-infrastructure/concurrency-stress.feature`
Expected: "Parallel Ignition" scenario passes for "python, postgres, redis".

- [ ] **Step 2: Verify test output**
Analyze the stdout to ensure the specific 3-VM load was tested successfully.

### Task 3: Final Documentation

**Files:**
- Modify: `MEMORY.md`
- Modify: `docs/ARCHITECTURE.md`

- [ ] **Step 1: Update MEMORY.md**
Add note under "Phase 25 Progress" about recalibration to 3-VM concurrent load and "Combat Load" verification.

- [ ] **Step 2: Update docs/ARCHITECTURE.md**
Add section 3.4 "The 3-VM Striking Array (Standard Load)" explaining the 1 Language + 2 Services combat load verification.

- [ ] **Step 3: Final Verification [UAP-SUCCESS]**
Confirm all steps are complete and report success.
