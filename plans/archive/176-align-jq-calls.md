# Implementation Plan: Align jq Calls with vde_query_json Wrapper (Issue 176)

## Objective
Migrate direct `jq` calls in `lib/vde-metrics` to the `vde_query_json` safety wrapper to ensure full compliance with Rule G (The Scavenger's Ban) and provide a robust fallback to Docker-based parsing if the host lacks the `jq` binary.

## Key Files & Context
- **Affected Files:**
  - `lib/vde-metrics`
- **Context:** `lib/vde-metrics` currently performs manual capability checks (`if command -v jq`) and invokes `jq` directly, bypassing the centralized, fail-safe `vde_query_json` logic in `lib/vde-core`.

## Implementation Steps
1. **Analyze Direct jq Usage:** Review all direct `jq` occurrences in `lib/vde-metrics`.
2. **Refactor to vde_query_json:** 
   - Replace explicit `if command -v jq >/dev/null 2>&1; then` checks and `command jq` executions with direct calls to `vde_query_json`.
   - The `vde_query_json` function inherently handles the existence check and Docker fallback.
3. **Handle Edge Cases:** 
   - If there are scenarios where a simple text-append fallback was used in the absence of `jq`, assess whether the guaranteed execution via `vde_query_json` (which falls back to Docker) renders the text-append fallback obsolete. Given the mandate for Zero-Host Dependency, `vde_query_json` should be the universal solution.

## Verification & Testing
1. **Audit Compliance:** Run `bin/vde-enforce-uap.zsh` to verify continued compliance with core mandates.
2. **Validation Sweep:** Execute `grep` to ensure no direct `jq` calls remain in `lib/vde-metrics`.
3. **Execution Test:** Run a metrics-dependent command (e.g., `bin/vde stats` or `bin/vde health`) to confirm the `vde_query_json` wrapper functions correctly in the metrics context.