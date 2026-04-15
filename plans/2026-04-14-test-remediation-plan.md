# BDD Test Suite Remediation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remediate SIGINT translation and SSH Agent forwarding regressions in the BDD test suite.

**Architecture:** 
1. Update `tests/features/steps/error_handling_steps.py` to use process groups for signal delivery.
2. Update `scripts/vde-entrypoint.zsh` to make SSH_AUTH_SOCK export conditional in `.zshenv`.

**Tech Stack:** Python (BDD Steps), ZSH (Entrypoint).

---

### Task 1: SIGINT Test Remediation

**Files:**
- Modify: `tests/features/steps/error_handling_steps.py`

- [x] **Step 1: Update step_simulate_sigint**

Apply the following change to `tests/features/steps/error_handling_steps.py`:

```python
@when('I simulate a user interruption (SIGINT) during "{command}"')
def step_simulate_sigint(context, command):
    # Run the ACTUAL command in a new process group
    proc = subprocess.Popen(
        command.split(),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd=VDE_ROOT,
        start_new_session=True # Force new session/process group
    )
    
    # Wait for ignition to start (progress spinner)
    time.sleep(2)
    # Send ACTUAL signal to the entire process group
    os.killpg(proc.pid, signal.SIGINT)
    
    try:
        context.command_output, _ = proc.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL) # Kill the whole group if it hangs
        context.command_output, _ = proc.communicate()
        
    context.command_output = context.command_output or ""
    context.command_exit_code = proc.returncode
```

- [x] **Step 2: Commit Task 1**

```bash
git add tests/features/steps/error_handling_steps.py
git commit -m "fix(test): use process groups for SIGINT simulation"
```

---

### Task 2: SSH Agent Bridge Hardening

**Files:**
- Modify: `scripts/vde-entrypoint.zsh`

- [x] **Step 1: Refine .zshenv generation**

Apply the following change to `scripts/vde-entrypoint.zsh` (around line 90):

```zsh
        # Persistent bridge for non-login shells (Hardened: do not overwrite existing agent)
        echo 'if [[ -z "${SSH_AUTH_SOCK}" ]]; then export SSH_AUTH_SOCK="'${_proxy_sock}'"; fi' > /home/devuser/.zshenv
```

- [x] **Step 2: Commit Task 2**

```bash
git add scripts/vde-entrypoint.zsh
git commit -m "fix(bridge): protect protocol SSH agent forwarding from socat bridge override"
```

---

### Task 3: Verification

- [x] **Step 1: Run error handling tests**

Run: `python3 -m behave tests/features/core-infrastructure/error-handling.feature`
Expected: PASS

- [x] **Step 2: Run system spine tests**

Run: `python3 -m behave tests/features/core-infrastructure/system-spine.feature`
Expected: PASS

- [x] **Step 3: Run full suite**

Run: `python3 -m behave tests/features/core-infrastructure/`
Expected: 100% PASS
