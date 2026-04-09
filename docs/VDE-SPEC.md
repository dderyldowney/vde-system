# VDE-SPEC v2.2.0 (Absolute)

## VERSION HISTORY
| Version | Date       | Changes                                                                 |
| :---    | :---       | :---                                                                    |
| 2.2.0   | 2026-04-08 | Hardened Sovereign Bridges (Docker/SSH Socat Proxy) and certified 100% GREEN high-fidelity test suite. |
| 2.1.0   | 2026-04-07 | Completed Sovereign Audit; pruned 24k lines of redundant tests.         |
| 2.0.3   | 2026-04-03 | Aligned SSH identity naming (vde_student) across the bridge.            |
| 2.0.4   | 2026-04-04 | Implemented Ignition Sync, Universal Script Parity (USP), and 8-Field Registry Standard. |
| 2.0.5   | 2026-04-04 | Version bump to 2.0.5.                                                  |
| 2.0.6   | 2026-04-05 | Implemented Fleet Strike (3-VM Concurrent Limit).                       |
| 2.0.7   | 2026-04-07 | Codified Section 10: THE SEEKER’S RECON (The Verification Law).         |
| 2.0.8   | 2026-04-07 | Codified Section 11: THE ARCHIVIST’S INTEL (The Researcher Law).        |
| 2.0.9   | 2026-04-07 | Refined Section 11: Real-time intelligence and physical verification.   |
| 2.1.0   | 2026-04-07 | Sovereign Ecosystem: Docker Socket Sovereignty and SSH Agent Trust Bridge. |

**Status:** AUTHORITATIVE  
**Last Updated:** 2026-04-07T23:55:00Z  

## 1. Absolute Mandates

- **Born Ready (BTO)**: Every jail MUST be fully functional at the moment of image creation. No network-dependent configurations are permitted during container runtime.
- **Universal Script Parity (USP)**: Every VM entry MUST point to a setup script at `scripts/setup/<alias>-init.zsh`. Inline logic is strictly prohibited.
- **Ignition Sync (Pre-Flight)**: The CLI MUST perform a timestamp audit at ignition. If source files (`.conf`, `.json`) are newer than the cache, a re-smelt is mandatory.
- **8-Field Standard**: Data integrity is maintained via a strict 8-field registry layout: `type|name|aliases|display|pkgs|custom_cmd|env|ports`.
- **ZSH-ONLY**: All CLI tools, libraries, and jail shells MUST use `#!/usr/bin/env zsh`.
- **Absolute Portability**: Images must function identically without requiring internet access for setup once built.
- **Docker Socket Sovereignty**: Containers MUST have dynamic non-root access to the host Docker daemon.
- **SSH Agent Trust Bridge**: Host SSH identities MUST be forwarded to guest VMs via secure agent bridging.

## 2. Directory Structure

- `bin/`: CLI entry points (`vde`, `vde-bootstrap`).
- `lib/`: Sourced ZSH libraries.
- `data/`: The Beskar Vault (`vm-types.conf`, `vm-types.json`).
- `scripts/setup/`: USP-compliant initialization rituals.
- `configs/docker/`: The Hub (`vde-base.Dockerfile`) and Spoke templates.
- `projects/`: Student workspace mounted from host.
- `.cache/`: Persistent tool caches and VM registry cache.

## 3. Universal Agent Protocol (UAP)

1. **Startup**: Verify local environment, version (v2.1.0), and execute Ignition Sync.
2. **Planning**: Design a TDD strategy with explicit failing tests.
3. **Implementation**: Execute changes under `bin/vde-enforce-uap.zsh` using local, unique-prefixed variables.
4. **Audit**: Confirm USP compliance and "Born Ready" status.
5. **Research**: When the path is obscured or platform quirks arise, dispatch the Researcher for physical verification.
