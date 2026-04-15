# Set Default Branch to Develop Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Change the GitHub repository's default branch to `develop` to natively support issue auto-closure upon PR merge, and update the documentation to ensure end-users clone the stable `main` branch.

**Architecture:** Modifying GitHub repository settings via the `gh` CLI and updating Markdown documentation files (`VDE_INSTALL.md`, `USER_GUIDE.md`, `CONTRIBUTING.md`).

**Tech Stack:** GitHub CLI (`gh`), Markdown.

---

### Task 1: Update Documentation

**Files:**
- Modify: `VDE_INSTALL.md`
- Modify: `USER_GUIDE.md`
- Modify: `CONTRIBUTING.md`

- [ ] **Step 1: Update VDE_INSTALL.md**

Modify the cloning instructions in `VDE_INSTALL.md` to specify the `main` branch:

```bash
git clone -b main https://github.com/dderyldowney/vde-system.git ~/vde
```

- [ ] **Step 2: Update USER_GUIDE.md**

Modify the cloning instructions under "Final Step: Clone & Init" in `USER_GUIDE.md` to specify the `main` branch:

```bash
git clone -b main https://github.com/dderyldowney/vde-system.git ~/vde
```

- [ ] **Step 3: Update CONTRIBUTING.md**

Modify the cloning instructions in `CONTRIBUTING.md` to specify the `main` branch:

```bash
git clone -b main https://github.com/YOUR_USERNAME/vde-system.git
```

- [ ] **Step 4: Commit documentation updates**

```bash
git add VDE_INSTALL.md USER_GUIDE.md CONTRIBUTING.md
git commit -m "docs(core): update clone instructions to target main branch"
git push origin develop
```

---

### Task 2: Change Default Branch to Develop

- [ ] **Step 1: Change the default branch via GitHub CLI**

Execute the following command to update the repository settings:

```bash
gh repo edit --default-branch develop
```

- [ ] **Step 2: Verify the change**

Execute the following command and ensure the output is `develop`:

```bash
gh repo view --json defaultBranchRef -q .defaultBranchRef.name
```