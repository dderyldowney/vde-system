# Remediation Plan: Migration Regressions (Rule B)
<!-- @forge (Governance Sentinel) -->

The Phase-End Re-Audit Swarm identified critical regressions following the consolidation into `.gemini/`.

## Identified Issues

### 1. Critical CLI Failure: `Error loading vde-errors`
- **Symptom**: Almost all `vde` subcommands fail with `Error loading vde-errors`.
- **Root Cause**: The refactoring of `bin/vde` or `lib/vde-errors` during the ZSH-native compliance phase likely introduced a path discovery or sourcing issue.
- **Impact**: Blocks all integration and VM-lifecycle tests.

### 2. BDD Feature Failures
- **Cache System**: `ASSERT FAILED: Cache file should exist at ~/VDE/.cache/vm-types.cache`.
- **Parser Intent**: Expected intents (e.g., `restart_vm`, `status`) are returning empty strings.
- **Service Hardening**: Containers are reported as "not running" or failing to become healthy within timeouts.

## Remediation Steps

### Phase 1: Fix CLI Core (Blocking)
1. **Investigate `bin/vde`**: Verify how `vde-errors` is being sourced. Check `VDE_ROOT_DIR` discovery.
2. **Investigate `lib/vde-errors`**: Ensure it satisfies ZSH-native compliance without breaking its exports or internal logic.
3. **Verify**: Run `bin/vde help` and `bin/vde list` to ensure the "Error loading" message is gone.

### Phase 2: Fix Cache & Parser
1. **Cache**: Run `bin/vde rebuild-cache` manually and inspect `.cache/`. Update BDD steps if paths shifted.
2. **Parser**: Verify `vde-parser` logic. Ensure it correctly detects intents after the ZSH-native refactor.

### Phase 3: Verify Environment
1. **Docker**: Ensure the test environment is clean (`vde nuke --force` if necessary, then `vde init`).
2. **Re-Audit**: Rerun all Behave scenarios until stable.

## Final Approval Gate
Once all regressions are fixed and tests pass, I will request explicit approval to:
1. Commit the `.gemini/` consolidation.
2. Delete the legacy `.claude/` and `.kilocode/` directories.
