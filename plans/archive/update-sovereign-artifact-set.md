# Implementation Plan: Sovereign Artifact Set Alignment (1.3.0)
<!-- @shared-law (Forge Component) -->

## Objective
To strictly enforce Rule 19 ("The Sovereign Artifact Set Mandate") by updating the core documentation artifacts to perfectly reflect the 1.3.0 implementation reality.

## Scope & Impact
This aligns the following documents to the canonical `data/vm-types.conf` and `lib/vde-constants` realities:
- `docs/VDE-SPEC.md`
- `docs/ARCHITECTURE.md`
- `docs/Technical-Deep-Dive.md`

## Implementation Steps

1. **Update `docs/VDE-SPEC.md`:**
   - Correct the 8-Field Standard in Section 1 from `type|name|aliases|display|pkgs|custom_cmd|env|ports` to `type|name|aliases|display|pkgs|custom_cmd|service_ports|ssh_port`.
   - Restore the missing Section 4 (Directory Structure) and renumber the Sovereign Artifact Set Mandate to Section 5.

2. **Update `docs/ARCHITECTURE.md`:**
   - Align the 8-Field Standard string in Section 2 to match the corrected format.

3. **Update `docs/Technical-Deep-Dive.md`:**
   - Align the 8-Field Standard string in Section 2.
   - Ensure the Sovereign Error Table in Section 6 explicitly maps `VDE_ERR_SYNC_DRIFT` to `13`.

## Verification & Testing
- Execute `bin/vde-sync-version` to guarantee the artifact set is successfully aligned without warnings.
- Run `git diff` to manually verify the string replacements occurred perfectly across all 3 target files.