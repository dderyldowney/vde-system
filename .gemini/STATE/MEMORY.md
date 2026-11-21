# VDE Memory: Standing Watch
# @shared-law (Forge Component)

## SOVEREIGN BASELINE: 1.5.7
- VDE 1.5.7 is the unique, global Sovereign Baseline (cut 2026-11-21 at the User's direction; Signet #672).
- All prior versions (1.5.6 and earlier) are of historical archival value only.
- Heartbeat Certified: 2026-11-21 (6/6 scenarios, 73/73 steps)
- **Latest Release**: Tag 1.5.7 on main (SHA daffb810, the stable-into-main merge; contains code baseline c4560371 from docs/releases/1.5.7.md), published 2026-11-21
- **develop HEAD**: debc2e81 at the 1.5.7 roll (PR #673); later doc-only PRs advance it
- **stable HEAD**: daffb810 after the 1.5.7 roll: `.github/workflows/update-stable-alias.yml` force-pushes `stable` to `main` on every push to `main` (it moved stable from 66a04308 to daffb810, 13 s after PR #675). `stable` is for release plus updates, so a develop -> stable roll without a release is normal and leaves it ahead of `main` until the next release.

## 2026-05-06
## Security Audit: Postgres Dev Secret Build Arg Exposure
**Date:** 2026-05-06
**Branch:** fix/dockerfile-dead-arg
**Severity:** Medium
**Status:** Fixed

### Problem
The variable `POSTGRES_DEV_PASSWORD` was being passed as a `build.arg` in all service 
docker-compose files (postgres, redis, mysql, mongodb, couchdb, rabbitmq, 
nginx, jupyterlab). This caused the secret to be baked into image layers 
at build time — a Docker Scout security violation.

Additionally, `ARG POSTGRES_DEV_PASSWORD` (defaulting to empty) was declared in 
`configs/docker/vde-lang.Dockerfile` with no legitimate build-time use.

### Fix
- Removed the password variable from `build.args` in all service compose files.
- Removed the dead `ARG` declaration from `configs/docker/vde-lang.Dockerfile`.
- Runtime injection correctly handled by existing `env_file` blocks in each 
  service compose file — these were not modified.

### Verification
```bash
grep -rn "POSTGRES_DEV_PASSWORD" configs/docker/services/
grep -n "POSTGRES_DEV_PASSWORD" configs/docker/vde-lang.Dockerfile
```
Both should return no results in `build.args` blocks.

### Lesson
Secrets belong in `env_file` at runtime, never in `build.args` at build time.

## BRANCHING MODEL (CRITICAL - MEMORIZE)
| Branch | Purpose | Users Clone? |
|--------|---------|--------------|
| `main` | Official releases only (immutable, frozen at release) | NO |
| `stable` | Official release + patches/updates (most current stable) | **YES** |
| `develop` | Bug fixes and new feature work | NO |

**Flow:** `develop` → `stable` → `main`
- `stable` receives patches and updates continuously
- `main` only updated when `stable` is rolled into it for a release
- Users ALWAYS clone `stable` for most current stable code

## INSTALLATION (CORRECT)
```bash
git clone -b stable https://github.com/dderyldowney/vde-system.git VDE
cd VDE
bin/vde path-of-the-foundling
```

## WSL2 LOCKS REMEDIATION STATUS
**Phase:** Longterm Wait — Pending WSL2 Beta Tester Volunteers

### Completed (Safe, Environment-Agnostic)
- Tactical sweep (`bin/vde-tactical-sweep.zsh`) now cleans queue directories
- 5 scenario BDD test coverage (`tests/core-infrastructure/wsl2-locks-remediation.feature`)
- 12 WSL2 test step definitions simulating dead PID conditions
- All 72 Proof of Life steps passing

### Deferred (Requires WSL2 Testing Environment)
- WSL2 detection flag (`VDE_WSL2_DETECTED` in `lib/vde-constants`) — cannot validate false-positive detection
- Enhanced `zshexit` hook — race condition risks without WSL2
- Pre-flight lock health check — premature cleanup risks without WSL2
- Root `bin/vde` caller ID validation — WSL2-specific logic unvalidated

### Why Deferred
Per VDE Protocol: No environment-specific logic shall be implemented without empirical testing on target environment. WSL2 fixes blocked pending volunteer beta testers.

## NEXT STRIKES QUEUE
In the User's order (2026-11-21):
1. **#679** (Signet #676) — `vde upgrade`: merge it, with all CI and Sourcery feedback cleared.
2. **Roll `develop` into `stable` ONLY.** Not a release: no tag, no GitHub Release, no `main` mirror. A develop -> stable PR merged as a merge commit (never squash or rebase), after checks and sentinels are clean, with the User's written approval (Rule R).
3. **1.5.8: the docs release** (scope below).
4. **#671** — fix(armor): alias uniqueness inside the lock and stale SSH port locks (#538 items 1, 6, 7).
5. Ask the User about **#621** and **#629**.

Left open until after these: #441 function-trace JSONL export, #442 Ollama daemon connection, #539 USB debug probe, #653, #628, #615, #627, #631.

### 1.5.8 = THE DOCS RELEASE (scope APPROVED by the User, 2026-11-21)
1.5.8 is all about documentation. Nothing starts until the two goals above are done. Each part is its own Strike (Signet first).
- **Audience and voice.** Rewrite the docs for BOTH students AND VDE developers in a plain, direct, 1970s helper-manual voice: second person, concrete payoff first, short declarative sentences, a verification line in every step ("you should now see X; if not, see <page>"), dry wit sparingly. The excitement comes from competence transfer, not enthusiasm.
- **No mythos outside the AI.** Remove ALL mythos from everything student-facing AND developer-facing, including the VDE developer documentation. The mythos lives only in agent-facing files (`CLAUDE.md`, `AGENTS.md`, `.gemini/`). Use industry terms (Signet = Issue, Chronicle = Pull request, Strike = change, etc.). KEEP: Hub and Spoke (the real design philosophy) and the command `vde path-of-the-foundling` (the init + teaching path).
- **Real, true commands.** Every command, flag and path in a rewritten doc is verified by running it or by reading the code that parses it. Show how to pass flags.
- **Inside vs outside the container.** Explain what lives in a Spoke and what lives on the host, where a student's projects really are, and how to change it at install time (`--projects-dir` / `VDE_PROJECTS_DIR`; bootstrap has no prompt) and afterwards (`vde set-projects-dir`).
- **Link the docs to the code.** Pages that describe a library file or script link to that file (`lib/`, `bin/`, `scripts/`, `configs/`, `tests/`) so developers can open it. Surfacing the code means access from the docs, not relocating files. Docs heavily outweigh code today: take a census (code vs docs vs vendored) first; the vendored zsh manual (`docs/shell_manuals/zsh/zsh_5_9_us.md`, 31,344 lines) is 54% of all markdown and `bin/archive/` is 592 KB. Move or delete NOTHING without the User's decision; check `tests/` and the files that name `bin/archive/` first.
- **Simplify.** A full docs / doctree audit so information is easier to find and use.
