# Armor Runtime Realignment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Surgically realign artifacts currently tagged as `@shared-law` into their proper Project domains: `@armor` for the pure runtime contract and `@forge` for governance verification (BDD tests).

**Architecture:** We will retag the core engine intelligence and registry as `@armor` (Project 1) to establish a "Guaranteed-to-Run" bundle. Conversely, we will retag all BDD feature files and step definitions as `@forge` (Project 2), as they are exclusively part of the development/governance rig.

**Tech Stack:** ZSH, Markdown, Python

---

### Task 1: Realize the Pure Armor Runtime (@armor)

**Files:**
- Modify: `lib/vde-core`, `lib/vde-constants`, `lib/vde-shell-compat`, `lib/vm-common`
- Modify: `data/vm-types.json`, `data/vm-types.conf`, `data/vm-types.schema.json`
- Modify: `bin/vde-init`, `bin/vde-bootstrap`, `bin/vde-spine-check.zsh`, `bin/vde-check-tetrad.zsh`
- Modify: `.env.template`, `configs/ssh/config`

- [ ] **Step 1: Retag Core Libraries**
Update the tags on line 2/3:
- `lib/vde-core`: `@armor (Engine Core)`
- `lib/vde-constants`: `@armor (Engine Constants)`
- `lib/vde-shell-compat`: `@armor (Shell Abstraction)`
- `lib/vm-common`: `@armor (Registry Logic)`

- [ ] **Step 2: Retag Registry & Blueprints**
- `data/vm-types.json`: `"@armor": "(Beskar Registry)",`
- `data/vm-types.conf`: `# @armor (Beskar Registry Source)`
- `data/vm-types.schema.json`: `"@armor": "(Beskar Registry Schema)",`
- `.env.template`: `# @armor (Environment Blueprint)`
- `configs/ssh/config`: `# @armor (Bridge Blueprint)`

- [ ] **Step 3: Retag Ignition Binaries**
- `bin/vde-init`: `# @armor (Engine Ignition)`
- `bin/vde-bootstrap`: `# @armor (Bootstrap Ritual)`
- `bin/vde-spine-check.zsh`: `# @armor (Technical Gate)`
- `bin/vde-check-tetrad.zsh`: `# @armor (Technical Gate)`

- [ ] **Step 4: Commit**
```bash
git add lib/ data/ bin/ configs/ .env.template
git commit -m "refactor(armor): realign core engine artifacts to Project 1"
```

### Task 2: Realize Forge Governance Verification (@forge)

**Files:**
- Modify: `tests/features/core-infrastructure/*.feature`
- Modify: `tests/features/steps/concurrency_queue_steps.py`, `tests/features/steps/tech_stack_steps.py`, `tests/features/steps/usp_alias_steps.py`, `tests/features/steps/usp_steps.py`

- [ ] **Step 1: Retag BDD Feature Files**
For every `.feature` file in `tests/features/core-infrastructure/`, update the tag:
`# @forge (Governance Verification)`

- [ ] **Step 2: Retag BDD Step Definitions**
For the identified `.py` files, update the tag on line 2:
`# @forge (Governance Step Definition)`

- [ ] **Step 3: Commit**
```bash
git add tests/features/
git commit -m "refactor(forge): realign BDD verification tests to Project 2"
```

### Task 3: Update the Gospel (@shared-law)

**Files:**
- Modify: `docs/SOVEREIGN_CHARTER.md`, `docs/VDE-SPEC.md`

- [ ] **Step 1: Update Charter & SPEC**
Synchronize the hierarchical component outlines in both documents to reflect that the core libraries and registry now belong to **Project 1 (@armor)** and BD tests belong to **Project 2 (@forge)**.

- [ ] **Step 2: Commit**
```bash
git add docs/
git commit -m "docs(shared-law): synchronize Gospel with architectural realignment"
```

### Task 4: Final Audit

- [ ] **Step 1: Run Sovereign Audit**
```bash
bin/vde-enforce-uap.zsh
```

- [ ] **Step 2: Verification**
Verify that `lib/vde-core` is correctly tagged as `@armor` and `tests/features/core-infrastructure/system-spine.feature` is correctly tagged as `@forge`.
