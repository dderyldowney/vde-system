# VDE Security Process
<!-- @forge (Governance Sentinel) -->

This is the binding procedure for handling security problems in VDE, from the first report to the public advisory. It applies to every maintainer and every AI agent working in this repository. The public summary is [`SECURITY.md`](../../SECURITY.md); the rules agents must follow are in [`.gemini/RULES/security.md`](../../.gemini/RULES/security.md).

It follows ISO/IEC 29147 (vulnerability disclosure), ISO/IEC 30111 (vulnerability handling), the OpenSSF *Guide to Coordinated Vulnerability Disclosure for Open Source Projects*, FIRST CVSS v4.0, MITRE CWE and, for prevention, NIST SSDF (SP 800-218). It is sized for a project with one maintainer.

## 0. Roles

| Role | Who | May |
|---|---|---|
| Security lead | The maintainer | Everything. The ONLY person who confirms severity, approves a fix for merge, publishes an advisory and requests a CVE |
| Agents (AI) | Any agent working in this repository | Find, verify, draft and fix inside a Strike. Never publish anything and never put weakness detail in public text |
| Reporters | Anyone | Report privately; are credited |

## 1. Intake

A finding arrives from: private vulnerability reporting (the **Report a vulnerability** button), our own audits (human or agent), CodeQL, Dependabot, secret scanning, or an upstream advisory (base image, installer, GitHub Action).

- A suspected vulnerability is NEVER written in a public issue, pull request, commit message, discussion, state file or changelog.
- It goes straight into a **draft GitHub Security Advisory** (private). Our own findings are entered there directly by the security lead, or by an agent only when the security lead asks.
- **Check for a duplicate first.** Before creating a draft, search the private ledger and the existing drafts. A repeat report of the same finding (another source, or a retried report) is attached to the existing record and never gets a second draft.
- An agent that finds a suspected vulnerability tells the security lead in the session and records it in the private ledger straight away, without waiting to be asked. The ledger is private and outside the repository; creating a draft advisory still waits for the security lead's request.
- A finding in a third-party project is reported privately to that project (through its own security policy), and our exposure to it is tracked in our own draft advisory.

## 2. Triage

Targets: acknowledge an outside report within **3 business days**; finish triage within **7 days**.

1. **Reproduce.** Record how it was verified: by running it (EXEC), by reading the code (SOURCE), or not yet (OPEN).
2. **Apply the threat model.** The attackers are: content inside a Spoke, a peer on the local network, a hostile repository, registry entry or contribution, and a compromised upstream. The logged-in user passing arguments to their own commands is NOT an attacker.
3. **Classify:**
   - **Vulnerability**: crosses one of those boundaries. Gets an advisory.
   - **Hardening**: a real defect that crosses no boundary. Fixed in the normal flow, no advisory.
   - **Not an issue**: closed with the reason (the reporter is told why).
   - **Close the draft on Hardening or Not an issue.** The security lead closes or deletes the draft advisory, and the triage reason stays in the private ledger.
4. **Score** with a CVSS v4.0 vector and one or more CWE ids. The severity band follows the score; the security lead confirms or adjusts it and records why.
5. **Record** the evidence in the private ledger (Section 3).

## 3. Tracking

| Where | What it holds | Who sees it |
|---|---|---|
| Draft GitHub Security Advisory | Full detail, CVSS, CWE, affected and patched versions, credit | Maintainer and reporter |
| Private ledger (kept by the security lead outside the repository) | Verification evidence, the map from public item numbers to findings, the fix log | Security lead only |
| Public issue (the Signet) | Title `fix: <version> security hardening, item NN` and a generic body | Everyone |
| Branch, commits, pull request | A Vulnerability: in the advisory's temporary private fork. Hardening: public, with the same neutral wording (branch `fix/sec-item-NN`) | Vulnerability: maintainer and reporter. Hardening: everyone |

Every security item, Hardening or Vulnerability, uses the branch name `fix/sec-item-NN` (NN is the item number in the neutral issue title). For a Vulnerability the branch lives in the advisory's temporary private fork; the name reveals nothing and maps straight to the neutral issue. The stance behind all of this is **NO AID TO THE ENEMY**: the repository is public, so nothing about the inner workings or failings of unfixed code is published first, and when unsure the item stays private.

Public text names no component, file, weakness class or attack until the fix has shipped. An item number links the public issue to the private record.

**Reserve the item number first.** The security lead assigns each item number by writing it in the private ledger before any issue, branch or parallel triage uses it. A number is never reused.

**The private directory.** The ledger, the evidence and any saved copies live in one directory outside the repository: `~/.vde-security/` by default, or the path in the `VDE_SECURITY_DIR` environment variable. It is created by the Forge (the Sovereign Audit, `bin/vde-enforce-uap.zsh`, through `lib/vde-security-dir`) the first time the Forge is used on a machine, with mode `0700`. A looser mode is tightened, nothing in it is ever deleted or overwritten, and a path that is relative, inside the repository, a symlink, not a directory or owned by someone else is refused. The student install and upgrade never create it.

**Remove any public text that discloses a weakness we are fixing.** This is a standing order for every maintainer and every agent. If a bot (a code reviewer, a scanner, a CI log) or a person posts, in public, how an unfixed weakness works (a pull request comment, a review body, an issue comment, a check output), the security lead is told and the public text is removed at once, in this order: first save a private copy in the private directory and note it in the private ledger, then delete the public text. Inline and issue comments can be deleted; a submitted review body cannot be deleted through the API, so it is hidden (minimized) and GitHub Support is asked to purge it. Hiding alone is not enough, because hidden text stays readable. Deleting does not recall email notifications or public event archives, so the exposure window is recorded in the ledger. Every bot review is scanned for this, including its review body and any summary comment, and the detail is never quoted again in public text: it is referred to by comment id.

## 4. Fix

| Class and severity | Fix target (from triage) | Where the fix is written |
|---|---|---|
| Vulnerability, Critical | 7 days, its own patch release | The advisory's **temporary private fork** |
| Vulnerability, High | 30 days | The advisory's **temporary private fork** |
| Vulnerability, Medium | 90 days | The advisory's **temporary private fork** |
| Vulnerability, Low | The next planned release | The advisory's **temporary private fork** |
| Hardening (no advisory) | The next planned release | A normal Strike with a neutral public pull request |

A public pull request shows its diff, its regression test and its RED and GREEN output, and any of them can reveal the hole. That is why every Vulnerability, whatever its severity, is fixed in the private fork.

**The Strike Protocol in a private fork.** The Signet is the neutral public issue (Section 3), and it is the only public trace before the release. The feature branch and the pull request (targeting `develop`) live in the advisory's temporary private fork, and the RED and GREEN evidence is posted there. The User's written approval is still required before the fork is merged, and the fork is merged as part of the release (Section 5), so the fix is not public before it ships. GitHub Actions do not run in a temporary private fork, so the local gates (the Sovereign suite, the pre-push Proof of Life and the audits) must pass there, and CI runs after the merge.

**Release-day sequence for a private fork.** The fork's pull request is merged only on release day, with the User's written approval, and the rest of the release chain (Section 5) follows in the same sitting: `develop` to `stable`, `stable` to `main`, the release published, the advisories published (Section 6). The fix is not merged to any public branch ahead of that sequence.

**Combined gate before the release chain.** No fork is run together with the others before this gate, so the merged tree is proven as a whole before any fix becomes public. The gate runs on a candidate tree: a local clone of `develop` into which every fork branch for the release is merged in the order set by the release plan, and which is never pushed. The release plan is a list of the fork pull requests in merge order, with any shared commits noted, and it pins the `develop` base sha and each fork head sha the gate tests; the User approves it before release day. On the candidate, (1) the full Sovereign suite (`tests/run-sovereign-tests.zsh`) passes; (2) the Proof of Life passes; (3) the Spoke smoke matrix (`tests/integration/spoke-smoke-matrix.test.zsh`) passes. A failure stops the sequence, and nothing is rolled to `stable` until the gate is green. A failure caused by a Vulnerability fix is fixed in that advisory's temporary private fork (a new commit and a new head sha) and the gate is run again on a fresh candidate; a failure in a Hardening item or an unrelated regression goes through a normal public Strike. The User's written approval for each fork merge is given after the gate passes and names the head sha the gate tested. Each release-day merge uses `--match-head-commit` with exactly the sha the gate tested, and if `develop` or a fork head moves after the gate, a new candidate is built and the gate is run again. After the fork pull requests are merged, the `develop` tree must be identical to the candidate tree (compare `git rev-parse develop^{tree}` with the candidate's); if it is identical the gate result carries over, and if it is not the full gate runs again on the merged `develop` tree before anything is rolled to `stable`. CI on `develop` must also be green; if it is not, the fixes are already public, so the sequence stops, the User is told at once, and the failure is fixed on `develop` before anything is rolled to `stable`. The release waits until it is ready; a failed gate never turns into an early release. The roll from `develop` to `stable` is a promotion pull request and needs its own written approval, as does the roll from `stable` to `main`. All of this happens in the same sitting as the release-day sequence.

Every fix, wherever it is written:

- follows the Strike Protocol (Signet, feature branch, pull request, written approval before merge);
- adds a regression test, shown failing before the fix and passing after it (literal RED and GREEN runs), which stays in the suite permanently;
- includes a **variant analysis**: search the code base for the same pattern; each variant found joins the same advisory or gets its own;
- keeps the Proof of Life green.

## 5. Patch Release

- Security fixes ship in a patch release (`1.5.x`). A Critical fix ships in its own release as soon as it is ready.
- Supported versions are the latest release and the `stable` branch. There are no backports; the remedy for an older version is to upgrade.
- The release notes get a **Security** section: each advisory id, its severity and one line of impact. Hardening items are listed briefly, without exploit detail.
- The release chain itself is unchanged (version bump, `develop` to `stable`, `stable` to `main`, release on `main`), with written approval at each outward step. For a Vulnerability fixed in a private fork, it runs as the release-day sequence in Section 4.

## 6. Disclosure

On the day the fixing release is published:

1. Publish each advisory (it then enters the GitHub Advisory Database and the OSV database).
2. Request a CVE through GitHub for every published vulnerability of Medium severity or higher.
3. Credit the reporter, unless they decline.
4. Correct any public documentation whose statements the fix changes (including `SECURITY.md`).
5. Add the entry to [`docs/security/advisories.md`](../security/advisories.md).

**Early disclosure.** The maximum embargo is **90 days** from the report. If a fix is not ready by then, or the problem is exploited or becomes public earlier, the security lead (never an agent) publishes the advisory early with what is known plus a workaround, and the fix follows in the patch release. This is the only exception to disclosure on release day.

## 7. Alerts

- The GitHub Release with its Security section notifies everyone who watches releases.
- A published advisory notifies watchers who chose security alerts and appears on the repository's Security tab, in the GitHub Advisory Database and in OSV.
- For Critical and High: also post a pinned announcement in GitHub Discussions.
- VDE is not a package that Dependabot tracks, so users receive no automatic Dependabot alert. `SECURITY.md` tells users how to watch the repository.

## 8. Prevention

Always on: secret scanning with push protection, Dependabot (Python and GitHub Actions), CodeQL (Actions and Python), the security audit (`bin/vde-security-audit.zsh`) inside the Sovereign Audit, the pre-commit secret scan and the pre-push gate.

Standing practice:

- A full security audit before every minor release, verified and triaged with this process.
- Every security rule must be proven to bite: a test shows it failing on a violating example.
- New downloads in setup scripts verify a checksum or signature.
- Planned improvements are tracked as their own issues (pinning GitHub Actions to commit SHAs, Dependabot for Dockerfiles, the OpenSSF Scorecard).

## 9. After Each Advisory

A short private retrospective in the ledger: the root cause, why our gates missed it, which test or gate now catches it, and whether the threat model needs an update.
