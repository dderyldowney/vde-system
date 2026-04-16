# VDE: Technical Deep-Dive (1.3.7 Sovereign)

## 1. The Rule Spine (UAP Enforcement)

The Virtual Development Environment is governed by the **Universal Agent Protocol (UAP)**, enforced by `bin/vde-enforce-uap.zsh`. This sentinel script ensures every action adheres to the **Resol’nare** (Supreme Prohibitions).

### Core Enforcement Mandates:
- **ZSH Native Sovereignty**: Detects "Fake ZSH" by verifying the use of native parameter expansion `${(` and associative arrays. Usage of `bash` or 0-indexed arrays is a Class-A violation.
- **Shebang Purity**: Recursively audits `bin/`, `lib/`, and `scripts/` to ensure `#!/usr/bin/env zsh` is the universal entry point.
- **Ghost Detection**: Monitors for "Ghost Zones" (unauthorized root directories), enforces shebang purity, and forbids `sleep` calls in favor of deterministic polling.
- **Supervised Execution**: Every CLI strike is wrapped in the Enforcer to maintain architectural integrity.

## 2. The Ignition Pipeline (The Smelting Ritual)

VDE employs a three-tier reactive synchronization pipeline to transform human-readable intent into high-performance runtime data.

1.  **The Source (`data/vm-types.conf`)**: The human-editable flat-file registry following the strict 8-field standard: `type|name|aliases|display_name|pkgs|custom_cmd|service_port|ssh_port`.
2.  **The Registry (`data/vm-types.json`)**: The `vde_translate_conf_to_json` ritual hammers the `.conf` into a structured JSON archive using pure ZSH parsing to avoid host-level `jq` dependencies.
3.  **The Cache (`.cache/vm-core.cache`)**: The `vde_core_save_cache` process generates a ZSH-native associative array for O(1) runtime lookup.
4.  **Ignition Sync**: The `bin/vde` orchestrator performs a timestamp audit. If source files are newer than the cache, a re-smelt is triggered automatically before Spoke ignition.

## 3. Concurrency & Atomic Stewardship

VDE manages high-concurrency operations via the **Lock-Queue Model**.

### FIFO Ticket-Based Locking (`lib/vm-lock`)
VDE uses a deterministic sequencing mechanism to prevent race conditions:
- **Ticket Registration**: Every process requesting a lock creates a unique "Ticket" file.
- **Oldest Ticket Priority**: The `claim_lock` function enforces FIFO order.
- **The Atomic Gate**: Uses kernel-level `mkdir` atomicity to claim the final directory-based lock.

### Port Stewardship (`lib/vde-docker`)
To prevent double-allocation during parallel strikes, VDE reserves ports using lock markers. No Spoke is assigned a port until:
1.  **Kernel Referee**: The port lock directory is successfully created.
2.  **The Seeker's Recon**: A physical diagnostic handshake verifies the port is not occupied.
3.  **Hub Registry Check**: Verification that the port isn't pre-defined.

## 4. Universal Script Parity (USP)

VDE decouples environment hydration from Dockerfile complexity through USP rituals stored in `scripts/setup/`.

- **Hydration Ritual**: Every Spoke entry MUST point to a setup script (`<alias>-init.zsh`).
- **Born Ready (BTO)**: All hydration happens during the `docker build` phase. Runtime `apt` calls are strictly forbidden to ensure images are immutable and portable.

## 5. Security & Infrastructure Bridge

### Identity Isolation (`lib/vde-security`)
- **Key Isolation**: The `vde_student` identity is confined to `~/.ssh/vde/`.
- **Permission Enforcement**: Recursive `700` to sensitive directories and `600` to identity files.
- **Network Segmentation**: `vde-net` bridge ensures container isolation.

### Sovereign Bridge & Sanitization
- **Command Sanitization**: Native ZSH arrays neutralize injection vectors.
- **SSH Agent Trust**: Forwarding via `socat` UNIX-proxying in the entrypoint.

---
**Version**: 1.3.7
**Status**: SOVEREIGN BASELINE CERTIFIED
**Reference**: ARCHITECTURE 1.3.7
**Identity**: The Covert
---
