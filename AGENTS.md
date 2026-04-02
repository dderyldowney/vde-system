# VDE Universal Agent Protocol (UAP)

This document defines the **MANDATORY** development lifecycle and behavioral constraints for **ALL** AI agents (Gemini CLI, Claude Code, Kilo CLI, and any sub-agents) interacting with the VDE workspace.

**There are NO EXCEPTIONS to these rules. Rationalizing bypasses is a critical failure.**

---

## 1. STOP: Mandatory Startup Checklist (Main Agent Only)

**DO NOT EXECUTE ANY TASK OR WRITE ANY CODE UNTIL THIS CHECKLIST IS COMPLETE.**

The main agent MUST complete these 8 steps sequentially before doing *anything else* (other than read-only discovery to find these files). 
*Note: Sub-agents inherit this context and MUST skip these steps to begin their assigned task immediately.*

1.  **Read @MEMORY.md**: Understand the current project mission, recent achievements, and immediate focus.
2.  **Read @session_handover.md**: Identify the specific goals and constraints of the current session.
3.  **Read @plans/session_handover_remediation.md**: Identify strategic debt and pending fixes.
4.  **Read @docs/VDE-SPEC.md**: Refresh knowledge of authoritative technical requirements and implementation priority.
5.  **Read @PROJECT_STATUS.md**: Understand the current reliability, pass rates, and identified gaps.

6.  **Query `memory` MCP**: Retrieve cross-session context and semantically relevant conversation history.
7.  **Refresh Library Documentation**: Use `context7` to fetch up-to-date documentation for any relevant libraries or frameworks.
8.  **Perform Housekeeping**: Strip dead logs, remove unused code, and meticulously verify `bin/` script compliance (ZSH shebangs only).

---

## 2. STRICT Core Mandates (Universal)

Violating any of these mandates is a failure of the agent's primary directive.

1.  **ZSH ONLY (ABSOLUTE)**: All shell scripts MUST use `#!/usr/bin/env zsh`. Bash is strictly forbidden. The agent MUST NOT use `bash` to execute commands.
2.  **Main Agent is Orchestrator ONLY**: The Main Agent MUST NOT write implementation code if it spans >1 file. The Main Agent's job is planning, orchestrating, and verifying. *Exception: If sub-agents are technically unavailable, the Main Agent may perform direct implementation provided every action is strictly supervised by the Enforcer.*
3.  **Enforcer Supervision (Rule A)**: Every single action (shell commands, dispatches, verification steps, and cleanup) MUST be run under the supervision of the Enforcer (`bin/vde-enforce-uap.zsh`).
4.  **Phase-End Re-Audit Swarm (Rule B)**: Every development phase MUST automatically conclude with a supervised re-audit swarm. This swarm MUST assume errors exist, search for regressions or weak spots, rerun all relevant Behave scenarios, and provide a summary of findings. Skipping or shortening this re-audit is a total mandate failure.
5.  **Explicit Commit Gate (Rule C)**: Following a successful re-audit, the agent MUST ask for explicit 'commit now' approval from the user. No commits are allowed without this manual gate.
6.  **DRY is Absolute**: No duplicate code or near-identical functions. Parameterize or consolidate.
7.  **TDD is Non-Negotiable**: Failing test (RED) first, then minimal implementation (GREEN), then refactor.
8.  **No Fake Tests**: `assert True`, `pass`, and placeholder context flags are strictly forbidden.
9.  **User-Centric Perspective**: All interactions and tests must use the canonical `vde` CLI (e.g., `vde ssh`). Never call internal `bin/` scripts directly.
10. **MCP-First**: Always prefer MCP services (`sequential-thinking`, `context7`, etc.) over local CLI or internal tools.
11. **Dual Approval Gate**: Commits require BOTH code-reviewer (agent) and user approval.
12. **No-Push Policy**: Never `git push` without explicit user instruction.

---

## 3. The Development Lifecycle (Phases 0-5)

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
- **Pre-Edit Gate (CRITICAL STOP)**:
  1. STATE: "I am about to make [N] direct edit(s) to [files]."
  2. COUNT: Is N > 1?
     - MAIN AGENT: **STOP.** Spawn a coder sub-agent swarm. **DO NOT PROCEED DIRECTLY.**
     - SUB-AGENT: **STOP.** Report back: "This task requires >1 file edit. Split into a swarm or re-assign."
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

## 4. Swarm Orchestration Rules

- **Main Agent**: Acts as the orchestrator. Synthesizes results, maintains `MEMORY.md`, and spawns swarms. **Does NOT write multi-file code UNLESS sub-agents are technically unavailable, in which case it may perform direct implementation provided every action is strictly supervised by the Enforcer.**
- **Sub-Agents**: Specialized experts. They inherit context from the Main Agent and perform isolated, single-file tasks.
- **Inheritance Mandate**: Sub-agents MUST inherit all context from the Main Agent. Re-reading or freshly pulling files that are already present in the Main Agent's context (specifically those loaded via the `@` startup checklist) is strictly forbidden. This prevents infinite loops and context window crashes.
- **Scope Limit**: If a sub-agent receives a task requiring >1 file edit, it **MUST STOP** and report back. It cannot expand its own scope or spawn its own sub-agents.
- **Parallelism**: Swarms must be launched simultaneously in a single message block, not sequentially.

---

## 5. Agent-Platform Mapping

| Capability | Gemini CLI | Claude Code / Kilo |
|------------|------------|---------------------|
| Plan Mode | `enter_plan_mode` | `/vde-plan` |
| Sub-Agents | `generalist`, `codebase_investigator` | `Agent` tool |
| Compliance | `/vde-enforce` | `/vde-enforce` |
| Review | `/vde-review` | `/vde-review` |

**The Agent Directory is the single source of truth. Rules apply regardless of which CLI is used.**
