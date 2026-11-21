# Remediation Plan: Session Handover

## Paired Update Policy
This file is one half of a pair with [.gemini/STATE/session_handover.md](../.gemini/STATE/session_handover.md). A change that touches either file MUST touch the other in the same PR, so accomplishments (there) and outstanding debt (here) cannot drift apart. `bin/paired_update_enforcer` (CI workflow "Paired Update Check") compares the files a PR changed against its base and fails when only one of the two changed.

## High-Priority Architectural Debt
- **Documentation Migration Complete**: All 40+ documentation files migrated to industry-standard category structure (guides/, reference/, architecture/, development/, operations/, api/, governance/, changelogs/).
- **Cross-Reference Audit**: All code paths (bin/, lib/, tests/, .gemini/) updated to reference new documentation locations.
- **Sovereign Artifact Set**: All 9 SAS files relocated and all internal/external cross-references synchronized.

## Remediation Goals
- **Zero Broken Links**: Verify all markdown cross-references resolve to existing files across the entire docs/ tree.
- **Proof of Life Certified**: 6/6 scenarios, 72/72 steps passing (100% GREEN).
- **UAP Compliance**: Enforcer returns PASS (CLEAN) — 0 violations, 0 warnings.
- **Startup Integrity**: All AGENTS.md and .gemini/instructions.md startup file references verified and resolved.

## Open Items
- **plans/session_handover_remediation.md**: Restored from git history (was missing pre-migration).

## Sovereign Baseline: 1.5.7 (full-suite figures below measured 2026-09-30 at commit `6308fe33`, the 1.5.6 baseline)
- Version: 1.5.7 (The Sovereign Baseline); Proof of Life re-certified 2026-11-21, 6 of 6 scenarios, 73 of 73 steps; released as tag 1.5.7 on `main` (daffb810; code baseline `c4560371`); `stable` follows `main` after a release and may run ahead of it between releases
- Heartbeat: Proof of Life 6 of 6 scenarios passed. Full BDD suite: 107 of 116 scenarios passed, 9 failed (details in `docs/development/testing.md`).
- Enforcer: `bin/vde-enforce-uap.zsh` success, exit 0.
- Documentation: not re-verified for 1.5.7. Known gap: the 1.5.5 entries in `docs/changelogs/current.md` are dead links.

## 1.5.8 Programme (approved by the User, 2026-11-21): the docs release
After `vde upgrade` (#679) is merged and `develop` is rolled into `stable` (no release): rewrite the docs for students and VDE developers in a plain 1970s helper-manual voice, remove all mythos outside agent-facing files, verify every printed command, explain inside vs outside the container and how to change it, link the docs to the code they describe, and audit the doc tree for simplicity. The full scope is in `.gemini/STATE/session_handover.md`.
