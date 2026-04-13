# VDE: Technical Deep-Dive (1.3.1 Sovereign)

## 1. The Rule Spine (UAP Enforcement)

The Universal Agent Protocol (UAP) is enforced by `bin/vde-enforce-uap.zsh`. This sentinel performs deep content inspection on all scripts in `bin/`, `lib/`, and `.gemini/` to ensure architectural purity.

### 1.1. Core Enforcement Logic:
- **Ghost Zone Detection**: Triggers an immediate blockade if unauthorized root directories (e.g., `conductor/`) are detected.
- **Shebang Purity**: Verifies that every script begins with `#!/usr/bin/env zsh`.
- **Forbidden Patterns**:
    - **No Sleep**: Blocks the use of `sleep` in favor of deterministic polling via `bin/vde-poll`.
    - **No Bash-isms**: Flags potential Bash-style single brackets `[ ]` and 0-indexed arrays `[0]`.
- **Fake ZSH Detection**: Audits scripts for the presence of ZSH-native parameter expansion `${(` to ensure high-fidelity logic.

## 2. The Ignition Pipeline (The Smelting Ritual)

VDE employs a three-tier reactive synchronization pipeline to transform human intent into O(1) runtime lookups.

1.  **Smelting (`vde_translate_conf_to_json`)**: Hammers the 8-field `.conf` Source into a structured `.json` Registry. This process is written in pure ZSH to avoid host-level `jq` dependencies (Rule G).
2.  **Caching (`vde_core_save_cache`)**: Serializes the Registry into ZSH-native associative arrays (`VDE_CORE_VM_TYPE`, `VDE_CORE_VM_ALIASES`, `VDE_CORE_VM_DISPLAY`).
3.  **Sync Trigger**: The orchestrator performs a timestamp audit (`-nt`). If any source component is newer than the cache, a re-smelt is forced before Spoke ignition.

## 3. Concurrency & Atomic Stewardship (Phase 25)

VDE manages high-velocity parallel operations via the **Lock-Queue Model** implemented in `lib/vm-lock`.

### 3.1. FIFO Ticket-Based Locking:
- **Registration**: Every process requesting a lock creates a unique "Ticket" file in `${lock_file}.queue/` using `${EPOCHREALTIME}-$$`.
- **Ordering**: The `claim_lock` function numericaly sorts tickets (`ls | sort -n`); only the oldest ticket is permitted to proceed.
- **The Atomic Gate**: Final ownership is claimed via kernel-level `mkdir` atomicity.
- **Progress Jitter**: If contention occurs, processes wait using a ZSH-native floating-point jitter: `0.1 + (RANDOM / 32768.0 * 0.4)`.

### 3.2. Port Stewardship:
- **Atomic Reservation**: Reserves candidate ports via `.locks/ports/port-<number>.lock` directories.
- **The Seeker's Recon**: Performs a physical diagnostic handshake using a transient container named `vde-port-probe-${port}`. If the bind fails, the port is marked as `STALE_HOST` and rotated.

## 4. Universal Script Parity (USP) & Hydration

USP ensures Spoke immutability by decoupling hydration rituals from runtime logic.
- **Rituals**: Every Spoke is hydrated via `scripts/setup/<alias>-init.zsh`.
- **Asynchronous Ignition**: Service Spokes register background startup scripts in `/usr/local/bin/vde-spoke-ignition.zsh`, ensuring the primary SSH gate remains responsive during service initialization.

## 5. Security & Sovereign Bridge

### 5.1. Identity Isolation:
- **Permission Sentinel**: `vde_security_enforce_permissions` applies strict `700` (directories) and `600` (files) permissions to all sensitive assets.
- **Key Isolation**: Confines all VDE identity assets to `~/.ssh/vde/` to prevent interference with host SSH configurations.

### 5.2. Bridge Mechanics:
- **Docker Socket Bridge**: Automatically detects the host `docker.sock` GID and performs dynamic GID mapping inside the jail, followed by `chmod 666` for non-root access.
- **SSH Agent Bridge**: Implements a "Symbolic Handshake" via `socat` UNIX-LISTEN proxying, mapping the host agent socket to `/home/devuser/.ssh/vde/agent.sock` for persistent identity forwarding.

## 6. Deterministic Error Engine (Phase 26)

All CLI strikes are wrapped in `vde_run` to capture kernel-level signals and map them to the Sovereign Error Table:
- `VDE_ERR_GENERAL (1)`
- `VDE_ERR_NOT_FOUND (3)`
- `VDE_ERR_LOCK (9)`
- `VDE_ERR_SYNC_DRIFT (13)`

## 7. CI/CD Hardening (The ZSH Deadlock Fix)

To ensure the Sovereign Baseline can be certified in non-interactive environments (GitHub Actions), VDE implements a "Chicken-and-Egg" ZSH bootstrap fix.

### 7.1. The ZSH Bootstrap ritual:
- **Problem**: GitHub Actions default runners often lack a properly configured ZSH environment during the initial `actions/checkout` phase, leading to deadlocks when the Orchestrator attempts to enforce UAP.
- **Solution**: The `tests/run-sovereign-tests.zsh` runner implements a pre-flight bootstrap that explicitly exports `SHELL=/usr/bin/zsh` and forces the sourcing of `~/.zshrc` logic into the runner's subshell.

### 7.2. VDE_CI_MODE (Port Allocation Bypass):
- **Mechanism**: When `VDE_CI_MODE=1` is detected, the `vde_docker_allocate_port` function bypasses the physical diagnostic probe (`docker run --rm`).
- **Rationale**: In CI environments without DinD (Docker-in-Docker) capabilities, physical probes will always fail. `VDE_CI_MODE` permits the allocator to rely on the atomic file-system locks alone, ensuring the pipeline remains green in restricted environments.

---
**Version**: 1.3.1
**Status**: SOVEREIGN BASELINE CERTIFIED
**Reference**: ARCHITECTURE 1.3.1
---
