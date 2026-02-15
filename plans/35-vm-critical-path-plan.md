# VM Critical Path Test Plan

## Objective
Create a high-priority, fast-executing test that validates the full lifespan of a single VM: creation, rebuild, start, stop, rebuild without cache, SSH key generation, public key copy to VM, SSH access, and deletion. This ensures the core user journey works end-to-end.

## Critical Path Scenario
Create a new feature: `tests/features/critical-path/vm-full-lifecycle.feature`

Single scenario: "Full VM lifecycle for Python development environment"

Steps:
1. **Create VM**: Run `vde create python` - verify config generated, docker-compose.yml created.
2. **Initial Rebuild & Start**: Run `vde start python --rebuild` - verify build, container starts, SSH port allocated.
3. **SSH Key Generation**: Verify SSH keys generated if none exist, public key copied to VM's authorized_keys.
4. **SSH Access**: SSH to VM, verify connection works, shell is zsh, workspace mounted.
5. **Stop VM**: Run `vde stop python` - verify container stops.
6. **Rebuild without Cache**: Run `vde start python --rebuild --no-cache` - verify no-cache build, starts.
7. **Verify SSH Still Works**: SSH again, confirm access.
8. **Delete VM**: Run `vde delete python` - verify config removed, container gone, SSH entry cleaned.

## Implementation
- Use `@critical-path @requires-docker-host` tag.
- Run this test first in CI (under 2 minutes target).
- Use Python VM for consistency (common use case).

## Benefits
- Early detection of regressions in core flow.
- Confidence in basic VM operations.
- Fast feedback loop.

## Dependencies
- Core infrastructure tests pass.
- SSH setup functional.