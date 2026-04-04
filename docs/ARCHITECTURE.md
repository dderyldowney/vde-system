# ARCHITECTURE v2.0.3 (Absolute)

## VERSION HISTORY
| Version | Date | Changes |
| :--- | :--- | :--- |
| 1.7.2 | 2026-04-02 | Modular Library and template-heavy design. |
| 2.0.0 | 2026-04-03 | Implemented Hub-and-Spoke model with Build-Time parameterization. |
| 2.0.1 | 2026-04-03 | Integrated OS-level upgrades in Hub for stability. |
| 2.0.3 | 2026-04-03 | Standardized SSH Key naming convention for vde-bootstrap. |

## 1. The Hub-and-Spoke Tiered Model

VDE uses a three-tier inheritance model to ensure identity consistency while allowing for specialized "Jails."

| Tier | Name | Component | Role |
| :--- | :--- | :--- | :--- |
| **Tier 1** | **The Hub** | `vde-base` | Defines Identity (devuser), Shell (Zsh), and Core Security (SSH/Sudo). |
| **Tier 2** | **The Spoke** | `vde-lang` | A parameterized template using `ARG PKGS_TO_INSTALL` to bake skills at build-time. |
| **Tier 3** | **The Jail** | Container | The running process (e.g., `vde-python`). Functional in <1s. |

## 2. Parameterized Manufacturing Logic

We have replaced individual language Dockerfiles with **Build-Time Injection**.

- **The Master Template**: `configs/docker/vde-lang.Dockerfile`.
- **Skill Injection**: The CLI passes the package list (e.g., `python3 python3-pip`) as a build argument.
- **Result**: The image is "Billed" as a finished product. No placeholders or runtime scripts are used.

## 3. Persistence & Identity Mapping

- **Workspace**: `/home/devuser/workspace` mapped to `projects/<lang>/`.
- **SSH Bridge**: `vde_student.pub` is mapped to the container's `authorized_keys` at start.
- **Identity**: All jails use the same `vde_student` private key for seamless access.

