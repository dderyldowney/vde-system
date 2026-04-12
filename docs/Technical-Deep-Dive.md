# VDE: Technical Deep-Dive (v1.3.0 Sovereign)

## 1. The Rule Spine (UAP Enforcement)

The Virtual Development Environment is governed by the **Universal Agent Protocol (UAP)**, enforced by `bin/vde-enforce-uap.zsh`. This sentinel script ensures every action adheres to the **Resol’nare** (Supreme Prohibitions).

### Core Enforcement Mandates:
- **ZSH Native Sovereignty**: Detects "Fake ZSH" by verifying the use of native parameter expansion `${(` and associative arrays. Usage of `bash` or 0-indexed arrays is a Class-A violation.
- **Shebang Purity**: Recursively audits `bin/`, `lib/`, and `scripts/` to ensure `#!/usr/bin/env zsh` is the universal entry point.
- **Ghost Detection**: Monitors for "Ghost Zones" (unauthorized root directories) and ensures build-time artifacts (`apt` lists) are purged.
- **Supervised Execution**: Every CLI strike is wrapped in the Enforcer to maintain architectural integrity.

## 2. The Ignition Pipeline (The Smelting Ritual)

VDE employs a three-tier reactive synchronization pipeline to transform human-readable intent into high-performance runtime data.

1.  **The Source (`data/vm-types.conf`)**: The user-editable flat-file registry following the 8-field standard.
2.  **The Registry (`data/vm-types.json`)**: The `vde_translate_conf_to_json` ritual (Rule G) hammers the `.conf` into a structured JSON archive using pure ZSH parsing.
3.  **The Cache (`.cache/vm-types.cache`)**: The `smelt_vm_cache` process generates a ZSH-native associative array for O(1) runtime lookup.
4.  **Ignition Sync**: The `bin/vde` orchestrator performs a timestamp audit. If source files are newer than the cache, a re-smelt is triggered automatically before Spoke ignition.

## 3. Concurrency & Atomic Stewardship

VDE manages high-concurrency operations (parallel builds and mass ignitions) via the **Lock-Queue Model** (Phase 25).

### FIFO Ticket-Based Locking (`lib/vm-lock`)
Unlike traditional spinlocks, VDE uses a deterministic sequencing mechanism:
- **Registration**: Every process requesting a lock creates a unique "Ticket" in `${lock_file}.queue/` using `${EPOCHREALTIME}-$$`.
- **Oldest Ticket Priority**: The `claim_lock` function enforces FIFO order—only the process with the oldest timestamped ticket may pass the atomic gate.
- **The Atomic Gate**: Uses kernel-level `mkdir` atomicity to claim the final directory-based lock.
- **Ownership Proof**: Once claimed, the lock directory contains a `pid` file recording `PID:PGID:TIMESTAMP` for transparent monitoring and crash recovery.

### Port Stewardship (`.locks/ports/`)
To prevent double-allocation during parallel strikes, VDE reserves ports using `<port>.lock` markers. No Spoke is assigned a port until a physical diagnostic handshake (`docker run --rm`) and a lock acquisition are both successful.

## 4. Universal Script Parity (USP)

VDE decouples environment hydration from Dockerfile complexity through USP rituals stored in `scripts/setup/`.

- **Hydration Ritual**: Every Spoke entry MUST point to a setup script (`<alias>-init.zsh`).
- **Asynchronous Ignition**: Service Spokes (Postgres, Redis, etc.) register background ignition hooks in `/usr/local/bin/vde-spoke-ignition.zsh`, detaching service availability from the primary SSH gate.
- **Born Ready (BTO)**: All hydration happens during the `docker build` phase. Runtime `apt` calls are strictly forbidden to ensure images are immutable and portable.

## 5. Cognitive Sovereignty (Section 13)

The "Alor" (Orchestrator) operates under the **Mandalorian Sequence**:
1.  **Kov'nyn (Think First)**: Spend the reasoning budget to form a hypothesis before deploying tools.
2.  **Recon (Scout Deployment)**: Use research scouts for factual ore (API signatures, error codes).
3.  **Synthesis (Strike the Beskar)**: Implement code derived from first principles. Paraphrasing scouts is forbidden; all code must be forged in the Orchestrator's core.
4.  **Ret'lini (The Revisit)**: Post-implementation self-critique against the Rule Spine.

## 6. Security & Infrastructure Bridge

- **Identity Isolation**: The `vde_student` identity is confined to the `${VDE_SSH_DIR}` (`~/.ssh/vde/`), ensuring no leakage into the host's primary SSH config.
- **Command Sanitization**: VDE has purged all `eval` usage in primary sinks. Commands are executed via native ZSH arrays `"${cmd[@]}"` to neutralize injection vectors.
- **Sovereign Bridge**: SSH Agent forwarding is established via `socat` UNIX-proxying in the entrypoint, bypassing filesystem permission blocks on Darwin and Linux.
- **Socket Sovereignty**: The Docker socket is bridged via dynamic GID mapping and secure `chmod 666` within the isolated `vde-net` environment.

---
**Version**: 1.3.0
**Status**: SOVEREIGN BASELINE CERTIFIED
**Reference**: ARCHITECTURE v1.3.0
---
