# ARCHITECTURE v1.3.0 (The Sovereign Baseline)

## VERSION HISTORY
| Version | Date       | Changes                                                                 |
| :---    | :---       | :---                                                                    |
| 1.3.0   | 2026-04-12 | Certified Sovereign Baseline with FIFO Ticket Locking and automated releases. |
| 1.3.0   | 2026-04-11 | Established The Sovereign Baseline and VDE_INSTALL.md.                  |
| 1.3.0   | 2026-04-10 | Absolute release with FIFO locking and deterministic signals.           |
| 1.2.1   | 2026-04-09 | Hardened System Spine Tetrad and Rule Spine integration.                |

## 1. The Hub-and-Spoke Tiered Model

VDE uses a three-tier inheritance and isolation model to ensure identity consistency while maintaining absolute Spoke autonomy.

| Tier | Name | Component | Role |
| :--- | :--- | :--- | :--- |
| **Tier 1** | **The Hub** | `vde-base` | Defines Identity (`devuser`), Shell (`Zsh`), and the **Transversal Bridge** (SSH). |
| **Tier 2** | **The Spoke** | `scripts/setup/` | **USP (Universal Script Parity)** rituals that hydrate the environment at build-time. |
| **Tier 3** | **The Jail** | Container | The running process (e.g., `vde-python`). Optimized for ignition in <4.2s. |

## 2. The Ignition Pipeline (The Smelting Ritual)

VDE uses a reactive synchronization pipeline to transform human intent into high-performance runtime data.

1.  **The Source (`data/vm-types.conf`)**: Human-editable flat-file following the strict 8-field standard: `type|name|aliases|display_name|pkgs|custom_cmd|service_port|ssh_port`.
2.  **The Registry (`data/vm-types.json`)**: Structured JSON archive hammered via pure ZSH parsing (`vde_translate_conf_to_json`) to avoid host-level `jq` dependencies (Rule G).
3.  **The Cache (`.cache/vm-core.cache`)**: High-speed ZSH-native associative arrays (`VDE_CORE_VM_TYPE`, `VDE_CORE_VM_ALIASES`, `VDE_CORE_VM_DISPLAY`) for O(1) runtime lookup.

- **Automatic Sync**: The Orchestrator performs a timestamp audit (`-nt`). If the Source is newer than the Registry, or the Registry newer than the Cache, a re-smelt is triggered automatically before any VM strike.

## 3. Concurrency & Resource Stewardship (Phase 25)

VDE uses a **Lock-Queue Model** to manage high-velocity parallel operations without race conditions.

### 3.1. FIFO Lock-Queue Sequencing (`lib/vm-lock`)
- **Ticket Registration**: Every strike requesting a lock registers a unique timestamped "Ticket" file in `${lock_file}.queue/` using `${EPOCHREALTIME}-$$`.
- **FIFO Enforcement**: The `claim_lock` function performs a line-check; only the process holding the **oldest ticket** (numerically sorted) is permitted to attempt the atomic `mkdir` gate.
- **Ownership Proof**: Once claimed, the lock directory contains a `pid` file recording `PID:PGID:TIMESTAMP`.
- **Paths**: Primary locks reside in `${VDE_ROOT_DIR}/.locks/vms/` and `global-config.lock`.

### 3.2. Port Stewardship (`lib/vde-docker`)
- **Atomic Reservation**: Uses `${VDE_ROOT_DIR}/.locks/ports/port-<number>.lock` to prevent double-allocation during concurrent ignitions.
- **Physical Handshake**: No port is assigned until a physical diagnostic probe (`docker run --rm`) verifies the port is not occupied by host-level "Scavenger" processes.
- **Port Ranges**: Defined in `lib/vde-constants`: `VDE_LANG_PORT_START` (2200) and `VDE_SVC_PORT_START` (2400).

### 3.3. Deterministic Error Engine (Phase 26)
- **Signal Translation**: Kernel-level signals (SIGINT/130, SIGKILL/137, SIGTERM/143) are captured by the `vde_run` wrapper and mapped to UX-friendly remediation feedback via `vde_error_map`.
- **Status Reporting**: All CLI operations utilize `vde_progress` (spinners and progress bars) for real-time visibility into lock contention and ignition states.

## 4. Universal Script Parity (USP) Logic

Manufacturing logic is decoupled from container orchestration to ensure "Born Ready" (BTO) images:
- **Registry Independence**: `vm-types.json` defines *what* exists; `scripts/setup/` defines *how* it is built.
- **Asynchronous Spoke Ignition**: Service Spokes register background hooks in `/usr/local/bin/vde-spoke-ignition.zsh`, ensuring the SSH Gate remains fast while services ignite in the background.
- **Image Hygiene**: Every USP ritual is mandated to "Purge the Ghosts" (`apt-get clean && rm -rf /var/lib/apt/lists/*`) to maintain immutable purity.

## 5. Persistence & Identity Bridge

- **Workspace Mapping**: `/home/devuser/workspace` maps to `projects/<alias>/` on the Hub.
- **Sovereign Bridge**: SSH Agent forwarding is established via `socat` UNIX-proxying in the entrypoint, mapping the Hub socket to `${VDE_SSH_DIR}/agent.sock`.
- **Identity Isolation**: The `vde_student` key is isolated to `~/.ssh/vde/` (`VDE_SSH_DIR`), preventing collision with personal identities.
- **Naming Standard**: Controlled by `lib/vde-naming`. Containers always use `vde-<base_name>` (e.g., `vde-python`).

---
Version: 1.3.0
Status: SOVEREIGN BASELINE CERTIFIED
Reference: THE WAY OF THE VDE
---
