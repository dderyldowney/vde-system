# Remediate IS240 & IS241 (@forge & @shared-law) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete architectural tagging for the Forge and Shared-Law domains, focusing on mythos documents, Data Authority files, and the Sovereign Artifact Set. Also implement UAP hardening for the `plans/` directory.

**Architecture:** We will apply the appropriate architectural tags to all remaining Project 2 (@forge) and Foundation (@shared-law) artifacts. We will also harden the UAP enforcer to prevent Rule 3 violations (Ghost Zones) in the `plans/` directory.

**Tech Stack:** ZSH, Markdown, JSON

---

### Task 1: Tag Forge Mythos Documents (@forge)

**Files:**
- Modify: `data/vde_core/forge_mythos.md`, `data/vde_core/mandalorian_mythos.md`

- [ ] **Step 1: Write the failing test**
Run `grep -L "@forge" data/vde_core/*.md` to verify they are untagged.

- [ ] **Step 2: Write minimal implementation**
Prepend `<!-- @forge (Mandalorian Mythos) -->` to the top of both files.

- [ ] **Step 3: Run test to verify it passes**
Run `grep -l "@forge" data/vde_core/*.md` to verify the fix.

- [ ] **Step 4: Commit**
```bash
git add data/vde_core/
git commit -m "docs(forge): apply architectural tags to mythos documents"
```

### Task 2: Tag Data Authority Files (@shared-law)

**Files:**
- Modify: `data/vm-types.conf`, `data/vm-types.json`

- [ ] **Step 1: Write the failing test**
Run `grep -L "@shared-law" data/vm-types.conf data/vm-types.json` to verify they are untagged.

- [ ] **Step 2: Write minimal implementation**
1. Add `# @shared-law (Beskar Registry Source)` to the top of `data/vm-types.conf`.
2. Add `"@shared-law": "Beskar Registry Authority",` as the first key-value pair in `data/vm-types.json`.

- [ ] **Step 3: Run test to verify it passes**
Run `grep -l "@shared-law" data/vm-types.conf data/vm-types.json` to verify the fix.

- [ ] **Step 4: Commit**
```bash
git add data/
git commit -m "chore(shared-law): apply architectural tags to Data Authority files"
```

### Task 3: Tag Sovereign Artifact Set (@shared-law)

**Files:**
- Modify: `docs/ARCHITECTURE.md`, `docs/TECHNICAL_DEEP_DIVE.md`, `docs/SOVEREIGN_CHARTER.md`, `docs/VDE-SPEC.md`, `USE_CASES.md`, `VDE_ANALYSIS.md`, `PROJECT_STATUS.md`, `RELEASE_NOTES.md`

- [ ] **Step 1: Write the failing test**
Run `grep -L "@shared-law" docs/ARCHITECTURE.md docs/TECHNICAL_DEEP_DIVE.md docs/SOVEREIGN_CHARTER.md docs/VDE-SPEC.md USE_CASES.md VDE_ANALYSIS.md PROJECT_STATUS.md RELEASE_NOTES.md` to verify they are untagged.

- [ ] **Step 2: Write minimal implementation**
Prepend `<!-- @shared-law (Sovereign Artifact Set) -->` to the top of each file.

- [ ] **Step 3: Run test to verify it passes**
Run the grep command from Step 1 again; it should return no results.

- [ ] **Step 4: Commit**
```bash
git add .
git commit -m "docs(shared-law): apply architectural tags to Sovereign Artifact Set"
```

### Task 4: UAP Hardening (Rule 3 Enforcement)

**Files:**
- Modify: `bin/vde-enforce-uap.zsh`

- [ ] **Step 1: Write the failing test**
Create a ghost directory `plans/ghost` and run `bin/vde-enforce-uap.zsh`. It should not currently flag it as a violation of Rule 3 (it only checks for `conductor/` currently).

- [ ] **Step 2: Write minimal implementation**
Update `bin/vde-enforce-uap.zsh` to include a check for unauthorized subdirectories in `plans/`. Only `plans/scripts/` and `plans/archive/` are authorized.

```zsh
# Authorized plans/ subdirectories
AUTHORIZED_PLANS_DIRS=("scripts" "archive")

# Check for unauthorized plans/ directories
for dir in plans/*(/N); do
    dir_name="${dir:t}"
    if [[ ! " ${AUTHORIZED_PLANS_DIRS[@]} " =~ " ${dir_name} " ]]; then
        echo -e "${RED}[UAP-ERROR]${NC} Unauthorized directory found in plans/: ${dir_name}"
        echo "Protocol Violation: Rule 3 (Ghost Zone Prohibition)."
        errors=$((errors + 1))
    fi
done
```

- [ ] **Step 3: Run test to verify it passes**
Run `bin/vde-enforce-uap.zsh`. It should now flag `plans/ghost`. Remove `plans/ghost` and run it again; it should pass.

- [ ] **Step 4: Commit**
```bash
git add bin/vde-enforce-uap.zsh
git commit -m "feat(forge): harden UAP enforcer for Rule 3 compliance"
```
