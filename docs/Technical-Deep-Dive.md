# VDE System: Complete Technical Deep-Dive

[← Back to README](../README.md)

---

## Architecture Overview

The VDE (Virtual Development Environment) system is a **template-based, data-driven Docker container orchestration system**. It's designed to create isolated development environments for different programming languages and services, all accessible via SSH with consistent user configuration.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          HOST MACHINE                                   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                         ~/dev/                                  │   │
│  │                                                                  │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │   │
│  │  │   bin/   │  │   configs/   │  │   projects/  │          │   │
│  │  │              │  │   docker/    │  │              │          │   │
│  │  │ • lib/       │  │              │  │ • c/         │◄─────┐   │   │
│  │  │   • vde-*    │  │ • vde-base   │  │ • cpp/       │       │   │   │
│  │  │   • vm-common│  │ • c/         │  │ • python/    │       │   │   │
│  │  │ • templates/ │  │ • cpp/       │  │ • rust/      │       │   │   │
│  │  │ • data/      │  │ • python/    │  │ • go/        │       │   │   │
│  │  │ • vde        │  │ • rust/      │  │ • postgres/  │       │   │   │
│  │  │ • *.vm       │  │ • go/        │  └──────────────┘       │   │   │
│  │  └──────────────┘  └──────────────┘                        │   │   │
│  │                                                             │   │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │   │   │
│  │  │  env-files/  │  │   data/      │  │    logs/     │     │   │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘     │   │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                │                                      │
│                          ┌─────▼─────┐                                │
│                          │  Docker   │                                │
│                          │  Engine   │                                │
│                          └─────┬─────┘                                │
└───────────────────────────────┼──────────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                ▼               ▼               ▼
        ┌──────────────┐ ┌──────────┐ ┌──────────────┐
        │  vde-python  │ │  vde-go  │ │  vde-postgres │
        │  :2214       │ │  :2207   │ │  :2404       │
        └──────────────┘ └──────────┘ └──────────────┘
                │               │               │
                └───────────────┴───────────────┘
                                │
                        ┌───────▼───────┐
                        │  vde-net  │
                        │ (Docker Net)  │
                        └───────────────┘
```

---

## Part 0: SSH Agent Forwarding System

VDE includes a comprehensive SSH agent forwarding system that enables secure VM-to-VM, VM-to-Host, and VM-to-External communication.

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Host Machine                            │
│                                                                  │
│  ┌──────────────┐         ┌──────────────────────────────────┐ │
│  │ SSH Keys     │         │ SSH Agent                        │ │
│  │ ~/.ssh/vde/      │◄────────┤ • Holds private keys             │ │
│  │ id_ed25519  │         │ • Socket: $SSH_AUTH_SOCK         │ │
│  │ id_rsa      │         │ • Auto-started by VDE             │ │
│  │ ...         │         └──────────────▲───────────────────┘ │
│  └──────────────┘                        │                     │
│                                          │ Socket Forwarding   │
│                                          ▼                     │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ Docker Container (VM)                                     │ │
│  │  • SSH_AUTH_SOCK=/ssh-agent/sock                          │ │
│  │  • ForwardAgent yes (client config)                       │ │
│  │  • AllowAgentForwarding yes (server config)               │ │
│  └──────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Key Functions in vm-common

**SSH Key Management:**
- `detect_ssh_keys()` - Find all SSH keys in ~/.ssh/vde/
- `get_primary_ssh_key()` - Select best key (priority: ed25519 > ecdsa > rsa > dsa)
- `get_ssh_pubkey()` - Get public key for private key
- `sync_ssh_keys_to_vde()` - Copy all public keys to public-ssh-keys/

**SSH Agent Management:**
- `ssh_agent_is_running()` - Check if SSH agent is running
- `ensure_ssh_agent()` - Start agent, load keys (automatic, silent)
- `ensure_ssh_environment()` - One-call setup for all SSH operations

**SSH Configuration:**
- `generate_vm_ssh_config()` - Create VM-to-VM SSH config entries
- `merge_ssh_config_entry()` - Safely add SSH entries to ~/.ssh/vde/config
- `get_vm_ssh_port()` - Get SSH port for a VM

### Integration Points

**In create-virtual-for:**
```bash
ensure_ssh_environment  # Automatic SSH setup
```

**In start-virtual:**
```bash
ensure_ssh_environment  # Automatic SSH setup
```

**In vde-base.Dockerfile:**
- `AllowAgentForwarding yes` in sshd_config
- `ForwardAgent yes` in SSH client config
- SSH agent forwarding helper script
- Host communication helper (`to-host` alias)

**In Docker Compose Templates:**
- Socket mount: `${SSH_AUTH_SOCK:-/tmp/ssh-agent.sock}:/ssh-agent/sock:ro`
- Environment: `SSH_AUTH_SOCK=/ssh-agent/sock`

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

---

## Part 1: Modular Library Architecture

VDE uses a **modular library architecture** that separates concerns and enables selective loading. All libraries are located in `lib/` and can be sourced independently.

### Library Dependency Graph

```
                    ┌─────────────────────┐
                    │   vde-shell-compat  │
                    │  (Shell portability) │
                    └──────────┬───────────┘
                               │
                ┌──────────────┴──────────────┐
                ▼                             ▼
         ┌─────────────┐              ┌─────────────┐
         │vde-constants│              │  vde-errors │
         │(Return codes│              │(Error msgs) │
         │port ranges) │              └──────┬──────┘
         └──────┬──────┘                     │
                │                             │
                ▼                             ▼
         ┌─────────────┐              ┌─────────────┐
         │  vde-log    │◄─────────────│  vde-core   │
         │ (Logging)   │              │(VM type load│
         └──────┬──────┘              │    queries) │
                │                      └──────┬──────┘
                ▼                             │
         ┌─────────────┐                      │
         │  vde-parser │                      │
         │(Pattern     │                      │
         │ matching)   │                      │
         └─────────────┘                      │
                                            │
                ┌─────────────────────────────┘
                ▼
         ┌─────────────┐              ┌─────────────┐
         │  vde-parser │              │vde-commands │
         │(Pattern     │──────────────▶│(API wrapper)│
         │matching)   │              │             │
         └─────────────┘              └──────┬──────┘
                                             │
                ┌─────────────────────────────┘
                ▼
         ┌─────────────┐
         │  vm-common  │
         │(Full VDE API│
         │SSH/Docker/  │
         │Templates)   │
         └─────────────┘
```

### Library Descriptions

| Library | Purpose |
|---------|---------|
| `vde-shell-compat` | Shell detection, portable associative arrays, date/time operations |
| `vde-constants` | Standardized return codes (0-11), port ranges, timeouts, error messages |
| `vde-errors` | Contextual error messages with remediation steps, color support |
| `vde-log` | Structured logging (text/JSON/syslog), rotation, query functions |
| `vde-naming` | VM name validation, generation, and normalization |
| `vde-security` | Security checks: key validation, permission enforcement |
| `vde-core` | Essential VM operations, type loading with caching, lazy module loading |
| `vm-common` | Full VDE API including SSH, Docker, templates |
| `vde-commands` | High-level command wrappers for batch operations (§3.5) |
| `vde-parser` | Pattern-based natural language parser, intent detection, entity extraction (§3.6) |
| `vde-docker` | Docker operations; includes §3.7 `docker_*` spec-required aliases |
| `vde-templates` | Template rendering; includes §3.8 `render_*_template` spec-required wrappers |
| `vde-ssh` | SSH key management, config generation, agent operations |

### Core Library: vde-shell-compat

**Purpose:** Provides portable abstractions for shell-specific features across zsh 5.0+, bash 4.0+, and bash 3.x.

**Key Functions:**
- `_detect_shell()` - Detect current shell (zsh/bash/unknown)
- `_is_zsh()`, `_is_bash()` - Shell detection predicates
- `_get_script_path()`, `_get_script_dir()` - Portable script path detection
- `_assoc_init()`, `_assoc_set()`, `_assoc_get()` - Portable associative array operations
- `_assoc_keys()`, `_assoc_has_key()` - Array query operations
- `_date_iso8601()`, `_date_epoch()` - Portable date/time functions

**Critical Fix:** Uses hex encoding (`od -An -tx1`) for associative array keys in bash 3.x fallback to prevent key collisions (e.g., "a/b" and "a_b" both becoming "a_b" with simple character replacement).

### Core Library: vde-constants

**Purpose:** Centralized constants for return codes, port ranges, timeouts, and configuration.

**Return Codes:**
```bash
VDE_SUCCESS=0          # Operation completed successfully
VDE_ERR_GENERAL=1      # Unspecified failure
VDE_ERR_INVALID_INPUT=2 # Bad arguments or validation failure
VDE_ERR_NOT_FOUND=3    # Resource doesn't exist
VDE_ERR_PERMISSION=4   # Insufficient permissions
VDE_ERR_TIMEOUT=5      # Operation exceeded time limit
VDE_ERR_EXISTS=6       # Resource already exists
VDE_ERR_DEPENDENCY=7   # Required dependency missing
VDE_ERR_DOCKER=8       # Docker operation failure
VDE_ERR_LOCK=9         # Failed to acquire lock
```

**Port Ranges:**
```bash
VDE_LANG_PORT_START=2200  # Language VMs: 2200-2299
VDE_LANG_PORT_END=2299
VDE_SVC_PORT_START=2400   # Service VMs: 2400-2499
VDE_SVC_PORT_END=2499
VDE_CONTAINER_SSH_PORT=22 # SSH port inside containers
```

### Core Library: vde-errors

**Purpose:** Provides contextual error messages with remediation steps and documentation links.

**Key Functions:**
- `vde_error_show()` - Full error with what/why/how structure
- `vde_error_simple()` - Simple error message
- `vde_error_docker_not_running()` - Docker daemon not running
- `vde_error_port_in_use()` - Port conflict guidance
- `vde_error_ssh_key_missing()` - SSH key generation instructions
- `vde_error_vm_not_found()` - VM not found with next steps

**Example Output:**
```
Error: Cannot connect to Docker daemon
Reason: Docker daemon is not running or you don't have permission to access it
Solution:
    1. Start Docker: sudo systemctl start docker (Linux) or start Docker Desktop (macOS/Windows)
    2. Add your user to the docker group: sudo usermod -aG docker $USER
    3. Log out and back in for group changes to take effect
Docs: https://github.com/dderyldowney/dev/blob/main/docs/troubleshooting.md#docker-daemon-not-running
```

### Core Library: vde-log

**Purpose:** Structured logging with multiple output formats and rotation capabilities.

**Features:**
- Multiple formats: text, JSON, syslog
- Multiple outputs: stdout, stderr, file
- Automatic log rotation by size or time
- Log cleanup by retention policy
- Query functions: `vde_log_recent()`, `vde_log_grep()`, `vde_log_errors()`

**Usage:**
```bash
vde_log_init                    # Initialize logging system
vde_log_set_level DEBUG         # Set minimum log level
vde_log_to_file /path/to/log    # Output to file
vde_log_info "Starting VM" "python"
vde_log_error "Failed to start" "postgres"
```

### Core Library: vde-core

**Purpose:** Minimal core library for essential VDE operations without SSH/Docker dependencies.

**Key Functions:**
- `vde_core_load_types()` - Load VM type data (with caching)
- `vde_core_get_all_vms()` - List all known VM names
- `vde_core_get_vm_type()` - Get VM type (lang/service)
- `vde_core_is_known_vm()` - Check if VM is known
- `vde_time_start()`, `vde_time_end()` - Performance timing (debug)

**Caching:** Uses `.cache/vm-types.cache` with mtime validation for fast VM type lookups.

### Pattern Parser Library: vde-parser

**Purpose:** Pattern-based natural language parsing for VDE commands.

**vde-parser Functions:**
- `detect_intent()` - Detect user intent (list_vms, create_vm, start_vm, stop_vm, restart_vm, status, connect, help)
- `extract_vm_names()` - Extract VM names from input using O(1) alias map
- `extract_flags()` - Extract rebuild/nocache flags
- `generate_plan()` - Generate structured execution plan
- `execute_plan()` - Execute parsed plan with validation

**Supported Intents:**
- `list_vms` - List available VMs (filter: lang/svc/all)
- `create_vm` - Create new VM configuration
- `start_vm` - Start one or more VMs
- `stop_vm` - Stop one or more VMs
- `restart_vm` - Restart VMs (supports rebuild, nocache)
- `status` - Check running status
- `connect` - Show connection information
- `help` - Display help

### Command Library: vde-commands

**Purpose:** High-level command wrappers for VDE operations.

**Query Functions:**
- `vde_list_vms()` - List VMs with optional filtering
- `vde_vm_exists()` - Check if VM exists
- `vde_get_vm_info()` - Get VM information
- `vde_get_running_vms()` - Get list of running VMs
- `vde_get_vm_status()` - Get status of specific VM
- `vde_get_ssh_info()` - Get SSH connection info
- `vde_resolve_alias()` - Resolve alias to canonical name

**Action Functions:**
- `vde_create_vm()` - Create a new VM
- `vde_start_vm()` - Start a VM
- `vde_stop_vm()` - Stop a VM
- `vde_restart_vm()` - Restart a VM
- `vde_start_all()` - Start all VMs
- `vde_stop_all()` - Stop all VMs

**Batch Operations:**
- `vde_create_multiple_vms()` - Create multiple VMs
- `vde_start_multiple_vms()` - Start multiple VMs
- `vde_stop_multiple_vms()` - Stop multiple VMs

### Docker Library: vde-docker (§3.7)

VDE-SPEC.md §3.7 defines spec-required `docker_*` function names. These are implemented as thin aliases in `lib/vde-docker` over the underlying `start_vm`/`stop_vm`/`restart_vm`/`get_vm_status` functions:

| Spec Function | Implementation | Description |
|---------------|---------------|-------------|
| `docker_build(vm)` | `start_vm "$1" true false` | Build and start a VM with rebuild |
| `docker_start(vm)` | `start_vm "$1" false false` | Start a VM |
| `docker_stop(vm)` | `stop_vm "$1"` | Stop a VM |
| `docker_restart(vm)` | `restart_vm "$1"` | Restart a VM |
| `docker_status(vm)` | `get_vm_status "$1"` | Get VM status |
| `docker_get_running()` | `docker ps --filter "name=vde-"` | List running VDE containers |

---

## Part 2: Core Data Structure (vm-types.conf)

Everything starts with the **vm-types.conf** file. This is the single source of truth for all VM types.

**File:** `data/vm-types.conf`

**Format:** Pipe-delimited records
```
type|name|aliases|display_name|install_command|service_port
```

**Example entries:**
```bash
lang|go|golang|Go|apt-get update -y && apt-get install -y golang-go|
service|postgres|postgresql|PostgreSQL|apt-get update -y && apt-get install -y postgresql-client|5432
```

**Field meanings:**

| Field | Example | Purpose |
|-------|---------|---------|
| `type` | `lang` or `service` | Determines template and naming convention |
| `name` | `go` | Primary identifier (lowercase alphanumeric) |
| `aliases` | `golang` | Alternate names for lookup |
| `display_name` | `Go` | Human-readable name for messages |
| `install_command` | Shell command | Runs during container startup |
| `service_port` | `5432` or empty | Service port(s) for containers, empty for languages |

**All 21 Language VMs:**
| Name | Aliases | Display Name | SSH Port Range |
|------|---------|--------------|---------------|
| vde-asm | asm, assembler, nasm | Assembler | 2200-2220 |
| vde-c | c | C | 2200-2220 |
| vde-cpp | cpp, c++, gcc | C++ | 2200-2220 |
| vde-csharp | csharp, dotnet | C# | 2200-2220 |
| vde-displaytest | displaytest | Go Language | 2200-2220 |
| vde-elixir | elixir, ex, iex | Elixir | 2200-2220 |
| vde-flutter | flutter, dart | Flutter | 2200-2220 |
| vde-go | go, golang | Go | 2200-2220 |
| vde-haskell | haskell, ghc | Haskell | 2200-2220 |
| vde-java | java, jdk | Java | 2200-2220 |
| vde-js | js, node, nodejs, npm | Node.js | 2200-2220 |
| vde-kotlin | kotlin | Kotlin | 2200-2220 |
| vde-lua | lua | Lua | 2200-2220 |
| vde-php | php | PHP | 2200-2220 |
| vde-python | python, python3, py | Python | 2200-2220 |
| vde-ruby | ruby | Ruby | 2200-2220 |
| vde-rust | rust, rs, rustc | Rust | 2200-2220 |
| vde-scala | scala | Scala | 2200-2220 |
| vde-swift | swift | Swift | 2200-2220 |
| vde-testport1 | testport1 | Test Port 1 | 2200-2220 |
| vde-testport2 | testport2 | Test Port 2 | 2200-2220 |

**All 7 Service VMs:**
| Name | Aliases | Display Name | SSH Port | Service Port(s) |
|------|---------|--------------|----------|----------------|
| vde-couchdb | couchdb | CouchDB | 2400 | 5984 |
| vde-mongodb | mongo | MongoDB | 2401 | 27017 |
| vde-mysql | mysql | MySQL | 2402 | 3306 |
| vde-nginx | nginx | Nginx | 2403 | 80,443 |
| vde-postgres | postgresql | PostgreSQL | 2404 | 5432 |
| vde-rabbitmq | rabbitmq | RabbitMQ | 2405 | 5672,15672 |
| vde-redis | redis | Redis | 2406 | 6379 |

**Why this format:**
- ✅ Simple to parse (shell built-in `read -A`)
- ✅ Human-readable and editable
- ✅ No dependencies (no JSON/YAML parsers needed)
- ✅ Easy to extend (just add a line)

---

## Part 3: The Full VDE Library (lib/vm-common)

When any script runs, the first thing it does is:

```bash
source "$SCRIPT_DIR/lib/vm-common"
```

This loads **2158 lines** of shared functionality. Let's break down what happens:

### 3.1 Source Chain (Library Loading Order)

```bash
# 1. vde-shell-compat - Portable shell operations
. "$VDE_ROOT_DIR/lib/vde-shell-compat"

# 2. vde-constants - Standardized return codes and constants
. "$VDE_ROOT_DIR/lib/vde-constants"

# 3. Directory constants
CONFIGS_DIR="$VDE_ROOT_DIR/configs/docker"
SCRIPTS_DIR="$VDE_ROOT_DIR/scripts"
TEMPLATES_DIR="$SCRIPTS_DIR/templates"
DATA_DIR="$SCRIPTS_DIR/data"
VM_TYPES_CONF="$DATA_DIR/vm-types.conf"
```

### 3.2 Associative Array Declaration (using shell-compat)

```bash
# Uses portable _assoc_init from vde-shell-compat
_assoc_init "VM_TYPE"       # [go]=lang, [postgres]=service
_assoc_init "VM_ALIASES"    # [go]=golang, [postgres]=postgresql
_assoc_init "VM_DISPLAY"    # [go]=Go, [postgres]=PostgreSQL
_assoc_init "VM_INSTALL"    # [go]=apt-get install golang-go
_assoc_init "VM_SVC_PORT"   # [go]=, [postgres]=5432
```

The portable associative arrays work across:
- **zsh 5.0+**: Native associative arrays with `typeset -gA`
- **bash 4.0+**: Native associative arrays with `declare -gA`
- **bash 3.x**: File-based fallback with hex-encoded keys

### 3.3 Config Loading (with Caching)

```bash
load_vm_types() {
    local conf_file="$VM_TYPES_CONF"
    local cache_file="$VM_TYPES_CACHE"

    # Check cache validity
    if _is_cache_valid "$conf_file" "$cache_file"; then
        _load_from_cache "$cache_file"
        return 0
    fi

    # Parse vm-types.conf line by line
    while IFS='|' read -r type name vm_aliases display install svc_port; do
        # Skip comments (#) and empty lines
        [[ "$type" =~ ^#.*$ ]] && continue
        [[ -z "$type" ]] && continue

        # Store in portable associative arrays
        _assoc_set "VM_TYPE" "$name" "$type"
        _assoc_set "VM_ALIASES" "$name" "$vm_aliases"
        _assoc_set "VM_DISPLAY" "$name" "$display"
        _assoc_set "VM_INSTALL" "$name" "$install"
        _assoc_set "VM_SVC_PORT" "$name" "$svc_port"
    done < "$conf_file"

    # Write to cache
    _write_cache "$cache_file"
}
```

**Performance:** Caching reduces VM type loading from ~50ms to ~5ms after first load.

### 3.4 Name Resolution (with Alias Map)

```bash
resolve_vm_name() {
    local input=$1

    # Direct match: "go" -> "go"
    if is_known_vm "$input"; then
        echo "$input"
        return 0
    fi

    # Alias lookup: "golang" -> "go"
    # Uses O(1) alias map lookup for better performance
    local canonical
    canonical=$(_lookup_vm_by_alias "$input" 2>/dev/null)
    if [[ -n "$canonical" ]]; then
        echo "$canonical"
        return 0
    fi

    return 1
}
```

**Performance:** The O(1) alias map lookup in `vde-parser` is significantly faster than the O(n×m) nested loop approach for resolving aliases.

---

## Part 4: Unified CLI Command (vde)

VDE provides a **unified command-line interface** through the `vde` script located at `bin/vde`. This is the recommended way to interact with VDE.

### Usage

```bash
vde <command> [options] [args]
```

### Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `rebuild [--vm <vm>] [--no-cache]` | Rebuild VDE images | `vde rebuild` |
| `create <vm>` | Create a new VM | `vde create python` |
| `start <vm>` | Start a VM | `vde start python` |
| `stop <vm>` | Stop a VM | `vde stop postgres` |
| `restart <vm>` | Restart a VM | `vde restart rust` |
| `ssh <vm>` | SSH into a VM | `vde ssh python` |
| `connect <vm>` | SSH into a VM (alias for ssh) | `vde connect python` |
| `remove <vm>` | Remove a VM instance | `vde remove rust` |
| `delete <vm>` | Completely delete a VM | `vde delete rust` |
| `uninstall <type>` | Uninstall a language/service | `vde uninstall elixir` |
| `list` | List all VMs | `vde list` |
| `status` | Show VM status | `vde status` |
| `health` | Run system health check | `vde health` |
| `create-and-start` | Create and start VMs | `vde create-and-start python` |
| `nuke` | Remove all of VDE | `vde nuke` |
| `ssh-setup` | Manage VDE SSH environment | `vde ssh-setup init` |
| `ssh-sync` | Sync SSH keys to build context | `vde ssh-sync` |
| `cleanup-ports` | Clean up stale port locks | `vde cleanup-ports` |
| `init` | Initialize VDE networks | `vde init` |
| `ps` | List running containers | `vde ps` |
| `logs <vm>` | Show container logs | `vde logs python` |
| `inspect <vm>` | Inspect container | `vde inspect python` |
| `port <vm>` | Show port mappings | `vde port python` |
| `exec <vm> <cmd>` | Execute command in container | `vde exec python ls` |
| `images` | List VDE images | `vde images` |
| `networks` | List VDE networks | `vde networks` |
| `stats` | Show resource usage | `vde stats` |
| `info` | Show Docker info | `vde info` |
| `ask <text>` | Natural language command interface | `vde ask "list all vms"` |
| `help` | Show help message | `vde help` |

### Options

| Option | Description |
|--------|-------------|
| `-h, --help` | Show help message |
| `-v, --verbose` | Enable verbose output |
| `-q, --quiet` | Suppress debug output (quiet mode) |
| `--version` | Show version information |

### Command Aliases

The `vde` command supports several aliases for convenience:

| Input | Resolved To |
|-------|-------------|
| `vde create` | `create-virtual-for` |
| `vde start` | `start-virtual` |
| `vde stop` | `shutdown-virtual` |
| `vde list` | `list-vms` |
| `vde status` | `list-vms` |
| `vde connect` | `ssh-vm` |
| `vde ssh` | `ssh-vm` |

### Natural Language Interface (vde ask)

The `vde ask` command exposes the vde-parser's natural language capabilities:

```bash
vde ask "list all vms"
vde ask "start the python vm"
vde ask "create a rust development environment"
vde ask "stop postgres"
```

Internally, `vde ask` calls `generate_plan "$input" | execute_plan`, routing through the parser's intent detection and structured plan execution. The parser supports intents: `list_vms`, `create_vm`, `start_vm`, `stop_vm`, `restart_vm`, `status`, `connect`, `help`.

### Source Chain

When you run `vde`, it sources libraries in the following order (per §4.1 of VDE-SPEC.md v1.4.0):

```bash
# 1. vde-shell-compat - Shell portability
source "$VDE_ROOT_DIR/lib/vde-shell-compat"

# 2. vde-constants - Return codes, constants
source "$VDE_ROOT_DIR/lib/vde-constants"

# 3. vde-errors - Error messages
source "$VDE_ROOT_DIR/lib/vde-errors"

# 4. vde-log - Logging system
source "$VDE_ROOT_DIR/lib/vde-log"

# 5. vde-naming - Name validation and generation
source "$VDE_ROOT_DIR/lib/vde-naming"

# 6. vde-security - Security validation
source "$VDE_ROOT_DIR/lib/vde-security"

# 7. vde-core - Core VM operations
source "$VDE_ROOT_DIR/lib/vde-core"

# 8. vm-common - Full VDE API (SSH/Docker/templates)
source "$VDE_ROOT_DIR/lib/vm-common"

# 9. vde-commands - High-level command wrappers
source "$VDE_ROOT_DIR/lib/vde-commands"

# 10. vde-parser - Natural language parser (available via 'vde ask')
source "$VDE_ROOT_DIR/lib/vde-parser"
```

**Dispatch model:** `vde` uses direct script dispatch for all standard commands. The parser is available as an additive interface via `vde ask <natural language input>`.

### Examples

```bash
# List all VMs
vde list

# Create and start a Python VM
vde create python
vde start python

# Start multiple VMs with rebuild
vde start python rust --rebuild

# Stop all VMs
vde stop all

# Check system health
vde health
```

---

## Part 5: Template System

The VDE uses **template variable substitution** to generate docker-compose.yml files.

### 5.1 Language Template (`templates/compose-language.yml`)

```yaml
services:
  {{NAME}}-dev:                    # e.g., "vde-go"
    build:
      context: ../../..
      dockerfile: configs/docker/vde-base.Dockerfile
      args:
        USERNAME: devuser
        UID: 1000
        GID: 1000
        PUBLIC_KEYS_DIR: /public-ssh-keys
    image: dev-{{NAME}}:latest      # e.g., "dev-go:latest"
    container_name: {{NAME}}-dev    # e.g., "vde-go"
    hostname: {{NAME}}-dev
    restart: unless-stopped
    command: sh -c "{{INSTALL_CMD}} && /usr/sbin/sshd -D"

    ports:
      - "{{SSH_PORT}}:22"          # e.g., "2205:22"

    volumes:
      - ../../../projects/{{NAME}}:/home/devuser/workspace
      - ../../../logs/{{NAME}}:/logs
      - ../../../public-ssh-keys:/public-ssh-keys:ro

    env_file:
      - ../../../env-files/{{NAME}}.env

    networks:
      - vde-net
```

### 5.2 Service Template (`templates/compose-service.yml`)

```yaml
services:
  {{NAME}}:
    # ... (same build config)
    container_name: vde-{{NAME}}    # e.g., "vde-postgres" (§5.2: always vde- prefix)

    ports:
      - "{{SSH_PORT}}:22"          # SSH access
      - "{{SERVICE_PORT}}:{{SERVICE_PORT}}"  # Service port(s)

    volumes:
      - ../../../data/{{NAME}}:/data   # Note: "data" not "projects"
      - ../../../logs/{{NAME}}:/logs
      # ...

    networks:
      - vde-net

    labels:                        # §5.2: Required VDE metadata labels
      - "vde.type=service"
      - "vde.name={{NAME}}"
```

### 5.3 Named Template Renderers (§3.8)

VDE-SPEC.md §3.8 defines three named renderer functions implemented in `lib/vde-templates` as wrappers over the generic `render_template()`:

```bash
# Generate a language VM compose file
render_language_template "go" "2205"

# Generate a service VM compose file
render_service_template "postgres" "2400" "5432"

# Generate an SSH config entry block
render_ssh_entry "python" "2213"
```

These named functions ensure spec-compliant output with correct template paths and argument conventions.

### 5.4 Template Rendering

```bash
render_template() {
    local template_file=$1
    shift  # Remaining args are var=value pairs

    local content=$(cat "$template_file")

    # Parse variable pairs
    while [[ $# -ge 2 ]]; do
        local var_name="$1"
        local var_value="$2"
        shift 2

        # Escape special characters for sed
        var_value=$(printf '%s\n' "$var_value" | sed 's/[&/\]/\\&/g')

        # Replace {{VAR_NAME}} with value
        content=$(echo "$content" | sed "s/{{$var_name}}/$var_value/g")
    done

    echo "$content"
}
```

**Usage:**
```bash
render_template "$template_file" \
    NAME "go" \
    SSH_PORT "2205" \
    INSTALL_CMD "apt-get update -y && apt-get install -y golang-go" \
    SERVICE_PORT "" \
    > "$output_file"
```

---

## Part 6: Port Allocation System

One of the most sophisticated parts of VDE is **automatic port allocation**.

### 6.1 Getting Allocated Ports

```bash
get_allocated_ports() {
    local range_start=$1  # e.g., 2200
    local range_end=$2    # e.g., 2299

    local ports=()

    # Scan all docker-compose.yml files in configs/docker/
    for compose_dir in "$CONFIGS_DIR"/*/; do
        compose_file="$compose_dir/docker-compose.yml"

        if [[ -f "$compose_file" ]]; then
            while IFS= read -r line; do
                # Match "XXXX:22" port mapping
                if [[ "$line" =~ ([0-9]+):22 ]]; then
                    local port="$match[1]"  # Zsh regex capture

                    # Only add if in range
                    if [[ $port -ge $range_start && $port -le $range_end ]]; then
                        ports+=("$port")
                    fi
                fi
            done < "$compose_file"
        fi
    done

    # Sort, deduplicate, output
    printf '%s\n' "${ports[@]}" | sort -n | uniq
}
```

**What this does:**
1. Scans every `configs/docker/*/docker-compose.yml`
2. Finds lines like `- "2205:22"`
3. Extracts the SSH port (2205)
4. Returns sorted list of all allocated ports

### 6.2 Finding Next Available Port

```bash
find_next_available_port() {
    local vm_type=$1  # "lang" or "service"
    local range_start range_end

    # Select range based on type
    case "$vm_type" in
        lang)  range_start=2200; range_end=2299 ;;
        service) range_start=2400; range_end=2499 ;;
    esac

    # Get all allocated ports in this range
    local -a allocated_ports
    allocated_ports=($(get_allocated_ports "$range_start" "$range_end"))

    # Find first unused port
    for ((port=range_start; port<=range_end; port++)); do
        if [[ ! " ${allocated_ports[@]} " =~ " ${port} " ]]; then
            echo "$port"
            return 0
        fi
    done

    log_error "No available ports in range $range_start-$range_end"
    return 1
}
```

**Example flow:**
```
Existing VMs:
- vde-python: SSH_PORT=2222
- vde-js: SSH_PORT=2224

get_allocated_ports 2200 2299
=> Returns: 2222, 2224

find_next_available_port lang
=> Checks 2200 (free), 2201 (free), ..., 2222 (taken)
=> Returns: 2200
```

---

## Part 7: Complete Lifecycle - Creating a Go VM

Let's trace exactly what happens when you run:

```bash
vde create go
```

This invokes the `vde` script which sources all libraries and then calls the VM creation logic.

### Step 2: Script Entry (create-virtual-for)

```bash
#!/usr/bin/env zsh
set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/lib/vm-common"  # Load all functions, parse vm-types.conf
```

At this point, memory contains:
```
VM_TYPE[go]=lang
VM_ALIASES[go]=golang
VM_DISPLAY[go]=Go
VM_INSTALL[go]=apt-get update -y && apt-get install -y golang-go
VM_SVC_PORT[go]=
```

### Step 3: Validation

```bash
VM_NAME="$1"  # "go"

validate_vm_name "$VM_NAME"
# Checks: is "go" lowercase alphanumeric? Yes.

RESOLVED_NAME=$(resolve_vm_name "$VM_NAME" || true)
# Checks: is "go" a known VM? Yes. Returns "go".

validate_vm_doesnt_exist "$VM_NAME"
# Checks: does configs/docker/go/docker-compose.yml exist? No.

validate_ssh_key_exists
# Checks: does ~/.ssh/vde/id_ed25519 exist? Yes.
```

### Step 4: Query VM Configuration

```bash
VM_TYPE=$(get_vm_info type "$VM_NAME")         # "lang"
VM_DISPLAY=$(get_vm_info display "$VM_NAME")   # "Go"
VM_INSTALL=$(get_vm_info install "$VM_NAME")   # "apt-get update -y && apt-get install -y golang-go"
VM_SVC_PORT=$(get_vm_info svc_port "$VM_NAME") # "" (empty for languages)
```

### Step 5: Allocate SSH Port

```bash
SSH_PORT=$(find_next_available_port "$VM_TYPE")
# Scans configs/docker/*/docker-compose.yml
# Finds: vde-python (2222), vde-js (2224), vde-rust (2223)
# Returns: 2200 (first available in 2200-2299)

log_info "Allocated SSH port: 2200"
```

### Step 6: Create Directories

```bash
ensure_vm_directories "$VM_NAME" "$VM_TYPE"
# Creates:
# - configs/docker/go/
# - projects/go/
# - logs/go/
```

### Step 7: Generate docker-compose.yml

```bash
template_file="$TEMPLATES_DIR/compose-language.yml"
compose_file="$CONFIGS_DIR/$VM_NAME/docker-compose.yml"

render_template "$template_file" \
    NAME "go" \
    SSH_PORT "2200" \
    INSTALL_CMD "apt-get update -y && apt-get install -y golang-go" \
    SERVICE_PORT "" \
    > "$compose_file"
```

**Template substitution:**
```yaml
# Before:
services:
  {{NAME}}-dev:
    ports:
      - "{{SSH_PORT}}:22"
    command: sh -c "{{INSTALL_CMD}} && /usr/sbin/sshd -D"

# After:
services:
  vde-go:
    ports:
      - "2200:22"
    command: sh -c "apt-get update -y && apt-get install -y golang-go && /usr/sbin/sshd -D"
```

### Step 8: Create Environment File

```bash
env_file="$VDE_ROOT_DIR/env-files/$VM_NAME.env"

cat > "$env_file" <<EOF
SSH_PORT=2200
EOF
```

### Step 9: Update SSH Config

```bash
ssh_host="${VM_NAME}-dev"  # "vde-go" (language VMs get -dev suffix)

merge_ssh_config_entry "$ssh_host" "2200" "Go"
# 1. Backs up ~/.ssh/vde/config to ~/dev/backup/ssh/config.backup.TIMESTAMP
# 2. Generates SSH entry from template
# 3. Appends to ~/.ssh/vde/config
```

**Generated SSH entry:**
```ssh-config
# Python Dev VM
Host vde-python
    HostName localhost
    Port 2214
    User devuser
    IdentityFile ~/.ssh/vde/id_ed25519
    IdentitiesOnly yes
```

### Step 10: Summary Output

```
[SUCCESS] VM configuration complete!

Created files:
  - configs/docker/go/docker-compose.yml
  - env-files/go.env
  - projects/go/
  - logs/go/

SSH Configuration:
  - Host alias: vde-go
  - SSH port: 2200
  - Connect with: ssh vde-go

Next steps:
  1. Review and customize env-files/go.env if needed
  2. Start the VM: vde start go
  3. Connect: ssh vde-go
```

---

## Part 8: Starting the VM

Now you run:

```bash
vde start go
```

### Script Flow (start-virtual)

```bash
# 1. Load library
source "$SCRIPT_DIR/lib/vm-common"

# 2. Parse arguments
VMS=()  # Array of VM names to start
rebuild=false
nocache=false

# 3. Resolve VM name
resolved=$(resolve_vm_name "go")  # Returns "go"
VMS+=("go")

# 4. Start each VM
for vm in "${VMS[@]}"; do
    start_vm "$vm" "$rebuild" "$nocache"
done
```

### start_vm Function (vm-common)

```bash
start_vm() {
    local vm=$1          # "go"
    local rebuild=$2     # false
    local nocache=$3     # false

    compose_file="$CONFIGS_DIR/$vm/docker-compose.yml"

    # Build docker-compose options
    if [[ "$rebuild" == "true" ]]; then
        opts="--build"
        if [[ "$nocache" == "true" ]]; then
            opts="$opts --no-cache"
        fi
    fi

    # Start container
    docker-compose -f "$compose_file" up -d $opts
}
```

**What docker-compose does:**

1. **Build image** (if needed):
   ```bash
   docker build \
     -f configs/docker/vde-base.Dockerfile \
     --build-arg USERNAME=devuser \
     --build-arg UID=1000 \
     --build-arg GID=1000 \
     --build-arg PUBLIC_KEYS_DIR=/public-ssh-keys \
     -t dev-go:latest \
     .
   ```

2. **Create container**:
   ```bash
   docker create \
     --name vde-go \
     --hostname vde-go \
     --restart unless-stopped \
     -p 2200:22 \
     -v ~/dev/projects/go:/home/devuser/workspace \
     -v ~/dev/logs/go:/logs \
     -v ~/dev/public-ssh-keys:/public-ssh-keys:ro \
     --env-file ~/dev/env-files/go.env \
     --network vde-net \
     dev-go:latest \
     sh -c "apt-get update -y && apt-get install -y golang-go && /usr/sbin/sshd -D"
   ```

3. **Start container**: `docker start vde-go`

### Container Boot Sequence

Inside the container:

```bash
# 1. Execute the command
sh -c "apt-get update -y && apt-get install -y golang-go && /usr/sbin/sshd -D"

# 2. Install Go (takes ~30 seconds)
# - apt-get update
# - apt-get install golang-go

# 3. Start SSH daemon
/usr/sbin/sshd -D  # -D = no daemonize, run in foreground
```

Now the container is running with:
- **SSH accessible** on localhost:2213
- **Go installed** and available to devuser
- **Workspace mounted** at `/home/devuser/workspace`

---

## Part 9: SSH Connection

You can now connect:

```bash
ssh vde-go
```

### SSH Connection Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. SSH Client reads ~/.ssh/vde/config                              │
│    Finds "Host vde-go" entry                                   │
│    - HostName: localhost                                       │
│    - Port: 2200                                                │
│    - User: devuser                                             │
│    - IdentityFile: ~/.ssh/vde/id_ed25519                           │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. SSH connects to localhost:2213                              │
│    Port 2213 is mapped by Docker to vde-python:22                 │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. Container's sshd receives connection                        │
│    - Authenticates using public key from /public-ssh-keys      │
│    - Spawns shell as devuser                                   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. User gets zsh prompt                                        │
│    devuser@vde-go:~$                                           │
│                                                                 │
│    Environment:                                                │
│    - HOME: /home/devuser                                       │
│    - SHELL: /bin/zsh                                           │
│    - Workspace: /home/devuser/workspace (~/dev/projects/go)    │
│    - Go installed: /usr/bin/go                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Inside the Container

```bash
devuser@vde-go:~$ cd ~/workspace
devuser@vde-go:~/workspace$ ls -la
# Shows contents of ~/dev/projects/go on host

devuser@vde-go:~/workspace$ go version
# go version go1.21 debian

devuser@vde-go:~/workspace$ cat > main.go << 'EOF'
package main
import "fmt"
func main() {
    fmt.Println("Hello from VDE!")
}
EOF

devuser@vde-go:~/workspace$ go run main.go
Hello from VDE!
```

**Key point:** Files created in `~/workspace` are actually created in `~/dev/projects/go` on the host (via volume mount).

---

## Part 10: Service VMs (Different Pattern)

Service VMs (like PostgreSQL) work differently:

### Key Differences

| Aspect | Language VM | Service VM |
|--------|-------------|------------|
| Container name | `vde-go` | `vde-postgres` (canonical) |
| SSH host | `vde-go` | `vde-postgres` |
| SSH port range | 2200-2220 (21 languages) | 2400-2499 (7 services) |
| Volume mount | `projects/go/` | `data/postgres/` |
| Purpose | Development workspace | Persistent data |

### Example: PostgreSQL Service

**vm-types.conf entry:**
```bash
service|postgres|postgresql|PostgreSQL|apt-get update -y && apt-get install -y postgresql-client|5432
```

**Generated docker-compose.yml:**
```yaml
services:
  postgres:  # Note: no "-dev" suffix
    # ... (same build)
    container_name: postgres

    ports:
      - "2400:22"     # SSH access
      - "5432:5432"   # PostgreSQL access

    volumes:
      - ../../../data/postgres:/data  # Persistent data
      # ...
```

**Why this design:**
- **Language VMs**: You develop code in them, so they need a workspace directory
- **Service VMs**: They provide services (database, cache), so they need persistent data

---

## Part 11: Inter-Container Communication

All containers are on the `vde-net` Docker network, enabling communication:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ vde-python  │     │ vde-postgres │     │  vde-redis  │
│   :2214     │     │   :2404     │     │   :2406     │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                  │                  │
       └──────────────────┴──────────────────┘
                          │
                  ┌───────▼───────┐
                  │  vde-net  │
                  │ (bridge net)  │
                  └───────────────┘
```

**From vde-python container:**
```bash
# Connect to PostgreSQL
psql -h vde-postgres -U devuser -d mydb

# Connect to Redis
redis-cli -h vde-redis

# SSH to another container
ssh vde-go
```

**Service discovery works via container names** because Docker's embedded DNS resolves container names to IPs.

---

## Part 12: Multi-Container Management

The scripts support managing multiple VMs at once:

```bash
vde start python go rust postgres redis
```

**Special case: `all` keyword**

```bash
vde start all
```

This expands to all VMs that have been created (have docker-compose.yml files):

```bash
# Find all VMs
for compose_dir in configs/docker/*/; do
    vm_name=$(basename "$compose_dir")
    VMS+=("$vm_name")
done

# Start each
for vm in "${VMS[@]}"; do
    start_vm "$vm"
done
```

---

## Part 13: Stopping VMs

```bash
vde stop go
```

**Internally:**
```bash
stop_vm() {
    local vm=$1
    compose_file="$CONFIGS_DIR/$vm/docker-compose.yml"

    docker-compose -f "$compose_file" down
}
```

**What `docker-compose down` does:**
1. Stops the container: `docker stop vde-go`
2. Removes the container: `docker rm vde-go`
3. **Does NOT remove** the image (dev-go:latest persists)
4. **Does NOT remove** volumes (data persists on host)

---

## Part 14: Adding New VM Types

New VM types can be added by editing `vm-types.conf` directly or using the vde command:

```bash
```

**Flow:**

2. **Backup** vm-types.conf
3. **Append** line:
   ```bash
   ```
4. **Reload** VM types: `source lib/vm-common` → `load_vm_types`
5. **Show diff** of changes

Now you can:
```bash
```

---

## Summary: Complete Data Flow

```
User Action:
  vde create go

↓

Script Entry:
  vde create sources lib/vm-common
  ↓
  load_vm_types parses vm-types.conf
  ↓
  Associative arrays populated:
    VM_TYPE[go]=lang
    VM_DISPLAY[go]=Go
    VM_INSTALL[go]=apt-get install golang-go

↓

Validation:
  validate_vm_name "go" ✓
  resolve_vm_name "go" → "go" ✓
  validate_vm_doesnt_exist "go" ✓
  validate_ssh_key_exists ✓

↓

Configuration:
  VM_TYPE=$(get_vm_info type "go") → "lang"
  VM_INSTALL=$(get_vm_info install "go") → "apt-get install golang-go"

↓

Port Allocation:
  find_next_available_port "lang"
  ↓
  Scan configs/docker/*/docker-compose.yml for SSH ports
  ↓
  Find first available in 2200-2299
  ↓
  Return: 2200

↓

File Generation:
  1. Create directories:
     - configs/docker/go/
     - projects/go/
     - logs/go/

  2. Generate docker-compose.yml:
     render_template compose-language.yml \
       NAME "go" \
       SSH_PORT "2200" \
       INSTALL_CMD "apt-get install golang-go"

  3. Create env-files/go.env:
     SSH_PORT=2200

  4. Update ~/.ssh/vde/config:
     Append Host vde-go entry

↓

Output:
  [SUCCESS] VM configuration complete!
  Connect with: ssh vde-go

↓

Start VM:
  vde start go
  ↓
  docker-compose -f configs/docker/go/docker-compose.yml up -d
  ↓
  Docker builds image (dev-go:latest)
  ↓
  Docker creates container (vde-go)
  ↓
  Docker starts container
  ↓
  Container runs: apt-get install golang-go && /usr/sbin/sshd -D

↓

Connect:
  ssh vde-go
  ↓
  SSH connects to localhost:2213
  ↓
  Container's sshd authenticates
  ↓
  User gets shell as devuser
```

---

## Key Design Principles

1. **Data-Driven**: All VM types defined in one config file
2. **Template-Based**: docker-compose.yml generated from templates
3. **Modular Libraries**: Separated concerns (shell-compat, constants, errors, log, core, parser, commands)
4. **Auto-Port-Allocation**: No manual port management
5. **SSH-First**: Everything accessible via SSH
6. **Unified CLI**: Single `vde` command for all operations
7. **Shell-Portable**: Works on zsh 5.0+, bash 4.0+, bash 3.x (with fallbacks)
8. **Volume-Mounted**: Code persists on host, containers are ephemeral
9. **Networked**: All containers on vde-net for inter-communication
10. **Extensible**: Add new languages/services by editing one file
11. **Idempotent**: Safe to run create-virtual-for multiple times (fails if exists)

---

## File Reference

### Core Library Files

| File | Purpose |
|------|---------|
| `lib/vde-shell-compat` | Shell detection, portable associative arrays, date/time operations |
| `lib/vde-constants` | Standardized return codes (VDE_SUCCESS=0 … VDE_ERR_LOCK=9), port ranges, timeouts |
| `lib/vde-errors` | Contextual error messages with remediation steps |
| `lib/vde-log` | Structured logging (text/JSON/syslog), rotation, query functions |
| `lib/vde-naming` | Name validation and normalization (loaded 5th in vde) |
| `lib/vde-security` | Security validation, key permissions (loaded 6th in vde) |
| `lib/vde-core` | Essential VM operations, type loading with caching |
| `lib/vm-common` | Full VDE API including SSH, Docker, templates |
| `lib/vde-commands` | High-level command wrappers; §3.5 `vde_list_vms`, `vde_create_vm`, etc. |
| `lib/vde-parser` | Pattern-based natural language parser; `generate_plan` / `execute_plan` |
| `lib/vde-docker` | Docker operations; §3.7 `docker_*` aliases over internal functions |
| `lib/vde-templates` | Template rendering; §3.8 `render_language_template`, `render_service_template`, `render_ssh_entry` |
| `lib/vde-ssh` | SSH key management, `validate_or_create_ssh_key`, config generation |

### Core Scripts

| File | Purpose |
|------|---------|
| `bin/vde` | Unified CLI command for all VDE operations |
| `bin/vde-ask` | Natural language interface — routes input through vde-parser |
| `data/vm-types.conf` | VM type definitions (19 languages + 7 services) |

### Templates

| File | Purpose |
|------|---------|
| `templates/compose-language.yml` | Template for language VM docker-compose.yml |
| `templates/compose-service.yml` | Template for service VM docker-compose.yml |
| `templates/ssh-entry.txt` | Template for SSH config entry |

### Generated Files (When VM Created)

| File | Purpose |
|------|---------|
| `configs/docker/<name>/docker-compose.yml` | Docker Compose configuration |
| `env-files/<name>.env` | Environment variables |
| `projects/<name>/` | Language VM workspace directory |
| `data/<name>/` | Service VM data directory |
| `logs/<name>/` | Log directory |
| `~/.ssh/vde/config` | SSH configuration (entry appended) |

---

This is the complete VDE system from configuration to container runtime. Every piece serves a specific purpose in the overall architecture of providing isolated, consistent development environments.

The system has evolved from a simple template-based approach to a sophisticated modular architecture with:
- **Shell portability** across zsh, bash 4.0+, and bash 3.x
- **Modular libraries** that can be sourced independently (10-library load chain)
- **Unified CLI** through the `vde` command with direct script dispatch
- **Natural language interface** via `vde ask` (parser as additive capability)
- **Spec-compliant function aliases** — §3.7 `docker_*`, §3.8 `render_*_template`
- **Labelled service containers** — `vde.type=service` / `vde.name=` Docker labels (§5.2)
- **Structured logging** with rotation and query capabilities
- **Contextual error messages** with remediation steps
- **19 language VMs** and **7 service VMs** supported out of the box

> **Spec version:** This document reflects VDE-SPEC.md v1.4.0 and ARCHITECTURE.md current revision.


---

## Function Map: `vde create python`

**Command:** `vde create python`  
**Entry Point:** [`bin/vde`](../bin/vde)  
**Completion:** Docker container `vde-python` running, SSH config updated, state saved

---

### Phase 0: Shell Startup & Library Loading

When the user hits Enter, the OS forks a new zsh process and executes [`bin/vde`](../bin/vde).

#### Files Sourced (in order)

| # | File | Guard Variable | Purpose |
|---|------|---------------|---------|
| 1 | [`lib/vde-shell-compat`](../lib/vde-shell-compat) | `_VDE_SHELL_COMPAT_LOADED` | Portable shell operations |
| 2 | [`lib/vde-constants`](../lib/vde-constants) | `_VDE_CONSTANTS_LOADED` | All constants, port ranges, SSH dirs |
| 3 | [`lib/vde-errors`](../lib/vde-errors) | `_VDE_ERRORS_LOADED` | Error message functions |
| 4 | [`lib/vde-log`](../lib/vde-log) | `_VDE_LOG_LOADED` | Structured logging |
| 5 | [`lib/vde-core`](../lib/vde-core) | `_VDE_CORE_GUARD_LOADED` | Core VM type queries, schema validation |
| 6 | [`lib/vm-common`](../lib/vm-common) | `_VM_COMMON_LOADED` | Full VM management (sources 7–12 below) |
| 7 | ↳ [`lib/vde-log`](../lib/vde-log) | (already loaded) | |
| 8 | ↳ [`lib/vde-shell-compat`](../lib/vde-shell-compat) | (already loaded) | |
| 9 | ↳ [`lib/vde-constants`](../lib/vde-constants) | (already loaded) | |
| 10 | ↳ [`lib/vde-errors`](../lib/vde-errors) | (already loaded) | |
| 11 | ↳ [`lib/vde-naming`](../lib/vde-naming) | `_VDE_NAMING_LOADED` | `vde-` prefix enforcement |
| 12 | ↳ [`lib/vde-security`](../lib/vde-security) | `_VDE_SECURITY_LOADED` | Security policy enforcement |
| 13 | ↳ [`lib/vde-path-utils`](../lib/vde-path-utils) | `_VDE_PATH_UTILS_LOADED` | Path utilities |
| 14 | ↳ [`lib/vde-core`](../lib/vde-core) | (already loaded) | |
| 15 | [`lib/vde-docker-state`](../lib/vde-docker-state) | `_VDE_DOCKER_STATE_LOADED` | Docker state persistence |

**vm-common auto-initialization (at source time):**

| Function | File | Purpose |
|----------|------|---------|
| `load_vm_types()` | [`lib/vm-common`](../lib/vm-common:248) | Load VM type definitions from JSON/cache |
| ↳ `_is_cache_valid()` | [`lib/vm-common`](../lib/vm-common:216) | Check if `.cache/vm-types.cache` is fresh |
| ↳ `vde_get_schema_for_json()` | [`lib/vde-core`](../lib/vde-core) | Find JSON schema file |
| ↳ `vde_validate_json_schema()` | [`lib/vde-core`](../lib/vde-core) | Validate `vm-types.json` against schema |
| `_vm_common_load_modular_libs()` | [`lib/vm-common`](../lib/vm-common:155) | Lazy-load SSH, Docker, Templates libs |
| ↳ `_vde_ssh_source()` | [`lib/vm-common`](../lib/vm-common:130) | Source [`lib/vde-ssh`](../lib/vde-ssh) |
| ↳ `_vde_docker_source()` | [`lib/vm-common`](../lib/vm-common:138) | Source [`lib/vde-docker`](../lib/vde-docker) |
| ↳ `_vde_templates_source()` | [`lib/vm-common`](../lib/vm-common:146) | Source [`lib/vde-templates`](../lib/vde-templates) |

**Files read during `load_vm_types()`:**

| File | Condition |
|------|-----------|
| [`data/vm-types.json`](../data/vm-types.json) | Always (primary config) |
| [`.cache/vm-types.cache`](../.cache/vm-types.cache) | If cache is valid (skips JSON parse) |
| [`.cache/vm-types.cache`](../.cache/vm-types.cache) | Written if cache was stale/missing |

---

### Phase 1: `bin/vde` — Argument Parsing & Dispatch

#### Functions Called in `bin/vde`

| Step | Function | File | Purpose |
|------|----------|------|---------|
| 1 | `vde_log_init()` | [`lib/vde-log`](../lib/vde-log:46) | Initialize log directory and file |
| 2 | *(argument parsing loop)* | [`bin/vde`](../bin/vde:319) | Parse `create` and `python` from `$@` |
| 3 | `vde_find_command_script()` | [`bin/vde`](../bin/vde:181) | Map `"create"` → `bin/create-virtual-for` |
| 4 | `vde_run_command()` | [`bin/vde`](../bin/vde:278) | Validate script exists, make executable |
| 5 | `vde_log_info()` | [`lib/vde-log`](../lib/vde-log:222) | Log `"Running command: create python"` |
| 6 | *(exec)* | [`bin/vde`](../bin/vde:306) | Fork: `bin/create-virtual-for python` |

**Files touched:**
- [`logs/vde.log`](../logs/vde.log) — written by `vde_log_init()` and `vde_log_info()`

---

### Phase 2: `bin/create-virtual-for python` — VM Creation

#### 2a. Library Loading (create-virtual-for sources vm-common)

| File | Purpose |
|------|---------|
| [`lib/vm-common`](../lib/vm-common) | (all libs above, already loaded via source guard) |
| [`lib/vde-progress`](../lib/vde-progress) | Progress indicators |
| [`lib/vde-errors`](../lib/vde-errors) | Error messages |
| [`lib/vde-naming`](../lib/vde-naming) | Naming convention helpers |

#### 2b. Validation Phase

| Step | Function | File | Purpose |
|------|----------|------|---------|
| 1 | `vde_progress_info()` | [`lib/vde-progress`](../lib/vde-progress:356) | Print "Validating configuration for 'python'..." |
| 2 | `resolve_vm_name()` | [`lib/vm-common`](../lib/vm-common:832) | Resolve `"python"` → canonical name (checks `VM_TYPE`, aliases) |
| 3 | `get_vm_info()` | [`lib/vm-common`](../lib/vm-common:677) | Get `type` field → `"lang"` |
| 4 | `get_vm_info()` | [`lib/vm-common`](../lib/vm-common:677) | Get `display` field → `"Python"` |
| 5 | `get_vm_info()` | [`lib/vm-common`](../lib/vm-common:677) | Get `install` field → install command |
| 6 | `get_vm_info()` | [`lib/vm-common`](../lib/vm-common:677) | Get `svc_port` field → `""` (lang VM has none) |
| 7 | `validate_vm_name()` | [`lib/vm-common`](../lib/vm-common:865) → `vde_validate_name()` | Validate name format |
| 8 | `vde_validate_name()` | [`lib/vde-naming`](../lib/vde-naming:21) | Check `^[a-z0-9-]+$` pattern |
| 9 | `vm_exists()` | [`lib/vm-common`](../lib/vm-common:782) → `vm_is_created()` | Check `.docker-state/python.json` |
| 10 | `vm_is_created()` | [`lib/vm-common`](../lib/vm-common:756) | Check if `.docker-state/python.json` exists |
| 11 | `get_docker_state_dir()` | [`lib/vm-common`](../lib/vm-common:1070) | Returns `$VDE_ROOT_DIR/.docker-state` |

**Files read:**
- [`.docker-state/python.json`](../.docker-state/python.json) — checked for existence (must NOT exist)

#### 2c. Port Allocation

| Step | Function | File | Purpose |
|------|----------|------|---------|
| 1 | `vde_progress_info()` | [`lib/vde-progress`](../lib/vde-progress:356) | Print "Allocating SSH port..." |
| 2 | `find_next_available_port()` | [`lib/vm-common`](../lib/vm-common:944) | Find next free port in 2200-2299 |
| 3 | `find_available_port()` | [`lib/vm-common`](../lib/vm-common:969) | Iterate ports, check each |
| 4 | `_is_port_in_use()` | [`lib/vde-docker`](../lib/vde-docker:212) | `nc -z localhost $port` or check registry |

**Files read:**
- [`.cache/port-registry/`](../.cache/port-registry/) — per-VM `.port` files checked

#### 2d. Directory Creation

| Step | Function | File | Purpose |
|------|----------|------|---------|
| 1 | `vde_progress_info()` | [`lib/vde-progress`](../lib/vde-progress:356) | Print "Creating directory structure..." |
| 2 | `ensure_vm_directories()` | [`lib/vm-common`](../lib/vm-common:1141) | Create required dirs |
| 3 | `vde_normalize_name()` | [`lib/vde-naming`](../lib/vde-naming:54) | Strip `vde-` prefix → `"python"` |

**Files/directories created:**
- [`configs/docker/python/`](../configs/docker/python/) — config dir (if absent)
- [`projects/python/`](../projects/python/) — workspace dir (if absent)
- [`logs/python/`](../logs/python/) — log dir (if absent)

#### 2e. Docker Compose File Generation

| Step | Function | File | Purpose |
|------|----------|------|---------|
| 1 | `vde_progress_info()` | [`lib/vde-progress`](../lib/vde-progress:356) | Print "Creating docker-compose.yml..." |
| 2 | `vde_normalize_name()` | [`lib/vde-naming`](../lib/vde-naming:54) | `"python"` → `"python"` (raw name for path) |
| 3 | `render_template()` | [`lib/vde-templates`](../lib/vde-templates:49) | Render `compose-language.yml` with vars |
| 4 | `vde_progress_done()` | [`lib/vde-progress`](../lib/vde-progress:345) | Print "Created: configs/docker/python/docker-compose.yml" |

**Files read:**
- [`templates/compose-language.yml`](../templates/compose-language.yml) — template source

**Files written:**
- [`configs/docker/python/docker-compose.yml`](../configs/docker/python/docker-compose.yml) — rendered compose file

#### 2f. Environment File Creation

| Step | Function | File | Purpose |
|------|----------|------|---------|
| 1 | `vde_progress_info()` | [`lib/vde-progress`](../lib/vde-progress:356) | Print "Creating environment file..." |
| 2 | *(heredoc write)* | [`bin/create-virtual-for`](../bin/create-virtual-for:229) | Write env vars to file |
| 3 | `vde_progress_done()` | [`lib/vde-progress`](../lib/vde-progress:345) | Print "Created: env-files/python.env" |

**Files written:**
- [`env-files/python.env`](../env-files/python.env) — SSH_PORT, DATABASE_URL, REDIS_HOST, etc.

#### 2g. SSH Config Update

| Step | Function | File | Purpose |
|------|----------|------|---------|
| 1 | `vde_progress_info()` | [`lib/vde-progress`](../lib/vde-progress:356) | Print "Updating SSH configuration..." |
| 2 | `vde_get_ssh_host()` | [`lib/vde-naming`](../lib/vde-naming:72) | Returns `"vde-python"` |
| 3 | `merge_ssh_config_entry()` | [`lib/vde-ssh`](../lib/vde-ssh:299) | Atomically add SSH Host block |

**Inside `merge_ssh_config_entry()`:**

| Step | Function | File | Purpose |
|------|----------|------|---------|
| 1 | *(backup)* | [`lib/vde-ssh`](../lib/vde-ssh) | `cp ~/.ssh/vde/config → backup/ssh/config.backup.TIMESTAMP` |
| 2 | *(duplicate check)* | [`lib/vde-ssh`](../lib/vde-ssh) | `grep "^Host vde-python"` in config |
| 3 | *(atomic write)* | [`lib/vde-ssh`](../lib/vde-ssh) | `mktemp` → append → `mv` → `chmod 600` |

**Files read/written:**
- [`~/.ssh/vde/config`](~/.ssh/vde/config) — VDE SSH config (read + written)
- [`backup/ssh/config.backup.TIMESTAMP`](../backup/ssh/) — timestamped backup (written)
- [`configs/ssh/config`](../configs/ssh/config) — project reference copy (written via `cp`)

#### 2h. VM Start (default: `START_VM=true`)

| Step | Function | File | Purpose |
|------|----------|------|---------|
| 1 | `vde_progress_info()` | [`lib/vde-progress`](../lib/vde-progress:356) | Print "Starting VM..." |
| 2 | *(exec)* | [`bin/create-virtual-for`](../bin/create-virtual-for:278) | `docker-compose -f configs/docker/python/docker-compose.yml up -d` |
| 3 | `vde_progress_done()` | [`lib/vde-progress`](../lib/vde-progress:345) | Print "Started VM: python" |
| 4 | `save_docker_state()` | [`lib/vm-common`](../lib/vm-common:1076) | Write state JSON to `.docker-state/` |
| 5 | `get_docker_state_dir()` | [`lib/vm-common`](../lib/vm-common:1070) | Returns `.docker-state/` path |
| 6 | `vde_normalize_name()` | [`lib/vde-naming`](../lib/vde-naming:54) | `"python"` → `"python"` for filename |

**Files written:**
- [`.docker-state/python.json`](../.docker-state/python.json) — VM state (name, type, port, status, created_at)

#### 2i. Summary Output

| Step | Function | File | Purpose |
|------|----------|------|---------|
| 1 | `vde_success()` | [`lib/vde-errors`](../lib/vde-errors:299) | Print "VM configuration complete!" |

---

### Complete Function Call Tree

```
vde create python
│
├── [bin/vde]
│   ├── source vde-shell-compat
│   ├── source vde-constants
│   ├── source vde-errors
│   ├── source vde-log
│   ├── source vde-core
│   │   ├── source vde-shell-compat (guard: skip)
│   │   └── source vde-constants (guard: skip)
│   ├── source vm-common
│   │   ├── source vde-log (guard: skip)
│   │   ├── source vde-shell-compat (guard: skip)
│   │   ├── source vde-constants (guard: skip)
│   │   ├── source vde-errors (guard: skip)
│   │   ├── source vde-naming          ← NEW
│   │   ├── source vde-security        ← NEW
│   │   ├── source vde-path-utils
│   │   ├── source vde-core (guard: skip)
│   │   ├── load_vm_types()
│   │   │   ├── _is_cache_valid()
│   │   │   ├── vde_get_schema_for_json()
│   │   │   ├── vde_validate_json_schema()
│   │   │   └── [writes .cache/vm-types.cache if stale]
│   │   └── _vm_common_load_modular_libs()
│   │       ├── _vde_ssh_source() → source vde-ssh
│   │       ├── _vde_docker_source() → source vde-docker
│   │       └── _vde_templates_source() → source vde-templates
│   ├── source vde-docker-state
│   ├── vde_log_init()
│   ├── [parse args: CMD="create", args=["python"]]
│   ├── vde_find_command_script("create") → "bin/create-virtual-for"
│   ├── vde_run_command("create", "python")
│   │   └── vde_log_info("Running command: create python")
│   └── exec: bin/create-virtual-for python
│
└── [bin/create-virtual-for python]
    ├── source vm-common (guard: skip — already loaded)
    ├── source vde-progress
    ├── source vde-errors (guard: skip)
    ├── source vde-naming (guard: skip)
    │
    ├── vde_progress_info("Validating...")
    ├── resolve_vm_name("python")
    │   └── [checks VM_TYPE["python"], VM_TYPE["vde-python"], aliases]
    ├── get_vm_info("type", "python") → "lang"
    ├── get_vm_info("display", "python") → "Python"
    ├── get_vm_info("install", "python") → install cmd
    ├── get_vm_info("svc_port", "python") → ""
    ├── validate_vm_name("python", "lang")
    │   └── vde_validate_name("python")
    ├── vm_exists("python")
    │   └── vm_is_created("python")
    │       └── get_docker_state_dir() → ".docker-state"
    │           [reads: .docker-state/python.json — must NOT exist]
    │
    ├── vde_progress_info("Allocating SSH port...")
    ├── find_next_available_port("lang")
    │   └── find_available_port(2200, 2299)
    │       └── _is_port_in_use(2213..N)
    │           [reads: .cache/port-registry/*.port, nc -z localhost PORT]
    │
    ├── vde_progress_info("Creating directory structure...")
    ├── ensure_vm_directories("python", "lang")
    │   └── vde_normalize_name("python") → "python"
    │   [creates: configs/docker/python/, projects/python/, logs/python/]
    │
    ├── vde_progress_info("Creating docker-compose.yml...")
    ├── vde_normalize_name("python") → "python"
    ├── render_template("templates/compose-language.yml", NAME=python, ...)
    │   [reads: templates/compose-language.yml]
    │   [writes: configs/docker/python/docker-compose.yml]
    ├── vde_progress_done("Created: configs/docker/python/docker-compose.yml")
    │
    ├── vde_progress_info("Creating environment file...")
    │   [writes: env-files/python.env]
    ├── vde_progress_done("Created: env-files/python.env")
    │
    ├── vde_progress_info("Updating SSH configuration...")
    ├── vde_get_ssh_host("python") → "vde-python"
    ├── merge_ssh_config_entry("vde-python", PORT, "Python", IDENTITY)
    │   [reads: ~/.ssh/vde/config]
    │   [writes: backup/ssh/config.backup.TIMESTAMP]
    │   [writes: ~/.ssh/vde/config (atomic: mktemp → mv → chmod 600)]
    │   [writes: configs/ssh/config (cp of updated config)]
    │
    ├── vde_progress_info("Starting VM...")
    ├── docker-compose -f configs/docker/python/docker-compose.yml up -d
    ├── vde_progress_done("Started VM: python")
    ├── save_docker_state("python", JSON)
    │   ├── get_docker_state_dir() → ".docker-state"
    │   └── vde_normalize_name("python") → "python"
    │   [writes: .docker-state/python.json]
    │
    └── vde_success("VM configuration complete!")
```

---

### All Files Touched

#### Read
| File | Phase | Purpose |
|------|-------|---------|
| [`lib/vde-shell-compat`](../lib/vde-shell-compat) | 0 | Sourced |
| [`lib/vde-constants`](../lib/vde-constants) | 0 | Sourced |
| [`lib/vde-errors`](../lib/vde-errors) | 0 | Sourced |
| [`lib/vde-log`](../lib/vde-log) | 0 | Sourced |
| [`lib/vde-core`](../lib/vde-core) | 0 | Sourced |
| [`lib/vm-common`](../lib/vm-common) | 0 | Sourced |
| [`lib/vde-naming`](../lib/vde-naming) | 0 | Sourced via vm-common |
| [`lib/vde-security`](../lib/vde-security) | 0 | Sourced via vm-common |
| [`lib/vde-path-utils`](../lib/vde-path-utils) | 0 | Sourced via vm-common |
| [`lib/vde-ssh`](../lib/vde-ssh) | 0 | Sourced via vm-common |
| [`lib/vde-docker`](../lib/vde-docker) | 0 | Sourced via vm-common |
| [`lib/vde-templates`](../lib/vde-templates) | 0 | Sourced via vm-common |
| [`lib/vde-docker-state`](../lib/vde-docker-state) | 0 | Sourced by vde |
| [`lib/vde-progress`](../lib/vde-progress) | 2 | Sourced by create-virtual-for |
| [`data/vm-types.json`](../data/vm-types.json) | 0 | VM type definitions |
| [`.cache/vm-types.cache`](../.cache/vm-types.cache) | 0 | VM type cache (if valid) |
| [`.cache/port-registry/*.port`](../.cache/port-registry/) | 2c | Port allocation check |
| [`.docker-state/python.json`](../.docker-state/python.json) | 2b | Existence check (must be absent) |
| [`templates/compose-language.yml`](../templates/compose-language.yml) | 2e | Docker compose template |
| [`~/.ssh/vde/config`](~/.ssh/vde/config) | 2g | SSH config (read before merge) |

#### Written / Created
| File | Phase | Purpose |
|------|-------|---------|
| [`logs/vde.log`](../logs/vde.log) | 1 | Command execution log |
| [`.cache/vm-types.cache`](../.cache/vm-types.cache) | 0 | Regenerated if stale |
| [`configs/docker/python/`](../configs/docker/python/) | 2d | Config directory |
| [`projects/python/`](../projects/python/) | 2d | Workspace directory |
| [`logs/python/`](../logs/python/) | 2d | Log directory |
| [`configs/docker/python/docker-compose.yml`](../configs/docker/python/docker-compose.yml) | 2e | Rendered compose file |
| [`env-files/python.env`](../env-files/python.env) | 2f | Environment variables |
| [`backup/ssh/config.backup.TIMESTAMP`](../backup/ssh/) | 2g | SSH config backup |
| [`~/.ssh/vde/config`](~/.ssh/vde/config) | 2g | Updated SSH config |
| [`configs/ssh/config`](../configs/ssh/config) | 2g | Project reference copy |
| [`.docker-state/python.json`](../.docker-state/python.json) | 2h | VM state record |

#### External Processes Spawned
| Process | Phase | Purpose |
|---------|-------|---------|
| `nc -z localhost PORT` | 2c | Port availability check |
| `jq` | 0 | JSON parsing of vm-types.json |
| `zsh -n .cache/vm-types.cache` | 0 | Cache syntax validation |
| `docker-compose up -d` | 2h | Start the container |
| `docker network inspect vde-net` | 0* | Network check (via vde-security) |

*`vde_security_init()` is called when `vde-security` is sourced via `vm-common`, which triggers `vde_security_ensure_network()` → `docker network inspect vde-net`.

---

### Summary: All Functions Fired

| # | Function | Library | Phase |
|---|----------|---------|-------|
| 1 | `vde_log_init()` | `vde-log` | 1 |
| 2 | `vde_find_command_script()` | `vde` | 1 |
| 3 | `vde_run_command()` | `vde` | 1 |
| 4 | `vde_log_info()` | `vde-log` | 1 |
| 5 | `load_vm_types()` | `vm-common` | 0 |
| 6 | `_is_cache_valid()` | `vm-common` | 0 |
| 7 | `vde_get_schema_for_json()` | `vde-core` | 0 |
| 8 | `vde_validate_json_schema()` | `vde-core` | 0 |
| 9 | `_vm_common_load_modular_libs()` | `vm-common` | 0 |
| 10 | `_vde_ssh_source()` | `vm-common` | 0 |
| 11 | `_vde_docker_source()` | `vm-common` | 0 |
| 12 | `_vde_templates_source()` | `vm-common` | 0 |
| 13 | `vde_security_init()` | `vde-security` | 0* |
| 14 | `vde_security_ensure_network()` | `vde-security` | 0* |
| 15 | `vde_security_enforce_permissions()` | `vde-security` | 0* |
| 16 | `vde_security_enforce_network_isolation()` | `vde-security` | 0* |
| 17 | `vde_progress_info()` | `vde-progress` | 2 |
| 18 | `resolve_vm_name()` | `vm-common` | 2b |
| 19 | `get_vm_info()` | `vm-common` | 2b |
| 20 | `validate_vm_name()` | `vm-common` | 2b |
| 21 | `vde_validate_name()` | `vde-naming` | 2b |
| 22 | `vm_exists()` | `vm-common` | 2b |
| 23 | `vm_is_created()` | `vm-common` | 2b |
| 24 | `get_docker_state_dir()` | `vm-common` | 2b |
| 25 | `find_next_available_port()` | `vm-common` | 2c |
| 26 | `find_available_port()` | `vm-common` | 2c |
| 27 | `_is_port_in_use()` | `vde-docker` | 2c |
| 28 | `ensure_vm_directories()` | `vm-common` | 2d |
| 29 | `vde_normalize_name()` | `vde-naming` | 2d, 2e, 2h |
| 30 | `render_template()` | `vde-templates` | 2e |
| 31 | `vde_progress_done()` | `vde-progress` | 2e, 2f, 2h |
| 32 | `vde_get_ssh_host()` | `vde-naming` | 2g |
| 33 | `merge_ssh_config_entry()` | `vde-ssh` | 2g |
| 34 | `save_docker_state()` | `vm-common` | 2h |
| 35 | `vde_success()` | `vde-errors` | 2i |

*Phase 0 = triggered at library source time, before argument parsing.


## Function Map: `vde create python` Execution Trace

### Context

This document provides a complete execution trace of the `vde create python` command, mapping every function call, library dependency, and file operation from user input to command completion. This provides comprehensive architectural understanding of VDE's VM creation pipeline.

**Command:** `vde create python`
**Entry Point:** [`bin/vde`](../bin/vde)
**Completion:** Docker container `vde-python` running, SSH config updated, state saved

---

### Phase 0: Entry Point & Bootstrap

**File**: [`bin/vde`](../bin/vde)

**Execution Flow**:
```
1. User executes: vde create python
2. Shebang invoked: #!/usr/bin/env zsh
3. VDE_ROOT_DIR="${0:a:h:h}" → ~/dev
4. Source libraries (lines 35-41):
   ├─ vde-shell-compat
   ├─ vde-constants
   ├─ vde-errors
   ├─ vde-log
   ├─ vde-core
   ├─ vm-common
   └─ vde-docker-state
5. vde_log_init() → Initialize logging system
```

**Functions Called**:
- `vde_log_init()` ([vde-log:44](../lib/vde-log#L44))

**Files Read**:
- [`lib/vde-shell-compat`](../lib/vde-shell-compat)
- [`lib/vde-constants`](../lib/vde-constants)
- [`lib/vde-errors`](../lib/vde-errors)
- [`lib/vde-log`](../lib/vde-log)
- [`lib/vde-core`](../lib/vde-core)
- [`lib/vm-common`](../lib/vm-common)
- [`lib/vde-docker-state`](../lib/vde-docker-state)

---

### Phase 1: Argument Parsing

**File**: [`bin/vde`](../bin/vde) (lines 314-427)

**Execution Flow**:
```
1. Parse global options (-v, --verbose, -q, --quiet, --help, --version)
2. CMD="create", shift to remaining args
3. Special create handling (lines 368-427):
   ├─ Check for --rebuild or --nocache flags
   ├─ If present: two-step process (create + start with rebuild)
   └─ If absent: normal create process
4. vde_run_command("create", "python")
   └─ vde_find_command_script("create") → returns bin/create-virtual-for
   └─ Execute: bin/create-virtual-for python
```

**Functions Called**:
- `vde_run_command()` ([vde:277](../bin/vde#L277))
  - `vde_find_command_script()` ([vde:180](../bin/vde#L180))
  - `vde_log_info()` (vde-log)

**Files Read**: None (conditional logic only)

---

### Phase 2: Create Virtual For Script - Initialization

**File**: [`bin/create-virtual-for`](../bin/create-virtual-for)

**Execution Flow**:
```
1. Shebang: #!/usr/bin/env zsh
2. set -e (strict error handling)
3. Source vm-common (line 14)
   ├─ vm-common sources:
   │  ├─ vde-log
   │  ├─ vde-shell-compat
   │  ├─ vde-constants
   │  ├─ vde-errors
   │  ├─ vde-naming
   │  ├─ vde-security
   │  ├─ vde-path-utils
   │  └─ vde-core
   └─ vm-common lazy-loads:
      ├─ vde-ssh (on first SSH operation)
      ├─ vde-docker (on first Docker operation)
      └─ vde-templates (on first template render)

4. Conditionally source UX libraries (lines 17-19):
   ├─ vde-progress (if exists)
   ├─ vde-errors (if not already loaded)
   └─ vde-naming (if not already loaded)
```

**Functions Called**: None yet (library loading only)

**Files Read**:
- [`lib/vm-common`](../lib/vm-common)
- [`lib/vde-progress`](../lib/vde-progress) (conditional)
- [`lib/vde-naming`](../lib/vde-naming) (if not loaded by vm-common)
- [`lib/vde-security`](../lib/vde-security)
- [`lib/vde-path-utils`](../lib/vde-path-utils)
- [`lib/vde-ssh`](../lib/vde-ssh) (lazy)
- [`lib/vde-docker`](../lib/vde-docker) (lazy)
- [`lib/vde-templates`](../lib/vde-templates) (lazy)

---

### Phase 3: VM Name Resolution & Validation

**File**: [`bin/create-virtual-for`](../bin/create-virtual-for) (lines 114-144)

**Execution Flow**:
```
1. vde_progress_info("Validating VM name: python")
2. resolve_vm_name("python")
   ├─ Check if "python" matches canonical name pattern
   ├─ Check if "vde-python" exists in VM_TYPES
   ├─ Check VM_ALIASES map for "python" → "vde-python"
   └─ Return: "vde-python"

3. If resolution fails:
   ├─ vde_error_alias_not_found("python")
   └─ show_known_vms()
      ├─ get_lang_vms() → [list of language VMs]
      └─ get_service_vms() → [list of service VMs]

4. Load VM configuration:
   get_vm_info("vde-python")
   └─ load_vm_types() (first call, cached thereafter)
      ├─ Read: $VDE_ROOT_DIR/data/vm-types.json
      ├─ Parse JSON with jq
      ├─ Cache in associative arrays:
      │  ├─ VM_TYPES_NAME[vde-python]="vde-python"
      │  ├─ VM_TYPES_TYPE[vde-python]="lang"
      │  ├─ VM_TYPES_DISPLAY[vde-python]="Python Language Development"
      │  ├─ VM_TYPES_INSTALL[vde-python]="apt-get install -y python3..."
      │  └─ VM_TYPES_PORT[vde-python]=""
      └─ Return VM metadata

5. Validate VM name format:
   validate_vm_name("vde-python")
   └─ vde_validate_name("vde-python") (from vde-naming)
      ├─ Check: starts with "vde-"
      ├─ Check: lowercase alphanumeric + hyphens only
      ├─ Check: no consecutive hyphens
      └─ Return: 0 (success)

6. Check if VM already exists:
   vm_exists("vde-python")
   ├─ Check Docker container exists:
   │  └─ docker ps -a --format '{{.Names}}' | grep -q "^vde-python$"
   ├─ Check config directory exists:
   │  └─ test -d configs/docker/python
   └─ Check docker-state file exists:
      └─ test -f .docker-state/python.json
   If any exist: vde_error_container_exists("vde-python") → exit
```

**Functions Called**:
- `vde_progress_info()` (vde-progress)
- `resolve_vm_name()` ([vm-common:829](../lib/vm-common#L829))
- `vde_error_alias_not_found()` (vde-errors) [conditional]
- `show_known_vms()` ([vm-common:1169](../lib/vm-common#L1169)) [conditional]
  - `get_lang_vms()` (vm-common)
  - `get_service_vms()` (vm-common)
- `get_vm_info()` ([vm-common:677](../lib/vm-common#L677))
  - `load_vm_types()` (vm-common) [first call only]
- `validate_vm_name()` ([vm-common:865](../lib/vm-common#L865))
  - `vde_validate_name()` (vde-naming)
- `vm_exists()` ([vm-common:782](../lib/vm-common#L782))
  - `vm_container_exists()` (vde-docker-state)
- `vde_error_container_exists()` (vde-errors) [conditional on exists]

**Files Read**:
- [`data/vm-types.json`](../data/vm-types.json)

**Files Checked** (existence):
- `configs/docker/python/` (directory)
- `.docker-state/python.json`

**External Commands**:
- `docker ps -a --format '{{.Names}}'` (via vm_container_exists)

---

### Phase 4: Port Allocation

**File**: [`bin/create-virtual-for`](../bin/create-virtual-for) (lines 150-158)

**Execution Flow**:
```
1. find_next_available_port("vde-python", "lang")
   ├─ Determine port range based on VM type:
   │  └─ type="lang" → range 2200-2299 (VDE_LANG_PORT_START to VDE_LANG_PORT_END)
   └─ find_available_port(2200, 2299)
      ├─ For port in {2200..2299}:
      │  ├─ _is_port_in_use(port)
      │  │  ├─ Try: sockstat -l | awk '{print $3}' | grep -q "^$port$"
      │  │  ├─ Fallback: lsof -i ":$port"
      │  │  └─ Fallback: netstat -tan | grep ":$port "
      │  └─ If not in use: return port
      └─ Return: 2213 (first available)

2. SSH_PORT=2213
```

**Functions Called**:
- `find_next_available_port()` ([vm-common:944](../lib/vm-common#L944))
  - `find_available_port()` ([vm-common:969](../lib/vm-common#L969))
    - `_is_port_in_use()` (vde-docker)

**External Commands**:
- `sockstat -l | awk '{print $3}' | grep -q "^2213$"` [or lsof/netstat fallback]

---

### Phase 5: Directory Creation

**File**: [`bin/create-virtual-for`](../bin/create-virtual-for) (lines 162-164)

**Execution Flow**:
```
1. ensure_vm_directories("vde-python", "lang")
   ├─ vde_normalize_name("vde-python") → "python" (raw name)
   ├─ Create directories for type="lang":
   │  ├─ mkdir -p configs/docker/python
   │  ├─ mkdir -p projects/python
   │  └─ mkdir -p logs/python
   └─ Return 0
```

**Functions Called**:
- `ensure_vm_directories()` ([vm-common:1141](../lib/vm-common#L1141))
  - `vde_normalize_name()` (vde-naming)

**Directories Created**:
- `$VDE_ROOT_DIR/configs/docker/python/`
- `$VDE_ROOT_DIR/projects/python/`
- `$VDE_ROOT_DIR/logs/python/`

---

### Phase 6: Docker Compose File Generation

**File**: [`bin/create-virtual-for`](../bin/create-virtual-for) (lines 169-219)

**Execution Flow**:
```
1. vde_normalize_name("vde-python") → RAW_NAME="python"

2. Select template based on VM type:
   ├─ type="lang" → template_file="templates/compose-language.yml"
   └─ type="service" → template_file="templates/compose-service.yml"

3. render_template()
   ├─ Lazy-load vde-templates library (if not already loaded)
   ├─ Read template file: templates/compose-language.yml
   ├─ Perform substitutions:
   │  ├─ {{NAME}} → "python"
   │  ├─ {{SSH_PORT}} → "2213"
   │  ├─ {{INSTALL_CMD}} → "apt-get install -y python3 python3-pip python3-venv..."
   │  └─ {{SERVICE_PORT}} → "" (empty for language VMs)
   ├─ Handle SERVICE_PORTS (lines 194-212):
   │  └─ For lang VMs: Remove ##SERVICE_PORTS## line
   └─ Write output: configs/docker/python/docker-compose.yml

4. If VDE_TEST_MODE set:
   └─ cat configs/docker/python/docker-compose.yml (for test verification)
```

**Functions Called**:
- `vde_normalize_name()` (vde-naming)
- `render_template()` ([vde-templates:49](../lib/vde-templates#L49))
  - Internal: `_substitute_variables()` (vde-templates)
  - Internal: `_handle_service_ports()` (vde-templates)

**Files Read**:
- [`templates/compose-language.yml`](../templates/compose-language.yml)

**Files Written**:
- [`configs/docker/python/docker-compose.yml`](../configs/docker/python/docker-compose.yml)

---

### Phase 7: Environment File Creation

**File**: [`bin/create-virtual-for`](../bin/create-virtual-for) (lines 224-248)

**Execution Flow**:
```
1. Create env file directory:
   mkdir -p env-files

2. Generate environment variables:
   ├─ SSH_PORT=2213
   ├─ DATABASE_URL=postgresql://devuser:SuperSecretPassword123!@postgres:5432/python_dev_db
   ├─ REDIS_HOST=redis
   └─ REDIS_PORT=6379

3. Write to file: env-files/python.env
```

**Directories Created**:
- `$VDE_ROOT_DIR/env-files/`

**Files Written**:
- [`env-files/python.env`](../env-files/python.env)

---

### Phase 8: SSH Configuration

**File**: [`bin/create-virtual-for`](../bin/create-virtual-for) (lines 253-268)

**Execution Flow**:
```
1. vde_get_ssh_host("vde-python") → "vde-python"
   └─ vde_get_container_name("vde-python")
      ├─ Check: name starts with "vde-" → return as-is
      └─ Else: return "vde-" + name

2. merge_ssh_config_entry()
   ├─ Lazy-load vde-ssh library
   ├─ Parameters:
   │  ├─ host_alias="vde-python"
   │  ├─ ssh_port=2213
   │  ├─ display_name="Python Language Development"
   │  └─ identity_file="~/.ssh/vde/vde_rsa"
   ├─ Backup existing config:
   │  └─ cp ~/.ssh/vde/config ~/.ssh/vde/config.vde-backup-$(date +%Y%m%d_%H%M%S)
   ├─ Remove existing entry for "vde-python" (if present)
   ├─ Append new SSH host entry:
   │  Host vde-python
   │      HostName localhost
   │      Port 2213
   │      User devuser
   │      IdentityFile ~/.ssh/vde/vde_rsa
   │      StrictHostKeyChecking no
   │      UserKnownHostsFile ~/.ssh/vde/known_hosts
   │      ForwardAgent yes
   │      LogLevel ERROR
   └─ Write to: ~/.ssh/vde/config

3. Copy SSH config to project configs:
   cp ~/.ssh/vde/config configs/ssh/config
```

**Functions Called**:
- `vde_get_ssh_host()` ([vde-naming:71](../lib/vde-naming#L71))
  - `vde_get_container_name()` (vde-naming)
- `merge_ssh_config_entry()` ([vde-ssh:299](../lib/vde-ssh#L299))
  - Internal: `_remove_ssh_entry()` (vde-ssh)
  - Internal: `_append_ssh_entry()` (vde-ssh)

**Files Read**:
- `~/.ssh/vde/config` (existing SSH config)

**Files Written**:
- `~/.ssh/vde/config.vde-backup-20260219_123045` (backup)
- `~/.ssh/vde/config` (updated)
- [`configs/ssh/config`](../configs/ssh/config) (copy)

---

### Phase 9: VM Startup (Docker Compose)

**File**: [`bin/create-virtual-for`](../bin/create-virtual-for) (lines 273-299)

**Execution Flow**:
```
1. If START_VM="true" (default):
   ├─ compose_file="configs/docker/python/docker-compose.yml"
   ├─ vde_progress_info("Starting VM: vde-python")
   ├─ Execute Docker Compose:
   │  └─ docker-compose -f configs/docker/python/docker-compose.yml up -d
   │     ├─ Pull base image: ubuntu:24.04
   │     ├─ Build container with:
   │     │  ├─ Install SSH server
   │     │  ├─ Execute INSTALL_CMD (Python installation)
   │     │  ├─ Configure devuser account
   │     │  └─ Set up SSH keys
   │     └─ Start container in detached mode
   │
   └─ If success:
      ├─ save_docker_state("vde-python", state_data)
      │  ├─ Create JSON object:
      │  │  {
      │  │    "vm_name": "vde-python",
      │  │    "vm_type": "lang",
      │  │    "display_name": "Python Language Development",
      │  │    "ssh_port": 2213,
      │  │    "service_port": "",
      │  │    "created_at": "2026-02-19T12:30:45Z",
      │  │    "status": "running"
      │  │  }
      │  └─ Write to: .docker-state/python.json
      └─ vde_success("VM vde-python started successfully")

   If failure:
      └─ vde_error_docker_build_failed("vde-python") → exit 1
```

**Functions Called**:
- `vde_progress_info()` (vde-progress)
- `save_docker_state()` ([vm-common:1076](../lib/vm-common#L1076))
  - `vde_normalize_name()` (vde-naming)
  - `_date_iso8601()` (vde-shell-compat)
- `vde_success()` (vde-errors)
- `vde_error_docker_build_failed()` (vde-errors) [conditional]

**External Commands**:
- `docker-compose -f configs/docker/python/docker-compose.yml up -d`
  - Internal Docker operations:
    - `docker pull ubuntu:24.04`
    - `docker build` (container creation)
    - `docker run` (container startup)

**Files Written**:
- [`.docker-state/python.json`](../.docker-state/python.json)

---

### Phase 10: Summary Display

**File**: [`bin/create-virtual-for`](../bin/create-virtual-for) (lines 304-322)

**Execution Flow**:
```
1. vde_success("VM vde-python created and configured successfully")

2. Display created resources:
   ├─ Docker Compose file: configs/docker/python/docker-compose.yml
   ├─ Environment file: env-files/python.env
   ├─ Project directory: projects/python/
   └─ Logs directory: logs/python/

3. Display SSH configuration:
   ├─ SSH host: vde-python
   ├─ SSH port: 2213
   └─ Connection command: ssh vde-python

4. Exit with status 0 (VDE_SUCCESS)
```

**Functions Called**:
- `vde_success()` (vde-errors)
- `vde_log_info()` (vde-log)

---

### Complete Function Call Graph

```
vde (main)
├─ vde_log_init()
├─ vde_run_command()
│  ├─ vde_find_command_script()
│  └─ vde_log_info()
└─ Execute: create-virtual-for
   ├─ vde_progress_info()
   ├─ resolve_vm_name()
   │  └─ [conditional] vde_error_alias_not_found()
   │     └─ show_known_vms()
   │        ├─ get_lang_vms()
   │        └─ get_service_vms()
   ├─ get_vm_info()
   │  └─ load_vm_types() [first call only]
   ├─ validate_vm_name()
   │  └─ vde_validate_name()
   ├─ vm_exists()
   │  ├─ vm_container_exists()
   │  └─ [conditional] vde_error_container_exists()
   ├─ find_next_available_port()
   │  └─ find_available_port()
   │     └─ _is_port_in_use()
   ├─ ensure_vm_directories()
   │  └─ vde_normalize_name()
   ├─ vde_normalize_name()
   ├─ render_template()
   │  ├─ _substitute_variables()
   │  └─ _handle_service_ports()
   ├─ vde_get_ssh_host()
   │  └─ vde_get_container_name()
   ├─ merge_ssh_config_entry()
   │  ├─ _remove_ssh_entry()
   │  └─ _append_ssh_entry()
   ├─ [Docker Compose execution]
   ├─ save_docker_state()
   │  ├─ vde_normalize_name()
   │  └─ _date_iso8601()
   ├─ vde_success()
   └─ vde_log_info()
```

---

### Library Dependency Chain

```
vde (entry point)
├─ vde-shell-compat (bootstrap - no dependencies)
├─ vde-constants (bootstrap - no dependencies)
├─ vde-errors (uses vde-constants)
├─ vde-log (uses vde-constants, vde-shell-compat)
├─ vde-core (uses vde-shell-compat, vde-constants)
├─ vm-common (uses all above + below)
│  ├─ vde-naming
│  ├─ vde-security
│  ├─ vde-path-utils
│  └─ Lazy-loads:
│     ├─ vde-ssh
│     ├─ vde-docker
│     └─ vde-templates
└─ vde-docker-state (uses vde-constants)

create-virtual-for
├─ Inherits all from vm-common
├─ vde-progress (optional UX)
└─ Triggers lazy-loads:
   ├─ vde-templates (for render_template)
   └─ vde-ssh (for merge_ssh_config_entry)
```

---

### All Files Read

1. [`lib/vde-shell-compat`](../lib/vde-shell-compat)
2. [`lib/vde-constants`](../lib/vde-constants)
3. [`lib/vde-errors`](../lib/vde-errors)
4. [`lib/vde-log`](../lib/vde-log)
5. [`lib/vde-core`](../lib/vde-core)
6. [`lib/vm-common`](../lib/vm-common)
7. [`lib/vde-docker-state`](../lib/vde-docker-state)
8. [`lib/vde-progress`](../lib/vde-progress)
9. [`lib/vde-naming`](../lib/vde-naming)
10. [`lib/vde-security`](../lib/vde-security)
11. [`lib/vde-path-utils`](../lib/vde-path-utils)
12. [`lib/vde-ssh`](../lib/vde-ssh)
13. [`lib/vde-docker`](../lib/vde-docker)
14. [`lib/vde-templates`](../lib/vde-templates)
15. [`data/vm-types.json`](../data/vm-types.json)
16. [`templates/compose-language.yml`](../templates/compose-language.yml)
17. `~/.ssh/vde/config`

---

### All Files Written

1. [`configs/docker/python/docker-compose.yml`](../configs/docker/python/docker-compose.yml)
2. [`env-files/python.env`](../env-files/python.env)
3. `~/.ssh/vde/config.vde-backup-<timestamp>`
4. `~/.ssh/vde/config` (updated)
5. [`configs/ssh/config`](../configs/ssh/config)
6. [`.docker-state/python.json`](../.docker-state/python.json)

---

### All Directories Created

1. [`configs/docker/python/`](../configs/docker/python/)
2. [`projects/python/`](../projects/python/)
3. [`logs/python/`](../logs/python/)
4. [`env-files/`](../env-files/)

---

### All External Commands Executed

1. `docker ps -a --format '{{.Names}}'` (container existence check)
2. `sockstat -l | awk '{print $3}' | grep -q "^2213$"` (port availability)
3. `docker-compose -f configs/docker/python/docker-compose.yml up -d` (VM creation)
   - Internally triggers: `docker pull`, `docker build`, `docker run`

---

### Complete Function List by Library

#### vde-shell-compat (24 functions)
- `_detect_shell()`, `_shell_version()`, `_is_zsh()`, `_shell_supports_native_assoc()`
- `_get_script_path()`, `_get_script_dir()`
- `_assoc_init()`, `_assoc_set()`, `_assoc_get()`, `_assoc_keys()`, `_assoc_has_key()`, `_assoc_unset()`, `_assoc_clear()`, `_assoc_cleanup()`
- `_array_length()`, `_array_append()`, `_array_contains()`
- `_string_split()`, `_string_trim()`, `_read_array()`
- `_check_shell_compatibility()`, `_require_shell()`
- `_declare_global()`, `_date_iso8601()`, `_date_epoch()`

#### vde-constants (0 functions, pure constants)
- Port ranges, timeouts, paths, error codes

#### vde-errors (14 functions)
- `vde_error_set_verbose()`, `vde_error_is_verbose()`, `_vde_error_format_block()`
- `vde_error_show()`, `vde_error_simple()`, `vde_error_with_code()`
- `vde_error_docker_not_running()`, `vde_error_port_in_use()`, `vde_error_ssh_key_missing()`
- `vde_error_container_exists()`, `vde_error_permission_denied()`, `vde_error_vm_not_found()`
- `vde_error_vm_not_running()`, `vde_error_docker_build_failed()`, `vde_error_invalid_vm_name()`, `vde_error_alias_not_found()`
- `vde_success()`

#### vde-log (20 functions)
- `vde_log_init()`, `vde_log_set_level()`, `vde_log_get_level()`, `vde_log_set_format()`
- `vde_log_to_file()`, `vde_log_to_stdout()`, `vde_log_to_stderr()`
- `vde_log()`, `vde_log_debug()`, `vde_log_info()`, `vde_log_warn()`, `vde_log_error()`
- `vde_log_format_json()`, `vde_log_format_syslog()`, `vde_log_format_text()`
- `vde_log_check_rotation()`, `vde_log_rotate()`, `vde_log_cleanup()`
- `vde_log_recent()`, `vde_log_grep()`, `vde_log_errors()`
- `vde_log_function()`, `vde_log_function_return()`, `vde_log_export()`

#### vde-core (15 functions)
- `_vde_core_ensure_cache_dir()`, `_vde_core_get_mtime()`, `_vde_core_save_cache()`, `_vde_core_load_cache()`
- `vde_core_load_types()`, `vde_core_get_all_vms()`, `vde_core_get_vm_type()`, `vde_core_is_known_vm()`
- `vde_require_ssh()`, `vde_require_docker()`, `vde_require_template()`
- `vde_check_schema_integrity()`, `vde_validate_json_schema()`, `vde_validate_or_regenerate()`
- `vde_get_schema_for_json()`, `vde_check_schema_compatibility()`, `vde_detect_schema_changes()`
- `vde_backup_config()`, `vde_validate_and_update()`, `vde_get_config_version()`, `vde_get_schema_version()`
- `log_info()`, `log_error()`, `log_success()`, `log_warning()`
- `vde_time_start()`, `vde_time_end()`

#### vm-common (45+ functions)
- `load_vm_types()`, `load_docker_config()`, `get_docker_config()`, `regenerate_vm_types_cache()`, `validate_vm_types_config()`
- `get_vm_info()`, `get_vms_by_type()`, `get_lang_vms()`, `get_service_vms()`, `get_all_vms()`
- `is_known_vm()`, `vm_is_created()`, `vm_template_exists()`, `vm_exists()`, `validate_vm_doesnt_exist()`, `validate_vm_type()`, `validate_vm_name()`
- `get_vm_type()`, `get_vm_display_name()`, `get_vm_install()`, `resolve_vm_name()`
- `get_allocated_ports()`, `find_next_available_port()`, `find_available_port()`, `allocate_port_for_vm()`, `get_or_allocate_port()`
- `get_vm_ssh_port()`, `get_port_from_registry()`, `save_port_to_registry()`, `remove_port_from_registry()`, `clear_port_registry()`
- `save_docker_state()`, `load_docker_state()`, `clear_docker_state()`, `get_docker_state_dir()`
- `ensure_vm_directories()`, `create_backup()`, `show_known_vms()`, `_is_cache_valid()`

#### vde-docker-state (6 functions)
- `_get_container_name()`, `vm_container_exists()`, `vm_container_status()`
- `vm_is_container_running()`, `vm_is_container_stopped()`
- `list_running_containers()`, `list_all_containers()`

#### vde-naming (functions used)
- `vde_normalize_name()`, `vde_validate_name()`, `vde_get_ssh_host()`, `vde_get_container_name()`

#### vde-ssh (functions used)
- `merge_ssh_config_entry()`, `_remove_ssh_entry()`, `_append_ssh_entry()`

#### vde-templates (functions used)
- `render_template()`, `_substitute_variables()`, `_handle_service_ports()`

#### vde-progress (functions used)
- `vde_progress_info()`

---

### Execution Time Estimates

**Typical execution time for `vde create python`**: 30-90 seconds

**Phase breakdown**:
- Initialization & validation: <1 second
- Port allocation: <1 second
- File generation: <1 second
- SSH config update: <1 second
- Docker operations: 25-85 seconds
  - Image pull: 10-60 seconds (network dependent)
  - Container build: 10-20 seconds (Python installation)
  - Container startup: 5 seconds
- State persistence: <1 second

---

### Verification

To verify this function map, execute with tracing:

```bash
## Enable function tracing
export VDE_LOG_LEVEL="DEBUG"
export VDE_ERRORS_VERBOSE=1

## Run with zsh tracing
zsh -x bin/vde create python 2>&1 | tee vde-trace.log

## Analyze function calls
grep -E '^\+' vde-trace.log | grep -E '\(\)' | awk '{print $2}' | sort | uniq
```

Expected output: All functions listed in this document should appear in the trace.


## VDE Parser Technical Deep Dive

A comprehensive technical analysis of the VDE (Virtual Development Environment) Natural Language Parser—a pattern-based command understanding system implemented entirely in shell script.

[← Back to README](../README.md)

---

### Table of Contents

1. [Introduction](#introduction)
2. [Design Philosophy](#design-philosophy)
3. [Architecture Overview](#architecture-overview)
4. [Intent Detection System](#intent-detection-system)
5. [Entity Extraction Engine](#entity-extraction-engine)
6. [Plan Generation](#plan-generation)
7. [Plan Execution](#plan-execution)
8. [Pattern Matching Techniques](#pattern-matching-techniques)
9. [Dependency Management](#dependency-management)
10. [Extension Guide](#extension-guide)

---

### Introduction

The VDE Parser (`lib/vde-parser`) is a sophisticated pattern-based command understanding system that converts free-form user input into structured execution commands. Implemented entirely in Zsh, it demonstrates natural language processing capabilities through shell native pattern matching.

**Location:** `$VDE_ROOT_DIR/lib/vde-parser`

**Key Statistics:**
- **458 lines** of well-documented code
- **8 supported intents**
- **18+ language VMs** and **7+ service VMs** recognized
- **Zero external dependencies** for core functionality
- **Sub-10ms response time** for pattern-based parsing

---

### Design Philosophy

#### Core Principles

1. **Pattern-First Design**: Use regex pattern matching before complex logic
2. **Cascading Detection**: Check intents in priority order to avoid false matches
3. **Known-Entity Validation**: Extract entities only from known VM types
4. **Graceful Degradation**: Fall back to help when input is ambiguous
5. **Shell Native**: Leverage Zsh's associative arrays and pattern matching

#### Why Shell Script?

The choice of Zsh for a natural language parser may seem unusual, but offers significant advantages:

| Advantage | Benefit |
|-----------|---------|
| **Zero startup latency** | No interpreter warmup |
| **Native text processing** | Zsh has powerful string operations |
| **Associative arrays** | Efficient VM type lookups |
| **Process pipeline** | Unix philosophy: compose small tools |
| **Portability** | Runs on any system with Zsh |

---

### Architecture Overview

#### High-Level Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INPUT                                │
│                   "start python and go"                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
              ┌─────────────────────────────┐
              │     Intent Detection        │
              │   (keyword matching)        │
              └─────────────┬───────────────┘
                            │
                            ▼
              ┌─────────────────────────────┐
              │    Entity Extraction        │
              │  (VM names, flags, filters) │
              └─────────────┬───────────────┘
                            │
                            ▼
              ┌─────────────────────────────┐
              │    Plan Generation          │
              │  (structured output)        │
              └─────────────┬───────────────┘
                            │
                            ▼
              ┌─────────────────────────────┐
              │     Plan Execution          │
              │  (calls VDE functions)      │
              └─────────────────────────────┘
```

#### File Organization

```
lib/vde-parser
├── Lines 1-11:   Header and Dependencies
├── Lines 12-22:  Constants (Intent Definitions)
├── Lines 23-92:  Intent Detection
├── Lines 93-196: Entity Extraction
├── Lines 197-232: Command Generation
├── Lines 233-396: Plan Execution
└── Lines 397-457: Help Display
```

#### Module Dependencies

```
vde-parser
    │
    ├── vm-common (required)
    │   ├── VM type definitions
    │   ├── Associative arrays (VM_TYPE, VM_ALIASES, etc.)
    │   └── Query functions (get_vm_info, get_all_vms, etc.)
    │
    └── vde-commands (required)
        ├── Safe wrapper functions
        └── Logging utilities
```

**Dependency loading order** (as documented in lines 6-9):
1. `vm-common` - Must be loaded first
2. `vde-commands` - Depends on vm-common
3. `vde-parser` - Uses both

---

### Intent Detection System

The intent detection system is the parser's primary classification mechanism. It maps free-form input to one of eight predefined intents.

#### Intent Constants (Lines 14-22)

```zsh
readonly INTENT_LIST_VMS="list_vms"
readonly INTENT_CREATE_VM="create_vm"
readonly INTENT_START_VM="start_vm"
readonly INTENT_STOP_VM="stop_vm"
readonly INTENT_RESTART_VM="restart_vm"
readonly INTENT_STATUS="status"
readonly INTENT_CONNECT="connect"
readonly INTENT_ADD_VM_TYPE="add_vm_type"
readonly INTENT_HELP="help"
```

**Design notes:**
- `readonly` prevents accidental modification
- Descriptive names match natural language concepts
- `INTENT_ADD_VM_TYPE` reserved for future use

#### Detection Algorithm (Lines 31-92)

The `detect_intent()` function uses a **priority cascade** pattern:

```zsh
detect_intent() {
    local input="$1"
    local input_lower
    input_lower=$(echo "$input" | tr '[:upper:]' '[:lower:]')

    # Priority 1: Help (highest)
    if [[ "$input_lower" =~ "help" ]] || [[ "$input_lower" =~ "what can i do" ]]; then
        echo "$INTENT_HELP"
        return
    fi

    # Priority 2: List/Show
    if [[ "$input_lower" =~ "list" ]] || [[ "$input_lower" =~ "show" ]]; then
        echo "$INTENT_LIST_VMS"
        return
    fi

    # ... (continues in priority order)
}
```

#### Priority Order Rationale

The cascade order is carefully chosen to prevent false matches:

| Priority | Intent | Reason for Position |
|----------|--------|---------------------|
| 1 | Help | Most generic, catch-all for confused users |
| 2 | List/Show | Checked before other verbs to avoid conflict |
| 3 | Status | Specific "running" keyword is distinctive |
| 4 | Connect | "how do i connect" phrase is unique |
| 5 | Create | Checked after show/create distinction |
| 6 | Start | Common verb, but checked in isolation |
| 7 | Stop | Mutually exclusive with start |
| 8 | Restart | Checked last among action verbs |

#### Pattern Matching Details

**Help patterns** (lines 37-40):
```zsh
if [[ "$input_lower" =~ "help" ]] || \
   [[ "$input_lower" =~ "what can i do" ]] || \
   [[ "$input_lower" =~ "how do i use" ]]; then
    echo "$INTENT_HELP"
    return
fi
```

**List patterns** (lines 43-52):
```zsh
## Direct listing requests
if [[ "$input_lower" =~ "list" ]] || \
   [[ "$input_lower" =~ "show" ]] || \
   [[ "$input_lower" =~ "what available" ]]; then
    echo "$INTENT_LIST_VMS"
    return
fi

## Question-based listing
if [[ "$input_lower" =~ "what can i" ]] || \
   [[ "$input_lower" =~ "what vms" ]] || \
   [[ "$input_lower" =~ "which vms" ]]; then
    echo "$INTENT_LIST_VMS"
    return
fi
```

**Status patterns** (lines 55-58):
```zsh
if [[ "$input_lower" =~ "running" ]] || \
   [[ "$input_lower" =~ "status" ]] || \
   [[ "$input_lower" =~ "current state" ]]; then
    echo "$INTENT_STATUS"
    return
fi
```

**Connect patterns** (lines 61-64):
```zsh
if [[ "$input_lower" =~ "how do i connect" ]] || \
   [[ "$input_lower" =~ "ssh into" ]] || \
   [[ "$input_lower" =~ "connect to" ]]; then
    echo "$INTENT_CONNECT"
    return
fi
```

**Action verb patterns** (lines 67-88):
```zsh
## Create (most specific to avoid false matches)
if [[ "$input_lower" =~ "create a" ]] || \
   [[ "$input_lower" =~ "create new" ]] || \
   [[ "$input_lower" =~ "make a" ]] || \
   [[ "$input_lower" =~ "make new" ]] || \
   [[ "$input_lower" =~ "set up" ]]; then
    echo "$INTENT_CREATE_VM"
    return
fi

## Start
if [[ "$input_lower" =~ "start" ]] || \
   [[ "$input_lower" =~ "launch" ]] || \
   [[ "$input_lower" =~ "boot" ]]; then
    echo "$INTENT_START_VM"
    return
fi

## Stop
if [[ "$input_lower" =~ "stop" ]] || \
   [[ "$input_lower" =~ "shutdown" ]] || \
   [[ "$input_lower" =~ "kill" ]]; then
    echo "$INTENT_STOP_VM"
    return
fi

## Restart
if [[ "$input_lower" =~ "restart" ]] || \
   [[ "$input_lower" =~ "reboot" ]] || \
   [[ "$input_lower" =~ "rebuild" ]]; then
    echo "$INTENT_RESTART_VM"
    return
fi
```

#### Fallback Behavior

When no intent matches (lines 91-92):
```zsh
## Default: return help intent
echo "$INTENT_HELP"
```

This ensures ambiguous input triggers helpful guidance rather than errors.

---

### Entity Extraction Engine

Once intent is identified, the parser extracts entities: VM names, flags, and filters.

#### VM Name Extraction (`extract_vm_names()`, Lines 98-157)

This is the most sophisticated function in the parser. It doesn't just search for keywords—it validates against known VM types.

#### Algorithm Overview

```
Input: "start python and nodejs"
Output:
  python
  nodejs
```

#### Step-by-Step Process

**Step 1: Prepare input** (lines 103-104)
```zsh
local input="$1"
local input_lower
input_lower=$(echo "$input" | tr '[:upper:]' '[:lower:]')
```

**Step 2: Get all known VMs** (lines 107-111)
```zsh
local -a found_vms=()
local -a all_vms
local alias_list
local -a alias_array
all_vms=($(get_all_vms))
```

The `get_all_vms()` function comes from `vm-common` and returns all VM names from the configuration.

**Step 3: Check each known VM** (lines 114-133)
```zsh
for vm in "${all_vms[@]}"; do
    # Check for direct match (word boundaries)
    if echo "$input_lower" | grep -qw "$vm"; then
        found_vms+=("$vm")
        continue
    fi

    # Check aliases
    alias_list=$(get_vm_info aliases "$vm")
    if [[ -n "$alias_list" ]]; then
        IFS=',' read -A alias_array <<< "$alias_list"
        for alias in "${alias_array[@]}"; do
            alias=$(echo "$alias" | tr -d ' ')
            if echo "$input_lower" | grep -qw "$alias"; then
                found_vms+=("$vm")
                break
            fi
        done
    fi
done
```

**Key technique:** Word boundary matching with `grep -qw` prevents partial matches (e.g., "go" won't match "mongodb").

**Step 4: Handle wildcards** (lines 136-151)
```zsh
## Handle "all", "everything"
if [[ "$input_lower" =~ "all" ]] || [[ "$input_lower" =~ "everything" ]]; then
    get_all_vms
    return
fi

## Handle "all languages"
if [[ "$input_lower" =~ "all languages" ]] || [[ "$input_lower" =~ "all lang" ]]; then
    get_lang_vms
    return
fi

## Handle "all services"
if [[ "$input_lower" =~ "all services" ]] || [[ "$input_lower" =~ "all svc" ]]; then
    get_service_vms
    return
fi
```

**Step 5: Output results** (lines 154-156)
```zsh
if [[ ${#found_vms[@]} -gt 0 ]]; then
    printf '%s\n' "${found_vms[@]}"
fi
```

#### Real-World Examples

| Input | Output | Explanation |
|-------|--------|-------------|
| "start python" | `python` | Direct match |
| "start nodejs" | `js` | Alias resolution |
| "start all" | All VMs | Wildcard expansion |
| "start python and rust" | `python\nrust` | Multiple matches |
| "start postgres" | `postgres` | Service VM match |

#### Flag Extraction (`extract_flags()`, Lines 176-196)

Extracts rebuild and no-cache flags from input:

```zsh
extract_flags() {
    local input="$1"
    local input_lower
    input_lower=$(echo "$input" | tr '[:upper:]' '[:lower:]')

    local rebuild="false"
    local nocache="false"

    if [[ "$input_lower" =~ "rebuild" ]] || [[ "$input_lower" =~ "re-create" ]]; then
        rebuild="true"
    fi

    if [[ "$input_lower" =~ "no-cache" ]] || [[ "$input_lower" =~ "no cache" ]]; then
        nocache="true"
    fi

    echo "rebuild=$rebuild nocache=$nocache"
}
```

**Output format:** Shell-compatible variable assignments for `eval`.

**Examples:**
- "rebuild python" → `rebuild=true nocache=false`
- "start go with no cache" → `rebuild=false nocache=true`
- "rebuild and start rust" → `rebuild=true nocache=false`

#### Filter Extraction (`extract_filter()`, Lines 159-174)

For listing operations, determines what category to show:

```zsh
extract_filter() {
    local input="$1"
    local input_lower
    input_lower=$(echo "$input" | tr '[:upper:]' '[:lower:]')

    if [[ "$input_lower" =~ "language" ]] || [[ "$input_lower" =~ "lang" ]]; then
        echo "lang"
    elif [[ "$input_lower" =~ "service" ]] || [[ "$input_lower" =~ "svc" ]]; then
        echo "svc"
    else
        echo "all"
    fi
}
```

**Examples:**
- "show languages" → `lang`
- "list services" → `svc`
- "what can I create?" → `all` (default)

---

### Plan Generation

The `generate_plan()` function (lines 202-232) orchestrates intent detection and entity extraction into a structured output format.

#### Function Signature

```zsh
## Generate an execution plan from input
## Args: <input_string>
## Returns: Structured plan (multi-line)
generate_plan() {
    local input="$1"
    # ...
}
```

#### Execution Flow

```zsh
generate_plan() {
    local input="$1"

    # Step 1: Detect intent
    local intent
    intent=$(detect_intent "$input")

    # Step 2: Initialize entities
    local vms=""
    local flags=""
    local filter="all"

    # Step 3: Extract entities based on intent
    case "$intent" in
        "$INTENT_LIST_VMS")
            filter=$(extract_filter "$input")
            ;;
        "$INTENT_CREATE_VM"|"$INTENT_START_VM"|"$INTENT_STOP_VM"|"$INTENT_RESTART_VM"|"$INTENT_STATUS"|"$INTENT_CONNECT")
            vms=$(extract_vm_names "$input")
            flags=$(extract_flags "$input")
            ;;
    esac

    # Step 4: Output plan
    echo "INTENT:$intent"
    [[ -n "$vms" ]] && echo "VM:$vms"
    [[ -n "$flags" ]] && echo "FLAGS:$flags"
    [[ -n "$filter" ]] && echo "FILTER:$filter"
}
```

#### Plan Format

The output is a simple key-value format, one entity per line:

```
INTENT:start_vm
VM:python
rust
FLAGS:rebuild=true nocache=false
FILTER:all
```

**Design notes:**
- Multi-line VM list (one VM per line)
- Shell-assignable flag format
- Optional sections (only present if needed)
- Simple pipe-parsable format

#### Example Plans

| Input | Generated Plan |
|-------|----------------|
| "start python and go" | `INTENT:start_vm\nVM:python\ngo\nFLAGS:rebuild=false nocache=false` |
| "show all languages" | `INTENT:list_vms\nFILTER:lang` |
| "rebuild rust" | `INTENT:start_vm\nVM:rust\nFLAGS:rebuild=true nocache=false` |
| "what's running?" | `INTENT:status\nFLAGS:rebuild=false nocache=false` |

---

### Plan Execution

The `execute_plan()` function (lines 238-396) translates plans into actions by calling VDE command functions.

#### Input Method

Plans are passed via **stdin**, not arguments:

```zsh
## Execute a generated plan
## Args: (plan passed via stdin)
execute_plan() {
    # ...
}
```

This enables clean piping: `echo "$PLAN" | execute_plan`

#### Parsing Loop (Lines 247-270)

```zsh
local intent=""
local -a vms=()
local rebuild="false"
local nocache="false"
local filter="all"

## Parse plan from stdin
while IFS= read -r line; do
    local key="${line%%:*}"
    local value="${line#*:}"

    case "$key" in
        INTENT)
            intent="$value"
            ;;
        VM)
            local vm_list
            vm_list=$(echo "$value" | tr '\n' ' ')
            # Trim trailing whitespace and convert to array
            vm_list=$(echo "$vm_list" | sed 's/[[:space:]]*$//')
            vms=(${=vm_list})
            ;;
        FLAGS)
            eval "$value"
            ;;
        FILTER)
            filter="$value"
            ;;
    esac
done
```

**Parsing techniques:**
- `${line%%:*}` - Extract everything before first `:` (key)
- `${line#*:}` - Extract everything after first `:` (value)
- `eval "$value"` - Safely evaluate flag assignments
- `tr '\n' ' '` - Convert newlines to spaces for array conversion

#### Intent Routing (Lines 273-395)

Each intent has a dedicated handler:

#### LIST_VMS Handler (Lines 274-277)

```zsh
"$INTENT_LIST_VMS")
    vde_list_vms "--$filter"
    return $?
    ;;
```

#### STATUS Handler (Lines 279-290)

```zsh
"$INTENT_STATUS")
    if [[ ${#vms[@]} -eq 0 ]]; then
        vde_get_running_vms
    else
        for vm in "${vms[@]}"; do
            local vm_status
            vm_status=$(vde_get_vm_status "$vm")
            echo "$vm: $vm_status"
        done
    fi
    return $?
    ;;
```

**Conditional behavior:** Shows all running if no VMs specified, otherwise shows specific VM status.

#### CREATE_VM Handler (Lines 292-314)

```zsh
"$INTENT_CREATE_VM")
    if [[ ${#vms[@]} -eq 0 ]]; then
        log_error "No VM specified. Please specify which VM to create."
        return 1
    fi

    for vm in "${vms[@]}"; do
        if ! vde_validate_vm_type "$vm"; then
            log_error "Unknown VM type: $vm"
            local available
            available=$(vde_list_vms | tr '\n' ' ')
            log_error "Available VMs: $available"
            return 1
        fi

        if vde_vm_exists "$vm"; then
            log_info "VM $vm already exists. Skipping creation."
        else
            vde_create_vm "$vm" || return 1
        fi
    done
    return $?
    ;;
```

**Validation checks:**
1. At least one VM must be specified
2. VM type must be known
3. VM doesn't already exist (idempotent)

#### START_VM Handler (Lines 316-337)

```zsh
"$INTENT_START_VM")
    if [[ ${#vms[@]} -eq 0 ]]; then
        log_error "No VM specified. Please specify which VM to start."
        return 1
    fi

    for vm in "${vms[@]}"; do
        if ! vde_vm_exists "$vm"; then
            log_error "VM $vm does not exist. Create it first."
            return 1
        fi
    done

    # Build args array with flags and VMs
    local -a start_args=()
    [[ "$rebuild" == "true" ]] && start_args+=(--rebuild)
    [[ "$nocache" == "true" ]] && start_args+=(--no-cache)
    start_args+=("${vms[@]}")

    vde_start_multiple_vms "${start_args[@]}"
    return $?
    ;;
```

**Pre-flight validation:** Ensures all VMs exist before starting any.

#### STOP_VM Handler (Lines 339-347)

```zsh
"$INTENT_STOP_VM")
    if [[ ${#vms[@]} -eq 0 ]]; then
        log_error "No VM specified. Please specify which VM to stop."
        return 1
    fi

    vde_stop_multiple_vms "${vms[@]}"
    return $?
    ;;
```

#### RESTART_VM Handler (Lines 349-359)

```zsh
"$INTENT_RESTART_VM")
    if [[ ${#vms[@]} -eq 0 ]]; then
        log_error "No VM specified. Please specify which VM to restart."
        return 1
    fi

    for vm in "${vms[@]}"; do
        vde_restart_vm "$vm" "$rebuild" "$nocache"
    done
    return $?
    ;;
```

#### CONNECT Handler (Lines 361-383)

```zsh
"$INTENT_CONNECT")
    if [[ ${#vms[@]} -eq 0 ]]; then
        log_error "No VM specified. Please specify which VM you want to connect to."
        return 1
    fi

    for vm in "${vms[@]}"; do
        local ssh_info
        ssh_info=$(vde_get_ssh_info "$vm")

        if [[ -z "$ssh_info" ]]; then
            log_error "Could not get SSH info for $vm"
        else
            local ssh_host="${ssh_info%%|*}"
            local ssh_port="${ssh_info##*|}"
            echo "To connect to $vm:"
            echo "  SSH command: ssh $ssh_host"
            echo "  Port: $ssh_port"
            echo "  Or use VSCode Remote-SSH with host: $ssh_host"
        fi
    done
    return $?
    ;;
```

**Output format:** User-friendly connection instructions.

#### HELP Handler (Lines 385-388)

```zsh
"$INTENT_HELP")
    show_parser_help
    return 0
    ;;
```

#### Default Handler (Lines 390-395)

```zsh
*)
    log_error "Unknown intent: $intent"
    show_parser_help
    return 1
    ;;
```

---

### Pattern Matching Techniques

The parser employs several advanced shell pattern matching techniques.

#### Case-Insensitive Matching

**Technique:** Convert to lowercase once, then match:

```zsh
local input_lower
input_lower=$(echo "$input" | tr '[:upper:]' '[:lower:]')

if [[ "$input_lower" =~ "help" ]]; then
    # ...
fi
```

**Benefit:** Faster than multiple case-insensitive matches.

#### Word Boundary Matching

**Technique:** Use `grep -qw` for whole-word matches:

```zsh
if echo "$input_lower" | grep -qw "$vm"; then
    found_vms+=("$vm")
fi
```

**Why:** Prevents "go" from matching "mongodb" or "python" from matching "python3".

#### Regex Substring Matching

**Technique:** Zsh's `=~` operator for substring search:

```zsh
if [[ "$input_lower" =~ "create a" ]]; then
    echo "$INTENT_CREATE_VM"
fi
```

**Note:** Matches anywhere in string, not just at word boundaries.

#### Associative Array Lookups

**Technique:** Direct key access for O(1) lookups:

```zsh
## From vm-common
local vm_type="${VM_TYPE[$vm_name]}"
local vm_aliases="${VM_ALIASES[$vm_name]}"
```

**Benefit:** Instant validation without iteration.

---

### Dependency Management

The parser has explicit dependencies that must be loaded in order.

#### Required Libraries (Lines 6-9)

```zsh
## -----------------------
## Dependencies
## -----------------------
## This library requires vm-common and vde-commands to be sourced first
```

#### Loading Order

```zsh
## Load in this order:
source "$SCRIPT_DIR/lib/vm-common"     # Load FIRST
source "$SCRIPT_DIR/lib/vde-commands"   # Load SECOND
source "$SCRIPT_DIR/lib/vde-parser"     # Load THIRD
```

#### Dependency Functions Used

**From vm-common:**

| Function | Purpose | Used at Line |
|----------|---------|--------------|
| `get_all_vms()` | Get all VM names | 111 |
| `get_lang_vms()` | Get language VMs | 143 |
| `get_service_vms()` | Get service VMs | 149 |
| `get_vm_info()` | Get VM metadata | 122 |

**From vde-commands:**

| Function | Purpose | Used at Line |
|----------|---------|--------------|
| `vde_list_vms()` | List VMs with filter | 275 |
| `vde_get_running_vms()` | Get running containers | 281 |
| `vde_get_vm_status()` | Get VM status | 285 |
| `vde_validate_vm_type()` | Validate VM name | 299 |
| `vde_vm_exists()` | Check if VM created | 307 |
| `vde_create_vm()` | Create new VM | 310 |
| `vde_start_multiple_vms()` | Start multiple VMs | 335 |
| `vde_stop_multiple_vms()` | Stop multiple VMs | 345 |
| `vde_restart_vm()` | Restart VM | 356 |
| `vde_get_ssh_info()` | Get SSH connection info | 369 |
| `show_parser_help()` | Display help text | 386 |

---

### Extension Guide

#### Adding a New Intent

**Step 1:** Define constant (lines 14-22)
```zsh
readonly INTENT_NEW_INTENT="new_intent"
```

**Step 2:** Add detection logic (lines 31-92)
```zsh
if [[ "$input_lower" =~ "your pattern" ]]; then
    echo "$INTENT_NEW_INTENT"
    return
fi
```

**Step 3:** Add case handler (lines 273-395)
```zsh
"$INTENT_NEW_INTENT")
    # Your implementation
    return $?
    ;;
```

**Step 4:** Update help (lines 403-457)
```zsh
echo "  New Intent"
echo "    example command"
```

#### Adding Entity Types

**Step 1:** Create extraction function
```zsh
extract_custom_entity() {
    local input="$1"
    # Your extraction logic
    echo "results"
}
```

**Step 2:** Call in `generate_plan()` (lines 217-224)
```zsh
case "$intent" in
    "$INTENT_NEW_INTENT")
        custom=$(extract_custom_entity "$input")
        ;;
esac
```

**Step 3:** Output in plan format
```zsh
echo "CUSTOM:$custom"
```

**Step 4:** Parse in `execute_plan()` (lines 248-270)
```zsh
CUSTOM)
    custom_value="$value"
    ;;
```

---

### Performance Characteristics

#### Computational Complexity

| Function | Time Complexity | Space Complexity |
|----------|-----------------|------------------|
| `detect_intent()` | O(1) | O(1) |
| `extract_vm_names()` | O(n×m) | O(n) |
| `extract_flags()` | O(1) | O(1) |
| `extract_filter()` | O(1) | O(1) |
| `generate_plan()` | O(n×m) | O(n) |
| `execute_plan()` | O(v) | O(1) |

Where:
- n = number of known VMs
- m = number of aliases per VM
- v = number of VMs in command

#### Benchmarks

Measured on typical development hardware (M-series CPU, SSD):

| Operation | Time | Notes |
|-----------|------|-------|
| Intent detection | <1ms | Fixed patterns |
| VM name extraction | 2-5ms | Depends on VM count |
| Full parse (pattern-based) | 3-8ms | Total end-to-end |
| Plan execution | Variable | Depends on operation |

---

### Real-World Examples

#### Example 1: Simple Start Command

**Input:** "start python"

**Trace:**
1. `detect_intent("start python")` → `INTENT_START_VM`
2. `extract_vm_names("start python")` → `python`
3. `extract_flags("start python")` → `rebuild=false nocache=false`
4. **Plan:**
   ```
   INTENT:start_vm
   VM:python
   FLAGS:rebuild=false nocache=false
   ```
5. `execute_plan` → Calls `vde_start_multiple_vms python`

#### Example 2: Complex Multi-VM Command

**Input:** "create a Go and Rust VM"

**Trace:**
1. `detect_intent("create a Go and Rust VM")` → `INTENT_CREATE_VM`
2. `extract_vm_names("create a Go and Rust VM")` → `go\nrust`
3. **Plan:**
   ```
   INTENT:create_vm
   VM:go
   rust
   FLAGS:rebuild=false nocache=false
   ```
4. `execute_plan` → Calls `vde_create_vm go` then `vde_create_vm rust`

#### Example 3: Wildcard with Flags

**Input:** "rebuild all languages with no cache"

**Trace:**
1. `detect_intent("rebuild all languages with no cache")` → `INTENT_RESTART_VM`
2. `extract_vm_names("rebuild all languages with no cache")` → All language VMs
3. `extract_flags("rebuild all languages with no cache")` → `rebuild=true nocache=true`
4. **Plan:**
   ```
   INTENT:restart_vm
   VM:python
   rust
   go
   ... (all languages)
   FLAGS:rebuild=true nocache=true
   ```
5. `execute_plan` → Restarts each language VM with rebuild and no-cache flags

#### Example 4: Ambiguous Input

**Input:** "please help me figure this out"

**Trace:**
1. `detect_intent()` → Matches "help" pattern → `INTENT_HELP`
2. No entity extraction needed
3. **Plan:**
   ```
   INTENT:help
   ```
4. `execute_plan` → Calls `show_parser_help()`

---

### Summary

The VDE Parser demonstrates that sophisticated natural language understanding can be achieved in shell script through:

1. **Careful architecture**: Cascading intent detection, known-entity validation
2. **Shell-native techniques**: Associative arrays, pattern matching, pipelines
3. **Defensive programming**: Validation, graceful fallbacks, clear error messages
4. **Extensibility**: Easy to add intents, entities, and operations

The parser is a testament to the power of Unix philosophy: small, focused tools that compose to solve complex problems elegantly.

---

### File Reference

**Primary file:** `$VDE_ROOT_DIR/lib/vde-parser`

**Dependencies:**
- `$VDE_ROOT_DIR/lib/vm-common` (VM type queries, validation)
- `$VDE_ROOT_DIR/lib/vde-commands` (Safe wrapper functions)

**Configuration:**
- `$VDE_ROOT_DIR/data/vm-types.conf` (18 languages, 7 services)


