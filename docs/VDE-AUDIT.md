# VDE Technical and Operational Audit Report

**Date:** 2026-03-07
**Spec version audited:** VDE-SPEC.md v1.5.0
**Status:** Living document — resolved issues are removed as fixed

---

## Executive Summary

Port assignments are fully consistent across all four sources (vm-types.conf, vm-types.json, configs/ssh/config, templates). The scripts/ → bin/lib/ restructure is complete. Compose files, env-files, and docker-compose.yml files are now protected from deletion by VDE scripts — only manual user action can delete them.

**Open findings:** 0 High, 0 Medium, 0 Low

---




## Port Consistency Verification (PASSED)

All four sources are consistent. Sample cross-check:

| VM | vm-types.conf | vm-types.json | configs/ssh/config | Template |
|----|--------------|---------------|-------------------|----------|
| vde-python | 2213 | 2213 | 2213 | `{{SSH_PORT}}` |
| vde-rust | 2216 | 2216 | 2216 | `{{SSH_PORT}}` |
| vde-postgres | 2404 | 2404 | 2404 | `{{SSH_PORT}}` |
| vde-redis | 2406 | 2406 | 2406 | `{{SSH_PORT}}` |

---

## VM Lifecycle Gap Summary

| Stage | Status | Blocker |
|-------|--------|---------|
| `vde create` | OK | — |
| `vde start` | OK | — |
| `vde stop` | OK | — |
| `vde restart` | OK | — |
| `vde remove` | OK | — |
| `vde uninstall` | OK | — |
| `vde cleanup-ports` | OK | Fixed (CRIT-01) |

---

## Resolved (removed from open findings)

| ID | Resolution |
|----|-----------|
| CRIT-01 | `bin/cleanup-ports` created — removes stale port-registry entries for VMs not in vm-types.conf |
| HIGH-01 | Fixed undefined function calls in `bin/remove-virtual`, `bin/shutdown-all`, `bin/nuke-vde`, `bin/uninstall-vm-type` |
| HIGH-02 | Fixed `bin/restart-virtual` to use docker compose V2 and safe subshells |
| HIGH-03 | Removed global `local` declarations from `bin/start-virtual` and `bin/shutdown-virtual` |
| HIGH-04 | `bin/add-vm-type` heredoc now uses `${VDE_SSH_IDENTITY}` and `${VDE_SSH_KNOWN_HOSTS}` variables instead of hardcoded absolute paths |
| MED-01 | Removed redundant `vm_exists` from `lib/vde-docker` |
| MED-02 | Added source guard to `lib/vde-log` |
| MED-03 | Removed incorrect associative array functions from `lib/vde-core` |
| MED-04 | Fixed container naming logic in `vde-commands:vde_get_vm_status` |
| MED-05 | Replaced silent failures with explicit fail on library load failure in `bin/vde` |
| MED-06 | Fixed stale directory paths in `docs/VDE-SPEC.md:3.1` |
| MED-07 | Updated `add-vm-type` to inject the new VM type directly into `vm-types.json` |
| LOW-01 | Fixed fallback `VDE_ROOT_DIR` in `vde-core`, `vde-docker`, `vde-templates` |
| LOW-02 | Added `LogLevel ERROR` and absolute `UserKnownHostsFile` to `templates/ssh-entry.txt` |
| LOW-03 | Fixed type-check asymmetry in `bin/create-virtual-for` |
| LOW-04 | Updated `vde --version` library list and semantic version to 1.5.0 |
| LOW-05 | Added `vde.type` and `vde.name` labels to `templates/compose-language.yml` |
