# VDE Testing Strategy - 1.5.7 (The Sovereign Baseline)
<!-- @shared-law (Sovereign Law) -->

This document defines the absolute empirical standards for the Virtual Development Environment (VDE). All functional code MUST be verified by this suite.

## Testing Policy (binding)

This section is the single source of truth for how the project tests. Other documents link here and state no competing rule. The numbered sections below (1 to 7) describe the suites and how to run them; this policy states the obligations around them.

### Scope and authority

This policy binds every maintainer and every agent, sub-agents included. It governs every change to code, tests, the gate and the test tooling. The agent-facing obligations are in `.gemini/RULES/testing.md`, and the preamble every sub-agent prompt for code work begins with is `.gemini/RULES/testing-preamble.md`. Those files are derived summaries of this section for agents: they point here and restate no rule values, and where one of them differs from this section, this section wins.

The numbers are in `tests/test-policy.conf`, which mirrors the tooling defaults: the tooling does not read the file, and `tests/unit/testing-policy-wiring.test.zsh` fails if they drift. The table under "Policy numbers" below mirrors that file. The layer that enforces each rule is shown under "Which layer enforces which rule". A rule that is marked Planned is not yet enforced by the tooling, and the pull request that changes code must not claim otherwise.

### Standards followed

This policy uses the vocabulary of ISO/IEC/IEEE 29119 (software testing) and of the ISTQB glossary. Test sizes (small, medium, large) follow the Google style. The test pyramid guides the mix: many small tests, fewer medium tests, and few large tests. Non-determinism is handled as described in Fowler's "Eradicating Non-Determinism in Tests". Delivery health will be reported with the DORA measures that the run history supports (lead time for changes, to which the pipeline duration contributes, and change failure rate), through the history and reporting work (#779, #784); no DORA measure is computed today. Secure development follows NIST SSDF practices PW.7 (review and analyze human-readable code) and PW.8 (test executable code). The OpenSSF Scorecard Pinned-Dependencies check is the reference for the planned pinned test environment (#780); GitHub Actions are pinned by tag today, not by commit hash.

### Test sizes

| Size | Resources and limits | Where it runs | Examples today | Budget |
|------|----------------------|---------------|----------------|--------|
| Small | No containers, no network, no fixed sleeps. Must be safe to run in parallel. | The unit suites `tests/unit/*.test.zsh`, run by `tests/run-sovereign-tests.zsh` in the continuous integration job. | `tests/unit/vde-actions.test.zsh`, `tests/unit/test-runner-coverage.test.zsh` | `UNIT_SUITE_BUDGET_SECONDS` per suite |
| Medium | May start Spokes, never more than `MAX_RUNNING_SPOKES` at once (Rule K in `.gemini/instructions.md`). Runs serially. | Not in the continuous integration unit job, so not in the Sovereign suite runner's unit run. | `tests/integration/spoke-smoke-matrix.test.zsh` | No separate budget in the policy numbers |
| Large | The full lifecycle of a Spoke, end to end. Runs serially. | The pre-push full certification of the pushed tip. | The Proof of Life contract, `tests/features/core-infrastructure/proof-of-life-the-contract.feature` | Counts toward `FULL_TIER_BUDGET_SECONDS` |

Two small-tier suites are a known exception to the no-container rule: `vde-agent-sock.test.zsh` and `spine-git-env-isolation.test.zsh` each create one container. Moving them to the medium tier is Planned (#778).

### Determinism rules

- Do not use `sleep`. Wait on a condition or a timer through `zsh/zselect` (`zmodload zsh/zselect && zselect -t <hundredths>`).
- Do not assert an exact second or a sub-second timing edge. Assert with a margin.
- Output must not change under `LC_ALL`. Helpers pin their own formatting.
- Small tests use their own scratch `HOME` and scratch directories. `lib/vde-test-env` provides a scratch Projects base and a scratch directory, not a scratch `HOME`. The pre-push gate runs the suites under a scratch `HOME`, and a test that touches `HOME` must set its own scratch home, never the caller's. Medium tests use a scratch Projects base for their workspaces, with one documented read exception: they may READ the caller's SSH key directory (`VDE_SSH_DIR`, default under `HOME`), as the Spoke smoke matrix shows. Spokes started by a medium test keep their own data and log directories; this exception to the no-leftover rule is tracked separately. The large Proof of Life runs with the caller's `HOME` because the real tooling it exercises needs it; the gate records this in [github-lifecycle.md](github-lifecycle.md) section 6. These are the only deliberate exceptions, and any other test that needs the caller's `HOME` or writes outside scratch must say why in the pull request.
- Small tests use no network. Medium and large tests use only the local container runtime and what the project itself starts.
- No test depends on or changes shared mutable host state.
- A test leaves no process, container or file behind.
- Randomness, when a test needs it, uses a fixed seed.
- No test depends on the order in which other tests run.
- Measure a duration with `vde_test_now` from `lib/vde-test-env`, which reads a clock that a wall-clock step cannot move where `/proc/uptime` is readable (otherwise it falls back to the wall clock, a documented limitation). `$SECONDS` and `EPOCHREALTIME` both follow the wall clock in zsh 5.9 (measured: a one-hour step moved both by 3601 seconds), so `$SECONDS` is not a monotonic clock and a step during a run would corrupt a duration built on either. Format a number with `vde_test_fmt1` from the same file, which prints a dot in any locale.

### Flake policy

A flaky test is a test that both passes and fails on the same code.

The specified behaviour is this. A suite that fails is rerun once (`FLAKE_RERUN_ON_FAIL`). A suite that passes on the rerun is reported as FLAKY, never as a plain pass, and the flake is recorded. A suite that flakes `FLAKE_FAIL_THRESHOLD` times within the last `FLAKE_WINDOW_RUNS` runs fails the run until the flake is fixed or the test is quarantined. A quarantine entry needs a reason, an owner, an issue number and an expiry date. An expired or stale quarantine entry is an error.

Status: the rerun and the FLAKY report are Implemented (#779, step A) in `tests/run-sovereign-tests.zsh`. A suite that fails is rerun once. A pass on the rerun is reported FLAKY, never as a plain pass: the flaky suite counts as passed, is listed in the summary with its first exit code, and the run still exits 0 with a warning. A failure on the rerun is a real failure. The rerun gets its own SUITE TIMING row named `<suite>[rerun]`. In the parallel pool the rerun happens inside the worker, and a worker that died is not rerun. `VDE_FLAKE_RERUN=0` switches the rerun off for debugging, `1` switches it on, and any other non-empty value exits 2 (an empty value counts as unset). The default is `FLAKE_RERUN_ON_FAIL`, held in the runner constant `VDE_FLAKE_RERUN_DEFAULT`, which `tests/unit/testing-policy-wiring.test.zsh` pins.

Run history: Implemented (#779, step B) in `tests/run-sovereign-tests.zsh`. After each suite is reported, the runner appends one JSON line to `vde-test-history.jsonl` in the git common directory. The file is local, untracked, never pushed and append-only, with one line per write, so a killed run keeps the lines it had already written. Each line has the fields `v`, `run`, `ts` (UTC), `tree`, `dirty`, `suite`, `seconds`, `containers`, `result` (`pass`, `fail` or `flaky`) and `flaky`. The sovereign-audit and BDD-Metadata rows are recorded too, and a failed audit still records its line. A rerun's seconds fold into the suite's single line. `VDE_TEST_HISTORY_FILE` names another file, and `off` disables the record. A copy of the runner that is not the top level of its repository writes nothing by default. A history that cannot be written prints one warning and does not change the result.

Still Planned (#779, later steps): the repeat-flake threshold (`FLAKE_FAIL_THRESHOLD` of `FLAKE_WINDOW_RUNS`), the quarantine list and the history report. Until those land, a flaky test is fixed when it is found, and the pull request says so.

The Proof of Life is never rerun, never quarantined and never reported FLAKY: a Proof of Life that fails is a defect in the core, not a flake.

### Timing and budgets

Every run is timed. The runner prints a start time and a duration for each suite and a SUITE TIMING table. The pre-push gate prints the time of each step. After the Proof of Life, pass or fail, the gate also prints a PROOF OF LIFE TIMING table with every scenario's time, slowest first; this is step 1b of issue #774, and the numbers decide what steps 2 and 3 build. The per-suite and per-step timing is step 1 of issue #774 (PR #783) and is Implemented. Each run also reports how many containers each suite created, read from the container runtime's event stream for the suite's time window (the count is daemon-wide, and a window that reaches the runtime's event-history cap shows `256+`).

Budgets:

- `UNIT_SUITE_BUDGET_SECONDS` applies to each unit suite.
- `FULL_TIER_BUDGET_SECONDS` applies to the full certification of a tip.
- Budgets only go down. This is a ratchet: a budget may be lowered, never raised to hide a slow suite.
- A suite over its budget must be fixed, or the pull request must justify it.

Measured baseline, 2026-11-26, one gate run: the full tier took 1398.0 s, made up of the audit at 7.5 s, the suite at 452.7 s, the Proof of Life at 937.7 s and the documentation audit (`bin/vde-gospel-audit.zsh`) at 0.1 s. The slowest unit suite took 129.2 s. The number of containers each suite creates is measured and printed.

Unit suites run in parallel. `tests/run-sovereign-tests.zsh` runs up to `VDE_TEST_JOBS` unit suites at once, by default the lower of 4 and the number of online CPUs. Each parallel suite has its own scratch `HOME`, and its output is printed as one block, so blocks do not interleave. The runner does not start Spokes. A suite that creates a container of any kind is listed in `tests/serial-unit-suites.txt` and runs alone after the parallel pool has drained, so its container count stays per-suite. Today that is two suites, `vde-agent-sock.test.zsh` and `spine-git-env-isolation.test.zsh` (through the spine check), each of which starts a throwaway `docker run --rm` alpine container that exits at once. Measured, all 72 unit and integration suites took 145 s at 4 at a time against 456 s serially, with no failures in two runs. Values above 4 were not measured, so 4 is the tested maximum, and a larger value is clamped to 4. `VDE_TEST_JOBS=1` is the old serial behavior. A suite in the pool shows `n/a` in the containers column, because the daemon-wide count cannot be attributed to one suite while others run. The Proof of Life is never run in parallel and is never shortened or replaced.

Status of enforcement: budgets are not yet enforced by the tooling. Planned (#779).

### Coverage

Today the continuous integration coverage job runs kcov over every test that is not listed in [`tests/ci-coverage-exclusions.txt`](../../tests/ci-coverage-exclusions.txt) (the list currently names four tests) and publishes the report. It does not gate on a minimum, and the CI summary only requires that the job ran.

Policy: record the measured baseline from the published report, then ratchet it. The minimum may rise and must never fall. A pull request that lowers measured coverage must say why. The baseline value is recorded only when it has been measured; no value is invented.

Status: Planned (#782, the umbrella issue for this policy).

### Test quality and evidence

Every test must be able to fail. A new or changed test is shown failing before the change (RED) and passing after it (GREEN), with the literal output in the pull request, using the evidence section of the pull request template. The pull request evidence check (`bin/vde-check-pr-evidence.zsh`) requires the words RED and GREEN and at least one fenced block of literal output; reviewers still judge the quality of the evidence.

A rule that guards behaviour is shown to bite: a violating fixture or a mutation makes it fail. Code that carries the gate or the test tooling also carries a mutation proof (automated by #781).

Fake tests are forbidden. The rule and its examples are in `.gemini/RULES/fake_tests.md`; this policy does not restate them.

The full suite and the Proof of Life run at the push are the certification. Do not hand-run them first in place of the certification.

An independent review must pass before a commit. The review checklist is Implemented as the Testing Policy step in the reviewer skill (`.gemini/SKILLS/reviewer.md`). A reviewer applies that step; no tool checks that the review took place.

### Which layer enforces which rule

| Rule | Enforced by | Status |
|------|-------------|--------|
| Suite discovery and exclusions with a reason | `tests/run-sovereign-tests.zsh` and `tests/unit/test-runner-coverage.test.zsh` | Implemented |
| Parallel unit suites (Sovereign runner, VDE_TEST_JOBS, tests/serial-unit-suites.txt) | `tests/run-sovereign-tests.zsh` and `tests/serial-unit-suites.txt` | Implemented |
| Test-size and determinism rule checks (a unit suite that starts a container, uses the network or sleeps is detected) | Not yet in the tooling | Planned (#778) |
| Timing printed every run and per-step gate timing | `tests/run-sovereign-tests.zsh`, `githooks/gate-tree.zsh` and `lib/vde-junit-timing` (per-scenario Proof of Life timing); per-step timing (PR #783) | Implemented |
| Two-tier pre-push gate, stamps and no early release | `githooks/*`, `lib/vde-pol-stamp` and `lib/vde-gate-commits` (#770) | Implemented |
| Policy numbers match the tooling defaults | `tests/unit/testing-policy-wiring.test.zsh` | Implemented |
| Flake rerun once and FLAKY report | `tests/run-sovereign-tests.zsh`, `tests/unit/runner-flaky.test.zsh` | Implemented |
| Run history (one JSON line per suite per run) | `tests/run-sovereign-tests.zsh`, `tests/unit/runner-history.test.zsh` | Implemented |
| Flake threshold, quarantine and the history report | Not yet in the tooling | Planned (#779) |
| Timing budget enforcement | Not yet in the tooling | Planned (#779) |
| Pinned test environment | Not yet in the tooling | Planned (#780) |
| Mutation checks for the gate and the tooling | Not yet in the tooling | Planned (#781) |
| Style (4-space indentation) conformance | Not yet in the tooling | Planned (#777) |
| Coverage minimum ratchet | Not yet in the tooling | Planned (#782) |
| Reviewer checklist (Testing Policy step in the reviewer skill) | `.gemini/SKILLS/reviewer.md` | Implemented |
| Pull request evidence check (RED and GREEN output in the body) | `bin/vde-check-pr-evidence.zsh` and `.github/workflows/pr-evidence.yml` (the workflow's check is a job that runs on every pull request; making it a required check is a repository setting outside the code) | Implemented |

### Policy numbers

The values below are the same as `tests/test-policy.conf`. The wiring test `tests/unit/testing-policy-wiring.test.zsh` fails if they differ.

| Key | Value | Meaning |
|-----|-------|---------|
| `UNIT_SUITE_BUDGET_SECONDS` | `150` | Time budget for one unit suite. Budgets only go down. |
| `FULL_TIER_BUDGET_SECONDS` | `1500` | Time budget for the full certification of a tip. |
| `STAMP_TTL_SECONDS` | `1800` | How long a passed certification stamp stays valid for a push. Equals the default in `lib/vde-pol-stamp`. |
| `DOCKER_EVENTS_TIMEOUT_SECONDS` | `10` | Timeout for watching Docker events. Equals the default in `tests/run-sovereign-tests.zsh`. |
| `TEST_PARALLEL_JOBS` | `4` | The maximum number of unit suites run at once; the measured maximum, never raised without a new measurement. |
| `MAX_RUNNING_SPOKES` | `3` | Most Spokes that may run at once (Rule K). |
| `FLAKE_RERUN_ON_FAIL` | `1` | Whether a failing suite is rerun once before it is reported (1 = yes, 0 = no). `VDE_FLAKE_RERUN` overrides it for one run. |
| `FLAKE_WINDOW_RUNS` | `20` | How many recent runs are counted when judging flakes. |
| `FLAKE_FAIL_THRESHOLD` | `3` | Flakes within the window that fail the run. |

## 1. THE SUPREME GATE: @SYSTEM-SPINE
The System Spine tetrad is the foundational audit gate. If any pillar fails, the system triggers an immediate **Protocol Blockade**.

| Pillar | Technology | Verification Method |
|--------|------------|---------------------|
| I      | **Zsh**    | `zsh --version` (Voice of the Tribe) |
| II     | **Git**    | `git init` in transient workspace (The Chronicler) |
| III    | **Docker** | `docker run --rm` diagnostic probe (The World-Forge) |
| IV     | **SSH**    | `ssh-add -l` identity check (The Bridge) |

## 2. BDD PERFORMANCE METRICS (measured on the 1.5.6 baseline)
Measured on **2026-09-30** at commit `6308fe33`: full run of `behave tests/features/` on Linux with Docker 29.8.2 (6 min 17 s, the Python `jsonschema` module available to subprocesses). The suite is **not** at 100%.

| Metric | Count | Status |
|--------|-------|--------|
| **Total Features** | 28 (26 passed, 2 failed) | ❌ 2 FAILING |
| **Total Scenarios** | 116 (107 passed, 9 failed) | ❌ 9 FAILING |
| **Total Steps** | 720 (638 passed, 9 failed, 73 skipped) | ❌ 9 FAILING |
| **Undefined Steps** | 0 | ✅ NONE |
| **Scenario Pass Rate** | 92.2% (107 of 116) | ❌ BELOW 100% |

The Proof of Life (`proof-of-life-the-contract.feature`) passed 6 of 6 scenarios in this run. The CI-safe Sovereign Tests runner (`./tests/run-sovereign-tests.zsh`) passed 12 of 12 suites with `jsonschema` available and 11 of 12 without it (tracked in #492).

Failing scenarios at this commit, with the cause seen in the run log:

- `student-guidance/next-steps-guidance.feature` (8 scenarios, lines 14-78): the shared step `the Hub is synchronized to version 1.5.3` fails with `Sync error: Hub at 1.5.6, expected 1.5.3`, so none of them reaches the command under test. The version is hard-coded in the feature.
- `governance/gospel-audit.feature:20` "Detection of Undocumented Scripts": the audit printed `[GOSPEL-SUCCESS]` instead of `[CRITICAL FAILURE] Undocumented scripts detected`. `bin/vde-gospel-audit.zsh` skips its undocumented-script check when `docs/available-scripts.md` is missing, and that file does not exist in the repository.

Running the full suite against a Docker host is not side-effect free. In this measurement it removed the 4 stopped `vde-*` containers that existed beforehand (seen by comparing `docker ps -a` before and after; the responsible scenario was not identified) and re-dated tracked documents through the doc-sync scripts. Run it on a disposable host, or commit first and review `git status` afterwards.

## 3. CORE INFRASTRUCTURE SUITE
Located in `tests/features/core-infrastructure/` (22 feature files at commit `6308fe33`; the following is a non-exhaustive selection):

- **proof-of-life-the-contract.feature**: Verifies the 8 lifecycle states (create, rebuild, start, enter, stop, remove, add, uninstall).
- **system-spine.feature**: Hardens the 4 Pillars and deterministic Hub-to-Spoke ignition.
- **gateway-pillars.feature**: Verifies the Four Pillars Gateway before Proof of Life ignition.
- **jupyterlab-spoke.feature**: Certifies the Data Science stack and background service ignition.
- **tech-stack-cluster.feature**: Verifies parallel ignition of Python, PostgreSQL, and Redis as a unit.
- **usp-validation.feature**: Enforces Universal Script Parity across all registered VM setup scripts.
- **technical-integrity.feature**: Validates core technical integrity guards.
- **student-daily-usage.feature**: Verifies the student daily workflow end-to-end.
- **vde-init-empirical.feature**: Empirical verification of `vde init` lifecycle.
- **ssh-config-version.feature**: Validates SSH config versioning and synchronization.
- **sovereign-scope.feature**: Certifies VDE_ROOT_DIR relative pathing and portability.
- **location-blind-portability.feature**: Verifies location-blind execution from any working directory.
- **armor-integrity.feature**: Validates the Armor product runtime integrity.
- **armor-autonomy.feature**: Certifies AI-blind, Hub-blind student autonomy.
- **spoke-to-spoke-ssh.feature**: Verifies inter-Spoke SSH connectivity.
- **locking-recursion-fix.feature**: Validates config lock recursion prevention.
- **concurrency-queue.feature**: Verifies the 3-VM concurrent limit and queue behavior.
- **rust-path-repro.feature**: Validates Rust toolchain path resolution.
- **error-handling.feature**: Certifies error messaging and recovery paths.

## 4. EXECUTION PROTOCOLS

The commands below are for focused runs during work; these sections defer to the Testing Policy (binding), under which full-suite certification belongs to the pre-push gate.

### Full BDD Strike
```zsh
# Execute the complete behavior suite
behave
```

### Full System Test (Unit + Integration + BDD)
```zsh
# Standard Make target
make test
```

### Targeted Spine Check
```zsh
# Verify the 4 non-negotiable pillars
behave --tags @system-spine
```

## 5. HARDENED MANDATES

These mandates defer to the Testing Policy (binding) and to the fake-test rule in `.gemini/RULES/fake_tests.md` where they differ.

- **Zero Placeholder Policy**: No "pink" steps permitted. Every assertion MUST verify physical file existence, container state, or network response.
- **Auto-Cleanup**: The `after_scenario` hook in `environment.py` ensures 100% removal of test containers (labeled `vde.test=true`).
- **USP Compliance**: Every hydration script in `scripts/setup/` must pass the `usp-validation` suite before it is considered production Beskar.

## 6. ROUTER UNIT TESTS

`bin/vde` and `lib/vde-actions` are covered by Docker-free unit tests (run one with `zsh tests/unit/<name>.test.zsh`):

| File | Covers |
|------|--------|
| `vde-actions.test.zsh` | The eight action handlers in a sandbox with a stub `docker`: usage errors, unknown aliases, absent/present containers, failing docker operations, exit statuses, `function-trace` transparency. |
| `vde-router-exit-status.test.zsh` | Unknown command and bare `vde` exit 2; `vde help` exits 0. |
| `vde-router-delegate-args.test.zsh` | Typed arguments reach `audit`, `check-tetrad`/`spine-check`, `heal` and `dns-check`. |

How to verify a router change (characterization against a stub `docker`, trace comparison, mutation checks):
[router-handlers](router-handlers.md#8-verifying-a-change-to-the-router).

## 7. HOW CI FINDS THE UNIT TESTS

CI's "Sovereign Tests" job runs `tests/run-sovereign-tests.zsh`, which DISCOVERS every `tests/unit/*.test.zsh` and runs it: a new suite needs no edit to the runner. The only exclusions are the suites named in `tests/ci-unit-exclusions.txt`, one `<suite> <reason>` per line. A reason is mandatory and an entry naming a suite that does not exist is an error, so the list cannot rot silently; prefer a suite that skips loudly inside itself over an entry there.

- `zsh tests/run-sovereign-tests.zsh --list` prints the plan (`run  <suite>` / `skip <suite> :: <reason>`) and exits before the audit and before running anything.
- `tests/unit/test-runner-coverage.test.zsh` is the drift guard: every suite on disk is either run or excluded with a reason. The runner refuses to start on an exclusion with no reason (an inline `#` comment is not a reason), one that does not name a `*.test.zsh` suite, one for a suite that does not exist, or a suite listed twice.
- A suite passes or fails by its exit status alone.

---
**Status:** SYSTEM CERTIFIED (1.5.7)
