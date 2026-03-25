Verified commit following Phase 3-5 of the 5-phase workflow.

## Usage
/vde-commit $ARGUMENTS

`$ARGUMENTS` = commit message (required)

## Execution

**Pre-flight checks (fail fast — stop at first failure)**

1. Confirm yume-guardian is CLEAN on changed files
2. Confirm tests pass for changed scope (per `/vde-test` logic, not full suite)
3. Confirm code-reviewer approved (ask user if not already done this session)

If any check fails: STOP. Report which gate failed. Do not commit.

**Commit Sequence** (only after all checks pass)

```zsh
git add -A
# Final guardian check before commit
yume-guardian
git commit -m "$ARGUMENTS

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
git status
```

**Post-Commit**

```
COMMITTED: <hash> <message>
STATUS: Local only — NOT pushed to origin
REMINDER: Update MEMORY.md and session_handover.md with this commit.
```

**NEVER push to origin.** Push requires explicit user instruction ("push to origin" or equivalent).
