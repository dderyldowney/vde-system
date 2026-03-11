# Phase H: Root Normalization & Phase H Actions

Goals
- Enforce VDE_ROOT_DIR as sole root for host-side operations.
- Prevent hard-coded absolute paths; ensure all code uses "$VDE_ROOT_DIR/...".
- Introduce runtime guards and observability hooks for phase verification.

Plan & Actions
- [A] Codebase audit for absolute paths outside VDE_ROOT_DIR
  - Run a targeted grep/search for known absolute path prefixes like /Users/, /home/, /root/, /opt/ outside the VDE root.
  - Replace with "$VDE_ROOT_DIR/..." where safe and appropriate; defer system paths that legitimately live outside the repo (e.g., SSH host keys).
- [B] Phase H instrumentation scaffolding
  - Add a lightweight plan timing wrapper around the plan generation path (log start, end, duration).
  - Instrument plan generation entry points without changing behavior for users.
- [C] Guard hook additions
  - Ensure lib/vde-root-guard is sourced early in startup to detect leaks at runtime.
- [D] Documentation updates
  - Update MEMORY.md and session_handover_remediation.md cross-links to reflect Phase H changes.
- [E] Verification steps
  - Baseline: run full test suite with timing; confirm no hard-coded absolute paths are exercised.
  - Observability: verify timing data is captured in logs.
  - Documentation: confirm cross-links are accurate.

Deliverables
- Updated code with root-based path resolution; guard scripts; instrumentation scaffolding.
- Phase H plan companion documentation.
- Updated MEMORY with Phase H context and status.

Next Actions: implement changes, run baseline tests, and publish PR against main.
