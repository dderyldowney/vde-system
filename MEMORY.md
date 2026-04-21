# VDE Project Memory
<!-- @shared-law (Tribal Memory) -->

**Last Updated:** 2026-04-18T19:30:00Z
**Baseline Version:** 1.4.1 (The Sovereign Evolution)

---

## THE HEARTBEAT: PROOF OF LIFE CONTRACT
- **Gateway Entrypoint**: The **Four Pillars Gateway** (`tests/features/core-infrastructure/gateway-pillars.feature`) is the mandatory entrypoint to the Proof of Life ritual. It MUST be passed with 100% success to certify the host environment's readiness. Failure results in an immediate **Program Blockade**.
- **Mandatory Lifecycle**: The Proof of Life Contract (init -> create -> start -> enter -> rebuild -> stop -> rm -> add -> uninstall) is the non-negotiable heartbeat of the VDE.
- **Remediation Protocol**: Any status other than **100% GREEN** on `@system-spine` and core lifecycle tests triggers an immediate **Protocol Blockade**. No secondary features or refactoring are permitted until the heartbeat is restored to Green.
- **Proof of Life Certification (1.4.1)**: Successfully verified the v1.4.1 evolution with 100% pass rate (72/72 steps).

---

## SYSTEM EVOLUTION (2026-04-18) - 1.4.1 SOVEREIGN EVOLUTION
- **SSH Key "Hard Rule" Implementation:**
    - Mission: Automate SSH key generation within `vde init` to eliminate boot loops.
    - Result: Implemented inline `ssh-setup init` within `bin/vde-init`. Missing keys are now generated immediately during initialization.
    - Forced Refresh: The `--force` flag now explicitly triggers SSH key regeneration.
- **Unified SSH Management:**
    - Result: Integrated `ssh-setup` and `ssh-sync` as first-class subcommands in the unified `vde` CLI.
- **Onboarding Ritual (Path of the Foundling):**
    - Result: Forged `bin/vde-path-of-the-foundling` and `docs/FOUNDLING_GUIDE.md` to streamline the user journey.
- **Test Debt Remediation:**
    - Result: Eliminated all "pink" test debt, replacing `pass` stubs with empirical verification logic.

## SYSTEM EVOLUTION (2026-04-15) - 1.4.0 SOVEREIGN BASELINE
- **Plan Audit & Remediation (The Great Pruning):**
    - Mission: Systematically audit, remediate, and archive all legacy plans.
    - Result: Remediated the `bin/add-vm-type` concurrency race condition by moving port allocation *inside* the global lock.
    - Archival: Identified and moved all 6 remaining legacy/redundant plans to the archive.
    - Workspace Status: The root `plans/` directory is now 100% clean of pending implementable missions, containing only living records.
- **Chronicle Strengthening (Four Pillars):**
    - Result: Codified the "Four Pillars of the Chronicle" (Focus, Link, Dual-Gate, Evidence).
    - Enforcement: Implemented automated GitHub labeling and PR title validation.
- **Security & Automation:**
    - Result: Integrated Dependabot, CodeQL, and automated `stable` alias mirroring.
- **Proof of Life Certification:**
    - Final Status: Verified the hardened baseline with 100% pass rate (245/245 steps).

## SYSTEM EVOLUTION (2026-04-13) - 1.3.1 SOVEREIGN BASELINE
- **Global Path Sanitization:**
    - Result: Replaced all identifiers with `$HOME` or `~` across the entire Forge.
- **Forge's Ingot Stash (Pruning Ritual):**
    - Result: Implemented `bin/vde-prune.zsh` with Git-native engine.
- **Sovereign Branching Strategy (The Signet):**
    - Result: Codified mandatory feature branch lifecycle.

## SYSTEM BENCHMARKS (VDE 1.4.1)
- **Canonical Ignition Speed:** 3.959s. Benchmark for 3-VM Parallel Ignition.
- **Forge Volume (Core):** ~24,500 lines of active logic.
- **Forge Volume (Total):** 108,300 total tracked lines.

## THE VERDICT: 1.4.1 READY
- **Compliance Status**: 🟢 100% GREEN / SYSTEM HARDENED.
- **Security Certified**: CodeQL and Dependabot active.
- **Workflow Automated**: Auto-closure and stable alias active.

---

## CRITICAL: PROTOCOL ENFORCEMENT (THE CREED)

**ALL SESSIONS MUST ADHERE TO THESE RULES:**
0. **MANDATORY SESSION BOOTSTRAP**: If the CLI is Claude, `AGENTS.md` and `.gemini/instructions.md` MUST be read and fully applied at the start of every session.
1. **ZSH ONLY (ABSOLUTE)**: All shell scripts MUST use `#!/usr/bin/env zsh`.
2. **THE ANVIL IS DEFAULT**: All active work MUST occur on the `develop` branch.
3. **Rule P: Sovereign Branching**: Feature branches MUST originate from `develop`, track via GitHub Issues, and be deleted immediately post-merge.
4. **Detailed Signet Mandate**: Every GitHub Issue (Signet) MUST include exhaustive technical detail, exact command mappings, and specific mission scope at the moment of creation to enable immediate remediation planning.
5. **Enforcer Supervision (Rule A)**: Every action MUST be run under `bin/vde-enforce-uap.zsh`.
6. **Born Ready (BTO)**: Images must be immutable. No runtime `apt` calls.
7. **TDD & No Fake Tests**: Failing test (RED) first.
8. **Empirical Proof Mandate**: PRs MUST contain raw terminal output proof.

---

## PROJECT MISSION (Single Source of Truth)

**VDE** (Virtual Development Environment) enables users to create/manage Docker-based development VMs via natural language commands using a Beskar-forged ZSH ecosystem.

---

## CURRENT FOCUS: Phase 31 - Advanced Orchestration

**Active Mission**: Advanced Orchestration (DNS Discovery)

**Goal:** Implement inter-Spoke DNS resolution and discovery to allow VMs to communicate via hostnames rather than static IP/Port mappings.

| Phase | Focus | Status |
|-------|-------|--------|
| 31 | Advanced Orchestration | 🛠 IN PLANNING |
| 32 | Agent Self-Correction | ⏳ QUEUED |

---

## VERSIONING LAW & TAGGING AUTHORITY
- **Identity Lock**: "We are The Covert" (Rule 13).
- **Thesis surveillance**: Interplay monitoring active.

## **SEMANTIC BRANCH TARGETING LAW**
- **Living Mark**: The `stable` alias mirror is the production entry point.
- **Auto-Closure**: Natively supported via default branch `develop` and manual CI fallback.
