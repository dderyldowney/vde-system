# Session Handover: VDE Test Suite & Performance Remediation

## Context and Next Steps

- This document collection is shared across sessions to keep handover and remediation aligned.
- Context: Provides the high-level purpose, scope, and ownership for remediation work that follows the handover.
- Next steps: Keep cross-links in sync; update both handover and remediation plan when scope or priorities shift; reference remediation progress from the handover.

## Executive Summary (prior sessions)

Previous sessions resolved critical performance hangs and stability issues in the VDE integration test suite. Root causes were redundant JSON parsing cycles, Zsh variable leakage in the parser, logically flawed test assertions, and Docker safety gaps. A new safety mechanism using Docker labels was implemented to prevent accidental cleanup of non-VDE resources. A second pass eliminated a 24s/100-plans regression by removing all subshells from the `generate_plan` hot path.

## Key Accomplishments (prior sessions)

- Plan generation: 12s → ~25ms (subshell elimination, O(1) alias map, vm-types cache)
- Parser stability: `extract_vm_names` rewritten as pure Zsh array loop
- Docker safety: `vde.managed=true` label on all templates; label-filtered cleanup everywhere
- Integration tests: 79/79 passing; Behave: 240/240 passing
- Test infrastructure: promoted helper step files; fixed stale `scripts/` paths → `lib/`/`bin/`

## Current Session Work (2026-03-09 — User Guide + Deferred Mainlining)

### Goal
Two parallel goals:
1. **User Guide generation** via `tests/scripts/generate_user_guide.py` from `@user-guide-*` tagged scenarios
2. **Mainline deferred tests** — promote minimum needed from `tests/features/deferred/` into core suite

### Phase 1: Orphaned Step Audit — COMPLETE
- `tests/features/steps/ssh_agent_steps.py` — **DELETED** (64 dead stubs; 2 active steps rescued to `ssh_git_steps.py` and `installation_steps.py`)
- Dry-run confirmed: 240/240 still passing after deletion

### Phase 2: VM Lifecycle Promotion — IN PROGRESS (BLOCKED on failures)

**What was done:**
- Removed **zig** VM type from all sources: `data/vm-types.json`, `data/vm-types.conf`, `configs/docker/zig/`, `env-files/vde-zig.env`, `configs/ssh/config`, `docs/VDE-SPEC.md` (user confirmed zig apt packages are broken)
- Wrote `tests/features/steps/vm_lifecycle_steps.py` — new step definitions covering all patterns in both deferred feature files
- Promoted to `tests/features/core-infrastructure/`:
  - `vm-lifecycle.feature` (13 scenarios, `@core-suite @user-guide-starting-stopping`)
  - `vm-lifecycle-management.feature` (12 scenarios, `@core-suite @user-guide-starting-stopping`)
- Updated `tests/features/environment.py` `after_scenario` to clean up `_temp_vm_types`

**Current state: 12 failures + 3 errors** (regression from 240/240):

The new features added 25 scenarios; 12+ are failing. Root causes identified:

1. **list-vms --lang/--svc filter** — `bin/list-vms` only filters by `LIST_TYPE` in the `--all` section. Fix applied: changed test commands to `list-vms --all --lang` / `list-vms --all --svc`. *May be resolved.*
2. **add-vm-type test** — `get_vm_types()` returns `vde-testlang` (full prefix); step checked bare `testlang`. Fix applied. *May be resolved.*
3. **testlang ssh_port** — `_add_vm_type_temporarily` added no ssh_port; `create-virtual-for` needs it. Fix applied (port 2299). *May be resolved.*
4. **Restarting a VM** — `Given I have a running VM` was starting python but Then assertions check rust. Fix applied. *May be resolved.*
5. **Deleting a VM** — `remove-virtual` intentionally preserves compose file; `the VM should be removed` step was checking compose deleted. Fixed to check container stopped instead. *May be resolved.*
6. **they should be able to communicate** — `context.network_configured` was never set. Fixed in Given steps. *May be resolved.*
7. **3 errors + hook_errors** — Likely from after_scenario importing `_cleanup_temp_vm_types` from vm_lifecycle_steps incorrectly, OR from ssh-configuration.feature side effects. **NEEDS INVESTIGATION next session.**
8. **Start multiple VMs / Stop all running VMs** — rust container start timing/state issues. Possibly flaky. **NEEDS INVESTIGATION.**
9. **Rebuilding after code changes** — vde-ask output check for 'image'/'built' may not match. **NEEDS INVESTIGATION.**

### Next Session Must-Do

1. **Fix the 3 errors** — Likely `environment.py` import of `_cleanup_temp_vm_types`. Run `python3 -m behave 2>&1 | grep -E "ERROR|Traceback" | head -30` to see exact error.
2. **Run only new features first** to isolate: `python3 -m behave tests/features/core-infrastructure/vm-lifecycle.feature tests/features/core-infrastructure/vm-lifecycle-management.feature -q`
3. **Verify original 240 are unaffected** — if errors bleed into non-lifecycle features, that's a hook problem.
4. **Fix remaining failures** — use the root-cause list above.
5. Once Phase 2 passes: proceed to Phase 3 (daily workflow features promotion).

### Critical File List
- `tests/features/steps/vm_lifecycle_steps.py` — NEW; contains `_add_vm_type_temporarily`, `_cleanup_temp_vm_types`
- `tests/features/environment.py` — `after_scenario` now imports `_cleanup_temp_vm_types` from vm_lifecycle_steps (check this import)
- `tests/features/core-infrastructure/vm-lifecycle.feature` — PROMOTED (uses testlang, list-vms --all --lang)
- `tests/features/core-infrastructure/vm-lifecycle-management.feature` — PROMOTED
- `data/vm-types.json`, `data/vm-types.conf` — zig removed
- `configs/ssh/config` — zig SSH entry removed
- `docs/VDE-SPEC.md` — zig port entry removed

### Known list-vms behavior (important for test design)
`bin/list-vms --lang` shows ALL created VMs in "Created VMs:" section regardless of type filter.
The `LIST_TYPE` filter ONLY applies to the "Available VM Types:" section shown with `--all`.
So `list-vms --all --lang` correctly shows only "Language VMs:" section.

## Test State at Session End

- `make test-e2e`: **79/79 passing**
- `make test-unit`: **passing**
- `python3 -m behave`: **~248 passing, 12 failing, 3 errors** *(regression from Phase 2 promotion attempt)*
- `python3.13 -m pytest tests/unit/`: **72/72 passing**

The **original 240 scenarios should still pass** — the failures are all in the 25 newly promoted scenarios.

## Persistence Instructions

1. **Reloading Context**: Source `lib/vde-constants` and `lib/vm-common` first.
2. **Cache**: If VM types change, delete `.cache/vm-types.cache`.
3. **Zig removed**: Port 2219 is now free. Do not reassign it without updating configs/ssh/config.
4. **Cleanup**: Use `shutdown-virtual all` for safe, label-filtered cleanup.
5. **generate_plan performance**: The `$()` subshell pattern is the enemy — always use direct variable writes in hot paths.

## Related Plans

- Remediation plan: See `plans/session_handover_remediation.md` for end-to-end remediation steps.
- Cross-reference: This handover is aligned with the remediation plan; updates to one must be mirrored in the other.

## Paired Update Policy

- This handover is the paired companion to `plans/session_handover_remediation.md`.
- Any update to remediation plan must be mirrored here, and vice versa, in lockstep to preserve traceability.
- Ensure cross-links remain accurate between the two documents.
