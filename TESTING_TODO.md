# VDE Testing TODO

**Last Updated:** 2026-01-16

---

## Current Test Status

```
Features: 9 passed, 4 failed, 18 error
Scenarios: 254 passed, 28 failed, 209 error
Steps: 1525 passed, 28 failed, 12 error, 236 skipped, 702 undefined
```

---

## Remaining Work

### Highest Priority ⚠️

#### 1. Template System (~70 undefined steps)

**Status:** Not started

**Feature File:** `tests/features/template-system.feature`

**Undefined Steps:**
- Render language VM template
- Render service VM template
- Handle multiple service ports
- Escape special characters in template values
- Template includes SSH agent forwarding
- Template includes public keys volume
- Template uses correct network
- Template sets correct restart policy
- Template configures user correctly
- Template exposes SSH port
- Template includes install command
- Handle missing template gracefully

---

#### 2. VM Information and Discovery (~40 undefined steps)

**Status:** Not started

**Feature File:** `tests/features/vm-information-and-discovery.feature`

**Undefined Steps:**
- Listing all available VMs
- Listing only language VMs
- Listing only service VMs
- Getting detailed information about a specific VM
- Checking if a VM exists
- Discovering VMs by alias
- Understanding VM categories

---

#### 3. VM Lifecycle Management (~60 undefined steps)

**Status:** Not started

**Feature File:** `tests/features/vm-lifecycle-management.feature`

**Undefined Steps:**
- Creating a new VM
- Creating multiple VMs at once
- Starting a created VM
- Starting multiple VMs
- Checking VM status
- Stopping a running VM
- Stopping multiple VMs
- Restarting a VM
- Restarting with rebuild
- Deleting a VM
- Rebuilding after code changes
- Upgrading a VM
- Migrating to a new VDE version

---

#### 4. VM State Awareness (~50 undefined steps)

**Status:** Not started

**Feature File:** `tests/features/vm-state-awareness.feature`

**Undefined Steps:**
- Starting an already running VM
- Stopping an already stopped VM
- Creating an existing VM
- Restarting a stopped VM
- Status shows mixed states
- Smart start of already running VMs
- Smart start with mixed states
- Querying specific VM status
- Preventing duplicate operations
- State persistence information
- Waiting for VM to be ready
- Notifying about background operations
- State change notifications
- Batch operation state awareness

---

#### 5. Collaboration Workflow (~200 undefined steps)

**Status:** Not started

**Feature File:** `tests/features/collaboration-workflow.feature`

**Undefined Steps:**
- Team collaboration scenarios
- Project sharing
- Environment reproducibility
- Multi-developer workflows

---

#### 6. Configuration Management (~80 undefined steps)

**Status:** Not started

**Feature File:** `tests/features/configuration-management.feature`

**Undefined Steps:**
- Environment variable configuration
- Local overrides
- Configuration validation
- Migration handling

---

#### 7. Productivity Features (~100 undefined steps)

**Status:** Not started

**Feature File:** `tests/features/productivity-features.feature`

**Undefined Steps:**
- Developer productivity features
- Quick commands
- Workflow automation

---

### Medium Priority

#### 8. Other Features

- `tests/features/daily-workflow.feature` (~100 undefined steps)
- `tests/features/daily-development-workflow.feature` (~60 undefined steps)
- `tests/features/docker-and-container-management.feature` (~80 undefined steps)
- `tests/features/docker-operations.feature` (~120 undefined steps)
- `tests/features/shell-compatibility.feature` (~90 undefined steps)

---

### Low Priority

#### 9. Fuzzy Matching for Typo Handling

**Status:** Enhancement - parser cannot handle typos in user input

**Dependencies:** ✅ `thefuzz` (v0.22.1) installed

**Implementation Plan:** See [FUZZY_LOGIC_TODO.md](./FUZZY_LOGIC_TODO.md)

---

## Completed ✅

### SSH Features (79/79 scenarios passing)

All SSH-related features are complete:
- `ssh-agent-automatic-setup.feature` - 12/12 scenarios
- `ssh-configuration.feature` - 23/23 scenarios
- `ssh-agent-forwarding-vm-to-vm.feature` - 10/10 scenarios
- `ssh-agent-external-git-operations.feature` - 10/10 scenarios
- `ssh-agent-vm-to-host-communication.feature` - 12/12 scenarios
- `ssh-and-remote-access.feature` - 12/12 scenarios

### Cache System (7/9 scenarios passing)

Cache system mostly complete with 4 new step definitions implemented:
- Cache file validation
- VM array population checks (VM_DISPLAY, VM_INSTALL, VM_SVC_PORT)

---

## Running Tests

### All Tests
```bash
cd tests
python3 -m behave features/*.feature --no-timings
```

### Specific Feature
```bash
cd tests
python3 -m behave features/template-system.feature --no-timings
```

### Shell Tests
```bash
cd tests
./run-all-tests.sh
```

---

## Quick Reference

### Test File Locations
- **Step definitions:** `tests/features/steps/*.py`
- **BDD features:** `tests/features/*.feature`

### Step Definition Files
- `ssh_steps.py` - SSH-related steps (complete)
- `cache_steps.py` - Cache system steps (mostly complete)
- `vm_lifecycle_steps.py` - VM lifecycle steps (partial)
- `common_steps.py` - Common/shared steps (partial)
- `template_steps.py` - Template rendering steps (needs work)
