# Implementation Plan: Fix Hardcoded Paths in Setup Scripts (Issue 174)
<!-- @shared-law (Forge Component) -->

## Objective
Remove all hardcoded `/home/devuser` paths from the `scripts/setup/` hydration scripts to comply with the mandate for relative pathing and portability. Replace them with robust Zsh `~devuser` variable assignments.

## Key Files & Context
- **Affected Files:**
  - `scripts/setup/couchdb-init.zsh`
  - `scripts/setup/csharp-init.zsh`
  - `scripts/setup/elixir-init.zsh`
  - `scripts/setup/flutter-init.zsh`
  - `scripts/setup/jupyterlab-init.zsh`
  - `scripts/setup/kotlin-init.zsh`
  - `scripts/setup/lamp-init.zsh`
  - `scripts/setup/mean-init.zsh`
  - `scripts/setup/mongodb-init.zsh`
  - `scripts/setup/mysql-init.zsh`
  - `scripts/setup/nginx-init.zsh`
  - `scripts/setup/postgres-init.zsh`
  - `scripts/setup/rabbitmq-init.zsh`
  - `scripts/setup/redis-init.zsh`
- **Context:** The scripts currently use `local _zshenv="/home/devuser/.zshenv"` or similar constructs. These violate the portability requirement.

## Implementation Steps
1. **Define Local Home Variable:** For each affected script, introduce a `local dev_home=~devuser` variable assignment near the beginning of the "PERSISTENCE ANCHORS" section (or wherever the hardcoded paths begin). Ensure the tilde expansion works correctly by avoiding quotes around `~devuser`.
2. **Replace Hardcoded Paths:** Update all instances of `/home/devuser` within the script to use the `${dev_home}` variable. For example, `local _zshenv="${dev_home}/.zshenv"`.
3. **Verify Expansion Context:** Double-check that tilde expansion is not hindered by quotes in the initial `dev_home` assignment.
4. **Agent Swarm Dispatch:** Due to the number of files (>1), a swarm of `generalist` sub-agents will be dispatched to apply these changes concurrently, honoring the Rule Spine's multi-file edit restriction.

## Verification & Testing
1. **Audit Compliance:** Run `bin/vde-enforce-uap.zsh` to ensure all core mandates remain satisfied.
2. **Grep Validation:** Perform a final `grep -r "/home/devuser" scripts/setup/*.zsh` to confirm no stragglers remain.
3. **Proof of Life Certification:** Execute the absolute lifecycle test (`python3 -m behave tests/features/core-infrastructure/proof-of-life-the-contract.feature`) to verify that the Spoke hydration process is unharmed by the pathing changes.