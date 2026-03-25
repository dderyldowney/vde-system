Full code review: yume-guardian audit + DRY check + code-reviewer approval.

## Usage
/vde-review $ARGUMENTS

If `$ARGUMENTS` specifies files, review those. Otherwise review all unstaged/staged changes.

## Execution

**Step 1: Identify Changes**

```zsh
git diff --name-only HEAD
git diff --name-only --cached
```

**Step 2: yume-guardian Audit (Phase 3)**

Run `yume-guardian` on all changed files.
- If VIOLATIONS: use `yume-implementer` to fix, re-run until CLEAN
- No git actions during this phase (per `.kilocode/rules/workflow.md`)

**Step 3: DRY + Fake Test Audit (Swarm — spawn simultaneously)**

- DRY checker agent: grep changed files for duplicate functions, near-identical logic
  - Two functions with same body but different names
  - Step definitions with identical assertions
  - Reference: `.kilocode/rules/dry_requirement.md` examples
- Fake test scanner: scan for patterns per `.kilocode/rules/fake_tests.md`
  - `assert True`, `pass` in `@then`, `getattr(..., True)`, context flagging without real assertions

**Step 4: Code Review (per `.kilocode/rules/review.md`)**

Categorize issues found:
- **[Critical]** Hardcoded secrets, paths, or credentials
- **[Critical]** ZSH non-compliance (`/bin/sh` usage in .zsh files)
- **[Critical]** Port conflicts (duplicate in `data/vm-types.json`)
- **[Major]** DRY violations not caught in Step 3
- **[Major]** Missing input validation in public functions
- **[Minor]** Naming convention violations

**Step 5: Output**

```
YUME-GUARDIAN: CLEAN / VIOLATIONS (list)
DRY AUDIT: CLEAN / VIOLATIONS (list with remediation)
FAKE TESTS: NONE / VIOLATIONS (list with file:line)
CODE REVIEW: APPROVED / ISSUES (categorized)
OVERALL: READY FOR COMMIT / BLOCKED (reason)
```

**HARD STOP**: If any CRITICAL or yume-guardian violation — do not proceed to Phase 5.
Present results and wait for user approval before committing.
