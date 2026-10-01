# VDE Testing Strategy - 1.5.6 (The Sovereign Baseline)
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

## 2. BDD PERFORMANCE METRICS (1.5.6)
Measured on **2026-09-30** at commit `6308fe33`: full run of `behave tests/features/` on Linux with Docker 29.8.2 (6 min 17 s, the Python `jsonschema` module available to subprocesses). The suite is **not** at 100%.

| Metric | Count | Status |
|--------|-------|--------|
| **Total Features** | 28 (26 passed, 2 failed) | ❌ 2 FAILING |
| **Total Scenarios** | 116 (107 passed, 9 failed) | ❌ 9 FAILING |
| **Total Steps** | 720 (638 passed, 9 failed, 73 skipped) | ❌ 9 FAILING |
| **Undefined Steps** | 0 | ✅ NONE |
| **Scenario Pass Rate** | 92.2% (107 of 116) | ❌ BELOW 100% |

The Proof of Life (`proof-of-life-the-contract.feature`) passed 6 of 6 scenarios in this run. The CI-safe Sovereign Tests runner (`./tests/run-sovereign-tests.zsh`) passed 12 of 12 suites with `jsonschema` available and 11 of 12 without it (tracked in #492).

Failing scenarios at this commit, with the cause seen in the run log:

- `student-guidance/next-steps-guidance.feature` (8 scenarios, lines 14-78): the shared step `the Hub is synchronized to version 1.5.3` fails with `Sync error: Hub at 1.5.6, expected 1.5.3`, so none of them reaches the command under test. The version is hard-coded in the feature.
- `governance/gospel-audit.feature:20` "Detection of Undocumented Scripts": the audit printed `[GOSPEL-SUCCESS]` instead of `[CRITICAL FAILURE] Undocumented scripts detected`. `bin/vde-gospel-audit.zsh` skips its undocumented-script check when `docs/available-scripts.md` is missing, and that file does not exist in the repository.

Running the full suite against a Docker host is not side-effect free. In this measurement it removed the 4 stopped `vde-*` containers that existed beforehand (seen by comparing `docker ps -a` before and after; the responsible scenario was not identified) and re-dated tracked documents through the doc-sync scripts. Run it on a disposable host, or commit first and review `git status` afterwards.

## 3. CORE INFRASTRUCTURE SUITE
Located in `tests/features/core-infrastructure/` (22 feature files at commit `6308fe33`):

- **proof-of-life-the-contract.feature**: Verifies the 8 lifecycle states (create, rebuild, start, enter, stop, remove, add, uninstall).
- **system-spine.feature**: Hardens the 4 Pillars and deterministic Hub-to-Spoke ignition.
- **gateway-pillars.feature**: Verifies the Four Pillars Gateway before Proof of Life ignition.
- **jupyterlab-spoke.feature**: Certifies the Data Science stack and background service ignition.
- **tech-stack-cluster.feature**: Verifies parallel ignition of Python, PostgreSQL, and Redis as a unit.
- **usp-validation.feature**: Enforces Universal Script Parity across all registered VM setup scripts.
- **technical-integrity.feature**: Validates core technical integrity guards.
- **student-daily-usage.feature**: Verifies the student daily workflow end-to-end.
- **vde-init-empirical.feature**: Empirical verification of `vde init` lifecycle.
- **ssh-config-version.feature**: Validates SSH config versioning and synchronization.
- **sovereign-scope.feature**: Certifies VDE_ROOT_DIR relative pathing and portability.
- **location-blind-portability.feature**: Verifies location-blind execution from any working directory.
- **armor-integrity.feature**: Validates the Armor product runtime integrity.
- **armor-autonomy.feature**: Certifies AI-blind, Hub-blind student autonomy.
- **spoke-to-spoke-ssh.feature**: Verifies inter-Spoke SSH connectivity.
- **locking-recursion-fix.feature**: Validates config lock recursion prevention.
- **concurrency-queue.feature**: Verifies the 3-VM concurrent limit and queue behavior.
- **rust-path-repro.feature**: Validates Rust toolchain path resolution.
- **error-handling.feature**: Certifies error messaging and recovery paths.

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
**Status:** SYSTEM CERTIFIED (1.5.6)
