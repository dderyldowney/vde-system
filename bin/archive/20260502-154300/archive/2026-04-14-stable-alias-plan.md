# Automated 'stable' Alias for Main Branch Implementation Plan
<!-- @shared-law (Forge Component) -->

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Support `stable` as an alias for the `main` branch via GitHub Actions and documentation updates.

**Architecture:** A GitHub Action triggers on `main` branch pushes to automatically force-push to `stable`. Documentation instructs users to `git clone -b stable`. `lib/vde-constants` introduces `VDE_STABLE_ALIAS`.

**Tech Stack:** GitHub Actions, Markdown, ZSH.

---

### Task 1: Create GitHub Action for Stable Alias

**Files:**
- Create: `.github/workflows/update-stable-alias.yml`

- [ ] **Step 1: Write the workflow file**

Create `.github/workflows/update-stable-alias.yml` with the following content:

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
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Force push to stable branch
        run: |
          git checkout -b stable
          git push -f origin stable
```

- [ ] **Step 2: Commit the workflow file**

```bash
git add .github/workflows/update-stable-alias.yml
git commit -m "feat(ci): automate stable alias update on main branch push"
```

---

### Task 2: Update Documentation and Constants

**Files:**
- Modify: `VDE_INSTALL.md`
- Modify: `USER_GUIDE.md`
- Modify: `CONTRIBUTING.md`
- Modify: `README.md`
- Modify: `lib/vde-constants`
- Modify: `tests/features/core-infrastructure/proof-of-life-the-contract.feature`
- Modify: `tests/features/core-infrastructure/gateway-pillars.feature`

- [ ] **Step 1: Update VDE_INSTALL.md**
Change `git clone -b main` to `git clone -b stable`.

- [ ] **Step 2: Update USER_GUIDE.md**
Change `git clone -b main` to `git clone -b stable`.

- [ ] **Step 3: Update CONTRIBUTING.md**
Change `git clone -b main` to `git clone -b stable`.

- [ ] **Step 4: Update README.md**
Change mentions of cloning `main` to `stable`.

- [ ] **Step 5: Update lib/vde-constants**
Add `VDE_STABLE_ALIAS="stable"` near `VDE_PRODUCTION_BRANCH` and add it to the readonly list.

- [ ] **Step 6: Update Core Infrastructure Tests**
Change `And the file "VDE_INSTALL.md" should contain "git clone -b main"` to `"git clone -b stable"` in both `proof-of-life-the-contract.feature` and `gateway-pillars.feature`.

- [ ] **Step 7: Commit the updates**

```bash
git add VDE_INSTALL.md USER_GUIDE.md CONTRIBUTING.md README.md lib/vde-constants tests/
git commit -m "docs(core): update clone instructions to target stable alias"
```

---

### Task 3: Verify the Workflow Locally

- [ ] **Step 1: Run tests**
Execute `python3 -m behave tests/features/core-infrastructure/gateway-pillars.feature` to ensure the documentation validation passes.

- [ ] **Step 2: Push changes**
```bash
git push origin <current-branch>
```
