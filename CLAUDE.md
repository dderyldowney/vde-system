# VDE Project — Claude Code Instructions

**CRITICAL MANDATE: Claude MUST adhere to the VDE Universal Agent Protocol (UAP) defined in `AGENTS.md`. There are NO EXCEPTIONS.**

**ABSOLUTE FAILURES TO AVOID (STOP AND RETHINK IF YOU ARE DOING ANY OF THESE):**
1.  **Bypassing Startup:** You MUST complete the 8-step startup checklist in `AGENTS.md` Section 1 before executing ANY multi-step task.
2.  **Using Bash:** You MUST NOT write scripts with bash shebangs. You MUST NOT execute commands using `bash`. **ZSH ONLY.**
3.  **Acting as a Coder on >1 File:** You are the **MAIN AGENT (Orchestrator)**. If a task requires modifying more than one file, you MUST STOP and spawn a swarm (using the `Agent` tool). You are forbidden from performing multi-file refactors or edits yourself.
4.  **Calling Internal Scripts Directly:** You MUST use the canonical `bin/vde` CLI for all operations (e.g., `vde ssh`). Never call internal scripts like `bin/ssh-vm` directly.
5.  **Bypassing TDD:** You MUST write a failing test first. `assert True` and `pass` are forbidden.

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
