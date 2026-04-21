# Sovereign Tagging Specification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish absolute architectural tag literacy by implementing the multi-format syntax and universal regex detection across all VDE files.

**Architecture:** We will first update the Supreme Law and the UAP Sentinel with the new Literate Syntax and Universal Regex. Then, we will execute a project-wide strike to remediate all files into their native, valid tag formats.

**Tech Stack:** ZSH, Markdown, JSON, YAML, Dockerfile

---

### Task 1: Codify Literate Tagging Syntax (@shared-law)

**Files:**
- Modify: `GEMINI.md` (via `.gemini/instructions.md`)

- [ ] **Step 1: Update Tag Pattern & Positioning Rule**
Replace the simple `# @tag` instructions with the new **Literate Syntax Table** provided by the research swarm.

- [ ] **Step 2: Update Commitment Gate**
Ensure the instructions explicitly mention that tags must be syntactically valid for their file type.

- [ ] **Step 3: Commit**
```bash
git add .gemini/instructions.md
git commit -m "docs(shared-law): codify sovereign tagging specification for literate headers"
```

### Task 2: Hardening the Sentinel (@forge)

**Files:**
- Modify: `bin/vde-enforce-uap.zsh`

- [ ] **Step 1: Integrate Universal Regex**
Update the `audit_file_content` function to use the swarm-provided regex:
`^\s*(?:#|<!--|//|"|--|;)\s*@(armor|forge|shared-law)(?:"?:\s*")?\s*\(([^)]+)\)\s*(?:-->|")?,?\s*$`

- [ ] **Step 2: Commit**
```bash
git add bin/vde-enforce-uap.zsh
git commit -m "feat(forge): upgrade UAP sentinel with universal architectural regex"
```

### Task 3: 100% Literate Remediation Strike (@forge)

**Goal:** Convert all ~200 files to their correct, language-native tag format.

**Instructions:**
- **ZSH/Python/Shell**: Use `# @tag (Effect)`
- **JSON**: Use `"@tag": "(Effect)",`
- **Markdown**: Use `<!-- @tag (Effect) -->`
- **YAML/Dockerfile**: Use `# @tag (Effect)`

- [ ] **Step 1: Remediation Sweep**
Iterate through all files and apply the correct syntax based on extension.
*(Agent Note: Use a subagent swarm to handle the high volume of edits efficiently).*

- [ ] **Step 2: Verify compliance**
Run `bin/vde-enforce-uap.zsh`. Expect **100% GREEN**.

- [ ] **Step 3: Commit**
```bash
git add .
git commit -m "chore(core): achieve 100% literate architectural tagging compliance"
```

### Task 4: Enshrine Specification in the Gospel (@shared-law)

**Files:**
- Modify: `docs/VDE-SPEC.md`, `docs/SOVEREIGN_CHARTER.md`, `ARCHITECTURE.md`

- [ ] **Step 1: Document the Standard**
Add the **Sovereign Tagging Specification** (Positioning Law, Syntax Table, and Purpose) to the appropriate sections of the SAS documents.

- [ ] **Step 2: Maintain Version**
Ensure no version numbers are incremented during this update.

- [ ] **Step 3: Commit**
```bash
git add docs/ ARCHITECTURE.md
git commit -m "docs(shared-law): enshrine literate tagging specification in the Gospel"
```

### Task 5: Final Verification & PR Update (@forge)

- [ ] **Step 1: Create Signet & Chronicle**
Open the final compliance Issue and PR.

- [ ] **Step 2: Proof of Life**
Run full lifecycle tests.
