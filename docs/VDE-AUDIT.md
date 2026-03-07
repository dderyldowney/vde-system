# VDE Technical and Operational Audit Report

**Date:** 2026-03-07
**Spec version audited:** VDE-SPEC.md v1.5.0
**Status:** Living document — resolved issues are removed as fixed

---

## Executive Summary

Port assignments are fully consistent across all four sources (vm-types.conf, vm-types.json, configs/ssh/config, templates). The scripts/ → bin/lib/ restructure is complete. Compose files, env-files, and docker-compose.yml files are now protected from deletion by VDE scripts — only manual user action can delete them.

**Open findings:** 0 High, 0 Medium, 5 Low

---



## Low

### LOW-01: Fallback `VDE_ROOT_DIR` over-ascends in `vde-core`, `vde-docker`, `vde-templates`

- **Category:** Technical Bug
- **Files:** `lib/vde-core:42`, `lib/vde-docker:34`, `lib/vde-templates:29`
- **Description:** Fallback uses `$(dirname "$_VDE_*_SCRIPT_PATH")/../..` but these files live directly under `lib/` — one `..` reaches VDE root; two `../..` go above it.
- **Impact:** Masked in practice because bin/ scripts pre-set `VDE_ROOT_DIR`. Direct library sourcing would resolve paths above the repo.

---

### LOW-02: `templates/ssh-entry.txt` missing `LogLevel ERROR`

- **Category:** Consistency
- **File:** `templates/ssh-entry.txt`
- **Description:** The template used by `lib/vde-templates` does not include `LogLevel ERROR` or an absolute `UserKnownHostsFile` path. `configs/ssh/config` (authoritative) includes both on every host block.
- **Impact:** Template-generated SSH entries produce verbose output on each connection; `~/.ssh/vde/config` diverges from `configs/ssh/config`.

---

### LOW-03: `create-virtual-for` type-check asymmetry (`"service"` vs `"lang"`)

- **Category:** Consistency
- **File:** `bin/create-virtual-for:206`
- **Description:** Template selection checks `if [[ "$_vm_type" == "lang" ]]`; the subsequent multi-port expansion checks `if [[ "$_vm_type" == "service" ]]`. Complementary but asymmetric — fragile if a third VM type is ever added.
- **Impact:** No current bug; maintenance hazard.

---

### LOW-04: `vde --version` lists incomplete library set and non-semantic version

- **Category:** Consistency
- **File:** `bin/vde:161-172`
- **Description:** `vde_show_version` prints 6 of the ~14 loaded libraries and shows version `"1.0.0 (Stage 7 - Architectural Enhancements)"`.
- **Impact:** Misleads users and tooling about the actual library surface and project version.

---

### LOW-05: `compose-language.yml` template missing `vde.type`/`vde.name` labels

- **Category:** Spec Mismatch
- **File:** `templates/compose-language.yml`
- **Description:** `compose-service.yml` includes `vde.type` and `vde.name` labels. `compose-language.yml` has no `labels:` section at all.
- **Impact:** Language containers cannot be filtered by `docker ps --filter label=vde.type`; any label-based tooling misses all language VMs.

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
| `vde create` | **Broken for new types** | MED-07 |
| `vde start` | OK | — |
| `vde stop` | OK | — |
| `vde restart` | **Broken** | HIGH-02 |
| `vde remove` | **Broken** | HIGH-01 |
| `vde uninstall` | **Broken** | HIGH-01 |
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
