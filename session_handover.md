# Session Handover - VDE Streamlining

**Mission:** Reduce VDE to minimal code that accomplishes goals + validate with tests

---

## Latest: VM Lifecycle Complete (2026-03-24)

### ✅ vm-lifecycle.feature Updated

- Rewrote feature to match VDE's actual workflow
- Focus: start/stop/restart/remove VMs (not config creation)
- VDE auto-generates configs from vm-types.conf on first use

### Step Definitions Added (vm_rebuild_steps.py)
- `VM "{vm_name}" is not running`
- `VM "{vm_name}" is not created`
- `VM "{vm_name}" is not known`
- `vde start/stop/restart/remove` commands
- `Docker image should be built/rebuilt` assertions

### Fast Tests: 212 scenarios passing
- parser: 46 ✅
- critical-infrastructure: 51 ✅
- ssh-configuration: 33 ✅
- error-path: 7 ✅
- Plus 75 more...

---

## Running Tests

```bash
# Fast tests (no Docker)
python3 -m behave tests/features/core-infrastructure/parser.feature -q

# VM lifecycle (requires Docker, long timeout)
cd tests && python3 -m behave features/core-infrastructure/vm-lifecycle.feature --tags=@vm-lifecycle
```

---

## Running Tests

```bash
# Fast tests (no Docker)
python3 -m behave tests/features/core-infrastructure/parser.feature
python3 -m behave tests/features/core-infrastructure/critical-infrastructure.feature

# @vm-rebuild (requires Docker, slow)
python3 -m behave tests/features/core-infrastructure/vm-rebuild.feature --tags=@vm-rebuild

# All tests
python3 -m behave tests/features/core-infrastructure
```
