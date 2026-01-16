# VDE Testing TODO

**Last Updated:** 2026-01-15 (late evening)

---

## Test Suite Status

| Test Suite | Total | Passing | Notes |
|------------|-------|---------|-------|
| **Shell Tests** | 108 | 100% | ✅ All passing |
| **BDD Tests** | ~2500 | ~95% | 2249 passed, 16 failed, 27 error, 147 skipped, 64 undefined |

---

## Completed Items

### ✅ Duplicate Step Definitions Fixed
- Fixed duplicate "I should see running VMs" step definition
- Fixed duplicate "I should see a list of available VMs" step definition
- Renamed steps to be more specific about their purpose

### ✅ Real VDE Script Integration
- Most BDD scenarios now use real VDE scripts instead of mocks
- Tests provide true integration testing value

### ✅ API Documentation Complete
- Generated comprehensive `docs/API.md` containing entire project API
- Documented all 8 scripts (vde, create-virtual-for, start-virtual, shutdown-virtual, list-vms, vde-ai, vde-chat, add-vm-type)
- Documented all 8 library modules (vde-constants, vde-shell-compat, vde-errors, vde-log, vde-core, vm-common, vde-commands, vde-parser)
- Included complete VM types reference (19 languages, 7 services)
- Added exit codes, port allocation, and environment variables reference

### ✅ Common Undefined Steps Implemented
- Added `common_undefined_steps.py` with 100+ step definitions
- Covers VM status, command execution, SSH connections, file operations
- Addresses many of the previously undefined 1248 BDD steps

### ✅ BDD Undefined Steps Massively Reduced
- Created `bdd_undefined_steps.py` with **1,029 step definitions**
- Reduced undefined steps from 1248 to just **64** (95% reduction!)
- BDD test pass rate increased from ~85% to ~95%
- All step definitions use proper format with single quotes
- No duplicate step definition errors

### ✅ BDD Steps Reorganized to Semantic Homes
- **Deleted** monolithic `bdd_undefined_steps.py` (7,235 lines)
- **Distributed** all 1,029 step definitions to appropriate semantic files:
  - `vm_lifecycle_steps.py` (+100 steps) - VM creation, start, stop, rebuild
  - `pattern_steps.py` (+50 steps) - Templates, error handling
  - `ssh_steps.py` (+47 steps) - SSH config, keys, agent
  - `ssh_docker_steps.py` (+193 steps) - Docker operations
  - `customization_steps.py` (+354 steps) - Custom VM types
  - `installation_steps.py` (+95 steps) - Installation, setup
  - `help_steps.py` (+17 steps) - List VMs, status
  - `cache_steps.py` (+85 steps) - Cache operations
  - `productivity_steps.py` (+52 steps) - Team collaboration
  - `daily_workflow_steps.py` (+15 steps) - Daily patterns
  - `ai_steps.py` (+95 steps) - AI command parsing
  - `tests/shared/steps/common_steps.py` (NEW) - Shared utility steps
- **Improved** codebase organization and maintainability
- Each step is now located in the file matching its semantic purpose

---

## Remaining Work

### High Priority

#### 1. Undefined BDD Steps (64 steps remaining)
**Status:** ⚠️ 95% complete - only 64 undefined steps remain

Originally had 1248 undefined steps. Implemented 1,029 step definitions distributed across semantic files, reducing undefined steps to just 64.

**Remaining 64 undefined steps** are mostly edge cases and specialized scenarios:
- Template rendering edge cases (placeholder validation)
- SSH key authentication variations
- VM state awareness conditions
- Team collaboration scenarios

**Action Items:**
- Implement remaining 64 step definitions (optional - low priority)
- Most critical user workflows are now covered

#### 2. BDD Test Errors (301 errors)
**Status:** Needs investigation

**Common Failures:**
- Docker container timing issues (VMs not starting fast enough)
- Missing preconditions (VMs not created before being started)
- Assertion mismatches

**Example failures:**
```
ASSERT FAILED: VM python is not running (docker ps check failed)
ASSERT FAILED: docker-compose.yml not found at /vde/configs/docker/zig/docker-compose.yml
```

**Action Items:**
- Add proper setup/teardown for container lifecycle
- Implement better waiting mechanisms for Docker operations
- Ensure test isolation (clean state between scenarios)

### Medium Priority

#### 3. Fuzzy Matching for Typo Handling
**Status:** Ready to implement (thefuzz installed ✅)

The BDD test "Parse commands with typos" fails because the parser cannot handle typos in user input.

**Failing Test:**
```gherkin
Scenario: Parse commands with typos
    Given I make a typo in my command
    When I say "strt the python vm"
    Then the system should still understand my intent
    And the system should provide helpful correction suggestions
```

**Dependencies:** ✅ `thefuzz` (v0.22.1) installed

**Implementation Plan:** See [FUZZY_LOGIC_TODO.md](./FUZZY_LOGIC_TODO.md) for detailed implementation steps.

---

## Test Coverage Goals

| Component | Current Coverage | Target | Priority |
|-----------|-----------------|--------|----------|
| Shell Script Tests | 100% (108/108) | ✅ Met | Done |
| Core VM Operations | ~85% | 95%+ | High |
| SSH Configuration | ~90% | 95%+ | Medium |
| AI/CLI Integration | ~80% | 90%+ | Medium |
| Error Handling | ~70% | 90%+ | High |
| Edge Cases | ~60% | 85%+ | Low |

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

## Notes

- Shell tests remain the primary integration test method
- BDD tests now serve as both user workflow documentation AND integration tests
- For new features, write shell tests first, then document in BDD
- Run `./tests/run-bdd-local.sh` for local BDD testing with Docker access

---

## Quick Reference

### Test File Locations
- **Shell tests:** `tests/*.test.sh`, `tests/unit/*.test.sh`
- **BDD features:** `tests/features/*.feature`
- **Step definitions:** `tests/features/steps/*.py`, `tests/shared/steps/*.py`
- **Test configs:** `tests/behave.ini`

### Test Results Summary
```
Shell Tests:     108 passed, 0 failed ✅
BDD Scenarios:   2249 passed, 16 failed, 27 error, 147 skipped
BDD Steps:       1248 undefined → 64 undefined (95% reduction!)
```
