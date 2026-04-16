# VDE Universal Agent Protocol (UAP)

This document defines the **MANDATORY** development lifecycle and behavioral constraints for **ALL** AI agents (Gemini CLI and any sub-agents) interacting with the VDE workspace.

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

6.  **THE SOVEREIGN STARTUP RITUAL**: The Alor (Main Agent) MUST execute these three rituals in strict sequence upon session ignition. Sub-agents (Verd'ika) are strictly forbidden from running these steps — they inherit the Alor's certification.
    - `bin/vde-enforce-uap.zsh` (Sovereign Audit)
    - `bin/vde-spine-check.zsh` (Spine Check)
    - `python3 -m behave tests/features/core-infrastructure/proof-of-life-the-contract.feature` (Proof of Life)

7.  **Query `memory` MCP**: Retrieve cross-session context and semantically relevant conversation history.
8.  **Refresh Library Documentation**: Use `context7` to fetch up-to-date documentation for any relevant libraries or frameworks.
9.  **Perform Housekeeping**: Strip dead logs, remove unused code, and meticulously verify `bin/` script compliance (ZSH shebangs only).

---

## 2. STRICT Core Mandates (Universal)

Violating any of these mandates is a failure of the agent's primary directive.

1.  **ZSH ONLY (ABSOLUTE)**: All shell scripts MUST use `#!/usr/bin/env zsh`. Bash is strictly forbidden. The agent MUST NOT use `bash` to execute commands.
2.  **THE ANVIL IS DEFAULT**: All active work MUST occur on the `develop` branch (The Anvil). `main` (Production) is reserved for STABLE RELEASES ONLY. Direct work on `main` is strictly prohibited.
3.  **Main Agent is Orchestrator ONLY**: The Main Agent MUST NOT write implementation code if it spans >1 file. The Main Agent's job is planning, orchestrating, and verifying. *Exception: If sub-agents are technically unavailable, the Main Agent may perform direct implementation provided every action is strictly supervised by the Enforcer.*
4.  **Enforcer Supervision (Rule A)**: Every single action (shell commands, dispatches, verification steps, and cleanup) MUST be run under the supervision of the Enforcer (`bin/vde-enforce-uap.zsh`).
5.  **Phase-End Re-Audit Swarm (Rule B)**: Every development phase MUST automatically conclude with a supervised re-audit swarm. This swarm MUST assume errors exist, search for regressions or weak spots, rerun all relevant Behave scenarios, and provide a summary of findings. Skipping or shortening this re-audit is a total mandate failure.
6.  **Explicit Commit Gate (Rule C)**: Following a successful re-audit, the agent MUST ask for explicit 'commit now' approval from the user. No commits are allowed without this manual gate.
7.  **DRY is Sovereign**: No duplicate code or near-identical functions. Parameterize or consolidate.
8.  **TDD is Non-Negotiable**: Failing test (RED) first, then minimal implementation (GREEN), then refactor.
9.  **No Fake Tests**: `assert True`, `pass`, and placeholder context flags are strictly forbidden.
10. **Canonical Entrypoint**: `bin/vde` is the single canonical entrypoint. All operations must go through `bin/vde` subcommands; calling underlying scripts directly is out of mandate, except in tests whose explicit purpose is to unit‑test that script in isolation (not as a side effect of a normal bin/vde call).
11. **MCP-First**: Always prefer MCP services (`sequential-thinking`, `context7`, etc.) over local CLI or internal tools.
12. **User-Centric Perspective**: All interactions and tests must use the canonical `vde` CLI (e.g., `vde ssh`). Never call internal `bin/` scripts directly.
13. **Dual Approval Gate**: Commits require BOTH code-reviewer (agent) and user approval.
14. **No-Push Policy**: Never `git push` without explicit user instruction.
15. **Automated Remediation Path**: If the Enforcer (vde-enforce-uap.zsh) returns a non-zero exit code OR outputs and `UAP-WARN`, the agent MUST NOT attempt to continue the current phase. It MUST immediately:
    1. Generate a .gemini/PLANS/remediation_*.md file.
    2. List every violation as a sub-task.
    3. Obtain user approval on the remediation plan before executing any fixes.
16. **The Proof of Life Heartbeat (Alor's Mandate)**: The Proof of Life (`proof-of-life-the-contract.feature`) is an **Alor-exclusive (Orchestrator)** ritual. Sub-agents (Verd'ika) inherit the certification and MUST NOT run it independently. It is mandatory ONLY during:
    - The Sovereign Startup Ritual (Alor only).
    - Committing or Pushing changes.
    - Direct implementation work on the lifecycle logic itself.
17. **Authority of the Record**: Only the Orchestrator (Alor) and the User are permitted to alter The Record. Sub-agents (Verd'ika) are FORBIDDEN from making autonomous commits. They may only perform commits when explicitly instructed by the Orchestrator or the User, ensuring the intent and control remain centralized.
18. **The Release Ritual (Absolute)**: Step tagging (X.X.X) and GitHub releases are FORBIDDEN on `develop`. They MUST be applied exclusively to the `main` branch. The SHA certified on `main` is then mirrored to `stable`.
19. **Universal Review Mandate**: ALL code generated by an agent MUST be run through a formal code-review verification. This mandate is absolute and applies to all generated code, including but not limited to manually executed scripts, one-off tools, and code run as part of a release process. Verification is NOT optional.

### !! CRITICAL FORBIDDEN PATTERNS !!
- **NO BASH/SH SYNTAX:** This is a ZSH-only project. Use ZSH-specific features (e.g., `${(f)var}`, `**/*`, `ZSH arrays index at 1`).
  - **Requirement:** Prefer ZSH-native parameter expansion (e.g., ${(f)...}, ${var:t}) and zparseopts over external cut, sed, or getopt calls. Using 0-indexed arrays is a mandate failure.
- **NO SLEEP CALLS:** Any delay or monitoring MUST use the polling skill. Reintroducing `sleep()` is considered a system-wide failure.
- **NO FLATTERY:** Do not explain why you are following these rules. Just execute.

---

## 3. The Development Lifecycle (Phases 0-5)

All work must proceed through these phases in order. Skipping phases or "optimizing away" phases is a protocol violation. These structural checkpoints—scoping the mission at ignition and proving the work at finalization—are central to our core design goals and ensure the purity of the Forge.

### Phase 0: Mission Ignition (Swarm Mode)
- **Action**: Strike the Signet. Execute `gh issue create` using the appropriate template to define the mission scope and intent. Gather context using MCP services.
- **Scope Creep Prohibition**: The mission scope is FINAL once the Signet is struck. Forbidding any "while I'm at it" changes. ANY new requirement discovered during implementation MUST spawn a new, separate Signet (Issue). Mixing independent tasks in a single mission is a protocol violation.
- **Swarm**: Spawn `scout` and `security-auditor` agents to map dependencies and security posture.
- **Output**: Identification of DRY reuse opportunities and architectural constraints.

### Phase 1: Planning (Hard Gate)
- **Action**: Use `EnterPlanMode` / `vde-plan`.
- **Constraint**: Design a TDD strategy with explicit failing test cases.
- **Exit Gate**: **Explicit User Approval**.

### Phase 2: Implementation (TDD + Swarm)
- **Action**: Follow Red-Green-Refactor.
- **Record the Discussion**: Significant architectural decisions, hurdles, or logic pivots MUST be recorded as comments on the Signet (Issue) to preserve the 'Why' for future warriors.
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
- **The Dual-Gate Mandate**: The Orchestrator MUST dispatch the `code-reviewer` agent and obtain its explicit approval BEFORE seeking User approval. Seeking User approval for unreviewed code is a protocol violation.
- **Swarm**: `code-reviewer` agent performs deep logic, performance, and security audit.
- **Exit Gate**: **Reviewer Approval AND THEN User Approval**.

### Phase 5: Finalization
- **Action**: Final test run + commit using `/vde-commit`.
- **The Chronicle Title**: Every Pull Request title MUST conform to the Conventional Commits specification (e.g., `feat(core): implementation`, `fix!: breaking fix`). This title is the primary anchor for automated labeling and search.
- **The Unbreakable Link**: Every Chronicle (PR) MUST be linked to its Signet (Issue) using authorized GitHub auto-closing keywords (e.g., `Closes #N`, `Fixes #N`).
- **The Evidence Mandate**: The Chronicle (PR) body MUST include literal terminal output proof of successful test runs and lifecycle certification. Paraphrasing results is forbidden.
- **Submit the Beskar**: The Chronicle (PR) MUST include: 1) High-level mission summary, 2) Complete list of modified files, 3) Rationale for refactoring, 4) Mandatory Red/Green evidence, and 5) The Unbreakable Link to the Signet. Execute `gh pr create` using the mandated template.
- **Mandate**: Certification of the **Proof of Life** Heartbeat is mandatory before committing or pushing.
- **Hygiene**: Update `MEMORY.md` and session handovers.

---

## 4. Swarm Orchestration Rules

- **Main Agent**: Acts as the orchestrator. Synthesizes results, maintains `MEMORY.md`, and spawns swarms. **Does NOT write multi-file code UNLESS sub-agents are technically unavailable, in which case it may perform direct implementation provided every action is strictly supervised by the Enforcer.**
- **Sub-Agents**: Specialized experts. They inherit context from the Main Agent and perform isolated, single-file tasks.
- **Controlled Commits**: Sub-agents MUST NEVER make commits of their own accord. They operate strictly under the Orchestrator's intent. The Orchestrator may serialize commits using sub-agents, but the responsibility for the Record's integrity belongs to the Alor.
- **Inheritance Mandate**: Sub-agents (Verd'ika) MUST inherit all context from the Alor (Main Agent). This includes the certification of the **Proof of Life** Heartbeat; sub-agents are strictly forbidden from executing this ritual themselves. Re-reading or freshly pulling files that are already present in the Main Agent's context (specifically those loaded via the `@` startup checklist) is strictly forbidden. This prevents infinite loops and context window crashes.
- **Scope Limit**: If a sub-agent receives a task requiring >1 file edit, it **MUST STOP** and report back. It cannot expand its own scope or spawn its own sub-agents.
- **Parallelism**: Swarms must be launched simultaneously in a single message block, not sequentially.

---

## 5. Agent-Platform Mapping

| Capability | Gemini CLI |
|------------|------------|
| Plan Mode | `enter_plan_mode` |
| Sub-Agents | `generalist`, `codebase_investigator` |
| Compliance | `/vde-enforce` |
| Review | `/vde-review` |

**The Agent Directory is the single source of truth. Rules apply regardless of which CLI is used.**
