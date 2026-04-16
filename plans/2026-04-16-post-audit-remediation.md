# Sovereign Remediation Plan: Post-1.4.0 Hardening

**Goal:** Eliminate "pink" test debt and further harden Spoke hydration rituals.

**Context:** The Sovereign Test Suite passed 100%, but audits identified placeholder verification logic in core BDD steps.

---

### Task 1: implement 'verify all startable' logic

**Files:**
- Modify: `tests/features/steps/system_spine_steps.py`

- [ ] **Step 1: Replace 'pass' with real verification**
    - The step `every VM must be startable via the VDE orchestrator` is currently a stub.
    - Implementation should iterate through a sample of VM types (to save time) and verify `vde start` returns 0.

---

### Task 2: Signal Handling Verification

**Files:**
- Modify: `tests/features/steps/error_handling_steps.py`

- [ ] **Step 1: Harden signal trap tests**
    - Replace `pass` stubs with logic that verifies the presence of the translated error messages in terminal output.

---

### Task 3: Spoke Hydration Hygiene Audit

**Files:**
- Audit: `scripts/setup/*.zsh`

- [ ] **Step 1: Universal Ghost Purge**
    - Verify `apt-get clean && rm -rf /var/lib/apt/lists/*` is present in every script that performs an `apt` installation.
