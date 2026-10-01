# VDE Test Status Report (measured on 1.5.6)
<!-- @forge (Governance Sentinel) -->

Measured on 2026-09-30 at commit `6308fe33` (Linux, Docker 29.8.2). The suite as a whole is **not** at 100%; the failing scenarios and their causes are listed in [docs/development/testing.md](../docs/development/testing.md).

| Suite | Result |
| :--- | :--- |
| Full BDD suite (`behave tests/features/`) | 107 of 116 scenarios passed, 9 failed; 638 of 720 steps passed, 9 failed, 73 skipped; 26 of 28 features passed |
| Proof of Life (`proof-of-life-the-contract.feature`) | 6 of 6 scenarios passed |
| Sovereign Tests (`tests/run-sovereign-tests.zsh`) | 12 of 12 suites with the Python `jsonschema` module available; 11 of 12 without it (tracked in #492) |
| Spine check (`bin/vde-spine-check.zsh`) | all 4 pillars OK |
| UAP enforcement (`bin/vde-enforce-uap.zsh`) | success, exit 0 |
| Gospel audit (`bin/vde-gospel-audit.zsh`) | success, but its undocumented-script check is skipped because `docs/available-scripts.md` does not exist |

The rows in the tables below are exercised by these results: the four pillars by the spine check, the lifecycle rows by the six Proof of Life scenarios (init; create and start; enter and rebuild; stop and rm; add and uninstall; hardened rebuild), and the Sovereign Bridges row by the spoke-to-spoke SSH and DNS discovery features, which passed in the full run.

## Core Infrastructure
| Feature | Status | Description |
| :--- | :--- | :--- |
| **Pillar I: Zsh** | ✅ PASS | Zsh 5.9+ verified. |
| **Pillar II: Git** | ✅ PASS | Git 2.44.0+ verified. |
| **Pillar III: Docker** | ✅ PASS | Docker Daemon & Alpine Probe verified. |
| **Pillar IV: SSH** | ✅ PASS | SSH Agent & `vde_student` identity verified. |

## Lifecycle Verification (The Contract)
| Step | Status | Description |
| :--- | :--- | :--- |
| **`vde init`** | ✅ PASS | Initialized VDE structure and network. |
| **`vde create`** | ✅ PASS | Image creation from Beskar Registry. |
| **`vde start`** | ✅ PASS | Spoke ignition and port mapping. |
| **`vde enter`** | ✅ PASS | Secure shell execution via bridge. |
| **`vde rebuild`** | ✅ PASS | Image hydration and USP compliance. |
| **`vde stop`** | ✅ PASS | Graceful Spoke decommissioning. |
| **`vde rm`** | ✅ PASS | Total Spoke removal. |

## System Spine (Tetrad)
| Integration | Status | Description |
| :--- | :--- | :--- |
| **UAP Enforcement** | ✅ PASS | `bin/vde-enforce-uap.zsh` strictly active. |
| **Spine Check** | ✅ PASS | `bin/vde-spine-check.zsh` silent pre-flight. |
| **Sovereign Bridges** | ✅ PASS | Docker Socket & SSH Forwarding verified (1.5.6) |

---
**Measured**: 2026-09-30
**Baseline**: 1.5.6 (commit `6308fe33`)
**Heartbeat (Proof of Life)**: 6 of 6 scenarios passed
---
