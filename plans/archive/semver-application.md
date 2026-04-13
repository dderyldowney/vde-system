# VDE Implementation Plan: SemVer Application (1.3.1-sp1)

## Objective
Apply the new SemVer versioning format (`MAJOR.MINOR.STEP-spN`) across the Sovereign Artifact Set and ensure `bin/vde-sync-version` uses regular expressions that comply with SemVer requirements.

## Background & Motivation
The previous versioning format was simply `MAJOR.MINOR.STEP`. The new requirement specifies `MAJOR.MINOR.STEP-spN` (e.g., `-sp1` for Security Patch 1), which functions as a SemVer-compliant pre-release or extension identifier. Existing documentation and the synchronization script (`bin/vde-sync-version`) use the regex `[0-9.]+`, which fails to capture the `-spN` extension.

## Scope & Impact
- `.gemini/instructions.md`: Correct the typo from `-spN#` to `-spN` to accurately reflect the user's instructions.
- `docs/VDE-SPEC.md`: Update version references to `1.3.1-sp1`.
- `docs/ARCHITECTURE.md`: Update version references to `1.3.1-sp1`.
- `RELEASE_NOTES.md`: Update version references to `1.3.1-sp1`.
- `bin/vde-sync-version`: Update all `sed` patterns from `[0-9.]+` to `[0-9]+\.[0-9]+\.[0-9]+(-sp[0-9]+)?` to capture the new SemVer string format.

## Proposed Solution
1. **Rule 17 Correction**: Modify `.gemini/instructions.md` to formally define `MAJOR.MINOR.STEP-spN`.
2. **Artifact Set Update**: Replace literal strings of `1.3.1` with `1.3.1-sp1` in the core artifact files.
3. **Regex Harmonization**: Edit `bin/vde-sync-version` to ensure `sed -E` commands accurately identify and replace SemVer strings like `1.3.1-sp1`.

## Verification & Testing
- Verify changes visually across the files.
- Ensure `bin/vde-sync-version` regexes are POSIX ERE compliant (used by `sed -E`).

## Migration & Rollback
To rollback, revert the git commit produced by this plan.