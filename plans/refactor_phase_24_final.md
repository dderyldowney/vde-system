# Refactor Phase 24 Final - Setup Scripts Hardening

Refactor all target setup scripts in `scripts/setup/` to follow the mandatory VDE 2.0.6 USP pattern.

## Targets
- Languages/Tools: `asm`, `c`, `cpp`, `csharp`, `displaytest`, `elixir`, `flutter`, `go`, `haskell`, `java`, `js`, `kotlin`, `lua`, `php`, `python`, `ruby`, `rust`, `scala`, `swift`
- Services: `postgres`
- Test Configs: `testcfg*`, `testport*`

## Mandatory Pattern
1. `set -e` immediately after shebang.
2. `export DEBIAN_FRONTEND=noninteractive` before `apt-get`.
3. Standardized Headers (# 1. THE PACKAGE ALLOY, # 2. THE FORGE WORK, # 3. PURGING THE GHOSTS).
4. Persistence Anchor:
   - For `postgres`, use `postgresql` service name.
   - For others, skip.

## Approach
Use an automated ZSH script `plans/scripts/refactor_phase_24_final.zsh` to transform the scripts while preserving custom logic (e.g., `sdkman`, `asdf`, `rustup`).

## Tasks
- [ ] Research: Extract package lists and custom logic from each target script.
- [ ] Scripting: Create the automated refactor script.
- [ ] Execution: Run the refactor script.
- [ ] Verification: Run `bin/vde-enforce-uap.zsh` and inspect key files.
- [ ] Cleanup: Remove the refactor script.
