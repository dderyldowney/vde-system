# VDE Testing Strategy - 1.5.3 (The Sovereign Baseline)
<!-- @shared-law (Sovereign Law) -->

This document defines the absolute empirical standards for the Virtual Development Environment (VDE). All functional code MUST be verified by this suite.

## 1. THE SUPREME GATE: @SYSTEM-SPINE
The System Spine tetrad is the foundational audit gate. If any pillar fails, the system triggers an immediate **Protocol Blockade**.

| Pillar | Technology | Verification Method |
|--------|------------|---------------------|
| I      | **Zsh**    | `zsh --version` (Voice of the Tribe) |
| II     | **Git**    | `git init` in transient workspace (The Chronicler) |
| III    | **Docker** | `docker run --rm` diagnostic probe (The World-Forge) |
| IV     | **SSH**    | `ssh-add -l` identity check (The Bridge) |

## 2. BDD PERFORMANCE METRICS (1.5.3)
As of **2026-04-26**, the VDE Behavior Driven Development suite is at **100% Fidelity**.

| Metric | Count | Status |
|--------|-------|--------|
| **Total Features** | 5 | ✅ GREEN |
| **Total Scenarios** | 17 | ✅ GREEN |
| **Total Steps** | 137 | ✅ GREEN |
| **Undefined Steps** | 0 | ✅ NONE |
| **Pass Rate** | 100% | ✅ ABSOLUTE |

## 3. CORE INFRASTRUCTURE SUITE
Located in `tests/features/core-infrastructure/`:

1. **proof-of-life-the-contract.feature**: Verifies the 8 lifecycle states (create, rebuild, start, enter, stop, remove, add, uninstall).
2. **system-spine.feature**: Hardens the 4 Pillars and deterministic Hub-to-Spoke ignition.
3. **jupyterlab-spoke.feature**: Certifies the Data Science stack and background service ignition.
4. **tech-stack-cluster.feature**: Verifies parallel ignition of Python, PostgreSQL, and Redis as a unit.
5. **usp-validation.feature**: Enforces Universal Script Parity across all registered VM setup scripts.

## 4. EXECUTION PROTOCOLS

### Full BDD Strike
```zsh
# Execute the complete behavior suite
behave
```

### Full System Test (Unit + Integration + BDD)
```zsh
# Standard Make target
make test
```

### Targeted Spine Check
```zsh
# Verify the 4 non-negotiable pillars
behave --tags @system-spine
```

## 5. HARDENED MANDATES
- **Zero Placeholder Policy**: No "pink" steps permitted. Every assertion MUST verify physical file existence, container state, or network response.
- **Auto-Cleanup**: The `after_scenario` hook in `environment.py` ensures 100% removal of test containers (labeled `vde.test=true`).
- **USP Compliance**: Every hydration script in `scripts/setup/` must pass the `usp-validation` suite before it is considered production Beskar.

---
**Status:** SYSTEM CERTIFIED (1.5.3)
