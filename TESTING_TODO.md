# VDE Testing TODO

**Last Updated:** 2026-01-14

This document tracks remaining test work and known issues.

---

## Test Suite Status

| Test Suite | Total | Passing | Notes |
|------------|-------|---------|-------|
| **Shell Tests** | 87 | 100% | ✅ All passing |
| **Docker VM Lifecycle** | 10 | 80% | 2 timing-related failures |
| **BDD Tests** | 2497 | ~98% | Known architectural issues |

---

## Remaining Work

### 1. Fuzzy Matching for Typo Handling

**Status:** Pending Implementation

The BDD test "Parse commands with typos" fails because the parser cannot handle typos in user input.

**Failing Test:**
```gherkin
Scenario: Parse commands with typos
    Given I make a typo in my command
    When I say "strt the python vm"
    Then the system should still understand my intent
    And the system should provide helpful correction suggestions
```

**Expected Behavior:**
- Input: `"strt the python vm"`
- Output: Intent=`start_vm`, VM=`python`, plus correction suggestions like "Did you mean 'start'?"

**Implementation Plan:** See [FUZZY_LOGIC_TODO.md](./FUZZY_LOGIC_TODO.md) for detailed implementation steps.

---

## Remaining Work

### 2. Fix BDD Test Architecture (16 scenarios)

**Root Cause:** Many BDD tests use mocked context instead of calling actual VDE scripts.

**Action Required:**
1. Remove mocks from BDD step definitions
2. Implement real VM lifecycle operations in the BDD steps
3. Have tests call actual VDE scripts like `./scripts/start-virtual.sh`

**Affected Categories:**
- VM Lifecycle (7 scenarios)
- Port Management (5 scenarios)
- Cache System (2 scenarios)
- Docker Operations (2 scenarios)

**Reference:** Shell integration tests show the correct pattern:
- `tests/integration/docker-vm-lifecycle.test.sh`
- `tests/integration/test_integration_comprehensive.sh`

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
- ✅ Integration tests run in CI workflow

---

## Notes

- Shell tests should be the primary integration test method
- BDD tests serve as user workflow documentation
- For new features, write shell tests first, then document in BDD
