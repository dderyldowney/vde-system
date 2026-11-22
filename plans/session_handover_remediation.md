# Remediation Plan: Session Handover

> **Handing over to another agent? Start with `.gemini/STATE/handoff.md`:** the rules, the current state, the sequence and the traps, written for any AI agent. Verify its facts with the commands it gives.

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
- Version: 1.5.7 (The Sovereign Baseline); Proof of Life re-certified 2026-11-21, 6 of 6 scenarios, 73 of 73 steps; released as tag 1.5.7 on `main` (daffb810; code baseline `c4560371`); `stable` (read its tip with `git ls-remote origin stable`; it follows `main` after a release and may run ahead of it between releases)
- Heartbeat: Proof of Life 6 of 6 scenarios passed. Full BDD suite: 107 of 116 scenarios passed, 9 failed (details in `docs/development/testing.md`).
- Enforcer: `bin/vde-enforce-uap.zsh` success, exit 0.
- Documentation: not re-verified for 1.5.7. Known gap: the 1.5.5 entries in `docs/changelogs/current.md` are dead links.

## 1.5.9 Programme (approved by the User, 2026-11-21): the docs release (renumbered from 1.5.8)
Done: 1.5.7 released; `vde upgrade` (#679), the 1.5.7 record (#678), the state files (#681, #686), the `vde upgrade` review fixes (#684) and two `develop` -> `stable` rolls without a release (#682, #687). Next: the security release 1.5.8 (#726, which replaced #668, plus the security-related parked items; it follows the project security process in `docs/governance/security-process.md` and `.gemini/RULES/security.md`, Signet #736), then the docs release 1.5.9. `stable` equalled `main` after the 1.5.7 release, because `.github/workflows/update-stable-alias.yml` updates `stable` to `main` on pushes to `main`, and a develop -> stable roll leaves `stable` ahead of `main` until the next release. The approved scope (the same text is in `.gemini/STATE/MEMORY.md` and `.gemini/STATE/session_handover.md`):

1.5.9 is all about documentation. Each part is its own Strike (Signet first).
- **Audience and voice.** Rewrite the docs for BOTH students AND VDE developers in a plain, direct, 1970s helper-manual voice: second person, concrete payoff first, short declarative sentences, a verification line in every step ("you should now see X; if not, see <page>"), dry wit sparingly. The excitement comes from competence transfer, not enthusiasm.
- **No mythos outside the AI.** Remove ALL mythos from everything student-facing AND developer-facing, including the VDE developer documentation. The mythos lives only in agent-facing files (`CLAUDE.md`, `AGENTS.md`, `.gemini/`). Use industry terms (Signet = Issue, Chronicle = Pull request, Strike = change, etc.). KEEP: Hub and Spoke (the real design philosophy) and the command `vde path-of-the-foundling` (the init + teaching path).
- **Real, true commands.** Every command, flag and path in a rewritten doc is verified by running it or by reading the code that parses it. Show how to pass flags.
- **Inside vs outside the container.** Explain what lives in a Spoke and what lives on the host, where a student's projects really are, and how to change it at install time (`--projects-dir` / `VDE_PROJECTS_DIR`; bootstrap has no prompt) and afterwards (`vde set-projects-dir`).
- **Link the docs to the code.** Pages that describe a library file or script link to that file (`lib/`, `bin/`, `scripts/`, `configs/`, `tests/`) so developers can open it. Surfacing the code means access from the docs, not relocating files. Docs heavily outweigh code today: take a census (code vs docs vs vendored) first; the vendored zsh manual (`docs/shell_manuals/zsh/zsh_5_9_us.md`, 31,344 lines) is 54% of all markdown and `bin/archive/` is 592 KB. Move or delete NOTHING without the User's decision; check `tests/` and the files that name `bin/archive/` first.
- **Simplify.** A full docs / doctree audit so information is easier to find and use.
**Version plan** (the User, 2026-11-21): **1.5.7 is the CURRENT RELEASE** (tag on `main` at daffb810). **1.5.8 = the security release** (#726, which replaced #668, plus the security-related items parked earlier; only security-related work enters it; the details stay in the issues, not here). **1.5.9 = the docs release** (the programme below; it was first planned as 1.5.8). Versions are MAJOR.MINOR.STEP, so there is no 1.5.7.x. Order: security (1.5.8) FIRST, then docs (1.5.9); the User confirmed security before docs even if session time is mixed. What is already merged stays; the 1.5.8 notes name it plainly (the `vde upgrade` command and its hardening) and headline the security items. Expect major changes to the docs in 1.5.9.
- **Priority split (refinement, 2026-11-21).** FIRST the docs a new student or onboarding developer reads (README, quick start, install, getting started, commands, upgrade and rebuild guidance, inside/outside the container). SECOND the VDE-developer docs. The mythos stays COMPLETELY for the AIs and is never the voice of a human-facing doc; but the developer docs MUST explain it in plain language: why it exists, how and why it is applied, which files carry it (`.gemini/`, `CLAUDE.md`, `AGENTS.md`, the rules, skills and state), which hooks and tests pin it, and how to maintain it. Verify every path, hook, test and command named there.
- **THE MANTRA: "Well documented, empirically tested."** It includes correct commands AND correct orderings: every command, flag, path and the order of steps is run (or traced through the code that parses it) before it is written down, and a page is done only when its steps were executed in the order printed and produced what the page says. Put the evidence in the PR (what was run, what appeared), as code PRs show RED then GREEN. A step that was never run does not go in a doc.
