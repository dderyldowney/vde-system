# VDE-SPEC v2.0.3 (Absolute)

## VERSION HISTORY
| Version | Date | Changes |
| :--- | :--- | :--- |
| 1.7.2 | 2026-04-02 | Last modular/template-based version. |
| 2.0.0 | 2026-04-03 | Fundamental rewrite. Established Build-Time Only (BTO) mandate. |
| 2.0.1 | 2026-04-03 | Fixed Docker ENV syntax and aligned CLI headers. |
| 2.0.3 | 2026-04-03 | Aligned SSH identity naming (vde_student) across the bridge. |

**Status:** AUTHORITATIVE  
**Last Updated:** 2026-04-03T22:55:00Z  

## 1. Absolute Mandates

- **Born Ready (BTO)**: Every jail MUST be fully functional at the moment of image creation. No `apt-get` or network-dependent configurations are permitted during container runtime.
- **Zero-Friction On-Ramp**: Students must be able to launch any environment with a single command: `vde start <lang>`.
- **ZSH-ONLY**: All CLI tools, libraries, and jail shells MUST use `#!/usr/bin/env zsh`.
- **Absolute Portability**: Once built, images must function identically without requiring internet access for setup.

## 2. Directory Structure

- `bin/`: CLI entry points (`vde`, `vde-bootstrap`).
- `lib/`: Sourced ZSH libraries.
- `configs/docker/`: Contains the Hub (`vde-base.Dockerfile`) and the Spoke (`vde-lang.Dockerfile`).
- `projects/`: Student workspace mounted from the host.
- `.cache/`: Persistent tool caches (pip, npm, cargo).

## 3. Universal Agent Protocol (UAP)

1. **Startup**: Verify local environment and current version (v2.0.3).
2. **Planning**: Design a TDD strategy with explicit failing tests.
3. **Implementation**: Execute changes under the supervision of `bin/vde-enforce-uap.zsh`.
4. **Audit**: Confirm that the "Born Ready" requirement is met.

