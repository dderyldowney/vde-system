# VDE Testing TODO

**Last Updated:** 2026-01-15

This document tracks remaining test work and completed improvements.

---

## Test Suite Status

| Test Suite | Total | Passing | Notes |
|------------|-------|---------|-------|
| **Shell Tests** | 87 | 100% | ✅ All passing |
| **Docker VM Lifecycle** | 10 | 80% | 2 timing-related failures |
| **BDD Tests** | 2497 | ~98% | Many scenarios now use real VDE scripts |

---

## Remaining Work

### Fuzzy Matching for Typo Handling

**Status:** Pending Implementation (see [FUZZY_LOGIC_TODO.md](./FUZZY_LOGIC_TODO.md))

The BDD test "Parse commands with typos" fails because the parser cannot handle typos in user input.

**Failing Test:**
```gherkin
Scenario: Parse commands with typos
    Given I make a typo in my command
    When I say "strt the python vm"
    Then the system should still understand my intent
    And the system should provide helpful correction suggestions
```

**Implementation Plan:** See [FUZZY_LOGIC_TODO.md](./FUZZY_LOGIC_TODO.md) for detailed implementation steps.

---

## Completed Work

### Priority 1 - VM Lifecycle Integration Tests
- ✅ Created `tests/integration/docker-vm-lifecycle.test.sh`
- ✅ Tests call actual VDE scripts
- ✅ Verified with `docker ps` commands
- ✅ Added to CI workflow (Job 6)

### Priority 2 - Natural Language Parser
- ✅ Fixed intent detection order
- ✅ Fixed VM alias resolution
- ✅ Fixed comma-separated VM name extraction
- ✅ Fixed quote stripping in VM lists

### Priority 3 - Cache System
- ✅ Unit tests pass (vm-common.test.sh)
- ✅ Cache file creation/loading works
- ✅ No-cache flag works

### Priority 4 - CI/CD Integration
- ✅ Added docker-vm-lifecycle.test.sh to GitHub Actions
- ✅ BDD tests have Docker socket access in CI (Job 8)
- ✅ Local BDD test script: `./tests/run-bdd-local.sh`

### Priority 5 - BDD Test Architecture Fixes ✅ COMPLETED (2026-01-15)

**Major rewrite of 6 BDD step files to use real VDE scripts instead of mocks:**

| File | Before | After | Changes |
|------|--------|-------|---------|
| `vm_lifecycle_steps.py` | 3557 lines | 875 lines | Calls `create-virtual-for`, `start-virtual`, `shutdown-virtual` |
| `ssh_steps.py` | 3894 lines | 428 lines | Checks real SSH files, uses `docker ps`, `ssh-add -l` |
| `cache_steps.py` | 143 lines | 272 lines | Checks cache files, validates format |
| `pattern_steps.py` | 270 lines | 459 lines | Checks SSH config, Docker state, VM types |
| `ssh_docker_steps.py` | 710 lines | 285 lines | Uses `docker info`, `lsof` for ports |
| `daily_workflow_steps.py` | 1678 lines | 446 lines | Calls real VDE scripts, checks container state |

**New infrastructure:**
- Created `tests/features/steps/vde_test_helpers.py` - shared utility module
- All GIVEN steps now check actual system state (files, containers, processes)
- All WHEN steps call actual VDE scripts with proper timeouts
- All THEN steps verify real outcomes (exit codes, container state, file existence)

**Total impact:**
- **~10,000 lines reduced to ~2,750 lines** (72% reduction)
- Tests now validate actual VDE functionality instead of mock behavior
- BDD tests can now be used as real integration tests

---

## Notes

- Shell tests remain the primary integration test method
- BDD tests now serve as both user workflow documentation AND integration tests
- For new features, write shell tests first, then document in BDD
- Run `./tests/run-bdd-local.sh` for local BDD testing with Docker access
