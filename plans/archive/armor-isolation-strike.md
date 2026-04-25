# Armor Isolation Strike Implementation Plan
<!-- @shared-law (Forge Component) -->

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Surgically realign all runtime-critical artifacts into the `@armor` (Project 1) domain, establishing the definitive set of files and documents required for the VDE engine to operate in full isolation.

**Architecture:** We will move all core binaries, libraries, registry files, and student-facing documentation from `@shared-law` or `@forge` to `@armor`. This ensures that Project 1 is 100% self-contained for use on a "naked" machine.

**Tech Stack:** ZSH, Markdown, Python

---

### Task 1: Realign Core Binaries & Discovery (@armor)

**Files:**
- `bin/vde-init`, `bin/vde-bootstrap`, `bin/vde-spine-check.zsh`, `bin/vde-check-tetrad.zsh`
- `bin/list-vms`, `bin/vde-info`

- [ ] **Step 1: Retag Binaries**
Update tags on line 2:
- `bin/vde-init`: `# @armor (Engine Ignition Ritual)`
- `bin/vde-bootstrap`: `# @armor (Foundation Bootstrap)`
- `bin/vde-spine-check.zsh`: `# @armor (Technical Integrity Gate)`
- `bin/vde-check-tetrad.zsh`: `# @armor (Technical Integrity Gate)`
- `bin/list-vms`: `# @armor (Resource Discovery)`
- `bin/vde-info`: `# @armor (System Intel)`

- [ ] **Step 2: Commit**
```bash
git add bin/
git commit -m "refactor(armor): realign core binaries to Project 1"
```

### Task 2: Realign System Libraries (@armor)

**Files:**
- `lib/vde-log`, `lib/vde-errors`, `lib/vde-security`, `lib/vde-templates`, `lib/vde-docker-state`, `lib/vde-root`, `lib/vde-root-guard`

- [ ] **Step 1: Retag Libraries**
Update tags on line 2:
- `lib/vde-log`: `# @armor (Logging Engine)`
- `lib/vde-errors`: `# @armor (Error Handling)`
- `lib/vde-security`: `# @armor (Security Guard)`
- `lib/vde-templates`: `# @armor (Hydration Blueprints)`
- `lib/vde-docker-state`: `# @armor (Runtime State Management)`
- `lib/vde-root`: `# @armor (Engine Pathing Core)`
- `lib/vde-root-guard`: `# @armor (Engine Pathing Safeguard)`

- [ ] **Step 2: Commit**
```bash
git add lib/
git commit -m "refactor(armor): realign system libraries to Project 1"
```

### Task 3: Realign The Registry & Metadata (@armor)

**Files:**
- `data/vm-types.json`, `data/vm-types.conf`, `data/vm-types.schema.json`
- `data/README.md`
- `env-files/README.md`

- [ ] **Step 1: Retag Data Registry**
Update tags on line 2:
- `data/vm-types.json`: `"@armor": "(Beskar Registry DNA)",`
- `data/vm-types.conf`: `# @armor (Beskar Registry DNA)`
- `data/vm-types.schema.json`: `"@armor": "(Beskar Registry DNA)",`
- `data/README.md`: `<!-- @armor (Registry Documentation) -->`
- `env-files/README.md`: `<!-- @armor (Hydration Documentation) -->`

- [ ] **Step 2: Commit**
```bash
git add data/ env-files/
git commit -m "refactor(armor): realign registry and data metadata to Project 1"
```

### Task 4: Realign Product Documentation (@armor)

**Files:**
- `SECURITY.md`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`
- `VDE_PROTOCOL.md`, `docs/beskar-map.md`

- [ ] **Step 1: Retag Product Docs**
Update tags on line 2:
- `SECURITY.md`: `<!-- @armor (Product Security Policy) -->`
- `CODE_OF_CONDUCT.md`: `<!-- @armor (Product Ethics) -->`
- `CONTRIBUTING.md`: `<!-- @armor (Development Onboarding) -->`
- `VDE_PROTOCOL.md`: `<!-- @armor (Operational Doctrine) -->`
- `docs/beskar-map.md`: `<!-- @armor (Product Map) -->`

- [ ] **Step 2: Commit**
```bash
git add SECURITY.md CODE_OF_CONDUCT.md CONTRIBUTING.md VDE_PROTOCOL.md docs/beskar-map.md
git commit -m "refactor(armor): realign product documentation to Project 1"
```

### Task 5: Final Verification & Audit (@forge)

- [ ] **Step 1: Run Sovereign Audit**
```bash
bin/vde-enforce-uap.zsh
```

- [ ] **Step 2: Isolation Check**
Verify that no `@shared-law` or `@forge` artifacts are required for a standard `vde start python` lifecycle.
