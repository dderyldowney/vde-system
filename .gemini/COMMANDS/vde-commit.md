# /vde-commit Command (UAP Edition)

Verified Git Finalization following Phase 5 UAP mandates.

## Usage
/vde-commit <structured message>

## Pre-Flight Checks (MANDATORY)
1.  **Supervisor Gate**: `/vde-enforce` returned PASS.
2.  **Reviewer Gate**: `/vde-review` returned APPROVED.
3.  **User Gate**: User explicitly approved the review and commit.
4.  **Test Gate**: Relevant tests pass for the changed scope.

## Execution Flow
1.  **Stage**: `git add .`
2.  **Clean**: Automatically strip temporary artifacts (DEBUG_LOG.md, diagnostic scripts).
3.  **Commit**: Execute with mandatory `<type>: <description>` format.

## Post-Commit
- Update `MEMORY.md`.
- **DO NOT PUSH** without authorization.