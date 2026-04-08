# VDE 2.0.6 Concurrency and Port Registration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix systemic concurrency and port registration issues in VDE 2.0.6.

**Architecture:** 
1. Enhance `get_vm_ssh_port()` in `lib/vde-docker` to self-heal the port registry from `docker-compose.yml`.
2. Move port allocation in `bin/add-vm-type` inside the global config lock to prevent race conditions.
3. Validate with a clean sweep and stress test.

**Tech Stack:** ZSH, Docker, Docker Compose

---

### Task 1: Update `lib/vde-docker` for Port Registry Self-Healing

**Files:**
- Modify: `lib/vde-docker`

- [ ] **Step 1: Update `get_vm_ssh_port()` logic**

Update the `get_vm_ssh_port()` function in `lib/vde-docker` to repopulate the registry if the port is found in `docker-compose.yml` but missing from the registry.

```zsh
get_vm_ssh_port() {
    local vm_name="${1}"

    # 1. Try registry first (fast)
    if [[ -d "${VDE_PORT_REGISTRY}" ]]; then
        local registry_file="${VDE_PORT_REGISTRY}/${vm_name}.port"
        if [[ -f "${registry_file}" ]]; then
            cat "${registry_file}"
            return ${VDE_SUCCESS}
        fi
    fi

    # 2. Try docker-compose.yml (source of truth)
    local compose_file
    compose_file=$(get_compose_file "${vm_name}")
    if [[ -f "${compose_file}" ]]; then
        local port
        port=$(grep -oE '[0-9]+:22' "${compose_file}" | head -1 | cut -d':' -f1)
        if [[ -n "${port}" ]]; then
            # SELF-HEAL: Repopulate registry if found in compose but missing in registry
            # We use allocate_ssh_port as it also handles the numeric lock file
            allocate_ssh_port "${vm_name}" "${port}" >/dev/null 2>&1
            echo "${port}"
            return ${VDE_SUCCESS}
        fi
    fi

    return ${VDE_ERR_NOT_FOUND}
}
```

- [ ] **Step 2: Verify the change**
I'll manually verify this by removing a `.port` file for an existing VM and calling `get_vm_ssh_port`.

### Task 2: Update `bin/add-vm-type` for Atomic Port Allocation

**Files:**
- Modify: `bin/add-vm-type`

- [ ] **Step 1: Move port allocation inside the lock block**

Move the `SSH_PORT` auto-allocation logic inside the `global-config.lock` acquisition block.

Old location (around line 135):
```zsh
if [[ -z "${SSH_PORT}" ]]; then
    log_info "No SSH port specified, auto-allocating..."
    SSH_PORT=$(find_available_ssh_port)
    ...
fi
```

New location (inside the lock block, before validation):
```zsh
# -----------------------
# Atomic Registry Update
# -----------------------
log_info "Updating Pure Beskar registry..."
local global_lock="${VDE_LOCKS_DIR}/global-config.lock"
acquire_lock "${global_lock}" 60 || exit 1

{
    # AUTO-ALLOCATE PORT (Inside Lock)
    if [[ -z "${SSH_PORT}" ]]; then
        log_info "No SSH port specified, auto-allocating inside lock..."
        SSH_PORT=$(find_available_ssh_port)
        if [[ $? -ne 0 ]]; then
            log_error "Failed to auto-allocate port"
            exit ${VDE_ERR_GENERAL}
        fi
        log_success "Allocated port: ${SSH_PORT}"
    fi

    # TRIPLE-GATE VALIDATION (Inside Lock)
    ...
} always {
    release_lock "${global_lock}"
}
```

### Task 3: Final Verification Strike

- [ ] **Step 1: Perform Clean Sweep**
Run the following commands:
```bash
bin/shutdown-all all -f
rm -rf .cache/port-registry/*
rm -rf .locks/vms/*
```

- [ ] **Step 2: Run Concurrency Stress Test**
Run:
```bash
bin/vde-enforce-uap.zsh behave tests/features/core-infrastructure/concurrency-stress.feature
```

- [ ] **Step 3: Report Outcome**
Confirm the test results.
