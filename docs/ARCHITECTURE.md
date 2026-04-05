# ARCHITECTURE v2.0.5 (Absolute)

## VERSION HISTORY
| Version | Date       | Changes                                                                 |
| :---    | :---       | :---                                                                    |
| 2.0.3   | 2026-04-03 | Standardized SSH Key naming convention for vde-bootstrap.               |
| 2.0.4   | 2026-04-04 | Shifted hydration logic to USP setup scripts and formalized the Ignition Pipeline. |
| 2.0.5   | 2026-04-04 | Version bump to 2.0.5.                                                  |

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

## 3. Universal Script Parity (USP) Logic

Manufacturing logic has moved from build-args to modular scripts:
- **Registry Independence**: `vm-types.conf` defines *what* exists; `scripts/setup/` defines *how* it is built.
- **Image Hygiene**: Every USP script is mandated to purge its own ghosts (`apt-get clean`) to ensure the final jail is pure.

## 4. Persistence & Identity Mapping

- **Workspace**: `/home/devuser/workspace` mapped to `projects/<lang>/`.
- **SSH Bridge**: `vde_student.pub` is mapped to the container's `authorized_keys` at start.
- **Namespace Protection**: All library functions use local, unique-prefixed variables to prevent collisions with the global registry.
