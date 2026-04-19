# VDE Init SSH Key Remediation Plan

## Objective
Modify `vde init` (`bin/vde-init`) so that if the `vde_student` SSH identity key does not exist, it will immediately execute `vde ssh-setup init` to generate the key and initialize the SSH environment inline, without looping or restarting the initialization process. Add proper error handling to ensure failures are caught.

## Key Files & Context
- **`bin/vde-init`**: The main script for the `vde init` command.
- **`bin/vde`**: Main command router to integrate `ssh-setup` and `ssh-sync`.
- **`VDE_SSH_IDENTITY`**: The path to the `vde_student` key, defined in `lib/vde-constants`.

## Implementation Steps

1. **Inline SSH Setup & Error Handling**:
   Inside the "Full setup mode" block of `bin/vde-init`, add a Hard Rule to check for the SSH key:
   - If the key is missing or `--force` is passed, run `"${VDE_ROOT_DIR}/bin/vde" ssh-setup init ${ssh_force_flag} || exit $?`
   - Proceed with the rest of the initialization without `exec` or looping.

2. **Remove Redundant Agent Setup**:
   In `vde_init_setup_ssh` (inside `bin/vde-init`), remove the redundant call to `ssh-agent-setup --init` since `ssh-setup init` now fully handles key generation and agent initialization.

3. **CLI Router Integration**:
   Ensure `ssh-setup` and `ssh-sync` are properly integrated into the `bin/vde` main router.

## Verification & Testing
1. Delete the existing SSH key: `rm -f ~/.ssh/vde/vde_student*`.
2. Run `bin/vde init`.
3. Verify that `vde ssh-setup init` is called inline, the key is generated, and `vde init` completes successfully without restarting.
4. Run the full BDD test suite (`proof-of-life-the-contract.feature`) to ensure no regressions.