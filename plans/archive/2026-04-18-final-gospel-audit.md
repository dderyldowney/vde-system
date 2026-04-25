# Final Gospel Audit Plan
<!-- @shared-law (Forge Component) -->

**STATUS: 100% COMPLETE**
**DATE:** 2026-04-18

## Objective
Audit and update `docs/ARCHITECTURE.md` and `docs/Technical-Deep-Dive.md` to document the new SSH Hard Rule and the Unified CLI Command Structure, aligning them with the 1.4.1 Sovereign Baseline.

## Key Files & Context
- **`docs/ARCHITECTURE.md`**: Add details about the Unified CLI Router and the inline SSH Hard Rule.
- **`docs/Technical-Deep-Dive.md`**: Add an architectural explanation of the SSH Hard Rule, inline key generation, and the `vde ssh-setup` / `vde ssh-sync` consolidation.

## Implementation Steps

1. **Update `docs/ARCHITECTURE.md`**:
   - In Section 2 (Structural Design), add an entry for the **Unified Command Router (`bin/vde`)** that orchestrates Spoke lifecycles and infrastructure tasks (`vde ssh-setup`, `vde ssh-sync`).
   - Update the **Initialization Ritual (`vde init`)** entry to state that it is subject to the **SSH Hard Rule**, where missing keys are generated inline without restarting the process.

2. **Update `docs/Technical-Deep-Dive.md`**:
   - In Section 5 (Security & Sovereign Bridge), add a sub-section for **SSH Identity Auto-Remediation (The Hard Rule)**. Explain how `vde init` immediately invokes `vde ssh-setup init` inline to generate missing keys, preventing boot loops and preserving initialization determinism.
   - Mention that `vde ssh-setup` and `vde ssh-sync` are now first-class subcommands within the unified `vde` router.

## Verification
- Review the modified files to ensure accuracy and alignment with the 1.4.1 Sovereign Baseline.