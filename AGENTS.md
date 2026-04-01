# VDE Universal Agent Protocol (UAP)

This document defines the mandatory development lifecycle and behavioral constraints for **ALL** AI agents (Gemini CLI, Claude Code, Kilo CLI, and any sub-agents) interacting with the VDE workspace.

---

## 1. Core Mandates (Universal)

1.  **DRY is Absolute**: No duplicate code or near-identical functions. Parameterize or consolidate.
2.  **TDD is Non-Negotiable**: Failing test (RED) first, then minimal implementation (GREEN), then refactor.
3.  **No Fake Tests**: `assert True`, `pass`, and placeholder context flags are strictly forbidden.
4.  **User-Centric Perspective**: All interactions and tests must use the canonical `vde` CLI.
5.  **MCP-First**: Always prefer MCP services (`sequential-thinking`, `context7`, etc.) over local CLI or internal tools.
6.  **Dual Approval Gate**: Commits require BOTH code-reviewer (agent) and user approval.
7.  **No-Push Policy**: Never `git push` without explicit user instruction.

---

## 2. The Development Lifecycle (Phases 0-5)

All work must proceed through these phases in order. Skipping phases or "optimizing away" gates is a protocol violation.

### Phase 0: Discovery (Swarm Mode)
- **Action**: Gather context using MCP services.
- **Swarm**: Spawn `scout` and `security-auditor` agents to map dependencies and security posture.
- **Output**: Identification of DRY reuse opportunities and architectural constraints.

### Phase 1: Planning (Hard Gate)
- **Action**: Use `EnterPlanMode` / `vde-plan`.
- **Constraint**: Design a TDD strategy with explicit failing test cases.
- **Exit Gate**: **Explicit User Approval**.

### Phase 2: Implementation (TDD + Swarm)
- **Action**: Follow Red-Green-Refactor.
- **Pre-Edit Gate (MANDATORY)**:
  1. STATE: "I am about to make [N] direct edit(s) to [files]."
  2. COUNT: Is N > 1?
     - MAIN AGENT: STOP. Spawn a coder sub-agent swarm. Do NOT proceed directly.
     - SUB-AGENT: STOP. Report back: "This task requires >1 file edit. Split into a swarm or re-assign."
     - N = 1: Proceed directly.
  3. AFTER: Run `/vde-enforce` to verify compliance.

### Phase 3: Audit (The Guardian)
- **Action**: Run `/vde-enforce` (or `yume-guardian` equivalent).
- **Checks**: Automated verification of TDD (red state existence), DRY, and Swarm compliance.
- **Exit Gate**: Must return **PASS (CLEAN)**.

### Phase 4: Review (Dual Approval)
- **Action**: Run `/vde-review`.
- **Swarm**: `reviewer` agent performs deep logic, performance, and security audit.
- **Exit Gate**: **Reviewer Approval AND User Approval**.

### Phase 5: Finalization
- **Action**: Final test run + commit using `/vde-commit`.
- **Hygiene**: Update `MEMORY.md` and session handovers.

---

## 3. Swarm Orchestration Rules

- **Main Agent**: Acts as the orchestrator. Synthesizes results, maintains `MEMORY.md`, and spawns swarms.
- **Sub-Agents**: Specialized experts. They inherit context from the Main Agent and perform isolated, single-file tasks.
- **Scope Limit**: If a sub-agent receives a task requiring >1 file edit, it **MUST STOP** and report back. It cannot expand its own scope or spawn its own sub-agents.
- **Parallelism**: Swarms must be launched simultaneously in a single message block, not sequentially.

---

## 4. Mandatory Startup checklist (Main Agent Only)

1. Read `MEMORY.md`.
2. Read `session_handover.md` and remediation plans.
3. Query `memory` MCP for cross-session context.
4. Refresh library documentation via `context7`.
5. Perform housekeeping (strip dead logs/unused code).

---

## 5. Agent-Platform Mapping

| Capability | Gemini CLI | Claude Code / Kilo |
|------------|------------|---------------------|
| Plan Mode | `enter_plan_mode` | `/vde-plan` |
| Sub-Agents | `generalist`, `codebase_investigator` | `Agent` tool |
| Compliance | `/vde-enforce` | `/vde-enforce` |
| Review | `/vde-review` | `/vde-review` |

**The Agent Directory is the single source of truth. Rules apply regardless of which CLI is used.**
