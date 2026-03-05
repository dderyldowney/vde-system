# Architecture

Technical details about VDE's architecture and design.

[← Back to README](../README.md)

---

## Modular Library Structure

VDE is built on a modular library architecture that separates concerns and enables code reuse across the system.

### Core Libraries

| Library | Purpose | Dependencies |
|---------|---------|--------------|
| **vde-constants** | Centralized constants (return codes, port ranges, timeouts, SSH dirs) | None |
| **vde-shell-compat** | Portable shell operations (zsh/bash compatibility) | None |
| **vde-errors** | Error messages with remediation steps | vde-constants |
| **vde-log** | Structured logging with rotation (JSON/text/syslog) | vde-constants, vde-shell-compat |
| **vde-naming** | Naming conventions — enforces `vde-` prefix for containers/SSH | vde-constants |
| **vde-security** | Security policy enforcement (permissions, network isolation, SSH isolation) | vde-constants, vde-log |
| **vde-core** | Essential VDE functions (VM types, queries, caching) | vde-constants, vde-shell-compat |
| **vm-common** | Full VDE functionality (VM types, ports, Docker, SSH, templates) | vde-constants, vde-shell-compat, vde-naming, vde-security |
| **vde-commands** | Safe wrapper functions for VDE operations | vm-common |
| **vde-parser** | Pattern-based natural language parser (intent detection, entity extraction) | vm-common, vde-commands |

### Additional Libraries

| Library | Purpose |
|---------|---------|
| **vde-progress** | Progress bars and status indicators |
| **vde-audit** | VM audit trails and change tracking |
| **vde-metrics** | Performance metrics and monitoring |

### Library Loading Order

The libraries must be sourced in this order due to dependencies:

```zsh
source "$SCRIPTS_DIR/lib/vde-constants"      # 1. Base constants
source "$SCRIPTS_DIR/lib/vde-shell-compat"   # 2. Shell compatibility
source "$SCRIPTS_DIR/lib/vde-errors"         # 3. Error handling
source "$SCRIPTS_DIR/lib/vde-log"            # 4. Logging
source "$SCRIPTS_DIR/lib/vde-naming"         # 5. Naming conventions (vde- prefix)
source "$SCRIPTS_DIR/lib/vde-security"       # 6. Security enforcement
source "$SCRIPTS_DIR/lib/vde-core"           # 7. Core VDE functions
source "$SCRIPTS_DIR/lib/vm-common"          # 8. Full VDE functionality
source "$SCRIPTS_DIR/lib/vde-commands"       # 9. Command wrappers
source "$SCRIPTS_DIR/lib/vde-parser"         # 10. Natural language parser
```

---

## Template System

VDE uses a template-based architecture for generating container configurations.

### Templates

| Template | Purpose | Location |
|----------|---------|----------|
| `compose-language.yml` | Language VM docker-compose.yml | `scripts/templates/` |
| `compose-service.yml` | Service VM docker-compose.yml | `scripts/templates/` |
| `ssh-entry.txt` | SSH config entries | `scripts/templates/` |

### Data-Driven Configuration

- **File:** `scripts/data/vm-types.conf`
- **Format:** Pipe-delimited (type, name, aliases, display_name, install_command, service_port)
- **Purpose:** Single source of truth for all VM types
- **Caching:** VM types are cached in `.cache/vm-types.cache` for performance

---

## Shared Library

**File:** `scripts/lib/vm-common`

The `vm-common` library provides core functions used by all scripts:

| Function | Purpose |
|----------|---------|
| `get_vm_info()` | Query VM type data (type, aliases, display, install, port) |
| `resolve_vm_name()` | Handle aliases (e.g., "nodejs" → "js") |
| `find_next_available_port()` | Auto-allocate ports (with registry for fast lookup) |
| `render_template()` | Generate configs from templates |
| `merge_ssh_config_entry()` | Safely add SSH entries |
| `start_vm()` | Start a VM via docker-compose |
| `stop_vm()` | Stop a VM via docker-compose |
| `validate_vm_name()` | Validate VM name format |
| `vm_exists()` | Check if VM config exists |
| `detect_ssh_keys()` | Find all SSH keys in ~/.ssh/vde/ |
| `get_primary_ssh_key()` | Select best SSH key |
| `ensure_ssh_agent()` | Start SSH agent, load keys |
| `ensure_ssh_environment()` | One-call SSH setup |
| `generate_vm_ssh_config()` | Create VM-to-VM SSH config |
| `sync_ssh_keys_to_vde()` | Copy public keys to VDE |
| `get_all_vms()` | List all VM names |
| `get_lang_vms()` | List language VMs only |
| `get_service_vms()` | List service VMs only |
| `is_known_vm()` | Check if VM name is known |
| `load_vm_types()` | Load VM types from config or cache |

---

## Virtual Machines

### Language VMs (20 total, ports 2200-2299)

Container names use the mandatory `vde-` prefix. SSH access: `ssh vde-{name}` (using `~/.ssh/vde/config`).

| Name | Aliases | Container Name | SSH Port |
|------|---------|----------------|----------|
| js | node, nodejs | vde-js | 2209 |
| cpp | c++, gcc | vde-cpp | 2202 |
| asm | assembler, nasm | vde-asm | 2202 |
| c | c | vde-c | 2203 |
| rust | rust | vde-rust | 2216 |
| csharp | dotnet | vde-csharp | 2206 |
| go | golang | vde-go | 2206 |
| java | jdk | vde-java | 2209 |
| kotlin | kotlin | vde-kotlin | 2210 |
| swift | swift | vde-swift | 2214 |
| php | php | vde-php | 2212 |
| scala | scala | vde-scala | 2213 |
| r | rlang, r | vde-r | 2214 |
| lua | lua | vde-lua | 2218 |
| flutter | dart, flutter | vde-flutter | 2205 |
| elixir | elixir | vde-elixir | 2215 |
| haskell | ghc, haskell | vde-haskell | 2216 |
| zig | zig | vde-zig | 2219 |
| ruby | ruby | vde-ruby | 2215 |
| python | python3 | vde-python | 2213 |

### Service VMs (7 total, ports 2400-2499)

Container names use the mandatory `vde-` prefix. SSH access: `ssh vde-{name}` (using `~/.ssh/vde/config`).

| Name | Aliases | Container Name | SSH Port | Service Port |
|------|---------|----------------|----------|--------------|
| redis | redis | vde-redis | 2406 | 6379 |
| postgres | postgresql | vde-postgres | 2404 | 5432 |
| mongodb | mongo | vde-mongodb | 2402 | 27017 |
| couchdb | couchdb | vde-couchdb | 2404 | 5984 |
| mysql | mysql | vde-mysql | 2405 | 3306 |
| nginx | nginx | vde-nginx | 2403 | 80, 443 |
| rabbitmq | rabbitmq | vde-rabbitmq | 2405 | 5672, 15672 |

---

## Base Image

All VMs build from `configs/docker/vde-base.Dockerfile` which includes:

- System updates and security patches
- SSH server configuration (with agent forwarding enabled)
- SSH client configuration (ForwardAgent yes)
- sudo access for devuser
- zsh with oh-my-zsh framework
- neovim with LazyVim configuration
- Common development tools (git, curl, wget, etc.)
- SSH agent forwarding helper scripts
- Host communication helper (`to-host` alias)

---

---

## CLI Commands

### Primary Entry Point: `vde`

The `vde` command provides a unified interface to all VDE operations:

| Command | Script | Purpose |
|---------|--------|---------|
| `vde create <vm>` | create-virtual-for | Create a new VM |
| `vde start <vm>` | start-virtual | Start a VM |
| `vde stop <vm>` | shutdown-virtual | Stop a VM |
| `vde restart <vm>` | shutdown-virtual + start-virtual | Restart a VM |
| `vde list` | list-vms | List all VMs |
| `vde status` | list-vms | Show VM status |
| `vde health` | vde-health | Run system health check |
| `vde help` | (built-in) | Show help message |

### Utility Scripts

| Script | Purpose |
|--------|---------|
| `add-vm-type` | Add new VM types to vm-types.conf |
| `ssh-agent-setup` | View SSH agent status and configuration |
| `vde-health` | Run comprehensive system health check |

---

## Port Allocation Strategy

VDE uses a structured port allocation system to avoid conflicts:

### Language VM SSH Ports (2200-2299)

Language VMs are assigned SSH ports sequentially from the 2200 range:

```
vde-asm     2200    (alphabetical order)
vde-c       2201
vde-cpp     2202
vde-csharp  2203
...
```

### Service VM SSH Ports (2400-2499)

Service VMs are assigned SSH ports from the 2400 range:

```
vde-couchdb     2400    (alphabetical order)
vde-mongodb     2401
vde-mongodb     2402
vde-couchdb     2404
vde-mysql       2405
...
```

### Service Ports

Service VMs also expose their application ports on the host:

| VM | Service Port(s) |
|----|-----------------|
| postgres | 5432 |
| redis | 6379 |
| mongodb | 27017 |
| nginx | 80, 443 |
| couchdb | 5984 |
| mysql | 3306 |
| rabbitmq | 5672, 15672 |

### Port Registry

VDE maintains a port registry at `.cache/port-registry` for fast port lookups and to prevent port conflicts.

---

## Docker Compose Integration

### Docker Compose File Structure

Each VM has its own `docker-compose.yml` file:

```
configs/docker/
├── c/
│   └── docker-compose.yml    # vde-c container, SSH port 2201
├── cpp/
│   └── docker-compose.yml    # vde-cpp container, SSH port 2202
├── python/
│   └── docker-compose.yml    # vde-python container, SSH port 2203
├── postgres/
│   └── docker-compose.yml    # postgres container, SSH port 2404, service port 5432
└── ...
```

### Docker Network

All VMs are connected to a shared Docker network named `vde-net`, enabling inter-container communication.

### Container Naming Conventions

- **Language VMs:** `vde-{name}` (e.g., `vde-python`, `vde-rust`)
- **Service VMs:** `vde-{name}` (e.g., `vde-postgres`, `vde-redis`)

---

## Command Parser Architecture

The VDE command parser consists of four main components:

```
┌─────────────────────────────────────────────────────────────────┐
│                     User Input Layer                            │
│  vde CLI commands                                               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Parser Layer                                │
│  vde-parser - Pattern-based command understanding              │
│  • Intent detection (9 intents)                                │
│  • Entity extraction (VMs, flags, filters)                     │
│  • Plan generation                                              │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Commands Layer                               │
│  vde-commands - Safe wrapper functions                         │
│  • Query functions (list, status, info)                         │
│  • Action functions (create, start, stop)                       │
│  • Batch operations                                             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Core Layer                                 │
│  vm-common - Core VDE functions                                 │
│  • VM type management                                           │
│  • Port allocation                                              │
│  • Template rendering                                           │
│  • SSH management                                                │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Infrastructure                                │
│  Docker Compose + SSH                                           │
└─────────────────────────────────────────────────────────────────┘
```

### Supported Intents

The parser recognizes 9 distinct intents:

| Intent | Purpose | Example Commands |
|--------|---------|------------------|
| `list_vms` | List available VMs | "what VMs can I create?", "show languages" |
| `create_vm` | Create new VMs | "create a Go VM", "make Python and PostgreSQL" |
| `start_vm` | Start VMs | "start Go", "launch everything" |
| `stop_vm` | Stop VMs | "stop Go", "shutdown everything" |
| `restart_vm` | Restart VMs | "restart Python", "rebuild and start Go" |
| `status` | Show running status | "what's running?", "show status" |
| `connect` | Get SSH connection info | "how do I connect to Python?", "SSH into Go" |
| `add_vm_type` | Add new VM types | "add a new language called Zig" |
| `help` | Show help | "help", "what can I do?" |

---

## SSH Agent Forwarding Architecture

VDE includes SSH agent forwarding for secure VM-to-VM, VM-to-Host, and VM-to-External communication.

### Components

```
┌─────────────────────────────────────────────────────────────────┐
│                         Host Machine                            │
│                                                                  │
│  ┌──────────────┐         ┌──────────────────────────────────┐ │
│  │ SSH Keys     │         │ SSH Agent                        │ │
│  │ ~/.ssh/vde/      │◄────────┤ • Holds private keys             │ │
│  │ id_ed25519  │         │ • Never exposes keys directly     │ │
│  │ id_rsa      │         │ • Socket: $SSH_AUTH_SOCK         │ │
│  │ ...         │         │ • Auto-started by VDE             │ │
│  └──────────────┘         └──────────────▲───────────────────┘ │
│                                          │                     │
│                          Socket Forwarding (read-only mount)   │
│                                          │                     │
│                                          ▼                     │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ Docker Container (VM)                                     │ │
│  │                                                           │ │
│  │  • SSH_AUTH_SOCK=/ssh-agent/sock                          │ │
│  │  • ForwardAgent yes (client config)                       │ │
│  │  • AllowAgentForwarding yes (server config)               │ │
│  │  • Can authenticate using host's keys                     │ │
│  └──────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Communication Patterns

**VM → VM:**
```
[Go VM] --SSH--> [Host SSH Agent] --SSH--> [Python VM]
                      (authentication)
```

**VM → External:**
```
[Python VM] --SSH--> [Host SSH Agent] --SSH--> [GitHub/GitLab]
                         (uses your keys)
```

**VM → Host:**
```
[Python VM] --docker exec--> [Host Docker Daemon]
                 (direct access)
```

### Security Model

- **Private keys NEVER leave the host**: Only the authentication socket is forwarded
- **Read-only mount**: Containers cannot modify the SSH agent socket
- **Automatic key management**: All keys detected and loaded automatically
- **No manual configuration**: VDE handles agent startup and key loading

### Implementation

**Functions in `vm-common`:**

| Function | Purpose |
|----------|---------|
| `detect_ssh_keys()` | Find all SSH keys in ~/.ssh/vde/ |
| `get_primary_ssh_key()` | Select best key (ed25519 > ecdsa > rsa > dsa) |
| `ensure_ssh_agent()` | Start agent, load keys (automatic, silent) |
| `ensure_ssh_environment()` | One-call setup for all SSH operations |
| `generate_vm_ssh_config()` | Create VM-to-VM SSH config entries |
| `sync_ssh_keys_to_vde()` | Copy all public keys to public-ssh-keys/ |

**Docker Configuration:**

- **Socket mount:** `${SSH_AUTH_SOCK:-/tmp/ssh-agent.sock}:/ssh-agent/sock:ro`
- **Environment:** `SSH_AUTH_SOCK=/ssh-agent/sock`
- **Server config:** `AllowAgentForwarding yes`
- **Client config:** `ForwardAgent yes`

**Integration Points:**

- `create-virtual-for`: Calls `ensure_ssh_environment()` before creating VM
- `start-virtual`: Calls `ensure_ssh_environment()` before starting VM
- `vde-base.Dockerfile`: Installs openssh-client, configures agent forwarding
- `ssh-agent-setup`: User-facing status and information script

---

## Data Flow

```
User Command
    │
    ▼
Parse Intent ────────┐
    │                 │
    ▼                 ▼
Extract Entities   Generate Plan
    │                 │
    ▼                 ▼
Validate VMs ───────> Structured Plan
    │                 │
    ▼                 ▼
Route to Handler ────> Execute Plan
    │                 │
    ▼                 ▼
Call VDE Scripts ────> Result
    │
    ▼
Return to User
```

---

## Key Design Principles

1. **Data-Driven Configuration:** All VM types defined in a single config file
2. **Template-Based:** docker-compose.yml files generated from templates
3. **Separation of Concerns:** Parsing, commands, and core functions in separate libraries
4. **Safety First:** All operations validated before execution
5. **Extensibility:** Add new VM types without modifying code

---

## Testing Architecture

VDE uses Behave for behavior-driven testing (BDD) of all operations.

### Test Categories

| Path | Purpose |
|------|---------|
| [`tests/features/`](../tests/features/) | Behave BDD tests |
| [`tests/features/core-infrastructure/`](../tests/features/core-infrastructure/) | Primary test suite (tiered: unit, integration, docker) |
| [`tests/features/docker-required/`](../tests/features/docker-required/) | Legacy Docker-required tests |

Features tagged `@requires-docker-host` or `@docker` require a live Docker daemon and are excluded from the default `python3 -m behave` run. Use `--tags @docker` to include them.

### Step Definitions

All step definitions use the `run_vde_command()` helper from `vm_common.py` for real VDE execution:

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
| [`plans/completed/20-docker-required-test-remediation-plan.md`](../plans/completed/20-docker-required-test-remediation-plan.md) | Original 899-step remediation plan (archived) |
| [`plans/29-docker-required-remaining-steps-plan.md`](../plans/29-docker-required-remaining-steps-plan.md) | Current progress and remaining work |

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

---

[← Back to README](../README.md)
