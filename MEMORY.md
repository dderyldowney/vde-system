# VDE Project Memory

## Testing Guidelines (MANDATORY)

**NEVER run full test suite during debugging.** Only run when explicitly needed.

### Efficient Testing
- Isolate: Run specific feature/unit test, not everything
- Verify minimally: `zsh tests/unit/vde-X.test.zsh` or `behave tests/features/core-infrastructure/X.feature`
- Full suite: ONLY after all fixes complete + user requests it

### Examples
| Context | Command |
|---------|---------|
| Fix zsh assoc array | `zsh tests/unit/vde-shell-compat.test.zsh` |
| Fix cache test | `behave tests/features/core-infrastructure/cache-system.feature` |
| Verify all | `./tests/run-full-test-suite.zsh` |

---

## Current State (2026-03-15)

**Status: ✅ SSH Isolation & Standardization COMPLETE**

**Shell/Zsh Tests: 360 passing** | **Unit tests (isolated): 31/31 pass** | **BDD Scenarios: 33/33 pass**

### Test Results (Refresh Verified)
- ✅ `tests/unit/vde-ssh.test.zsh`: 8/8 passing
- ✅ `tests/unit/test_ssh_functions.test.zsh`: 13/13 passing
- ✅ `core-infrastructure/ssh-configuration.feature`: 33/33 scenarios passing (including locking and key generation)
- ✅ Standardized variable expansion `${VAR}` verified via `zsh -n` on all scripts.

### This Session's Fixes (2026-03-15)

1. **Total SSH Isolation**:
    - Isolated VDE agent to `~/.ssh/vde/agent_env`.
    - Disabled agent auto-discovery in `lib/vde-ssh` to prevent host leakage.
    - Forced VDE commands to exclusively use the isolated persistent agent.
2. **Variable Standardization**:
    - Converted all bare variables (e.g., `$VAR`) to braced format (`${VAR}`) across 100+ shell scripts.
    - Fixed pre-existing syntax errors in E2E tests discovered during migration.
3. **Agent Governance**:
    - Resolved "Generalist Not Allowed" issue by establishing "No Circular Delegation" mandate in `AGENTS.md`.
    - Created specialized sub-agent definitions in `agents/` directory.
4. **Mandate Enforcement**:
    - Created root-level `GEMINI.md` to point to `AGENTS.md`.
    - Updated global `~/.gemini/GEMINI.md` to reference project mandates.

---

## Historical State (2026-03-11)

**Shell/Zsh Tests: 360 passing** | **Unit tests (isolated): 18/18 pass**

### Test Results (Minimally Verified)
- ✅ installation-setup: 18/18
- ✅ cache-system: 9/9
- ✅ critical-infrastructure: 51/51
- ✅ error-path: 7/7
- ✅ SSH port uniqueness (fixed duplicates)
- ✅ vde-shell-compat: 18/18

### Previous Session's Fixes

1. **_assoc_unset** - Fixed zsh associative array (was using typeset -n incorrectly)
2. **docker-free path** - Updated to core-infrastructure
3. **SSH agent cleanup** - Added trap to full test suite
4. **SSH port duplicate** - testlang2: 2299→2300
5. **Duplicate entry** - Removed duplicate vde-testlang in vm-types.json
6. **Testing guidelines** - Added to AGENTS.md and MEMORY.md

### Remaining Issues (Pre-existing)

- Deferred/promoted features have incomplete step definitions
- Docker-start tests timeout (expected - slow containers)

**Review Session: No uncommitted changes detected**

Shell/Zsh Tests: **360 passing, 0 failed** (`make test`)
Python Tests: **72 passing, 0 failed** (`python3 -m pytest`)
Total: **432 tests passing**

Behave suite: **265 passing, 2 failed, 56 errors**

- Core tests: 265 passing (was 263 before promotion)
- 56 errors from newly promoted features (undefined step definitions - deferred step files not loaded)
- **106 verified passing scenarios in User Guide** (was 64)

## Phase H: Daily Workflow Promotion (2026-03-10) — COMPLETE

## Phase H: Root Normalization (2026-03-11) — COMPLETE

- Objective: Fully enforce VDE_ROOT_DIR as the sole source of truth for filesystem paths; ensure all code paths are relative to VDE_ROOT_DIR.
- Status: ✅ Complete

**Accomplishments:**
- Created lib/vde-root (auto-discovery) and lib/vde-root-guard (detect hardcoded paths)
- Wired both into bin/vde at startup
- Fixed vde-root-guard false positive on /usr paths
- Protected env-files and configs/docker from test deletion
- Restored missing vde-js.env
- Verified all 27 VM configs and env files exist

**Running VMs:** js, postgres, redis, rust

**2026-03-11 Updates:**
- Created lib/vde-root (auto-discovery) and lib/vde-root-guard (detect hardcoded paths)
- Wired both into bin/vde at startup
- Fixed zsh associative array compatibility in lib/vde-shell-compat
- **CRITICAL FIX**: Tests were deleting core project files (env-files/*.env, configs/docker/*.yml)
- Protected env-files and configs/docker from deletion in tests
- Tests now only delete VMs with "test" in name
- vde-postgres.env restored and verified

**User Guide now includes these core workflows for new students:**

1. Create VM for specific language/service
2. Start the VM
3. SSH into the VM
4. Stop the VM
5. Rebuild the VM (not destroy)
6. Run multiple VMs together (e.g., python + go + redis + postgres for school projects)

## Phase G COMPLETE (2026-03-09)

Behave suite: **263 scenarios passing, 2 failed** (pre-existing failures)
Behave test run: `python3 -m behave` | Tag selection: `tags = core-suite and not wip`

- Lifecycle tests: **25/25 passing** ✅
- 2 pre-existing failures unrelated to recent changes:
  - `cache-system.feature:49` - .cache/port-registry directory missing
  - `vm-lifecycle-management.feature:79` - Rebuild scenario issue
Zsh integration suite: `make test-e2e` → 79/79 passing
pytest: `python3.13 -m pytest tests/unit/` → 72/72 passing
`@requires-docker-host` scenarios: **all passing** — Docker is always available on host

### Phase 1 COMPLETE (2026-03-09)

- `ssh_agent_steps.py` deleted (553 lines, 64 dead stubs)
- 2 active steps rescued: `I have SSH keys on my host` → ssh_git_steps.py; `I create my first VM` → installation_steps.py
- Key finding: `behave --dry-run --format steps.usage` shows ALL step defs, NOT filtered to 0-usage
- All 555 "orphaned" steps are actually referenced somewhere (ssh-configuration.feature promotion activated ~100+ ssh_config_steps patterns)
- Commit: `5ad0327`

### Phase 2 NEXT: Mainline VM Lifecycle

Promote from deferred/ to core-infrastructure/:

- `vm-lifecycle.feature` (18 scenarios, @user-guide-starting-stopping) — remove @wip, add @core-suite
- `vm-lifecycle-management.feature` (13 scenarios) — same
Target: 240 → 271 passing scenarios

### Phase 3: Daily Workflow — PENDING APPROVAL (2026-03-09)

Promote: documented-development-workflows.feature (31), daily-workflow.feature (13), daily-development-workflow.feature (7), vm-information-and-discovery.feature (7)

**Plan created:** `plans/phase3-daily-workflow-promotion.md`

- 58 total scenarios to promote
- All step definitions exist (verified via dry-run)
- No @wip tags in target files
- Estimated duration: ~25 minutes

### Phase 4: TODO

Promote: collaboration-workflow.feature, debugging-troubleshooting.feature, multi-project-workflow.feature, productivity-features.feature, team-collaboration-and-maintenance.feature

### Phase 5: TODO

Promote: remaining deferred features

### Phase 6: TODO

User Guide generation from @user-guide-* tagged scenarios

### Phase 7: TODO

Final verification and cleanup
Target: 271 → 329 passing scenarios

Phase F — Test Infrastructure Hardening

Goals: Eliminate stale paths, add missing Makefile targets, promote step helpers, fix env file deletion, bring Python unit tests to full coverage with real implementations.

Tasks completed:

1. Promoted docker_helpers.py, shell_helpers.py, test_utilities.py from deferred/ to main steps directory
2. Rewrote test_docker_helpers.py, test_shell_helpers.py, test_test_utilities.py — no mocks, real container lifecycle
3. Fixed all stale `bin/` path references → `lib/`, `bin/`, `data/` in test files
4. Fixed _merge_restore_dir guard: never deletes vde-*.env canonical project files
5. Fixed .gitignore: added `!env-files/vde-*.env` negation; 28 env files now properly tracked
6. Added test-compatibility Makefile target; fixed test-parser/test-commands stale .sh→.zsh extensions
7. Fixed critical_steps.py Python 3.9 compat: `int | None` → `Optional[int]`
8. Fixed parser alias map rebuild on invalidate (lib/vm-common early-return path)
9. Removed pytest --ignore for test_test_utilities.py; total pytest count: 48→72

Results:

- All suites passing: Behave 240/240, pytest 72/72, make test-unit, test-e2e, test-security, test-benchmark, test-comprehensive, test-compatibility

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
