# VDE Project Protocol (1.3.1)

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

## **VI. THE LAWS OF THE FORGE (BRANCHING)**

The VDE repository strictly enforces a Sovereign Branching Strategy to maintain the purity of the Baseline:

1. **`main` (Production):** This is the stable production branch. It represents the certified, immutable **Sovereign Baseline** of the Forge.
2. **`develop` (The Anvil):** This is the primary integration branch for all ongoing development. It is the **Default Branch** for repository operations to enable automated issue closure.
3. **Semantic Targeting:** The Forge uses semantic roles (`VDE_PRODUCTION_BRANCH`, `VDE_ANVIL_BRANCH`) codified in `lib/vde-constants` to ensure portability.
4. **Feature Branches (The Strike):** All design, creation, modification, or remediation work MUST be performed on a feature-named branch (e.g., `feat/new-vm-type`, `fix/ssh-bridge`) branching **off of the Anvil (`develop`)**.
5. **The Merge & Deletion:** Once a feature branch survives the Trial of the Gauntlet (testing) and the code is formally **accepted**, it is merged back into the Anvil (`develop`). Immediately following a successful merge, the feature branch **MUST be deleted** to keep the Forge lean and prevent history corruption.
6. **The Chronicle (Pull Requests):** The transition of code from the Strike (Feature Branch) to the Anvil (`develop`) is recorded in the Chronicle. This ritual ensures that only pure Beskar is integrated into the baseline, governed by four unbreakable laws:
    *   **The Law of the Focused Strike:** Scope is absolute. A Pull Request MUST address ONLY the objectives defined in its Signet (Issue). Tangential refactoring or unrelated modifications are forbidden; they belong in their own Strike.
    *   **The Unbreakable Link:** Every Chronicle entry MUST be forged with auto-closing keywords (e.g., `Closes #N`) linked to an authorized Signet. This ensures every line of code has a documented purpose in the history of the Forge.
    *   **The Dual-Gate Review:** Certification requires two signatures. The Chronicler (AI Agent) must verify the technical integrity, and the Alor (User) must grant the final blessing. No merge is permitted without both gates being unlocked.
    *   **The Evidence Mandate:** Trust is earned, not given. The description of every Pull Request MUST contain literal, unedited test output from the Trial of the Gauntlet. Only 100% successful verification is accepted as proof of life.

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
