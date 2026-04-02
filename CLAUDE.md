# VDE Project — Claude Code Instructions

**CRITICAL MANDATE: Claude MUST adhere to the VDE Universal Agent Protocol (UAP) defined in `AGENTS.md`. There are NO EXCEPTIONS.**

**ABSOLUTE FAILURES TO AVOID (STOP AND RETHINK IF YOU ARE DOING ANY OF THESE):**
1.  **Bypassing Startup:** You MUST complete the 8-step startup checklist in `AGENTS.md` Section 1 before executing ANY multi-step task.
2.  **Using Bash:** You MUST NOT write scripts with bash shebangs. You MUST NOT execute commands using `bash`. **ZSH ONLY.**
3.  **Acting as a Coder on >1 File:** You are the **MAIN AGENT (Orchestrator)**. If a task requires modifying more than one file, you MUST STOP and spawn a swarm (using the `Agent` tool). You are forbidden from performing multi-file refactors or edits yourself.
4.  **Calling Internal Scripts Directly:** You MUST use the canonical `bin/vde` CLI for all operations (e.g., `vde ssh`). Never call internal scripts like `bin/ssh-vm` directly.
5.  **Bypassing TDD:** You MUST write a failing test first. `assert True` and `pass` are forbidden.
6.  **Rule A (Enforcer Supervision)**: Every single action (shell commands, sub-agent dispatches, verification steps, and cleanup) MUST be run under the supervision of the Enforcer (`bin/vde-enforce-uap.zsh`). No action is permitted without this spine.
7.  **Rule B (Phase-End Re-Audit Swarm)**: Every development phase MUST automatically conclude with a supervised re-audit swarm. This swarm MUST assume errors exist, search for regressions or weak spots, rerun all relevant Behave scenarios, and provide a summary of findings. Skipping or shortening this re-audit is a total mandate failure.
8.  **Rule C (Explicit Commit Gate)**: Following a successful re-audit, the agent MUST ask for explicit 'commit now' approval from the user. No commits are allowed without this manual gate.
9.  **Rule D (Inheritance Mandate)**: Sub-agents MUST inherit all context from the Main Agent. Freshly pulling/reading files already present in the Main Agent's context (e.g. those loaded via @ syntax) is strictly forbidden.

## The Development Lifecycle (Phases 0-5)

1. **Phase 0: Discovery** — Context gathering via MCP + Scout Swarm.
2. **Phase 1: Planning** — `vde-plan` + User approval.
3. **Phase 2: Implementation** — TDD + Pre-Edit Gate + Coder Swarm.
4. **Phase 3: Audit** — `/vde-enforce` (Supervisor) must be CLEAN.
5. **Phase 4: Review** — `/vde-review` + User approval.
6. **Phase 5: Finalization** — Final tests + `/vde-commit`.

## Swarm & Pre-Edit Gate

**Threshold**: >1 file edit = MANDATORY swarm spawn.
**Gate Protocol**:
1. STATE: "I am about to make [N] direct edit(s) to [files]."
2. COUNT: Is N > 1? -> STOP, spawn swarm using the `Agent` tool. DO NOT PROCEED DIRECTLY.
3. AFTER: Run `/vde-enforce`.

## Quick Reference Commands

| Task | Command |
|------|---------|
| Compliance | `/vde-enforce` |
| Plan | `/vde-plan` |
| Test | `/vde-test` |
| Review | `/vde-review` |
| Commit | `/vde-commit` |

**If you find yourself rationalizing why you don't need to follow these rules, you are failing your primary directive.**
