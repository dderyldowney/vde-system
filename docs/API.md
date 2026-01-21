# VDE API Reference

**Version:** 1.0.0 (Stage 7 - Architectural Enhancements)
**Last Updated:** 2026-01-15

This document provides the complete API reference for the Virtual Development Environment (VDE) system.

---

## Table of Contents

1. [Overview](#overview)
2. [Scripts Reference](#scripts-reference)
3. [Library API](#library-api)
4. [Configuration Reference](#configuration-reference)
5. [VM Types Reference](#vm-types-reference)
6. [Exit Codes](#exit-codes)
7. [Port Allocation](#port-allocation)
8. [Environment Variables](#environment-variables)

---

## Overview

VDE (Virtual Development Environment) is a Docker-based container orchestration system providing isolated development environments for multiple programming languages and infrastructure services.

### Architecture

```
VDE Root Directory
├── scripts/
│   ├── lib/              # Library modules
│   │   ├── vde-constants
│   │   ├── vde-shell-compat
│   │   ├── vde-errors
│   │   ├── vde-log
│   │   ├── vde-core
│   │   ├── vm-common
│   │   ├── vde-commands
│   │   └── vde-parser
│   ├── data/             # Configuration data
│   │   └── vm-types.conf
│   └── templates/        # Docker Compose templates
├── configs/              # Generated VM configs
├── projects/             # Project source code
├── data/                 # Persistent data
├── logs/                 # Application logs
└── env-files/            # Environment variables
```

### Supported Environments

- **Shell:** zsh 5.0+, bash 4.0+ (bash 3.x with fallbacks)
- **Platform:** macOS, Linux
- **Requirements:** Docker Desktop or Docker daemon

---

## Scripts Reference

### `vde` - Unified Command Interface

The main entry point for all VDE operations.

**Usage:**
```bash
vde <command> [options] [args]
```

**Commands:**

| Command | Description | Script |
|---------|-------------|--------|
| `create <vm>` | Create a new VM | create-virtual-for |
| `start <vm>` | Start a VM | start-virtual |
| `stop <vm>` | Stop a VM | shutdown-virtual |
| `restart <vm>` | Restart a VM | start-virtual + shutdown-virtual |
| `list` | List all VMs | list-vms |
| `status` | Show VM status | list-vms |
| `health` | Run system health check | vde-health |
| `help` | Show help message | - |

**Options:**
- `-h, --help` - Show help message
- `-v, --verbose` - Enable verbose output
- `--version` - Show version information

**Examples:**
```bash
vde list                          # List all VMs
vde create python                 # Create Python VM
vde start python-dev              # Start Python VM
vde stop postgres                 # Stop PostgreSQL service
vde health                        # Run health check
```

**Exit Codes:**
- `0` - Success
- `1` - General error
- `2` - Invalid input
- `3` - Resource not found

---

### `create-virtual-for` - Create New VMs

Creates a new VM with predefined configuration from `vm-types.conf`.

**Usage:**
```bash
create-virtual-for [OPTIONS] <vm_name>
```

**Arguments:**
- `vm_name` - Name of the VM (must be predefined in vm-types.conf)

**Options:**
- `-h, --help` - Show help message
- `-q, --quiet` - Suppress progress indicators
- `-v, --verbose` - Show detailed output

**What the script does:**
1. Validates the VM name (follows naming convention)
2. Auto-allocates SSH port (2200-2299 for languages, 2400-2499 for services)
3. Creates docker-compose.yml from template
4. Creates required directories (projects/ or data/, logs/)
5. Creates environment file (env-files/)
6. Adds SSH config entry to ~/.ssh/config

**Examples:**
```bash
create-virtual-for python    # Create Python language VM
create-virtual-for postgres  # Create PostgreSQL service VM
create-virtual-for --quiet rust
```

**Created Files:**
- `configs/docker/<vm_name>/docker-compose.yml`
- `env-files/<vm_name>.env`
- `projects/<vm_name>/` (for language VMs) or `data/<vm_name>/` (for service VMs)
- `logs/<vm_name>/`

---

### `start-virtual` - Start VMs

Starts one or more VMs.

**Usage:**
```bash
start-virtual <vm_name1> [vm_name2] ... [--rebuild] [--no-cache]
```

**Arguments:**
- `vm_name` - Name of the VM to start
- `all` - Start all created VMs

**Options:**
- `--rebuild` - Rebuild the container before starting
- `--no-cache` - Build with no cache (implies rebuild)

**Examples:**
```bash
start-virtual python                    # Start single VM
start-virtual python ruby js            # Start multiple VMs
start-virtual all                       # Start all VMs
start-virtual python --rebuild          # Rebuild and start
start-virtual all --no-cache            # Full rebuild all VMs
```

**Exit Codes:**
- `0` - All VMs started successfully
- `1` - One or more VMs failed to start

---

### `shutdown-virtual` - Stop VMs

Stops running VMs.

**Usage:**
```bash
shutdown-virtual <vm_name1> [vm_name2] ... [all]
```

**Arguments:**
- `vm_name` - Name of the VM to stop
- `all` - Stop all VMs with docker-compose.yml files

**Examples:**
```bash
shutdown-virtual python                    # Stop single VM
shutdown-virtual python ruby js            # Stop multiple VMs
shutdown-virtual all                       # Stop all VMs
```

---

### `list-vms` - List VM Types

Lists all predefined VM types (languages and services).

**Usage:**
```bash
list-vms [OPTIONS] [filter]
```

**Options:**
- `--lang, --languages` - List only language VMs
- `--svc, --services` - List only service VMs
- `--name-only` - Show only VM names (hostnames)
- `-a, --all` - Show all VMs including created status
- `--help, -h` - Show help message

**Arguments:**
- `filter` - Optional text filter (searches name, aliases, display)

**Examples:**
```bash
list-vms                    # List all VMs
list-vms --lang             # List only language VMs
list-vms --svc              # List only service VMs
list-vms --name-only        # Show only names/hostnames
list-vms python             # Search for 'python'
list-vms --lang script      # Search for script in languages
list-vms -a                 # Show status of all VMs
```

---

### `add-vm-type` - Add New VM Types

Adds a new language or service to the predefined VM types list.

**Usage:**
```bash
add-vm-type [OPTIONS] <name> "<install_cmd>" [aliases]
```

**Arguments:**
- `name` - Name of the VM (e.g., zig, dart, couchdb)
- `install_cmd` - Installation command (must be quoted)
- `aliases` - Optional comma-separated aliases (e.g., "js,node,nodejs")

**Options:**
- `--type TYPE` - Type of VM: lang or service (default: auto-detect)
- `--svc-port PORT` - Service port (required for services, e.g., 5432)
- `--display NAME` - Display name (default: auto-generated from name)
- `--help, -h` - Show help message

**Examples:**
```bash
# Add a language (auto-detects type as 'lang')
add-vm-type zig "apt-get update -y && apt-get install -y zig"

# Add a language with aliases
add-vm-type dart "apt-get update -y && apt-get install -y dart" "dartlang,flutter"

# Add a service (requires --type and --svc-port)
add-vm-type --type service --svc-port 5672 rabbitmq \
    "apt-get update -y && apt-get install -y rabbitmq-server" "rabbit"

# Add with custom display name
add-vm-type --display "Zig Language" zig \
    "apt-get update -y && apt-get install -y zig"
```

---

## Library API

### vde-constants

Standardized constants for VDE operations.

**Return Codes:**

| Constant | Value | Description |
|----------|-------|-------------|
| `VDE_SUCCESS` | 0 | Operation completed successfully |
| `VDE_ERR_GENERAL` | 1 | Unspecified failure |
| `VDE_ERR_INVALID_INPUT` | 2 | Bad arguments or validation failure |
| `VDE_ERR_NOT_FOUND` | 3 | Resource doesn't exist |
| `VDE_ERR_EXISTS` | 4 | Resource already exists |
| `VDE_ERR_DOCKER` | 5 | Docker operation failed |
| `VDE_ERR_SSH` | 6 | SSH operation failed |
| `VDE_ERR_PORT` | 7 | Port allocation failed |
| `VDE_ERR_TEMPLATE` | 8 | Template processing failed |
| `VDE_ERR_LOCK` | 9 | Lock acquisition failed |

**Port Ranges:**

| Constant | Value | Description |
|----------|-------|-------------|
| `LANG_PORT_START` | 2200 | Starting port for language VMs |
| `LANG_PORT_END` | 2299 | Ending port for language VMs |
| `SVC_PORT_START` | 2400 | Starting port for service VMs |
| `SVC_PORT_END` | 2499 | Ending port for service VMs |
| `NEXT_PORT_FILE` | `.cache/next-port` | Port allocation registry |

**Timeouts:**

| Constant | Value | Description |
|----------|-------|-------------|
| `DOCKER_TIMEOUT` | 300 | Docker operation timeout (seconds) |
| `SSH_TIMEOUT` | 30 | SSH operation timeout (seconds) |
| `CONTAINER_START_TIMEOUT` | 120 | Container startup timeout (seconds) |

**Retry Configuration:**

| Constant | Value | Description |
|----------|-------|-------------|
| `MAX_RETRIES` | 3 | Maximum retry attempts |
| `BASE_DELAY` | 2 | Base exponential delay (seconds) |
| `MAX_DELAY` | 30 | Maximum delay between retries (seconds) |

**Lock Configuration:**

| Constant | Value | Description |
|----------|-------|-------------|
| `SSH_LOCK_FILE` | `.cache/ssh-config.lock` | SSH config lock file path |
| `PORT_LOCK_FILE` | `.cache/port-allocation.lock` | Port allocation lock file path |
| `STALE_LOCK_AGE` | 300 | Age before lock is considered stale (seconds) |

**Docker Configuration:**

| Constant | Value | Description |
|----------|-------|-------------|
| `VDE_DOCKER_NETWORK` | "vde-network" | Docker network name |
| `LANG_CONTAINER_SUFFIX` | "-dev" | Suffix for language container names |
| `SVC_CONTAINER_SUFFIX` | "" | Suffix for service container names |

**SSH Preferences:**

| Constant | Value | Description |
|----------|-------|-------------|
| `SSH_KEY_TYPES` | "id_ed25519 id_ecdsa id_rsa id_ecdsa_sk id_ed25519_sk" | Preferred SSH key types |

**Error Message Templates:**

```bash
VDE_MSG_VM_NOT_CREATED="VM '%s' is not created yet"
VDE_MSG_VM_ALREADY_RUNNING="VM '%s' is already running"
VDE_MSG_VM_NOT_RUNNING="VM '%s' is not running"
VDE_MSG_PORT_IN_USE="Port %d is already in use"
VDE_MSG_NO_PORTS_AVAILABLE="No available ports in range %d-%d"
```

---

### vde-shell-compat

Portable shell compatibility layer for cross-shell operations.

**Shell Detection Functions:**

| Function | Returns | Description |
|----------|---------|-------------|
| `_detect_shell` | "zsh", "bash", "unknown" | Detect current shell type |
| `_shell_version` | Version string | Get shell version |
| `_is_zsh` | 0 if zsh, 1 otherwise | Check if running in zsh |
| `_is_bash` | 0 if bash, 1 otherwise | Check if running in bash |
| `_bash_version_major` | Major version number | Get bash major version |
| `_shell_supports_native_assoc` | 0 if supported, 1 otherwise | Check for native associative arrays |

**Script Path Functions:**

| Function | Returns | Description |
|----------|---------|-------------|
| `_get_script_path` | Absolute path | Get path of current script |
| `_get_script_dir` | Absolute path | Get directory of current script |

**Associative Array Functions:**

| Function | Description |
|----------|-------------|
| `_assoc_init <array_name>` | Initialize an associative array |
| `_assoc_set <array> <key> <value>` | Set a value in an associative array |
| `_assoc_get <array> <key>` | Get a value from an associative array |
| `_assoc_keys <array>` | Get all keys from an associative array |
| `_assoc_has_key <array> <key>` | Check if a key exists |
| `_assoc_unset <array> <key>` | Remove a key from an associative array |
| `_assoc_clear <array>` | Clear all entries from an associative array |
| `_assoc_cleanup` | Clean up file-based storage |

**Array Operations:**

| Function | Description |
|----------|-------------|
| `_array_length <array>` | Get the length of an indexed array |
| `_array_append <array> <value>` | Append a value to an array |
| `_array_contains <array> <value>` | Check if array contains a value |

**String Operations:**

| Function | Description |
|----------|-------------|
| `_string_split <string> <delimiter> <array>` | Split string by delimiter into array |
| `_string_trim <string>` | Trim leading and trailing whitespace |

**Date/Time Operations:**

| Function | Returns | Description |
|----------|---------|-------------|
| `_date_iso8601` | ISO 8601 timestamp | Get current timestamp |
| `_date_epoch` | Unix timestamp | Get current epoch time |

**Compatibility Checking:**

| Function | Description |
|----------|-------------|
| `_check_shell_compatibility` | Check and warn about shell compatibility |
| `_require_shell <shell_name>` | Require a specific shell or exit |

---

### vde-errors

Error messages with remediation steps.

**Core Error Functions:**

```bash
# Show full error message with what, why, and how
vde_error_show <what> <why> <how> [doc_link]

# Show simple error message
vde_error_simple <message>

# Show error with exit code
vde_error_with_code <message> <exit_code>

# Show success message
vde_success <message>
```

**Common Error Scenarios:**

| Function | Description |
|----------|-------------|
| `vde_error_docker_not_running` | Docker daemon not running |
| `vde_error_port_in_use <port>` | Port already in use |
| `vde_error_ssh_key_missing` | No SSH key found |
| `vde_error_container_exists <name>` | VM already exists |
| `vde_error_permission_denied <path>` | Permission denied |
| `vde_error_vm_not_found <name>` | VM not found |
| `vde_error_vm_not_running <name>` | VM not running |
| `vde_error_docker_build_failed <vm>` | Docker build failed |
| `vde_error_network_not_found <network>` | Docker network not found |
| `vde_error_template_not_found <template>` | Template not found |
| `vde_error_invalid_vm_name <name>` | Invalid VM name |
| `vde_error_alias_not_found <alias>` | Unknown VM type or alias |

**Configuration:**

| Variable | Default | Description |
|----------|---------|-------------|
| `VDE_ERRORS_VERBOSE` | 0 | Enable verbose mode |
| `VDE_ERRORS_DOC_URL` | GitHub docs URL | Documentation base URL |
| `VDE_ERRORS_SHOW_SOLUTION` | 1 | Show remediation steps |

---

### vde-log

Structured logging with rotation capabilities.

**Log Levels:**

| Level | Value | Description |
|-------|-------|-------------|
| DEBUG | 0 | Debug messages |
| INFO | 1 | Informational messages |
| WARN | 2 | Warning messages |
| ERROR | 3 | Error messages |

**Initialization:**

```bash
vde_log_init                    # Initialize logging system
```

**Level Control:**

```bash
vde_log_set_level <level>       # Set minimum log level (DEBUG|INFO|WARN|ERROR)
vde_log_get_level               # Get current log level name
```

**Format Control:**

```bash
vde_log_set_format <format>     # Set output format (text|json|syslog)
```

**Output Control:**

```bash
vde_log_to_file [filepath]      # Configure logging to file
vde_log_to_stdout               # Configure logging to stdout
vde_log_to_stderr               # Configure logging to stderr
```

**Logging Functions:**

```bash
vde_log_debug <message> [component] [context...]
vde_log_info <message> [component] [context...]
vde_log_warn <message> [component] [context...]
vde_log_error <message> [component] [context...]
```

**Log Rotation:**

```bash
vde_log_check_rotation          # Check if rotation is needed
vde_log_rotate                  # Perform log rotation
vde_log_cleanup                 # Clean up old log files
```

**Query Functions:**

```bash
vde_log_recent [count]          # Get recent log entries (default: 50)
vde_log_grep <pattern>          # Search logs
vde_log_errors [count]          # Get error logs (default: 100)
```

**Configuration Variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `VDE_LOG_LEVEL` | INFO | Minimum log level |
| `VDE_LOG_FORMAT` | text | Output format |
| `VDE_LOG_OUTPUT` | stdout | Output destination |
| `VDE_LOG_FILE` | logs/vde.log | Log file path |
| `VDE_LOG_MAX_SIZE` | 10485760 | Max log size (10MB) |
| `VDE_LOG_MAX_DAYS` | 7 | Log retention days |
| `VDE_LOG_RETENTION_POLICY` | size | Retention policy (size\|time\|both) |

---

### vde-core

Core VM type loading and essential functions.

**Directory Constants:**

| Variable | Value | Description |
|----------|-------|-------------|
| `VDE_CORE_CONFIGS_DIR` | $VDE_ROOT_DIR/configs/docker | VM configurations |
| `VDE_CORE_SCRIPTS_DIR` | $VDE_ROOT_DIR/scripts | Scripts directory |
| `VDE_CORE_DATA_DIR` | $VDE_CORE_SCRIPTS_DIR/data | Data directory |
| `VDE_CORE_CACHE_DIR` | $VDE_ROOT_DIR/.cache | Cache directory |
| `VDE_CORE_VM_TYPES_CONF` | $VDE_CORE_DATA_DIR/vm-types.conf | VM types config |
| `VDE_CORE_VM_TYPES_CACHE` | $VDE_CORE_CACHE_DIR/vm-types.cache | VM types cache |

**Logging Functions:**

```bash
log_info <message>     # Output informational message
log_error <message>    # Output error message to stderr
log_success <message>  # Output success message
log_warning <message>  # Output warning message
```

**VM Type Loading:**

```bash
vde_core_load_types    # Load minimal VM type data
```

**Core VM Query Functions:**

```bash
vde_core_get_all_vms       # List all known VM names
vde_core_get_vm_type <vm>  # Get the type of a VM (lang or service)
vde_core_is_known_vm <vm>  # Check if a VM name is known
```

**Performance Timing (Debug):**

```bash
vde_time_start <label>     # Start a timing measurement
vde_time_end <label>       # End a timing measurement and print result
```

---

### vm-common

Core VM management functionality.

**VM Type Caching:**

```bash
load_vm_types                      # Load VM types from config
load_vm_types_if_needed            # Load if cache is stale
invalidate_vm_cache                # Force reload of VM types
get_all_vms                        # Get all VM names
get_lang_vms                       # Get language VM names
get_service_vms                    # Get service VM names
get_vm_info <field> <vm>           # Get VM info field (type, name, aliases, display, install, svc_port)
is_known_vm <vm>                   # Check if VM is known
```

**Port Management:**

```bash
find_next_available_port <type>    # Find next available SSH port
allocate_port <vm> <port>          # Register port allocation
get_vm_port <vm>                   # Get allocated port for VM
is_port_available <port>           # Check if port is available
read_port_registry                 # Read port allocation registry
write_port_registry <data>         # Write port allocation registry
```

**Docker Compose Operations:**

```bash
docker_compose_with_retry <args>   # Run docker-compose with retry logic
get_compose_file <vm>              # Get path to docker-compose.yml
vm_exists <vm>                     # Check if VM has been created
is_vm_running <vm>                 # Check if VM container is running
wait_for_container <vm> [timeout]  # Wait for container to be ready
```

**SSH Key Management:**

```bash
detect_ssh_keys                    # Detect available SSH keys
get_first_ssh_key                  # Get path to first available SSH key
ensure_ssh_environment             # Ensure SSH agent and keys are set up
copy_public_keys                   # Copy public keys to VDE directory
```

**Template Rendering:**

```bash
render_template <template> [key=value...]  # Render template with variables
```

**SSH Config Management:**

```bash
merge_ssh_config_entry <host> <port> <display>  # Add SSH config entry atomically
get_ssh_host <vm>                 # Get SSH hostname for VM
```

**Validation Functions:**

```bash
validate_vm_name <vm>             # Validate VM name format
validate_vm_doesnt_exist <vm>     # Ensure VM doesn't exist
ensure_vm_directories <vm> <type> # Create VM directories
resolve_vm_name <name>            # Resolve alias to canonical name
vde_detect_vm_type_from_name <name>  # Detect VM type from name
```

**Directory Creation:**

```bash
ensure_directory <path>           # Create directory if it doesn't exist
```

---

### vde-commands

High-level command wrappers for AI/CLI operations.

**Query Functions:**

```bash
vde_list_vms [--all|--lang|--svc]     # List available VMs
vde_vm_exists <vm>                     # Check if VM exists
vde_get_vm_info <vm>                   # Get detailed VM information
vde_get_running_vms                    # Get list of running VMs
vde_get_vm_status <vm>                 # Get status of a VM
vde_get_ssh_info <vm>                  # Get SSH connection info (host|port)
vde_resolve_alias <alias>              # Resolve alias to VM name
vde_validate_vm_type <vm>              # Validate VM type
```

**Action Functions:**

```bash
vde_create_vm <vm>                     # Create a new VM
vde_start_vm <vm> [rebuild] [nocache]  # Start a VM
vde_stop_vm <vm>                       # Stop a VM
vde_restart_vm <vm> [rebuild] [nocache] # Restart a VM
vde_start_all                          # Start all VMs
vde_stop_all                           # Stop all VMs
vde_add_vm_type <name> <install> [aliases]  # Add new VM type
```

**Batch Operations:**

```bash
vde_create_multiple_vms <vm1> <vm2> ...  # Create multiple VMs
vde_start_multiple_vms <vm1> <vm2> ...   # Start multiple VMs
vde_stop_multiple_vms <vm1> <vm2> ...    # Stop multiple VMs
```

**Dry Run Mode:**

```bash
vde_set_dry_run <true|false>            # Enable/disable dry run mode
vde_exec <command> [args...]            # Execute command (respects dry run)
```

---

### vde-parser

Natural language parsing for conversational commands.

**Intent Detection:**

```bash
detect_intent <input>    # Detect primary intent from user input
```

**Supported Intents:**

| Intent Constant | Description |
|-----------------|-------------|
| `INTENT_LIST_VMS` | List available VMs |
| `INTENT_CREATE_VM` | Create new VMs |
| `INTENT_START_VM` | Start VMs |
| `INTENT_STOP_VM` | Stop VMs |
| `INTENT_RESTART_VM` | Restart VMs |
| `INTENT_STATUS` | Show VM status |
| `INTENT_CONNECT` | Get connection info |
| `INTENT_ADD_VM_TYPE` | Add new VM type |
| `INTENT_HELP` | Show help |

**Entity Extraction:**

```bash
extract_vm_names <input>     # Extract VM names from input
extract_filter <input>       # Extract filter type (all|lang|svc)
extract_flags <input>        # Extract operation flags (rebuild, nocache)
```

**Command Generation:**

```bash
generate_plan <input>        # Generate execution plan from input
execute_plan                 # Execute a generated plan (reads from stdin)
```

**Alias Mapping:**

```bash
_lookup_vm_by_alias <alias>  # O(1) lookup of VM name by alias
invalidate_alias_map         # Force rebuild of alias map
```

---

## Configuration Reference

### vm-types.conf Format

The VM types configuration file defines all available VM types in a pipe-delimited format.

**Location:** `scripts/data/vm-types.conf`

**Format:**
```
type|name|aliases|display_name|install_command|service_port
```

**Fields:**

| Field | Description | Example |
|-------|-------------|---------|
| type | VM type (lang or service) | lang |
| name | Canonical VM name | python |
| aliases | Comma-separated aliases | python3,py |
| display_name | Human-readable name | Python |
| install_command | Shell installation command | apt-get install -y python3 |
| service_port | Service port(s) - empty for languages | 5432 |

**Example Entry:**
```
lang|python|python3|Python|apt-get update -y && apt-get install -y python3 python3-pip|
service|postgres|postgresql|PostgreSQL|apt-get update -y && apt-get install -y postgresql-client|5432
```

**Comments:** Lines starting with `#` are ignored.

---

### Environment Files

Each VM has its own environment file in `env-files/<vm_name>.env`.

**Variables:**

```bash
SSH_PORT=<allocated_ssh_port>           # SSH port for this VM
<VM_NAME>_PORT=<service_port>            # Service port (for service VMs)
```

**Example (postgres.env):**
```bash
SSH_PORT=2400
POSTGRES_PORT=5432
```

---

### Template System

Templates are stored in `scripts/templates/` and use shell variable substitution.

**Templates:**

| Template | Description |
|----------|-------------|
| `compose-language.yml` | Docker Compose template for language VMs |
| `compose-service.yml` | Docker Compose template for service VMs |

**Template Variables:**

| Variable | Description |
|----------|-------------|
| `NAME` | VM name |
| `SSH_PORT` | Allocated SSH port |
| `INSTALL_CMD` | Installation command from vm-types.conf |
| `SERVICE_PORT` | Service port from vm-types.conf |

**Rendering:**
```bash
render_template <template_file> NAME "python" SSH_PORT 2200 INSTALL_CMD "..." SERVICE_PORT ""
```

---

## VM Types Reference

### Language VMs (19 total)

| Name | Aliases | Display Name | Default Port |
|------|---------|--------------|--------------|
| c | c | C | 2200 |
| cpp | c++, gcc | C++ | 2201 |
| asm | assembler, nasm | Assembler | 2202 |
| python | python3, py | Python | 2203 |
| rust | rust-dev | Rust | 2204 |
| js | node, nodejs | JavaScript | 2205 |
| csharp | dotnet | C# | 2206 |
| ruby | rb, ruby | Ruby | 2207 |
| go | golang | Go | 2208 |
| java | jdk | Java | 2209 |
| kotlin | kotlin | Kotlin | 2210 |
| swift | swift | Swift | 2211 |
| php | php | PHP | 2212 |
| scala | scala | Scala | 2213 |
| r | rlang, r | R | 2214 |
| lua | lua | Lua | 2215 |
| flutter | dart, flutter | Flutter | 2216 |
| elixir | elixir | Elixir | 2217 |
| haskell | ghc, haskell | Haskell | 2218 |
| zig | | Zig Language | 2219 |

**Container Naming:** `<name>-dev` (e.g., `python-dev`)

**Port Range:** 2200-2299

### Service VMs (7 total)

| Name | Aliases | Display Name | Service Port | Default Port |
|------|---------|--------------|--------------|--------------|
| postgres | postgresql | PostgreSQL | 5432 | 2400 |
| redis | redis | Redis | 6379 | 2401 |
| mongodb | mongo | MongoDB | 27017 | 2402 |
| nginx | nginx | Nginx | 80,443 | 2403 |
| couchdb | couchdb | CouchDB | 5984 | 2404 |
| mysql | mysql | MySQL | 3306 | 2405 |
| rabbitmq | rabbitmq | RabbitMQ | 5672,15672 | 2406 |

**Container Naming:** `<name>` (no suffix)

**Port Range:** 2400-2499

---

## Exit Codes

VDE uses standardized exit codes across all scripts and libraries.

| Code | Constant | Description |
|------|----------|-------------|
| 0 | VDE_SUCCESS | Operation completed successfully |
| 1 | VDE_ERR_GENERAL | Unspecified failure |
| 2 | VDE_ERR_INVALID_INPUT | Bad arguments or validation failure |
| 3 | VDE_ERR_NOT_FOUND | Resource doesn't exist |
| 4 | VDE_ERR_EXISTS | Resource already exists |
| 5 | VDE_ERR_DOCKER | Docker operation failed |
| 6 | VDE_ERR_SSH | SSH operation failed |
| 7 | VDE_ERR_PORT | Port allocation failed |
| 8 | VDE_ERR_TEMPLATE | Template processing failed |
| 9 | VDE_ERR_LOCK | Lock acquisition failed |

---

## Port Allocation

### Port Ranges

| Type | Range | Usage |
|------|-------|-------|
| Language VMs | 2200-2299 | SSH access to development containers |
| Service VMs | 2400-2499 | SSH access to service containers |

### Port Allocation System

Ports are allocated atomically using a file-based registry to prevent collisions.

**Registry File:** `.cache/next-port`

**Allocation Process:**
1. Acquire lock on `.cache/port-allocation.lock`
2. Read current port from registry
3. Find next available port in range
4. Update registry with allocated port
5. Release lock

**Functions:**
```bash
find_next_available_port <type>    # Find and allocate next port
get_vm_port <vm>                   # Get port allocated to VM
is_port_available <port>           # Check if port is in use
```

### SSH Host Aliases

For language VMs, the SSH host alias is `<name>-dev`.
For service VMs, the SSH host alias is `<name>`.

Examples:
- `python-dev` → Port 2203
- `postgres` → Port 2400

---

## Environment Variables

### VDE Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `VDE_ROOT_DIR` | VDE root directory | Auto-detected |
| `VDE_LOG_LEVEL` | Logging level | INFO |
| `VDE_LOG_FORMAT` | Log format | text |
| `VDE_ERRORS_VERBOSE` | Enable verbose errors | 0 |
| `VDE_DEBUG_TIMING` | Enable performance timing | 0 |
| `VDE_SKIP_COMPAT_CHECK` | Skip shell compatibility check | 0 |

### Docker Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `VDE_DOCKER_NETWORK` | Docker network name | vde-network |
| `DOCKER_TIMEOUT` | Docker operation timeout | 300 |

### SSH Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `VDE_SSH_KEY_TYPES` | Preferred SSH key types | id_ed25519 id_ecdsa id_rsa |
| `SSH_TIMEOUT` | SSH operation timeout | 30 |

---

## Quick Reference

### Essential Commands

```bash
# List available VMs
vde list
./scripts/list-vms

# Create a new VM
vde create <name>
./scripts/create-virtual-for <name>

# Start VMs
vde start <name>
./scripts/start-virtual <name>

# Stop VMs
vde stop <name>
./scripts/shutdown-virtual <name>

# Stop everything
vde stop all
./scripts/shutdown-virtual all

# Rebuild a VM
./scripts/start-virtual <name> --rebuild

# Add custom VM type
./scripts/add-vm-type <name> "<install_cmd>"
```

### SSH Connections

```bash
# Language VMs
ssh c-dev           # C development
ssh cpp-dev         # C++ development
ssh asm-dev         # Assembler development
ssh python-dev      # Python development
ssh rust-dev        # Rust development
ssh js-dev          # JavaScript/Node.js
ssh csharp-dev      # C# development
ssh ruby-dev        # Ruby development
ssh go-dev          # Go development
ssh java-dev        # Java development
ssh kotlin-dev      # Kotlin development
ssh swift-dev       # Swift development
ssh php-dev         # PHP development
ssh scala-dev       # Scala development
ssh r-dev           # R development
ssh lua-dev         # Lua development
ssh flutter-dev     # Flutter development
ssh elixir-dev      # Elixir development
ssh haskell-dev     # Haskell development
ssh zig-dev         # Zig development

# Service VMs
ssh postgres        # PostgreSQL database
ssh redis           # Redis cache
ssh mongodb         # MongoDB
ssh nginx           # Nginx web server
ssh couchdb         # CouchDB
ssh mysql           # MySQL
ssh rabbitmq        # RabbitMQ
```

---

[← Back to README](../README.md)

*This API reference is generated from the VDE source code. For the latest updates, see the source files in `scripts/lib/`.*
