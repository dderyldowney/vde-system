# [CONSOLIDATED] - CONTENT MOVED TO plans/plan.md


# Fortification Plan: VDE Initialization (vde-init)

## Objective
Ensure `vde init` guarantees a complete transition from a raw clone to a battle-ready state by managing the SSH keys, explicitly priming the SSH configuration from the canonical artifact, and building the foundational `vde-base` image.

## Key Files & Context
- `bin/vde-init`: Needs explicit steps for key generation, config copying (priming the pump), and base image building.
- `lib/vde-ssh`: Remains unchanged. `generate_vm_ssh_config` continues to regenerate from scratch for dynamic operations, while `vde-init` handles the initial prime.

## Implementation Steps

### 1. Fortify `bin/vde-init`
- **Explicit Key Generation**: Add an explicit check and call to `ssh-keygen` or ensure `validate_or_create_ssh_key` is called reliably to forge the key pair before any other SSH operations, guaranteeing its presence.
- **Config Priming**: Add a dedicated step to explicitly copy the newly generated artifact `${VDE_ROOT_DIR}/configs/ssh/config` to `${VDE_SSH_CONFIG}`. This acts as a known-good primer for the initial state.
- **Base Image Ignition**: Add a new function `vde_init_build_base_image` that executes `${VDE_ROOT_DIR}/bin/vde-rebuild --vm base`. This ensures the `vde-base` image is baked with the newly synchronized public SSH keys immediately after initialization.

## Verification & Testing
- Run `bin/vde-init -f` to simulate a fresh initialization.
- Verify the SSH key pair is successfully generated in `~/.ssh/vde/`.
- Verify `~/.ssh/vde/config` is successfully primed from `configs/ssh/config`.
- Verify the `vde-base` image is built and exists in Docker.
- Run `bin/vde-spine-check.zsh` to ensure Pillar IV (SSH) remains unbroken.
- Execute the Proof of Life test to certify the Heartbeat.