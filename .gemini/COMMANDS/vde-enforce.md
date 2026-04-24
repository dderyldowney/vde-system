# /vde-enforce Command (UAP Edition)
<!-- @forge (Governance Sentinel) -->

Universal Supervisor Pass. Verifies compliance with Phase 0-5 lifecycle and UAP mandates.

## Usage
/vde-enforce [description of work]

## What This Does
The Rule Enforcer (Supervisor) performs an automated audit of the 3 core rules:
1.  **Rule 1: TDD**: Checks for red state existence, minimal implementation, and fake test prohibition.
2.  **Rule 2: DRY**: Checks for duplicated logic or assertion patterns.
3.  **Rule 3: Swarm+MCP**: Verifies Phase 0 discovery, parallel swarms, and Pre-Edit Gate compliance.

## Execution
Main Agent spawns Rule Enforcer Agent with:
- description of work
- `git status --short`
- `git diff HEAD`

## Results
- **PASS**: Lifecycle proceeds.
- **BLOCKED**: STOP immediately. All violations MUST be fixed. No work can proceed until PASS is returned.