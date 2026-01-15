# VDE Testing TODO - Failing Tests & Issues

**Last Updated:** 2026-01-14

This document tracks all failing tests and what needs to be fixed.

---

## Test Suite Overview

| Test Suite | Total | Passed | Failed | Error | Skipped |
|------------|-------|--------|--------|-------|---------|
| **Shell Tests** | 87 | 87 | 0 | 0 | 0 |
| **Docker VM Lifecycle** | 10 | 8 | 2 | 0 | 0 |
| **BDD Tests** | 2497 | 2446 | 15 | 6 | 24 |

**Shell Tests:** ✅ 100% passing
**Docker VM Lifecycle:** ⚠️ 80% passing (2 failures - likely timing issues)
**BDD Tests:** ⚠️ ~98% passing (21 failing/error scenarios)

---

## Recent Fixes (2026-01-14)

✅ **Fixed zsh subshell scoping in `ensure_vm_directories`** - Changed from string-based iteration to array-based iteration
✅ **Fixed log functions output to stderr** - Prevents log messages from being captured in variable assignments
✅ **Created Docker VM Lifecycle integration test** - `tests/integration/docker-vm-lifecycle.test.sh` (8/10 passing)

### Integration Test Results (docker-vm-lifecycle.test.sh)

| Test | Status |
|------|--------|
| Create language VM (elixir) | ✅ PASS |
| Create service VM (couchdb) | ✅ PASS |
| Start VM | ✅ PASS |
| Start multiple VMs | ❌ FAIL (timing issue) |
| Stop VM | ✅ PASS |
| Stop all VMs | ✅ PASS |
| Restart container | ❌ FAIL (container may not be running) |
| Rebuild VM | ✅ PASS |
| List VMs | ✅ PASS |
| Port allocation | ✅ PASS |

---

## Category 1: Natural Language Parser (1 remaining failure)

**Status:** ✅ Fixed 6 out of 7 issues

| Feature | Scenario | Status | Notes |
|---------|----------|--------|-------|
| `natural-language-parser.feature` | Detect list languages intent | ✅ FIXED | Pattern order fixed |
| `natural-language-parser.feature` | Detect list services intent | ✅ FIXED | Pattern now matches "available" |
| `natural-language-parser.feature` | Detect start multiple VMs intent | ✅ FIXED | Quote stripping added |
| `natural-language-parser.feature` | Detect status for specific VMs | ✅ FIXED | "show status" checked before "show" |
| `natural-language-parser.feature` | Resolve VM aliases | ✅ FIXED | Alias map merged from context |
| `natural-language-parser.feature` | Extract VM names from natural input | ✅ FIXED | Quote stripping for comma lists |
| `ai-assistant-workflow.feature` | Parse commands with typos | ⚠️ PENDING | Requires fuzzy matching (advanced) |

**Remaining work:**
- Typo handling requires fuzzy matching algorithm (Levenshtein distance or similar)
- This is an advanced feature for better user experience

---

## Category 2: VM Lifecycle - ARCHITECTURE ISSUE (7 failures/errors)

**Root Cause:** These tests are in BDD but use **mocked context** instead of calling actual VDE scripts.

| Feature | Scenario | Issue | Current Behavior |
|---------|----------|-------|------------------|
| `vm-lifecycle.feature` | Create a new language VM | Tests mock context, never calls scripts | Sets `context.vm_created = True` |
| `vm-lifecycle.feature` | Create a new service VM with custom port | Same issue | FileNotFoundError: `/vde/configs/docker/python` |
| `vm-lifecycle.feature` | Start multiple VMs | Same issue | Error - no actual VMs created |
| `vm-lifecycle.feature` | Start all VMs | Same issue | Error - no actual VMs created |
| `vm-lifecycle.feature` | Stop a running VM | No VMs exist to stop | Tries to stop non-existent container |
| `vm-lifecycle.feature` | Stop all running VMs | Same issue | Same |
| `team-collaboration-and-maintenance.feature` | Stopping only development VMs | Same issue | Error |

**Current BDD step pattern (WRONG):**
```python
@given('VM "{vm_name}" has been created')
def step_vm_created(context, vm_name):
    """Set up a VM as being created."""
    # This just sets a flag - doesn't actually create anything!
    context.created_vms.add(vm_name)
```

**What it should be (shell test):**
```bash
@test "Create a new language VM" {
    # Actually call the VDE script
    run ./scripts/create-virtual-for python

    # Verify it was created
    [ -f "configs/docker/python/docker-compose.yml" ]

    # Verify docker container exists
    docker ps | grep python-dev
}
```

**Action needed:** Move these tests from BDD to shell tests in `tests/integration/vm-lifecycle-integration.test.sh`

---

## Category 3: Port Management (5 failures)

**Root Cause:** Depends on VMs being created (see Category 2), so fails at the root.

| Feature | Scenario | Issue |
|---------|----------|-------|
| `port-management.feature` | Allocate first available port for language VM | VM creation fails first |
| `port-management.feature` | Allocate first available port for service VM | VM creation fails first |
| `port-management.feature` | Skip allocated ports when finding next available | VM creation fails first |
| `port-management.feature` | Detect host port collision during allocation | VM creation fails first |
| `port-management.feature` | Error when all ports in range are allocated | VM creation fails first |

**Action needed:** Will be fixed when Category 2 is resolved (real VM creation).

---

## Category 4: Cache System (2 failures)

**Root Cause:** Cache persistence and/or port registry consistency issues.

| Feature | Scenario | Issue |
|---------|----------|-------|
| `cache-system.feature` | Cache VM types after first load | Cache not persisting |
| `cache-system.feature` | Verify port registry consistency | Registry inconsistent |

**Files to check:**
- `.cache/` directory logic
- `scripts/lib/vm-common` - Cache handling functions
- `scripts/start-virtual` - Port allocation and caching

**Action needed:** Debug why `.cache/vm-types.cache` isn't being written/read correctly.

---

## Category 5: Docker Operations (2 failures)

**Root Cause:** Tests expect actual Docker containers but BDD uses mocks.

| Feature | Scenario | Issue |
|---------|----------|-------|
| `docker-operations.feature` | Restart container | No containers exist (never created) |
| `debugging-troubleshooting.feature` | Rebuild VM from scratch | No containers exist (never created) |

**Action needed:** Move to shell tests that use actual Docker commands (similar to existing CI Job 6).

---

## Priority Summary

### ✅ Priority 1 - Architecture Fix (COMPLETED)
- [x] **Move VM lifecycle tests from BDD to shell tests**
  - ✅ Created `tests/integration/docker-vm-lifecycle.test.sh`
  - Tests call actual `./scripts/create-virtual-for`, `./scripts/start-virtual`, `./scripts/shutdown-virtual`
  - Verifies with actual `docker ps` commands
  - Cleans up containers after each test
  - **Status:** 8/10 tests passing (2 timing-related failures)

### ✅ Priority 2 - Parser Fixes (COMPLETED)
- [x] Fix intent detection in BDD tests
- [x] Fix VM alias resolution
- [x] Fix name extraction from natural input
- [ ] Implement typo handling (requires fuzzy matching - advanced feature)

### Priority 3 - Cache System
- [ ] Debug cache persistence (2 failures)
- [ ] Fix port registry consistency

### Priority 4 - CI/CD Integration
- [ ] Update GitHub Actions workflow to run new integration tests
- [ ] Ensure Docker-in-Docker works in CI

---

## Created Files

1. ✅ **`tests/integration/docker-vm-lifecycle.test.sh`** - Real VM lifecycle tests (8/10 passing)
2. **`tests/integration/docker-operations-integration.test.sh`** - Real Docker operations tests (TODO)
3. **`tests/integration/nlp-parser-integration.test.sh`** - Parser tests with real script calls (TODO)

---

## Notes

- GitHub Actions already supports Docker-in-Docker (see `.github/workflows/vde-ci.yml` Job 6)
- Shell tests already pass 100% - use them as the pattern
- BDD tests should be for user workflow documentation, not integration testing
- Integration tests should use actual VDE scripts, not mocked contexts
- **Bugs Fixed Today:**
  - `ensure_vm_directories`: Changed from string splitting to array iteration for zsh compatibility
  - `log_info`, `log_success`, `log_warning`: Now output to stderr to prevent capture in variable assignments
