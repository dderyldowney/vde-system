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
- Version: 1.5.7 (The Sovereign Baseline); Proof of Life re-certified 2026-11-21, 6 of 6 scenarios, 73 of 73 steps; released as tag 1.5.7 on `main` (daffb810; code baseline `c4560371`); `stable` is `daffb810` (it follows `main` after a release and may run ahead of it between releases)
- Heartbeat: Proof of Life 6 of 6 scenarios passed. Full BDD suite: 107 of 116 scenarios passed, 9 failed (details in `docs/development/testing.md`).
- Enforcer: `bin/vde-enforce-uap.zsh` success, exit 0.
- Documentation: not re-verified for 1.5.7. Known gap: the 1.5.5 entries in `docs/changelogs/current.md` are dead links.

## 1.5.8 Programme (approved by the User, 2026-11-21): the docs release
Order of work: merge `vde upgrade` (#679), then roll `develop` into `stable` without a release, then 1.5.8. `stable` is `daffb810` after the 1.5.7 release: `.github/workflows/update-stable-alias.yml` force-pushes `stable` to `main` on every push to `main`, and a develop -> stable roll leaves `stable` ahead of `main` until the next release. The approved scope (the same text is in `.gemini/STATE/MEMORY.md` and `.gemini/STATE/session_handover.md`):

1.5.8 is all about documentation. Nothing starts until the two goals above are done. Each part is its own Strike (Signet first).
- **Audience and voice.** Rewrite the docs for BOTH students AND VDE developers in a plain, direct, 1970s helper-manual voice: second person, concrete payoff first, short declarative sentences, a verification line in every step ("you should now see X; if not, see <page>"), dry wit sparingly. The excitement comes from competence transfer, not enthusiasm.
- **No mythos outside the AI.** Remove ALL mythos from everything student-facing AND developer-facing, including the VDE developer documentation. The mythos lives only in agent-facing files (`CLAUDE.md`, `AGENTS.md`, `.gemini/`). Use industry terms (Signet = Issue, Chronicle = Pull request, Strike = change, etc.). KEEP: Hub and Spoke (the real design philosophy) and the command `vde path-of-the-foundling` (the init + teaching path).
- **Real, true commands.** Every command, flag and path in a rewritten doc is verified by running it or by reading the code that parses it. Show how to pass flags.
- **Inside vs outside the container.** Explain what lives in a Spoke and what lives on the host, where a student's projects really are, and how to change it at install time (`--projects-dir` / `VDE_PROJECTS_DIR`; bootstrap has no prompt) and afterwards (`vde set-projects-dir`).
- **Link the docs to the code.** Pages that describe a library file or script link to that file (`lib/`, `bin/`, `scripts/`, `configs/`, `tests/`) so developers can open it. Surfacing the code means access from the docs, not relocating files. Docs heavily outweigh code today: take a census (code vs docs vs vendored) first; the vendored zsh manual (`docs/shell_manuals/zsh/zsh_5_9_us.md`, 31,344 lines) is 54% of all markdown and `bin/archive/` is 592 KB. Move or delete NOTHING without the User's decision; check `tests/` and the files that name `bin/archive/` first.
- **Simplify.** A full docs / doctree audit so information is easier to find and use.
