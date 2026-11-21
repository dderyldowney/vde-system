# VDE Memory: Standing Watch
# @shared-law (Forge Component)

## SOVEREIGN BASELINE: 1.5.7
- VDE 1.5.7 is the unique, global Sovereign Baseline (cut 2026-11-21 at the User's direction; Signet #672).
- All prior versions (1.5.6 and earlier) are of historical archival value only.
- Heartbeat Certified: 2026-11-21 (6/6 scenarios, 73/73 steps)
- **Latest Release**: Tag 1.5.7 on main (SHA daffb810, the stable-into-main merge; contains code baseline c4560371 from docs/releases/1.5.7.md), published 2026-11-21
- **develop HEAD**: debc2e81 at the 1.5.7 roll (PR #673); later doc-only PRs advance it
- **stable HEAD**: 66a04308 at the 1.5.7 roll (PR #674); main merge is daffb810 (PR #675)

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
In the User's order (2026-11-21, after the 1.5.7 release):
1. **#676** — feat(armor): `vde upgrade` updates an install to its branch's latest and says what to rebuild
2. The project-wide docs rework: student-facing docs only, manual-style voice, mythos replaced by industry terms (Hub and Spoke stay; `path-of-the-foundling` stays); its Signet opens when it starts
3. **#671** — fix(armor): alias uniqueness inside the lock and stale SSH port locks (#538 items 1, 6, 7)
4. Ask the User about **#621** and **#629**

Left open until after these: #441 function-trace JSONL export, #442 Ollama daemon connection, #539 USB debug probe, #653, #628, #615, #627, #631.
