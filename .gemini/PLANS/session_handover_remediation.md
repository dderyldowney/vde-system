# Remediation Plan: VDE 2.0.6 Architectural Alignment

## High-Priority Architectural Debt
- **vde-info speedup**: Performs multiple `docker inspect` calls. Should cache these labels in `.docker-state/*.json` during startup/refresh.
- **USP Compliance**: Ensure all VM types have an isolated hydration ritual in `scripts/setup/` and that `data/vm-types.json` correctly points to them.
- **Ignition Link**: Modify `bin/vde` to call `bin/vde-sync-version` during ignition to ensure the "Automatic Versioning" mandate is met.

## Remediation Goals
- **Deterministic Readiness (The big step)**:
    - Replace arbitrary `time.sleep()` calls in Python BDD Step Definitions (`tests/features/steps/`) with deterministic polling using `vde_poll`.
    - Rename `wait_for_condition` in `shell_helpers.py` to `vde_poll` to align with the project's canonical terminology.
- **USP Verification**: Confirm all hydrations move to Tier 2 (The Spoke) rituals in `scripts/setup/`. Purge any inline logic or reliance on build-args for runtime setup.
- **Zero-Host Dependency**:
    - Ensure `vde_query_json` is correctly defined in `lib/vde-core`.
    - Refactor all legacy `jq` calls to use the `vde_query_json` wrapper.
- **100% Coverage**: Complete the implementation of the 366 undefined steps to ensure 100% documentation-to-code parity under v2.0.6 constraints.

## Task Tracking
- [X] System Re-Alignment (The Triple Strike)
- [X] Update MEMORY.md to v2.0.6
- [X] Update session_handover.md with Sovereign Audit mandate
- [ ] Rename `wait_for_condition` to `vde_poll` in `shell_helpers.py`
- [ ] Implement `vde_poll` based logic in `configuration_management_steps.py`
- [ ] Update `bin/vde` ignition sequence with `bin/vde-sync-version`
- [ ] Audit and verify 100% USP compliance in `scripts/setup/`

See ./session_handover.md
