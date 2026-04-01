# VDE Project — Claude Code Instructions

## Authority

**AGENTS.md** is the single source of truth for all AI agent behavior.
- All interactions MUST follow the **Universal Agent Protocol (UAP)** defined in `AGENTS.md`.
- No agent (Claude, Kilo, Gemini, etc.) may bypass the UAP mandates.

## Core Mandates (Universal)

1.  **DRY is Absolute**: No duplicate code.
2.  **TDD is Non-Negotiable**: RED -> GREEN -> REFACTOR.
3.  **No Fake Tests**: `assert True`, `pass` are forbidden.
4.  **User-Centric**: Use the canonical `vde` CLI for all tests.
5.  **MCP-First**: Prefer MCP services over local tools.
6.  **Dual Approval Gate**: Agent Reviewer + User approval required for commits.
7.  **No-Push Policy**: Never `git push` without authorization.

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
2. COUNT: Is N > 1? -> STOP, spawn swarm.
3. AFTER: Run `/vde-enforce`.

## Startup Checklist (MANDATORY)

Execute the 5-step checklist in `AGENTS.md` section 4 at every session start.

## Quick Reference Commands

| Task | Command |
|------|---------|
| Compliance | `/vde-enforce` |
| Plan | `/vde-plan` |
| Test | `/vde-test` |
| Review | `/vde-review` |
| Commit | `/vde-commit` |

**See AGENTS.md for full protocol details.**
