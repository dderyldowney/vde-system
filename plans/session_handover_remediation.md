# Remediation Plan: Docker Feature Stack (Wave 4 & Phase P)

## Related Handovers
- Session Handover: see `../session_handover.md`
- **Audit findings status:** ALL Systemic Debt and Architectural Reorganization (Phase P) items resolved. UAP Hardening (Phase U) is 100% COMPLETE.

## Priority Remediation Items

### [HIGH] `ssh-vm`: Harden argument parsing (strict `--` separator)
- **Status:** ✅ **RESOLVED (2026-04-01)**
- **Fix:** Implemented robust parsing in `bin/ssh-vm` that honors the `--` separator to stop VDE option processing.
- **Verification:** 100% pass in `tests/features/docker-required/ssh-vm-hardening.feature`.

### [MEDIUM] Phase 21 (Cluster Persistence): Start working on multi-VM state persistence.
- **Status:** ✅ **RESOLVED (2026-04-01)**
- **Fix:** Implemented `vde cluster` command and `lib/vde-cluster-utils`. Added JSON persistence in `.docker-state/clusters/`.
- **Verification:** 100% pass in `tests/features/docker-required/cluster-persistence.feature`.

### [LOW] Optimization: `vde-info` speedup (caching container labels)
- **Status:** PENDING
- **Issue:** `vde-info` performs multiple `docker inspect` calls. Should cache these labels in `.docker-state/*.json` during startup/refresh.

---

## Technical Health Dashboard
- **UAP Compliance:** 🟢 100% (Enforced via `bin/vde-enforce-uap.zsh`)
- **BDD Fast Tests:** 🟢 100% (272/272 scenarios)
- **Process Leakage:** **0** orphaned agents after cleanup.

---

## Paired Update Policy
- This plan is the paired companion to `../session_handover.md`.
- Updates must be synchronized; maintain cross-links and same scope.
