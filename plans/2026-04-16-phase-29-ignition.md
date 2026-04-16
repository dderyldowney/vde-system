# Phase 29: Tech Stack Clusters & Infrastructure Hardening

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Harden core infrastructure requirements and expand the Tech Stack Cluster library.

**Architecture:** 
1.  **Hardening**: Replace lazy-source stubs in `lib/vde-core` with active verification probes for SSH and Docker.
2.  **Expansion**: Audit `scripts/setup/` and harden `vde cluster` orchestration for multi-VM tech stacks.

**Tech Stack:** Zsh, Docker, SSH, BDD (Behave).

---

### Task 1: Harden lib/vde-core Requirements

**Files:**
- Modify: `lib/vde-core`

- [ ] **Step 1: Harden vde_require_ssh**
    - Replace the current stub with logic that verifies the `ssh` binary and the `vde_student` identity.

```zsh
vde_require_ssh() {
    # 1. Verify binary availability
    if ! command -v ssh >/dev/null 2>&1; then
        return ${VDE_ERR_NOT_FOUND:-3}
    fi
    # 2. Verify identity existence (The Transversal Bridge)
    local vde_key="${HOME}/.ssh/vde/vde_student"
    if [[ ! -f "${vde_key}" ]]; then
        # Log warning but don't fail, as some commands might not need the identity yet
        vde_log_warning "VDE identity not found at ${vde_key}"
    fi
    _VDE_SSH_LOADED=1
    return ${VDE_SUCCESS:-0}
}
```

- [ ] **Step 2: Harden vde_require_docker**
    - Replace the current stub with a fast physical probe (`docker info`).

```zsh
vde_require_docker() {
    # 1. Verify binary
    if ! command -v docker >/dev/null 2>&1; then
        return ${VDE_ERR_NOT_FOUND:-3}
    fi
    # 2. Verify daemon responsiveness (The World-Forge)
    # We use 'docker info' as it is the canonical probe for daemon health
    if ! docker info >/dev/null 2>&1; then
        vde_log_error "Docker daemon is not responsive. Is it running?"
        return ${VDE_ERR_GENERAL:-1}
    fi
    _VDE_DOCKER_LOADED=1
    return ${VDE_SUCCESS:-0}
}
```

---

### Task 2: Audit and Expand Spoke Hydration

**Files:**
- Audit: `scripts/setup/`
- Target: `MEAN`, `LAMP`, `ELK` stacks.

- [ ] **Step 1: Audit existing multi-VM scripts**
    - Identify gaps in current coordination logic for clusters.
- [ ] **Step 2: Harden vde cluster orchestration**
    - Ensure `bin/vde-cluster` (or equivalent) uses the hardened `vde_run` and `vm-lock` mechanisms.

---

### Task 3: Audit and Finalize

- [ ] **Step 1: Run Sovereign Audit**
    - Command: `bin/vde-enforce-uap.zsh`
- [ ] **Step 2: Run Proof of Life**
    - Command: `python3 -m behave tests/features/core-infrastructure/proof-of-life-the-contract.feature`
- [ ] **Step 3: Request Code Review**
    - Dispatch `code-reviewer`.
- [ ] **Step 4: Commit and Link**
    - PR body includes evidence of hardened requirement checks.
