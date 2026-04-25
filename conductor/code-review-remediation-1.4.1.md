# Code Review Remediation Plan: VDE Forge (CR-1.4.1)
# @forge (Sovereign Remediation Blueprint)

## Background & Motivation
A comprehensive architectural and technical code review was conducted on the `develop` branch of the VDE Forge. While the core is strong, the Sentinel unmasked several lingering fractures related to **Mandate C (ZSH ONLY)** and **Mandate 24 (Mandatory Labeling Rule)**. These impurities include top-level `local` declarations in specific libraries/hooks, residual `=~` regex usage, and missing architectural tags in configuration and initialization files.

## Objective
Systematically purge all remaining technical and architectural fractures identified in the code review to achieve 100% compliance across the entire repository. This will be an absolute, zero-tolerance strike.

## Implementation Steps

### Strike I: Global Shell Purification (Mandate C)
1. **Target**: `lib/vde-cluster-utils`, `githooks/usp-validator.zsh`, `bin/check-zsh-shebang.zsh`, and any other scripts identified by a deep scan.
2. **Action**:
   - Convert all top-level `local` declarations to `typeset` or standard assignments to ensure strict functional scope compliance and prevent `RC 2` errors in `zsh -c` direct execution.
   - Purge all remaining Bash-style `=~` regex operators, replacing them with Zsh-native globbing (e.g., `[[ $var == pattern ]]`).

### Strike II: Architectural Tagging Completion (Mandate 24)
1. **Target**: `configs/ssh/config`, `tests/features/__init__.py`, `tests/features/steps/__init__.py`, and any other `.py`, `.zsh`, or configuration files lacking tags.
2. **Action**:
   - Inject the mandatory `@forge`, `@armor`, or `@shared-law` architectural tags into lines 2-3 of these files, adhering to the correct comment syntax for each file type.

### Strike III: Archival Purification & Final Sweep
1. **Target**: `plans/archive/` and the broader repository.
2. **Action**:
   - Audit archival scripts for bashisms and apply necessary corrections or re-classify them to ensure they do not contaminate future code searches or audits.
   - Perform a final deep search for `export -f`, `0`-indexed arrays (`[0]`), and `tr`/`sed` subshells to guarantee absolute Zsh-native purity.

## Verification & Testing
- Execute `python3 -m behave tests/features/core-infrastructure/system-spine.feature`.
- Execute `python3 -m behave tests/features/core-infrastructure/tech-stack-cluster.feature`.
- Invoke the `code-reviewer` agent again to certify that "no issues found" is the final verdict.
