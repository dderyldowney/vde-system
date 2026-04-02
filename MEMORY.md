# VDE Project Memory

**Last Updated:** 2026-04-02T12:00:00Z

---

## CRITICAL: PROTOCOL ENFORCEMENT

**ALL SESSIONS MUST ADHERE TO THESE RULES:**
1. **ZSH-ONLY MANDATE**: Every script in `bin/` and `lib/` MUST use `#!/usr/bin/env zsh`. Non-ZSH scripts are a protocol bypass and will block execution.
2. **8-STEP STARTUP**: All entry points MUST follow the authoritative 8-step startup sequence defined in `VDE-SPEC.md`.
3. **UAP ENFORCEMENT**: `bin/vde-enforce-uap.zsh` MUST be called during initialization to verify workspace integrity.
4. **CANONICAL NETWORKING**: Always use canonical `vde-` container names (e.g., `vde-postgres`, `vde-redis`) for inter-container communication and environment variables. `localhost` refers ONLY to the local container or host machine, not the service VM. The name without `vde-` is the software, not the VM.
5. **ORCHESTRATOR ROLE**: Gemini CLI acts EXCLUSIVELY as a strategic orchestrator. Complex or repetitive tasks MUST be delegated to sub-agents.
6. **INHERITANCE MANDATE**: Sub-agents MUST inherit context from the Main Agent. Freshly pulling information already present in the Main Agent's context (e.g., @-loaded files) is strictly forbidden.
7. **SPEC v1.7.2**: Authoritative spec v1.7.2 implemented with Cluster/SSH hardening and strict protocol enforcement across all core commands.
8. **Rule A (Enforcer Supervision)**: Every single action (shell commands, sub-agent dispatches, verification steps, and cleanup) MUST be run under the supervision of the Enforcer (`bin/vde-enforce-uap.zsh`).
9. **Rule B (Phase-End Re-Audit Swarm)**: Every development phase MUST automatically conclude with a supervised re-audit swarm. This swarm MUST assume errors exist, search for regressions or weak spots, rerun all relevant Behave scenarios, and provide a summary of findings. Skipping or shortening this re-audit is a total mandate failure.
10. **Rule C (Explicit Commit Gate)**: Following a successful re-audit, the agent MUST ask for explicit 'commit now' approval from the user. No commits are allowed without this manual gate.

---

**Mission:** Ensure core Docker infrastructure is working and passing, then stack Docker features one by one

---

## PROJECT MISSION (Single Source of Truth)

**VDE** (Virtual Development Environment) enables users to create/manage Docker-based development VMs via natural language commands.

**Target Users:** New users, students with zero-to-minimal knowledge

**Core Capabilities (from VDE-SPEC.md):**
1. Create/Start/Stop/Remove VMs via `vde` command
2. Natural language parsing ("start python", "create go VM")
3. SSH access to VMs
4. Service VMs (PostgreSQL, Redis, etc.)
5. Multi-VM clusters (vde cluster command)

---

## RECENT ACHIEVEMENTS (Wave 4 & Phase P)
- **Resolved ssh-vm argument parsing [HIGH] debt**: Refactored `bin/ssh-vm` to use a robust argument parser that correctly handles all edge cases and legacy formats.
- **Implemented `vde cluster` Command**: Added native support for multi-VM cluster persistence and lifecycle management, including NLP support for cluster operations.
- **Phase 21 (Cluster Persistence) Complete**: Successfully implemented and verified multi-VM cluster persistence and synchronization.
- **Phase P Architectural Refactoring**: Successfully reorganized `configs/docker/` into `languages/` and `services/` subdirectories. Updated all core logic, CLI scripts, and BDD tests to be category-aware.
- **User-Centric BDD Refactor**: Completed global refactor of all features and steps to use the canonical `vde` CLI, enforcing the User perspective across the entire project.
- **Resolved Systemic Debt**: Consolidated VM loaders, host-path resolvers, and SSH port extractors into canonical helpers in `vm_common.py`.
- **Remediated ssh-agent Leakage**: Implemented surgical `stop` logic in `lib/vde-ssh` and `bin/ssh-setup`. Updated `environment.py` and BDD steps to use the isolated `VDE_SSH_AGENT_ENV` file, ensuring no orphaned processes are left behind.
- **Hardened Parser & BDD Tests**: Updated `vde-parser` intent detection for `ADD_VM_TYPE` and `REMOVE_VM`. Fixed BDD steps to handle canonical `vde-` name prefixing and compact `FLAGS:` output format.
- **Phase 1-14, 17-21 Complete**: Successfully implemented and verified core lifecycle, configuration, error handling, installation, SSH, and cluster persistence (100% registration).
- **Verified Standard User identity**: Reverted all 'vdeuser' occurrences to 'devuser' to align with VDE-SPEC.md v1.5.1.

---

## CURRENT FOCUS: Docker Feature Stack

**Goal:** Validate core Docker infrastructure first, then stack Docker-tagged features on top one by one.
**Rule:** Nothing Docker works if core capabilities are not properly implemented.

### Production Sprint (Phases 22-26)

| # | Phase | Focus | Status |
|---|-------|-------|--------|
| 22 | Service & Volume Hardening | Networking & Persistence | ✅ COMPLETE |
| 23 | Deterministic Readiness | Health Checks vs. Sleep | ✅ COMPLETE |
| 24 | The Big Step Completion | 366 Undefined Steps | 🔴 Blocked |
| 25 | Concurrency & Stress | Port/Locking Races | ⚪ Pending |
| 26 | Error Engine & Polish | UX & SPEC v2.0.0 | ⚪ Pending |

### Phase 0 Progress (2026-04-02)
- **O-1 through O-8:** ✅ Complete
- **Universal Agent Protocol (UAP):** ✅ **IMPLEMENTED**. All agents and commands reworked across `.claude/` and `.kilocode/` to enforce Phase 0-5 lifecycle, TDD (No Fake Tests), Dual Approval.
- **Service & Volume Hardening (Phase 22):** ✅ **COMPLETE**. 
- **Deterministic Readiness (Phase 23):** ✅ **COMPLETE**.
    - Replaced all static `sleep` calls >0.5s in `bin/` and `lib/` with high-precision 0.2s polling loops using ZSH floating-point arithmetic (`typeset -F`).
    - Standardized `vde_wait_for_container_healthy` to use `docker inspect --health` directly.
    - Added **Rule A (Enforcer Supervision)**, **Rule B (Phase-End Re-Audit)**, and **Rule C (Commit Gate)** as permanent global mandates to `AGENTS.md`, `GEMINI.md`, `CLAUDE.md`, and `VDE-SPEC.md`.
    - Added **Inheritance Mandate** to ensure sub-agents use Main Agent context.
- **Integration Features (Phases 8-19):** ✅ Core registration and hardening complete.
- **SSH & Remote Access (Phase 20):** ✅ **100% COMPLETE** (12/12 scenarios).
- **Cluster Persistence (Phase 21):** ✅ **100% COMPLETE**. Multi-VM cluster persistence verified.
- **Baseline:** 272 non-integration scenarios **PASS** under UAP mandates.
- **Next:** Phase 24 (The Big Step Completion)

---

## KEY PRINCIPLES

1. **DRY or DIE**: One function, parameterized. No copy-paste.
2. **Tests Prove Goals**: Every test must validate a stated goal from SPEC.
3. **No Dead Code**: Unused imports, helpers, step files = DELETE.
4. **Minimal Footprint**: If it doesn't help users accomplish goals = REMOVE.
5. **Core First**: Validate infrastructure before stacking features on top.
6. **No Direct Docker Calls**: Step files must use `bin/vde` CLI — not `docker` subprocess calls.
