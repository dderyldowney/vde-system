# VDE Session Handover: 2026-11-21
# @shared-law (Forge Component)

## Paired Update Policy
This file is one half of a pair with [plans/session_handover_remediation.md](../../plans/session_handover_remediation.md). A change that touches either file MUST touch the other in the same PR, so accomplishments (here) and outstanding debt (there) cannot drift apart. `bin/paired_update_enforcer` (CI workflow "Paired Update Check") compares the files a PR changed against its base and fails when only one of the two changed.

## SOVEREIGN STATE
- **Baseline**: 1.5.7 (Sovereign Baseline) — RELEASED 2026-11-21, tag 1.5.7 on `main` (daffb810; code baseline `c4560371`): https://github.com/dderyldowney/vde-system/releases/tag/1.5.7
- **develop**: advances past `debc2e81` (the 1.5.7 roll, PR #673) with each merged PR; read it from `git log`
- **main**: `daffb810` (production — 1.5.7, Merge PR #675 stable → main)
- **stable**: read the tip with `git ls-remote origin stable`; after the 1.5.7 release it equalled `main` (PR #674 rolled develop into it at 66a04308; the Update Stable Alias workflow then reset it to `main` on the #675 push). `stable` is for release plus updates; it may sit ahead of `main` between releases.
- **Status**: 100% GREEN
- **Heartbeat**: 6/6 scenarios, 73/73 steps
- **Gospel Audit**: GOSPEL-SUCCESS

## NEXT STRIKE
Done as of 2026-11-21: 1.5.7 released; `vde upgrade` (#679), the 1.5.7 record (#678), the state files (#681), the `vde upgrade` review fixes (#684, Signet #683) and the develop -> stable roll (#682, merge commit, no release). VERIFY with `gh pr list --state merged --limit 10` before relying on this line.
Queue, in the User's order:
1. **1.5.8, the SECURITY release** (#668 plus the security-related items parked earlier, and ONLY security-related work): its own Signet, PR and release chain, with the User's approval at each outward step. Security comes BEFORE docs, even if session time is mixed.
2. **1.5.9, the docs release** (approved scope below): starts only after 1.5.8 ships; Signet first, each part its own Strike.
3. **#671** — alias uniqueness inside the lock and stale SSH port locks (#538 items 1, 6, 7; Signet open, investigation done, no code).
4. Then ask about #621 and #629.

### Version plan (the User, 2026-11-21)
**1.5.7 is the CURRENT RELEASE** (tag on `main` at daffb810). **1.5.8 = the security release** (#668, plus the security-related items parked earlier; only security-related work enters it; the details stay in the issues, not here). **1.5.9 = the docs release** (the programme below; it was first planned as 1.5.8). Versions are MAJOR.MINOR.STEP, so there is no 1.5.7.x. Order: security (1.5.8) FIRST, then docs (1.5.9); the User confirmed security before docs even if session time is mixed. What is already merged stays; the 1.5.8 notes name it plainly (the `vde upgrade` command and its hardening) and headline the security items. Expect major changes to the docs in 1.5.9.

### 1.5.9 = THE DOCS RELEASE (scope APPROVED by the User, 2026-11-21; renumbered from 1.5.8)
1.5.9 is all about documentation. Each part is its own Strike (Signet first).
- **Audience and voice.** Rewrite the docs for BOTH students AND VDE developers in a plain, direct, 1970s helper-manual voice: second person, concrete payoff first, short declarative sentences, a verification line in every step ("you should now see X; if not, see <page>"), dry wit sparingly. The excitement comes from competence transfer, not enthusiasm.
- **No mythos outside the AI.** Remove ALL mythos from everything student-facing AND developer-facing, including the VDE developer documentation. The mythos lives only in agent-facing files (`CLAUDE.md`, `AGENTS.md`, `.gemini/`). Use industry terms (Signet = Issue, Chronicle = Pull request, Strike = change, etc.). KEEP: Hub and Spoke (the real design philosophy) and the command `vde path-of-the-foundling` (the init + teaching path).
- **Real, true commands.** Every command, flag and path in a rewritten doc is verified by running it or by reading the code that parses it. Show how to pass flags.
- **Inside vs outside the container.** Explain what lives in a Spoke and what lives on the host, where a student's projects really are, and how to change it at install time (`--projects-dir` / `VDE_PROJECTS_DIR`; bootstrap has no prompt) and afterwards (`vde set-projects-dir`).
- **Link the docs to the code.** Pages that describe a library file or script link to that file (`lib/`, `bin/`, `scripts/`, `configs/`, `tests/`) so developers can open it. Surfacing the code means access from the docs, not relocating files. Docs heavily outweigh code today: take a census (code vs docs vs vendored) first; the vendored zsh manual (`docs/shell_manuals/zsh/zsh_5_9_us.md`, 31,344 lines) is 54% of all markdown and `bin/archive/` is 592 KB. Move or delete NOTHING without the User's decision; check `tests/` and the files that name `bin/archive/` first.
- **Simplify.** A full docs / doctree audit so information is easier to find and use.
- **Priority split (refinement, 2026-11-21).** FIRST the docs a new student or onboarding developer reads (README, quick start, install, getting started, commands, upgrade and rebuild guidance, inside/outside the container). SECOND the VDE-developer docs. The mythos stays COMPLETELY for the AIs and is never the voice of a human-facing doc; but the developer docs MUST explain it in plain language: why it exists, how and why it is applied, which files carry it (`.gemini/`, `CLAUDE.md`, `AGENTS.md`, the rules, skills and state), which hooks and tests pin it, and how to maintain it. Verify every path, hook, test and command named there.
- **THE MANTRA: "Well documented, empirically tested."** It includes correct commands AND correct orderings: every command, flag, path and the order of steps is run (or traced through the code that parses it) before it is written down, and a page is done only when its steps were executed in the order printed and produced what the page says. Put the evidence in the PR (what was run, what appeared), as code PRs show RED then GREEN. A step that was never run does not go in a doc.

## CURRENT PROGRAMME: USB hardware access for embedded work

Students plug development boards into the Hub and use them from inside a Spoke.

- **PR #527** (Signet #526) — USB serial passthrough for `python`, `rust`, `c`, `cpp` ✅ MERGED
- **PR #529** (Signet #528) — stable per-port device names ✅ MERGED
- **PR #535** (Signet #533) — the `embed` Spoke: Python, C, C++, Rust, full LLVM suite ✅ MERGED
- **PR #536** (Signet #534) — ten defects in `vde add` / `vde uninstall` ✅ MERGED

Boards surface as `/dev/ttyUSB<n>` and `/dev/ttyACM<n>`: eight and four slots, hotplug tolerant, enumerated device-cgroup rules (no wildcards), stable names under `/dev/vde/by-port/` keyed to the physical socket. See `docs/guides/usb-serial-boards.md` and `docs/guides/embedded-development.md`.

## DEFERRED: #539 (hardware-gated)

- **#539** — USB debug-probe access (SWD/JTAG) for `vde-embed` only. Grants bus 1 (128 enumerated rules on major 189) plus `/dev/bus/usb:ro`; bus 7 (the T2 virtual controller holding every internal device) stays kernel-refused. Includes udev rules installed on the Hub and `devuser` added to `dialout` and `plugdev`. **Gated on an STM32F3DISCOVERY arriving 2026-10-12 to 2026-10-14**; the mechanism is provable before then, the probe-specific behaviour is not.

## OPEN, DEFERRED BY THE CLAN LEADER

Not actionable until open issues are reviewed as a set:

- **#530** Gospel audit's script check silently skips on a stale doc path
- **#531** `templates/compose-language.yml` has drifted from its 32 generated files
- **#532** `dns-check` shifts argv the dispatcher already consumed
- **#537** the Proof of Life never builds what it adds, leaving add→create uncertified
- **#538** 17 deferred findings from the #534 review
- **#540** this handover refresh

Pre-dating the programme: **#441** function-trace JSONL export, **#442** Ollama daemon connection.

## RECENT STRIKES (1.5.6 Sovereign Baseline)
- **PR #462** — chore(release): VDE 1.5.6 Sovereign Baseline ✅ MERGED
- **PR #460** — fix(docker): pre-create host projects/data/logs dirs to prevent root-owned bind mounts ✅ MERGED
- **PR #458** — fix(docker): stop entrypoint from corrupting host docker.sock group ownership ✅ MERGED
- **PR #455** — feat(base): inject TERM override for ghostty into devuser ~/.zshrc ✅ MERGED

## PRIOR STRIKES (1.5.5 Sovereign Baseline)
- **PR #452** — docs(wsl2): establish WSL2 locks remediation plan and test coverage ✅ MERGED
- **PR #427** — fix(ci): resolve prune syntax error and add Bot Feedback Mandate ✅ MERGED
- **PR #425** — release(vde): bump to 1.5.5 Sovereign Baseline ✅ MERGED
- **PR #423** — fix(docs): correct docs/operations/ to match implementation ✅ MERGED
- **PR #422** — fix(docs): correct docs/reference/ and docs/api/ to match implementation ✅ MERGED
- **PR #419** — fix(governance): reconcile vde-spec.md with implementation reality ✅ MERGED
- **PR #417** — chore(docs): update development docs to current state ✅ MERGED
- **PR #415** — chore(docs): update PROJECT_STATUS.md Proof of Life date ✅ MERGED
- **PR #411** — chore(docs): update SECURITY.md to 1.5.4 Sovereign Baseline standards ✅ MERGED
- **PR #409** — fix(docs): purge stale 1.5.2 references and update session handover ✅ MERGED
- **PR #408** — fix(docs): purge stale 1.5.2 references ✅ MERGED

## BRANCHING STRATEGY
Feature work on `develop` → merge to `stable` (QA) → merge to `main` (Release)
Retag + GitHub Release always on `main`

## TAGS POLICY
Tags (X.X.X) and GitHub Releases occur EXCLUSIVELY on `main`. No tags on `develop` or `stable`.

## NEXT STEPS
- Forge standing watch on `develop`

## DEFERRED: #441 and #442 (after the queue above)
- **#442** — feat(forge): establish canonical connection to local Ollama daemon
- **#441** — feat(governance): enhance function-trace with JSONL export and secure dry-run

**This is the Way.**

## PENDING WSL2 LOCKS REMEDIATION (Longterm Wait)
**Status:** Deferred pending WSL2 beta tester volunteers

### Completed
- Tactical sweep updated to clean queue directories
- 5 scenario test coverage for WSL2 lock conditions
- 12 WSL2 test step definitions added

### Deferred (awaiting WSL2 beta testers)
- WSL2 environment detection (`lib/vde-constants`) — cannot safely implement without WSL2 test environment
- Enhanced `zshexit` hook — race condition risks without WSL2 testing
- Pre-flight lock health check — premature cleanup risks without WSL2 environment
- Root `bin/vde` caller ID check — WSL2-specific logic not yet validated

**Volunteers needed:** WSL2 users to test and validate lock robustness fixes.

**This is the Way.**
