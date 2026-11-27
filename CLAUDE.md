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
6. **MERGE**: Only after the User's explicit written approval for that PR (an approval for one PR does not cover another) and only for the head commit they approved. Use `gh pr merge N --merge --delete-branch --match-head-commit <the approved head sha> --subject "$SUBJECT" --body "$BODY"`: a merge commit, never `--squash` or `--rebase` (squash and rebase are disabled in the repository settings), so every commit made during the work stays individually in `develop`. PR titles are untrusted input: build `SUBJECT` ("Merge pull request #N: <PR title>") and `BODY` (what it changes, what it closes, the review outcome, see PR #N) as shell variables and never paste a title into the command text. For a promotion PR (its head is `develop` or `stable`, a permanent branch) omit `--delete-branch`. A security item's merge body stays neutral (item NN, no mechanism).

Committing implementation directly to `develop` is a Creed violation. If you catch yourself writing code or running `git commit` on `develop` without a prior `gh issue create` and feature branch, STOP immediately and retro-fix the process before continuing.

## SECURITY PLAN — MANDATORY. NO EXCEPTIONS.

All security work follows `docs/governance/security-process.md` and the binding agent rules in `.gemini/RULES/security.md` (read it at session start). Never put weakness detail in public text (issues, PRs, branches, commits, state files, changelogs) before its fix has shipped; findings go to a private draft GitHub Security Advisory; only the User publishes an advisory or requests a CVE. `SECURITY.md` is the public policy. For a Vulnerability the Strike runs in the advisory's temporary private fork: the Signet is the neutral public issue, while the branch and the PR (targeting `develop`) live in the fork and are merged as part of the release, after the User's written approval. Only Hardening uses a public PR.

**NO AID TO THE ENEMY.** The repository is public, so nothing about the inner workings or failings of unfixed code goes into any public text, and when unsure it stays private. Every agent, however activated (main agent, sub-agent, skill or command), obeys `.gemini/RULES/security-preamble.md`; every sub-agent prompt begins with it. Security-item branches are named `fix/sec-item-NN`.

## TESTING POLICY — MANDATORY. NO EXCEPTIONS.

All testing follows `docs/development/testing.md` (section "Testing Policy (binding)"), the single source of truth for how we test, and the binding agent rule `.gemini/RULES/testing.md`. Every sub-agent, however activated, obeys `.gemini/RULES/security-preamble.md` and `.gemini/RULES/testing-preamble.md`, and every sub-agent prompt for code work begins with the security preamble and then the testing preamble. A test is shown failing before the change and passing after it, with the literal output of both runs.
