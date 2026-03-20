# Session Handover - March 20, 2026 (Session 44)

## Summary

Fixed test isolation issue in documented-workflows.feature. Added `@requires-docker-host` tag to scenarios that create Docker VMs. **All tests passing** (18 shell compat, 72 pytest, 58 parser BDD, 20 docker helpers).

---

## Session 44 Accomplishments

### 1. Fixed Test Isolation in documented-workflows.feature

**Problem:** Scenario "Switching Projects - Stop Current Project" failed with "VMs still running: ['vde-python']"

**Root Cause:** Previous scenario "Adding Cache Layer - Start Redis" created VMs via `Given I have an existing Python and PostgreSQL stack` which calls `vde create python postgres`. Cleanup only happened for scenarios tagged `@requires-docker-host`, but those scenarios weren't tagged.

**Solution:** Added `@requires-docker-host` tag to scenarios that create Docker VMs:
- Scenario: Adding Cache Layer - Create Redis
- Scenario: Adding Cache Layer - Start Redis

---

## Test Results

```
Shell compat: 18/18 passing
Python unit tests: 72/72 passing
Docker helper tests: 20/20 passing
Parser/intent BDD: 58/58 passing (4 features, 34.7s)
```

---

## Files Modified

### tests/features/core-infrastructure/documented-workflows.feature
- Added `@requires-docker-host` tag to 2 scenarios that create Docker VMs

---

## SSH Config Drift

`configs/ssh/config` has uncommitted changes:
- zig entries removed (expected)
- test VMs added (expected)

To sync: `cp configs/ssh/config ~/.ssh/vde/config`

---

## Running Tests

```bash
# Shell compat
zsh tests/unit/vde-shell-compat.test.zsh

# Python unit tests
python3 -m pytest tests/unit/ -q

# Parser/intent features
python3 -m behave tests/features/core-infrastructure/documented-workflows.feature \
  tests/features/core-infrastructure/daily-workflow.feature \
  tests/features/core-infrastructure/daily-development.feature \
  tests/features/core-infrastructure/multi-project.feature -q

# Docker helper tests
python3 -m pytest tests/unit/test_docker_helpers.py -q
```
