# VDE GitHub Infrastructure Lifecycle
<!-- @forge (AI Governance) -->

This document defines the official procedures and lifecycle for interacting with the VDE Hub (GitHub). The VDE ecosystem consists of two distinct projects with separate responsibilities, governed by the **Sovereign Baseline (1.5.7)**.

## 1. Project Separation

| Project | Designation | Responsibility | Dependencies |
| :--- | :--- | :--- | :--- |
| **Project 1** | **The Armor** | The VDE Engine product (Runtime). | Unyielding Tetrad (zsh, git, docker, ssh). AI-Unaware. |
| **Project 2** | **The Forge** | AI-Governance & Development System. | `gh` (GitHub CLI), AI rules, workflows, MCP servers. |

### Core Mandate
- **Project 1 (The Armor)** must never depend on Project 2 or `gh` for its runtime operation. It is purely driven by the Tetrad.
- **Project 2 (The Forge)** owns all GitHub life (Issues, PRs, CI, Releases) and uses the `gh` CLI as its foundational tool.

## 2. The Strike Loop (Project 2: The Forge)

All development on the Armor (Project 1) must be governed by the Forge (Project 2) using the **Ritual of the Signet and Chronicle**:

1.  **Signet (Issue)**: Create an Issue detailing the "Sovereign Reason".
    - Command: `gh issue create --title "..." --body "..."`
    - *Note: `gh` is a mandatory requirement for the Forge development backend.*
2.  **The Anvil (Branching)**: VDE follows a strict three-branch model:
    - **`develop` (The Anvil)**: The primary integration branch and repository default. All work MUST occur on feature branches originating here.
    - **`stable`**: The intermediate stability branch. Represents the last certified release plus any pending stable updates. **Users ALWAYS clone `stable` for the most current stable code.**
    - **`main` (Production)**: Reserved for certified releases of the Sovereign Baseline. All step tagging and GitHub releases occur here. `main` is always mirrored from `stable`.
    - **Flow**: `develop` → `stable` → `main`
3.  **Strike (Branch)**: Create a feature branch from `develop`.
    - Command: `git checkout -b <type>/<slug> develop`
4.  **Reforging (Development)**: Apply changes using the iterative **Plan -> Act -> Validate** cycle.
5.  **Chronicle (PR)**: Create a Pull Request linking to the Signet.
    - Command: `gh pr create --title "..." --body "..."`
6.  **Audit (CI/CD)**: All GitHub Actions, workflows, and scanner bots must report **100% GREEN**.
7.  **Finalization**: Merge is performed ONLY by the Clan Leader (User) after a successful Code Review.

## 3. CI/CD Heartbeat

The VDE CI Pipeline (`.github/workflows/vde-ci.yml`) is the heartbeat of the Forge. It enforces the following:

- **Technical Integrity**: Runs `bin/vde-check-tetrad.zsh` to ensure the Armor's base is sound.
- **Governance Audit**: Runs `bin/vde-enforce-uap.zsh` (Project 2) to ensure development adheres to mandates.
- **Atomic Real-Time Audit**: Core data (`vm-types.json`) is audited against the schema using self-destructing atomic copies.
- **Linting & Tests**: Standard ZSH syntax, Ruff Python, and 100% PASS for Sovereign Tests.

## 4. Label Governance

Repository labels are standardized to Conventional Commit specifications:

| Label | Usage |
| :--- | :--- |
| `feat` / `feature` | New features and capabilities. |
| `fix` / `bug` | Correcting fractures in the Beskar. |
| `chore` | Maintenance and housekeeping. |
| `docs` | Documentation and sacred texts. |
| `ci` | Automation and GitHub Actions. |
| `refactor` | Code restructuring without behavioral change. |
| `security` | Remediations and hardening. |

*Note: `feature` is an alias for `enhancement`/`feat` for project-specific convenience.*

## 5. The Dual-Gate System

The VDE uses two distinct validation gates to ensure both technical and structural integrity.

### Gate 1: The Technical Integrity Gate (Project 1: The Armor)
- **Script**: `bin/vde-check-tetrad.zsh`
- **Trigger**: Every execution of the `vde` orchestrator or `bin/ssh-vm`.
- **Purpose**: AI-unaware verification of the Unyielding Tetrad (zsh, git, docker, ssh) and the directory environment.
- **Usage**: Lightweight, student-facing, mandatory for runtime.

### Gate 2: The Heavy Governance Gate (Project 2: The Forge)
- **Script**: `bin/vde-enforce-uap.zsh`
- **Trigger**: **Agent** ignition, **CI/CD** workflows, and the **Pre-Push Hook**.
- **Purpose**: Deep audit of the Rule Spine, Mandate compliance, and structural governance.
- **Pillar Link**: The Forge cannot be lit without the Armor. This gate **trips the Technical Integrity Gate first** before proceeding to governance checks.
- **Requirement**: `gh` (GitHub CLI) is a mandatory requirement for this gate to interact with the Hub.

## 6. The Pre-Push Gate

The push is the full-certification boundary. The `pre-push` git hook checks every commit the push carries, oldest first. The tip of every pushed branch (the newest commit of each ref in the push; a push of one branch has one tip) gets the full certification, once per tip, and every other commit in the range gets the fast check. Each commit's tree is checked in a throwaway worktree, so the working tree is never touched.

- **Tip (full tier), once per tip**: the Sovereign Audit (`vde-enforce-uap.zsh`), the full Sovereign suite (`tests/run-sovereign-tests.zsh`), the **Proof of Life** (`tests/features/core-infrastructure/proof-of-life-the-contract.feature`), and the Gospel Audit.
- **Each earlier commit (fast tier)**: the Sovereign Audit, the Gospel Audit, and the unit suites (`tests/unit/*.test.zsh`) that this commit adds or changes, each run exactly as the Sovereign runner would run it (a suite that uses docker uses it as its own test does). The runner's exclusion list applies. No full suite, no Proof of Life, and no Spoke smoke matrix run. A commit that changes no unit suites is checked by the audits alone. A changed unit suite that the Sovereign runner does not list as runnable (it is in the exclusion list) is not run by the fast check, exactly as the full suite skips it. For a merge commit the changed files are those it brings in relative to its first parent, so the unit suites a merge changes are checked like any other commit's.

A refused push names the commit, the tier and the step that failed. A failing earlier commit blocks the push even when the tip would pass. The Proof of Life never runs for an earlier commit.

The unit suites and the full Sovereign suite run under a throwaway HOME inside the gate's scratch directory; the Proof of Life (behave) runs with the caller's own HOME, while the repository-selecting git variables are removed for every step of the gate.

Range rules: for a branch that already exists on the remote, the range is the commits after the remote's tip. For a new branch, it is the commits the remote does not already hold. A delete, or a push with no new commits, has nothing to certify. A pushed tip that the remote already holds carries nothing new and is not certified again, whether it comes from a rewind or from a new branch or tag at a commit the remote already has: the range holds only the commits the remote lacks, and an empty range prints "nothing to certify". Trust model: each commit is checked with its own audit, test runner and tests (they are part of the commit), while the gate script and the gate's own libraries always come from the tree that is pushing, so a commit cannot replace the gate.

**Stamp reuse (Signet #602, Signet #769, Signet #770)**: each certified check gets a stamp in `vde-gate-stamps` under the git common directory (local, untracked, never pushed). A full stamp is per tree, named by the tree hash, because "this tree passed the full certification" is the claim. A fast stamp is per commit, named `<tree>.<commit>`, because "this commit passed the fast check" is the claim. A full stamp satisfies a fast request for any commit with that tree. A fast stamp never satisfies a full request and is never reused for another commit that happens to have the same tree, so the tip is always fully certified before it is pushed. Every stamp is reused only for the exact tree hash (full) or exact commit (fast), only when its checkout was clean, and only while it is under 30 minutes old (`VDE_POL_STAMP_TTL`, seconds, default 1800). Any new commit, any edit, an expired stamp, or a failed check means the check runs again.

To certify HEAD in full ahead of a push, run `zsh githooks/proof-of-life-hook.zsh`. A manual run certifies HEAD only and needs a clean tracked worktree; untracked files are outside the pushed tree and do not affect the result.

On GitHub the same tests run again in CI as part of the pull request. In an advisory's temporary private fork CI does not run, so this local gate is the only check, and it behaves the same way there.

Code is strictly forbidden from leaving the Forge unless both Gates are Green.

**This is the Way.**
