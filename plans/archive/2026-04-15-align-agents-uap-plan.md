# Align AGENTS.md with Four Pillars of the Chronicle Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Update `AGENTS.md` to enforce Phase 0 scope creep prohibitions, Phase 4 Dual-Gate Review (reviewer agent first), and Phase 5 Unbreakable Link/Evidence mandates.

**Architecture:** Systematic update of the Universal Agent Protocol (UAP) lifecycle sections in `AGENTS.md`.

**Tech Stack:** Markdown, Git, GitHub CLI.

---

### Task 1: Update Phase 0 - Forbid Scope Creep

**Files:**
- Modify: `AGENTS.md`

- [ ] **Step 1: Edit AGENTS.md Phase 0**
Update the section to explicitly forbid scope creep and mandate new Issues for new requirements.

```markdown
### Phase 0: Mission Ignition (Swarm Mode)
- **Action**: Strike the Signet. Execute `gh issue create` using the appropriate template to define the mission scope and intent. Gather context using MCP services.
- **Scope Creep Prohibition**: The mission scope is FINAL once the Signet is struck. Forbidding any "while I'm at it" changes. ANY new requirement discovered during implementation MUST spawn a new, separate Signet (Issue). Mixing independent tasks in a single mission is a protocol violation.
- **Swarm**: Spawn `scout` and `security-auditor` agents to map dependencies and security posture.
- **Output**: Identification of DRY reuse opportunities and architectural constraints.
```

- [ ] **Step 2: Commit changes**
```bash
git add AGENTS.md
git commit -m "chore(uap): forbid scope creep in Phase 0"
```

### Task 2: Update Phase 4 - Mandate Dual-Gate Review

**Files:**
- Modify: `AGENTS.md`

- [ ] **Step 1: Edit AGENTS.md Phase 4**
Update the section to mandate `code-reviewer` agent approval BEFORE seeking User approval.

```markdown
### Phase 4: Review (Dual Approval)
- **Action**: Run `/vde-review`.
- **The Dual-Gate Mandate**: The Orchestrator MUST dispatch the `code-reviewer` agent and obtain its explicit approval BEFORE seeking User approval. Seeking User approval for unreviewed code is a protocol violation.
- **Swarm**: `code-reviewer` agent performs deep logic, performance, and security audit.
- **Exit Gate**: **Reviewer Approval AND THEN User Approval**.
```

- [ ] **Step 2: Commit changes**
```bash
git add AGENTS.md
git commit -m "chore(uap): mandate Dual-Gate Review in Phase 4"
```

### Task 3: Update Phase 5 - Enforce Unbreakable Link and Evidence

**Files:**
- Modify: `AGENTS.md`

- [ ] **Step 1: Edit AGENTS.md Phase 5**
Update the section to enforce auto-closing keywords and literal evidence in PR body.

```markdown
### Phase 5: Finalization
- **Action**: Final test run + commit using `/vde-commit`.
- **The Unbreakable Link**: Every Chronicle (PR) MUST be linked to its Signet (Issue) using authorized GitHub auto-closing keywords (e.g., `Closes #N`, `Fixes #N`).
- **The Evidence Mandate**: The Chronicle (PR) body MUST include literal terminal output proof of successful test runs and lifecycle certification. Paraphrasing results is forbidden.
- **Submit the Beskar**: The Chronicle (PR) MUST include: 1) High-level mission summary, 2) Complete list of modified files, 3) Rationale for refactoring, 4) Mandatory Red/Green evidence, and 5) The Unbreakable Link to the Signet. Execute `gh pr create` using the mandated template.
- **Mandate**: Certification of the **Proof of Life** Heartbeat is mandatory before committing or pushing.
- **Hygiene**: Update `MEMORY.md` and session handovers.
```

- [ ] **Step 2: Commit changes**
```bash
git add AGENTS.md
git commit -m "chore(uap): enforce Unbreakable Link and Evidence in Phase 5"
```

### Task 4: Final Validation and PR

- [ ] **Step 1: Verify AGENTS.md readability and formatting**
- [ ] **Step 2: Run UAP Enforcer**
Run: `bin/vde-enforce-uap.zsh`
- [ ] **Step 3: Create PR**
Submit the Chronicle with the required evidence.
