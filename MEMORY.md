# VDE Project Memory

**Last Updated:** 2026-04-12T10:00:00Z
**Baseline Version:** 1.3.0 (The Sovereign Evolution)

---

## THE HEARTBEAT: PROOF OF LIFE CONTRACT
- **Mandatory Lifecycle**: The Proof of Life Contract (init -> create -> start -> enter -> rebuild -> stop -> rm -> add -> uninstall) is the non-negotiable heartbeat of the VDE.
- **Remediation Protocol**: Any status other than **100% GREEN** on `@system-spine` and core lifecycle tests triggers an immediate **Protocol Blockade**. No secondary features or refactoring are permitted until the heartbeat is restored to Green.


---

## SYSTEM EVOLUTION (2026-04-12) - v1.3.0 SOVEREIGN EVOLUTION
- **Pre-Strike Sentinel:** Implemented ZSH-native git hooks via `bin/install-githooks` to enforce shebang purity and secret scanning before every commit.
- **System Breath:** Upgraded `bin/vde start` with resource-aware ignition logic (Section 2), replacing static limits with dynamic CPU/Memory checks.
- **Archivist Vision:** Introduced `bin/vde-vision` for real-time observability of spoke health, port mappings, and version parity.
- **Image Purity:** Integrated automated verification in Docker build rituals to ensure no leftover `apt` cache remains in production spokes.
- **Identity Pulse:** Hardened SSH bridge monitoring within the orchestrator to ensure identity continuity across all execution paths.

## SYSTEM EVOLUTION (2026-04-10) - VDE 1.3.0 HARDENING STRIKE
- **Spoke Ignition Hook:** Implemented `/usr/local/bin/vde-spoke-ignition.zsh` hook in `scripts/vde-entrypoint.zsh`. This allows spokes to register background services that start automatically on container ignition, detaching them from the SSH gate lifecycle.
- **Rebuild Hardening:** Updated `bin/vde-rebuild` to default to `NOCACHE=true` and `PULL=true`. This ensures all rebuilds are "Pure Beskar," pulling fresh layers from original source images and capturing script changes that Docker's build-cache might miss.
- **Ignition Performance Optimization:** Redacted the recursive `sudo chown -R devuser:devuser /home/devuser` from the entrypoint. Replaced with targeted `chown` on `.ssh` directory. This resolves critical ignition blocks on large mounted workspaces (like JupyterLab).
- **JupyterLab Certification (100% Green):** 
    - Verified full Data Science stack (pandas, tensorflow, matplotlib, scikit-learn).
    - Implemented background startup via the new Ignition Hook.
    - Achieved "Born Ready (BTO)" compliance by moving heavy hydration (venv/pkg installation) and directory ownership finalization to the build phase.
- **Test Fidelity:** Updated `Makefile` to include `*.zsh` in all test targets and added reliable polling to the JupyterLab integration suite to account for service binding time.
- **Deterministic Error Engine (Phase 26 - The Sovereign Baseline):**
    - **Execution Wrapper:** Implemented `vde_run` in `lib/vde-core` to provide a unified, deterministic entry point for all command execution. It captures exit codes and system signals, immediately handing off to the centralized VDE Error Engine.
    - **Signal Translation:** Hardened `lib/vde-errors` to map raw kernel signals (130 SIGINT, 137 SIGKILL, 143 SIGTERM) into clear, remediable UX feedback.
    - **Global Interception:** Integrated a global `SIGINT` trap in `bin/vde` to provide instantaneous feedback and clean exits during user interruptions.
    - **Lock-Queue Model (Phase 25 - The Sovereign Baseline):**
        - **FIFO Sequencing:** Replaced competitive spinlocks with a deterministic First-In-First-Out (FIFO) ticket queue in `lib/vm-lock`. Processes are now served in exact arrival order.
        - **Concurrency Hardening:** Successfully verified strict ordering under "Thundering Herd" conditions (10+ simultaneous requests).
        - **Transparency:** Updated `lib/vm-lock` and `lib/vde-progress` to extract and report real process owners (PID/PGID) and queue positions during resource contention.
    - **100% BDD Fidelity:** Implemented and verified `error-handling.feature` and `concurrency-queue.feature` using real environmental conditions.

## SYSTEM BENCHMARKS (VDE 1.3.0)
- **Canonical Ignition Speed:** 3.959s. This is the benchmark for 3-VM Parallel Ignition (python, postgres, redis) on current hardware. Any future refactor that slows this down is a deviation from the Way.

## THE VERDICT: v1.3.0 READY
- **Utility Over Exploration**: The VDE has transitioned from a project of exploration to a project of utility. It is now a platform a developer can rely on for daily work without environmental friction.
- **Reliability Handshake**: Ignition is deterministic (< 4.5s), Identity is persistent (SSH bridge), and Security is enforced (GID mapping/8-field standard).
- **Certification**: The ecosystem is 100% stable and verified as of v1.3.0.
- **Sovereign Bridges Re-Forged:** Implemented 'Symbolic Handshake' via `socat` UNIX-proxying in `scripts/vde-entrypoint.zsh`, bypassing virtual filesystem permission blocks on Darwin.
- **Persistent Bridge established:** Added `.zshenv` export for `SSH_AUTH_SOCK` inside containers, ensuring non-interactive `vde exec` and login `vde enter` both inherit the host SSH agent identities.
- **Atomic Handshake Hardening (Section 10.3):** Implemented dynamic probe naming (`vde-recon-probe-${port}-${RANDOM}`) and 3s strike timeouts to neutralize Darwin kernel race conditions.
- **Certified 100% GREEN Suite:** Achieved 100% fidelity across Behave BDD features, ZSH unit, integration, and security tests.

## SYSTEM EVOLUTION (2026-04-07) - VDE 2.1.0 SOVEREIGN AUDIT
- **Sovereign Audit:** Pruned ~24,000 lines of redundant and "pink" (placeholder) test code. Condensed suite to high-fidelity core verifications.
- **Docker Socket Sovereignty:** Implemented dynamic GID mapping and `chmod 666` in the entrypoint for non-root Docker usage.

## SYSTEM EVOLUTION (2026-04-07) - VDE 2.0.9 HARDENING
- **Section 10: THE SEEKER’S RECON (Verification Law):** Codified the mandate for physical Docker handshakes (`docker run --rm`) for all port allocations.
- **Section 11: THE ARCHIVIST’S INTEL (Researcher Law):** Codified the Researcher sub-agent mandate for real-time implementation intelligence.
- **lib/vm-lock (Registry Retry Ritual):** Forged a new atomic locking library with ZSH-native floating-point jitter.

---

## CRITICAL: PROTOCOL ENFORCEMENT (THE CREED)

**ALL SESSIONS MUST ADHERE TO THESE RULES:**
1. **ZSH ONLY (ABSOLUTE)**: All shell scripts MUST use `#!/usr/bin/env zsh`. Bash is strictly forbidden.
2. **DEVELOP BRANCH ONLY**: All active work MUST occur on the `develop` branch. `main` is reserved for STABLE RELEASES ONLY. Direct work on `main` is prohibited.
3. **Main Agent is Orchestrator ONLY**: Spawns swarms for multi-file implementation.
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
| 27 | Sovereign Ecosystem | Verification & Hardening | ✅ COMPLETE |

### Phase 27 Completion (2026-04-08)
- **Unified Socket Discovery:** ✅ COMPLETE. Implemented `vde_get_host_ssh_sock` in `lib/vde-ssh` to unify discovery logic between CLI and libraries.
- **Rule Spine Enforcement:** ✅ COMPLETE. Integrated `bin/vde-enforce-uap.zsh --quiet` into the core `vde` entrypoint to ensure mandatory supervision of all actions.
- **Empirical Verification:** ✅ COMPLETE. High-fidelity BDD scenarios in `system-spine.feature` verified Docker Socket and SSH Agent bridges with 100% pass rate.
- **JupyterLab Spoke Certification:** ✅ COMPLETE. Successfully integrated and verified the `vde-jupyterlab` VM type with modern startup patterns (`tini`, `jupyter-server`).
