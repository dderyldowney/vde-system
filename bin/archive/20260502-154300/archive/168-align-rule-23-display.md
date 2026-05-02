# Implementation Plan: Align Rule 23 (display vs display_name)
<!-- @shared-law (Forge Component) -->

## Objective
Align Rule 23 and the 8-Field Registry standard across the entire codebase to consistently use `display` instead of `display_name`, and pluralize `service_port` to `service_ports`. This addresses the architectural fracture between the Beskar Registry (JSON) and the runtime state generation, ensuring total alignment with the Sovereign Baseline.

## Key Files & Context
- **Documentation & Specs:** `gemini.md`, `data/vm-types.conf` (header), `docs/Technical-Deep-Dive.md`, `docs/extending-vde.md`.
- **Core Libraries & Tools:** `lib/vm-common`, `lib/vde-ssh`, `bin/vde-info`, `bin/vde-ps`, `bin/list-vms`, `bin/add-vm-type`.
- **Tests & Scripts:** `tests/scripts/generate_user_guide.py`, `tests/features/steps/vm_common.py`, `tests/features/steps/critical_steps.py`, `tests/features/steps/jupyterlab_steps.py`.

## Implementation Steps
1. **Update Documentation & Config Headers**:
   - `gemini.md`: Update Rule 23 and Section 2 to use `display`, `service_ports`, `ssh_port`.
   - `data/vm-types.conf`: Update the header comment.
   - `docs/Technical-Deep-Dive.md`: Update Section 2, item 1.
   - `docs/extending-vde.md`: Update the table and format strings.
2. **Update Core Libraries & CLI Tools**:
   - `lib/vm-common`: Rename `get_vm_display_name` to `get_vm_display`. Update format comments.
   - `bin/vde-info`, `bin/vde-ps`, `bin/list-vms`: Update calls from `get_vm_display_name` to `get_vm_display`. Update JSON keys from `display_name` to `display`.
   - `lib/vde-ssh`: Rename local variables `display_name` to `display`.
   - `bin/add-vm-type`: Rename `DISPLAY_NAME` to `DISPLAY`.
3. **Update Test Scripts & Helpers**:
   - `tests/scripts/generate_user_guide.py`: Update variable names and parser comments.
   - `tests/features/steps/vm_common.py`: Update parsing comments.
   - `tests/features/steps/critical_steps.py`: Change `SERVICE_PORT` to `SERVICE_PORTS` where referring to the template variable.
   - `tests/features/steps/jupyterlab_steps.py`: Update assertions to use `service_ports`.

## Verification & Testing
- Run `bin/vde-enforce-uap.zsh` to ensure UAP compliance.
- Run test suite: `python3 -m behave tests/features/` to verify tests pass and no functional regression occurred.
- Verify no remaining instances of `display_name` exist in `bin/`, `lib/`, `data/`, or `docs/`.