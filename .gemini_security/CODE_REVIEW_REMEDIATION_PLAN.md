# Code Review Remediation Plan

## Findings
1. **CRITICAL - UAP Violation (Shebang):** `scripts/setup/elixir-init.zsh` uses `#!/bin/bash`. All shell scripts MUST use `#!/usr/bin/env zsh`.
2. **HIGH - UAP Violation (Bash Usage):** `scripts/setup/csharp-init.zsh` and `scripts/setup/js-init.zsh` call `bash` directly. These should use `zsh` or native shell commands.
3. **HIGH - The Scavenger's Ban (JQ):** `bin/vde-ps` and `lib/vde-cluster-utils` directly call `jq`, which is forbidden. They must use the `vde_query_json` wrapper or pure ZSH parsing.
4. **MEDIUM - Dangerous `eval` usage:** `bin/vde-rebuild` and `bin/vde-ps` use `eval` to execute commands constructed from strings. This is a known anti-pattern and a potential security risk. They should be refactored to use arrays.

## Remediation Steps
- [ ] Fix shebang in `scripts/setup/elixir-init.zsh`.
- [ ] Replace `bash` with `zsh` in `csharp-init.zsh` and `js-init.zsh`.
- [ ] Refactor `vde-ps` to remove direct `jq` calls and `eval`.
- [ ] Refactor `vde-cluster-utils` to remove direct `jq` calls.
- [ ] Refactor `vde-rebuild` to use arrays instead of `eval`.