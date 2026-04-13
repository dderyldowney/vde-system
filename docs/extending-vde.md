# Extending VDE

VDE is designed to be easily extensible. You can add support for new programming languages, new services, or customize existing ones without modifying core library code. The entire system is data-driven through configuration files and templates.

[← Back to README](../README.md)

---

## Understanding VDE Architecture

Before extending VDE, it helps to understand the Hub-and-Spoke model detailed in `docs/ARCHITECTURE.md`:

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Request                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  vm-common (Shared Library)                     │
│  • Parses vm-types.conf (with caching)                          │
│  • Allocates SSH port (from port registry)                      │
│  • Validates configuration                                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Template Rendering                          │
│  • Reads templates/compose-language.yml                         │
│  • Substitutes: {{NAME}}, {{SSH_PORT}}, {{INSTALL_CMD}}        │
│  • Writes to: configs/docker/<name>/docker-compose.yml          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      File Creation                              │
│  • configs/docker/<name>/docker-compose.yml                     │
│  • env-files/<name>.env                                         │
│  • projects/<name>/ (or data/<name>/ for services)              │
│  • logs/<name>/                                                 │
│  • ~/.ssh/vde/config (appends entry)                                │
└─────────────────────────────────────────────────────────────────┘
```

### Key Files

| File | Purpose | Edit to Extend |
|------|---------|----------------|
| `data/vm-types.conf` | Defines all VM types (Beskar Source) | ✅ **Yes** - Add new entries |
| `templates/compose-language.yml` | Language VM template | Rarely - only for structural changes |
| `templates/compose-service.yml` | Service VM template | Rarely - only for structural changes |
| `templates/ssh-entry.txt` | SSH config template | Rarely - only for format changes |
| `lib/vm-common` | Core functions | Never - use templates/config instead |
| `lib/vde-*` | Modular libraries | Never - use templates/config instead |

### vm-types.conf Format (The 8-Field Standard)

```
type|name|aliases|display_name|pkgs|custom_cmd|service_port|ssh_port
```

| Field | Description | Example |
|-------|-------------|---------|
| `type` | `lang` or `service` | `lang` |
| `display_name` | Human-readable name | `Zig` |
| `pkgs` | Required system packages | `zig-sdk` |
| `custom_cmd` | USP initialization script | `zsh /vde/scripts/setup/zig-init.zsh` |
| `service_port` | Port number (services only) | `5432` |

---

## Adding New Languages

Adding a new programming language to VDE is a three-step process:

### Step 1: Add to vm-types.conf

You can do this manually or with the `add-vm-type` script.

**Option A: Using vde add (Recommended)**

```zsh
vde add lang zig "Zig" "zig-sdk" "zsh /vde/scripts/setup/zig-init.zsh"
```

**Option B: Manual Entry**

Edit `data/vm-types.conf` and add a line:

```zsh
lang|vde-zig|zig|Zig|zig-sdk|zsh /vde/scripts/setup/zig-init.zsh||
```

### Step 2: Create the USP Hydration Script

Create `scripts/setup/zig-init.zsh`. It MUST be ZSH-only and follow the USP mandate (Rule F).

```zsh
#!/usr/bin/env zsh
set -e
# Install logic here
apt-get update && apt-get install -y zig
apt-get clean && rm -rf /var/lib/apt/lists/*
```

### Step 3: Ignite the Spoke

```zsh
vde start zig
```

### What Gets Created

```
configs/docker/zig/
└── docker-compose.yml

env-files/
└── zig.env

~/.ssh/vde/config               # New entry appended:
                            #     HostName localhost
                            #     Port 2206
                            #     User devuser
                            #     IdentityFile ~/.ssh/vde/vde_student
                            #     IdentitiesOnly yes
```

---

## Adding New Services

Adding a service (database, cache, etc.) requires specifying the service port.

### Step 1: Add to vm-types.conf

```zsh
service|vde-rabbitmq|rabbit,rabbitmq-server|RabbitMQ|rabbitmq-server|zsh /vde/scripts/setup/rabbitmq-init.zsh|5672,15672|2405
```

### Step 2: Create the Service VM

```zsh
vde create rabbitmq
vde start rabbitmq
ssh rabbitmq
```

---

## Library Extension Patterns

VDE's modular library architecture allows for extension without modifying core code.

### Using vde-core for Lightweight Operations

For scripts that don't need full VDE functionality, use `vde-core`:

```zsh
#!/usr/bin/env zsh
source "lib/vde-core"

# Load VM types (with caching)
vde_core_load_types

# Query VM information
if vde_core_is_known_vm "python"; then
    echo "Python is a known VM type"
fi
```

### Adding Custom Error Messages

Use `vde-errors` to provide contextual error messages:

```zsh
source "lib/vde-errors"

vde_error_show \
    "Custom operation failed" \
    "Because of X condition" \
    "1. Do this\n2. Do that" \
    "docs/troubleshooting.md#custom-error"
```

### Extending the Parser

To add new intents to the natural language parser:

1. **Edit `lib/vde-parser`** to add the intent constant:
```zsh
readonly INTENT_CUSTOM="custom"
```

2. **Add detection pattern** in `detect_intent()`:
```zsh
if [[ "$input_lower" =~ "custom pattern" ]]; then
    echo "$INTENT_CUSTOM"
    return
fi
```

3. **Add handler** in `execute_plan()`:
```zsh
"$INTENT_CUSTOM")
    # Your custom logic here
    return $?
    ;;
```

---

## Current VM Types (v1.3.1 The Sovereign Baseline)

VDE supports 29+ pre-configured VM types including Python, Go, Rust, PostgreSQL, Redis, and JupyterLab.

See [predefined-vm-types.md](./predefined-vm-types.md) for detailed information.

---

[← Back to README](../README.md)
