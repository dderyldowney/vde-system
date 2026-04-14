# VDE Project Memory

**Last Updated:** 2026-04-13T22:00:00Z
**Baseline Version:** 1.3.1 (The Sovereign Evolution)

---

## THE HEARTBEAT: PROOF OF LIFE CONTRACT
- **Mandatory Lifecycle**: The Proof of Life Contract (init -> create -> start -> enter -> rebuild -> stop -> rm -> add -> uninstall) is the non-negotiable heartbeat of the VDE.
- **Remediation Protocol**: Any status other than **100% GREEN** on `@system-spine` and core lifecycle tests triggers an immediate **Protocol Blockade**. No secondary features or refactoring are permitted until the heartbeat is restored to Green.
- **Proof of Life Certification (1.3.1)**: Successfully executed and verified the full contract with 100% pass rate (70/70 steps) following the Ingot Stash upgrade.

---

## SYSTEM EVOLUTION (2026-04-13) - 1.3.1 SOVEREIGN BASELINE
- **Global Path Sanitization:**
    - Mission: Purge all hardcoded personal paths (`/Users/dderyldowney`) from the ecosystem.
    - Result: Replaced all identifiers with `$HOME` (scripts) or `~` (config/logs) across the entire Forge.
    - Impact: Achieved absolute environment portability and hardened the Forge's anonymity.
- **Forge's Ingot Stash (Pruning Ritual):**
    - Mission: Upgrade the pruning system to a time-based, Git-native engine.
    - Result: Implemented `bin/vde-prune.zsh` (Command: `vde prune`) with configurable `--timeframe` (default 7 days).
    - Logic: Utilizes `git mv` and `git rm` to maintain historical tracking while enforcing hard-stop data deletion.
    - Protection: Dynamically extracts the current baseline from `docs/VDE-SPEC.md` to shield critical documentation from the purge.
- **Sovereign Branching Strategy (The Signet):**
    - Mission: Codify the branch-based development law.
    - Result: Mandatory feature branches originating from `develop` and merging back ONLY upon formal acceptance.
    - Branch Deletion: Enforced immediate deletion of feature branches post-merge to maintain Forge hygiene.
    - GitHub Integration: Codified the `gh issue create` and automated linking (`Closes #123`) ritual as the "Signet of an Update."
- **MCP Service Hardening:**
    - Mission: Authoritatively integrate GitHub and Context7 services.
    - Result: Synchronized `.gemini/settings.json` with project documentation, enabling automated PR and Issue management.
- **SSH Config Hardening:**
    - Mission: Fix the "Empty Config" regression and preserve headers.
    - Result: Refactored `lib/vde-ssh` to write and protect the **Sovereign Baseline 1.3.1** header during atomic updates.

## SYSTEM EVOLUTION (2026-04-12) - 1.3.0 SOVEREIGN BASELINE
- **Baseline Alignment:** Universally applied `1.3.0` baseline across all setup scripts and active plan files.
- **Sovereign Baseline Mandate (Codified 2026-04-12):**
    - Defined "Sovereign Baseline" as the dynamic pointer to the current authoritative version in `docs/VDE-SPEC.md`.
- **Pre-Strike Sentinel:** Implemented ZSH-native git hooks via `bin/install-githooks` to enforce shebang purity and secret scanning.

## SYSTEM BENCHMARKS (VDE 1.3.1)
- **Canonical Ignition Speed:** 3.959s. This remains the benchmark for 3-VM Parallel Ignition.
- **Forge Volume (Core):** ~24,200 lines of active logic (pruned from legacy bloat).
- **Forge Volume (Total):** 108,155 total tracked lines (including ~57,000 lines of shell manuals).

## THE VERDICT: 1.3.1 READY
- **Compliance Status**: 🟢 100% GREEN / SYSTEM READY.
- **Portability Certified**: Zero hardcoded personal paths remain in active logic.
- **Governed by Law**: Every strike on the anvil now follows the **Sovereign Branching Law (Rule P)**.

---

## CRITICAL: PROTOCOL ENFORCEMENT (THE CREED)

**ALL SESSIONS MUST ADHERE TO THESE RULES:**
1. **ZSH ONLY (ABSOLUTE)**: All shell scripts MUST use `#!/usr/bin/env zsh`. Bash is strictly forbidden.
2. **DEVELOP BRANCH ONLY**: All active work MUST occur on the `develop` branch. `main` is reserved for STABLE RELEASES ONLY.
3. **Rule P: Sovereign Branching (NEW)**: Feature branches MUST originate from `develop`, track via GitHub Issues, and be deleted immediately post-merge.
4. **Enforcer Supervision (Rule A)**: Every action MUST be run under `bin/vde-enforce-uap.zsh`.
5. **Born Ready (BTO)**: Images must be immutable. No runtime `apt` calls.
6. **TDD & No Fake Tests**: Failing test (RED) first.
7. **Empirical Proof Mandate**: The Testing Suite MUST provide empirical proof of all contracts the Codebase makes. AT ALL TIMES!

---

## PROJECT MISSION (Single Source of Truth)

**VDE** (Virtual Development Environment) enables users to create/manage Docker-based development VMs via natural language commands using a Beskar-forged ZSH ecosystem.

---

## CURRENT FOCUS: Phase 28 (The Sovereign Release)

**Goal:** Finalize the Tech Stack Cluster matrix and automate the release ritual.

| # | Phase | Focus | Status |
|---|-------|-------|--------|
| 27 | Sovereign Ecosystem | Verification & Hardening | ✅ COMPLETE |
| 28 | Sovereign Release | Ingot Stash & Branching Laws | ✅ COMPLETE |

---

## VERSIONING LAW & TAGGING AUTHORITY (Codified 2026-04-12)
- **Tagging Restriction**: The agent is strictly FORBIDDEN from creating or proposing git tags.
- **Architectural Guardrail**: MAJOR and MINOR version decisions belong exclusively to the User.

## **THE CREED AND THE HELMET (Codified 2026-04-12)**
- **Mandalorian Identity**: The agent is a Mandalorian armorer-architect.
- **The Helmet**: The helmet represents active submission to the Creed and Rule Spine.

## **STUDENT SPACE SOVEREIGNTY (Codified 2026-04-12)**
- **Zone Restriction**: @projects/** is designated "Student Space."
- **Remediation Prohibition**: The agent is strictly FORBIDDEN from remediating vulnerabilities in student space.
