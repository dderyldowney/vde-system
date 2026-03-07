# VDE Technical and Operational Audit Report

**Date:** 2026-03-07
**Spec version audited:** VDE-SPEC.md v1.5.0
**Status:** Living document — resolved issues are removed as fixed

---

## Executive Summary

Port assignments are fully consistent across all four sources (vm-types.conf, vm-types.json, configs/ssh/config, templates). The scripts/ → bin/lib/ restructure is complete. Compose files, env-files, and docker-compose.yml files are now protected from deletion by VDE scripts — only manual user action can delete them.

**Open findings:** 3 High, 7 Medium, 5 Low

---

## High

### HIGH-01: `vm_is_running` and `shutdown_vm` called but never defined

- **Category:** Technical Bug
- **Files:** `bin/remove-virtual`, `bin/shutdown-all`, `bin/nuke-vde`, `bin/uninstall-vm-type`
- **Description:** Neither `vm_is_running` nor `shutdown_vm` is defined anywhere in lib/. The actual function names are `is_vm_running` (in `lib/vde-docker`) and `stop_vm` (in `lib/vde-docker`). Under `set -e`, scripts abort mid-flow leaving containers running when the user expects them stopped.
- **Impact:** `vde remove`, `vde uninstall`, `shutdown-all`, and `nuke-vde` silently skip the stop step or abort mid-flow, leaving containers running.

---

### HIGH-02: `restart-virtual` uses legacy `docker-compose` V1 binary and unguarded `cd` in loop

- **Category:** Technical Bug
- **File:** `bin/restart-virtual:58-62`
- **Description:** The script calls `cd "$vm_dir"` at the top-level loop body (not inside a subshell), permanently changing the working directory for subsequent iterations. It then calls `docker-compose` (deprecated V1 Python binary) instead of `docker compose` (V2 Go plugin). All other lifecycle scripts use `docker compose`.
- **Impact:** `vde restart python rust go` will fail silently for all VMs on Docker Desktop (V2-only). Multi-VM restarts leave the shell in the last VM's directory.

---

### HIGH-03: `local` keyword at global script scope in `start-virtual` and `shutdown-virtual`

- **Category:** Technical Bug
- **Files:** `bin/start-virtual:77-79`, `bin/shutdown-virtual:74-76`
- **Description:** `local` is only valid inside a function body. Used at top-level script scope it is a no-op or warning in standard zsh; under strict settings it can abort the script before any VM is started or stopped.
- **Impact:** Scripts may abort at the variable declaration before doing any work under strict zsh configurations.

---

## Medium

### MED-01: `vm_exists` defined twice with incompatible semantics

- **Category:** Technical Bug
- **Files:** `lib/vde-docker:93`, `lib/vm-common:790`
- **Description:** `lib/vde-docker` defines `vm_exists` to check for compose file existence. `lib/vm-common` defines it to check for a docker-state JSON file. Because `vm-common` sources `vde-docker` after itself, the `vde-docker` version silently wins. Any code relying on the docker-state check gets the compose-file check instead.
- **Impact:** `create-virtual-for` may block re-creation of a VM whose compose file was manually deleted but whose state file persists.

---

### MED-02: `vde-log` lacks a source guard — re-sourcing resets log level

- **Category:** Technical Bug
- **File:** `lib/vde-log` (whole file)
- **Description:** Every other library has an `if [ "${_VDE_*_LOADED:-}" = "1" ]; then return 0; fi` guard. `vde-log` has none. It is sourced at least twice per `vm-common` load, resetting `_VDE_LOG_CURRENT_LEVEL` to INFO on each re-source.
- **Impact:** Any caller that sets `VDE_LOG_LEVEL=DEBUG` before sourcing vm-common will have it silently reset.

---

### MED-03: `vde-core` redefines `_assoc_get` with broken indirect expansion

- **Category:** Technical Bug
- **File:** `lib/vde-core:141-156`
- **Description:** After sourcing `vde-shell-compat` (which correctly defines `_assoc_get`), `vde-core` redefines it with a broken `${(P)array_name}[$key]` indirect expansion. This produces empty output for all keys, causing cache writes to emit empty values.
- **Impact:** VM type cache is always corrupt; every startup forces a full JSON re-parse.

---

### MED-04: `vde_get_vm_status` uses stale `-dev` container suffix

- **Category:** Consistency
- **File:** `lib/vde-commands:137-138`
- **Description:** `vde_get_vm_status` sets `container_name="${vm_name}-dev"` for language VMs. The current naming convention is `vde-<name>` with no suffix for any VM type.
- **Impact:** Library callers using `vde_get_vm_status` get `not_created` for all language VMs regardless of actual state.

---

### MED-05: Suppressed source errors mask undefined error codes in `bin/vde`

- **Category:** Technical Bug
- **File:** `bin/vde:356-360`
- **Description:** All library sources use `&>/dev/null`. If sourcing fails, `$VDE_ERR_INVALID_INPUT` is undefined. `exit $VDE_ERR_INVALID_INPUT` becomes `exit ` which exits 0, silently hiding the error.
- **Impact:** Library load failures in `bin/vde` appear as success to calling scripts and CI pipelines.

---

### MED-06: VDE-SPEC.md §3.1 shows stale `scripts/` subdirectory paths

- **Category:** Spec Mismatch
- **File:** `docs/VDE-SPEC.md:167-174`
- **Description:** The spec's §3.1 vde-constants block shows `SCRIPTS_DIR`, `TEMPLATES_DIR="${SCRIPTS_DIR}/templates"`, `DATA_DIR="${SCRIPTS_DIR}/data"`. Actual lib/vde-constants defines these as top-level directories under `VDE_ROOT_DIR` with no `scripts/` prefix.
- **Impact:** Developers implementing from the spec will build paths to non-existent directories.

---

### MED-07: `add-vm-type` writes only to `vm-types.conf`, not `vm-types.json`

- **Category:** Operational Gap
- **File:** `bin/add-vm-type:248-253`
- **Description:** `add-vm-type` appends to `data/vm-types.conf` but never updates `data/vm-types.json`. `load_vm_types` in vm-common prefers JSON when it exists. Because vm-types.json is always present, newly added types are invisible to the runtime.
- **Impact:** `vde add mytype ...` appears to succeed but `vde create mytype` immediately fails with "unknown VM type".

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
| HIGH-04 | `bin/add-vm-type` heredoc now uses `${VDE_SSH_IDENTITY}` and `${VDE_SSH_KNOWN_HOSTS}` variables instead of hardcoded absolute paths |
