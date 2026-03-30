# Plan: Phase P - Architectural Refactoring (Directory Reordering)

## Objective
Reorganize `configs/docker/` into `languages/` and `services/` subdirectories to improve project structure and scalability.

**Example Change:**
- **Before:** `configs/docker/python/` and `configs/docker/postgres/`
- **After:** `configs/docker/languages/python/` and `configs/docker/services/postgres/`

## Core Mandate: ZSH ONLY
- All scripts must use `#!/usr/bin/env zsh`.
- No `.sh` extensions allowed. Use `.zsh` or extensionless script names.
- All temporary scripts used for migration must be Zsh.

## Implementation Plan

### Phase 1: Code & Template Updates (Non-destructive)
1.  **`lib/vm-common`**:
    - Add `get_vm_category(vm_name)` to return "languages" or "services" based on VM type.
    - Update `ensure_vm_directories` to use category-specific paths.
    - Update `vm_is_created` to check for config trio in the new category paths.
2.  **`lib/vde-docker`**:
    - Refactor `get_compose_file` to resolve paths using `get_vm_category` (with backward-compatible fallback).
3.  **CLI Scripts**:
    - Update `bin/create-virtual-for` output path.
    - Update `bin/vde-rebuild` recursive scan and build logic.
4.  **Templates**:
    - Update `templates/compose-language.yml` and `templates/compose-service.yml` relative paths (`../../../../`).
5.  **Static Config**:
    - Update `data/vm-docker-config.json` paths and `data/vm-docker-config.schema.json` regex.

### Phase 2: Migration (Destructive)
1.  Create and execute `bin/migrate-configs-to-categories.zsh`.
2.  Physically move directories and update `docker-compose.yml` files on disk.

### Phase 3: Verification
1.  Run `vde list --all` to confirm all VMs found and categorized.
2.  Update BDD feature files (`tests/features/core-infrastructure/*.feature`) to use new paths.
3.  Run `behave` test suites.
4.  Supervisor Audit -> Final PASS.
