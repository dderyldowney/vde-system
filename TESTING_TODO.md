# VDE Testing TODO

**Last Updated:** 2026-01-16

---

## Remaining Work

### Highest Priority ⚠️

#### 1. SSH Configuration BDD Scenarios

**Status:** IN PROGRESS - 0/27 scenarios passing, 117 undefined steps

**Feature File:** `tests/features/ssh-configuration.feature`

**Why This Is Critical:**
- SSH configuration is the foundation for all VM access
- Without proper SSH config, users cannot connect to their VMs
- This feature is tested before any other SSH functionality

**Scenarios (27 total):**
- SSH config file creation and management
- Host entry generation
- Port configuration
- Identity file selection
- Config backup and restoration
- Multiple VM configuration
- Config validation
- Custom settings preservation

**Action Required:**
- Implement 117 undefined step definitions in `tests/features/steps/ssh_steps.py`
- Verify all 27 scenarios pass

---

### High Priority

#### 2. SSH Agent Automatic Setup BDD Scenarios ✅ COMPLETE

**Status:** 12/12 scenarios passing

**Feature File:** `tests/features/ssh-agent-automatic-setup.feature`

**Completed:** All scenarios working

---

#### 3. SSH Agent Forwarding (VM-to-VM)

**Status:** Not started - 86 undefined steps

**Feature File:** `tests/features/ssh-agent-forwarding-vm-to-vm.feature`

---

#### 4. SSH Agent External Git Operations

**Status:** Not started - 92 undefined steps

**Feature File:** `tests/features/ssh-agent-external-git-operations.feature`

---

#### 5. SSH Agent VM-to-Host Communication

**Status:** Not started - 73 undefined steps

**Feature File:** `tests/features/ssh-agent-vm-to-host-communication.feature`

---

### Medium Priority

#### 6. SSH and Remote Access

**Status:** Not started - 46 undefined steps

**Feature File:** `tests/features/ssh-and-remote-access.feature`

---

#### 7. Investigate BDD Test Failures

**Status:** Tests have failures that need investigation

**Common Failure Types:**
- Docker container timing issues (VMs not starting fast enough)
- Missing preconditions (VMs not created before being started)
- Assertion mismatches
- Steps that require real environment (Docker host, SSH keys)

**Action Items:**
- Distinguish between expected failures (test environment limitations) and actual bugs
- Add proper setup/teardown for container lifecycle where needed
- Implement better waiting mechanisms for Docker operations
- Ensure test isolation (clean state between scenarios)

---

#### 8. Undefined BDD Steps

**Status:** ~467 undefined steps remaining (79% reduction from original 2248)

**SSH Steps:** 414 undefined steps across 5 SSH features
**Other Steps:** ~53 undefined steps (template rendering, VM state awareness, etc.)

---

### Low Priority

#### 9. Fuzzy Matching for Typo Handling

**Status:** Enhancement - parser cannot handle typos in user input

**Dependencies:** ✅ `thefuzz` (v0.22.1) installed

**Implementation Plan:** See [FUZZY_LOGIC_TODO.md](./FUZZY_LOGIC_TODO.md)

---

## SSH Feature Files Summary

| File | Scenarios | Passing | Status | Undefined Steps |
|------|-----------|----------|--------|-----------------|
| ✅ `ssh-agent-automatic-setup.feature` | 12 | 12/12 | COMPLETE | 0 |
| ⚠️ `ssh-configuration.feature` | 27 | 0/27 | IN PROGRESS | 117 |
| `ssh-agent-forwarding-vm-to-vm.feature` | 10 | 0/10 | Not started | 86 |
| `ssh-agent-external-git-operations.feature` | 10 | 0/10 | Not started | 92 |
| `ssh-agent-vm-to-host-communication.feature` | 12 | 0/12 | Not started | 73 |
| `ssh-and-remote-access.feature` | 12 | 0/12 | Not started | 46 |

**Total SSH:** 1/83 scenarios passing, 414 undefined steps

---

## Running Tests

### SSH Configuration Tests
```bash
cd tests
behave features/ssh-configuration.feature
```

### All SSH Tests
```bash
cd tests
behave features/*ssh*.feature
```

### Shell Tests
```bash
cd tests
./run-all-tests.sh
```

---

## Quick Reference

### Test File Locations
- **SSH step definitions:** `tests/features/steps/ssh_steps.py`
- **VDE test helpers:** `tests/features/steps/vde_test_helpers.py`
- **BDD features:** `tests/features/*.feature`

### Current Test Status
```
Shell Tests:     108 passed, 0 failed ✅
SSH Agent Auto:  12/12 scenarios passing ✅
SSH Config:      0/27 scenarios (414 undefined steps total)
```
