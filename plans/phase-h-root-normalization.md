# Phase H: Root Normalization & Phase H Actions

Goals
- Enforce VDE_ROOT_DIR as sole root for host-side operations.
- Prevent hard-coded absolute paths; ensure all code uses "$VDE_ROOT_DIR/...".
- Introduce runtime guards and observability hooks for phase verification.

Status: IN PROGRESS

Plan & Actions
- [A] Codebase audit for absolute paths outside VDE_ROOT_DIR ✅ DONE
  - Fixed: configs/ssh/config, test_shutdown.sh, test_perf_integration.zsh
  - Verified: no /Users/dderyldowney paths in source code
- [B] Phase H instrumentation scaffolding ✅ DONE
  - Added timing to generate_plan() in lib/vde-parser (logs ms when DEBUG)
- [C] Guard hook additions ✅ DONE
  - lib/vde-root-guard sourced at startup in bin/vde
- [D] Documentation updates 📋 IN PROGRESS
  - Update MEMORY.md and session_handover_remediation.md cross-links
- [E] Verification steps 📋 IN PROGRESS
  - Run test suite
  - Confirm no hard-coded paths in source

Deliverables
- Updated code with root-based path resolution; guard scripts; instrumentation scaffolding.
- Phase H plan companion documentation.
- Updated MEMORY with Phase H context and status.

Next Actions
1. Update MEMORY.md with Phase H completion status
2. Run full test suite verification
3. Mark Phase H complete
