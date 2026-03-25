Run the Rule Enforcer supervisor pass on recent work.

## Usage
/vde-enforce $ARGUMENTS

`$ARGUMENTS` = description of work just completed (e.g., "added vde_check_http_endpoint to vde-health"), or empty to check recent git changes.

## What This Does

The Rule Enforcer checks exactly 3 rules. It cannot be skipped. It cannot be overruled.

**Rule 1 — TDD**: Was a failing test written FIRST? Is implementation minimal? Are all tests real (no fake/pink tests)?

**Rule 2 — DRY**: Is there any repeated logic, copy-pasted code, or near-identical functions that should be parameterized?

**Rule 3 — Swarm+MCP**: Was MCP used before local tools? Were parallel sub-agents spawned simultaneously, not sequentially? Did the main agent delegate rather than do research itself?

## Execution

Spawn the `rule-enforcer` agent with full context:

1. Pass the description: `$ARGUMENTS`
2. Pass the list of changed files: `git diff --name-only HEAD`
3. Pass the git diff of changed code: `git diff HEAD`
4. Include context about how the work was executed (swarm usage, MCP calls, test sequence)

The rule-enforcer agent will return either:

```
RULE ENFORCER: PASS
Rules checked: TDD ✓ | DRY ✓ | Swarm+MCP ✓
Work may proceed.
```

or:

```
RULE ENFORCER: BLOCKED
VIOLATION N — Rule X: <name>
  What was broken: <exact description>
  Evidence: <file:line or action>
  Required fix: <what must change>
Work is BLOCKED. Fix all violations before continuing.
```

## If BLOCKED

**Stop immediately.** Do not continue to the next task.

1. Read each violation carefully
2. Fix every violation listed — do not skip any
3. Run `/vde-enforce` again after fixing
4. Only proceed when RULE ENFORCER returns PASS

**The Rule Enforcer is a higher authority than your own confidence. If you disagree with a ruling, you are wrong. Fix the violation.**
