# VDE Project Memory

**Last Updated:** 2026-03-19T18:45:00-04:00
**Session Focus:** Test infrastructure fixes, rebuild tag configuration, port registry cleanup

---

## Current Status

### Completed This Session

1. **SSH Agent Setup Fixed**:
   - `tests/setup-ssh-agent.zsh` - Uses `${0:a:h:h}` for portable VDE_ROOT_DIR
   - `tests/run-full-test-suite.zsh` - Sets VDE_ROOT_DIR before sourcing SSH agent

2. **Port Registry Cleanup Fixed**:
   - `cleanup_port_registry()` updated to handle directory architecture (`.cache/port-registry/*.port`)
   - `tests/unit/test_test_utilities.py` updated to match actual directory structure

3. **cleanup_docker_volumes() Added**:
   - Implemented in `test_utilities.py` to match test expectations

4. **Rebuild Tag Created and Configured**:
   - `behave.ini` updated: `tags = core-suite and not wip and not rebuild`
   - New file: `core-infrastructure/vm-rebuild.feature` with 3 rebuild scenarios
   - `@rebuild` tag applied to `vm-full-lifecycle.feature`
   - Removed duplicate rebuild scenarios from `docker-operations.feature` and `vm-lifecycle.feature`

5. **documented_workflow_steps.py Fixed**:
   - Added `sys.path.insert` for proper vm_common import

### Test Status

| Test Suite | Status | Details |
|------------|--------|---------|
| Docker-free tests | ✅ PASSING | 10 scenarios, ~8s |
| Unit tests | ✅ PASSING | 72/72 pytest passed |
| Integration tests | ✅ PASSING | ~60s |
| Core-infrastructure | ⚠️ IN PROGRESS | Many undefined step implementations needed |

### Fast Test Commands
```bash
# Docker-free tests (~8s)
python3 -m behave tests/features/docker-free/ -q

# Unit tests (~33s)
python3 -m pytest tests/unit/ -q

# Integration tests (~60s)
make test-integration

# Core-infrastructure without rebuild (~2min)
python3 -m behave core-infrastructure/ --tags="~@rebuild" -q

# Include rebuild tests (5-15min each)
python3 -m behave core-infrastructure/ --tags="core-suite and not wip"
```

---

## Key Files Reference

- **Step Definitions:** `tests/features/steps/*.py`
- **Feature Files:** `tests/features/core-infrastructure/*.feature`
- **Helpers:** `tests/features/steps/vm_common.py`, `tests/features/steps/ssh_helpers.py`
- **Config:** `behave.ini`, `tests/features/steps/config.py`

---

## Fake Test Prohibition Reminder

**CRITICAL**: All step definitions must:
- Perform REAL verification (file checks, command execution, container state)
- NO `assert True` without real checks
- NO `or True` patterns
- NO `pass` statements
- NO placeholder implementations

---

## Portability Architecture

**Design Principle:**
- `VDE_ROOT_DIR` - wherever user cloned the project (portable)
- `VDE_SSH_DIR="$HOME/.ssh/vde"` - SSH operations (always in $HOME)

**Path Usage:**
- Project configs use relative paths from `VDE_ROOT_DIR`
- SSH config uses `~/.ssh/vde/` (tilde, portable)
- Docker compose uses relative paths (`../../../`)

---

## Known Issues / Remediation Work In Progress

### Undefined Step Implementations Needed
Multiple feature files have scenarios with undefined step definitions that need implementations:
- `collaboration.feature` - 7+ undefined steps
- `documented-workflows.feature` - multiple undefined steps
- Other promoted features

**Approach:** Implement REAL step definitions that call actual vde commands and verify actual results.

---

## Session History

### Session 37 (2026-03-18) - SSH Test Remediation
- Fixed ssh_helpers.py for VDE isolated SSH agent
- Fixed ssh-agent-forwarding-vm-to-vm.feature contradictory Background
- Added missing WHEN steps for VM-to-VM SSH

### Session 38 (2026-03-19) - Test Infrastructure
- Fixed VDE_ROOT_DIR portability
- Fixed port registry directory handling
- Created rebuild tag and configuration
- Running tests to identify undefined steps

