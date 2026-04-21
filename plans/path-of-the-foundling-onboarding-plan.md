# Path of the Foundling Onboarding Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish `vde path-of-the-foundling` as the primary, interactive entry point for new students in all onboarding documentation.

**Architecture:** Transition documentation from static command lists to interactive rituals. Lead with the Path, retain `vde init` as a secondary/repair tool.

**Tech Stack:** Markdown

---

### Task 1: Update README.md (Primary Entry)

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Locate existing Ignition section**
Search for the "Ignition (The Journey Begins)" section in `README.md`.

- [ ] **Step 2: Replace manual init with the Path**
Replace the code block:
```zsh
# Ignite the Forge (Mandatory Ritual)
vde init
```
With:
```zsh
# Take the Path of the Foundling (Interactive Onboarding)
vde path-of-the-foundling
```
Add a brief sentence explaining that this script automates ignition, spine verification, and your first Spoke creation.

- [ ] **Step 3: Verify links and formatting**
Ensure the "Next Rituals" section still points correctly to `USER_GUIDE.md` and `docs/quick-start.md`.

- [ ] **Step 4: Commit**
```bash
git add README.md
git commit -m "docs(forge): lead with path-of-the-foundling in README"
```

### Task 2: Update USER_GUIDE.md (Installation Ritual)

**Files:**
- Modify: `USER_GUIDE.md`

- [ ] **Step 1: Update Installation ritual**
Find section `1. Installation & Ignition`.
Replace `# Ignite the Forge (Sets up networks and keys)` command `vde init` with `vde path-of-the-foundling`.

- [ ] **Step 2: Update Reference section**
Ensure `vde init` remains in the "Essential Commands" table for repair/manual use, but add `vde path-of-the-foundling` as the "Recommended Onboarding Ritual".

- [ ] **Step 3: Commit**
```bash
git add USER_GUIDE.md
git commit -m "docs(forge): update User Guide installation to use interactive induction"
```

### Task 3: Refactor docs/FOUNDLING_GUIDE.md (Guided Induction)

**Files:**
- Modify: `docs/FOUNDLING_GUIDE.md`

- [ ] **Step 1: Rename Ignition section**
Rename "Initialization (The Ignition)" to "The Path of the Foundling (Interactive Induction)".

- [ ] **Step 2: Update ritual instructions**
Replace the `vde init` block with `vde path-of-the-foundling`.
Update the text to explain that the script will ask for permission at each step (Ignition -> Spine Check -> Spoke Creation).

- [ ] **Step 3: Align Step-by-Step guide**
Update subsequent sections to reflect that the Python Spoke is created during the Path, rather than as a separate manual step.

- [ ] **Step 4: Commit**
```bash
git add docs/FOUNDLING_GUIDE.md
git commit -m "docs(forge): refactor Foundling Guide around the interactive induction"
```

### Task 4: Update docs/quick-start.md (The First Strike)

**Files:**
- Modify: `docs/quick-start.md`

- [ ] **Step 1: Update code block**
Update the "Ignite the Forge" ritual code block to use `vde path-of-the-foundling`.

- [ ] **Step 2: Update "What Just Happened?" section**
Modify the explanation to reflect the consolidated interactive flow.
Example: "When you ran `vde path-of-the-foundling`, you completed the Ignition, the Spine Check, and your first Spoke creation."

- [ ] **Step 3: Commit**
```bash
git add docs/quick-start.md
git commit -m "docs(forge): synchronize quick-start with interactive onboarding"
```

### Task 5: Final Review & UAP Verification

- [ ] **Step 1: Run UAP Audit**
```bash
bin/vde-enforce-uap.zsh
```

- [ ] **Step 2: Check for dead links**
Ensure no documentation links were broken by the refactor.

- [ ] **Step 3: Commit all**
```bash
git add .
git commit -m "docs(forge): complete Path of the Foundling onboarding integration"
```
