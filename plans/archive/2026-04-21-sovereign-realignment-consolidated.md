# Consolidated Sovereign Realignment & Purification Plan (Issue 1.4.1-CSR)
<!-- @shared-law (Forge Component) -->

## Objective
This consolidated strike aims to achieve total alignment with the Sovereign Baseline (1.4.1) by addressing architectural fractures, removing hardcoded environmental dependencies, and purifying technical debt identified by the UAP Enforcer.

## Track 1: Architectural Domain Realignment (@armor, @forge, @shared-law)
**Goal:** Surgically realign artifacts into their proper Project domains to establish a 100% self-contained Project 1 (@armor) engine.

### Actions:
- [ ] **Rule 23 Alignment:** Consistently use `display` instead of `display_name` and `service_ports` (plural) across all documentation, libraries, and tests.
- [ ] **Engine Isolation:** Realign core binaries (`vde-init`, `vde-bootstrap`, `vde-spine-check.zsh`, etc.) and system libraries (`vde-log`, `vde-errors`, `vde-security`, etc.) into the `@armor` domain.
- [ ] **Governance Realignment:** Realign all BDD feature files and step definitions into the `@forge` (@forge) domain.
- [ ] **The Gospel Update:** Synchronize `docs/SOVEREIGN_CHARTER.md` and `docs/VDE-SPEC.md` to reflect these hierarchical shifts.

## Track 2: Portability & Standardized Querying (@shared-law)
**Goal:** Eliminate host-level dependencies and hardcoded pathing to ensure the "Naked Machine" mandate is met.

### Actions:
- [ ] **Path Remediation:** Replace hardcoded `/home/devuser` paths in `scripts/setup/*.zsh` with relative `~devuser` assignments (e.g., `local dev_home=~devuser`).
- [ ] **Scavenger's Ban Migration:** Replace direct `jq` calls in `lib/vde-metrics` (and any other missed files) with the `vde_query_json` safety wrapper.

## Track 3: UAP Compliance & Purification (@forge)
**Goal:** Achieve 100% UAP PASS by purifying scripts flagged with "Fake ZSH" warnings.

### Actions:
- [ ] **UAP Warning Purification:** Insert ZSH-native parameter expansion flags (shibboleths) into entrypoints (`scripts/vde-entrypoint.zsh`), test runners (`tests/run-sovereign-tests.zsh`), and githooks (`githooks/proof-of-life-hook.zsh`) to satisfy the sentinel.

## Verification & Testing (Dual Audit Loop)
1. **Sovereign Audit:** Run `bin/vde-enforce-uap.zsh` to ensure all core mandates (including new alignment) are satisfied.
2. **Heartbeat Certification:** Execute the absolute lifecycle test (`python3 -m behave tests/features/core-infrastructure/proof-of-life-the-contract.feature`).
3. **Registry Audit:** Verify `bin/vde-info` and `bin/vde-ps` correctly display the `display` field.
4. **Portability Audit:** Grep for `/home/devuser` in `scripts/setup/` (should be 0).
5. **Gospel Audit:** Verify `docs/VDE-SPEC.md` reflects the 1.4.1 Sovereign Baseline structure.

---
*Created on 2026-04-21 by the Armorer-Architect.*
