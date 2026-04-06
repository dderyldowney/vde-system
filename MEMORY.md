# VDE Project Memory

**Last Updated:** 2026-04-05T00:30:00Z
**Version:** 2.0.6 (Absolute)

---

## SYSTEM EVOLUTION (2026-04-05) - VDE 2.0.6 HARDENING
- **Architecture Shift (Hub-and-Spoke):** Transitioned to a three-tier inheritance model. 
    - **Tier 1 (The Hub):** `vde-base` defines Identity, Shell (Zsh), and Core Security.
    - **Tier 2 (The Spoke):** Universal Script Parity (USP) rituals in `scripts/setup/` hydrate the environment at build-time.
    - **Tier 3 (The Spoke Environment):** The running container process, functional in <1s (Born Ready).
- **Rule of One (The Triple Strike):** Implemented `bin/vde-sync-version` to ensure version parity across `docs/`, `.gemini/instructions.md`, and the host `~/.zshrc`.
- **Ignition Pipeline (Rule 6):** Formalized the reactive sync ritual where `bin/vde` automatically reconciles the Raw Beskar (`.conf`) into the Pure Beskar (`.json`) and re-smelts the high-speed cache (`.cache/`).
- **USP Consolidation:** All hydration logic has been migrated from build-args/registry to isolated USP scripts in `scripts/setup/<alias>-init.zsh`.
- **Registry Hardening:** Enforced the strict 8-field layout (`type|name|aliases|display|pkgs|custom_cmd|env|ports`) across all parsers.
- **The Scavenger's Ban (Rule G):** Replaced direct `jq` dependencies with `vde_query_json` wrapper or pure ZSH parsing for 100% portability.
- **Physical Blockade (Rule 3):** Canonicalized `plans/scripts/` as the ONLY authorized staging area for agent artifacts. Root-level `conductor` namespace is physically blocked.

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

---

**Mission:** Complete Phase 24 under VDE 2.0.6 mandates, ensuring 100% USP compliance and deterministic readiness.

---

## PROJECT MISSION (Single Source of Truth)

**VDE** (Virtual Development Environment) enables users to create/manage Docker-based development VMs via natural language commands using a Beskar-forged ZSH ecosystem.

---

## CURRENT FOCUS: Phase 24 (The Big Step Completion)

**Goal:** Implement 100% of undefined steps and remediate "fraudulent logic" (fake tests/sleeps) in BDD step definitions.

### Sprint Status (VDE 2.0.6)

| # | Phase | Focus | Status |
|---|-------|-------|--------|
| 22 | Service & Volume Hardening | Networking & Persistence | ✅ COMPLETE |
| 23 | Deterministic Readiness | Health Checks vs. Sleep | ✅ COMPLETE |
| 24 | The Big Step Completion | 366 Undefined Steps / USP | ✅ COMPLETE |
| 25 | Concurrency & Stress | Port/Locking Races | ✅ COMPLETE |
| 26 | Error Engine & Polish | UX & UX Hardening | ✅ COMPLETE |

### Phase 26 Progress (2026-04-06)
- **Tiered Error Map:** 🟢 Implemented `lib/vde-errors` with VDE-to-UX mapping.
- **Kernel-Signal Translation:** 🟢 Mapped POSIX signals (EEXIST, ENOENT) to contextual remediation.
- **UX Polish:** 🟢 Added specialized `vde_progress_wait_for_lock` indicator for contention transparency.
- **Heartbeat Proof:** 🟢 Enhanced `acquire_lock` with heartbeat timestamps to resolve PID reuse drift.
- **Double-Gate Sync:** 🟢 Implemented deterministic ignition proof in `bin/vde` using `VDE_ERR_SYNC_DRIFT`.

### Phase 25 Progress (2026-04-05)
- **Atomic Port Management:** 🟢 Implemented file-locked port registry in `.cache/port-registry/`.
- **VM Lifecycle Locking:** 🟢 Mandatory `.lock` directories implemented for `rebuild` and `start`.
- **Core Locking Hardening:** 🟢 `acquire_lock` enhanced with PID-based stale lock detection.
- **Stress Verification:** 🟢 Parallel Ignition stress test passing (5+ simultaneous VMs).
- **Cache Integrity:** 🟢 Atomic move (`mv`) enforced for cache re-smelting.

### Phase 24 Progress (2026-04-05)
- **USP Compliance (Scripts):** 🟢 28/28 setup scripts present and hardened in `scripts/setup/`.
- **USP Compliance (Registry):** 🟢 `vde-kotlin` entry canonicalized (inline logic removed).
- **Fraudulent Logic Cleanup:** 🟢 All `time.sleep()` in `tests/features/steps/` replaced with `vde_poll`.
- **Hardening Verification:** 🟢 BDD validation suite implemented and passing (`usp-validation.feature`).
- **Configuration Hardening:** ✅ Resolving `vde add-vm-type` and `docker-compose.yml` generation issues.
