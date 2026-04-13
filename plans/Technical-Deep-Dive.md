# VDE: Technical Deep-Dive (1.3.0 Sovereign)

## 1. The Rule Spine (UAP Enforcement)

The Virtual Development Environment is governed by the **Universal Agent Protocol (UAP)**, enforced by `bin/vde-enforce-uap.zsh`. This sentinel script ensures every action adheres to the **Resol’nare** (Supreme Prohibitions).

### Core Enforcement Mandates:
- **ZSH Native Sovereignty**: Detects "Fake ZSH" by verifying the use of native parameter expansion `${(` and associative arrays. Usage of `bash` or 0-indexed arrays is a Class-A violation.
- **Shebang Purity**: Recursively audits `bin/`, `lib/`, and `scripts/` to ensure `#!/usr/bin/env zsh` is the universal entry point.
- **Ghost Detection**: Monitors for "Ghost Zones" (unauthorized root directories) and ensures build-time artifacts (`apt` lists) are purged.
- **Supervised Execution**: Every CLI strike is wrapped in the Enforcer to maintain architectural integrity.

## 2. The Ignition Pipeline (The Smelting Ritual)

VDE employs a three-tier reactive synchronization pipeline to transform human-readable intent into high-performance runtime data.

1.  **The Source (`data/vm-types.conf`)**: The human-editable flat-file registry following the strict 8-field standard: `type|name|aliases|display_name|pkgs|custom_cmd|service_port|ssh_port`.
2.  **The Registry (`data/vm-types.json`)**: The `vde_translate_conf_to_json` ritual (Rule G) hammers the `.conf` into a structured JSON archive using pure ZSH parsing to avoid host-level `jq` dependencies.
3.  **The Cache (`.cache/vm-core.cache`)**: The `vde_core_save_cache` process generates a ZSH-native associative array (`VDE_CORE_VM_TYPE`, `VDE_CORE_VM_ALIASES`, `VDE_CORE_VM_DISPLAY`) for O(1) runtime lookup.
4.  **Ignition Sync**: The `bin/vde` orchestrator performs a timestamp audit. If source files are newer than the cache, a re-smelt is triggered automatically before Spoke ignition.

## 3. Concurrency & Atomic Stewardship

VDE manages high-concurrency operations (parallel builds and mass ignitions) via the **Lock-Queue Model** (Phase 25).

### FIFO Ticket-Based Locking (`lib/vm-lock`)
VDE uses a deterministic sequencing mechanism to prevent "Thundering Herd" race conditions:
- **Ticket Registration**: Every process requesting a lock creates a unique "Ticket" file in `${lock_file}.queue/` using `${EPOCHREALTIME}-$$`.
- **Oldest Ticket Priority**: The `claim_lock` function enforces FIFO order—only the process with the oldest numerically sorted ticket file may proceed.
- **The Atomic Gate**: Uses kernel-level `mkdir` atomicity to claim the final directory-based lock (`${lock_file}`).
- **Ownership Proof**: Once claimed, the lock directory contains a `pid` file recording `PID:PGID:TIMESTAMP` for transparent monitoring and crash recovery.
- **Paths**: Primary locks reside in `${VDE_ROOT_DIR}/.locks/vms/` and `global-config.lock`.

### Port Stewardship (`lib/vde-docker`)
To prevent double-allocation during parallel strikes, VDE reserves ports using `${VDE_ROOT_DIR}/.locks/ports/port-<number>.lock` markers. No Spoke is assigned a port until:
1.  **Kernel Referee**: The port lock directory is successfully created.
2.  **The Seeker's Recon**: A physical diagnostic handshake (`docker run --rm`) verifies the port is not occupied by host-level "Scavenger" processes.
3.  **Hub Registry Check**: Verification that the port isn't pre-defined in the Beskar Source.

## 4. Universal Script Parity (USP)

VDE decouples environment hydration from Dockerfile complexity through USP rituals stored in `scripts/setup/`.

- **Hydration Ritual**: Every Spoke entry MUST point to a setup script (`<alias>-init.zsh`).
- **Asynchronous Ignition**: Service Spokes register background ignition hooks in `/usr/local/bin/vde-spoke-ignition.zsh`, detaching service availability from the primary SSH gate.
- **Born Ready (BTO)**: All hydration happens during the `docker build` phase. Runtime `apt` calls are strictly forbidden to ensure images are immutable and portable.

## 5. Security & Infrastructure Bridge

### Identity Isolation (`lib/vde-security`)
- **Key Isolation**: The `vde_student` identity is confined to `${VDE_SSH_DIR}` (`~/.ssh/vde/`).
- **Permission Enforcement**: `vde_security_enforce_permissions` applies recursive `700` to sensitive directories (`data/`, `logs/`, `.cache/`, `.locks/`) and `600` to identity/env files.
- **Network Segmentation**: `vde-net` (bridge) ensures container isolation with `vde.managed=true` labeling.

### Sovereign Bridge & Sanitization
- **Command Sanitization**: VDE has purged all `eval` usage in primary sinks. Commands are executed via native ZSH arrays `"${cmd[@]}"` to neutralize injection vectors.
- **SSH Agent Trust**: Forwarding is established via `socat` UNIX-proxying in the entrypoint, mapping the host socket to `/home/devuser/.ssh/vde/agent.sock` inside the jail.
- **Socket Sovereignty**: The Docker socket is bridged via dynamic GID mapping and secure `chmod 666` within the isolated `vde-net` environment.

## 6. Deterministic Error Engine (Phase 26)

All VDE operations are wrapped in `vde_run`, which captures return codes and maps them to the **Sovereign Error Table**:
- `VDE_ERR_GENERAL (1)`
- `VDE_ERR_NOT_FOUND (3)`
- `VDE_ERR_LOCK (9)`
- `VDE_ERR_SYNC_DRIFT (13)`

---
**Version**: 1.3.0
**Status**: SOVEREIGN BASELINE CERTIFIED
**Reference**: ARCHITECTURE 1.3.0
---
