# VDE Implementation Plan: SemVer & Conventional Commits (v1.3.1-STEP)

## Objective
Update the core rules in `.gemini/instructions.md` to formally adopt Semantic Versioning (SemVer) for release numbering and Conventional Commits for Git history, creating a clear separation between version format and commit message formatting.

## Background & Motivation
The current versioning law defines a `MAJOR.MINOR.STEP` structure but lacks formal alignment with industry standards. Furthermore, commit messages lack a codified structure. By adopting SemVer 2.0.0 and Conventional Commits 1.0.0, we ensure that the VDE's history is predictable, parseable, and aligned with standard development practices.

## Scope & Impact
- `.gemini/instructions.md`: Update Section 17 and insert Section 18.
- **Git History**: All future commits (starting with this implementation) will strictly adhere to the Conventional Commits specification.

## Proposed Solution
1. **Rule 17 Revision (SemVer Authority)**:
   - Formally adopt SemVer Specification 2.0.0.
   - Define VDE's specific mapping: `MAJOR.MINOR.STEP.p#` where `.p#` (or `-pN`) is the patch/extension level reserved for security and emergency updates.
2. **Rule 18 Insertion (Conventional Commits Mandate)**:
   - Mandate adherence to the Conventional Commits specification for all commits.
   - Enforce the use of scopes (e.g., `feat(core):`, `fix(security):`).
   - Introduce the dynamic variable `CONVENTIONAL_COMMITS_SPEC_VERSION="1.0.0"` to ensure the rule scales with upstream specification changes.

## Verification & Testing
- Manually verify the exact text replacement in `.gemini/instructions.md`.
- Verify the new rule is correctly formatted in markdown and aligns with the Mandalorian Rule Spine.
- Execute the very next commit using the newly codified Conventional Commits format to demonstrate compliance.

## Migration & Rollback
No runtime migration required. This is a documentation and procedural rule update. To rollback, `git revert` the commit that applies this documentation change.