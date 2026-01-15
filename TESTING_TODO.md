# VDE Testing TODO - Failing Tests & Issues

**Last Updated:** 2025-01-14

This document tracks all failing tests and what needs to be fixed.

---

## Test Suite Overview

| Test Suite | Total | Passed | Failed | Error | Skipped |
|------------|-------|--------|--------|-------|---------|
| **Shell Tests** | 87 | 87 | 0 | 0 | 0 |
| **BDD Tests** | 2503 | 2459 | 20 | 3 | 21 |

**Shell Tests:** ✅ 100% passing
**BDD Tests:** ⚠️ ~98% passing (23 failing/error scenarios)

---

## Category 1: Natural Language Parser (7 failures)

**Root Cause:** The parser in `scripts/vde-nlp-parser.sh` has intent detection bugs.

| Feature | Scenario | Issue | File |
|---------|----------|-------|------|
| `natural-language-parser.feature` | Detect list languages intent | Returns 'help' instead of 'list_vms' | N/A |
| `natural-language-parser.feature` | Detect list services intent | Returns 'help' instead of 'list_vms' | N/A |
| `natural-language-parser.feature` | Detect start multiple VMs intent | Intent parsing issues | N/A |
| `natural-language-parser.feature` | Detect status for specific VMs | Intent parsing issues | N/A |
| `natural-language-parser.feature` | Resolve VM aliases | Alias resolution not working | N/A |
| `natural-language-parser.feature` | Extract VM names from natural input | Name extraction issues | N/A |
| `ai-assistant-workflow.feature` | Parse commands with typos | Typo handling not implemented | N/A |

**Files to fix:**
- `scripts/vde-nlp-parser.sh` - Intent detection logic
- `scripts/lib/vde-parser` - Parser library functions

**Action needed:** Review and fix intent detection patterns in the parser.

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

### Priority 1 - Architecture Fix (enables other fixes)
- [ ] **Move VM lifecycle tests from BDD to shell tests**
  - Create `tests/integration/vm-lifecycle-integration.test.sh`
  - Tests should call actual `./scripts/create-virtual-for`, `./scripts/start-virtual`, `./scripts/shutdown-virtual`
  - Verify with actual `docker ps` commands
  - Clean up containers after each test

### Priority 2 - Parser Fixes
- [ ] Fix intent detection in `scripts/vde-nlp-parser.sh`
- [ ] Fix VM alias resolution
- [ ] Fix name extraction from natural input
- [ ] Implement typo handling

### Priority 3 - Cache System
- [ ] Debug cache persistence
- [ ] Fix port registry consistency

### Priority 4 - CI/CD Integration
- [ ] Update GitHub Actions workflow to run new integration tests
- [ ] Ensure Docker-in-Docker works in CI

---

## Files to Create

1. **`tests/integration/vm-lifecycle-integration.test.sh`** - Real VM lifecycle tests
2. **`tests/integration/docker-operations-integration.test.sh`** - Real Docker operations tests
3. **`tests/integration/nlp-parser-integration.test.sh`** - Parser tests with real script calls

---

## Notes

- GitHub Actions already supports Docker-in-Docker (see `.github/workflows/vde-ci.yml` Job 6)
- Shell tests already pass 100% - use them as the pattern
- BDD tests should be for user workflow documentation, not integration testing
- Integration tests should use actual VDE scripts, not mocked contexts
