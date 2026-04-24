# Phase 31 Code Review Remediation Plan

## Objective
Remediate the findings from the Code Reviewer to ensure absolute technical integrity, consistency across the orchestrator, and adherence to the Mandalorian Rule Spine. Upon completion, commit the fixes and execute the final merge push to origin.

## Implementation Steps

### 1. Unify Cluster Resolution (`bin/vde`)
- **Fracture**: `start`, `stop`, `restart`, and `remove` delegate to `vde-cluster`, while `create` and `rebuild` perform inline expansion.
- **Fix**: Refactor `start`, `stop`, `restart`, and `remove` to match `create` and `rebuild`. All commands will use inline Zsh-native expansion (`vde_query_json`) for named clusters and the `default` keyword, ensuring centralized, deterministic target resolution.

### 2. Execute BDD Verification
- Re-run `python3 -m behave tests/features/` to certify that the removal of `vde-cluster` delegation does not break the `tech-stack-cluster.feature` and that the overall heartbeat remains 100% Green.

### 3. The Chronicler's Ritual (Commit)
- Stage `bin/vde`.
- Commit the changes with the message: `fix(core): unify cluster expansion logic across all orchestrator commands`.

### 4. The Final Ascent (Merge & Push)
- Execute `python3 -m behave tests/features/core-infrastructure/proof-of-life-the-contract.feature` to certify the Heartbeat.
- IF AND ONLY IF Proof of Life is 100% Green, execute the merge to `develop` and push to `origin develop`.

## Verification & Testing
- The BDD suite must pass 100% Green (47/47 scenarios).
- `vde start default` must successfully ignite both `jupyterlab` and `postgres`.