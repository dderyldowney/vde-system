# Agent Handoff
<!-- @shared-law (Forge Component) -->

Written 2026-11-21 at the end of a long working session, for ANY AI agent (not only Claude) taking over VDE-SYSTEM. It says what was done, what is going on, what comes next, and the rules and traps that cost time. It is a snapshot: **verify every fact below with the commands given before you act on it.**

## 1. Start here

1. Read, in order: `CLAUDE.md`, `.gemini/instructions.md`, `AGENTS.md`, `.gemini/STATE/MEMORY.md`, `.gemini/STATE/session_handover.md`, then this file.
2. Run the startup ritual: `bin/vde-enforce-uap.zsh`, `bin/vde-spine-check.zsh`, and the Proof of Life (`python3 -m behave tests/features/core-infrastructure/proof-of-life-the-contract.feature`; it takes about 15 minutes, and the pre-push gate runs it too, so do not run it twice for one push).
3. The Contract in `.gemini/instructions.md` binds any agent that works here.
4. Check the world before trusting this file:
   - `git fetch origin && git log --oneline -8 origin/develop`
   - `git ls-remote origin develop stable main` and `git rev-parse 1.5.7^{commit}`
   - `gh pr list --state open` and `gh issue list --state open`
   - `ps -eo args | grep -E "behave|pre-push|vde-rebuild"` (stop strays by exact PID, never with a pattern kill)
   - `docker ps -a` (a `vde-python` container and old `vde-*-probe-1` containers are normal residue of an interrupted Proof of Life)

## 2. How work is done here (the Strike protocol)

Every unit of work: open an Issue (the Signet) BEFORE any code; branch from `develop`; work on the branch only; open a PR into `develop` (the Chronicle); **stop and get the User's written approval before any merge** (Rule R); merge only after checks and review feedback are clean. Never commit implementation to `develop`.

- Approvals are specific. A written approval covers the named step only. Outward steps (a release, a tag, `main`, editing a published GitHub Release body) always need their own written approval.
- Do not open new Issues for side findings without the User's approval; keep a parked list instead.
- Code PRs show the Issue's tests, a literal RED run from the code before the fix, and a literal GREEN run from the branch.
- Prove tests can fail: break the code on purpose and watch the test catch it.
- Review feedback (Sourcery, CI, a formal `/code-review`) is read in full, answered thread by thread, and fixed when it can plausibly lose a user's file or break the product in ordinary use. Purely theoretical races are answered with a reason. Do not chase the reviewer forever.
- Do not reply to a review thread with a commit that is not yet on the PR's remote head.
- After any Proof of Life or image build: `docker builder prune --all -f` (never prune images).
- Test runs must scrub the real `HOME` (VDE scripts write real `~/.zshrc` and SSH lines). Tests that run the router or the Spine need the REAL home for the SSH identity.

## 3. Branches, releases and tags

- `develop` is where work lands. `stable` is what students clone: release plus updates. `main` is certified releases only.
- Flow: `develop` -> `stable` (merge commit, never squash or rebase) -> `main` (merge commit) -> `gh release create <tag> --target main`.
- **A published tag is never moved.** Documentation fixes made after a release go to `develop` and wait for the next roll; `main` is not re-rolled for them.
- `.github/workflows/update-stable-alias.yml` force-pushes `stable` to `main` on every push to `main`. So after a release `stable` equals `main`; a roll without a release leaves `stable` ahead of `main` until the next release. (Known weakness, parked: overlapping pushes to `main` could move `stable` backward.)
- The Release body is built from the approved format in section 6.

## 4. What happened (as of the end of this session)

- **1.5.7 is released** (tag `1.5.7` on `main`, GitHub Release live), the baseline of record.
- Merged since: `vde upgrade` (#679, Signet #676), the 1.5.7 release record (#678), the state files (#681), the `vde upgrade` hardening (#684, Signet #683), and a roll of `develop` into `stable` without a release (#682).
- In flight when this was written: PR #686 (these state files, Signet #685). If it is merged, a small second roll into `stable` carries it; verify with `gh pr list` and `git log`.
- `vde upgrade [--dry-run]`: finds the install from where the script lives, fetches the branch you are on, fast-forwards, refuses (changing nothing) on unsafe states, and says which image to rebuild (the base image first when something baked into `vde-base` changed). Exit statuses: 0 done, 2 bad option, 3 cannot be updated, 9 a rebuild or start is running, 13 your copy and origin disagree. Documented in `docs/reference/commands.md` and `docs/reference/scripts.md`; tests in `tests/unit/vde-upgrade.test.zsh`.

## 5. What comes next, in order

1. **1.5.8 is the SECURITY release.** Strictly security-related work only. It contains #668 and the security-related items from the parked list (triage them when this starts; take only the genuinely security-related ones). What is already merged stays; the 1.5.8 notes name it plainly and headline the security items. Do not describe an unpatched weakness in public text, state files, PR text or the changelog until the fix has shipped; refer to it by issue number. Its own Signet, PR and release chain, with the User's approval at every outward step.
2. **1.5.9 is the DOCS release**, and security comes first. Scope the User approved: rewrite the docs for students and for VDE developers in a plain, direct, 1970s helper-manual voice (second person, payoff first, short sentences, a verification line in every step, dry wit sparingly); remove ALL mythos from human-facing docs (it stays only in agent-facing files: `CLAUDE.md`, `AGENTS.md`, `.gemini/`); new-student and onboarding docs FIRST, VDE-developer docs SECOND, including a developer doc that explains the agent layer in plain language (why it exists, how and why it is applied, how to maintain it); every command shown must have been run, in the order printed; explain what lives inside and outside the container and how to change the Projects location at install and after (`--projects-dir`, `vde set-projects-dir`); link each doc to the code it describes; take a census of docs versus code before moving or deleting anything (the vendored zsh manual and `bin/archive/` are large); Hub and Spoke and the command `path-of-the-foundling` stay.
   - **The mantra: "Well documented, empirically tested."**
3. Later: #671 and the other open code Issues (`gh issue list`), and the parked items that are not security-related.

## 6. Release notes format (approved, standing)

Marketing-style hero and headline; "What's new" as short benefit blocks in second person; "Fixes and hardening in detail" grouped, every item with its Issue or PR number as a link; "Get VDE <version>" with install and upgrade steps; "Known limits"; a footer with an ABSOLUTE link to `docs/releases/<version>.md`. The repo record ends with an "About this record" section. Mirror the same content into `docs/releases/<version>.md`. Show the User the draft before publishing. Do not add a README to `docs/releases/` (the version sync tool lists every `.md` there as a release).

## 7. Technical traps (each cost real time)

- The Sovereign Audit forbids `sleep N` in ANY zsh file ("use polling"): use `zmodload zsh/zselect; zselect -t <centiseconds>` or `bin/vde-poll`. Run `VDE_SHIB_REFRESH_BASE=1 zsh bin/vde-enforce-uap.zsh --quiet; echo $?` BEFORE every push; it must print 0.
- A pre-push gate that fails prints its reason in the first lines; do not cut push output with `tail`. Run `git push > log 2>&1; echo PUSHRC=$? >> log`, and judge success by the REMOTE sha, never by a background task saying "completed".
- Every zsh file needs the shibboleth line `typeset _ZSH_PURE=${(%):-%x}` in the first 20 lines. Style: 2-space indent, a `main()` entry point, `print -P` for colour. Never call `jq` directly. No `bash` or `sh` outside the documented exceptions.
- `"${${(f)"$(cmd)"}[1]}"` returns the first CHARACTER, not the first line: put the lines in an array first. `status` is a read-only zsh variable.
- `claim_lock` writes `PID:PGID:TIMESTAMP` to a lock's `pid` file; per-Spoke locks live under `${VDE_LOCKS_DIR:-<root>/.locks}/vms/<name>.lock`, and `vde start` uses `<root>/.locks`.
- Older git (CI) refuses to overwrite an identical untracked or ignored file in a merge; newer git silently overwrites ignored files.
- Tests are tagged `@forge` unless the Proof of Life needs them (reviewers keep suggesting `@armor`; the repo rule stands).
- Shell commands that match a process pattern (`pkill -f`) can match your own command line. `rm -rf` on temp directories is blocked by a safety check; use `mktemp` inside the scratchpad and leave it. `git push --delete` is blocked; use `gh pr merge --delete-branch`. `gh pr edit` fails on the deprecated Projects field; use `gh api -X PATCH repos/dderyldowney/vde-system/pulls/N -f title=...`. PR titles must not start with an uppercase subject. A running git worktree must not be edited while its pre-push gate runs.
- If the permission classifier denies a merge or a kill, stop and report; the User will say "retry".
- Multi-file edits should be one-file-per-agent swarms (Mandate E); when they were scripted instead, say so in the PR.

## 8. Parked, not yet Issues

Needs the User's approval to file. The `update-stable-alias.yml` workflow can move `stable` backward on overlapping pushes. A retry after an interrupted `vde upgrade` cannot reprint the rebuild guidance. `bin/add-vm-type` passes `${QUIET}` as `skip_probe`. `bin/cleanup-ports` runs under `set -e` with `((removed++))`. Several older findings in the maintainer's backlog; the security-related ones belong to 1.5.8.

**This is the Way.**
