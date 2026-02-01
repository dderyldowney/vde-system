# VDE Test Remediation Plan

Generated from failures database

## Executive Summary

- **Total Failures**: 4
- **Pass Rate**: 99.3%
- **By Severity**: {'MEDIUM': 3, 'LOW': 1}
- **By Category**: {'DEBUG_OUTPUT': 3, 'SSH_AGENT': 1}


## MEDIUM Fixes

### Fix #1: Debug Output

**Impact**: 3 failure(s) | **Severity**: MEDIUM

**Affected Tests**:
- docker-free/documented-development-workflows.feature:8 - Example 1 - Python API with PostgreSQL Setup
- docker-free/documented-development-workflows.feature:15 - Example 1 - Create PostgreSQL for Python API
- docker-free/documented-development-workflows.feature:144 - Adding Cache Layer - Create Redis

**Error Examples**:
```
["ASSERT FAILED: Expected create_vm intent, got 'DEBUG: _load_vm_types_from_config called with VDE_ROOT_DIR = /Users/dderyldowney/dev", 'DEBUG: VM_TYPES_CONF = /Users/dderyldowney/dev/scripts/data/vm-types.conf', 'DEBUG: conf_file = /Users/dderyldowney/dev/scripts/data/vm-types.conf', "create_vm'"]
```

**Root Cause**:
- VM types config loader outputs DEBUG to stdout instead of stderr

**Impact**:
- Parser receives contaminated output, intent detection fails

**Fix Steps**:
- Redirect DEBUG output in `_load_vm_types_from_config` to stderr
- Update parser script that loads `scripts/data/vm-types.conf`
- Ensure all DEBUG/logging goes to stderr, not stdout

**Files to Modify**:
- Parser scripts that load VM types config

**Verification**:
```bash
./tests/run-docker-free-tests.sh
# Expect: 0 failures in this category
```

---


## LOW Fixes

### Fix #2: Ssh Agent

**Impact**: 1 failure(s) | **Severity**: LOW

**Affected Tests**:
- docker-required/ssh-agent-external-git-operations.feature:91 - Git operations in automated workflows

**Error Examples**:
```
ASSERT FAILED: SSH agent should be running for automated Git operations
```

**Root Cause**:
- No SSH agent in test environment

**Impact**:
- SSH-dependent tests fail (vde-ssh-commands, ssh-agent-external-git-operations)

**Fix Steps**:
- Start ssh-agent in test setup (via @given or setUp)
- Generate test SSH key and add to agent
- OR mark tests as requiring ssh-agent and skip if not available

**Files to Modify**:
- tests/features/steps/ssh_agent_steps.py
- test environment setup

**Verification**:
```bash
./tests/run-docker-required-tests.sh
# Expect: 0 failures in this category
```

---

## Final Validation

After implementing all fixes:

```bash
# Run full test suite
./tests/run-full-test-suite.sh

# Verify no failures
python tests/analyze-failures.py
cat tests/failures-database.json | jq '.summary.total_failures'
# Expected: 0
```
