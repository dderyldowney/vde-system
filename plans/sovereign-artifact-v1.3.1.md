# Sovereign Artifact Set Update Plan - v1.3.1

## Objective
Comply with VDE Sovereign Baseline mandates (Rule 19 and Rule O) by documenting the completion of the CI/CD remediation effort before the user formally cuts the v1.3.1 release.

## Key Files & Context
- `docs/VDE-SPEC.md`
- `docs/ARCHITECTURE.md`
- `docs/Technical-Deep-Dive.md` (Note: the project uses a capitalized filename)
- `RELEASE_NOTES.md`
- `docs/releases/v1.3.1.md` (New archive record)

## Proposed Solution
We will systematically update the core four artifacts to reflect the new state of the VDE pipeline:
1.  **VDE-SPEC.md**: Bump version to v1.3.1 and note the hardened CI/CD ZSH purity requirements.
2.  **ARCHITECTURE.md**: Document the separation of tests into CI-safe (`tests/run-sovereign-tests.zsh`) and physical DinD flows, along with the purging of Claude Code from the platform definitions.
3.  **Technical-Deep-Dive.md**: Explain the "chicken-and-egg" ZSH bootstrap fix for GitHub Actions and the `VDE_CI_MODE` port allocation bypass mechanism.
4.  **RELEASE_NOTES.md**: Add the v1.3.1 entry summarizing the CI/CD hardening and linking to the new archive record.
5.  **docs/releases/v1.3.1.md**: Create the formal record of the release, detailing the empirical test pass counts and the elimination of legacy agent debt.

## Implementation Steps
1.  Read the current state of each file to determine the correct insertion points.
2.  Use the `replace` tool to surgically update versions, dates, and architectural descriptions.
3.  Use the `write_file` tool to generate the new release archive record.
4.  Execute a local UAP audit (`bin/vde-enforce-uap.zsh`) to ensure no formatting or purity rules were broken.

## Verification & Testing
1. Confirm all four files of the Sovereign Artifact set mention version v1.3.1.
2. Verify the new release archive exists and is linked correctly in the root `RELEASE_NOTES.md`.
3. Provide the user with the explicit GitHub CLI command to create the tag and release on `main`.