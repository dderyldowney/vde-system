# VDE Memory: Standing Watch
# @shared-law (Forge Component)

## SOVEREIGN BASELINE: 1.5.5
- VDE 1.5.5 is the unique, global Sovereign Baseline.
- All prior versions are of historical archival value only.
- Heartbeat Certified: 2026-05-05 (6/6 scenarios, 72/72 steps)

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
