# VDE Project Protocol (v2.0.5)

## Authoritative Tooling Mandate
This project uses a custom orchestration layer. Direct Docker commands are strictly forbidden for environment interaction.

### 1. The "Anti-Exec" Rule
- **NEVER** use `docker exec` to enter a container.
- **ALWAYS** use `bin/vde enter <alias>` to ensure SSH bridge and environment variables are active.

### 2. Ignition & Lifecycle
- **NEVER** use `docker run` or `docker start` manually.
- **ALWAYS** use `bin/vde start <alias>` to exercise the port-mapping and volume-mounting logic.
- **ALWAYS** use `bin/vde rebuild <alias>` for image generation to ensure the `CUSTOM_BUILD_CMD` logic is applied.

### 3. Data Authority (Material Truth)
- All configuration resides in `data/vm-types.json`.
- The library logic resides in `lib/vm-common`.
- Schema validation is handled by `vde-core`.

### 4. Identity
- All development happens as `devuser`.
- Root is only used for system-level background processes (like `sshd`).

