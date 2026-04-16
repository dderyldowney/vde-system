# VDE Project Memory

**Last Updated:** 2026-04-15T20:45:00Z
**Baseline Version:** 1.3.7 (The Sovereign Hardening)

---

## THE HEARTBEAT: PROOF OF LIFE CONTRACT
- **Gateway Entrypoint**: The **Four Pillars Gateway** (`tests/features/core-infrastructure/gateway-pillars.feature`) is the mandatory entrypoint to the Proof of Life ritual. It MUST be passed with 100% success to certify the host environment's readiness. Failure results in an immediate **Program Blockade**.
- **Mandatory Lifecycle**: The Proof of Life Contract (init -> create -> start -> enter -> rebuild -> stop -> rm -> add -> uninstall) is the non-negotiable heartbeat of the VDE.
- **Remediation Protocol**: Any status other than **100% GREEN** on `@system-spine` and core lifecycle tests triggers an immediate **Protocol Blockade**. No secondary features or refactoring are permitted until the heartbeat is restored to Green.
- **Proof of Life Certification (1.3.7)**: Successfully verified the v1.3.7 hardening with 100% pass rate (72/72 steps).

---

## SYSTEM EVOLUTION (2026-04-15) - 1.3.7 SOVEREIGN BASELINE
- **Chronicle Strengthening (Four Pillars):**
    - Mission: Enforce GitHub best practices for traceability and discipline.
    - Result: Codified the "Four Pillars of the Chronicle" into the Rule Spine (GEMINI.md, AGENTS.md, VDE_PROTOCOL.md).
    - The Pillars: 1) Focused Strike (Scope), 2) Unbreakable Link (Auto-closure), 3) Dual-Gate Review (Agent + User), 4) Evidence Mandate (Raw test output).
    - Artifact: Updated `.github/PULL_REQUEST_TEMPLATE.md` to physically enforce these laws.
- **Security Scanner Integration:**
    - Mission: Automate vulnerability detection and dependency management.
    - Result: Integrated **Dependabot** (`dependabot.yml`) and **CodeQL** (`codeql-analysis.yml`).
    - Scope: Automated weekly dependency updates and static analysis for Python and Shell code (using the new `actions` language support).
- **Stable Alias & Default Branch:**
    - Mission: Native GitHub automation support.
    - Result: Aligned the repository's default branch to `develop`.
    - Automation: Implemented `update-stable-alias.yml` to automatically mirror `main` to a `stable` branch upon push.
    - Verification: Users can now natively execute `git clone -b stable` to receive the certified Baseline.
- **Automated Issue Closure:**
    - Mission: Replicate native auto-closure for non-default branches.
    - Result: Implemented `close-linked-issues.yml` to manually close issues linked in PRs merged into `develop`.
- **Total Version Synchronization:**
    - Mission: Absolute parity across the Sovereign Artifact Set.
    - Result: Executed `bin/vde-sync-version` to align all manuals, records, and test expectations with v1.3.7.

## SYSTEM EVOLUTION (2026-04-13) - 1.3.1 SOVEREIGN BASELINE
- **Global Path Sanitization:**
    - Result: Replaced all identifiers with `$HOME` or `~` across the entire Forge.
- **Forge's Ingot Stash (Pruning Ritual):**
    - Result: Implemented `bin/vde-prune.zsh` with Git-native engine.
- **Sovereign Branching Strategy (The Signet):**
    - Result: Codified mandatory feature branch lifecycle.

## SYSTEM BENCHMARKS (VDE 1.3.7)
- **Canonical Ignition Speed:** 3.959s. Benchmark for 3-VM Parallel Ignition.
- **Forge Volume (Core):** ~24,500 lines of active logic.
- **Forge Volume (Total):** 108,300 total tracked lines.

## THE VERDICT: 1.3.7 READY
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
4. **Enforcer Supervision (Rule A)**: Every action MUST be run under `bin/vde-enforce-uap.zsh`.
5. **Born Ready (BTO)**: Images must be immutable. No runtime `apt` calls.
6. **TDD & No Fake Tests**: Failing test (RED) first.
7. **Empirical Proof Mandate**: PRs MUST contain raw terminal output proof.

---

## PROJECT MISSION (Single Source of Truth)

**VDE** (Virtual Development Environment) enables users to create/manage Docker-based development VMs via natural language commands using a Beskar-forged ZSH ecosystem.

---

## CURRENT FOCUS: Phase 29 (Tech Stack Expansion)

**Goal:** Broaden the Spoke hydration library and Tech Stack Cluster matrix.

| # | Phase | Focus | Status |
|---|-------|-------|--------|
| 28 | Sovereign Release | Ingot Stash & Branching Laws | ✅ COMPLETE |
| 29 | Tech Stack Clusters | Spoke Hydration Expansion | 🚧 NEXT |

---

## VERSIONING LAW & TAGGING AUTHORITY
- **Identity Lock**: "We are The Covert" (Rule 13).
- **Thesis surveillance**: Interplay monitoring active.

## **SEMANTIC BRANCH TARGETING LAW**
- **Living Mark**: The `stable` alias mirror is the production entry point.
- **Auto-Closure**: Natively supported via default branch `develop` and manual CI fallback.
