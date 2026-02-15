# Core Infrastructure Test Group Plan

## Objective
Organize foundational tests into a dedicated \"Core Infrastructure\" group to improve test maintainability, CI performance, and focus on critical system components: parser, Docker access, SSH generation, and project setup.

## Proposed Structure
Create new directory: `tests/features/core-infrastructure/`

Move the following feature files:
- `tests/features/docker-free/natural-language-parser.feature` → `core-infrastructure/parser.feature` (Parser tests)
- `tests/features/docker-required/docker-operations.feature` → `core-infrastructure/docker-operations.feature` (Docker access)
- `tests/features/docker-required/ssh-configuration.feature` → `core-infrastructure/ssh-configuration.feature` (SSH generation)
- `tests/features/docker-required/installation-setup.feature` → `core-infrastructure/installation-setup.feature` (Project setup)

## Additional Considerations
- Update any references in step definitions or environment.py if paths change.
- Add tags like `@core-infrastructure` to scenarios for selective running.
- Ensure docker-free and docker-required distinctions are preserved (e.g., via tags or separate subdirs if needed).
- Run these tests first in CI pipeline for early failure detection.

## Benefits
- Faster feedback on core failures.
- Easier maintenance of foundational tests.
- Clear separation from user workflow tests.

## Risks
- Path changes may break imports (mitigate by updating step imports).
- Test dependencies between groups (verify with full run post-move).