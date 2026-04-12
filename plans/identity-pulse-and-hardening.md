# Identity Pulse & Image Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement Active Bridge Monitoring (Identity Pulse), extend BDD for Image Purity, and align all documentation for the v1.3.0 release.

**Architecture:**
- **Identity Pulse**: A health-check mechanism that verifies the SSH agent bridge from within the Jail.
- **Image Hardening**: BDD-level verification of Rule 12.5 (No apt artifacts).
- **Documentation**: 100% parity across `bin/`, `lib/`, and `.md` files.

**Tech Stack:** Zsh, Docker, BDD (Behave/Python)

---

### Task 1: Identity Pulse (Active Bridge Monitoring)

**Files:**
- Create: `lib/vde-pulse`
- Modify: `bin/vde`
- Modify: `bin/vde-exec`
- Modify: `bin/ssh-vm`

- [ ] **Step 1: Create Pulse Library**
File: `lib/vde-pulse`
```zsh
#!/usr/bin/env zsh
# VDE Identity Pulse - Active Bridge Monitoring
vde_identity_pulse() {
    local target="${1}"
    # Verify Spoke can see the host agent
    if ! ./bin/vde-exec "${target}" "ssh-add -l" >/dev/null 2>&1; then
        vde_log_error "Identity Pulse Lost: Spoke '${target}' cannot see host SSH agent." "pulse"
        return 1
    fi
    return 0
}
```

- [ ] **Step 2: Integrate into vde-exec**
Add a silent pulse check before execution to ensure the bridge is active.

- [ ] **Step 3: Integrate into ssh-vm**
Perform a pulse check before opening the login shell.

- [ ] **Step 4: Verification**
Start a VM, manually kill the `socat` process inside, and verify `vde enter` or `vde exec` fails with a Pulse error.

---

### Task 2: Test-Driven Image Hardening (BDD)

**Files:**
- Modify: `tests/features/core-infrastructure/system-spine.feature`
- Modify: `tests/features/steps/system_spine_steps.py`

- [ ] **Step 1: Add Scenario to Feature File**
Add a scenario: "Spoke Image Purity Verification (Rule 12.5)".
Steps: "Given 'vde-python' is currently running", "Then the directory '/var/lib/apt/lists/' should be empty in the Spoke".

- [ ] **Step 2: Implement Step Definition**
In `system_spine_steps.py`, add a step that uses `vde exec` to list `/var/lib/apt/lists/` and assert it's empty (ignoring `.keep` or base directories if necessary, but Rule 12.5 says empty).

- [ ] **Step 3: Run Audit**
`behave tests/features/core-infrastructure/system-spine.feature`.

---

### Task 3: Documentation & Version Alignment

**Files:**
- Modify: `docs/available-scripts.md`
- Audit: All `.md` files in `docs/`

- [ ] **Step 1: Update available-scripts.md**
Add `vde-vision` and `vde-pulse` (logic) to the core scripts list.

- [ ] **Step 2: Version Audit**
Run a final `grep -r "1.3.0"` and `grep -r "1.2.9"` to ensure no legacy pointers remain.

---

### Task 4: Final Release Certification

- [ ] **Step 1: Full System Audit**
Run `behave tests/features/` and ensure 100% GREEN.

- [ ] **Step 2: Commit & Final Approval**
Final commit before code-review and security audit.
