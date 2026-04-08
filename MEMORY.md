# VDE Project Memory

**Last Updated:** 2026-04-07T23:55:00Z
**Version:** 2.1.0 (Absolute)

---

## SYSTEM BENCHMARKS (VDE 2.1.0)
- **Canonical Ignition Speed:** 3.959s. This is the benchmark for 3-VM Parallel Ignition (python, postgres, redis) on current hardware. Any future refactor that slows this down is a deviation from the Way.

## SYSTEM EVOLUTION (2026-04-07) - VDE 2.1.0 SOVEREIGN ECOSYSTEM
- **Docker Socket Sovereignty:** Implemented the "Atomic Handshake" in `scripts/vde-entrypoint.zsh`. Dynamically maps host `docker.sock` GID to `devuser` inside containers and grants 666 permissions to the socket, enabling non-root Docker usage within VMs.
- **SSH Agent Trust Bridge:** Standardized on `vde_student` identity. Implemented explicit host-to-guest agent socket mounting in `bin/vde` with macOS bridge symlinking in the entrypoint. Verified via `vde_verify_agent_forwarding`.
- **Unified CLI Routing:** Integrated `ask`, `port`, `info`, and `ssh` subcommands into `bin/vde`. Fixed argument displacement issues caused by premature `shift` calls.
- **BDD Infrastructure Hardening:** `run_vde_command` now filters infrastructure logs from `stdout` while preserving `vde_command_output_raw` for verbose handshake verification (e.g., SSH -v).

## SYSTEM EVOLUTION (2026-04-07) - VDE 2.0.9 HARDENING
- **Section 10: THE SEEKER’S RECON (Verification Law):** Codified the mandate for physical Docker handshakes (`docker run --rm`) for all port allocations.
- **Section 11: THE ARCHIVIST’S INTEL (Researcher Law):** Codified the Researcher sub-agent mandate for real-time implementation intelligence.
- **lib/vm-lock (Registry Retry Ritual):** Forged a new atomic locking library with ZSH-native floating-point jitter.

---

## CRITICAL: PROTOCOL ENFORCEMENT (THE CREED)

**ALL SESSIONS MUST ADHERE TO THESE RULES:**
1. **ZSH ONLY (ABSOLUTE)**: All shell scripts MUST use `#!/usr/bin/env zsh`. Bash is strictly forbidden.
2. **Main Agent is Orchestrator ONLY**: Spawns swarms for multi-file implementation.
3. **Enforcer Supervision (Rule A)**: Every action MUST be run under `bin/vde-enforce-uap.zsh`.
4. **Phase-End Re-Audit Swarm (Rule B)**: Mandatory re-audit swarm assuming errors exist.
5. **Explicit Commit Gate (Rule C)**: Requires explicit 'commit now' approval.
6. **Born Ready (BTO)**: Images must be immutable. No runtime `apt` calls.
7. **TDD & No Fake Tests**: Failing test (RED) first.
8. **Ghost Zone Kill Switch**: Any artifact outside `plans/scripts/` or presence of `conductor/` triggers immediate session halt.
9. **Verification Law (Section 10)**: Docker Probe mandatory for port allocation.
10. **Researcher Law (Section 11)**: Physical intent web research mandatory; Clone Prohibition absolute.
11. **Empirical Proof Mandate**: The Testing Suite MUST provide empirical proof of all contracts the Codebase makes. AT ALL TIMES!

---

## PROJECT MISSION (Single Source of Truth)

**VDE** (Virtual Development Environment) enables users to create/manage Docker-based development VMs via natural language commands using a Beskar-forged ZSH ecosystem.

---

## CURRENT FOCUS: Phase 27 (The Sovereign Ecosystem)

**Goal:** Empirical Verification and Hardening of Sovereign Bridges (Docker Socket & SSH Forwarding).

### Sprint Status (VDE 2.1.0)

| # | Phase | Focus | Status |
|---|-------|-------|--------|
| 24 | The Big Step Completion | 366 Undefined Steps / USP | ✅ COMPLETE |
| 25 | Concurrency & Stress | Port/Locking Races | ✅ COMPLETE |
| 26 | Forge Hardening Strike | Section 10/11 & vm-lock | ✅ COMPLETE |
| 27 | Sovereign Ecosystem | Verification & Hardening | 🟡 IN PROGRESS |

### Phase 27 Progress (2026-04-08)
- **Sovereign Audit (v2.1.0):** ✅ COMPLETE. Pruned ~24,000 lines of redundant and "pink" test code. Condensed suite to 2 high-fidelity Behave features and 11 verified ZSH scripts.
- **Sovereignty (27.2):** ✅ COMPLETE. Docker Socket Sovereignty and SSH Agent Trust Bridge are implemented in `scripts/vde-entrypoint.zsh`.
- **Verification (27.3):** ⏳ IN PROGRESS. Implementing high-fidelity empirical verification for sovereign bridges in `system-spine.feature`.
