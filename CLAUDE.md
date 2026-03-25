# VDE Project — Claude Code Instructions

## Authority

**VDE-SPEC.md** (`docs/VDE-SPEC.md`) is the single source of truth.
- Never modify it without explicit user authorization.
- All implementations must conform to it.
- See `AGENTS.md` for the full authority chain and mandate details.

## Agent Loading (MANDATORY AT STARTUP)

**At session start, agents and commands MUST be scanned and loaded into context immediately, not lazy-loaded, before ANY tasks run. This applies to initial startup AND any context refresh steps before tasks run. e.g the `/new` command.**

The agent definitions in `.claude/agents/` (Claude Code) or `.kilocode/agents/` (Kilo) must be read at session initialization before any task execution. This ensures all sub-agent capabilities are available immediately.

## STARTUP (MANDATORY — EXECUTE BEFORE FIRST RESPONSE)

**ALL steps below MUST be executed automatically at session start — before answering ANY user prompt. No exceptions. No lazy-loading. No skipping for "simple" sessions.**

1. **Read `MEMORY.md`** — load project state, test status, active goals
2. **Read `session_handover.md`** — load current session context and next steps
3. **Read `plans/session_handover_remediation.md`** — load active remediation plan
4. **Query `memory` MCP** — retrieve cross-session context from knowledge graph
5. **Scan and load agent definitions** from `.claude/agents/` — load all sub-agent capabilities into working memory
6. **Read `AGENTS.md`** — load any instructions not already in this file into working memory
7. **Run `/vde-enforce`** (Supervisor) — verify framework compliance before any work begins

**Session control MUST NOT be handed to the user until all 7 steps above are complete.**
If any step fails, report the failure to the user before proceeding.

## Rule Enforcer (HIGHEST AUTHORITY — NON-NEGOTIABLE)

**Run `/vde-enforce` after every major change, plan, refactor, or new feature. No exceptions.**

The Rule Enforcer checks 3 rules:
1. **TDD** — failing test first (red), minimal code to pass (green), then refactor. No fake/pink tests.
2. **DRY** — no repeated code or logic. One parameterized function, never near-identical copies.
3. **Swarm+MCP** — MCP before local tools, parallel sub-agents spawned simultaneously, main agent synthesizes only.

**If the Rule Enforcer returns BLOCKED:**
- Stop immediately. Do not continue to the next task.
- Fix every listed violation.
- Run `/vde-enforce` again.
- Only proceed when it returns PASS.

**If you disagree with a ruling: you are wrong. Fix the violation.**
The Rule Enforcer is a higher authority than your own confidence. See `.claude/agents/rule-enforcer.md`.

## 5-Phase Workflow (MANDATORY)

Full detail in `.kilocode/rules/workflow.md`. Summary:

1. **Plan** — `sequential-thinking` MCP, get explicit user approval → **run `/vde-enforce`**
2. **Code** — Implement strictly per approved plan, no unauthorized refactoring → **run `/vde-enforce`**
3. **Audit** — Run `yume-guardian`, loop with `yume-implementer` until CLEAN
4. **Review** — `code-reviewer` approval + user approval (both required)
5. **Git** — Verify tests → commit locally. **NO push without explicit user auth.**

## Sub-Agent Swarm (MANDATORY)

Full detail in `.kilocode/rules/subagent_mcp_mandate.md`. Summary:
- ALL multi-step work uses sub-agents in parallel swarm form
- Single-agent direct execution is forbidden (except trivial read-only queries)
- Spawn all agents simultaneously; main agent synthesizes results only

## MCP Priority (MANDATORY)

1. MCP Services: `sequential-thinking`, `context7`, `github`, `fetch`, `memory`, `MCP_DOCKER`
2. Sub-Agents
3. Local CLI
4. Internal Tools (last resort)

## DRY (MANDATORY)

Full detail in `.kilocode/rules/dry_requirement.md`. Core rule:
- ONE parameterized function, never multiple near-identical functions
- Violations are rejected in review — no exceptions

## Test Protocol

Full detail in `AGENTS.md` Testing Guidelines. Summary:
- **Isolate first**: run only the specific failing feature/test
- **Fast tags** (no Docker): `@parser`, `@spec`, `@config`, `@error-path`
- **Avoid timeouts**: Always use `--tags="not @integration"` when running BDD tests to exclude Docker-requiring tests
- **BDD**: `python3 -m behave tests/features/core-infrastructure/<feature>.feature`
- **Full suite**: `./tests/run-full-test-suite.zsh` — final verification only
- **No fake tests**: see `.kilocode/rules/fake_tests.md`

## Port Allocation

| Range | VM Type |
|-------|---------|
| 2200–2299 | Language VMs (20 slots) |
| 2400–2499 | Service VMs (7 slots) |

Check `data/vm-types.json` before assigning any port. No conflicts permitted.

## Shell Rules

- **ZSH ONLY**: `#!/usr/bin/env zsh` — mandatory for all shell scripts
- **FORBIDDEN**: `/bin/sh`, `/usr/bin/env sh`, bash-only syntax
- Features used: associative arrays, process substitution, zsh 5.x

## No-Push Policy

Commit locally freely. **DO NOT `git push` without explicit user instruction.**

## Session Start Checklist

This checklist is **automatically executed** (not optionally consulted) at every session start per the STARTUP section above. Steps are listed here for reference only.

1. Read `MEMORY.md` — project state, test status, active goals
2. Read `session_handover.md` — current session context, next steps
3. Read `plans/session_handover_remediation.md` — active remediation plan
4. Query `memory` MCP for cross-session context
5. Scan and load `.claude/agents/` agent definitions
6. Read `AGENTS.md` and load into working memory
7. Run `/vde-enforce` — Supervisor compliance check

## Agent Additions / Command Additions

**Sync Requirement**: When adding a new agent/command, copy to BOTH `.claude/` and `.kilocode/` directories to ensure availability regardless of which CLI is used. When running under Claude Code CLI, convert to Kilo format before copying into the .kilocode directories. When running under Kilo CLI, convert to Claude Code format before copying into the .claude directories. Convert in-memory only to the other CLI's format before writing into the other CLI's directories. Never touch the source file on disk before copying. This is to prevent incorrectly copying the wrong format to the wrong CLI.
## Quick Reference

```zsh
# Run specific BDD feature (fast, no Docker)
python3 -m behave tests/features/core-infrastructure/parser.feature

# Run docker-free test suite
./tests/run-docker-free-tests.zsh

# Run full suite (final verification only)
./tests/run-full-test-suite.zsh

# Run specific unit test
zsh tests/unit/<libname>.test.zsh
```

## Available Slash Commands

| Command | Purpose |
|---------|---------|
| `/vde-enforce` | **Rule Enforcer pass (run after every change)** |
| `/vde-plan` | Plan a feature or fix (swarm + VDE-SPEC.md) |
| `/vde-test` | Smart test runner (auto-detects scope) |
| `/vde-review` | yume-guardian + DRY + code-reviewer |
| `/vde-commit` | Phase 3-5 verified commit |
| `/vde-spec` | Spec compliance check vs VDE-SPEC.md |
| `/vde-debug` | Debug failing tests or runtime errors |
| `/vde-new-vm` | Guided new VM type workflow |

## Rule Files Reference

- `.kilocode/rules/workflow.md` — 5-phase workflow detail
- `.kilocode/rules/subagent_mcp_mandate.md` — swarm execution protocol
- `.kilocode/rules/dry_requirement.md` — DRY enforcement
- `.kilocode/rules/fake_tests.md` — fake test prohibition
- `.kilocode/rules/review.md` — code review standards
- `AGENTS.md` — agent directory, mandates, testing guidelines, session handover
