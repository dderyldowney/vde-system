# Design Spec: Automated 'stable' Alias for Main Branch

**Date:** 2026-04-14
**Status:** Approved
**Target:** Sovereign Baseline 1.3.1 (GitHub Automation & Documentation)

## 1. Goal
Support `stable` as an alias for the `main` branch, allowing users to natively execute `git clone -b stable` and receive the certified Sovereign Baseline, reflecting that `main` *is* the `stable` branch.

## 2. Technical Strategy
Implement a GitHub Action workflow triggered by pushes to the `main` branch (which occurs only during formal releases). This workflow will automatically force-push the `main` branch reference to a `stable` branch. Update all documentation to instruct users to target the `stable` alias.

## 3. Implementation Details
**Workflow Structure:**
*   **File:** `.github/workflows/update-stable-alias.yml`
*   **Trigger:** `push` on branches `[main]`.
*   **Action:** Check out the repository, configure Git, and force-push the `main` commit to the `stable` branch.
*   **Permissions:** Requires `contents: write` to push the branch.

**Example Workflow Logic:**
```yaml
name: Update Stable Alias

on:
  push:
    branches:
      - main

permissions:
  contents: write

jobs:
  update-stable:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Force push to stable branch
        run: |
          git checkout -b stable
          git push -f origin stable
```

**Documentation Updates:**
*   Replace `-b main` with `-b stable` in `VDE_INSTALL.md`, `USER_GUIDE.md`, and `CONTRIBUTING.md`.
*   Refine `README.md` to reference the `stable` branch as the target for the Sovereign Baseline.

**Constant Alignment:**
*   Add `VDE_STABLE_ALIAS="stable"` to `lib/vde-constants`.

## 4. Verification Plan
1.  Create the workflow file `.github/workflows/update-stable-alias.yml`.
2.  Update all affected documentation files.
3.  Add the `VDE_STABLE_ALIAS` constant.
4.  Commit the changes to a new feature branch `feat/stable-branch-alias`.
5.  Open a PR targeting `develop` and merge it.

## 5. Compliance
- **Automation**: Resolves the need for manual maintenance of a secondary branch.
- **Security**: Relies on native GitHub Actions and explicit permissions.
- **Rule P (Sovereign Branching)**: Follows the established Git lifecycle for merging into the Anvil (`develop`).
