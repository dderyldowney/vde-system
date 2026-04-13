# ARCHITECTURE v1.3.1 (The Sovereign Baseline)

## 1. The Hub-and-Spoke Tiered Model

VDE uses a three-tier inheritance and isolation model to ensure identity consistency while maintaining absolute Spoke autonomy. The system has been purged of legacy agent debt (Claude Code) to ensure the Sovereign Bridge remains purely ZSH-driven.

| Tier | Name | Component | Role |
| :--- | :--- | :--- | :--- |
| **Tier 1** | **The Hub** | `vde-base` | Defines Identity (`devuser`), Shell (`Zsh`), and the **Sovereign Bridge** (SSH/Docker). |
| **Tier 2** | **The Spoke** | `scripts/setup/` | **USP (Universal Script Parity)** rituals that hydrate the environment at build-time. |
| **Tier 3** | **The Jail** | Container | The immutable running process bridged to the host. Optimized for ignition in <4.2s. |

## 2. The Ignition Pipeline (The Smelting Ritual)

VDE uses a reactive synchronization pipeline to transform human intent into high-performance runtime data.

1.  **The Source (`data/vm-types.conf`)**: Human-editable flat-file following the strict 8-field standard: `type|name|aliases|display_name|pkgs|custom_cmd|service_port|ssh_port`.
2.  **The Registry (`data/vm-types.json`)**: Structured JSON archive hammered via pure ZSH parsing (`vde_translate_conf_to_json`) to avoid host-level `jq` dependencies (Rule G).
3.  **The Cache (`.cache/vm-core.cache`)**: High-speed ZSH-native associative arrays (`VDE_CORE_VM_TYPE`, `VDE_CORE_VM_ALIASES`, `VDE_CORE_VM_DISPLAY`) for O(1) runtime lookup.

- **Automatic Sync**: The Orchestrator performs a timestamp audit (`-nt`). If the Source is newer than the Registry, or the Registry newer than the Cache, a re-smelt is triggered automatically before any VM strike.

## 3. Concurrency & Resource Stewardship (Phase 25)

VDE uses a **Lock-Queue Model** to manage high-velocity parallel operations without race conditions.

### 3.1. FIFO Lock-Queue Sequencing (`lib/vm-lock`)
- **Ticket Registration**: Every strike requesting a lock registers a unique "Ticket" file in `${lock_file}.queue/` using `${EPOCHREALTIME}-$$`.
- **FIFO Enforcement**: Only the process holding the **oldest numerically sorted ticket** is permitted to attempt the atomic `mkdir` gate.
- **Ownership Proof**: Once claimed, the lock directory contains a `pid` file recording `PID:PGID:TIMESTAMP` for transparent monitoring.

### 3.2. Port Stewardship (`lib/vde-docker`)
- **Atomic Reservation**: Uses `.locks/ports/port-<number>.lock` to prevent double-allocation during concurrent ignitions.
- **Physical Handshake**: No port is assigned until a physical diagnostic probe (`docker run --rm --name vde-port-probe-<port>`) verifies the port is not occupied.
- **Port Ranges**: `VDE_LANG_PORT_START` (2200) and `VDE_SVC_PORT_START` (2400).

## 4. Deterministic Error Engine (Phase 26)

All VDE operations are wrapped in the `vde_run` deterministic execution wrapper:
- **Signal Translation**: Kernel signals (SIGINT/130, SIGKILL/137, SIGTERM/143) are captured and mapped to UX-friendly remediation feedback.
- **Zero-Host Fidelity**: Errors are reported using the Sovereign Error Table defined in `lib/vde-constants`.

## 5. Persistence & Sovereign Bridge

- **Identity Isolation**: The `vde_student` key is isolated to `~/.ssh/vde/`.
- **SSH Agent Bridge**: Established via `socat` UNIX-proxying in the entrypoint, mapping the host socket to `~/.ssh/vde/agent.sock` inside the container.
- **Docker Socket Bridge**: Bridged via dynamic GID mapping and `chmod 666` within the isolated `vde-net` environment.
- **Workspace Mapping**: `/home/devuser/workspace` maps to `projects/<alias>/` on the Hub.

## 6. Sovereign Testing Framework (The Gauntlet)

VDE employs a dual-stream testing architecture to ensure high-velocity CI/CD without sacrificing physical validation.

- **The Sovereign Runner (`tests/run-sovereign-tests.zsh`)**: A high-speed, CI-optimized runner that executes a subset of core infrastructure tests (The Tetrad) without requiring physical Docker-in-Docker (DinD) privileges.
- **Physical Validation**: Full-lifecycle BDD scenarios (Behave/Python) are reserved for local Forge environments where physical container-within-container operations are permitted.

---
Version: 1.3.1
Status: SOVEREIGN BASELINE CERTIFIED
Reference: THE WAY OF THE VDE
---
