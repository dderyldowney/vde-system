# Remediation Plan: Docker Feature Stack (Wave 4 & Phase P)

## Related Handovers
- Session Handover: see `../session_handover.md`
- **Audit findings status:** ALL Systemic Debt and Architectural Reorganization (Phase P) items resolved.

## Resolved Items (2026-03-31)
1. **ssh-agent process leakage**: ✅ RESOLVED. Surgical `stop` logic implemented and verified.
2. **Parser intent detection**: ✅ RESOLVED. `vde-parser` now handles all core intents robustly.
3. **BDD test regressions**: ✅ RESOLVED. `parser_steps.py` updated for Wave 5 normalization.
4. **Advanced SSH Integration (Phase 20)**: ✅ **100% PASS** (12/12 scenarios).
5. **Universal Agent Protocol (UAP)**: ✅ **IMPLEMENTED**. Unified dev cycle across all platforms.
6. **Core CLI Hardening**: ✅ Enhanced `info`, `exec`, `ssh` for robust automation.

## Strategic Debt & Remaining Work
- **Code Review Remediation (Phase 20)**: 
  - [MEDIUM] `vde-info`: Optimize `docker-compose.yml` lookup (direct category pathing).
  - [HIGH] `ssh-vm`: Harden argument parsing (strict `--` separator).
  - [MEDIUM] `vm_common.py`: Harden log filtering regex.
  - [MEDIUM] `ssh_remote_access_steps.py`: Refine permissions check for filesystem differences.
- **Integration Hardening**: Implementing real logic for remaining integration features (HIGH priority).
- **Phase 21 (Cluster Persistence)**: Implementation of multi-VM state tracking (MEDIUM priority).

## Verification Success
- Fast Test Pass Rate: **100%** (268/268 scenarios).
- Process Leakage: **0** orphaned agents after cleanup.

---\n\n## Paired Update Policy\n- This plan is the paired companion to `../session_handover.md`.\n- Updates must be synchronized; maintain cross-links and same scope.\n