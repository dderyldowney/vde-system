# VDE Testing TODO

**Last Updated:** 2026-01-16

---

## Remaining Work

### Highest Priority ⚠️

#### 1. SSH Agent Forwarding (VM-to-VM)

**Status:** Not started - 86 undefined steps

**Feature File:** `tests/features/ssh-agent-forwarding-vm-to-vm.feature`

**Why This Is Critical:**
- VM-to-VM SSH communication is a core VDE feature
- Enables containers to communicate with each other
- Foundation for distributed development workflows

**Action Required:**
- Implement 86 undefined step definitions

---

### High Priority

#### 2. SSH Agent External Git Operations

**Status:** Not started - 92 undefined steps

**Feature File:** `tests/features/ssh-agent-external-git-operations.feature`

---

#### 3. SSH Agent VM-to-Host Communication

**Status:** Not started - 73 undefined steps

**Feature File:** `tests/features/ssh-agent-vm-to-host-communication.feature`

---

### Completed ✅

#### SSH Agent Automatic Setup BDD Scenarios ✅ COMPLETE

**Status:** 12/12 scenarios passing

**Feature File:** `tests/features/ssh-agent-automatic-setup.feature`

---

#### SSH Configuration BDD Scenarios ✅ COMPLETE

**Status:** 23/23 scenarios passing (27 total - 4 require @requires-docker-ssh)

**Feature File:** `tests/features/ssh-configuration.feature`

**Completed:**
- All 117 undefined step definitions implemented
- 23 scenarios passing (run without Docker)
- 4 scenarios tagged with `@requires-docker-ssh` for real environment testing
- All SSH config merge, backup, and validation scenarios covered

---

### Medium Priority

#### 4. SSH and Remote Access

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

#### 5. Undefined BDD Steps

**Status:** ~297 undefined steps remaining (87% reduction from original 2248)

**SSH Steps:** 297 undefined steps across 4 SSH features (ssh-agent-automatic-setup and ssh-configuration are complete)
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
| ✅ `ssh-configuration.feature` | 27 | 23/23 | COMPLETE | 0 |
| `ssh-agent-forwarding-vm-to-vm.feature` | 10 | 0/10 | Not started | 86 |
| `ssh-agent-external-git-operations.feature` | 10 | 0/10 | Not started | 92 |
| `ssh-agent-vm-to-host-communication.feature` | 12 | 0/12 | Not started | 73 |
| `ssh-and-remote-access.feature` | 12 | 0/12 | Not started | 46 |

**Total SSH:** 35/35 scenarios passing (excluding @requires-docker-ssh), 297 undefined steps remaining

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
SSH Config:      23/23 scenarios passing ✅ (4 require @requires-docker-ssh)
```
