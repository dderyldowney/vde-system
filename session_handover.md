# Session Handover — Phase 22: Service & Volume Hardening

**Current Status:** 🟡 BLOCKED by Container Instability / Terminal Permissions.

## The Blocker
Service containers (vde-postgres, vde-redis) are starting but then immediately exiting or entering a restart loop.
- `docker logs` showed Postgres starting, but the container didn't stay alive.
- Hypothesis: The `command` block in `docker-compose.yml` is finishing its script, allowing the container to die.
- Interference: iTerm2 permission prompts are likely causing automation timeouts.

## Immediate Next Steps
1.  **Rebuild Base**: `docker build -t vde-base:latest -f configs/docker/vde-base.Dockerfile .`
2.  **Clean Refresh**: `rm -rf configs/docker/services/postgres configs/docker/services/redis data/postgres data/redis`
3.  **Regenerate**: `vde create postgres && vde create redis`
4.  **Verify**: `python3 -m behave tests/features/docker-required/service-volume-hardening.feature`
