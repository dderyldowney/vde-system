# Remediation Plan: Chaos Feature UAP Violations (2026-04-29)
<!-- @forge (Governance Sentinel) -->

## Trigger
`bin/vde-enforce-uap.zsh` exited non-zero with 2 violations in untracked chaos-strike files.
Per AGENTS.md §2 Mandate 15, all phases are HALTED pending user approval of this plan.

## Violations

### Violation 1 — Tag on Line 1
- **File**: `tests/features/chaos/beskar-hardening.feature`
- **Finding**: Architectural tag `# @armor (Chaos Test - Rule 12.5 Violation)` is on line 1.
  Line 2 also contains an incorrect `#!/usr/bin/env zsh` shebang (Gherkin files require none).
- **Required fix**: Line 1 must be blank or the `Feature:` declaration.
  Tag must move to line 2 or 3. The erroneous zsh shebang on line 2 must be removed.

### Violation 2 — Non-Canonical Python Shebang
- **File**: `tests/features/steps/chaos_steps.py`
- **Finding**: Line 1 contains `#!/usr/bin/env zsh`, which is incorrect for a Python file.
- **Required fix**: Change line 1 to `#!/usr/bin/env python3`.

## Sub-Tasks (requires user approval before execution)

- [ ] **Task 1**: Fix `tests/features/chaos/beskar-hardening.feature`
  - Remove `#!/usr/bin/env zsh` from line 2.
  - Move `# @armor` tag to line 2 (or appropriate line per Gherkin structure).
  - Ensure `Feature:` declaration is present and properly placed.

- [ ] **Task 2**: Fix `tests/features/steps/chaos_steps.py`
  - Change line 1 from `#!/usr/bin/env zsh` to `#!/usr/bin/env python3`.

## Post-Fix Verification
After fixes, re-run `bin/vde-enforce-uap.zsh` to confirm CLEAN exit, then:
1. `bin/vde-spine-check.zsh`
2. `python3 -m behave tests/features/core-infrastructure/proof-of-life-the-contract.feature`
