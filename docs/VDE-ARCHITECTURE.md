# VDE Architecture Reference

## System Overview

VDE (Virtual Development Environment) is a Docker-based container orchestration system for managing 19+ language VMs with shared services. This document defines the canonical architecture breakdown for all sessions.

---

## Directory Structure

### Control Center
| Path | Purpose |
|------|---------|
| [`scripts/vde`](../scripts/vde) | Master control script - entry point for all VDE operations |
| [`scripts/lib/`](../scripts/lib) | VDE libraries (vde-constants, vde-commands, vde-parser, vde-core, vm-common, etc.) |
| [`scripts/data/vm-types.conf`](../scripts/data/vm-types.conf) | Data-driven VM type definitions |

### Configuration Center
| Path | Purpose |
|------|---------|
| [`configs/`](configs/) | Docker configurations for all VMs (VOLATILE - generated from templates) |
| [`configs/docker/*/docker-compose.yml`](../configs/docker/) | Docker-compose files for each VM type (SOURCE OF TRUTH - never delete) |
| [`env-files/`](../env-files/) | Individual VM environment files (python.env, rust.env, go.env, etc.) |

### Data Directories
| Path | Purpose |
|------|---------|
| [`data/`](data/) | Persistent data directories (postgres, redis, mongodb, etc.) |

---

## Execution Flow

```
User: ./vde <command>
  ↓
scripts/vde (master control)
  ↓
vde-parser (natural language parsing)
  ↓
scripts/lib/* (libraries execute logic)
  ↓
scripts/* (individual scripts complete command)
```

---

## VM Architecture

### Language VMs (Ports 2200-2299)
| VM Type | Port Range |
|---------|------------|
| c, cpp, asm, python, rust, js, csharp, ruby, go, java, kotlin, swift, php, scala, r, lua, flutter, elixir, haskell, zig | 2200-2299 |

### Service VMs (Ports 2400-2499)
| Service | Port |
|---------|------|
| postgres, redis, mongodb, nginx, mysql, rabbitmq, couchdb | 2400-2499 |

---

## Key Commands

All VDE operations flow through `scripts/vde`:

| Command | Purpose |
|---------|---------|
| `./vde create <type> <name>` | Create a new VM |
| `./vde start <name>` | Start a VM |
| `./vde stop <name>` | Stop a VM |
| `./vde restart <name>` | Restart a VM |
| `./vde ssh <name>` | SSH into VM |
| `./vde remove <name>` | Remove a VM |
| `./vde list` | List all VMs |
| `./vde status <name>` | Get VM status |
| `./vde connect <name>` | Connect to VM |

---

## Testing Architecture

### BDD Tests
| Path | Purpose |
|------|---------|
| [`tests/features/`](tests/features/) | Behave BDD tests |
| [`tests/features/docker-required/`](tests/features/docker-required/) | Tests requiring Docker |
| [`tests/features/docker-free/`](tests/features/docker-free/) | Tests without Docker dependencies |

### Step Definitions
| File | Purpose |
|------|---------|
| `tests/features/steps/vde_command_steps.py` | Natural language command patterns |
| `tests/features/steps/config_and_verification_steps.py` | Configuration patterns |
| `tests/features/steps/vm_project_steps.py` | VM Project patterns |
| `tests/features/steps/debugging_and_port_steps.py` | Debug patterns |
| `tests/features/steps/network_and_resource_steps.py` | Network patterns |
| `tests/features/steps/crash_recovery_steps.py` | Crash recovery patterns |
| `tests/features/steps/file_verification_steps.py` | File verification patterns |
| `tests/features/steps/vm_common.py` | `run_vde_command()` helper function |

---

## Plans

| Plan | Purpose |
|------|---------|
| [`plans/completed/20-docker-required-test-remediation-plan.md`](plans/completed/20-docker-required-test-remediation-plan.md) | Original 899-step remediation plan (archived) |
| [`plans/29-docker-required-remaining-steps-plan.md`](plans/29-docker-required-remaining-steps-plan.md) | Current progress and remaining work |

---

## Shell Requirements

- **ZSH ONLY:** `#!/usr/bin/env zsh` or `#!/bin/zsh`
- **Forbidden:** `/bin/sh` and `/usr/bin/env sh`
- **Features:** Associative arrays, process substitution, zsh 5.x

---

## User Model

- User: `devuser` with passwordless sudo
- Authentication: SSH key only
- Editor: neovim/LazyVim
