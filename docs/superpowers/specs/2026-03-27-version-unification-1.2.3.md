# Design Doc: Version Unification v1.2.3 (The Sovereign Baseline)

## 1. Goal
Unify the project version to `1.2.3` and replace all occurrences of `Absolute`, `Sovereign Handshake`, and `Hardened Handshake` with `The Sovereign Baseline` in the context of the current project version.

## 2. Scope
Update the following files:
- `README.md`
- `PROJECT_STATUS.md`
- `docs/VDE-SPEC.md`
- `docs/ARCHITECTURE.md`
- `docs/API.md`
- `docs/TESTING.md`
- `docs/Technical-Deep-Dive.md`
- `docs/extending-vde.md`
- `MEMORY.md`
- `session_handover.md`
- `bin/vde-spine-check.zsh`
- `bin/vde-sync-version`
- `lib/vde-core` (comments)
- `tests/TEST_STATUS_REPORT.md`
- `plans/system-spine-contract.md`
- `tests/features/core-infrastructure/proof-of-life-the-contract.feature`
- `tests/features/steps/system_spine_steps.py`

## 3. Detailed Changes

### 3.1. Version Replacements
- Replace `1.2.2`, `1.2.1`, `1.2.0`, `1.1.0`, `1.0.0` with `1.2.3` in the context of project version strings (e.g., `v1.2.2`, `Version: 1.2.2`, `ARCHITECTURE v1.2.2`).

### 3.2. Phrase Replacements
- Replace `(Absolute)`, `(The Sovereign Handshake)`, `(The Hardened Handshake)` with `(The Sovereign Baseline)`.
- Replace `Sovereign Handshake`, `Hardened Handshake`, `Absolute` with `The Sovereign Baseline` when referring to the current version/baseline.
- Note: "Sovereign Handshake (SSH)" in `README.md` will become "The Sovereign Baseline (SSH)".

### 3.3. Script Logic (bin/vde-sync-version)
- Update the default version and the naming templates in the script.
- Ensure `sed` templates are ZSH compliant.

### 3.4. Test Updates
- Update `tests/features/core-infrastructure/proof-of-life-the-contract.feature` to expect version `1.2.3`.
- Update `tests/features/steps/system_spine_steps.py` to assert version `1.2.3`.

## 4. Implementation Plan
1.  Verify the content of each file to ensure precise replacements.
2.  Perform surgical replacements using the `replace` tool or `write_file` tool for each file.
3.  Perform a final validation by running `grep` again and checking for consistency.
4.  Run tests to ensure everything still passes.

## 5. Verification
- `grep -rnE "1\.[0-2]\.[0-2]|Absolute|Sovereign Handshake|Hardened Handshake"` should return zero matches in the targeted files.
- `bin/vde-spine-check.zsh` should run correctly.
- Behave tests (`tests/features/core-infrastructure/proof-of-life-the-contract.feature`) should pass.
