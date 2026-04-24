# Identity Re-Forging Strike: v1.0.0 Refactor
<!-- @shared-law (Forge Component) -->

## Background & Motivation
The VDE Identity needs to reflect its specific purpose within the Creed. The generic `id_ed25519` key name must be refactored to `vde_student` across the ecosystem, strictly distinguishing between the key type (ed25519) and the file name.

## Scope & Impact
- **Core Variables:** `VDE_SSH_IDENTITY` is already correctly defined as `vde_student` in `lib/vde-constants`.
- **Key-Forge Ritual:** The creation of the key in `bin/vde-bootstrap` and `lib/vde-ssh` already correctly utilizes `vde_student` via the core variables.
- **Bridge Synchronization:** The scripts `bin/ssh-vm` and `bin/vde-exec` successfully consume `VDE_SSH_IDENTITY` natively.
- **Remediation Required:** Numerous lingering hardcoded file paths exist in documentation, testing scripts, and configuration generators that must be purged.

## Proposed Solution
A targeted find-and-replace operation across the codebase to update any file path references from `id_ed25519` to `vde_student`.

## Implementation Steps
1. **Update Test Files:**
   - Modify `tests/features/steps/ssh_helpers.py` to point `VDE_SSH_IDENTITY` to `vde_student`.
   - Modify `tests/features/steps/critical_steps.py` to check for `~/.ssh/vde/vde_student`.
   - Update comment in `tests/unit/vde-security.test.zsh`.
2. **Update Core Scripts & Libraries:**
   - Update `bin/ssh-setup` to check for `vde_student.pub` instead of `vde_id_ed25519.pub`.
   - Update `bin/generate-all-configs` to output `IdentityFile ~/.ssh/vde/vde_student`.
   - Update documentation comments in `lib/vde-path-utils`.
3. **Update Documentation:**
   - Update `docs/extending-vde.md`, `docs/Technical-Deep-Dive.md`, `docs/user-guide-intros.yml`, `docs/TESTING.md`, `docs/troubleshooting.md`, `docs/ssh-configuration.md`, `docs/requirements.md`, and `USER_GUIDE.md`.
4. **Validation:**
   - Run `bin/vde-enforce-uap.zsh` to verify ZSH purity.
   - Execute a test ignition (`vde start rust`) to empirically verify the Sovereign Handshake operates over the new identity.

## Verification
- Execution of `bin/vde-enforce-uap.zsh` yielding a `[UAP-SUCCESS]`.
- Successful end-to-end boot of the `vde-rust` container, verifying the key was located/forged and the SSH bridge operates smoothly.
