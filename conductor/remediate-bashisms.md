# Remediation Plan: The Great Purification (Bashism Purge Stage 2)
<!-- @shared-law (Forge Component) -->

## Background & Motivation
The Forge currently contains scattered "Bashisms"—syntax and operators exclusive to Bash that fracture the Zsh parser (Mandate C). While standard POSIX utilities (`tr`, `sed`, `awk`, `grep`) are acceptable and considered part of the host environment, Bash-specific constructs like the `=~` regex operator, `export -f`, and `0`-indexed array assumptions cause silent failures (`RC 2`) in restricted or automated Zsh environments.

## Objective
Comb through the codebase extensively to remove actual Bash-specific syntax and rewrite them using Zsh-native equivalents, ensuring 100% compliance with Mandate C (ZSH ONLY).

## Implementation Steps

### 1. The Regex Operator Purge (`=~`)
- **Target**: All `bin/`, `lib/`, and `scripts/` files.
- **Action**: Replace the Bash `=~` regex operator with Zsh-native glob matching (`[[ $var == pattern ]]`) or standard `#`/`%` string stripping.

### 2. Array Indexing Alignment (`[0]`)
- **Target**: Codebase-wide.
- **Action**: Scan for and eradicate any `0`-indexed array assumptions, replacing them with the Zsh `1`-indexed standard (`$array[1]`).

### 3. Function Export Purge (`export -f`)
- **Target**: `lib/` directory.
- **Action**: Ensure no bash-style function exports exist (`export -f function_name`), replacing them with standard library sourcing, which is the Zsh way.

### 4. Bash-Specific Parameter Expansion Check
- **Target**: Codebase-wide.
- **Action**: Search for Bash-only case modifications (e.g., `${var,,}` or `${var^^}`) and replace them with Zsh `${(L)var}` and `${(U)var}` if found.

### 5. Codebase-Wide Swarm Execution
- Dispatch a `generalist` sub-agent to systematically replace these specific Bash patterns directory by directory.

## Verification & Testing
- Execute `python3 -m behave tests/features/core-infrastructure/system-spine.feature`.
- Execute `python3 -m behave tests/features/clusters/tech-stack-cluster.feature`.
- Confirm 100% Green status with absolute Zsh-native purity.
