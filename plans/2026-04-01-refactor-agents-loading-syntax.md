# Refactor AGENTS.md Loading Syntax Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor `AGENTS.md` to use the `@` loading syntax for context injection and condense linked files for better context efficiency.

**Architecture:** Update the startup checklist in `AGENTS.md` to use `** Read @FILENAME **`. Condense `MEMORY.md`, `session_handover.md`, `plans/session_handover_remediation.md`, `docs/VDE-SPEC.md`, and `PROJECT_STATUS.md` to their most critical authoritative sections.

**Tech Stack:** ZSH, Markdown

---

### Task 1: Verify Initial Compliance

**Files:**
- N/A

- [ ] **Step 1: Run the UAP Enforcer**
Run: `bin/vde-enforce-uap.zsh`
Expected: Verification of current workspace integrity.

### Task 2: Condense MEMORY.md

**Files:**
- Modify: `MEMORY.md`

- [ ] **Step 1: Rewrite MEMORY.md**
Condense to Mission, Recent Achievements, and Current Focus. Use the current sections but remove verbose details.

### Task 3: Condense session_handover.md

**Files:**
- Modify: `session_handover.md`

- [ ] **Step 1: Rewrite session_handover.md**
Condense to:
- Current Status: Phase 24
- Achievements: 22, 23
- Next Steps

### Task 4: Condense plans/session_handover_remediation.md

**Files:**
- Modify: `plans/session_handover_remediation.md`

- [ ] **Step 1: Rewrite plans/session_handover_remediation.md**
Condense to:
- Key Architectural Debt
- High-Priority Fixes

### Task 5: Condense docs/VDE-SPEC.md

**Files:**
- Modify: `docs/VDE-SPEC.md`

- [ ] **Step 1: Rewrite docs/VDE-SPEC.md**
Condense to core authoritative technical requirements (Core Data Structures, Port Assignments, Security Mandates).

### Task 6: Condense PROJECT_STATUS.md

**Files:**
- Modify: `PROJECT_STATUS.md`

- [ ] **Step 1: Rewrite PROJECT_STATUS.md**
Condense to:
- Technical Health Dashboard
- Test Suite Statistics

### Task 7: Update AGENTS.md Checklist

**Files:**
- Modify: `AGENTS.md`

- [ ] **Step 1: Update Checklist Syntax**
Replace the 5 file references in "Mandatory Startup Checklist" with the `** Read @FILENAME **` syntax.

### Task 8: Final Compliance Check

**Files:**
- N/A

- [ ] **Step 1: Run the UAP Enforcer**
Run: `bin/vde-enforce-uap.zsh`
Expected: PASS (CLEAN)
