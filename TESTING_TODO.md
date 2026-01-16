# VDE Testing TODO

**Last Updated:** 2026-01-16

---

## Remaining Work

### High Priority

#### 1. SSH Agent Automatic Setup BDD Scenarios

**Status:** Scenarios exist but many steps are undefined

**Feature File:** `tests/features/ssh-agent-automatic-setup.feature`

**Scenarios (12 total):**
1. First-time user with no SSH keys
2. First-time user with existing SSH keys
3. User with multiple SSH key types
4. SSH agent setup is silent during normal operations
5. SSH agent restart if not running
6. Viewing SSH status
7. SSH config auto-generation for all VMs
8. Rebuilding VMs preserves SSH configuration
9. Automatic key generation preference
10. Public keys automatically synced to VDE
11. SSH setup works with different SSH clients
12. No manual SSH configuration needed

**Current Status:**
- Feature file exists and is active (no @wip tag)
- Some steps may be undefined (need verification)

**Action Required:**
- Implement remaining undefined step definitions in `tests/features/steps/ssh_steps.py`
- Verify scenarios pass with actual SSH setup implementation

---

### Medium Priority

#### 3. Investigate BDD Test Failures

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

#### 3. Undefined BDD Steps

**Status:** Some steps remain undefined

**Current Count:** ~53 undefined steps (96% reduction from original 1248)
**Recent Progress:** Implemented 11 idempotent operations and state communication steps

**Remaining undefined steps** are mostly edge cases:
- Template rendering edge cases (placeholder validation)
- SSH key authentication variations
- VM state awareness conditions
- Team collaboration scenarios
- Various feature-specific steps

**Note:** Most critical user workflows are already covered. Implementing remaining steps is optional.

---

### Low Priority

#### 4. Fuzzy Matching for Typo Handling

**Status:** Enhancement - parser cannot handle typos in user input

**Failing Scenario:**
```gherkin
Scenario: Parse commands with typos
    Given I make a typo in my command
    When I say "strt the python vm"
    Then the system should still understand my intent
    And the system should provide helpful correction suggestions
```

**Dependencies:** ✅ `thefuzz` (v0.22.1) installed

**Implementation Plan:** See [FUZZY_LOGIC_TODO.md](./FUZZY_LOGIC_TODO.md)

---

## Running Tests

### Shell Tests
```bash
cd tests
./run-all-tests.sh
```

### BDD Tests (Local with Docker)
```bash
cd tests
./run-bdd-local.sh
```

### Specific BDD Features
```bash
cd tests
behave features/vm-lifecycle.feature
```

---

## Quick Reference

### Test File Locations
- **Shell tests:** `tests/*.test.sh`, `tests/unit/*.test.sh`
- **BDD features:** `tests/features/*.feature`
- **Step definitions:** `tests/features/steps/*.py`, `tests/shared/steps/*.py`
- **Test configs:** `tests/behave.ini`

### Current Test Status
```
Shell Tests:     108 passed, 0 failed ✅
BDD Scenarios:   ~2500 scenarios
Verified Scenarios: 96
```
