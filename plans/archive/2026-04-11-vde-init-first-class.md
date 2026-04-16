# The Integration of `vde init` (Sovereign Baseline)

## 1. Objective
Elevate the orphaned `bin/vde-init` script to a fully registered, functional, and empirically tested first-class command in the VDE Orchestrator. This ensures VDE can be initialized cleanly by new users without relying on legacy fallback patterns.

## 2. Key Files & Context
- `bin/vde`: The canonical entrypoint (requires registration).
- `bin/vde-init`: The orphaned script (requires refactoring).
- `tests/features/core-infrastructure/vde-init-empirical.feature`: The new physical test bank (requires creation).

## 3. Implementation Steps

### 3.1. Orchestrator Registration (`bin/vde`)
- Add `init` to the primary `case` statement in `bin/vde`, routing it to `vde_run "init" "${VDE_ROOT_DIR}/bin/vde-init" "$@"`.
- Update the usage/help string to include `init`.

### 3.2. Script Remediation (`bin/vde-init`)
- **Path Sovereignity**: Replace the hardcoded `local ssh_dir="${HOME}/.ssh/vde"` with the globally authenticated `${VDE_SSH_DIR}` imported from `lib/vde-constants`.
- **Legacy Purge**: Remove the `build-and-start` fallback execution block. The `init` command must act as a strict infrastructure initializer (directories, networks, SSH keys), leaving container hydration to `vde create`.
- **Idempotency**: Ensure all `mkdir`, `chmod`, and `docker network create` commands handle pre-existing artifacts gracefully without failing the script.

### 3.3. Empirical Verification Bank (The TDD Law)
- Create `tests/features/core-infrastructure/vde-init-empirical.feature` to physically assert the side effects of `vde init`.
- The test must verify:
    - The creation of mandatory directories (`.cache/`, `data/`, `projects/`).
    - The generation of SSH identities in `${VDE_SSH_DIR}`.
    - The existence of the `vde-net` Docker network.
    - The command's successful exit code.

## 4. Verification & Testing
- Run `python3 -m behave tests/features/core-infrastructure/vde-init-empirical.feature` to demonstrate a **RED** failure initially.
- Execute the implementation steps.
- Run the test again to demonstrate a **GREEN** victory.
