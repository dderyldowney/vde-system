# Surgical Realignment and Purification Plan
<!-- @shared-law (Sovereign Realignment) -->

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Perform surgical realignment and purification across multiple artifacts to ensure portability, correct tagging, rule alignment, and shibboleth hygiene.

**Architecture:** Use a sub-agent to perform batch edits across the specified file sets, ensuring adherence to positioning laws and the Mandalorian Rule Spine.

**Tech Stack:** Zsh, Python, Git.

---

### Task 1: Portability (@armor)
**Files:** `scripts/setup/*.zsh`
- [ ] **Step 1: Replace `~devuser` with `$HOME`**
  Search for `~devuser` in `scripts/setup/*.zsh` and replace with `$HOME`.

### Task 2: Tagging (@armor)
**Files:** 
- `env-files/couchdb.env`
- `env-files/jupyterlab.env`
- `env-files/mongodb.env`
- `env-files/mysql.env`
- `env-files/nginx.env`
- `env-files/postgres.env`
- `env-files/rabbitmq.env`
- `env-files/redis.env`

- [ ] **Step 1: Add tagging on line 2**
  Add `# @armor (Engine Configuration)` to line 2 of each specified `.env` file. Ensure existing content is shifted down.

### Task 3: Rule 23 Alignment (@shared-law)
**Files:**
- `plans/archive/rewrite-sovereign-artifact-set.md`
- `plans/archive/update-sovereign-artifact-set.md`

- [ ] **Step 1: Pluralize `service_port` to `service_ports`**
  In both files, replace `service_port` with `service_ports`.
- [ ] **Step 2: Update `display_name` to `display`**
  In both files, replace `display_name` with `display`.

### Task 4: Governance Tagging (@forge)
**Files:**
- `tests/features/steps/technical_integrity_steps.py`
- `tests/features/steps/vde_init_steps.py`
- `tests/features/steps/critical_steps.py`

- [ ] **Step 1: Update tags**
  Replace `# @armor (BDD Integration Logic)` (or similar) with `# @forge (Governance Step Definition)`.

### Task 5: Shibboleth Cleanup (@armor)
**File:** `scripts/vde-entrypoint.zsh`

- [ ] **Step 1: Cleanup ZSH-native shibboleth**
  Remove duplicate `local _zsh_pure=${(%):-%x}` calls and ensure exactly ONE instance exists at the top (Line 2 or 3).
  Actually, the file starts with:
  ```zsh
  #!/usr/bin/env zsh
  # @armor (Spoke Lifecycle)
  ```
  I will add it on line 3 and remove the ones at lines 44/47.

---

**Execution Handoff**
Plan complete and saved to `plans/2026-04-21-surgical-purification.md`.
Using Subagent-Driven Execution.
