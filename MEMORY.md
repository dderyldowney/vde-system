# VDE Project Memory

**Last Updated:** 2026-04-07T19:00:00Z
**Version:** 2.0.9 (Absolute)

---

## SYSTEM BENCHMARKS (VDE 2.0.9)
- **Canonical Ignition Speed:** 3.959s. This is the benchmark for 3-VM Parallel Ignition (python, postgres, redis) on current hardware. Any future refactor that slows this down is a deviation from the Way.

## SYSTEM EVOLUTION (2026-04-07) - VDE 2.0.9 HARDENING
- **Section 10: THE SEEKER’S RECON (Verification Law):** Codified the mandate for physical Docker handshakes (`docker run --rm`) for all port allocations. Eliminated "Host Assumption" (lsof/nc) which is unreliable on Darwin/macOS.
- **Section 11: THE ARCHIVIST’S INTEL (Researcher Law):** Codified the Researcher sub-agent mandate for real-time implementation intelligence. Enforced an Absolute Clone Prohibition—all external research must be re-forged in VDE-native ZSH.
- **lib/vm-lock (Registry Retry Ritual):** Forged a new atomic locking library with ZSH-native floating-point jitter and 10-attempt limits. Neutralized the "Thundering Herd" on the Global Config.
- **Absolute Deterministic Ignition:** Achieved 100% success rate on parallel ignition and concurrent registry updates under high stress.
- **Schema Hardening:** Updated `vm-types.schema.json` to support hyphenated VM names and enforced non-empty display names in `add-vm-type`.

## SYSTEM EVOLUTION (2026-04-05) - VDE 2.0.6 HARDENING
- **Architecture Shift (Hub-and-Spoke):** Transitioned to a three-tier inheritance model. 
- **Rule of One (The Triple Strike):** Implemented `bin/vde-sync-version` for version parity.
- **Ignition Pipeline (Rule 6):** Formalized reactive sync ritual.
- **USP Consolidation:** All hydration logic migrated to `scripts/setup/`.
- **Registry Hardening:** Enforced strict 8-field layout.
- **The Scavenger's Ban (Rule G):** Replaced direct `jq` dependencies.
- **Physical Blockade (Rule 3):** Canonicalized `plans/scripts/`.

---

## CRITICAL: PROTOCOL ENFORCEMENT (THE CREED)

**ALL SESSIONS MUST ADHERE TO THESE RULES:**
1. **ZSH ONLY (ABSOLUTE)**: All shell scripts MUST use `#!/usr/bin/env zsh`. Bash is strictly forbidden.
2. **Main Agent is Orchestrator ONLY**: Spawns swarms for multi-file implementation.
3. **Enforcer Supervision (Rule A)**: Every action MUST be run under `bin/vde-enforce-uap.zsh`. Sovereign Execution pre-authorized.
4. **Phase-End Re-Audit Swarm (Rule B)**: Mandatory re-audit swarm assuming errors exist.
5. **Explicit Commit Gate (Rule C)**: Requires explicit 'commit now' approval.
6. **Born Ready (BTO)**: Images must be immutable. No runtime `apt` calls.
7. **TDD & No Fake Tests**: Failing test (RED) first. `time.sleep()` and placeholder tests are forbidden.
8. **Ghost Zone Kill Switch**: Any artifact outside `plans/scripts/` or presence of `conductor/` triggers immediate session halt.
9. **Verification Law (Section 10)**: Docker Probe mandatory for port allocation.
10. **Researcher Law (Section 11)**: Physical intent web research mandatory for obscured paths; Clone Prohibition absolute.

---

## PROJECT MISSION (Single Source of Truth)

**VDE** (Virtual Development Environment) enables users to create/manage Docker-based development VMs via natural language commands using a Beskar-forged ZSH ecosystem.

---

## CURRENT FOCUS: Phase 26 (The Forge Hardening)

**Goal:** Achieve Absolute Deterministic Ignition and Registry Sovereignty.

### Sprint Status (VDE 2.0.9)

| # | Phase | Focus | Status |
|---|-------|-------|--------|
| 22 | Service & Volume Hardening | Networking & Persistence | ✅ COMPLETE |
| 23 | Deterministic Readiness | Health Checks vs. Sleep | ✅ COMPLETE |
| 24 | The Big Step Completion | 366 Undefined Steps / USP | ✅ COMPLETE |
| 25 | Concurrency & Stress | Port/Locking Races | ✅ COMPLETE |
| 26 | Forge Hardening Strike | Section 10/11 & vm-lock | ✅ COMPLETE |

### Phase 26 Progress (2026-04-07)
- **Section 10 & 11 Implementation:** ✅ CODIFIED. Updated `instructions.md` and `docs/VDE-SPEC.md`.
- **Atomic Locking Hardening:** ✅ IMPLEMENTED. Created `lib/vm-lock` with staggered jitter and reference-counted re-entrancy.
- **Registry Concurrency:** ✅ FIXED. Registry writes are now 100% deterministic under parallel load.
- **Port Probe Reliability:** ✅ HARDENED. `find_available_ssh_port` uses unique probe container names and kernel-level directory locks.
- **Schema Validation:** ✅ FIXED. Corrected inverted logic in `vde-core` and updated schema patterns.
- **Signal Translation:** ✅ IMPLEMENTED. `vde_error_map` handles SIGINT/SIGTERM.
- **UX Polish:** ✅ INTEGRATED. `lib/vde-progress` spinners integrated into core workflows.
