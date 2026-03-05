# VDE Technical Specification

**Document Type:** Technical Implementation Specification
**Project:** Virtual Development Environment (VDE)
**Version:** 1.3.0
**Status:** AUTHORITATIVE SPECIFICATION
**Last Updated:** 2026-03-04T12:00:00Z

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
> **Revision Control**: The version number MUST be incremented for EVERY single change, whether to test requirements or specification blocks. The Last Updated timestamp MUST also be updated to full ISO 8601 format (e.g., 2026-02-15T05:33:16Z). Minor changes increment the patch version (1.0.1), significant changes increment minor (1.1.0), breaking changes increment major (2.0.0).

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
cpp:2201
asm:2202
c:2203
redis:2400
postgres:2401
mongodb:2402
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
readonly VDE_ERR_DOCKER=8
readonly VDE_ERR_LOCK=9
readonly VDE_ERR_INVALID_DATA=10
readonly VDE_ERR_CACHE_INVALID=11

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

# Docker / Container Naming
readonly VDE_CONTAINER_PREFIX="vde-"
readonly VDE_DOCKER_NETWORK="${VDE_DOCKER_NETWORK:-vde-net}"

# SSH Isolation — all VDE SSH assets live under ~/.ssh/vde/
readonly VDE_SSH_DIR="${VDE_HOME_DIR}/.ssh/vde"
readonly VDE_SSH_CONFIG="${VDE_SSH_DIR}/config"
readonly VDE_SSH_KNOWN_HOSTS="${VDE_SSH_DIR}/known_hosts"
readonly VDE_SSH_IDENTITY="${VDE_SSH_DIR}/id_ed25519"
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

# validate_or_create_ssh_key
# Generate new ed25519 SSH key if none exists, or validate existing key
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

# merge_ssh_config_entry HOST PORT DISPLAY_NAME [IDENTITY_FILE]
# Merge SSH config entry atomically (idempotent — replaces existing entry)
# Args: HOST (string), PORT (number), DISPLAY_NAME (string), IDENTITY_FILE (path, default: VDE_SSH_IDENTITY)
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

### 3.9 vde-naming

**File:** `scripts/lib/vde-naming`

Enforces the canonical `vde-{name}` naming convention for all Docker containers,
images, and SSH host aliases. Filesystem directories (e.g., `configs/docker/python/`)
retain the raw name for clarity; the `vde-` prefix is applied only at the
container/SSH layer.

```zsh
# vde_validate_name NAME
# Validate a VM name (accepts names with or without vde- prefix)
# Args: NAME (string)
# Output: error message to stdout on failure
# Returns: VDE_SUCCESS or 1

# vde_normalize_name NAME
# Strip vde- prefix and lowercase — returns raw canonical name for filesystem use
# Args: NAME (string, e.g., "vde-python" or "Python")
# Output: raw name (e.g., "python") to stdout
# Returns: VDE_SUCCESS

# vde_get_container_name VM_NAME
# Get Docker container name (ensures vde- prefix)
# Args: VM_NAME (string, raw or prefixed)
# Output: "vde-{name}" to stdout
# Returns: VDE_SUCCESS

# vde_get_ssh_host VM_NAME
# Get SSH Host alias (identical to container name)
# Args: VM_NAME (string)
# Output: "vde-{name}" to stdout
# Returns: VDE_SUCCESS

# vde_get_hostname VM_NAME
# Get internal container hostname (identical to container name)
# Args: VM_NAME (string)
# Output: "vde-{name}" to stdout
# Returns: VDE_SUCCESS

# vde_detect_vm_type_from_name NAME
# Detect VM type from name using VM_TYPE map or built-in fallback patterns
# Args: NAME (string)
# Output: "lang" | "service" to stdout
# Returns: VDE_SUCCESS
```

### 3.10 vde-security

**File:** `scripts/lib/vde-security`

Centralizes security policy enforcement. Automatically called during startup
by `vde-init`, `ensure_vde_ssh_environment`, and `build-and-start`.

```zsh
# vde_security_enforce_permissions
# Enforce strict permissions on all sensitive VDE directories and files:
#   0700: .cache/, .docker-state/, .locks/, data/, logs/, VDE_SSH_DIR, env-files/
#   0600: VDE_SSH_IDENTITY, VDE_SSH_CONFIG, VDE_SSH_KNOWN_HOSTS, *.env files
#   0755: scripts/ and all script files
# Returns: VDE_SUCCESS

# vde_security_ensure_network [NETWORK_NAME]
# Ensure the isolated VDE Docker bridge network exists
# Args: NETWORK_NAME (default: VDE_DOCKER_NETWORK = "vde-net")
# Creates network with label "vde.managed=true" if absent
# Returns: VDE_SUCCESS

# vde_security_validate_naming
# Audit running vde-* containers for naming convention compliance
# Returns: VDE_SUCCESS

# vde_security_enforce_network_isolation [NETWORK_NAME]
# Ensure all running vde-* containers are connected to the VDE network
# Automatically re-attaches any container that has drifted off the network
# Args: NETWORK_NAME (default: VDE_DOCKER_NETWORK)
# Returns: VDE_SUCCESS

# vde_security_init
# Initialize full security environment in one call:
#   1. vde_security_ensure_network
#   2. vde_security_enforce_permissions
#   3. vde_security_enforce_network_isolation
# Called by: vde-init, ensure_vde_ssh_environment, build-and-start
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
#   init                      Initialize VDE project (first-time setup)
#   create <vm>              Create a new VM
#   start <vm> [...]         Start one or more VMs
#   stop <vm> [...]         Stop one or more VMs
#   restart <vm> [...]      Restart one or more VMs
#   remove <vm>             Remove a VM instance
#   list [filter]           List VMs (lang|svc|all)
#   status                  Show VM status
#   health                  Run health check
#   networks                Manage Docker networks
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
| vde-init | `scripts/vde-init` | `./vde-init` (first-time setup) |
| list-vms | `scripts/list-vms` | `./list-vms [--lang\|--svc] [search]` |
| create-virtual-for | `scripts/create-virtual-for` | `./create-virtual-for <name>` |
| start-virtual | `scripts/start-virtual` | `./start-virtual <name>... [--rebuild] [--no-cache]` |
| shutdown-virtual | `scripts/shutdown-virtual` | `./shutdown-virtual <name>...` |
| build-and-start | `scripts/build-and-start` | `./build-and-start [--rebuild] [--no-cache]` |
| vde-networks | `scripts/vde-networks` | `./vde-networks [--create] [--quiet]` |
| add-vm-type | `scripts/add-vm-type` | `./add-vm-type <name> "<install>" [aliases]` |

---

## 5. Template Formats

### 5.1 Language VM Template

**File:** `scripts/templates/compose-language.yml`

Container names MUST use the `vde-` prefix. The `{{NAME}}` placeholder receives
the raw name (e.g., `python`); the template prepends `vde-` for the container
and service keys.

```yaml
# Template for language VMs
# Variables: {{NAME}}, {{SSH_PORT}}, {{INSTALL_CMD}}
name: vde-{{NAME}}
services:
  vde-{{NAME}}:
    build:
      context: ../../..
      dockerfile: configs/docker/vde-base.Dockerfile
      args:
        USERNAME: devuser
        UID: 1000
        GID: 1000
        PUBLIC_KEYS_DIR: /public-ssh-keys
    image: vde-{{NAME}}:latest
    container_name: vde-{{NAME}}
    hostname: vde-{{NAME}}
    restart: unless-stopped
    command: sh -c "{{INSTALL_CMD}} && /usr/sbin/sshd -D"

    ports:
      - "{{SSH_PORT}}:22"

    volumes:
      - ../../../projects/{{NAME}}:/home/devuser/workspace
      - ../../../logs/{{NAME}}:/logs
      - ../../../public-ssh-keys:/public-ssh-keys:ro
      # SSH agent forwarding for VM->VM, VM->Host, VM->External communication
      - ${SSH_AUTH_SOCK:-/tmp/ssh-agent.sock}:/ssh-agent/sock:ro

    environment:
      - SSH_AUTH_SOCK=/ssh-agent/sock

    env_file:
      - ../../../env-files/vde-{{NAME}}.env

    networks:
      - vde-net

networks:
  vde-net:
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

SSH Host aliases MUST use the `vde-` prefix to match the container name.
The `{{VM_NAME}}` placeholder receives the raw name (e.g., `python`);
the template prepends `vde-` for the Host alias.

```
Host vde-{{VM_NAME}}
    HostName localhost
    Port {{SSH_PORT}}
    User devuser
    ForwardAgent yes
    StrictHostKeyChecking no
    UserKnownHostsFile ~/.ssh/vde/known_hosts
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
│   │   ├── vde-constants            # Constants (return codes, ports, paths, SSH dirs)
│   │   ├── vde-shell-compat         # Shell compatibility
│   │   ├── vde-errors               # Error handling
│   │   ├── vde-log                  # Logging
│   │   ├── vde-naming               # Naming conventions (vde- prefix enforcement)
│   │   ├── vde-security             # Security policy (permissions, network, SSH isolation)
│   │   ├── vde-path-utils           # Path utilities
│   │   ├── vde-core                 # Core functions
│   │   ├── vm-common                # Common functions
│   │   ├── vde-commands             # Command wrappers
│   │   ├── vde-parser               # NLP parser
│   │   ├── vde-ssh                  # SSH management
│   │   ├── vde-docker               # Docker operations
│   │   ├── vde-templates            # Template rendering
│   │   ├── vde-init                 # Project initialization
│   │   ├── vde-health               # Health checks
│   │   ├── vde-networks             # Network management
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
| Parser | `tests/features/core-infrastructure/parser.feature` |
| Cache | `tests/features/core-infrastructure/cache-system.feature` |
| Shell | `tests/features/core-infrastructure/shell-compatibility.feature` |
| VM Lifecycle (critical path) | `tests/features/core-infrastructure/critical-path.feature` |
| Infrastructure invariants | `tests/features/core-infrastructure/critical-infrastructure.feature` |
| SSH Config | `tests/features/core-infrastructure/ssh-configuration.feature` |
| SSH Commands | `tests/features/core-infrastructure/vde-ssh-commands.feature` |
| Error Handling | `tests/features/core-infrastructure/error-path.feature` |
| Docker Operations | `tests/features/core-infrastructure/docker-operations.feature` (@requires-docker-host) |
| Installation | `tests/features/core-infrastructure/installation-setup.feature` |

All features live under `tests/features/core-infrastructure/`. Features tagged `@requires-docker-host` or `@docker` require a live Docker daemon and are excluded from the default `python3 -m behave` run (see `behave.ini`). Run with `--tags @docker` to include them.

---

## 14. Security Architecture

### 14.1 Permission Policy

VDE enforces strict filesystem permissions at startup via `vde_security_enforce_permissions()`:

| Path | Permission | Rationale |
|------|-----------|-----------|
| `VDE_ROOT_DIR/` | `0755` | Readable by owner and group |
| `.cache/` | `0700` | Internal state — owner only |
| `.docker-state/` | `0700` | Internal state — owner only |
| `.locks/` | `0700` | Lock files — owner only |
| `data/` and subdirs | `0700` | Service data — owner only |
| `logs/` and subdirs | `0700` | Log files — owner only |
| `env-files/` | `0700` | May contain credentials |
| `env-files/*.env` | `0600` | Credential files — owner read/write only |
| `VDE_SSH_DIR` (`~/.ssh/vde/`) | `0700` | SSH directory — owner only |
| `VDE_SSH_IDENTITY` | `0600` | Private key — owner read/write only |
| `VDE_SSH_CONFIG` | `0600` | SSH config — owner read/write only |
| `VDE_SSH_KNOWN_HOSTS` | `0600` | Known hosts — owner read/write only |
| `scripts/` and script files | `0755` | Must be executable |

### 14.2 Network Isolation

All VDE containers run on a dedicated Docker bridge network named `vde-net`:

```zsh
# Network creation (vde_security_ensure_network)
docker network create \
    --driver bridge \
    --label "vde.managed=true" \
    vde-net
```

- Network is created automatically if absent
- All containers that drift off `vde-net` are automatically re-attached by `vde_security_enforce_network_isolation()`
- The network is labeled `vde.managed=true` for identification and auditing

### 14.3 SSH Isolation

All VDE SSH assets are isolated in `~/.ssh/vde/` (separate from the user's personal `~/.ssh/`):

| Asset | Path | Purpose |
|-------|------|---------|
| Private key | `~/.ssh/vde/id_ed25519` | VDE container authentication |
| Public key | `~/.ssh/vde/id_ed25519.pub` | Injected into containers |
| SSH config | `~/.ssh/vde/config` | VDE-only SSH host entries |
| Known hosts | `~/.ssh/vde/known_hosts` | VDE container host keys only |

This isolation ensures:
- VDE SSH operations never interfere with the user's personal SSH configuration
- VDE container host keys are tracked separately
- Revoking VDE access is a single directory deletion

### 14.4 Naming Convention Enforcement

The `vde-` prefix is **mandatory** for all Docker containers and SSH host aliases:

| Layer | Convention | Example |
|-------|-----------|---------|
| Docker container name | `vde-{name}` | `vde-python`, `vde-postgres` |
| Docker image name | `vde-{name}:latest` | `vde-python:latest` |
| SSH Host alias | `vde-{name}` | `vde-python`, `vde-postgres` |
| Filesystem config dir | `{name}` (raw) | `configs/docker/python/` |
| Workspace dir | `{name}` (raw) | `projects/python/` |

The `vde_normalize_name()` function strips the prefix for filesystem operations;
`vde_get_container_name()` adds it for Docker/SSH operations.

### 14.5 Startup Integration

Security initialization is automatically triggered at three entry points:

| Entry Point | Function Called | Trigger |
|-------------|----------------|---------|
| `scripts/vde-init` | `vde_security_init` | First-time setup |
| `scripts/lib/vde-ssh` `ensure_vde_ssh_environment` | `vde_security_init` | SSH environment setup |
| `scripts/build-and-start` | `vde_security_ensure_network` + `vde_security_enforce_permissions` | Build/start all VMs |
| `scripts/vde-networks` | `vde_security_ensure_network` | Network management |

---

*End of Technical Specification*
