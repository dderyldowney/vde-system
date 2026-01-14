# Architecture

Technical details about VDE's architecture and design.

[← Back to README](../README.md)

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

---

## Shared Library

**File:** `scripts/lib/vm-common`

The `vm-common` library provides core functions used by all scripts:

| Function | Purpose |
|----------|---------|
| `get_vm_info()` | Query VM type data |
| `resolve_vm_name()` | Handle aliases |
| `find_next_available_port()` | Auto-allocate ports |
| `render_template()` | Generate configs from templates |
| `merge_ssh_config_entry()` | Safely add SSH entries |
| `start_vm()` | Start a VM via docker-compose |
| `stop_vm()` | Stop a VM via docker-compose |
| `validate_vm_name()` | Validate VM name format |
| `vm_exists()` | Check if VM config exists |
| `detect_ssh_keys()` | Find all SSH keys in ~/.ssh/ |
| `get_primary_ssh_key()` | Select best SSH key |
| `ensure_ssh_agent()` | Start SSH agent, load keys |
| `ensure_ssh_environment()` | One-call SSH setup |
| `generate_vm_ssh_config()` | Create VM-to-VM SSH config |
| `sync_ssh_keys_to_vde()` | Copy public keys to VDE |

---

## Base Image

All VMs build from `configs/docker/base-dev.Dockerfile` which includes:

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

## AI System Architecture

The VDE AI Assistant consists of three main components:

```
┌─────────────────────────────────────────────────────────────────┐
│                     User Input Layer                            │
│  vde-ai (CLI)           vde-chat (Interactive)                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Parser Layer                                │
│  vde-parser - Natural language processing                      │
│  • Intent detection (8 intents)                                │
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
│  │ ~/.ssh/      │◄────────┤ • Holds private keys             │ │
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
| `detect_ssh_keys()` | Find all SSH keys in ~/.ssh/ |
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
- `base-dev.Dockerfile`: Installs openssh-client, configures agent forwarding
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

[← Back to README](../README.md)
