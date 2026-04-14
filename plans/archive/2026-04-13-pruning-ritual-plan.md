# Pruning Ritual Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a systematic pruning schedule and `git sparse-checkout` strategy to archive old plans, logs, scripts, and docs, leaving only the Sovereign Baseline (1.3.1) and immediate previous release (1.3.0) active in the physical workspace.

**Architecture:** Use a dedicated `bin/vde-prune.zsh` script to enforce file limits (10 most recent plans/scripts, 7-day logs, 1.3.1 & 1.3.0 docs). Move older artifacts to `*/archive/` directories. Utilize Git Sparse-Checkout to hide the `archive/` directories from the local filesystem while maintaining them in the Git repository history.

**Tech Stack:** Pure ZSH, `find`, `mv`, Git Sparse-Checkout.

---

### Task 1: Initialize Archive Directories and Migration

**Files:**
- Create: `plans/archive/`
- Create: `docs/archive/`

- [ ] **Step 1: Create the archive directories**
```bash
mkdir -p plans/archive/scripts docs/archive/releases
```

- [ ] **Step 2: Move identified finished plans to the archive**
Move all finished plans from the 1.3.0 and early 1.3.1 era into `plans/archive/`.
```bash
mv plans/codify-mandalorian-creed.md plans/archive/
mv plans/empirical-spine-tests.md plans/archive/
mv plans/identity-pulse-and-hardening.md plans/archive/
mv plans/pristine-environment-implementation.md plans/archive/
mv plans/rewrite-sovereign-artifact-set.md plans/archive/
mv plans/semver-and-conventional-commits.md plans/archive/
mv plans/semver-application.md plans/archive/
mv plans/semver-formatting.md plans/archive/
mv plans/update-sovereign-artifact-set.md plans/archive/
mv plans/usp-alias-resolution.md plans/archive/
mv plans/v1.3.0-final-remediation.md plans/archive/
mv plans/vde-ci-v1.3.0-update.md plans/archive/
```

- [ ] **Step 3: Move legacy temporary scripts to the archive**
Exclude the active hydration rituals (`*-init.zsh`) and the core `system-spine-contract.md`.
```bash
mv plans/scripts/beskar-trap-plan.md plans/archive/scripts/
mv plans/scripts/commit_plan.md plans/archive/scripts/
mv plans/scripts/debug_port_alloc.zsh plans/archive/scripts/
mv plans/scripts/fifo_test.log plans/archive/scripts/
mv plans/scripts/fix-config-smelting.md plans/archive/scripts/
mv plans/scripts/fleet_rebuild_strike.zsh plans/archive/scripts/
mv plans/scripts/phase_24_bucket_1_plan.md plans/archive/scripts/
mv plans/scripts/refactor_setup_simple.zsh plans/archive/scripts/
mv plans/scripts/repro_ssh_failure.py plans/archive/scripts/
mv plans/scripts/signal_test.txt plans/archive/scripts/
mv plans/scripts/test-pulse-tdd.zsh plans/archive/scripts/
mv plans/scripts/v1.3.0-hardening-strike.md plans/archive/scripts/
mv plans/scripts/v1.3.0-spine-hardening.md plans/archive/scripts/
mv plans/scripts/vde_signal_report.txt plans/archive/scripts/
mv plans/scripts/verify-usp-hardening.zsh plans/archive/scripts/
```

### Task 2: Implement the Pruning Ritual Script

**Files:**
- Create: `bin/vde-prune.zsh`
- Modify: `bin/vde`

- [ ] **Step 1: Write `bin/vde-prune.zsh`**
```zsh
#!/usr/bin/env zsh
# VDE Pruning Ritual: Enforces retention limits on logs, plans, and scripts.
# - Logs: Delete older than 7 days.
# - Plans/Scripts: Keep last 10 runs, move remainder to archive.
# - Docs: Sovereign Baseline (1.3.1) and immediate previous (1.3.0) only.

local _zsh_compliance_flag=${(z):-"zsh native parameter expansion"}
set -e

VDE_ROOT="${VDE_ROOT_DIR:-$HOME/VDE}"
LOGS_DIR="${VDE_ROOT}/logs"
PLANS_DIR="${VDE_ROOT}/plans"
SCRIPTS_DIR="${PLANS_DIR}/scripts"
DOCS_DIR="${VDE_ROOT}/docs/releases"

echo "Commencing the Pruning Ritual..."

# 1. Prune Logs (Delete older than 7 days)
find "${LOGS_DIR}" -type f -name "*.log" -mtime +7 -delete 2>/dev/null || true
echo "Logs pruned to 7-day retention."

# 2. Prune Plans (Keep 10 most recent .md files, excluding system-spine-contract.md)
# Move older plans to archive
mkdir -p "${PLANS_DIR}/archive"
# zsh array of files sorted by modification time (newest first)
plans=(${PLANS_DIR}/*.md(OmN))
# filter out the contract
active_plans=()
for p in "${plans[@]}"; do
    if [[ "$(basename "$p")" != "system-spine-contract.md" ]]; then
        active_plans+=("$p")
    fi
done

if (( ${#active_plans[@]} > 10 )); then
    for old_plan in "${active_plans[@]:10}"; do
        mv "$old_plan" "${PLANS_DIR}/archive/"
        echo "Archived plan: $(basename "$old_plan")"
    done
fi

# 3. Prune Temp Scripts (Keep 10 most recent, excluding hydration rituals *-init.zsh)
mkdir -p "${SCRIPTS_DIR}/archive"
scripts=(${SCRIPTS_DIR}/*(OmN))
active_scripts=()
for s in "${scripts[@]}"; do
    if [[ ! "$(basename "$s")" == *-init.zsh ]] && [[ -f "$s" ]]; then
        active_scripts+=("$s")
    fi
done

if (( ${#active_scripts[@]} > 10 )); then
    for old_script in "${active_scripts[@]:10}"; do
        mv "$old_script" "${SCRIPTS_DIR}/archive/"
        echo "Archived script: $(basename "$old_script")"
    done
fi

# 4. Prune Docs (Keep only 1.3.1.md and 1.3.0.md)
mkdir -p "${VDE_ROOT}/docs/archive/releases"
for doc in "${DOCS_DIR}"/*.md(N); do
    filename=$(basename "$doc")
    if [[ "$filename" != "1.3.1.md" && "$filename" != "1.3.0.md" ]]; then
        mv "$doc" "${VDE_ROOT}/docs/archive/releases/"
        echo "Archived documentation: $filename"
    fi
done

echo "The Pruning Ritual is complete. The Forge is lean."
```

- [ ] **Step 2: Make the script executable**
```bash
chmod +x bin/vde-prune.zsh
```

- [ ] **Step 3: Link to the Orchestrator (`bin/vde`)**
Add `prune` as a command in `bin/vde` case statement:
```bash
    prune)
        exec "${VDE_ROOT_DIR}/bin/vde-prune.zsh" "$@"
        ;;
```

### Task 3: Git Sparse-Checkout Implementation

**Files:**
- Modify: Git Working Tree
- Modify: `README.md` (or `VDE_INSTALL.md`) to document sparse checkout

- [ ] **Step 1: Commit the archived files**
```bash
git add plans/ docs/
git commit -m "chore(archive): move finished plans and legacy scripts to archive directories"
```

- [ ] **Step 2: Enable Git Sparse-Checkout**
Initialize sparse-checkout in cone mode to keep everything except the newly created archive directories.
```bash
git sparse-checkout init --cone
git sparse-checkout set "/*" "!plans/archive" "!docs/archive" "!plans/scripts/archive"
```

- [ ] **Step 3: Document the Sparse-Checkout process**
Add a note to `README.md` or a relevant docs file explaining how to access archives:
```markdown
### Accessing Archives
The VDE uses Git Sparse-Checkout to keep the working tree lean by hiding the \`plans/archive/\` and \`docs/archive/\` directories. The files remain in the Git repository history.

To view the archives locally, disable sparse-checkout:
\`\`\`zsh
git sparse-checkout disable
\`\`\`
To hide them again:
\`\`\`zsh
git sparse-checkout init --cone
git sparse-checkout set "/*" "!plans/archive" "!docs/archive" "!plans/scripts/archive"
\`\`\`
```

- [ ] **Step 4: Commit the pruning script and docs**
```bash
git add bin/vde-prune.zsh bin/vde README.md
git commit -m "feat(core): implement pruning ritual and sparse-checkout strategy"
```

- [ ] **Step 5: Verify working tree state**
Run `ls plans/archive/` and expect it to not exist in the physical tree, while `git ls-files | grep plans/archive/` proves they are still tracked in git.