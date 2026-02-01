# SSH_AGENT Test Failure Remediation Plan

## Problem Statement

Test failure in `docker-required/ssh-agent-external-git-operations.feature:91`:
```
ASSERT FAILED: SSH agent should be running for automated Git operations
```

## Root Cause Analysis

The test relies on `ssh_agent_is_running()` from [`tests/features/steps/ssh_helpers.py:34`](tests/features/steps/ssh_helpers.py:34):

```python
def ssh_agent_is_running():
    """Check if SSH agent is running."""
    try:
        result = subprocess.run(
            ["ssh-add", "-l"],
            capture_output=True, text=True, timeout=5
        )
        return result.returncode == 0 or "no identities" in result.stderr.lower()
    except Exception:
        return False
```

**Issue:** The test environment has no SSH agent running. The function returns `False` when:
- `ssh-add -l` fails (exit code 1)
- An exception occurs (agent not found, can't connect)

## Impact

- **Severity:** LOW
- **Affected Tests:** 1 scenario (`Git operations in automated workflows`)
- **Test Type:** Docker-required (integration test)

## Remediation Options

### Option 1: Start SSH Agent in Test Setup (Recommended)

Add SSH agent startup to the test environment setup:

**Implementation:**
1. Create a test setup script that:
   - Starts ssh-agent and captures `SSH_AUTH_SOCK`, `SSH_AGENT_PID`
   - Generates a test SSH key if none exists
   - Adds the key to the agent
   - Exports environment variables for child processes

2. Modify test runner to source the setup before running tests

**Pros:**
- Real SSH agent testing
- Tests actual SSH key forwarding behavior

**Cons:**
- Modifies test environment
- Requires cleanup after tests

**Files to Modify:**
- `tests/run-full-test-suite.sh`
- `tests/features/environment.py` (create if not exists)

### Option 2: Skip Tests When No SSH Agent Available

Add a skip condition to the scenario:

**Implementation:**
```gherkin
  @skipUnless ssh_agent_available
  Scenario: Git operations in automated workflows
```

**Pros:**
- Tests pass when SSH agent unavailable
- No environment modification

**Cons:**
- Tests don't actually verify SSH functionality
- Reduces test coverage

**Files to Modify:**
- `tests/features/docker-required/ssh-agent-external-git-operations.feature`

### Option 3: Mock SSH Agent for Tests

Replace `ssh_agent_is_running()` with a mock that returns True during tests:

**Implementation:**
1. Set environment variable `VDE_TEST_MOCK_SSH_AGENT=true`
2. Modify `ssh_helpers.py` to check this variable
3. Return mock True when variable is set

**Pros:**
- Simple to implement
- No external dependencies

**Cons:**
- Not testing real SSH agent behavior
- May miss real-world issues

**Files to Modify:**
- `tests/features/steps/ssh_helpers.py`

## Recommended Approach: Option 1 (Start SSH Agent)

This provides the most realistic testing while ensuring tests can run in CI/CD environments.

### Implementation Steps

1. **Create SSH agent setup script** (`tests/setup-ssh-agent.sh`):
```bash
#!/usr/bin/env zsh
# Start SSH agent and generate test key if needed

# Check if agent already running
if ssh-add -l >/dev/null 2>&1 || [ "$?" = "1" ]; then
    echo "SSH agent already running"
    return 0
fi

# Start agent
eval "$(ssh-agent -s)" >/dev/null

# Generate test key if not exists
if [ ! -f ~/.ssh/vde/id_ed25519 ]; then
    mkdir -p ~/.ssh/vde
    ssh-keygen -t ed25519 -f ~/.ssh/vde/id_ed25519 -N "" -q
fi

# Add key to agent
ssh-add ~/.ssh/vde/id_ed25519

# Export for child processes
export SSH_AUTH_SOCK
export SSH_AGENT_PID

echo "SSH agent started: PID=$SSH_AGENT_PID"
```

2. **Modify test runner** to source the setup script

3. **Add cleanup** to stop agent after tests

## Verification

After implementing the fix:

```bash
# Run the specific failing test
behave tests/features/docker-required/ssh-agent-external-git-operations.feature:91

# Verify SSH agent check passes
ssh-add -l  # Should show key loaded or "no identities"
```

## Alternative Quick Fix

If full implementation is too complex for immediate needs, mark the test as `@skip` for now:

```gherkin
  @skip  # Requires SSH agent - tracked in issue #123
  Scenario: Git operations in automated workflows
```

This allows the test suite to pass while a proper fix is developed.
