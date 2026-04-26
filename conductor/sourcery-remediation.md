# Sourcery-AI Remediation Plan
<!-- @shared-law (Forge Component) -->

## Objective
Address the feedback provided by the automated auditor (Sourcery-AI) on PR #285. This ensures the BDD test suite remains resilient across platforms and the documentation provides sufficient semantic detail for users.

## Identified Feedback
1.  **Fragile DNS Assertion**: The `nc` test for service bridge connectivity relies on the output containing "succeeded", which varies across `netcat` implementations.
2.  **Missing Semantics**: The detailed behavioral description of `vde create` (port allocation, directory creation, SSH config generation) was lost in the 1.4.1 refactor of `docs/command-reference.md`.

## Remediation Steps
1.  **Harden Test Assertion**:
    - File: `tests/features/advanced-orchestration/dns-discovery.feature`
    - Action: Remove the output content assertion for `nc` and rely exclusively on the `exit code should be 0` assertion, which is the universal standard for connectivity probes.
2.  **Restore Command Details**:
    - File: `docs/command-reference.md`
    - Action: Expand the documentation for `vde create` to include a concise summary of the underlying operations (atomic port allocation, workspace mount creation, and SSH config generation).

## Verification
- `bin/vde-enforce-uap.zsh` must return **PASS (CLEAN)**.
- `python3 -m behave tests/features/advanced-orchestration/dns-discovery.feature` must return **PASS**.
