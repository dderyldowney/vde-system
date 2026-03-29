# VDE Agent Directory --- Strict Ops Edition

Operational rules for Claude Code / Kilo CLI in VDE. This file is
intentionally minimal and normative.

------------------------------------------------------------------------

## 1. Mandatory Startup
> **SCOPE: MAIN AGENT ONLY.** Sub-agents spawned via the Agent tool must NOT run these steps. They inherit context from the main agent and must begin their assigned task immediately.

**Idempotent loading:** Before each step, check whether the content is already present in the current context. If it is, skip that step — never reload information already loaded this session.

Run before answering any user prompt, and again after any context reset (e.g. `/new`). Skip any step whose content is already in context.

1.  Read `MEMORY.md`
2.  Read `session_handover.md`
3.  Read `plans/session_handover_remediation.md`
4.  Query `memory` MCP
5.  Load agent definitions from `.claude/agents/` or `.kilocode/agents/`
6.  Read `AGENTS.md`
7.  Run `/vde-enforce`
8.  Run Context7 refresh for: Python, behave, PyYAML, Docker,
    docker-compose, Zsh, SSH

Do not proceed until all startup steps complete. If any step fails,
report it before continuing.

------------------------------------------------------------------------

## 2. CLI Layout

  ------------------------------------------------------------------------------------
  CLI               Commands                Agents                Rules
  ----------------- ----------------------- --------------------- --------------------
  Claude Code       `.claude/commands/`     `.claude/agents/`     `.claude/rules/`

  Kilo              `.kilocode/commands/`   `.kilocode/agents/`   `.kilocode/rules/`
  ------------------------------------------------------------------------------------

### Sync Rule

Every new command or agent must exist in both trees.

-   Convert in memory before writing to the other CLI's directory
-   Do not overwrite the source file's native format before copying

------------------------------------------------------------------------

## 3. Commands

See `.claude/rules/commands-reference.md` for full list.

Quick reference: `/vde-enforce`, `/vde-plan`, `/vde-test`, `/vde-review`, `/vde-commit`, `/vde-debug`, `/vde-spec`

------------------------------------------------------------------------

## 4. Specification Authority

**Source of truth:** `docs/VDE-SPEC.md`

All implementation and tests must conform to it.

Flow:

USER GUIDE → SPEC → CODE → TESTS

Rules: - Do not modify `docs/VDE-SPEC.md` without explicit user
approval - Every spec change must: - bump version - update full ISO 8601
timestamp

Any implementation that violates the spec is invalid.

------------------------------------------------------------------------

## 5. Core Execution Rules

1.  DRY is mandatory
2.  Code review is mandatory — both code-reviewer AND user approval required before commit
3.  Sub-agents required for non-trivial work
4.  MCP-first
5.  No circular delegation
6.  Docs via context7/fetch
7.  Validate MCP connectivity
8.  Log MCP interactions
9.  Local-first git hygiene
10. **No-push policy**: DO NOT `git push` without explicit user instruction

------------------------------------------------------------------------

## 6. Pre-Edit Gate

```
PRE-EDIT GATE:
1. STATE: "I am about to make [N] direct edit(s) to [files]."
2. COUNT: Is N > 1?
   - MAIN AGENT: STOP. Spawn coder sub-agent swarm. Do NOT proceed directly.
   - SUB-AGENT: STOP. Report back: "This task requires >1 file edit. Split into a swarm or re-assign." Do NOT spawn sub-agents. Do NOT proceed.
   - NO → STATE: "1 edit. Proceeding directly." Then execute.
3. AFTER: Run /vde-enforce to verify compliance.
```

Sub-agent rule: "This task requires >1 file edit. Split into a swarm or re-assign."

------------------------------------------------------------------------

## 7. Streamlining Mandate

-   DRY or delete
-   Tests must validate spec goals
-   Delete dead code
-   Keep only goal-serving code

------------------------------------------------------------------------

## 8. Portability Rules

-   No hardcoded paths
-   `VDE_ROOT_DIR` from `bin/vde`
-   SSH: `$HOME/.ssh/vde`
-   Relative compose paths
-   Cache contains no project paths

------------------------------------------------------------------------

## 9. Testing Rules

-   No full suite during debugging
-   No docker-tagged tests unless user explicitly requests
-   Run minimal scope first
-   Update MEMORY.md after tests

------------------------------------------------------------------------

## 10. Session Files

-   `MEMORY.md`
-   `session_handover.md`
-   `plans/session_handover_remediation.md`

Read at start. Update during work. Keep synchronized.

------------------------------------------------------------------------

## 11. Agent Map

See `.claude/rules/agents-reference.md` for agent responsibility mapping.
