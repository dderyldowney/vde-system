# Test Remediation Implementation Plan

## Current: 83 passed, 26 failed | Target: <15 failures

---

## STEP 1: Fix Parser "create js" Intent Detection

### Problem
Test fails: `assert js_intent == 'create_vm'` at `tests/features/steps/documented_workflow_steps.py:923`
- Input: `"create js"` 
- Expected: `create_vm` intent
- Actual: fails (intent not detected)

### Root Cause
The `detect_intent()` function in `scripts/lib/vde-parser` doesn't recognize "js" as a valid language VM name.

### Fix Required

**File:** `scripts/lib/vde-parser`

1.1 Find LANG_VMS pattern (~line 50-70) and add "js":
```zsh
# Current (example):
LANG_VMS="python|go|rust|java|ruby|php|..."

# Change to:
LANG_VMS="python|js|go|rust|java|ruby|php|..."
```

1.2 Find INTENT_CREATE_VM regex (~line 100-150):
```zsh
# Current may match only multi-word:
if [[ "$input" =~ ^create[[:space:]]+(.+)$ ]]; then

# Change to match single-word VM names:
if [[ "$input" =~ ^create[[:space:]]+([a-zA-Z]+)$ ]]; then
```

---

## STEP 2: Fix SSH Service in Dockerfile

### Problem
Container starts but "No running VM found to check SSH accessibility"

### Root Cause
SSH service may not be starting properly in container

### Fix Required

**File:** `configs/docker/vde-base.Dockerfile`

2.1 Verify openssh-server is installed:
```dockerfile
RUN apt-get update && apt-get install -y \
    openssh-server \
    ...
```

2.2 Ensure SSH directories exist:
```dockerfile
RUN mkdir /var/run/sshd && \
    chmod 0755 /var/run/sshd && \
    ssh-keygen -A
```

2.3 Fix startup command (should NOT use -D for daemonless mode in compose):
```dockerfile
# In compose-language.yml command:
# Current: command: sh -c "apt-get update... && /usr/sbin/sshd -D"
# Fix: Remove -D flag, use proper daemon mode
command: sh -c "apt-get update... && /usr/sbin/sshd"
```

---

## STEP 3: Verify vm-types.json has js Entry

### Problem
Parser may fail because "js" not defined in VM types

### Fix Required

**File:** `scripts/data/vm-types.json`

3.1 Add js entry if missing:
```json
{
  "name": "js",
  "type": "lang",
  "display_name": "JavaScript",
  "install_cmd": "apt-get update -y && apt-get install -y nodejs npm",
  "ssh_port": 2201,
  ...
}
```

---

## STEP 4: Fix Test Timing/Assertion Issues

### Problem
Tests check for SSH too quickly before container is ready

### Fix Required

**File:** `tests/features/steps/vm_lifecycle_assertion_steps.py`

4.1 Add wait/retry for SSH port:
```python
# Add before SSH check:
import time
for i in range(10):
    result = subprocess.run(['docker', 'ps'...])
    if result.returncode == 0:
        time.sleep(2)  # Wait for SSH to start
        break
```

---

## STEP 5: Fix Network Cleanup Between Tests

### Problem
Tests may interfere with each other due to network state

### Fix Required

**File:** `tests/features/steps/environment.py`

5.1 Ensure network cleanup in before_scenario:
```python
def before_scenario(context, scenario):
    # Clean up networks before each test
    subprocess.run(['docker', 'network', 'prune', '-f'])
    ...
```

---

## STEP 6: Run Tests and Validate

### Command
```bash
# Run all docker-free tests
behave tests/features/docker-free/ --no-skipped

# Run critical path
behave tests/features/critical-path/vm-full-lifecycle.feature
```

### Expected Results
| Metric | Before | After |
|--------|--------|-------|
| Passed | 83 | 95+ |
| Failed | 26 | <10 |
| Skipped | 1 | 0 |

---

## Files Summary

| Step | File | Change |
|------|------|--------|
| 1 | `scripts/lib/vde-parser` | Add js to LANG_VMS, fix regex |
| 2 | `configs/docker/vde-base.Dockerfile` | Verify SSH install/start |
| 2 | `scripts/templates/compose-language.yml` | Fix sshd command |
| 3 | `scripts/data/vm-types.json` | Verify js entry |
| 4 | `tests/features/steps/vm_lifecycle_assertion_steps.py` | Add SSH wait |
| 5 | `tests/features/steps/environment.py` | Add network cleanup |
| 6 | - | Run & validate |
