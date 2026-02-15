# VDE Technical Specification

**Document Type:** Technical Implementation Specification  
**Project:** Virtual Development Environment (VDE)  
**Version:** 1.0.0  
**Status:** AUTHORITATIVE SPECIFICATION  
**Last Updated:** 2026-02-13T21:48:00Z

> **MANDATE**: This document is the authoritative specification for the VDE project. All development, bug fixes, and implementation work MUST conform to this specification.
>
> **Specification by Tests - Complete Flow**:
> ```
> USER GUIDE (Documented Workflows)
>         ↓
> SPECIFICATION (Technical Requirements)
>         ↓
> CODE / IMPLEMENTATION
>         ↓
> TESTS (Prove implementation works as designed)
>   Scenarios → Individual Steps
> ```
>
> The User Guide documents the workflows. The Specification translates these into technical requirements. The Code implements the specification. The Tests prove the code does what it was designed to do, from Scenarios (feature-level) down to individual Steps (implementation-level).
>
> **Update Authorization**: Specification updates require explicit User authorization. Agents must not modify this specification without prior approval.
>
> **Revision Control**: The version number MUST be incremented for EVERY single change, whether to test requirements or specification blocks. The Last Updated timestamp MUST also be updated to full ISO 8601 format (e.g., 2026-02-13T21:48:00Z). Minor changes increment the patch version (1.0.1), significant changes increment minor (1.1.0), breaking changes increment major (2.0.0).

---

## 1. Overview

This document provides a technical specification for the Virtual Development Environment (VDE) system. It is designed to be implementation-complete: a competent developer should be able to implement the entire system from this specification alone.

---

## 2. Core Data Structures

### 2.1 VM Type Configuration

**File:** `scripts/data/vm-types.json`

```json
{
  "vms": {
    "language": [
      {
        "name": "string (required, unique)",
        "aliases": ["string"],
        "display": "string",
        "install": "string (shell command)",
        "port": "number (2200-2299)"
      }
    ],
    "service": [
      {
        "name": "string (required, unique)",
        "aliases": ["string"],
        "display": "string",
        "install": "string (shell command)",
        "port": "number (2400-2499)",
        "service_port": "number (application port)"
      }
    ]
  }
}
```

### 2.2 VM Type Arrays (Runtime)

```zsh
# Global associative arrays - sourced from vm-types.conf or cache
typeset -gA VM_TYPE       # name -> "lang" | "service"
typeset -gA VM_ALIASES   # name -> comma-separated aliases
typeset -gA VM_DISPLAY   # name -> display name
typeset -gA VM_INSTALL   # name -> install command
typeset -gA VM_SVC_PORT  # name -> service port (services only)

# Index arrays
typeset -ga lang_vms     # ordered list of language VM names
typeset -ga service_vms   # ordered list of service VM names
```

### 2.3 Port Registry

**File:** `.cache/port-registry`

```
# Format: one entry per line
vm_name:port
python:2200
rust:2201
postgres:2400
```

### 2.4 Cache File Format

**File:** `.cache/vm-types.cache`

```zsh
# VM Types Cache - Auto-generated
# DO NOT EDIT MANUALLY

typeset -gA VM_TYPE
VM_TYPE[python]='lang'
VM_TYPE[rust]='lang'
...

typeset -gA VM_ALIASES
VM_ALIASES[python]='python3'
...

lang_vms=(python rust go js ...)
service_vms=(postgres redis mongodb ...)
```

---

## 3. Library Interface Specifications

### 3.1 vde-constants

**File:** `scripts/lib/vde-constants`

```zsh
# Return Codes
readonly VDE_SUCCESS=0
readonly VDE_ERR_GENERAL=1
readonly VDE_ERR_INVALID_INPUT=2
readonly VDE_ERR_NOT_FOUND=3
readonly VDE_ERR_PERMISSION=4
readonly VDE_ERR_TIMEOUT=5
readonly VDE_ERR_EXISTS=6
readonly VDE_ERR_DEPENDENCY=7

# Port Ranges
readonly LANG_PORT_START=2200
readonly LANG_PORT_END=2299
readonly SVC_PORT_START=2400
readonly SVC_PORT_END=2499

# Directory Paths
readonly CONFIGS_DIR="${VDE_ROOT_DIR}/configs/docker"
readonly SCRIPTS_DIR="${VDE_ROOT_DIR}/scripts"
readonly TEMPLATES_DIR="${SCRIPTS_DIR}/templates"
readonly DATA_DIR="${SCRIPTS_DIR}/data"
readonly BACKUP_DIR="${VDE_ROOT_DIR}/backup"
readonly CACHE_DIR="${VDE_ROOT_DIR}/.cache"
readonly VM_TYPES_CONF="${DATA_DIR}/vm-types.conf"
readonly VM_TYPES_JSON="${DATA_DIR}/vm-types.json"
readonly VM_TYPES_CACHE="${CACHE_DIR}/vm-types.cache"
readonly PORT_REGISTRY="${CACHE_DIR}/port-registry"
```

### 3.2 vde-shell-compat

**File:** `scripts/lib/vde-shell-compat`

```zsh
# _assoc_init NAME
# Initialize associative array with given name
# Args: NAME (string) - variable name
# Returns: VDE_SUCCESS

# _assoc_set NAME KEY VALUE
# Set key-value pair in associative array
# Args: NAME (string), KEY (string), VALUE (string)
# Returns: VDE_SUCCESS

# _assoc_get NAME KEY
# Get value from associative array
# Args: NAME (string), KEY (string)
# Output: value to stdout
# Returns: VDE_SUCCESS or VDE_ERR_NOT_FOUND

# _assoc_has_key NAME KEY
# Check if key exists in associative array
# Args: NAME (string), KEY (string)
# Returns: VDE_SUCCESS if exists, VDE_ERR_NOT_FOUND otherwise

# _assoc_clear NAME
# Clear all entries from associative array
# Args: NAME (string)
# Returns: VDE_SUCCESS

# _get_script_path
# Get absolute path of currently executing script
# Output: absolute path to stdout
# Returns: VDE_SUCCESS
```

### 3.3 vm-common

**File:** `scripts/lib/vm-common`

```zsh
# load_vm_types
# Load VM type definitions from config or cache
# Returns: VDE_SUCCESS on load, error code otherwise

# get_vm_info FIELD VM_NAME
# Get specific field for a VM
# Args: FIELD (type|aliases|display|install|svc_port), VM_NAME (string)
# Output: field value to stdout
# Returns: VDE_SUCCESS or VDE_ERR_NOT_FOUND

# get_all_vms
# Get all VM names (languages and services)
# Output: space-separated list to stdout
# Returns: VDE_SUCCESS

# get_lang_vms
# Get language VM names only
# Output: space-separated list to stdout
# Returns: VDE_SUCCESS

# get_service_vms
# Get service VM names only
# Output: space-separated list to stdout
# Returns: VDE_SUCCESS

# is_known_vm VM_NAME
# Check if VM name or alias exists
# Args: VM_NAME (string)
# Returns: VDE_SUCCESS if valid, VDE_ERR_NOT_FOUND otherwise

# resolve_vm_name ALIAS_OR_NAME
# Resolve alias to canonical name
# Args: ALIAS_OR_NAME (string)
# Output: canonical name to stdout
# Returns: VDE_SUCCESS or VDE_ERR_NOT_FOUND

# find_next_available_port VM_TYPE
# Find next available port in range
# Args: VM_TYPE (lang|service)
# Output: port number to stdout
# Returns: VDE_SUCCESS or VDE_ERR_EXISTS (no ports available)

# vm_exists VM_NAME
# Check if VM configuration exists
# Args: VM_NAME (string)
# Returns: VDE_SUCCESS if exists, VDE_ERR_NOT_FOUND otherwise

# get_vm_port VM_NAME
# Get allocated port for VM
# Args: VM_NAME (string)
# Output: port number to stdout
# Returns: VDE_SUCCESS or VDE_ERR_NOT_FOUND

# render_template TEMPLATE_NAME KEY=VALUE ...
# Render template with variables
# Args: TEMPLATE_NAME (string), key=value pairs
# Output: rendered file to stdout
# Returns: VDE_SUCCESS or VDE_ERR_NOT_FOUND (template missing)

# merge_ssh_config_entry HOST PORT USER
# Add SSH config entry atomically
# Args: HOST (string), PORT (number), USER (string)
# Returns: VDE_SUCCESS or VDE_ERR_EXISTS (entry exists)
```

### 3.4 vde-parser

**File:** `scripts/lib/vde-parser`

```zsh
# Intent Constants
readonly INTENT_LIST_VMS="list_vms"
readonly INTENT_CREATE_VM="create_vm"
readonly INTENT_START_VM="start_vm"
readonly INTENT_STOP_VM="stop_vm"
readonly INTENT_RESTART_VM="restart_vm"
readonly INTENT_STATUS="status"
readonly INTENT_CONNECT="connect"
readonly INTENT_ADD_VM_TYPE="add_vm_type"
readonly INTENT_HELP="help"

# detect_intent INPUT_STRING
# Detect primary intent from natural language input
# Args: INPUT_STRING (string)
# Output: INTENT_* constant to stdout
# Returns: VDE_SUCCESS (always)

# extract_vm_names INPUT_STRING
# Extract VM names from natural language input
# Args: INPUT_STRING (string)
# Output: newline-separated canonical VM names
# Returns: VDE_SUCCESS (always)

# extract_filter INPUT_STRING
# Extract filter type (lang|svc|all) from input
# Args: INPUT_STRING (string)
# Output: "lang" | "svc" | "all"
# Returns: VDE_SUCCESS (always)

# extract_flags INPUT_STRING
# Extract operation flags from input
# Args: INPUT_STRING (string)
# Output: "rebuild=true|false nocache=true|false"
# Returns: VDE_SUCCESS (always)

# _lookup_vm_by_alias ALIAS_OR_NAME
# O(1) lookup of VM name by alias
# Args: ALIAS_OR_NAME (string)
# Output: canonical name to stdout
# Returns: VDE_SUCCESS or VDE_ERR_NOT_FOUND

# contains_dangerous_chars STRING
# Check for shell injection characters
# Args: STRING (string)
# Returns: VDE_SUCCESS if dangerous chars found, VDE_ERR_NOT_FOUND otherwise

# validate_plan_line LINE
# Validate plan line against whitelist
# Args: LINE (string)
# Returns: VDE_SUCCESS or VDE_ERR_INVALID_INPUT
```

### 3.5 vde-commands

**File:** `scripts/lib/vde-commands`

```zsh
# vde_list [filter]
# List VMs by type
# Args: filter (lang|svc|all, default: all)
# Returns: VDE_SUCCESS or error code

# vde_create VM_NAME
# Create a new VM
# Args: VM_NAME (string)
# Returns: VDE_SUCCESS or error code

# vde_start VM_NAMES... [--rebuild] [--no-cache]
# Start one or more VMs
# Args: VM_NAME(s), optional flags
# Returns: VDE_SUCCESS or error code

# vde_stop VM_NAMES...
# Stop one or more VMs
# Args: VM_NAME(s)
# Returns: VDE_SUCCESS or error code

# vde_restart VM_NAMES... [--rebuild] [--no-cache]
# Restart one or more VMs
# Args: VM_NAME(s), optional flags
# Returns: VDE_SUCCESS or error code

# vde_status
# Show status of all VMs
# Returns: VDE_SUCCESS

# vde_connect VM_NAME
# Get SSH connection information
# Args: VM_NAME (string)
# Returns: VDE_SUCCESS or error code
```

### 3.6 vde-ssh

**File:** `scripts/lib/vde-ssh`

```zsh
# ensure_ssh_agent
# Start SSH agent if not running
# Returns: VDE_SUCCESS

# detect_ssh_keys
# Find all SSH keys in ~/.ssh/vde/
# Output: newline-separated key filenames
# Returns: VDE_SUCCESS

# get_primary_ssh_key
# Get best available SSH key (ed25519 > ecdsa > rsa > dsa)
# Output: key filename to stdout
# Returns: VDE_SUCCESS or VDE_ERR_NOT_FOUND

# generate_ssh_key
# Generate new ed25519 SSH key
# Returns: VDE_SUCCESS or error code

# sync_ssh_keys_to_vde
# Copy public keys to public-ssh-keys directory
# Returns: VDE_SUCCESS

# ensure_ssh_environment
# One-call SSH setup (agent + keys + config)
# Returns: VDE_SUCCESS

# generate_vm_ssh_config VM_NAME PORT
# Generate SSH config entry for VM
# Args: VM_NAME (string), PORT (number)
# Returns: VDE_SUCCESS

# merge_ssh_config_entry ENTRY
# Merge entry into SSH config atomically
# Args: ENTRY (string - full config block)
# Returns: VDE_SUCCESS or error code
```

### 3.7 vde-docker

**File:** `scripts/lib/vde-docker`

```zsh
# docker_build VM_NAME
# Build Docker image for VM
# Args: VM_NAME (string)
# Returns: VDE_SUCCESS or error code

# docker_start VM_NAME
# Start container for VM
# Args: VM_NAME (string)
# Returns: VDE_SUCCESS or error code

# docker_stop VM_NAME
# Stop container for VM
# Args: VM_NAME (string)
# Returns: VDE_SUCCESS or error code

# docker_restart VM_NAME
# Restart container for VM
# Args: VM_NAME (string)
# Returns: VDE_SUCCESS or error code

# docker_status VM_NAME
# Get container status
# Args: VM_NAME (string)
# Output: "running" | "stopped" | "not_created" | "unknown"
# Returns: VDE_SUCCESS

# docker_get_running
# Get list of running VM names
# Output: space-separated list
# Returns: VDE_SUCCESS
```

### 3.8 vde-templates

**File:** `scripts/lib/vde-templates`

```zsh
# render_language_template NAME SSH_PORT
# Render docker-compose.yml for language VM
# Args: NAME (string), SSH_PORT (number)
# Output: YAML to stdout
# Returns: VDE_SUCCESS

# render_service_template NAME SSH_PORT SERVICE_PORT
# Render docker-compose.yml for service VM
# Args: NAME (string), SSH_PORT (number), SERVICE_PORT (number)
# Output: YAML to stdout
# Returns: VDE_SUCCESS

# render_ssh_entry VM_NAME PORT
# Render SSH config entry
# Args: VM_NAME (string), PORT (number)
# Output: SSH config block to stdout
# Returns: VDE_SUCCESS
```

---

## 4. CLI Interface Specification

### 4.1 Main Entry Point: `vde`

**Location:** `scripts/vde`

```zsh
#!/usr/bin/env zsh
# Usage: vde <command> [options] [arguments]
#
# Commands:
#   create <vm>              Create a new VM
#   start <vm> [...]         Start one or more VMs
#   stop <vm> [...]         Stop one or more VMs
#   restart <vm> [...]      Restart one or more VMs
#   remove <vm>             Remove a VM instance
#   list [filter]           List VMs (lang|svc|all)
#   status                  Show VM status
#   health                  Run health check
#   help                    Show help
#
# Options:
#   --rebuild               Rebuild before starting
#   --no-cache              Build without cache
#   --update-ssh            Regenerate SSH config
```

### 4.2 Direct Scripts

| Script | Location | Usage |
|--------|----------|-------|
| list-vms | `scripts/list-vms` | `./list-vms [--lang\|--svc] [search]` |
| create-virtual-for | `scripts/create-virtual-for` | `./create-virtual-for <name>` |
| start-virtual | `scripts/start-virtual` | `./start-virtual <name>... [--rebuild] [--no-cache]` |
| shutdown-virtual | `scripts/shutdown-virtual` | `./shutdown-virtual <name>...` |
| build-and-start | `scripts/build-and-start` | `./build-and-start [--rebuild] [--no-cache]` |
| add-vm-type | `scripts/add-vm-type` | `./add-vm-type <name> "<install>" [aliases]` |

---

## 5. Template Formats

### 5.1 Language VM Template

**File:** `scripts/templates/compose-language.yml`

```yaml
services:
  {{NAME}}-dev:
    build:
      context: ../../
      dockerfile: configs/docker/vde-base.Dockerfile
    container_name: {{NAME}}-dev
    ports:
      - "{{SSH_PORT}}:22"
    volumes:
      - {{WORKSPACE}}:/home/devuser/workspace
      - {{LOGS}}:/home/devuser/logs
      - ${SSH_AUTH_SOCK:-/tmp/ssh-agent.sock}:/ssh-agent/sock:ro
      - ../../public-ssh-keys:/public-ssh-keys:ro
    environment:
      - SSH_PORT={{SSH_PORT}}
      - SSH_AUTH_SOCK=/ssh-agent/sock
    networks:
      - vde-net
    restart: unless-stopped
    user: devuser
    labels:
      - "vde.type=language"
      - "vde.name={{NAME}}"

networks:
  vde-net:
    name: vde-network
    external: true
```

### 5.2 Service VM Template

**File:** `scripts/templates/compose-service.yml`

```yaml
services:
  {{NAME}}:
    image: {{IMAGE}}
    container_name: {{NAME}}
    ports:
      - "{{SSH_PORT}}:22"
      - "{{SERVICE_PORT}}:{{SERVICE_PORT}}"
    volumes:
      - {{DATA}}:/var/lib/{{NAME}}
      - ${SSH_AUTH_SOCK:-/tmp/ssh-agent.sock}:/ssh-agent/sock:ro
    environment:
      - SSH_PORT={{SSH_PORT}}
    networks:
      - vde-net
    restart: unless-stopped
    labels:
      - "vde.type=service"
      - "vde.name={{NAME}}"
```

### 5.3 SSH Config Entry Template

**File:** `scripts/templates/ssh-entry.txt`

```
Host {{VM_NAME}}-dev
    HostName localhost
    Port {{SSH_PORT}}
    User devuser
    ForwardAgent yes
    StrictHostKeyChecking no
    IdentityFile ~/.ssh/vde/id_ed25519
```

---

## 6. Docker Configuration

### 6.1 Base Dockerfile

**File:** `configs/docker/vde-base.Dockerfile`

```dockerfile
FROM ubuntu:22.04

# System packages
RUN apt-get update && apt-get install -y \
    openssh-server \
    openssh-client \
    zsh \
    curl \
    wget \
    git \
    vim \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# Create devuser
RUN useradd -m -s /bin/zsh -u 1000 -g 1000 devuser
RUN echo 'devuser ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

# SSH configuration
RUN mkdir /var/run/sshd
RUN echo 'PermitRootLogin no' >> /etc/ssh/sshd_config
RUN echo 'AllowAgentForwarding yes' >> /etc/ssh/sshd_config
RUN echo 'AllowUsers devuser' >> /etc/ssh/sshd_config

# Oh-My-Zsh
RUN su - devuser -c "sh -c 'curl -L https://install.ohmyz.sh | sh'"

# LazyVim
RUN su - devuser -c "git clone https://github.com/LazyVim/LazyVim.git ~/.config/nvim"

# SSH agent forwarding script
COPY ssh-agent-forward.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/ssh-agent-forward.sh

EXPOSE 22

CMD ["/usr/sbin/sshd", "-D"]
```

---

## 7. Error Handling Specification

### 7.1 Error Message Format

```zsh
# Each error should include:
# - What happened
# - Why it happened
# - How to fix it (suggestions)

_error() {
    echo "[ERROR] $1" >&2
    echo "        $2" >&2
    echo "        Suggestion: $3" >&2
}
```

### 7.2 Standard Error Messages

| Error Code | Condition | Message Format |
|------------|-----------|----------------|
| VDE_ERR_NOT_FOUND | VM not found | "Unknown VM: $VM_NAME. Available: $LIST" |
| VDE_ERR_EXISTS | VM already exists | "VM '$VM_NAME' already exists. Use 'vde start $VM_NAME' or 'vde remove $VM_NAME' first." |
| VDE_ERR_INVALID_INPUT | Invalid input | "Invalid value '$VALUE' for $FIELD. Valid values: $LIST" |
| VDE_ERR_PERMISSION | Permission denied | "Permission denied. Ensure you have write access to $PATH" |
| VDE_ERR_TIMEOUT | Operation timeout | "Operation timed out after $SECONDS seconds. Try again or check logs." |
| VDE_ERR_DEPENDENCY | Missing dependency | "Required dependency '$TOOL' not found. Install with: $INSTALL_CMD" |

---

## 8. Natural Language Parsing Specification

### 8.1 Intent Detection Rules

```zsh
# Order matters - check more specific patterns first

# 1. Help intent (includes typos)
detect_help() {
    case "$input" in
        *help*|*hel*|*hepl*|"what can i do"|"how do i use"*) return help ;;
    esac
}

# 2. Status intent
detect_status() {
    case "$input" in
        *running*|*"status"*|*"staus"*|*"satus"*) return status ;;
    esac
}

# 3. List intent
detect_list() {
    case "$input" in
        *"list"*|*"show "*|*"available"*|*"what can i create"*) return list_vms ;;
    esac
}

# 4. Connect intent
detect_connect() {
    case "$input" in
        *"how do i connect"*|*"connect to"*|*"ssh into"*) return connect ;;
    esac
}

# 5. Restart intent (before start/stop)
detect_restart() {
    case "$input" in
        *restart*|*rebuild*|*reboot*) return restart_vm ;;
    esac
}

# 6. Create intent
detect_create() {
    case "$input" in
        *"create"*|*"make"*|*"set up"*|*"add "*) return create_vm ;;
    esac
}

# 7. Start intent
detect_start() {
    case "$input" in
        *start*|*launch*|*boot*) return start_vm ;;
    esac
}

# 8. Stop intent (last - most generic)
detect_stop() {
    case "$input" in
        *stop*|*shutdown*|*kill*) return stop_vm ;;
    esac
}
```

### 8.2 Entity Extraction

```zsh
# VM name extraction using alias map
# 1. Split input into words
# 2. For each word, lookup in VM_ALIAS_MAP
# 3. If found, add canonical name to result
# 4. Handle "all" special case

# Filter extraction
extract_filter() {
    case "$input" in
        *language*|*lang*) echo "lang" ;;
        *service*|*svc*) echo "svc" ;;
        *) echo "all" ;;
    esac
}

# Flag extraction
extract_flags() {
    local rebuild="false"
    local nocache="false"
    
    [[ "$input" == *rebuild* ]] && rebuild="true"
    [[ "$input" == *"no-cache"* ]] && nocache="true"
    
    echo "rebuild=$rebuild nocache=$nocache"
}
```

---

## 9. File System Layout

```
VDE_ROOT/
├── scripts/
│   ├── vde                          # Main entry point
│   ├── list-vms                     # List VMs
│   ├── create-virtual-for            # Create VM
│   ├── start-virtual                # Start VM
│   ├── shutdown-virtual             # Stop VM
│   ├── remove-virtual               # Remove VM
│   ├── add-vm-type                  # Add new VM type
│   ├── build-and-start               # Build and start all
│   ├── lib/
│   │   ├── vde-constants            # Constants
│   │   ├── vde-shell-compat         # Shell compatibility
│   │   ├── vde-errors               # Error handling
│   │   ├── vde-log                  # Logging
│   │   ├── vde-naming               # Naming validation
│   │   ├── vde-path-utils           # Path utilities
│   │   ├── vde-core                 # Core functions
│   │   ├── vm-common                # Common functions
│   │   ├── vde-commands             # Command wrappers
│   │   ├── vde-parser               # NLP parser
│   │   ├── vde-ssh                  # SSH management
│   │   ├── vde-docker               # Docker operations
│   │   ├── vde-templates            # Template rendering
│   │   ├── vde-health               # Health checks
│   │   ├── vde-audit                # Audit logs
│   │   └── vde-metrics              # Metrics
│   ├── templates/
│   │   ├── compose-language.yml
│   │   ├── compose-service.yml
│   │   └── ssh-entry.txt
│   └── data/
│       ├── vm-types.conf             # Legacy config
│       └── vm-types.json             # JSON config
├── configs/
│   └── docker/
│       ├── vde-base.Dockerfile
│       ├── vde-base.Dockerfile
│       ├── c/, cpp/, python/, ...   # Per-VM configs
│       └── postgres/, redis/, ...    # Service configs
├── data/
│   ├── projects/                    # Project workspaces
│   │   ├── python/, rust/, go/, ...
│   ├── logs/                        # VM logs
│   └── (service data directories)
├── public-ssh-keys/                 # SSH public keys for containers
├── backup/
│   └── ssh/                         # SSH config backups
├── .cache/
│   ├── vm-types.cache               # VM type cache
│   └── port-registry               # Port allocations
├── tests/
│   ├── features/                   # BDD tests
│   └── unit/                       # Unit tests
└── docs/                           # Documentation
```

---

## 10. Port Allocation Algorithm

```zsh
find_next_available_port() {
    local vm_type="$1"  # "lang" or "service"
    
    if [[ "$vm_type" == "lang" ]]; then
        local start=2200
        local end=2299
    else
        local start=2400
        local end=2499
    fi
    
    # Load port registry
    local registry="${PORT_REGISTRY:-.cache/port-registry}"
    declare -A used_ports
    if [[ -f "$registry" ]]; then
        while IFS=':' read -r vm port; do
            used_ports[$port]=1
        done < "$registry"
    fi
    
    # Find first available port
    for port in {$start..$end}; do
        if [[ -z "${used_ports[$port]}" ]]; then
            # Check if port is actually available on host
            if ! nc -z localhost $port 2>/dev/null; then
                echo $port
                return $VDE_SUCCESS
            fi
        fi
    done
    
    return $VDE_ERR_EXISTS  # No ports available
}
```

---

## 11. SSH Config Merge Algorithm

```zsh
merge_ssh_config_entry() {
    local entry="$1"
    local config_file="${HOME}/.ssh/vde/config"
    local backup_dir="${VDE_ROOT}/backup/ssh"
    
    # Create backup
    mkdir -p "$backup_dir"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    cp "$config_file" "${backup_dir}/config.backup.${timestamp}" 2>/dev/null
    
    # Check for duplicate
    local host_entry=$(echo "$entry" | grep "^Host ")
    if grep -q "^Host ${host_entry#Host }" "$config_file" 2>/dev/null; then
        return $VDE_ERR_EXISTS
    fi
    
    # Atomic update using temp file
    local temp_file
    temp_file=$(mktemp)
    
    cat "$config_file" > "$temp_file"
    echo "" >> "$temp_file"
    echo "$entry" >> "$temp_file"
    
    mv -f "$temp_file" "$config_file"
    chmod 600 "$config_file"
    
    return $VDE_SUCCESS
}
```

---

## 12. Implementation Priority

### Priority 1: Core Functionality

1. **VM Type Loading** - Load from JSON/conf, cache support
2. **Intent Detection** - 9 intents with pattern matching
3. **Entity Extraction** - VM names, filters, flags
4. **Alias Resolution** - O(1) lookup using associative array
5. **Port Allocation** - Sequential with collision detection
6. **Template Rendering** - Variable substitution

### Priority 2: VM Lifecycle

1. **VM Creation** - docker-compose.yml generation
2. **VM Start/Stop** - Docker operations
3. **VM Status** - Container state detection
4. **SSH Config** - Entry generation and merging

### Priority 3: Reliability

1. **Error Handling** - Consistent error messages
2. **Cache System** - Performance optimization
3. **Shell Compatibility** - zsh native support

### Priority 4: Enhancement

1. **Team Collaboration** - Shared configurations
2. **Debugging Tools** - Logs, diagnostics
3. **Audit Trail** - Operation logging

---

## 13. Test Scenario Mapping

Each requirement maps to BDD scenarios in:

| Feature | Test File |
|---------|-----------|
| Parser | `tests/features/docker-free/natural-language-parser.feature` |
| Cache | `tests/features/docker-free/cache-system.feature` |
| Shell | `tests/features/docker-free/shell-compatibility.feature` |
| VM Lifecycle | `tests/features/docker-required/vm-lifecycle.feature` |
| SSH Config | `tests/features/docker-required/ssh-configuration.feature` |
| Port Mgmt | `tests/features/docker-required/port-management.feature` |
| Errors | `tests/features/docker-required/error-handling-and-recovery.feature` |
| Docker | `tests/features/docker-required/docker-operations.feature` |

---

*End of Technical Specification*
