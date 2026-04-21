# CLAUDE
<!-- @forge (Agent Instructions) -->
<!-- @shared-law (Agent Instructions) -->
Read and apply @AGENTS.md

## STRIKE PROTOCOL — MANDATORY. NO EXCEPTIONS.

Every unit of work (a "Strike") MUST follow this sequence. There is no bypass except an explicit written instruction from the User in the current session:

1. **SIGNET**: `gh issue create` — open a GitHub Issue describing the work BEFORE any implementation begins
2. **BRANCH**: `git checkout -b <type>/<slug>` from `develop` — create a feature branch tied to the Issue
3. **IMPLEMENT**: All code changes on the feature branch only. NEVER commit implementation to `develop` directly.
4. **CHRONICLE**: `gh pr create` — open a PR from the feature branch targeting `develop`
5. **PRE-MERGE HALT**: Stop. Present the PR URL to the User. Wait for explicit written approval before merging.
6. **MERGE**: Only after User written approval. Use `gh pr merge`.

Committing implementation directly to `develop` is a Creed violation. If you catch yourself writing code or running `git commit` on `develop` without a prior `gh issue create` and feature branch, STOP immediately and retro-fix the process before continuing.
