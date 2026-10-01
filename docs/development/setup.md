# VDE Development Guide
<!-- @forge (AI Governance) -->

**Version:** 1.5.6 (The Sovereign Baseline)

## Code Style

- **All shell scripts must use zsh** (`#!/usr/bin/env zsh`)
  - Zsh version: 5.0 or later required.
  - `bash` usage is strictly prohibited (Mandate C).
- **Indentation**: 2 spaces.
- **Mandate 24 (Tagging)**: Every file MUST be tagged as `@armor`, `@forge`, or `@shared-law` on Line 2 or 3.

## Architecture: The Two Projects

1.  **The Armor (`@armor`)**: The student-facing product. Must be AI-blind and depend strictly on the Tetrad.
2.  **The Forge (`@forge`)**: The governance and auditing system. Manages the lifecycle and AI integration.

### Libraries (`lib/`)

All VDE logic is modular. For detailed function references, see `docs/api/library-api.md`.

| Library | Domain | Purpose |
|---------|--------|---------|
| **vde-core** | `@armor` | Essential initialization and JSON queries. |
| **vm-common** | `@armor` | The primary orchestrator for Spoke lifecycles. |
| **vde-ssh** | `@armor` | Transversal Bridge management. |
| **vde-enforce-uap** | `@forge` | The Rule Spine enforcement engine. |

## Testing

Measured on 2026-09-30 at commit `6308fe33` (1.5.6; Linux, zsh 5.9, Python 3.12, Docker 29.8.2). The full BDD suite is **not** at 100%; the failing scenarios and their causes are listed in [Testing](testing.md).

- **BDD Framework**: Behave (Python).
- **Full suite** (`behave tests/features/`): 116 scenarios, 720 steps. **107 scenarios passed, 9 failed**; 638 steps passed, 9 failed, 73 skipped.
- **Proof of Life** (`proof-of-life-the-contract.feature`): 6 of 6 scenarios passed.
- **Sovereign Tests** (`./tests/run-sovereign-tests.zsh`, the CI-safe subset): 12 of 12 suites passed when the Python `jsonschema` module was available, 11 of 12 without it (tracked in #492).
- **Protocol**: No functional code is committed without a failing test (Trial of the Gauntlet).

### Test Commands
```zsh
vde health              # Fast Spine Check
make test               # Full suite (Unit + BDD)
behave tests/features/  # BDD only
```

## Security

- **Identity**: Spokes run as `devuser`. The Hub uses the `vde_student` key for authentication.
- **Agent Forwarding**: Authentication is proxied via `socat`; private keys never enter the Spoke.
- **Sanitization**: All user input is normalized via `vde-naming` to prevent path traversal.

---

## Development Workflows (Examples)

### Example: Python + PostgreSQL Stack

```zsh
# 1. Forge the tech stack
vde start python postgres

# 2. Enter as devuser
vde enter python

# 3. Work in the synced workspace
cd ~/workspace
# (Syncs to projects/python on your Hub)

# 4. Connect to the database via DNS
psql -h vde-postgres -U devuser
```

### Daily Rhythm

1. **Morning**: `vde start python postgres`
2. **During**: `vde enter python` -> code in `~/workspace/`
3. **Evening**: `vde stop all`

---

[← Back to README](../../README.md)
**This is the Way.**
