# Remediation Plan: Session Handover Issues (VDE Test Suite & Performance)

## Related Handovers

- Session Handover: see ../session_handover.md

Overview

- Address the 5 problem areas captured in session_handover.md: performance hangs, subshell hot-paths, parser variable leakage, Docker safety/isolation, and integration test expectations.
- Deliverables: robust plan execution, validated test results, hardened Docker cleanup, and clear documentation updates.

Phased Plan (high level)

- Phase A: Baseline verification and scoping — **COMPLETE**
- Phase B: Hot-path optimizations and parser hygiene — **COMPLETE**
- Phase C: Docker safety, labeling, and isolation hardening — **COMPLETE**
- Phase D: Test suite alignment (integration and Behave) — **COMPLETE**
- Phase E: Validation, observability, and documentation — **COMPLETE**

Detailed steps, owners, inputs, and success criteria

Phase A — Baseline Verification and Scoping

- Tasks:
  - Run make test-e2e and record timings, successes, and any stalls.
  - Run Behave (python3 -m behave) and catalog all failing scenarios (22 currently).
  - Map each failure to root cause category (environment vs. code vs. test data).
- Inputs: session_handover.md findings; current repo state.
- Deliverables: Baseline report with list of failing Behave scenarios and estimated impact.
- Owner: Platform/QA Lead; Collaboration: VM-Infra, Parser, and Test Engineers
- Success Criteria: Clear, prioritized defect list for Phase B.

Phase B — Hot-Path Optimizations and Parser Hygiene
Goals

- Remove all subshells from generate_plan hot path; fix JSON parsing bottlenecks; eliminate Zsh variable leakage.

Tasks

1) Subshell Elimination Audit

- Inspect generate_plan hot path for any remaining subshell invocations.
- Implement direct variable passing and inlined logic (case statements) where possible.
- Ensure _extract_vm_names_direct wiring persists VM_ALIAS_MAP across calls.
- Update tests to cover hot-path behavior with a representative input set.

1) VM Type Loading and Caching

- Verify load_vm_types refactor to a single jq batch; validate O(1) lookup using vde-parser.
- Confirm creation and correctness of .cache/vm-types.cache and cache invalidation strategy.

1) Parser Stability

- Replace any remaining subshell-based local variable usage with pure Zsh array handling.
- Ensure extract_vm_names outputs are clean (no leaked locals into stdout).

1) Instrumentation (Light)

- Add minimal timing logs around plan generation to document improvements.

Inputs: Code references from session_handover (vm-common, vde-parser, generate_plan), existing caches.

Deliverables

- Updated code paths with zero subshells in hot path; tests covering changes; performance metrics showing improvements.
- Success Criteria: 97x improvement example replicated; no parser leaks; tests pass.

Phase C — Docker Safety, Labeling, and Isolation Hardening
Goals

- Prevent accidental cleanup of non-VDE resources; ensure all VM templates carry a VDE management label; tighten cleanup scripts to respect labels.

Tasks

1) Label Enforcement

- Add vde.managed=true label to all Docker VM templates; verify in templates/compose files.
- Propagate label to any new VM types added after this remediation.

1) Cleanup Filtering

- Update shutdown-virtual, list-vms, and teardown_test_env to filter by vde.managed label only.
- Add a CI check that docker ps/diff uses label filters and logs any deviations.

1) Safety Validation

- Run a dry-run cleanup scenario to ensure no non-VDE containers are touched.
- Document any exceptions and how they are handled.

1) Documentation

- Update maintenance notes to require label presence for new templates.

Phase D — Test Suite Alignment and Stabilization
Goals

- Align integration tests with actual parser capabilities; stabilize Behave suite; reduce environmental fragility.

Tasks

1) Integration Test Remediation

- Update test_integration_comprehensive.zsh to execute as two sequential vde ask calls for compound strings, reflecting parser behavior.
- Add explicit assertions that verify sequential intent handling rather than string-splitting.

1) Behave Stability Improvements

- Instrument tests to better surface environment issues (docker readiness, daemon state).
- Create environment checks at test startup to validate prerequisites (Docker, VM templates, cached VM types).

1) Environment Repro Edges

- Document known Docker lifecycle dependencies; suggest running in a controlled Docker-in-Docker or dedicated host as needed.

1) Regression Guardrails

- Add targeted tests for critical paths identified in Phase B (plan generation, VM type loading).

Inputs: Known failing Behave scenarios; session persistence guidance.

Deliverables

- Updated tests reflecting actual architecture; reduced false failures due to environment.
- Success Criteria: 22 failing Behave scenarios reduced to aligned failures (or passing once environment issues resolved); integration tests pass with new approach.

Phase E — Validation, Observability, and Documentation
Goals

- Validate end-to-end health; add lightweight observability; finalize handover documentation.

Tasks

1) Validation Run

- Re-run make test-e2e and Behave; ensure the majority of issues are resolved.
- Collect timing data to confirm performance improvements.

1) Observability

- Add optional timing telemetry for plan generation (start, end, duration) and cache hits/misses.

1) Documentation and Handover Updates

- Update session_handover.md with remediation actions, current baselines, and new best practices.
- Create a concise post-mortem style note capturing root causes and mitigation success.

1) Debrief Readiness

- Prepare a summary for stakeholders including risks and next steps.

Inputs: Phase A–D outputs; updated tests and code changes.

Deliverables

- Final validation results; instrumentation data; updated docs.

Timeline and milestones

- Phase A: 1–2 weeks
- Phase B: 2–3 weeks
- Phase C: 1–2 weeks
- Phase D: 1–2 weeks
- Phase E: 1 week
- Total: ~6–9 weeks

Risks and mitigations

- Environmental flakiness; mitigation: isolate Docker tests; environment guards.
- Cache invalidation complexity; mitigation: explicit invalidation triggers.
- Potential regression; mitigation: regression tests.

Next actions

- Proceed with Phase A execution plan and assign owners; report baseline results to kick off Phase B.

Artifacts to produce

- Baseline report (Phase A)
- Phase B changes and results
- Phase C safety results
- Phase D test alignment
- Phase E final validation and updated docs

End state

- Critical issues resolved or mitigated; test suites healthier; Docker safety enforced; documentation synchronized.

End.

## Paired Update Policy

- This remediation plan is the paired companion to `../session_handover.md`.
- Updates must be synchronized with the handover document; maintain cross-links and same scope.
