# Remediate Issue #193 - Remove hardcoded password from JupyterLab Init implementation Plan
<!-- @shared-law (Forge Component) -->

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the hardcoded password fallback from the `DATABASE_URL` export in `scripts/setup/jupyterlab-init.zsh`.

**Architecture:** Update the ZSH setup script to use `${POSTGRES_DEV_PASSWORD}` directly without the `:-vde_dev_pass` default expansion.

**Tech Stack:** ZSH

---

### Task 1: Update scripts/setup/jupyterlab-init.zsh

**Files:**
- Modify: `scripts/setup/jupyterlab-init.zsh`

- [ ] **Step 1: Perform dry-run replacement to verify targeting**

I will use `grep_search` again to ensure I have the exact string for replacement.

- [ ] **Step 2: Apply the fix**

Replace:
`    echo "export DATABASE_URL=postgresql://devuser:\${POSTGRES_DEV_PASSWORD:-vde_dev_pass}@vde-postgres:5432/postgres_dev_db" >> "${_zshenv}"`
With:
`    echo "export DATABASE_URL=postgresql://devuser:\${POSTGRES_DEV_PASSWORD}@vde-postgres:5432/postgres_dev_db" >> "${_zshenv}"`

- [ ] **Step 3: Verify the change**

Run: `grep "DATABASE_URL" scripts/setup/jupyterlab-init.zsh`
Expected: `    echo "export DATABASE_URL=postgresql://devuser:\${POSTGRES_DEV_PASSWORD}@vde-postgres:5432/postgres_dev_db" >> "${_zshenv}"`

- [ ] **Step 4: Commit the change**

```bash
git add scripts/setup/jupyterlab-init.zsh
git commit -m "fix(security): remove hardcoded password from jupyterlab-init.zsh"
```
