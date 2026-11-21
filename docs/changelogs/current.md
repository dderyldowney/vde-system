# VDE Release Archive
<!-- @shared-law (Sovereign Chronicle) -->

This file tracks the evolution of the Virtual Development Environment. For detailed technical changes and empirical certifications, refer to the individual release records in `docs/releases/`.

## 🟢 Latest Sovereign Baseline: [1.5.7](../releases/1.5.7.md) (2026-11-21)

---
## 🔨 Forged on develop and shipped in 1.5.7

These changes were forged on `develop` and are part of the 1.5.7 Sovereign Baseline (full record: [1.5.7](../releases/1.5.7.md)). New work lands under a fresh "On The Anvil" heading.

- **Configurable Projects Directory** (Signet [#543](https://github.com/dderyldowney/VDE-SYSTEM/issues/543)): The projects base is now student-configurable instead of fixed. Chosen at onboarding, it defaults to `${VDE_ROOT_DIR}/projects` and is overridable via `vde init --projects-dir <path>` or an exported `VDE_PROJECTS_DIR`, persisted as the absolute `.env` key `VDE_PROJECTS_DIR`. The base may live anywhere the student controls, inside or outside the repo. A new `vde set-projects-dir <new-path>` command safely re-points the base after onboarding, MOVING existing alias folders (skipping collisions, never overwriting or deleting), updating `.env`, and regenerating configs with no rebuild.
- **`vde nuke` Data Integrity** (Signet [#543](https://github.com/dderyldowney/VDE-SYSTEM/issues/543)): The teardown ritual now **preserves** the projects base and the service database `data/` directory (in-tree or external) and **offers to move** both to safety before proceeding, removing only VDE's own operational state.

---
## 📦 Release History

- [1.5.7](../releases/1.5.7.md)
- [1.5.6](../releases/1.5.6.md)
- [1.5.5] (./1.5.5.md)
- [1.5.3] (./1.5.3.md)
- [1.5.2] (./1.5.2.md)
- [1.5.1] (./1.5.1.md)
- [1.5.0] (./1.5.0.md)
- [1.4.1] (./1.4.1.md)
- [1.4.0] (./1.4.0.md)
- [1.3.7] (./1.3.7.md)
