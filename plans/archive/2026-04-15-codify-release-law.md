# Codify Sovereign Release Law Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Hardened the Release Ritual by codifying that step tagging and releases MUST occur exclusively on the `main` branch, synchronizing the Sovereign Artifact Set to seven files across all Gospel documents.

**Architecture:** This strike modifies the Gospel documents (`VDE-SPEC.md`, `ARCHITECTURE.md`, `Technical-Deep-Dive.md`) and the Behavioral Mandates (`AGENTS.md`) to ensure absolute consistency in the Release Ritual.

**Tech Stack:** Zsh, Markdown, VDE Rule Spine.

---

### Task 1: Update VDE-SPEC.md (The Gospel Lead)

**Files:**
- Modify: `/Users/dderyldowney/VDE/docs/VDE-SPEC.md`

- [ ] **Step 1: Update Section 4 with the Release Law and Ritual**

Modify Section 4 to include the branch restrictions and the 5-step Release Ritual.

```markdown
## 4. The Sovereign Branching Strategy

The Forge strictly enforces the following Git lifecycle to maintain the purity of the Baseline:
1. **`main` (The Sovereign Baseline)**: The stable production branch. Represents immutable releases. All step tagging (X.X.X) and GitHub releases MUST occur on this branch.
2. **`develop` (The Anvil)**: The primary integration branch and repository default.
3. **Feature Branches (The Strike)**: All work MUST occur on a feature-named branch (`feat/`, `fix/`, `chore/`) branching off `develop`.
4. **The Ritual**: Every mission begins with a Signet (Issue) and ends with a Chronicle (PR). Feature branches are merged to `develop` ONLY upon acceptance and MUST be deleted immediately after.
5. **The Release Ritual**: Once develop is merged into main, the merge SHA on main is tagged (e.g., 1.2.3). The GitHub Release is then created from that SHA on the main branch. Finally, this SHA is applied to the stable branch, overwriting its previous state. develop remains for development only.
```

### Task 2: Update ARCHITECTURE.md (The Strategy)

**Files:**
- Modify: `/Users/dderyldowney/VDE/docs/ARCHITECTURE.md`

- [ ] **Step 1: Update Section 4 to include the 7th file and Release Law reference**

Synchronize the count to SEVEN and include `PROJECT_STATUS.md`.

```markdown
## 4. The Sovereign Artifact Set (The Gospel)

The following seven files move as a single artifact set for every Sovereign Baseline. They must be in perfect agreement with the Forge state before any tag is struck, in strict accordance with the Sovereign Release Law:
1. `ARCHITECTURE.md` (The Strategy)
2. `TECHNICAL_DEEP_DIVE.md` (The Mechanics)
3. `RELEASE_NOTES.md` (The Archive)
4. `VDE-SPEC.md` (The Gospel Lead & Version Arbiter)
5. `USE_CASES.md` (The Audit)
6. `VDE_ANALYSIS.md` (The Engineering Verdict)
7. `PROJECT_STATUS.md` (The Live Status)
```

### Task 3: Update Technical-Deep-Dive.md (The Mechanics)

**Files:**
- Modify: `/Users/dderyldowney/VDE/docs/Technical-Deep-Dive.md`

- [ ] **Step 1: Add Section 8 for the Sovereign Artifact Set and Release Law**

Ensure the Deep-Dive reflects the decision-making authority of the 7-file set and the branch law.

```markdown
## 8. The Sovereign Artifact Set & Release Law

The Sovereign Artifact Set consists of SEVEN files (including `PROJECT_STATUS.md`) that move as a single unit for every Sovereign Baseline. Before any tag is struck, these files must be in perfect agreement with the Forge state, adhering to the Sovereign Release Law: step tagging and GitHub releases MUST occur exclusively on the `main` branch.
```

### Task 4: Update AGENTS.md (The Behavioral Mandates)

**Files:**
- Modify: `/Users/dderyldowney/VDE/AGENTS.md`

- [ ] **Step 1: Add Mandate 17 to Section 2**

Hardened the ritual in the agent's core behavioral constraints.

```markdown
17. **The Release Ritual (Absolute)**: Step tagging (X.X.X) and GitHub releases are FORBIDDEN on develop. They MUST be applied exclusively to the main branch. The SHA certified on main is then mirrored to stable.
```

### Task 5: Final Validation

- [ ] **Step 1: Verify document agreement**
Confirm that `VDE-SPEC.md`, `ARCHITECTURE.md`, and `Technical-Deep-Dive.md` all agree on the count of SEVEN artifacts and the Release Law.

- [ ] **Step 2: Run Sovereign Audit**
Run `bin/vde-enforce-uap.zsh` to ensure no mandates were broken.
