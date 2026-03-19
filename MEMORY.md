# VDE Project Memory

**Last Updated:** 2026-03-18T14:30:00-04:00
**Session Focus:** Complete remediation of SSH-related feature tests

---

## Current Status

### Completed This Session

1. **ssh-agent-automatic-setup.feature**: ✅ ALL PASSING
   - 12 scenarios passed, 75 steps passed
   - All step definitions working correctly

2. **ssh-agent-forwarding-vm-to-vm.feature**: ⚠️ Partial (2/10 scenarios)
   - Step definitions complete (no undefined steps)
   - Remaining failures are functional (VMs not running, SSH connections)
   - Not step definition issues

3. **Fixed ssh_helpers.py** (Critical Fix):
   - Updated `ssh_agent_is_running()` to detect VDE's isolated SSH agent
   - Updated `ssh_agent_has_keys()` to use VDE agent environment
   - Reads `~/.ssh/vde/agent_env` for socket and PID

4. **Fixed ssh-agent-forwarding-vm-to-vm.feature**:
   - Removed contradictory Background section
   - Background required SSH agent running but first scenario required it NOT running
   - Each scenario now has explicit preconditions

5. **Unified Step Definitions**:
   - Removed duplicate decorators across files
   - Added aliases to existing steps instead of creating new ones
   - Files cleaned: ssh_vm_to_vm_steps.py, ssh_config_steps.py, ssh_git_steps.py

6. **Added Missing WHEN Steps** (ssh_vm_to_vm_steps.py):
   - `I create a file in the Python VM`
   - `I run "scp vde-go:/tmp/file ." from the Python VM`
   - `I run "ssh vde-rust pwd" from the Python VM`
   - `I SSH from one VM to another`
   - `I SSH from VM1 to VM2` (and VM2 to VM3, etc.)

---

## Files Modified This Session

| File | Changes |
|------|---------|
| `tests/features/steps/ssh_helpers.py` | Fixed agent detection for VDE isolation |
| `tests/features/steps/ssh_vm_to_vm_steps.py` | Unified decorators, added missing steps |
| `tests/features/steps/ssh_config_steps.py` | Added decorators for unified step patterns |
| `tests/features/steps/vm_lifecycle_steps.py` | Added SSH setup before VM creation |
| `tests/features/steps/installation_steps.py` | Added SSH setup before first VM creation |
| `tests/features/docker-required/ssh-agent-forwarding-vm-to-vm.feature` | Fixed contradictory Background |

---

## Test Status

### ssh-agent-automatic-setup.feature
- **Status**: ✅ PASSING
- **Scenarios**: 12/12 passed
- **Steps**: 75/75 passed

### ssh-agent-forwarding-vm-to-vm.feature
- **Status**: ⚠️ Partial (functional issues, not step issues)
- **Scenarios**: 2/10 passed
- **Steps**: 74 passed, 8 failed, 19 skipped
- **Note**: Failures are due to VMs not running during test execution

---

## Known Issues

### Functional Issues (Not Step Definitions)
1. VM-to-VM SSH tests require running VMs
2. Some tests expect `context.ssh_connection_success` to be set
3. PostgreSQL and Redis VM tests need service VMs running

### Remaining Work
1. Run full test suite: `./tests/run-full-test-suite.zsh`
2. Investigate functional failures in vm-to-vm tests
3. Verify other docker-required features

---

## Next Session Actions

1. Run `./tests/run-full-test-suite.zsh`
2. Review functional failures in vm-to-vm tests
3. Check other SSH-related features if needed

---

## Key Files Reference

- **Step Definitions:** `tests/features/steps/*.py`
- **Feature Files:** `tests/features/docker-required/*.feature`
- **Helpers:** `tests/features/steps/vm_common.py`, `tests/features/steps/ssh_helpers.py`
- **Config:** `tests/features/steps/config.py`

---

## Fake Test Prohibition Reminder

**CRITICAL**: All step definitions must:
- Perform REAL verification (file checks, command execution, container state)
- NO `assert True` without real checks
- NO `or True` patterns
- NO `pass` statements
- NO placeholder implementations

---

## Lesson Learned: VM Startup in Step Definitions (2026-03-19)

**Problem**: Step definitions like `Given I am connected to a VM` were FAKE TESTS - they only checked if a VM was running but did NOT start one. This caused cascading failures in isolated scenario runs.

**Bad Pattern** (FAKE TEST):
```python
@given("I am connected to a VM")
def step_connected_via_ssh(context):
    running = docker_ps()
    if running:
        context.ssh_connected = True
    else:
        context.ssh_connected = False  # FAILS LATER - no real action taken
```

**Good Pattern** (REAL TEST):
```python
@given("I am connected to a VM")
def step_connected_via_ssh(context):
    running = docker_ps()
    if not running:
        run_vde_command("start python", context=context)
        wait_for_container("python", timeout=120)
    running = docker_ps()
    assert running, "No VMs running - failed to start python VM"
    context.ssh_connected = True
```

**Rule**: Any step that implies a VM is running ("I am connected to a VM", "I have a running VM", etc.) MUST actually start the VM if none is running.

**Files Fixed**:
- `tests/features/steps/ssh_remote_access_steps.py:34` - Added VM startup

---

## Cache Corruption Fix (2026-03-19)

**Root Cause:** `vde-displaytest` has display name "Go Language" with a space. The cache builder was creating `VM_ALIAS_MAP[go language]=vde-displaytest` which breaks zsh associative array syntax.

**Fix Applied:** lib/vm-common line 427 - added space stripping for display names:
```zsh
d_low="${d_low//[[:space:]]/}"
```

**Files Modified:**
- `lib/vm-common` - Fixed display name space stripping

**Verification:** `./bin/vde start python` now returns exit 0 (previously returned exit 1 due to cache error).

---

## SSH Config Sync Issue (2026-03-19)

**Problem:** `~/.ssh/vde/config` had absolute paths (`/Users/dderyldowney/.ssh/vde/`) while `configs/ssh/config` (authoritative) had tilde paths (`~/.ssh/vde/`). SCP uses `-F` flag but step definitions need correct paths in config.

**Rule:** Always use `configs/ssh/config` as authoritative. Copy to `~/.ssh/vde/config`:
```bash
cp configs/ssh/config ~/.ssh/vde/config
```

**Files Needing SSH Config Path Fix:**
- `tests/features/steps/ssh_remote_access_steps.py` - scp command now uses `-F` flag with correct config path

---

## Portability Architecture (2026-03-19)

**Design Principle:**
- `VDE_ROOT_DIR` - wherever user cloned the project (portable)
- `VDE_SSH_DIR="$HOME/.ssh/vde"` - SSH operations (always in $HOME)

**Path Usage:**
- Project configs use relative paths from `VDE_ROOT_DIR`
- SSH config uses `~/.ssh/vde/` (tilde, portable)
- Docker compose uses relative paths (`../../../`)

**SSH Config Synchronization:**
- Authoritative source: `configs/ssh/config`
- Installed location: `~/.ssh/vde/config`
- Always use `cp configs/ssh/config ~/.ssh/vde/config` to sync
- Never edit `~/.ssh/vde/config` manually - it is managed by `generate-all-configs`

**Important:** When `generate-all-configs` regenerates configs, it updates `configs/ssh/config` but does NOT automatically copy to `~/.ssh/vde/config`. User must manually sync or run `vde-init`.
