# Forge's Ingot Stash (Time-Based Pruning Ritual)
<!-- @shared-law (Forge Component) -->

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the Pruning Ritual to a time-based "Ingot Stash" system. Enforce a hard-stop deletion of all data older than the specified timeframe (default 7 days) and dynamically archive remaining artifacts older than 24 hours. Maintain full Git tracking history using `git mv` and `git rm`. Protect the current Sovereign Baseline documentation.

**Architecture:** Refactor `bin/vde-prune.zsh` to accept a `--timeframe` argument. Implement `safe_rm` and `safe_mv` functions that check `git ls-files` to determine if a file is tracked, applying the appropriate Git or standard POSIX command. Extract the `CURRENT_BASELINE` dynamically from `docs/VDE-SPEC.md`.

**Tech Stack:** Pure ZSH, `find` (`-mmin`), `git ls-files`, `awk`.

---

### Task 1: Refactor the Pruning Script

**Files:**
- Modify: `bin/vde-prune.zsh`

- [ ] **Step 1: Rewrite `bin/vde-prune.zsh` with Time-Based Logic**
Replace the contents of the script with the new Git-native, time-based engine.

```zsh
#!/usr/bin/env zsh
# VDE Pruning Ritual (Forge's Ingot Stash)
# Usage: vde prune [--timeframe <7d|3d|24h|12h>]

local _zsh_compliance_flag=${(z):-"zsh native parameter expansion"}
set -e

VDE_ROOT="${VDE_ROOT_DIR:-$HOME/VDE}"

TIMEFRAME="7d"
if [[ "$1" == "--timeframe" && -n "$2" ]]; then
    TIMEFRAME="$2"
fi

# Convert timeframe to minutes for find
local minutes=10080 # Default 7d
case "$TIMEFRAME" in
    *d) minutes=$(( ${TIMEFRAME%d} * 24 * 60 )) ;;
    *h) minutes=$(( ${TIMEFRAME%h} * 60 )) ;;
    *m) minutes=${TIMEFRAME%m} ;;
esac

# ZSH Git Tracking Check
is_tracked() {
    git -C "${VDE_ROOT}" ls-files --error-unmatch "$1" >/dev/null 2>&1
}

safe_rm() {
    local file="$1"
    if is_tracked "$file"; then
        git -C "${VDE_ROOT}" rm -qf "$file"
    else
        rm -rf "$file"
    fi
}

safe_mv() {
    local src="$1"
    local dest="$2"
    mkdir -p "$dest"
    if is_tracked "$src"; then
        # git mv requires the destination directory to be tracked or it acts on the file directly
        git -C "${VDE_ROOT}" mv "$src" "$dest/"
    else
        mv "$src" "$dest/"
    fi
}

echo "Commencing the Forge's Ingot Stash Ritual (Timeframe: ${TIMEFRAME}, ${minutes}m)..."

# Extract the Sovereign Baseline
CURRENT_BASELINE=$(head -n 1 "${VDE_ROOT}/docs/VDE-SPEC.md" | awk '{print $2}')
echo "Protecting Sovereign Baseline: ${CURRENT_BASELINE}"

# 1. Hard Stop Delete (> timeframe) "No Mercy"
for dir in logs plans plans/scripts backup docs/releases; do
    if [[ -d "${VDE_ROOT}/${dir}" ]]; then
        find "${VDE_ROOT}/${dir}" -type f -mmin +${minutes} | while read -r file; do
            filename=$(basename "$file")
            # Protect current baseline doc and contract
            if [[ "${dir}" == "docs/releases" && "$filename" == "${CURRENT_BASELINE}.md" ]]; then continue; fi
            if [[ "$filename" == "system-spine-contract.md" || "$filename" == "2026-04-13-pruning-ritual-plan.md" || "$filename" == "2026-04-13-ingot-stash-plan.md" ]]; then continue; fi
            
            echo "Deleting expired data: $filename"
            safe_rm "$file"
        done
    fi
done

# 2. Archive (Active -> Archive for items older than 24h, but within timeframe)
archive_minutes=$(( 24 * 60 ))
for dir in plans plans/scripts docs/releases; do
    if [[ -d "${VDE_ROOT}/${dir}" ]]; then
        mkdir -p "${VDE_ROOT}/${dir}/archive"
        # Find files older than 24h but not in archive directory
        find "${VDE_ROOT}/${dir}" -maxdepth 1 -type f -mmin +${archive_minutes} | while read -r file; do
            filename=$(basename "$file")
            # Protect current baseline doc, contract, and active hydration rituals
            if [[ "${dir}" == "docs/releases" && "$filename" == "${CURRENT_BASELINE}.md" ]]; then continue; fi
            if [[ "$filename" == "system-spine-contract.md" || "$filename" == *-init.zsh || "$filename" == "2026-04-13-pruning-ritual-plan.md" || "$filename" == "2026-04-13-ingot-stash-plan.md" ]]; then continue; fi
            
            echo "Archiving to Ingot Stash: $filename"
            safe_mv "$file" "${VDE_ROOT}/${dir}/archive"
        done
    fi
done

echo "The Ingot Stash Ritual is complete. The Forge is lean."
```

### Task 2: Execution and Verification

**Files:**
- Execute: `bin/vde prune --timeframe 7d`

- [ ] **Step 1: Execute the new pruning script**
Run the script to ensure it correctly identifies tracked files, applies the `git mv`/`git rm` logic, and respects the 7-day hard stop.

- [ ] **Step 2: Commit the changes**
Commit the refactored script with a Conventional Commits message indicating the upgrade to the Ingot Stash system.