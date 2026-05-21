# VDE Memory: Standing Watch
# @shared-law (Forge Component)

## SOVEREIGN BASELINE: 1.5.5
- VDE 1.5.5 is the unique, global Sovereign Baseline.
- All prior versions (1.5.4, 1.5.2, 1.5.1, 1.5.0) are of historical archival value only.
- Heartbeat Certified: 2026-05-06 (6/6 scenarios, 72/72 steps)
- **Latest Release**: Tag 1.5.5 on main (SHA 55d287dd)
- **develop HEAD**: 4053d890 (#427 — fix(ci): resolve prune syntax error)
- **stable HEAD**: d7c252df (merge: vde-release.zsh automation)

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

### Current System Status
- Existing lock system handles WSL2 via stale lock buster (57-70) and stale ticket buster (79-87)
- 10-second grace period provides legitimate process cleanup window
- Tests simulate dead PID conditions without WSL2-specific code
