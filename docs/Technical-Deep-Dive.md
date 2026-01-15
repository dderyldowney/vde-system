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
│  │  │   scripts/   │  │   configs/   │  │   projects/  │          │   │
│  │  │              │  │   docker/    │  │              │          │   │
│  │  │ • lib/       │  │              │  │ • c/         │◄─────┐   │   │
│  │  │   • vde-*    │  │ • base-dev   │  │ • cpp/       │       │   │   │
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
        │  python-dev  │ │  go-dev  │ │  postgres    │
        │  :2200       │ │  :2207   │ │  :2400       │
        └──────────────┘ └──────────┘ └──────────────┘
                │               │               │
                └───────────────┴───────────────┘
                                │
                        ┌───────▼───────┐
                        │  vde-network  │
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
│  │ ~/.ssh/      │◄────────┤ • Holds private keys             │ │
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
- `detect_ssh_keys()` - Find all SSH keys in ~/.ssh/
- `get_primary_ssh_key()` - Select best key (priority: ed25519 > ecdsa > rsa > dsa)
- `get_ssh_pubkey()` - Get public key for private key
- `sync_ssh_keys_to_vde()` - Copy all public keys to public-ssh-keys/

**SSH Agent Management:**
- `ssh_agent_is_running()` - Check if SSH agent is running
- `ensure_ssh_agent()` - Start agent, load keys (automatic, silent)
- `ensure_ssh_environment()` - One-call setup for all SSH operations

**SSH Configuration:**
- `generate_vm_ssh_config()` - Create VM-to-VM SSH config entries
- `merge_ssh_config_entry()` - Safely add SSH entries to ~/.ssh/config
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

**In base-dev.Dockerfile:**
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

VDE uses a **modular library architecture** that separates concerns and enables selective loading. All libraries are located in `scripts/lib/` and can be sourced independently.

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
         │ vde-ai-api  │                      │
         │(AI client)  │                      │
         └─────────────┘                      │
                                            │
                ┌─────────────────────────────┘
                ▼
         ┌─────────────┐              ┌─────────────┐
         │  vde-parser │              │vde-commands │
         │(NLP parsing)│──────────────▶│(API wrapper)│
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

| Library | Lines | Purpose |
|---------|-------|---------|
| `vde-shell-compat` | 719 | Shell detection, portable associative arrays, date/time operations |
| `vde-constants` | 204 | Standardized return codes, port ranges, timeouts, error messages |
| `vde-errors` | 306 | Contextual error messages with remediation steps, color support |
| `vde-log` | 469 | Structured logging (text/JSON/syslog), rotation, query functions |
| `vde-core` | 297 | Essential VM operations, type loading with caching, lazy module loading |
| `vde-ai-api` | 281 | Anthropic API client, natural language command parsing |
| `vde-parser` | 890 | Natural language parser, intent detection, entity extraction |
| `vde-commands` | 545 | High-level command wrappers for AI assistant, batch operations |
| `vm-common` | 2158 | Full VDE API including SSH, Docker, templates (legacy) |

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

### AI & NLP Libraries: vde-ai-api, vde-parser

**Purpose:** Enable natural language interaction with VDE through AI-powered command parsing.

**vde-ai-api Functions:**
- `call_ai_api()` - Make API call to Anthropic or compatible endpoint
- `extract_ai_content()` - Extract text content from API response
- `parse_command_with_ai()` - Parse natural language using AI
- `ai_api_available()` - Check if API key is configured
- `show_ai_config()` - Display API configuration

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

**Purpose:** High-level command wrappers designed for AI assistant invocation.

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

---

## Part 2: Core Data Structure (vm-types.conf)

Everything starts with the **vm-types.conf** file. This is the single source of truth for all VM types.

**File:** `scripts/data/vm-types.conf`

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

**All 19 Language VMs:**
| Name | Aliases | Display Name | SSH Port Range |
|------|---------|--------------|---------------|
| c | c | C | 2200-2217 |
| cpp | c++,gcc | C++ | 2200-2217 |
| asm | assembler,nasm | Assembler | 2200-2217 |
| python | python3 | Python | 2200-2217 |
| rust | rust | Rust | 2200-2217 |
| js | node,nodejs | JavaScript | 2200-2217 |
| csharp | dotnet | C# | 2200-2217 |
| ruby | ruby | Ruby | 2200-2217 |
| go | golang | Go | 2200-2217 |
| java | jdk | Java | 2200-2217 |
| kotlin | kotlin | Kotlin | 2200-2217 |
| swift | swift | Swift | 2200-2217 |
| php | php | PHP | 2200-2217 |
| scala | scala | Scala | 2200-2217 |
| r | rlang,r | R | 2200-2217 |
| lua | lua | Lua | 2200-2217 |
| flutter | dart,flutter | Flutter | 2200-2217 |
| elixir | elixir | Elixir | 2200-2217 |
| haskell | ghc,haskell | Haskell | 2200-2217 |

**All 7 Service VMs:**
| Name | Aliases | Display Name | SSH Port | Service Port(s) |
|------|---------|--------------|----------|----------------|
| postgres | postgresql | PostgreSQL | 2400-2406 | 5432 |
| redis | redis | Redis | 2400-2406 | 6379 |
| mongodb | mongo | MongoDB | 2400-2406 | 27017 |
| nginx | nginx | Nginx | 2400-2406 | 80,443 |
| couchdb | couchdb | CouchDB | 2400-2406 | 5984 |
| mysql | mysql | MySQL | 2400-2406 | 3306 |
| rabbitmq | rabbitmq | RabbitMQ | 2400-2406 | 5672,15672 |

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
. "$VDE_ROOT_DIR/scripts/lib/vde-shell-compat"

# 2. vde-constants - Standardized return codes and constants
. "$VDE_ROOT_DIR/scripts/lib/vde-constants"

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

VDE provides a **unified command-line interface** through the `vde` script located at `scripts/vde`. This is the recommended way to interact with VDE.

### Usage

```bash
vde <command> [options] [args]
```

### Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `create <vm>` | Create a new VM | `vde create python` |
| `start <vm>` | Start a VM | `vde start python` |
| `stop <vm>` | Stop a VM | `vde stop postgres` |
| `restart <vm>` | Restart a VM | `vde restart rust` |
| `list` | List all VMs | `vde list` |
| `status` | Show VM status | `vde status` |
| `health` | Run system health check | `vde health` |
| `chat` | Start AI assistant chat | `vde chat` |
| `help` | Show help message | `vde help` |

### Options

| Option | Description |
|--------|-------------|
| `-h, --help` | Show help message |
| `-v, --verbose` | Enable verbose output |
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

### Source Chain

When you run `vde`, it sources libraries in the following order:

```bash
# 1. vde-shell-compat - Shell portability
source "$VDE_ROOT_DIR/scripts/lib/vde-shell-compat"

# 2. vde-constants - Return codes, constants
source "$VDE_ROOT_DIR/scripts/lib/vde-constants"

# 3. vde-errors - Error messages
source "$VDE_ROOT_DIR/scripts/lib/vde-errors"

# 4. vde-log - Logging system
source "$VDE_ROOT_DIR/scripts/lib/vde-log"

# 5. vde-core - Core VM operations
source "$VDE_ROOT_DIR/scripts/lib/vde-core"

# 6. vm-common - Full VDE API
source "$VDE_ROOT_DIR/scripts/lib/vm-common"
```

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

# Start AI assistant chat
vde chat
```

---

## Part 5: Template System

The VDE uses **template variable substitution** to generate docker-compose.yml files.

### 5.1 Language Template (`templates/compose-language.yml`)

```yaml
services:
  {{NAME}}-dev:                    # e.g., "go-dev"
    build:
      context: ../../..
      dockerfile: configs/docker/base-dev.Dockerfile
      args:
        USERNAME: devuser
        UID: 1000
        GID: 1000
        PUBLIC_KEYS_DIR: /public-ssh-keys
    image: dev-{{NAME}}:latest      # e.g., "dev-go:latest"
    container_name: {{NAME}}-dev    # e.g., "go-dev"
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
      - dev-net
```

### 5.2 Service Template (`templates/compose-service.yml`)

```yaml
services:
  {{NAME}}:                        # No "-dev" suffix!
    # ... (same build config)
    container_name: {{NAME}}        # e.g., "postgres" not "postgres-dev"

    ports:
      - "{{SSH_PORT}}:22"          # SSH access
      - "{{SERVICE_PORT}}:{{SERVICE_PORT}}"  # Service port(s)

    volumes:
      - ../../../data/{{NAME}}:/data   # Note: "data" not "projects"
      - ../../../logs/{{NAME}}:/logs
      # ...
```

### 5.3 Template Rendering

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
- python-dev: SSH_PORT=2222
- js-dev: SSH_PORT=2224

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
./scripts/create-virtual-for go
```

### Step 1: Using the Unified CLI

```bash
vde create go
```

This invokes the `vde` script which sources all libraries and then calls `create-virtual-for go`.

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
# Checks: does ~/.ssh/id_ed25519 exist? Yes.
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
# Finds: python-dev (2222), js-dev (2224), rust-dev (2223)
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
  go-dev:
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
ssh_host="${VM_NAME}-dev"  # "go-dev" (language VMs get -dev suffix)

merge_ssh_config_entry "$ssh_host" "2200" "Go"
# 1. Backs up ~/.ssh/config to ~/dev/backup/ssh/config.backup.TIMESTAMP
# 2. Generates SSH entry from template
# 3. Appends to ~/.ssh/config
```

**Generated SSH entry:**
```ssh-config
# Go Dev VM
Host go-dev
    HostName localhost
    Port 2200
    User devuser
    IdentityFile ~/.ssh/id_ed25519
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
  - Host alias: go-dev
  - SSH port: 2200
  - Connect with: ssh go-dev

Next steps:
  1. Review and customize env-files/go.env if needed
  2. Start the VM: vde start go
  3. Connect: ssh go-dev
```

---

## Part 8: Starting the VM

Now you run:

```bash
vde start go
```

Or equivalently:

```bash
./scripts/start-virtual go
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
     -f configs/docker/base-dev.Dockerfile \
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
     --name go-dev \
     --hostname go-dev \
     --restart unless-stopped \
     -p 2200:22 \
     -v ~/dev/projects/go:/home/devuser/workspace \
     -v ~/dev/logs/go:/logs \
     -v ~/dev/public-ssh-keys:/public-ssh-keys:ro \
     --env-file ~/dev/env-files/go.env \
     --network dev-net \
     dev-go:latest \
     sh -c "apt-get update -y && apt-get install -y golang-go && /usr/sbin/sshd -D"
   ```

3. **Start container**: `docker start go-dev`

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
- **SSH accessible** on localhost:2200
- **Go installed** and available to devuser
- **Workspace mounted** at `/home/devuser/workspace`

---

## Part 9: SSH Connection

You can now connect:

```bash
ssh go-dev
```

### SSH Connection Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. SSH Client reads ~/.ssh/config                              │
│    Finds "Host go-dev" entry                                   │
│    - HostName: localhost                                       │
│    - Port: 2200                                                │
│    - User: devuser                                             │
│    - IdentityFile: ~/.ssh/id_ed25519                           │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. SSH connects to localhost:2200                              │
│    Port 2200 is mapped by Docker to go-dev:22                 │
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
│    devuser@go-dev:~$                                           │
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
devuser@go-dev:~$ cd ~/workspace
devuser@go-dev:~/workspace$ ls -la
# Shows contents of ~/dev/projects/go on host

devuser@go-dev:~/workspace$ go version
# go version go1.21 debian

devuser@go-dev:~/workspace$ cat > main.go << 'EOF'
package main
import "fmt"
func main() {
    fmt.Println("Hello from VDE!")
}
EOF

devuser@go-dev:~/workspace$ go run main.go
Hello from VDE!
```

**Key point:** Files created in `~/workspace` are actually created in `~/dev/projects/go` on the host (via volume mount).

---

## Part 10: Service VMs (Different Pattern)

Service VMs (like PostgreSQL) work differently:

### Key Differences

| Aspect | Language VM | Service VM |
|--------|-------------|------------|
| Container name | `go-dev` | `postgres` (no suffix) |
| SSH host | `go-dev` | `postgres` |
| SSH port range | 2200-2218 (19 languages) | 2400-2406 (7 services) |
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

All containers are on the `vde-network` Docker network, enabling communication:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ python-dev  │     │  postgres   │     │    redis    │
│   :2200     │     │   :2400     │     │   :2401     │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                  │                  │
       └──────────────────┴──────────────────┘
                          │
                  ┌───────▼───────┐
                  │  vde-network  │
                  │ (bridge net)  │
                  └───────────────┘
```

**From python-dev container:**
```bash
# Connect to PostgreSQL
psql -h postgres -U devuser -d mydb

# Connect to Redis
redis-cli -h redis

# SSH to another container
ssh go-dev
```

**Service discovery works via container names** because Docker's embedded DNS resolves container names to IPs.

---

## Part 12: Multi-Container Management

The scripts support managing multiple VMs at once:

```bash
# Using the unified CLI
vde start python go rust postgres redis

# Or using direct scripts
./scripts/start-virtual python go rust postgres redis

# This internally does:
for vm in "python" "go" "rust" "postgres" "redis"; do
    start_vm "$vm" "$rebuild" "$nocache"
done
```

**Special case: `all` keyword**

```bash
vde start all
# or
./scripts/start-virtual all
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
# or
./scripts/shutdown-virtual go
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
1. Stops the container: `docker stop go-dev`
2. Removes the container: `docker rm go-dev`
3. **Does NOT remove** the image (dev-go:latest persists)
4. **Does NOT remove** volumes (data persists on host)

---

## Part 14: Adding New VM Types

The `add-vm-type` script appends new entries to `vm-types.conf`:

```bash
./scripts/add-vm-type zig \
    "apt-get update -y && apt-get install -y zig"
```

Or using the unified CLI:

```bash
vde add-vm-type zig "apt-get update -y && apt-get install -y zig"
```

**Flow:**

1. **Validate** (zig doesn't exist, name is valid)
2. **Backup** vm-types.conf
3. **Append** line:
   ```bash
   lang|zig||Zig|apt-get update -y && apt-get install -y zig|
   ```
4. **Reload** VM types: `source lib/vm-common` → `load_vm_types`
5. **Show diff** of changes

Now you can:
```bash
vde create zig
# or
./scripts/create-virtual-for zig
```

---

## Summary: Complete Data Flow

```
User Action:
  ./scripts/create-virtual-for go

↓

Script Entry:
  create-virtual-for sources lib/vm-common
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

  4. Update ~/.ssh/config:
     Append Host go-dev entry

↓

Output:
  [SUCCESS] VM configuration complete!
  Connect with: ssh go-dev

↓

Start VM:
  ./scripts/start-virtual go
  ↓
  docker-compose -f configs/docker/go/docker-compose.yml up -d
  ↓
  Docker builds image (dev-go:latest)
  ↓
  Docker creates container (go-dev)
  ↓
  Docker starts container
  ↓
  Container runs: apt-get install golang-go && /usr/sbin/sshd -D

↓

Connect:
  ssh go-dev
  ↓
  SSH connects to localhost:2200
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
9. **Networked**: All containers on vde-network for inter-communication
10. **Extensible**: Add new languages/services by editing one file
11. **Idempotent**: Safe to run create-virtual-for multiple times (fails if exists)
12. **AI-Ready**: Natural language parsing and AI assistant integration

---

## File Reference

### Core Library Files

| File | Lines | Purpose |
|------|-------|---------|
| `scripts/lib/vde-shell-compat` | 719 | Shell detection, portable associative arrays, date/time operations |
| `scripts/lib/vde-constants` | 204 | Standardized return codes, port ranges, timeouts, configuration |
| `scripts/lib/vde-errors` | 306 | Contextual error messages with remediation steps |
| `scripts/lib/vde-log` | 469 | Structured logging (text/JSON/syslog), rotation, query functions |
| `scripts/lib/vde-core` | 297 | Essential VM operations, type loading with caching |
| `scripts/lib/vde-ai-api` | 281 | Anthropic API client, natural language command parsing |
| `scripts/lib/vde-parser` | 890 | Natural language parser, intent detection, entity extraction |
| `scripts/lib/vde-commands` | 545 | High-level command wrappers for AI assistant |
| `scripts/lib/vm-common` | 2158 | Full VDE API including SSH, Docker, templates |

### Core Scripts

| File | Lines | Purpose |
|------|-------|---------|
| `scripts/vde` | 237 | Unified CLI command for all VDE operations |
| `scripts/data/vm-types.conf` | 34 | VM type definitions (19 languages + 7 services) |
| `scripts/create-virtual-for` | 199+ | Create new VM from predefined type |
| `scripts/start-virtual` | 85+ | Start one or more VMs |
| `scripts/shutdown-virtual` | 65+ | Stop one or more VMs |
| `scripts/add-vm-type` | 252+ | Add new VM type to vm-types.conf |
| `scripts/list-vms` | - | List all VMs and their status |

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
| `~/.ssh/config` | SSH configuration (entry appended) |

---

This is the complete VDE system from configuration to container runtime. Every piece serves a specific purpose in the overall architecture of providing isolated, consistent development environments.

The system has evolved from a simple template-based approach to a sophisticated modular architecture with:
- **Shell portability** across zsh, bash 4.0+, and bash 3.x
- **Modular libraries** that can be sourced independently
- **Unified CLI** through the `vde` command
- **AI-powered natural language** interaction
- **Structured logging** with rotation and query capabilities
- **Contextual error messages** with remediation steps
- **19 language VMs** and **7 service VMs** supported out of the box
