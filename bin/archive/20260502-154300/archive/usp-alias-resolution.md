# VDE Implementation Plan: USP Alias Resolution (1.3.1-STEP)
<!-- @shared-law (Forge Component) -->

## Objective
Implement dynamic alias hydration script resolution to enforce Universal Script Parity (USP) without redundant symlinks, ensuring the Beskar Registry (`data/vm-types.json`) acts as the Sole Source of Truth.

## Background & Motivation
The previous implementation satisfied USP by creating a physical symlink in `scripts/setup/` for every registered alias (e.g., `py-init.zsh -> python-init.zsh`). This cluttered the Armory, increased audit overhead for the UAP Sentinel, and risked drift from the registry.

## Scope & Impact
- `lib/vm-common`: Centralize alias distillation.
- `bin/uninstall-vm-type`: Use dynamic resolution for cleanup.
- `tests/features/steps/usp_steps.py`: Use dynamic resolution for USP tests.
- `scripts/setup/`: Purge redundant symlinks.

## Proposed Solution (Implemented & Tested)
1. **Dynamic Ritual**: Created `vde_get_hydration_script` in `lib/vm-common` that maps an alias to its primary custom command.
2. **Cleanup Integration**: Updated `bin/uninstall-vm-type` to use the new ritual.
3. **Red Gauntlet (TDD)**: Added BDD scenario in `tests/features/core-infrastructure/usp-validation.feature` to certify alias distillation.
4. **Armory Purge**: Removed all redundant symlinks from `scripts/setup/`.

## Verification & Testing
- The full Core Infrastructure suite passed (100% Green) after implementation.
- The new `vde_get_hydration_script` was empirically certified to correctly distill all 54 registered aliases.

## Migration & Rollback
No user intervention is required. The system automatically utilizes the new resolution ritual. To rollback, revert the changes in `lib/vm-common` and recreate the symlinks using a simple loop over the `data/vm-types.json` aliases.