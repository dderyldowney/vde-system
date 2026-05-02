# SSH Backup Sanitization Implementation Plan
<!-- @shared-law (Forge Component) -->

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Sanitize all files in `backup/ssh/` by replacing the hardcoded personal path `$HOME` with `~`.

**Architecture:** Use a single-command bulk process with `sed` for speed and efficiency on backup files, followed by empirical verification.

**Tech Stack:** ZSH, sed

---

### Task 1: Research and Preparation

**Files:**
- Research: `backup/ssh/`

- [ ] **Step 1: Identify all files requiring sanitization**
Run: `grep -l "$HOME" backup/ssh/* | wc -l`
Expected: A count of files containing the hardcoded path.

- [ ] **Step 2: Backup the entire directory (Precaution)**
Run: `cp -r backup/ssh/ backup/ssh_pre_sanitization/`
Expected: `backup/ssh_pre_sanitization/` directory created.

### Task 2: Execution

**Files:**
- Modify: All files in `backup/ssh/`

- [ ] **Step 3: Run the bulk replacement**
Run: `bin/vde-enforce-uap.zsh sed -i '' 's|$HOME|~|g' backup/ssh/*`
Expected: All occurrences of `$HOME` replaced with `~`.

### Task 3: Verification

**Files:**
- Verify: All files in `backup/ssh/`

- [ ] **Step 4: Verify zero occurrences of the hardcoded path**
Run: `grep -r "$HOME" backup/ssh/`
Expected: No output (zero matches).

- [ ] **Step 5: Verify sample files contain the new pattern**
Run: `grep "~/.ssh" backup/ssh/config.backup.20260326_131148 | head -n 5`
Expected: Output showing `~/.ssh` instead of `$HOME/.ssh`.

- [ ] **Step 6: Remove the temporary backup if successful**
Run: `rm -rf backup/ssh_pre_sanitization/`
Expected: Temporary directory removed.

### Task 4: Reporting

- [ ] **Step 7: Final report in Sovereign Reporting Format**
Document the process according to Rule 18 and the Rule Spine.
