# CLAUDE
<!-- @shared-law (Forge Component) -->
Read and apply @.gemini/instructions.md

Project state and rules live under `.gemini/`: read `.gemini/STATE/MEMORY.md` and `.gemini/STATE/session_handover.md` at session start (see READING LOCATIONS in `.gemini/instructions.md` and the startup checklist in `AGENTS.md`); project rules are in `.gemini/RULES/`.

## STRIKE PROTOCOL — MANDATORY. NO EXCEPTIONS.

Every unit of work (a "Strike") MUST follow this sequence. There is no bypass except an explicit written instruction from the User in the current session:

1. **SIGNET**: `gh issue create` — open a GitHub Issue describing the work BEFORE any implementation begins
2. **BRANCH**: `git checkout -b <type>/<slug>` from `develop` — create a feature branch tied to the Issue
3. **IMPLEMENT**: All code changes on the feature branch only. NEVER commit implementation to `develop` directly.
4. **CHRONICLE**: `gh pr create` — open a PR from the feature branch targeting `develop`
5. **PRE-MERGE HALT**: Stop. Present the PR URL to the User. Wait for explicit written approval before merging.
6. **MERGE**: Only after User written approval. Use `gh pr merge`.

Committing implementation directly to `develop` is a Creed violation. If you catch yourself writing code or running `git commit` on `develop` without a prior `gh issue create` and feature branch, STOP immediately and retro-fix the process before continuing.

## SECURITY PLAN — MANDATORY. NO EXCEPTIONS.

All security work follows `docs/governance/security-process.md` and the binding agent rules in `.gemini/RULES/security.md` (read it at session start). Never put weakness detail in public text (issues, PRs, branches, commits, state files, changelogs) before its fix has shipped; findings go to a private draft GitHub Security Advisory; only the User publishes an advisory or requests a CVE. `SECURITY.md` is the public policy. For a Vulnerability the Strike runs in the advisory's temporary private fork: the Signet is the neutral public issue, while the branch and the PR (targeting `develop`) live in the fork and are merged as part of the release, after the User's written approval. Only Hardening uses a public PR.
