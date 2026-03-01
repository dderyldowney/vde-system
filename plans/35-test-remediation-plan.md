# VDE Test Remediation Plan

## Session Context

This plan captures the test remediation work in progress. The installation-setup.feature tests have been fixed (18/18 passing). The full test suite has remaining issues that need remediation.

## Current Status (as of 2026-03-01)

- **Installation Setup**: ✅ FIXED - 18 scenarios passing, 0 failing
- **Full Test Suite**: 273 passing, 62 failing, 154 errors, 343 undefined steps

## Fixes Applied in Previous Session

1. Fixed typo "vde-testingwork" → "vde-testing" in test steps
2. Added upgrade guide section to README.md
3. Fixed platform-specific test to check vde-health script
4. Fixed build progress test to check vde-rebuild
5. Fixed network check to use docker directly (vm_common.py)
6. Fixed VM network config check to include .env files
7. Updated vde-networks with --all flag
8. Updated test setup to use vde init --networks-only --testing

## Remaining Work - Prioritized

### Priority 1: CRITICAL (Core Functionality)
These features break essential VDE operations:

1. **VM State Awareness** (17 issues)
   - File: `tests/features/steps/vm_state_verification_steps.py`
   - Need: Implement missing step definitions for state checking
   
2. **Error Handling and Recovery** (13 issues)
   - File: `tests/features/steps/error_handling_steps.py`
   - Need: Implement error scenario step definitions

3. **Debugging and Troubleshooting** (16 issues)
   - File: `tests/features/steps/debugging_steps.py`
   - Need: Implement debugging step definitions

### Priority 2: HIGH (Frequent Operations)
4. **Docker and Container Management** (13 issues)
   - File: `tests/features/steps/docker_lifecycle_steps.py`
   
5. **Port Management** (12 issues)
   - File: `tests/features/steps/port_management_steps.py`
   
6. **VM Lifecycle Management** (11 issues)
   - File: `tests/features/steps/vm_lifecycle_steps.py`

### Priority 3: MEDIUM (Important Features)
7. **Template System** (12 issues)
8. **VM-to-Host Communication** (12 issues)
9. **Daily Development Workflow** (13 issues)
10. **Team Collaboration** (11 issues)
11. **SSH Features** (various)

### Priority 4: LOW (Nice to Have)
- Cache System
- Productivity Features
- Multi-Project Workflow
- Natural Language Commands

## How to Continue

1. **Run tests**: `cd tests/features && behave --format progress`
2. **Check specific feature**: `behave features/<feature-name>.feature`
3. **Find undefined steps**: Look for "StepNotImplementedError" in output
4. **Implement missing steps** in the corresponding step files

## Key Files to Modify

- `tests/features/steps/vm_state_verification_steps.py`
- `tests/features/steps/error_handling_steps.py`
- `tests/features/steps/debugging_steps.py`
- `tests/features/steps/docker_lifecycle_steps.py`
- `tests/features/steps/port_management_steps.py`
- `tests/features/steps/vm_lifecycle_steps.py`

## Notes

- Many failures are due to undefined step definitions (StepNotImplementedError)
- Some tests may still have hardcoded return values instead of real checks
- The fake test prohibition rules apply to all new implementations
