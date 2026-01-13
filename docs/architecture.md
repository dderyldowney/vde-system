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

---

## Base Image

All VMs build from `configs/docker/base-dev.Dockerfile` which includes:

- System updates and security patches
- SSH server configuration
- sudo access for devuser
- zsh with oh-my-zsh framework
- neovim with LazyVim configuration
- Common development tools (git, curl, wget, etc.)

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
