# [CONSOLIDATED] - CONTENT MOVED TO plans/plan.md
<!-- @shared-law (Forge Component) -->


# @System-Spine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish the **System-Spine** as a cognitive context and implement empirical verification of the core tetrad (Zsh, Git, Docker, SSH) to achieve **1.3.0 The Sovereign Baseline** certification.
 This plan codifies the **Proof of Life** standard (init, create, rebuild, start, enter, stop, remove).

**Architecture:** The ritual begins with the **Four Pillars Gateway**, verifying tool-chain capability before VDE-specific hydration. A lightweight, silent ZSH script `bin/vde-spine-check.zsh` will perform functional challenges for each of the four pillars. This script will be integrated into `bin/vde` as a mandatory pre-flight check. The System-Spine is codified as a cognitive context for all VDE operations and is finalized with the `@system-spine` git tag.

**Tech Stack:** Zsh, Docker, Git, SSH, Behave (Python).

---

### Task 1: Create the Empirical Spine-Check Script

**Files:**
- Create: `bin/vde-spine-check.zsh`

- [ ] **Step 1: Write the failing test**
Run: `[[ -f bin/vde-spine-check.zsh ]] && echo "Exists" || echo "Missing"`
Expected: `Missing`

- [ ] **Step 2: Implement the Pillar I check (Zsh)**
```zsh
#!/usr/bin/env zsh
# Pillar I: Zsh
if [[ -z "${ZSH_VERSION}" ]] || ! [[ "${ZSH_VERSION}" =~ "^5\." ]]; then
    echo "[CRITICAL] Pillar I (Zsh) failed: Zsh 5.0+ required." >&2
    exit 1
fi
```

- [ ] **Step 3: Implement the Pillar II check (Git)**
```zsh
# Pillar II: Git
if ! command -v git &>/dev/null; then
    echo "[CRITICAL] Pillar II (Git) failed: git not found." >&2
    exit 1
fi
local git_test_dir=$(mktemp -d)
(cd "${git_test_dir}" && git init --quiet && rm -rf .git) || { echo "[CRITICAL] Pillar II (Git) failed: git init failed."; exit 1; }
rmdir "${git_test_dir}"
```

- [ ] **Step 4: Implement the Pillar III check (Docker)**
```zsh
# Pillar III: Docker
if ! docker info &>/dev/null; then
    echo "[CRITICAL] Pillar III (Docker) failed: Docker daemon not responsive." >&2
    exit 1
fi
if ! docker run --rm alpine echo 'Forge Active' | grep -q 'Forge Active'; then
    echo "[CRITICAL] Pillar III (Docker) failed: Alpine diagnostic probe failed." >&2
    exit 1
fi
```

- [ ] **Step 5: Implement the Pillar IV check (SSH)**
```zsh
# Pillar IV: SSH
if ! ssh-add -l | grep -q "vde_student"; then
    # Attempt to add if missing
    local vde_key="${HOME}/.ssh/vde/vde_student"
    if [[ -f "${vde_key}" ]]; then
        ssh-add "${vde_key}" &>/dev/null || { echo "[CRITICAL] Pillar IV (SSH) failed: Failed to add vde_student identity."; exit 1; }
    else
        echo "[CRITICAL] Pillar IV (SSH) failed: vde_student identity not found at ${vde_key}." >&2
        exit 1
    fi
fi
```

- [ ] **Step 6: Make script executable and commit**
Run: `chmod +x bin/vde-spine-check.zsh`
```bash
git add bin/vde-spine-check.zsh
git commit -m "feat: add @system-spine empirical check script"
```

---

### Task 2: Integrate Silent Spine-Check and 'create' command into bin/vde

**Files:**
- Modify: `bin/vde`

- [ ] **Step 1: Write the failing test for Spine-Check integration**
Run: `grep "vde-spine-check.zsh" bin/vde`
Expected: (Empty)

- [ ] **Step 2: Update bin/vde to include the check**
Insert after `vde-enforce-uap.zsh` call.
```zsh
# Enforce @system-spine tetrad (Section 16)
# This is the cognitive context and operational spine
"${VDE_ROOT_DIR}/bin/vde-spine-check.zsh" --quiet || exit 1
```

- [ ] **Step 3: Implement 'vde create' command**
Add `create)` case to the command router, mapping it to `vde-rebuild` or ensuring the image exists.
```zsh
    create)
        shift
        # Map create to build-and-start or simply ensuring image exists
        "${VDE_ROOT_DIR}/bin/vde-rebuild" "$@"
        ;;
```

- [ ] **Step 4: Verify integration**
Run: `bin/vde help`
Expected: Command runs successfully (spine check passes silently).

- [ ] **Step 5: Commit**
```bash
git add bin/vde
git commit -m "feat: integrate system-spine cognitive check and 'create' command into CLI"
```

---

### Task 3: Codify "The Proof of Life - The Contract"

**Files:**
- Create: `tests/features/core-infrastructure/proof-of-life-the-contract.feature`

**Mandate: Ghost Registry Hygiene**
The `plans/scripts/git-test/` directory MUST be purged before and after every test run to prevent nested `.git` objects from corrupting the Hub's index.

- [ ] **Step 0: Ensure the **Four Pillars Gateway** (`gateway-pillars.feature`) is executed and passed as the first scenario of the Proof of Life ritual.**

- [ ] **Step 1: Write "The Contract" BDD Feature**
```gherkin
@system-spine @critical-path @contract
Feature: The Proof of Life - The Contract
  As an Alor of the VDE
  I require empirical proof that a Spoke can be fully managed
  So that the fundamental building block of the platform is verified

  Scenario: The Sovereign Lifecycle - From Forge to Quench
    # 1. The Forge (Create)
    Given I have a valid VM definition for "python" in the Beskar Registry
    When I execute "bin/vde create python"
    Then the Docker image "vde-python" should exist on the Hub
    And the return code should be 0

    # 2. The Ignition (Start)
    When I execute "bin/vde start python"
    Then a container named "vde-python" should be running
    And the SSH bridge to "python" should be established
    And the return code should be 0

    # 3. The Reinforcement (Rebuild)
    When I execute "bin/vde rebuild python"
    Then the command should succeed
    And the Docker image "vde-python" should exist on the Hub
    And the container "vde-python" should be running
    And the return code should be 0

    # 4. The Handshake (Enter & Shell Execution)
    # Note: We use 'vde enter' to prove orchestration, NOT raw SSH.
    When I execute "bin/vde enter python --command 'echo \"The Contract is Signed\"'"
    Then the output should contain "The Contract is Signed"
    And the command should be executed as the "vde_student" identity
    And the return code should be 0

    # 5. The Quench (Stop)
    When I execute "bin/vde stop python"
    Then the container "vde-python" should not be running
    And the return code should be 0

    # 6. The Dissolution (Remove)
    When I execute "bin/vde rm python"
    Then the container "vde-python" should not exist
    And the return code should be 0

  Scenario: The Expansion Mandate - Dynamic Registration (Packages)
    Given the 4 Pillars (Zsh, Git, Docker, SSH) have passed their individual proofs
    When I execute "bin/vde add --quiet --pkgs 'htop' dynamic-pkg-vm"
    Then the command should succeed
    And the VM "vde-dynamic-pkg-vm" must be registered as a "lang"
    And the setup script for "dynamic-pkg-vm" must exist
    And I execute "bin/vde uninstall dynamic-pkg-vm --skip-confirm"
    Then the command should succeed

  Scenario: The Expansion Mandate - Dynamic Registration (Custom Command)
    Given the 4 Pillars (Zsh, Git, Docker, SSH) have passed their individual proofs
    When I execute "bin/vde add --quiet dynamic-cmd-vm 'echo Custom Forge'"
    Then the command should succeed
    And the VM "vde-dynamic-cmd-vm" must be registered as a "lang"
    And the setup script for "dynamic-cmd-vm" must exist
    And I execute "bin/vde uninstall dynamic-cmd-vm --skip-confirm"
    Then the command should succeed

  Scenario: The Forge Hardening - Hardened Rebuild
    Given the 4 Pillars (Zsh, Git, Docker, SSH) have passed their individual proofs
    And I have a valid VM definition for "python" in the Beskar Registry
    When I execute "bin/vde rebuild --no-cache python"
    Then the command should succeed
    And the Docker image "vde-python" should exist on the Hub
    And the return code should be 0
```

- [ ] **Step 2: Run "The Contract" feature**
Run: `python3 -m behave tests/features/core-infrastructure/proof-of-life-the-contract.feature`
Expected: FAIL (Steps not implemented yet)

- [ ] **Step 3: Implement Step Definitions**
Update `tests/features/steps/system_spine_steps.py` to handle the lifecycle steps using `bin/vde`.

- [ ] **Step 4: Verify "The Contract" PASSES**
Run: `python3 -m behave tests/features/core-infrastructure/proof-of-life-the-contract.feature`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add tests/features/core-infrastructure/proof-of-life-the-contract.feature tests/features/steps/system_spine_steps.py
git commit -m "feat: codify The Proof of Life - The Contract"
```

---

### Task 4: Final Certification and Tagging

**Files:**
- Modify: `tests/TEST_STATUS_REPORT.md`

- [ ] **Step 1: Update TEST_STATUS_REPORT.md**
```markdown
## Section 16: System-Spine Enforcement
- **Status**: PASSED (1.3.0 The Sovereign Baseline certified)
- **Pillars Verified**: Zsh, Git, Docker, SSH
- **Ignition Check**: Active in `bin/vde`
- **Cognitive Context**: Established
- **The Contract**: Verified (Proof of Life Active)
```

- [ ] **Step 2: Run full BDD suite**
Run: `python3 -m behave --tags=@system-spine`
Expected: All scenarios PASS.

- [ ] **Step 3: Apply git tag and commit final certification**
Run: `git tag -f @system-spine -m "1.3.0 The Sovereign Baseline certified"`
```bash
git add tests/TEST_STATUS_REPORT.md
git commit -m "docs: certify system-spine 1.3.0 The Sovereign Baseline"
```
