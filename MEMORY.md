# VDE Project Memory

## Testing Guidelines (MANDATORY)

**NEVER run full test suite during debugging.** Only run when explicitly needed.

### Efficient Testing
- Isolate: Run specific feature/unit test, not everything
- Verify minimally: `zsh tests/unit/vde-X.test.zsh` or `behave tests/features/core-infrastructure/X.feature`
- Full suite: ONLY after all fixes complete + user requests it

### Examples
| Context | Command |
|---------|---------|
| Fix zsh assoc array | `zsh tests/unit/vde-shell-compat.test.zsh` |
| Fix cache test | `behave tests/features/core-infrastructure/cache-system.feature` |
| Verify all | `./tests/run-full-test-suite.zsh` |

---

## Current State (2026-03-16 Session 34)

**Status: ✅ Fake Test Remediation COMPLETE**

**Test Suite Status:**
- Docker-free BDD: ✅ PASS (10 scenarios, 34 steps)
- Unit Tests: ✅ PASS (~108 tests)
- Integration Tests: ✅ PASS
- Core Infrastructure BDD: ⚠️ CRASHED (empty log - needs investigation)
- Docker-required BDD: ❌ FAIL (15 failures, 23 undefined steps)
- Postgres OOM: ✅ FIXED (no OOM detected, memory within 1GiB limit)

### Remediation Completed

| Task | Count | Status |
|------|-------|--------|
| TASK 1: Delete unused steps | 6 | ✅ DONE |
| TASK 2: Fix `assert True` violations | 7 | ✅ DONE |
| TASK 3: Implement missing WHEN/THEN steps | 2 | ✅ DONE |
| TASK 4: Implement missing step definition | 1 | ✅ DONE |
| TASK 5: Fix tautological THEN steps | 21 | ✅ DONE |
| TASK 6: Fix `or True` patterns | 11 | ✅ DONE |
| TASK 7: Fix Postgres OOM | 1 | ✅ DONE |
| TASK 8: Delete meaningless simulation step | 1 | ✅ DONE |
| Mark Given steps as NARRATIVE | 13 | ✅ DONE |

### Remaining Issues (Not Fake Tests)

1. **Undefined Steps** (23 scenarios): Feature files written but step definitions not implemented
   - `ssh-agent-automatic-setup.feature`: 12 scenarios
   - `ssh-agent-forwarding-vm-to-vm.feature`: 10 scenarios
   - These are INCOMPLETE tests, not fake tests

2. **VDE_ROOT_DIR Environment**: Test runner fails when not pre-set

3. **Core Infrastructure BDD Crash**: Empty log output - needs investigation

### Key Architecture Notes

- **Given steps with `pass` are NARRATIVE markers** - Legitimate for User Guide generation
- **THEN steps must have real verification** - No tautological patterns
- **Port Registry Source of Truth**: `vm-types.conf` and `vm-types.json`
- **Postgres Config**: Added `shm_size: '256m'` and `memory: 1G` limit

---

## Historical State (2026-03-16 Earlier Sessions)

### Session 2026-03-16 (Late)
1. **Documentation Path Fix**:
    - Fixed incorrect paths in `.kilocode/rules/vde_context.md` and `tests/generate-remediation-plan.py`
    - Changed `bin/lib/` → `lib/` and `bin/data/` → `data/`
    - Committed: `a5e8cf3`
2. **Session Startup Enforcement**:
    - Added mandatory MEMORY.md read to `vde_context.md` session startup section

### Session 2026-03-16 (Earlier)
1. **Port Range Constant Fix**:
    - Corrected `VDE_LANG_PORT_END` from `2399` → `2299` to match spec (2200-2299 for languages).
    - Updated unit test to expect correct value.
2. **Port Registry Architecture**:
    - Fixed `verify_port_registry` to use `vm-types.conf/json` as source of truth (not compose files).
    - Updated cache-system BDD tests to reflect correct architecture.
    - Removed `@wip` tag from "Rebuild port registry" scenario - now fully passing.
3. **list-vms Categorization**:
    - Updated `list-vms` to display VMs categorized by type (Language/Service sections).
    - Fixed `--lang` and `--svc` flags to show only the requested type.
4. **Configuration Test Fix**:
    - Fixed `step_vm_boot_start` to check `context.restart_set` attribute before output fallback.
5. **Fake Test Remediation** (cache_steps.py):
    - Replaced 6 `assert True` with real verification logic.
    - Steps now verify: cache mtime, port file existence, valid port ranges, command execution.
