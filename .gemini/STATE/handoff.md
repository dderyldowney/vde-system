# Agent Handoff
<!-- @shared-law (Forge Component) -->

Written 2026-11-21 and refreshed 2026-11-22 (Signet #740) at the end of long working sessions, for ANY AI agent (not only Claude) taking over VDE-SYSTEM. It says what was done, what is going on, what comes next, and the rules and traps that cost time. It is a snapshot: **verify every fact below with the commands given before you act on it.**

## 1. Start here

1. Read, in order: `CLAUDE.md`, `.gemini/instructions.md`, `AGENTS.md`, `.gemini/RULES/security.md`, `.gemini/STATE/MEMORY.md`, `.gemini/STATE/session_handover.md`, then this file.
2. The Contract in `.gemini/instructions.md` binds any agent that works here.
3. Check the world before trusting this file or running any lifecycle test:
   - `git fetch origin && git log --oneline -8 origin/develop`
   - `git ls-remote origin develop stable main` and `git rev-parse '1.5.7^{commit}'`
   - `gh pr list --state open` and `gh issue list --state open`
   - `ps -eo pid,args | grep -E '[b]ehave|[p]re-push|[v]de-rebuild'` (stop strays by exact PID, never with a pattern kill; do not start Proof of Life while another run is active)
   - `docker ps -a` (a `vde-python` container and old `vde-*-probe-1` containers are normal residue of an interrupted Proof of Life)
4. **Main agent only** (sub-agents inherit certification and MUST skip this step, per `AGENTS.md`): once the process check above shows no active run, run the startup ritual in order: `bin/vde-enforce-uap.zsh`, `bin/vde-spine-check.zsh`, and the Proof of Life (`python3 -m behave tests/features/core-infrastructure/proof-of-life-the-contract.feature`, ~15 minutes). Note that a direct `behave` run does **not** write the pre-push stamp (`lib/vde-pol-stamp`), so a later push will rerun the gate unless you rely on the pre-push gate itself or invoke Proof of Life through `vde_pol_run_and_stamp` from `lib/vde-pol-stamp` on a clean tree.

## 2. How work is done here (the Strike protocol)

Every unit of work: open an Issue (the Signet) BEFORE any code; branch from `develop`; work on the branch only; open a PR into `develop` (the Chronicle); **stop and get the User's written approval before any merge** (Rule R); merge only after checks and review feedback are clean. Never commit implementation to `develop`. **Branch promotions are exempt from the branch-from-`develop` / PR-into-`develop` rule**: `develop` -> `stable` promotes from `develop` into `stable`, and `stable` -> `main` promotes from `stable` into `main` (never from `develop`).

- Approvals are specific. A written approval covers the named step only. Outward steps (a release, a tag, `main`, editing a published GitHub Release body) always need their own written approval.
- Do not open new Issues for side findings without the User's approval; keep a parked list instead.
- Code PRs show the Issue's tests, a literal RED run from the code before the fix, and a literal GREEN run from the branch.
- Prove tests can fail: break the code on purpose and watch the test catch it.
- Review feedback (Sourcery, CI, a formal `/code-review`) is read in full, answered thread by thread, and fixed when it can plausibly lose a user's file or break the product in ordinary use. Purely theoretical races are answered with a reason. Do not chase the reviewer forever.
- Do not reply to a review thread with a commit that is not yet on the PR's remote head.
- After any Proof of Life or image build: `docker builder prune --all -f` (never prune images).
- Test runs must scrub the real `HOME` (VDE scripts write real `~/.zshrc` and SSH lines). Tests that run the router or the Spine need the REAL home for the SSH identity.
- Do NOT add a `Co-Authored-By` line (or a "Generated with" line) to commit messages or PR bodies: the tooling adds it automatically. Write a neutral message and `Refs #N` / `Closes #N`.
- Public text that discloses an unfixed weakness (a bot review, a comment) is handled by the standing order in `.gemini/RULES/security.md` rule 10: save a private copy in the private security directory, then delete it; hide only what cannot be deleted. Scan every bot review, including the review body, before merging; answer each review thread.
- The private security directory is `~/.vde-security/` (or `VDE_SECURITY_DIR`), created by the Forge at mode 0700 through `lib/vde-security-dir` (called from `bin/vde-enforce-uap.zsh`). Ledger and evidence live there, never in the repository.
- **NO AID TO THE ENEMY.** The repository is public: nothing about the inner workings or failings of unfixed code goes into any public text, and when unsure it stays private. Every agent, however activated, obeys `.gemini/RULES/security-preamble.md`, and every sub-agent prompt begins with it. Security-item branches are named `fix/sec-item-NN` (NN = the item number in the neutral issue title). New findings go to the private ledger first; the public issue is created neutral from the start.

## 3. Branches, releases and tags

- `develop` is where work lands. `stable` is what students clone: release plus updates. `main` is certified releases only.
- Flow: `develop` -> `stable` (promotion PR targeting `stable`; merge commit, never squash or rebase) -> `main` (promotion PR targeting `main`; merge commit) -> `gh release create <tag> --target main`.
- **Every PR merges with a merge commit**, never a squash or a rebase (both are disabled in the repository settings, since squash drops a branch's own commits from `develop`): `gh pr merge N --merge --delete-branch --match-head-commit <the approved head sha> --subject "$SUBJECT" --body "$BODY"`, where `SUBJECT` ("Merge pull request #N: <PR title>") and `BODY` (what it changes, what it closes, the review outcome, see PR #N) are shell variables: PR titles are untrusted input and are never pasted into the command text. For a promotion PR (its head is `develop` or `stable`, a permanent branch) omit `--delete-branch`. A merge needs the User's explicit written approval for that PR, for the head commit they approved; an approval for one PR does not cover another. A security item's merge body stays neutral (item NN, no mechanism).
- **A published tag is never moved.** Documentation fixes made after a release go to `develop` and wait for the next roll; `main` is not re-rolled for them.
- `.github/workflows/update-stable-alias.yml` updates `stable` to `main` on pushes to `main`. So after a release `stable` equals `main`; a roll without a release leaves `stable` ahead of `main` until the next release. (A parked workflow hardening item is queued for 1.5.8; details stay out of public state files until shipped.)
- The Release body is built from the approved format in section 6.

## 4. What happened (as of the end of this session)

- **1.5.7 is released** (tag `1.5.7` on `main`, GitHub Release live), the baseline of record.
- Merged since: `vde upgrade` (#679, Signet #676), the 1.5.7 release record (#678), the state files (#681, #686), the `vde upgrade` review fixes (#684, Signet #683), and two `develop` -> `stable` rolls without a release (#682, #687). Verify current state with `gh pr list` and `git log`.
- `vde upgrade [--dry-run]`: finds the install from where the script lives, fetches the branch you are on, fast-forwards, refuses (changing nothing) on unsafe states, and says which image to rebuild (the base image first when something baked into `vde-base` changed). Exit statuses: 0 done, 2 bad option, 3 cannot be updated, 9 a rebuild or start is running, 13 your copy and origin disagree. Documented in `docs/reference/commands.md` and `docs/reference/scripts.md`; tests in `tests/unit/vde-upgrade.test.zsh`.
- 2026-11-22: the fail-closed audit and check scripts (#724, Signet #719), the security process (#738, Signet #736) and the private security directory (#739, Signet #737) merged. `develop` moved past them; read the tip with `git log -1 origin/develop`.

## 5. What comes next, in order

**#725 is DONE in PR #743** (the Code Coverage job now fails when a test fails; `tests/ci-coverage-exclusions.txt` lists the three tests it does not run: two Docker-only integration tests and the slow git-fixture-isolation suite, which still runs in Sovereign Tests). **NEXT ACTION: the 1.5.8 security items** (#707-#718, #722, #723, #726, #727-#735, #742), in the severity order the User approves; ask the User before starting.

1. **1.5.8 is the SECURITY release.** Strictly security-related work only. It contains #726 (which replaced #668), the neutral issues #707-#718, #722, #723, the sub-issues #727-#735 of #720 and #721, and #725 (DONE in PR #743, so the fixes have tests that can fail). All of it follows the project security process: `docs/governance/security-process.md` and the binding agent rules in `.gemini/RULES/security.md` (Signet #736). What is already merged stays; the 1.5.8 notes name it plainly and headline the security items. Do not describe an unpatched weakness in public text, state files, PR text or the changelog until the fix has shipped; refer to it by issue number. Its own Signet, PR and release chain, with the User's approval at every outward step.
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
- Shell commands that match a process pattern (`pkill -f`) can match your own command line. `rm -rf` on temp directories is blocked by a safety check; use `mktemp` inside the scratchpad and leave it. `git push --delete` is blocked; use the merge command from CLAUDE.md step 6 (it carries `--delete-branch`). `gh pr edit` fails on the deprecated Projects field; use `gh api -X PATCH repos/dderyldowney/vde-system/pulls/N -f title=...`. PR titles must not start with an uppercase subject. A running git worktree must not be edited while its pre-push gate runs.
- If the permission classifier denies a merge or a kill, stop and report; the User will say "retry".
- Multi-file edits should be one-file-per-agent swarms (Mandate E); when they were scripted instead, say so in the PR.
- In zsh an unquoted separator such as `=====` starts a command substitution and fails: quote separators like `'-----'`.
- A background shell command is capped at 10 minutes; a ~15 minute pre-push gate can outlive it. Judge a push by the REMOTE sha (`git ls-remote --heads origin <branch>`), not by a task notification. Do not start a second Proof of Life while one is running (they collide on Docker state and locks): wait for the first, then push.
- A task notification that says a background command "completed" only means the wrapper shell exited; check the log file or process list for the real result.
- `gh pr checks --watch` waits for every check, including the final summary job; use it before merging.
- A sub-agent's output is not a commit: review every diff yourself.
- Running an integration test by hand (tests/integration/jupyterlab-spoke, tech-stack-empirical) ignites real Spokes and the latter runs `vde stop all -f`: stop any Spoke you started afterwards, or the next Proof of Life fails Rule K (3 Spokes max).

## 8. Parked, not yet Issues

Needs the User's approval to file. Security-related parked items (queued for 1.5.8 alongside `#726`) are kept out of public state files until fixed; refer to them by issue number once filed. Non-security parked items include minor CLI and script follow-ups (`vde upgrade` retry rebuild guidance, `bin/add-vm-type` quiet-flag forwarding, `bin/cleanup-ports` counter arithmetic under `set -e`, and other non-security backlog items deferred past 1.5.8/1.5.9).

**This is the Way.**
