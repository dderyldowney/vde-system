# ARCHITECTURE v2.1.0 (Absolute)

## VERSION HISTORY
| Version | Date       | Changes                                                                 |
| :---    | :---       | :---                                                                    |
| 2.0.3   | 2026-04-03 | Standardized SSH Key naming convention for vde-bootstrap.               |
| 2.0.4   | 2026-04-04 | Shifted hydration logic to USP setup scripts and formalized the Ignition Pipeline. |
| 2.0.5   | 2026-04-04 | Version bump to 2.0.5.                                                  |
| 2.0.6   | 2026-04-06 | Implemented Phase 25: Concurrency Hardening. Atomic port management and VM-level locking spinlocks. |

## 1. The Hub-and-Spoke Tiered Model

VDE uses a three-tier inheritance model to ensure identity consistency while allowing for specialized "Jails."

| Tier | Name | Component | Role |
| :--- | :--- | :--- | :--- |
| **Tier 1** | **The Hub** | `vde-base` | Defines Identity (devuser), Shell (Zsh), and Core Security (SSH/Sudo). |
| **Tier 2** | **The Spoke** | `scripts/setup/` | USP rituals that hydrate the environment at build-time using absolute logic. |
| **Tier 3** | **The Jail** | Container | The running process (e.g., `vde-python`). Functional in <1s. |

## 2. The Ignition Pipeline (Pre-Flight)

We have replaced static configurations with a **Reactive Sync Ritual**.

1. **The Raw Beskar**: `data/vm-types.conf` (User-edited source).
2. **The Pure Beskar**: `data/vm-types.json` (Atomic 8-field registry).
3. **The Tracking Fob**: `.cache/vm-types.cache` (High-speed runtime hydration).

- **Automatic Reconciliation**: If any upstream file is newer (`-nt`) than its downstream target, the CLI triggers a pure ZSH re-smelt immediately to ensure the environment matches the latest manual strike.

## 3. Concurrency & Resource Stewardship (Phase 25)

VDE 2.0.6 introduces a **Lock-Queue Model** to handle high-concurrency operations.

### 3.1. Atomic Port Management
- **The Registry**: Located at `.cache/port-registry/`.
- **The Protocol**: Uses atomic `<port>.lock` files to reserve ports before assignment. This prevents "Double Allocation" when multiple VMs are created simultaneously.
- **Stewardship**: Ports are now verified against both the registry and the live host bridge before being struck.

### 3.2. Lifecycle Spinlocks
- **VM Locking**: Every lifecycle operation (`rebuild`, `start`) is protected by a mandatory directory lock at `.locks/vms/<vm_name>.lock`.
- **Global Config Lock**: Sensitive registry operations are governed by a global mutex (`.locks/global-config.lock`) to prevent corruption of the "Pure Beskar" during parallel updates.
- **Deterministic Backoff**: Lock acquisition uses sub-second precision polling with random jitter to prevent "Thundering Herd" collisions.

### 3.3. Deterministic Error Engine (Phase 26)
- **Signal Translation**: Kernel-level signals (EEXIST, ENOENT) are mapped to `VDE_ERR_*` codes and translated into contextual remediation via `lib/vde-errors`.
- **Heartbeat Proof**: Every lock records a PID:PGID:TIMESTAMP heartbeat. This allows the system to deterministically recover from hung processes without risking PID-reuse collisions.
- **Double-Gate Sync**: The Orchestrator verifies Hub sovereignty by checking timestamps *inside* the lock block, ensuring zero-drift execution.

## 4. Universal Script Parity (USP) Logic

Manufacturing logic has moved from build-args to modular scripts:
- **Registry Independence**: `vm-types.conf` defines *what* exists; `scripts/setup/` defines *how* it is built.
- **Image Hygiene**: Every USP script is mandated to purge its own ghosts (`apt-get clean`) to ensure the final jail is pure.

## 5. Persistence & Identity Mapping

- **Workspace**: `/home/devuser/workspace` mapped to `projects/<lang>/`.
- **SSH Bridge**: `vde_student.pub` is mapped to the container's `authorized_keys` at start.
- **Namespace Protection**: All library functions use local, unique-prefixed variables to prevent collisions with the global registry.
