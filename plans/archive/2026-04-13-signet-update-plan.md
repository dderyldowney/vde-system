# Sovereign Integration Ritual Implementation Plan
<!-- @shared-law (Forge Component) -->

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Incorporate the Sovereign Branching Strategy and GitHub PR Workflow into the core instructions of the VDE. This establishes the "Signet of an Update" for all future development missions, ensuring strict adherence to the branch lifecycle and automated issue linking.

**Architecture:** 
1. Update `docs/VDE-SPEC.md` with a new authoritative section detailing the Branching Strategy.
2. Update the "Supreme Prohibitions (A–O)" in both `GEMINI.md` and `.gemini/instructions.md` to include a new rule "P. The Sovereign Branching Law", expanding the Resol'nare.

**Tech Stack:** Markdown documentation updates.

---

### Task 1: Update the Sovereign Authority (VDE-SPEC.md)

**Files:**
- Modify: `docs/VDE-SPEC.md`

- [ ] **Step 1: Add Section 6 to VDE-SPEC.md**
Append a new section detailing the Branching Strategy and GitHub Workflow.

```markdown
## 6. The Sovereign Branching Strategy

The Forge strictly enforces the following Git lifecycle to maintain the purity of the Baseline:
1.  **`main` (The Sovereign Baseline)**: The stable production branch. Represents immutable releases.
2.  **`develop` (The Anvil)**: The primary integration branch.
3.  **Feature Branches (The Strike)**: All work MUST occur on a feature-named branch (e.g., `feat/name`) branching off `develop`.
4. **The GitHub Workflow (The Signet)**: 
    - **Issue Creation**: Missions must be recorded via `gh issue create`.
    - **Linking**: Commits or PR bodies MUST link the issue (e.g., `Closes #123`).
    - **Acceptance & Deletion**: A feature branch is merged into `develop` ONLY when accepted. It MUST be deleted immediately following the merge.
```

### Task 2: Expand the Resol'nare (GEMINI.md & .gemini/instructions.md)

**Files:**
- Modify: `GEMINI.md`
- Modify: `.gemini/instructions.md`

- [ ] **Step 1: Update the Resol'nare Title**
Change `## **THE RESOL’NARE: SUPREME PROHIBITIONS (A–N)**` (or A-O) to `## **THE RESOL’NARE: SUPREME PROHIBITIONS (A–P)**` in both files.

- [ ] **Step 2: Append Rule P**
Add the following bullet point to the end of the Resol'nare list in both files:

```markdown
* **P. The Sovereign Branching Law (The Signet)**:
    * `main` is production. `develop` is the primary integration branch. All work MUST occur on feature branches originating from `develop`.
    * Work MUST be tracked via GitHub Issues (`gh issue create`) and linked in PRs.
    * Feature branches are merged to `develop` ONLY upon acceptance and MUST be deleted immediately after.
```

### Task 3: Review and Commit

**Files:**
- Execute: Git commands

- [ ] **Step 1: Verify the Markdown formatting**
Review `docs/VDE-SPEC.md`, `GEMINI.md`, and `.gemini/instructions.md` to ensure the new sections render correctly and match the document's tone.

- [ ] **Step 2: Commit the changes**
Commit the documentation updates with a Conventional Commits message.
`git commit -m "docs(core): codify Branching Strategy and GitHub workflow into core mandates (The Signet)"`