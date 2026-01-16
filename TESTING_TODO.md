# VDE Testing TODO

**Last Updated:** 2026-01-16

---

## Remaining Work

### Highest Priority ⚠️

#### 1. SSH Agent External Git Operations

**Status:** Not started - 92 undefined steps

**Feature File:** `tests/features/ssh-agent-external-git-operations.feature`

**Why This Is Critical:**
- Git operations from VMs using host SSH keys is a core feature
- Enables seamless GitHub/GitLab workflow from within containers
- Essential for modern development practices

**Action Required:**
- Implement 92 undefined step definitions

---

### High Priority

#### 2. SSH Agent VM-to-Host Communication

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

#### SSH Agent Forwarding (VM-to-VM) ✅ COMPLETE

**Status:** 10/10 scenarios passing

**Feature File:** `tests/features/ssh-agent-forwarding-vm-to-vm.feature`

**Completed:**
- 70+ step definitions implemented
- All 10 scenarios passing
- Tests cover: VM-to-VM SSH, SCP between VMs, agent forwarding
- Key features tested: host key usage, no password required, private keys remain on host

---

### Medium Priority

#### 3. SSH and Remote Access

**Status:** Not started - 46 undefined steps

**Feature File:** `tests/features/ssh-and-remote-access.feature`

---

#### 4. Undefined BDD Steps

**Status:** ~211 undefined steps remaining (91% reduction from original 2248)

**SSH Steps:** 211 undefined steps across 3 SSH features (ssh-agent-automatic-setup, ssh-configuration, and ssh-agent-forwarding-vm-to-vm are complete)
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
| ✅ `ssh-agent-forwarding-vm-to-vm.feature` | 10 | 10/10 | COMPLETE | 0 |
| `ssh-agent-external-git-operations.feature` | 10 | 0/10 | Not started | 92 |
| `ssh-agent-vm-to-host-communication.feature` | 12 | 0/12 | Not started | 73 |
| `ssh-and-remote-access.feature` | 12 | 0/12 | Not started | 46 |

**Total SSH:** 45/45 scenarios passing (excluding @requires-docker-ssh), 211 undefined steps remaining

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
SSH Agent VM-to-VM: 10/10 scenarios passing ✅
```
