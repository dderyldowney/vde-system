# Design Spec: BDD Test Suite Remediation (SIGINT & SSH Agent)
<!-- @shared-law (Forge Component) -->

**Date:** 2026-04-14
**Status:** Approved
**Target:** Sovereign Baseline 1.3.1 (Test Infrastructure & Sovereign Bridge)

## 1. Goal
Remediate the two regression blockades identified during the full test suite execution to restore the 100% Green status of the Forge.

## 2. Technical Strategy

### 2.1. SIGINT Interception (Task 1)
**Problem:** The current test sends SIGINT only to the parent Zsh process. Zsh waits for the foreground command (e.g., `docker run`) to finish before executing the trap. The test times out and kills the process, missing the error message.
**Solution:** Modify the Python step to use a process group. By starting the process in a new session and signaling the process group, both the Zsh script and the foreground command receive SIGINT simultaneously, triggering the trap immediately.

### 2.2. SSH Agent Forwarding (Task 2)
**Problem:** The `vde-entrypoint.zsh` unconditionally sets `SSH_AUTH_SOCK` in `/home/devuser/.zshenv`. This overwrites the legitimate agent socket provided by the SSH protocol during `ssh -A` sessions. If the `socat` bridge is inactive or broken, `ssh-add -l` fails.
**Solution:** Update the `.zshenv` generation to be conditional. Only export the proxy socket if `SSH_AUTH_SOCK` is currently empty. This ensures that protocol-based forwarding is prioritized while the `socat` bridge remains available for `docker exec` sessions.

## 3. Implementation Details

### 3.1. `tests/features/steps/error_handling_steps.py`
```python
# Updated step_simulate_sigint
proc = subprocess.Popen(
    command.split(),
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    cwd=VDE_ROOT,
    start_new_session=True # Force new process group
)
...
os.killpg(proc.pid, signal.SIGINT) # Signal the entire group
```

### 3.2. `scripts/vde-entrypoint.zsh`
```zsh
# Updated .zshenv generation
echo 'if [[ -z "${SSH_AUTH_SOCK}" ]]; then export SSH_AUTH_SOCK="'${_proxy_sock}'"; fi' > /home/devuser/.zshenv
```

## 4. Verification Plan
1.  Apply the fixes.
2.  Run `python3 -m behave tests/features/core-infrastructure/error-handling.feature`.
3.  Run `python3 -m behave tests/features/core-infrastructure/system-spine.feature`.
4.  Execute full test suite: `python3 -m behave tests/features/core-infrastructure/`.
5.  Verify 100% PASS.

## 5. Compliance
- **Rule 16.3 (Zero-Tolerance Failure)**: Remediates blockages in the System Spine.
- **Rule 10.5 (Empirical Proof)**: Restores the ability to prove the Codebase contracts.
- **Sovereign Bridge (Section 5)**: Hardens the SSH Agent forwarding logic against collision.
