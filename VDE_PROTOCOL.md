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


---

## **V. THE LAWS OF THE FORGE (GIT HOOKS)**

The VDE repository enforces its mandates through physical gatekeepers known as the "Laws of the Forge." These are version-controlled Git hooks stored in the root-level `githooks/` directory.

### **1. The Pre-Strike Sentinel**
The `pre-commit` hook is the primary guardian of the repository. It performs the following automated checks before any commit is accepted:
*   **Rule C (Zsh Purity):** Strictly blocks any script using unauthorized shebangs (e.g., `bash`, `sh`). Only `zsh` is permitted.
*   **Rule 12 (Security Law):** Scans staged changes for hardcoded credentials (API keys, secrets, passwords).
*   **Silent Spine Check:** Automatically executes the `@system-spine` check to ensure the technological pillars are active and stable.

### **2. Activation Ritual**
To activate these guardians on a new machine or after a fresh clone, you MUST run the installation script:
```zsh
./bin/install-githooks
```
This script symlinks the tracked files from `githooks/` into your local `.git/hooks/` directory, ensuring that the project's security laws are active for all contributors.
