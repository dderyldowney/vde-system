# VDE Daily Workflow Improvements Plan

## Summary

This plan addresses issues identified during VDE daily workflow testing. Four issues were found, with two requiring immediate priority.

## Test Results (2026-01-31)

| Step | Command | Status | Notes |
|------|---------|--------|-------|
| Morning Setup | `vde start python postgres redis` | ✅ PASS | VMs started successfully |
| Check Status | `vde status` | ⚠️ PARTIAL | Doesn't show running VMs |
| SSH (Python) | `vde ssh python` | ✅ PASS | Connected as devuser |
| SSH (Services) | `vde ssh postgres` | ❌ FAIL | Missing SSH config entries |
| Evening Cleanup | `vde stop all` | ✅ PASS | All VMs stopped cleanly |

## Issues Identified

### Priority 1: `vde status` doesn't show running VMs - ✅ DONE

**Status:** Already implemented in `scripts/list-vms` (lines 95-109)

**Verification:**
```
$ ./scripts/list-vms
Predefined VM Types:

Language VMs:
  asm                  Assembler [RUNNING]
  c                    C [RUNNING]
  cpp                  C++ [RUNNING]
```

---

### Priority 2: Service VMs lack SSH config entries

**Severity:** MEDIUM  
**User Impact:** Cannot use `vde ssh postgres` or `vde ssh redis`

**Current Behavior:**
```bash
$ vde ssh postgres
# Error: Could not resolve hostname postgres
```

**Root Cause:** SSH config (`~/.ssh/vde/config`) only contains entries for language VMs (python-dev, rust-dev, etc.) on port 2200. Service VMs (postgres, redis, etc.) on ports 2400+ are missing.

**Files to Modify:**
- `scripts/lib/vm-common` - `merge_ssh_config_entry()` function
- `scripts/create-virtual-for` - Add SSH config generation for services

**Implementation:**
```zsh
# In merge_ssh_config_entry(), add handling for service VMs
if [[ "$vm_type" == "service" ]]; then
    # Service VMs use name directly, not <name>-dev
    ssh_host="$vm_name"
    ssh_port=$VDE_SVC_PORT_START  # 2400+
else
    # Language VMs use <name>-dev
    ssh_host="${vm_name}-dev"
    ssh_port=$VDE_LANG_PORT_START  # 2200+
fi
```

---

### Priority 3: Debug output floods stdout (Deferred)

**Severity:** LOW  
**Current:** Debug messages print during normal operation  
**Proposed:** Add `--quiet` flag or suppress by default

---

### Priority 4: `timeout` command unavailable (Deferred)

**Severity:** LOW  
**System:** `/bin/sh` doesn't have `timeout` on macOS  
**Proposed:** Document as system requirement or use alternative

---

## Implementation Order

### Phase 1: High Priority (User-Facing Bugs)

1. **Fix `vde status` running display**
   - Modify `scripts/list-vms` to check `is_vm_running()`
   - Test with `vde start python postgres` → `vde status`
   - Verify "[RUNNING]" appears for active VMs

2. **Add service VM SSH config**
   - Modify `merge_ssh_config_entry()` in `scripts/lib/vm-common`
   - Add SSH config entry during `vde create` for services
   - Test with `vde ssh postgres`

### Phase 2: Quality of Life (Deferred)

3. Add `--quiet` flag to suppress debug output
4. Document `timeout` requirement or provide fallback

---

## MCP Services to Use

| MCP Service | Purpose |
|-------------|---------|
| `context7` | Check SSH config best practices, documentation patterns |
| `github` | Search for related issues, review code patterns |
| `fetch` | Get latest Docker/SSH documentation |

---

## Testing Plan

### Test Priority 1 Fix

```bash
# Clean state
./scripts/vde stop all

# Start VMs
./scripts/vde start python postgres redis

# Check status (should show RUNNING)
./scripts/vde status

# Verify output contains "[RUNNING]"
```

### Test Priority 2 Fix

```bash
# Create service VM if needed
./scripts/vde create postgres

# SSH to service (should work)
vde ssh postgres whoami
# Expected: devuser

# SSH to Redis
vde ssh redis whoami
# Expected: devuser
```

---

## Files to Modify

| File | Change | Priority |
|------|--------|----------|
| `scripts/list-vms` | Add running status check | P1 |
| `scripts/lib/vm-common` | Add service VM SSH config | P1 |
| `scripts/create-virtual-for` | Generate SSH for services | P1 |

---

## Success Criteria

- ✅ `vde status` shows "[RUNNING]" for active VMs
- ✅ `vde ssh postgres` connects successfully
- ✅ `vde ssh redis` connects successfully
- ✅ No regression in existing functionality

---

**Created:** 2026-01-31  
**Status:** Plan ready for implementation
