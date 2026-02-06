# Plan 32: SSH Configuration Remediation - LARGEST SINGLE WIN

## Executive Summary

**Status:** PENDING - Infrastructure Fixed by Plan 31

**Feature:** `tests/features/docker-required/ssh-configuration.feature`

**Scope:** 108 undefined steps + 7 errors (LARGEST)

## Infrastructure Status

**FIXED by Plan 31:** `vde create` now correctly checks container existence, not config existence.
- Previously: Tests failed during setup because `vde create` refused to recreate containers
- Now: Containers can be deleted and recreated during test setup

---

## Problem Breakdown

### SSH Configuration Scenarios (28 total)

| Scenario | Status | Steps |
|----------|--------|-------|
| Automatically start SSH agent if not running | FAILED | 6 |
| Generate SSH key if none exists | FAILED | 5 |
| Sync public keys to VDE directory | ERROR | 8 |
| Validate public key files only | PASSED | 4 |
| Create SSH config entry for new VM | FAILED | 9 |
| Backup SSH config before modification | FAILED | 5 |
| Atomic SSH config update prevents corruption | ERROR | 9 |
| Remove SSH config entry when VM is removed | FAILED | 8 |
| VM-to-VM communication uses agent forwarding | ERROR | 6 |
| Detect all common SSH key types | ERROR | 9 |
| Prefer ed25519 keys when multiple exist | ERROR | 8 |
| Merge new VM entry with existing SSH config | ERROR | 6 |
| Merge preserves user's custom SSH settings | ERROR | 6 |
| Merge preserves existing VDE entries | ERROR | 5 |
| Merge does not duplicate existing VDE entries | ERROR | 5 |
| Atomic merge prevents corruption if interrupted | ERROR | 7 |
| Merge uses temporary file then atomic rename | ERROR | 6 |
| Merge creates SSH config if it doesn't exist | ERROR | 5 |
| Merge creates .ssh directory if needed | ERROR | 5 |
| Merge preserves blank lines and formatting | ERROR | 5 |
| Merge respects file locking for concurrent updates | ERROR | 7 |
| Merge creates backup before any modification | ERROR | 6 |
| Merge entry has all required SSH config fields | ERROR | 9 |
| Remove VM entry when VM is removed | ERROR | 8 |
| Remove known_hosts entry when VM is removed | ERROR | 8 |
| Remove multiple hostname patterns from known_hosts | ERROR | 7 |
| Create backup of known_hosts before cleanup | ERROR | 6 |
| Known_hosts cleanup handles missing file gracefully | ERROR | 5 |
| Known_hosts cleanup removes entries by port number | ERROR | 5 |
| Recreating VM after removal succeeds | ERROR | 6 |

---

## Root Cause: AmbiguousStep Errors

**Issue:** Steps scattered across multiple files causing AmbiguousStep conflicts:

- `tests/features/steps/ssh_config_steps.py`
- `tests/features/steps/pattern_steps.py`
- `tests/features/steps/documented_workflow_steps.py`

**Solution:** Consolidate existing implementations before adding new steps.

---

## Implementation Strategy

### Phase 1: Consolidate Existing Steps
1. Audit `pattern_steps.py` for SSH-related patterns
2. Audit `documented_workflow_steps.py` for SSH steps
3. Move/disambiguate conflicting patterns

### Phase 2: Add Missing Steps
1. Implement remaining undefined steps in `ssh_config_steps.py`
2. Add proper error handling
3. Mock SSH operations for isolated testing

### Phase 3: Fix Errors
1. Investigate 7 error scenarios
2. Fix setup/teardown issues
3. Validate all scenarios pass

---

## Files Involved

- `tests/features/docker-required/ssh-configuration.feature`
- `tests/features/steps/ssh_config_steps.py`
- `tests/features/steps/pattern_steps.py`
- `tests/features/steps/documented_workflow_steps.py`
- `scripts/lib/ssh/` (SSH helper scripts)

---

## Run Tests

```bash
# Dry run to see undefined steps
python3 -m behave tests/features/docker-required/ssh-configuration.feature --dry-run

# Full run with verbose
python3 -m behave tests/features/docker-required/ssh-configuration.feature -v

# Check for AmbiguousStep
python3 -m behave tests/features/docker-required/ssh-configuration.feature 2>&1 | grep -i ambiguous
```

---

## Expected Outcome

After completion:
- 108 undefined → 0 undefined
- 7 errors → 0 errors
- 28 scenarios passing
