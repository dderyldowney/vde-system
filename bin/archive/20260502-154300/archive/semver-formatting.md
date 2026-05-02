# VDE Implementation Plan: SemVer Formatting (1.3.1)
<!-- @shared-law (Forge Component) -->

## Objective
To strictly comply with Semantic Versioning 2.0.0, the VDE ecosystem must be purged of the non-compliant 'v' prefix (e.g., `1.3.1` becomes `1.3.1`). Additionally, the synchronization script must be updated to correctly parse and manipulate SemVer strings containing the new `-spN` (Security Patch) extension format.

## Background & Motivation
The SemVer specification explicitly states that a normal version number MUST take the form `X.Y.Z` without a leading 'v'. Currently, VDE's documentation and synchronization scripts prepend 'v' to version strings. We must correct this globally and ensure that `bin/vde-sync-version` supports the new `-spN` format (e.g., `1.3.1-sp1`).

## Scope & Impact
- **Sovereign Artifact Set**: `docs/VDE-SPEC.md`, `docs/ARCHITECTURE.md`, `RELEASE_NOTES.md` and related core files (`README.md`, `PROJECT_STATUS.md`, `MEMORY.md`, `tests/TEST_STATUS_REPORT.md`, `docs/API.md`, `docs/TESTING.md`, `docs/extending-vde.md`, `VDE_PROTOCOL.md`).
- **Rule Definitions**: `.gemini/instructions.md` (correcting the `MAJOR.MINOR.STEP-spN#` rule to `-spN`).
- **Orchestration**: `bin/vde-sync-version` must be updated to use proper SemVer regexes (`[0-9]+\.[0-9]+\.[0-9]+(?:-sp[0-9]+)?`) and strip hardcoded 'v' prefixes from its `sed` replacement logic.

## Proposed Solution
1. **Rule Correction**: Edit `.gemini/instructions.md` to remove the `#` from `-spN#` and strip 'v' prefixes from rule examples.
2. **Global Prefix Purge**: Use highly targeted `sed` or `replace` operations across the artifact set to change `1.3.1` and `1.3.0` to `1.3.1` and `1.3.0`.
3. **Synchronizer Update**: Rewrite the `sed` patterns in `bin/vde-sync-version` to omit 'v' and support the full SemVer + `-spN` regex pattern.

## Verification & Testing
- Ensure `bin/vde-sync-version` syntax is valid ZSH and POSIX ERE compliant.
- Check git diff before committing to ensure no unintended strings were modified.

## Migration & Rollback
To rollback, simply revert the git commit produced by this implementation.