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
source "lib/vde-constants"      # 1. Base constants
source "lib/vde-shell-compat"   # 2. Shell compatibility
source "lib/vde-errors"         # 3. Error handling
source "lib/vde-log"            # 4. Logging
source "lib/vde-naming"         # 5. Naming conventions (vde- prefix)
source "lib/vde-security"       # 6. Security enforcement
source "lib/vde-core"           # 7. Core VDE functions
source "lib/vm-common"          # 8. Full VDE functionality
source "lib/vde-commands"       # 9. Command wrappers
source "lib/vde-parser"         # 10. Natural language parser
```

---

## Template System

VDE uses a template-based architecture for generating container configurations.

### Templates

| Template | Purpose | Location |
|----------|---------|----------|
| `compose-language.yml` | Language VM docker-compose.yml | `templates/` |
| `compose-service.yml` | Service VM docker-compose.yml | `templates/` |
| `ssh-entry.txt` | SSH config entries | `templates/` |

### Data-Driven Configuration

- **File:** `data/vm-types.conf`
- **Format:** Pipe-delimited (type, name, aliases, display_name, install_command, service_port)
- **Purpose:** Single source of truth for all VM types
- **Caching:** VM types are cached in `.cache/vm-types.cache` for performance

---

## Shared Library

**File:** `lib/vm-common`

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


---

## VDE Schema Update Mechanisms

Comprehensive schema update mechanisms for version detection, compatibility checking, backup, and validation workflows.

### Overview

The schema update system provides:
- **Version detection** from config and schema files
- **Compatibility checking** between config and schema versions
- **Change detection** to identify when schemas are updated
- **Automatic backup** before config updates
- **Validation and update** workflow
- **Cache regeneration** when needed

### Functions

#### Version Detection

#### vde_get_config_version

Get version from JSON config file.

**Usage:**
```zsh
version=$(vde_get_config_version "data/vm-types.json")
echo "Config version: $version"
## Output: Config version: 1.0
```

**Returns:**
- `VDE_SUCCESS` (0) - Version found and output
- `VDE_ERR_NOT_FOUND` (3) - File missing or no version field

#### vde_get_schema_version

Get version pattern from schema file.

**Usage:**
```zsh
schema_version=$(vde_get_schema_version "data/vm-types.schema.json")
echo "Schema version pattern: $schema_version"
## Output: Schema version pattern: ^[0-9]+\.[0-9]+$
```

**Returns:**
- `VDE_SUCCESS` (0) - Version pattern found
- `VDE_ERR_NOT_FOUND` (3) - File missing or no version property

#### Compatibility Checking

#### vde_check_schema_compatibility

Check if config version matches schema requirements.

**Usage:**
```zsh
if vde_check_schema_compatibility "vm-types.json" "vm-types.schema.json"; then
    echo "Compatible"
else
    echo "Version mismatch - migration needed"
fi
```

**Returns:**
- `VDE_SUCCESS` (0) - Versions compatible
- `VDE_ERR_INVALID_DATA` (10) - Version mismatch

**Example Output:**
```
[INFO] Config version 1.0 compatible with schema
```

#### Change Detection

#### vde_detect_schema_changes

Detect if schema has been updated (newer than config).

**Usage:**
```zsh
if vde_detect_schema_changes "vm-types.json"; then
    echo "No changes"
else
    echo "Schema updated - regenerate cache"
fi
```

**Returns:**
- `VDE_SUCCESS` (0) - No changes detected
- `VDE_ERR_CACHE_INVALID` (11) - Schema is newer (changes detected)
- `VDE_ERR_NOT_FOUND` (3) - Schema file missing

**Example Output:**
```
[INFO] Schema has been updated, config may need regeneration
```

#### Backup

#### vde_backup_config

Create timestamped backup of config file.

**Usage:**
```zsh
backup_file=$(vde_backup_config "vm-types.json")
echo "Backed up to: $backup_file"
## Output: Backed up to: .cache/config-backups/vm-types.json.20260208_123045.bak
```

**Returns:**
- `VDE_SUCCESS` (0) - Backup created successfully
- `VDE_ERR_NOT_FOUND` (3) - Config file not found
- `VDE_ERR_GENERAL` (1) - Backup failed

**Backup Location:** `.cache/config-backups/`

**Filename Format:** `{config_name}.{timestamp}.bak`

#### Validation and Update

#### vde_validate_and_update

Complete validation and update workflow.

**Usage:**
```zsh
if vde_validate_and_update "vm-types.json" "vm-types.schema.json" ".cache/vm-types.cache"; then
    echo "Valid and up to date"
else
    case $? in
        $VDE_ERR_CACHE_INVALID)
            echo "Cache needs regeneration"
            regenerate_vm_types_cache
            ;;
        $VDE_ERR_INVALID_DATA)
            echo "Validation failed"
            ;;
    esac
fi
```

**Returns:**
- `VDE_SUCCESS` (0) - Config valid and cache current
- `VDE_ERR_CACHE_INVALID` (11) - Cache needs regeneration
- `VDE_ERR_INVALID_DATA` (10) - Validation failed

**Checks Performed:**
1. Version compatibility
2. Schema validation
3. Cache freshness (vs config and schema)

### Usage Examples

#### Example 1: Check Version Compatibility

```zsh
source lib/vde-core

config="data/vm-types.json"
schema="data/vm-types.schema.json"

## Get versions
config_version=$(vde_get_config_version "$config")
schema_version=$(vde_get_schema_version "$schema")

echo "Config version: $config_version"
echo "Schema requires: $schema_version"

## Check compatibility
if vde_check_schema_compatibility "$config" "$schema"; then
    echo "✓ Compatible"
else
    echo "✗ Incompatible - migration needed"
fi
```

**Output:**
```
Config version: 1.0
Schema requires: ^[0-9]+\.[0-9]+$
[INFO] Config version 1.0 compatible with schema
✓ Compatible
```

#### Example 2: Detect and Handle Schema Changes

```zsh
source lib/vde-core
source lib/vm-common

config="data/vm-types.json"

if ! vde_detect_schema_changes "$config"; then
    echo "Schema has been updated"

    # Backup before regenerating
    backup=$(vde_backup_config "$config")
    echo "Backed up to: $backup"

    # Regenerate cache
    regenerate_vm_types_cache
    echo "Cache regenerated"
fi
```

#### Example 3: Complete Update Workflow

```zsh
source lib/vde-core
source lib/vm-common

config="data/vm-types.json"
schema="data/vm-types.schema.json"
cache=".cache/vm-types.cache"

echo "Running update workflow..."

## Step 1: Check compatibility
if ! vde_check_schema_compatibility "$config" "$schema"; then
    echo "ERROR: Version incompatible"
    exit 1
fi

## Step 2: Backup
backup=$(vde_backup_config "$config")
echo "Backed up to: $backup"

## Step 3: Validate and update
if vde_validate_and_update "$config" "$schema" "$cache"; then
    echo "✓ Config valid and cache current"
else
    if [ $? -eq $VDE_ERR_CACHE_INVALID ]; then
        echo "Regenerating cache..."
        regenerate_vm_types_cache
        echo "✓ Cache regenerated"
    else
        echo "ERROR: Validation failed"
        exit 1
    fi
fi

echo "Update workflow complete"
```

#### Example 4: Automated Update Check

```zsh
#!/usr/bin/env zsh
## check-schemas.zsh - Automated schema update check

source lib/vde-core

configs=(
    "data/vm-types.json"
    "data/vm-docker-config.json"
)

for config in "${configs[@]}"; do
    echo "Checking: $config"

    # Get schema
    schema=$(vde_get_schema_for_json "$config")

    # Check version
    version=$(vde_get_config_version "$config")
    echo "  Version: $version"

    # Check compatibility
    if vde_check_schema_compatibility "$config" "$schema"; then
        echo "  ✓ Compatible"
    else
        echo "  ✗ Incompatible - manual update required"
    fi

    # Check for changes
    if vde_detect_schema_changes "$config"; then
        echo "  ✓ No schema changes"
    else
        echo "  ⚠ Schema updated - regenerate cache"
    fi

    echo ""
done
```

### Testing

#### Unit Tests

**Location:** `tests/unit/vde-schema-updates.test.zsh`

**Coverage:**
- Version detection (5 tests)
- Schema compatibility (2 tests)
- Change detection (2 tests)
- Config backup (3 tests)
- Validate and update (2 tests)
- Integration workflows (4 tests)

**Run tests:**
```bash
tests/unit/vde-schema-updates.test.zsh
## Expected: 20 passed, 0 failed
```

#### Demo Script

**Location:** `bin/demo-schema-updates.zsh`

**Demonstrates:**
1. Version detection
2. Compatibility checking
3. Change detection
4. Backup creation
5. Schema validation
6. Validate and update workflow
7. Complete update workflow
8. Schema integrity check

**Run demo:**
```bash
./bin/demo-schema-updates.zsh
```

**Sample Output:**
```
╔════════════════════════════════════════╗
║  VDE Schema Update Mechanisms Demo    ║
╚════════════════════════════════════════╝

========================================
1. Version Detection
========================================

➤ Detecting VM types config version...
  → Config version: 1.0

➤ Detecting VM types schema version...
  → Schema version pattern: ^[0-9]+\.[0-9]+$

========================================
2. Schema Compatibility Check
========================================

➤ Checking VM types compatibility...
  ✓ VM types: Config and schema are compatible

========================================
Summary
========================================

  ✓ All schema update mechanisms demonstrated successfully!
```

### Integration with Validation

The update mechanisms integrate with the existing validation system:

**Validation Functions** (from vde-core):
- `vde_check_schema_integrity` - Validate schema structure
- `vde_validate_json_schema` - Validate config against schema
- `vde_get_schema_for_json` - Find schema for config

**Update Mechanisms** (new):
- `vde_get_config_version` - Get config version
- `vde_get_schema_version` - Get schema version
- `vde_check_schema_compatibility` - Check versions match
- `vde_detect_schema_changes` - Detect schema updates
- `vde_backup_config` - Backup before updates
- `vde_validate_and_update` - Complete workflow

**Together they provide:**
1. Schema structure validation
2. Config data validation
3. Version compatibility
4. Change detection
5. Safe updates with backup

### Error Handling

#### Version Mismatch

```zsh
if ! vde_check_schema_compatibility "$config" "$schema"; then
    echo "ERROR: Config version incompatible with schema"
    echo "Manual migration required"
    exit 1
fi
```

#### Schema Changes

```zsh
if ! vde_detect_schema_changes "$config"; then
    echo "WARNING: Schema has been updated"
    echo "Cache regeneration recommended"
    regenerate_vm_types_cache
fi
```

#### Validation Failure

```zsh
if ! vde_validate_and_update "$config" "$schema" "$cache"; then
    case $? in
        $VDE_ERR_CACHE_INVALID)
            # Safe to regenerate
            regenerate_vm_types_cache
            ;;
        $VDE_ERR_INVALID_DATA)
            # Data problem - manual intervention
            echo "ERROR: Validation failed"
            echo "Check config file for errors"
            exit 1
            ;;
    esac
fi
```

### Best Practices

#### 1. Always Backup Before Updates

```zsh
backup=$(vde_backup_config "$config")
## ... perform updates ...
```

#### 2. Check Compatibility First

```zsh
if ! vde_check_schema_compatibility "$config" "$schema"; then
    echo "Incompatible - manual migration needed"
    exit 1
fi
```

#### 3. Detect Changes Proactively

```zsh
if ! vde_detect_schema_changes "$config"; then
    regenerate_vm_types_cache
fi
```

#### 4. Use Complete Workflow

```zsh
## Preferred: Use vde_validate_and_update for complete workflow
vde_validate_and_update "$config" "$schema" "$cache"
```

#### 5. Handle Errors Appropriately

```zsh
if ! vde_validate_and_update "$config" "$schema" "$cache"; then
    case $? in
        $VDE_ERR_CACHE_INVALID)
            # Automatic recovery
            regenerate_vm_types_cache
            ;;
        $VDE_ERR_INVALID_DATA)
            # Manual intervention required
            echo "ERROR: Fix config file"
            exit 1
            ;;
    esac
fi
```

### Troubleshooting

#### "Version incompatible"

**Cause:** Config version doesn't match schema requirements

**Solution:**
1. Check config version: `vde_get_config_version config.json`
2. Check schema version: `vde_get_schema_version schema.json`
3. Update config version to match schema
4. Or migrate config to new format

#### "Schema has been updated"

**Cause:** Schema file is newer than config

**Solution:**
```bash
## Regenerate cache
source lib/vm-common
regenerate_vm_types_cache
```

#### "Backup failed"

**Cause:** Permission issues or disk full

**Solution:**
```bash
## Check permissions
ls -la .cache/config-backups/

## Check disk space
df -h .cache/
```

#### "Cannot determine version"

**Cause:** Config or schema missing version field

**Solution:**
1. Add version to config:
   ```json
   {
     "version": "1.0",
     ...
   }
   ```
2. Add version to schema:
   ```json
   {
     "properties": {
       "version": {
         "type": "string",
         "pattern": "^[0-9]+\\.[0-9]+$"
       }
     }
   }
   ```

### Summary

The schema update mechanisms provide:

✅ **Version Management**
- Detect config and schema versions
- Check compatibility automatically

✅ **Change Detection**
- Identify when schemas are updated
- Trigger cache regeneration

✅ **Safe Updates**
- Automatic backup before changes
- Validation at every step

✅ **Complete Workflows**
- Integrated update processes
- Error recovery mechanisms

✅ **Tested and Validated**
- 20/20 unit tests passing
- Demo script for all features
- Integration with existing validation

All mechanisms are production-ready and fully tested.


## VDE Schema Validation System

Centralized JSON schema validation and cache regeneration for all VDE libraries.

### Overview

The VDE schema validation system provides:
- **Automatic validation** of JSON config files against their schemas
- **Cache regeneration** when configs change or become corrupt
- **Error recovery** from corrupt or missing files
- **Consistent validation** across all libraries

### Architecture

#### Core Functions (vde-core)

All schema validation logic is centralized in `lib/vde-core`:

```zsh
## Check if schema file is valid
vde_check_schema_integrity <schema_file>

## Validate JSON against schema
vde_validate_json_schema <json_file> <schema_file>

## Get schema file for a JSON config
vde_get_schema_for_json <json_file>

## Validate JSON and check if cache needs regeneration
vde_validate_or_regenerate <json_file> <schema_file> <cache_file>
```

#### Library Integration (vm-common)

Libraries use centralized validation:

```zsh
## Validate VM types config without loading
validate_vm_types_config

## Force cache regeneration
regenerate_vm_types_cache

## Load VM types (with automatic validation)
load_vm_types
```

### Error Codes

New error codes in `vde-constants`:

| Code | Value | Description |
|------|-------|-------------|
| `VDE_ERR_INVALID_DATA` | 10 | Data validation failed (corrupt file, schema mismatch) |
| `VDE_ERR_CACHE_INVALID` | 11 | Cache is stale, corrupt, or missing (needs regeneration) |

### Usage

#### Automatic Validation

Validation happens automatically when loading VM types:

```zsh
source lib/vm-common
load_vm_types  # Validates JSON against schema automatically
```

Output:
```
[INFO] Using JSON VM types config: data/vm-types.json
[INFO] Validating config against schema: data/vm-types.schema.json
[INFO] Schema validation passed: data/vm-types.json
[INFO] Loading VM types from cache...
```

#### Manual Validation

Validate without loading:

```zsh
source lib/vm-common
validate_vm_types_config
## Returns: VDE_SUCCESS (0) or VDE_ERR_INVALID_DATA (10)
```

#### Force Cache Regeneration

Rebuild cache from JSON:

```zsh
source lib/vm-common
regenerate_vm_types_cache
```

This will:
1. Validate JSON against schema
2. Remove old cache
3. Reload and regenerate cache

#### Direct Core Functions

Use core functions directly:

```zsh
source lib/vde-core

## Get schema for JSON file
schema_file=$(vde_get_schema_for_json "data/vm-types.json")

## Validate JSON
if vde_validate_json_schema "data/vm-types.json" "$schema_file"; then
    echo "Valid"
else
    echo "Invalid"
fi
```

### Cache Management

#### Cache Validation

The system validates cache files before loading:

1. **Syntax check**: Verify cache is valid zsh
2. **Source check**: Test sourcing the cache
3. **Corruption detection**: Remove corrupt cache automatically

```zsh
## Cache validation (automatic in load_vm_types)
if _is_cache_valid "$VM_TYPES_CACHE" "$VM_TYPES_JSON"; then
    if zsh -n "$VM_TYPES_CACHE" 2>/dev/null; then
        if . "$VM_TYPES_CACHE" 2>/dev/null; then
            # Cache loaded successfully
        else
            # Cache corrupt, remove and regenerate
            rm -f "$VM_TYPES_CACHE"
        fi
    fi
fi
```

#### Cache Regeneration

Cache is regenerated when:
- Cache file is missing
- Cache file is corrupt
- JSON file is newer than cache
- Explicitly requested via `regenerate_vm_types_cache`

Regeneration process:
1. Validate JSON against schema
2. Parse JSON with `jq`
3. Generate zsh associative arrays
4. Write cache file with proper escaping

### Schema Files

#### vm-types.schema.json

Location: `data/vm-types.schema.json`

Defines validation rules for VM type configuration:

**Language VMs** must have:
- `name`: lowercase alphanumeric string
- `display`: non-empty string
- `install`: non-empty shell command
- `port`: null

**Service VMs** must have:
- `name`: lowercase alphanumeric string
- `display`: non-empty string
- `install`: non-empty shell command
- `port`: comma-separated port numbers (e.g., `"80,443"`)

#### Schema Naming Convention

Schemas follow the naming pattern: `{config}.schema.json`

Example:
- Config: `vm-types.json`
- Schema: `vm-types.schema.json`

This allows automatic schema discovery via `vde_get_schema_for_json`.

### Error Handling

#### Validation Failures

When validation fails:

```zsh
[ERROR] JSON validation failed: data/vm-types.json
[ERROR] Config file may be corrupt or missing required fields
```

The function returns `VDE_ERR_INVALID_DATA` (10).

#### Recovery

The system automatically recovers from:
- **Corrupt cache**: Removed and regenerated
- **Missing cache**: Generated on next load
- **Stale cache**: Regenerated when JSON is newer

For corrupt JSON:
- **No automatic recovery** (requires manual fix)
- **Clear error messages** indicating the problem
- **Validation prevents bad data** from being used

### Testing

#### Unit Tests

Location: `tests/unit/vde-schema-validation.test.zsh`

Coverage:
- Schema integrity validation
- JSON schema validation
- Schema discovery
- Error code definition
- Cache validation
- Invalid data detection

Run tests:
```bash
tests/unit/vde-schema-validation.test.zsh
## Expected: 16+ passed, 0-1 failed
```

#### VM Types Schema Tests

Location: `tests/unit/vm-types-schema.test.zsh`

Coverage:
- VM types structure validation
- Language VM requirements
- Service VM requirements
- Name and port patterns

Run tests:
```bash
tests/unit/vm-types-schema.test.zsh
## Expected: 10 passed, 0 failed
```

### Design Principles

#### 1. Single Source of Truth

JSON files are the authoritative source:
- **Schemas validate** JSON structure
- **Caches optimize** loading speed
- **Validation ensures** data integrity

#### 2. Fail Fast

Validation happens early:
- **On load**: Validate before using data
- **On write**: Validate before committing
- **On cache**: Validate before generation

#### 3. Automatic Recovery

System self-heals when possible:
- **Corrupt cache**: Auto-regenerate
- **Missing cache**: Auto-create
- **Stale cache**: Auto-update

#### 4. Centralized Logic

All validation in one place:
- **vde-core**: Core validation functions
- **Libraries**: Call core functions
- **Consistent**: Same validation everywhere

### Future Enhancements

#### Additional Schemas

Create schemas for other JSON configs:
- Docker compose configurations
- Environment variable files
- Test configurations

#### Schema Versioning

Track schema versions for migration:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "version": "2.0",
  "previousVersions": ["1.0"]
}
```

#### Validation Caching

Cache validation results to avoid re-validating:
```zsh
## Cache validation result with checksum
validation_cache=".cache/validation-$(md5sum vm-types.json)"
```

#### JSON Schema Library

Use proper JSON Schema validator:
```bash
pip install jsonschema
python3 -m jsonschema -i vm-types.json vm-types.schema.json
```

### Examples

#### Example 1: Loading VM Types

```zsh
#!/usr/bin/env zsh
source lib/vm-common

## Automatic validation happens here
load_vm_types

## Use VM data
echo "Python VM: ${VM_DISPLAY[python]}"
```

#### Example 2: Validating Before Commit

```zsh
#!/usr/bin/env zsh
source lib/vm-common

## Validate config before committing changes
if validate_vm_types_config; then
    echo "Config valid, safe to commit"
    git add data/vm-types.json
    git commit -m "Update VM types config"
else
    echo "Config invalid, fix errors first"
    exit 1
fi
```

#### Example 3: Forcing Cache Rebuild

```zsh
#!/usr/bin/env zsh
source lib/vm-common

## Rebuild cache if corrupt
if ! load_vm_types 2>/dev/null; then
    echo "Load failed, regenerating cache..."
    regenerate_vm_types_cache
fi
```

#### Example 4: Custom Validation

```zsh
#!/usr/bin/env zsh
source lib/vde-core

## Validate custom JSON config
json_file="my-config.json"
schema_file=$(vde_get_schema_for_json "$json_file")

if vde_validate_json_schema "$json_file" "$schema_file"; then
    echo "✓ Configuration valid"
else
    echo "✗ Configuration invalid"
    exit $VDE_ERR_INVALID_DATA
fi
```

### Troubleshooting

#### "Schema validation failed"

**Cause**: JSON doesn't match schema requirements

**Solution**:
1. Check JSON syntax: `jq . data/vm-types.json`
2. Compare against schema: `data/vm-types.schema.json`
3. Fix missing/invalid fields
4. Re-run validation

#### "Cache file corrupt"

**Cause**: Cache has syntax errors or invalid content

**Solution**:
```zsh
## Automatic recovery - just reload
source lib/vm-common
regenerate_vm_types_cache
```

#### "Schema file not found"

**Cause**: Schema missing or in wrong location

**Solution**:
1. Verify schema exists: `ls data/*.schema.json`
2. Check naming: `{config}.schema.json`
3. Create schema if missing

#### "Python not available"

**Cause**: Validation requires Python 3

**Solution**:
```bash
## Install Python 3
brew install python3  # macOS
apt install python3   # Debian/Ubuntu
```

### References

- **JSON Schema Spec**: https://json-schema.org/
- **Draft 7 Spec**: http://json-schema.org/draft-07/schema
- **Validation Examples**: `tests/unit/vde-schema-validation.test.zsh`
- **VM Types Schema**: `data/vm-types.schema.json`


## User Model & Naming Conventions

Information about the user account inside containers and VDE naming conventions.

[← Back to README](../README.md)

---

### User Account

All containers run with the same user configuration for consistency.

| Setting | Value |
|---------|-------|
| **Username** | `devuser` |
| **UID** | `1000` |
| **GID** | `1000` |
| **Shell** | `/bin/zsh` with oh-my-zsh |
| **Editor** | neovim with LazyVim |
| **Sudo** | Passwordless sudo access |

---

### Home Directory Structure

Inside each VM:

```
/home/devuser/
├── .ssh/              # SSH keys and known_hosts
├── .zshrc            # Zsh configuration with oh-my-zsh
├── .zprofile         # PATH configuration
├── .config/nvim/      # LazyVim configuration
└── workspace/         # Your project directory (mounted from host)
```

---

### Modifying User Setup

To modify user setup across all containers, edit: `configs/docker/vde-base.Dockerfile`

Then rebuild:
```bash
./bin/build-and-start --rebuild
```

---

### Naming Conventions

#### Language VMs

| Aspect | Convention | Example |
|--------|------------|---------|
| **Container** | `<name>-dev` | `vde-python` |
| **SSH Host** | `<name>-dev` | `vde-python` |
| **Port Range** | 2200-2299 | 2200, 2201, 2202... |
| **Project Directory** | `projects/<name>/` | `projects/python/` |
| **Volume Mount** | `/home/devuser/workspace` | (from `projects/python/`) |

#### Service VMs

| Aspect | Convention | Example |
|--------|------------|---------|
| **Container** | `<name>` | `postgres` |
| **SSH Host** | `<name>` | `postgres` |
| **Port Range** | 2400-2499 | 2400, 2401, 2402... |
| **Data Directory** | `data/<name>/` | `data/postgres/` |
| **Service Port** | Container-specific | 5432 for postgres |

---

### Container Examples

| Type | Name | Container | SSH Host | SSH Port | Service Port |
|------|------|-----------|----------|----------|-------------|
| Language | python | vde-python | vde-python | 2213 | - |
| Language | rust | vde-rust | vde-rust | 2216 | - |
| Language | go | vde-go | vde-go | 2202 | - |
| Service | postgres | postgres | postgres | 2404 | 5432 |
| Service | redis | redis | redis | 2406 | 6379 |
| Service | mongodb | mongodb | mongodb | 2402 | 27017 |

---

[← Back to README](../README.md)


