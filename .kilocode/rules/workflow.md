# DEVELOPMENT WORKFLOW PHASES

## Phase 1: Plan Mode
- Entry: User requests implementation.
- Action: Use `EnterPlanMode`, analyze with sequential-thinking, generate step-by-step plan.
- Exit Gate: HARD STOP for explicit user approval.
- Violation Protocol: Proceeding without approval → STOP immediately, return to Plan Mode.

## Phase 2: Code Mode
- Entry: Plan approved.
- Action: Switch to Code Mode. Implement strictly in sequence.
- Constraint: No unauthorized refactoring or optimizations.
- Violation Protocol: Changes beyond approved plan → Return to Phase 1, get approval for revised plan.

## Phase 3: yume-guardian Audit
- Entry: Code changes complete (Phase 2).
- Action: Run `yume-guardian` on all changes.
- Loop: If fails, use `yume-implementer` to fix and re-run until CLEAN.
- Constraint: No git actions allowed during this phase.
- Exit Gate: Yume-guardian returns CLEAN (zero violations).
- Violation Protocol: Git actions during audit → STOP immediately.

## Phase 4: Code Review
- Entry: Yume-guardian CLEAN (Phase 3).
- Action: Run `code-reviewer` agent on unstaged changes.
- Exit Gate: Requires BOTH `code-reviewer` approval and user approval.
- Violation Protocol: Proceeding without both approvals → STOP immediately.

## Phase 5: Git Hygiene
- Entry: Code-reviewer approval AND user approval (Phase 4).
- Action: Verify tests, verify guardian, verify reviewer.
- Commit: `git add -A` followed by a final guardian check before committing.
- Exit Gate: Changes committed to repository.
- Violation Protocol: Skipping verification steps → STOP immediately.

