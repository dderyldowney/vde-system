# Phase 31 Documentation Purification and Closure Plan
<!-- @forge (Implementation Plan) -->

## Objective
Complete Phase 31 by purifying the documentation, updating the Sovereign Artifact Set (starting with `VDE-SPEC.md`), and empirically verifying the test suite. This ensures the "Gospel" is in perfect harmony with the 1.4.1 Sovereign Baseline before igniting Phase 32.

## Key Files & Context
- `docs/VDE-SPEC.md`
- `docs/directory-structure.md`
- `docs/command-reference.md`
- `session_handover.md`
- `MEMORY.md`
- Other Sovereign Artifact Set files (`ARCHITECTURE.md`, `TECHNICAL_DEEP_DIVE.md`, `RELEASE_NOTES.md`, `USE_CASES.md`, `VDE_ANALYSIS.md`, `PROJECT_STATUS.md`, `SOVEREIGN_CHARTER.md`, `STDLIB.md`)

## Implementation Steps
1.  **Update Sovereign Artifact Set**:
    *   Update `docs/VDE-SPEC.md` to officially mark Phase 31 as complete and prepare the specification for Phase 32.
    *   Review and update the remaining 8 files in the Sovereign Artifact Set to ensure they reflect the Phase 31 DNS discovery and bridge capabilities.
2.  **Refactor Directory Structure**:
    *   Update `docs/directory-structure.md` to match the 1.4.1 layout.
    *   Add missing critical infrastructure directories like `.docker-state/` and `.cache/`.
    *   Remove deprecated script references (e.g., `create-virtual-for`) and replace them with the unified `bin/vde` standard.
3.  **Synchronize Command Reference**:
    *   Update `docs/command-reference.md` to accurately reflect the 1.4.1 Unified CLI.
    *   Correct the syntax for adding new VM types from `vde create` to the modern `vde add`.
    *   Document the new Phase 31 features: `vde dns-check`, `vde cluster`, and `vde vision`.
4.  **Final State Synchronization (Memory & Handover)**:
    *   Upon completion of all documentation updates and successful test verification, update `MEMORY.md` to record the completion of the Documentation Purification Strike.
    *   Update `session_handover.md` with the final "then-state" (100% GREEN, Phase 31 complete, Phase 32 ready) so the next session inherits perfect context.

## Verification & Testing
1.  Execute the Sovereign Audit: `bin/vde-enforce-uap.zsh`
2.  Execute the Spine Check: `bin/vde-spine-check.zsh`
3.  Execute the complete BDD test suite: `python3 -m behave tests/features/` to generate the terminal evidence of the 100% pass rate required for the Phase 31 Chronicle (PR) closure.