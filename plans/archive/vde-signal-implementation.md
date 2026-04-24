# Plan: actual Signal Verification (Phase 26)
<!-- @shared-law (Forge Component) -->

## Objective
Implement actual signal verification using resource contention. NO SIMULATIONS.

## Strategy: Resource Contention Strike
Instead of guessing timing with `sleep`, we will use the VDE locking system to pause the process deterministically.

1. **Lock**: Create a manual lock at `.locks/vms/python.lock`.
2. **Execute**: Run `vde rebuild python` in the background. It will block on the lock.
3. **Poll**: Use `vde-poll --wait` (or a custom check for the PID file) to confirm VDE is actually spinning.
4. **Signal**: Send `SIGINT` to the blocked process.
5. **Verify**: Check that VDE catches the signal and displays the new "Operation Interrupted" message.

## Implementation Steps

### 1. Test Script: `plans/scripts/test_signal_interception.zsh`
- Create a ZSH script that:
    - Cleans existing locks.
    - Creates a manual `python.lock` with a fake PID.
    - Starts `vde rebuild python` in the background.
    - Polls until `vde` is confirmed waiting (check process list or lock PID file).
    - Sends `SIGINT`.
    - Captures and displays output.

### 2. BDD Step Update
- Refactor `step_interrupt_command` in `tests/features/steps/vde_error_steps.py` to use this contention logic instead of `Popen` + `time.sleep`.

## Verification
- Run `behave tests/features/core-infrastructure/vde-signal-handling.feature`.
- Manually run `plans/scripts/test_signal_interception.zsh`.
