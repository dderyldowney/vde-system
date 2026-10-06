# VDE Session Handover: 2026-10-05
# @shared-law (Forge Component)

## SOVEREIGN STATE
- **Baseline**: 1.5.6 (Sovereign Baseline) — CERTIFIED
- **develop**: `2fe4cbb0` (Merge PR #536)
- **main**: `4d02d116` (production — 1.5.6, Merge PR #468 stable → main)
- **stable**: `7cc412f1` at the 1.5.6 roll (Merge PR #467)
- **Status**: 100% GREEN
- **Heartbeat**: 6/6 scenarios, 72/72 steps
- **Gospel Audit**: GOSPEL-SUCCESS

## CURRENT PROGRAMME: USB hardware access for embedded work

Students plug development boards into the Hub and use them from inside a Spoke.

- **PR #527** (Signet #526) — USB serial passthrough for `python`, `rust`, `c`, `cpp` ✅ MERGED
- **PR #529** (Signet #528) — stable per-port device names ✅ MERGED
- **PR #535** (Signet #533) — the `embed` Spoke: Python, C, C++, Rust, full LLVM suite ✅ MERGED
- **PR #536** (Signet #534) — ten defects in `vde add` / `vde uninstall` ✅ MERGED

Boards surface as `/dev/ttyUSB<n>` and `/dev/ttyACM<n>`: eight and four slots, hotplug tolerant, enumerated device-cgroup rules (no wildcards), stable names under `/dev/vde/by-port/` keyed to the physical socket. See `docs/guides/usb-serial-boards.md` and `docs/guides/embedded-development.md`.

## NEXT STRIKE

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

## OPEN ISSUES FOR NEXT STRIKE
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
