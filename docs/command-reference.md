# Command Reference

Complete reference for all VDE commands.

[← Back to README](../README.md)

---

## List Available VMs

```bash
# List all VMs
./scripts/list-vms

# List only language VMs
./scripts/list-vms --lang

# List only service VMs
./scripts/list-vms --svc

# Search for specific VMs
./scripts/list-vms python
./scripts/list-vms --lang script
```

---

## Create New VMs

```bash
# Create a language VM
./scripts/create-virtual-for go

# Create a service VM
./scripts/create-virtual-for postgres

# Create using alias
./scripts/create-virtual-for nodejs      # Same as 'js'
./scripts/create-virtual-for postgresql  # Same as 'postgres'

# Show help
./scripts/create-virtual-for --help
```

### What `create-virtual-for` does:

1. Validates the VM name exists in predefined list
2. Auto-allocates SSH port (2200-2299 for languages, 2400-2499 for services)
3. Creates `configs/docker/<name>/docker-compose.yml` from template
4. Creates directories: `projects/<name>/` or `data/<name>/`, `logs/<name>/`
5. Creates `env-files/<name>.env`
6. Adds SSH config entry to `~/.ssh/config` (with backup)

---

## Start VMs

```bash
# Start single VM
./scripts/start-virtual python

# Start multiple VMs
./scripts/start-virtual python go rust

# Start all VMs
./scripts/start-virtual all

# Start with rebuild (when Dockerfiles change)
./scripts/start-virtual python --rebuild

# Start with full clean rebuild
./scripts/start-virtual all --rebuild --no-cache

# Mix languages and services
./scripts/start-virtual python postgres redis
```

---

## Stop VMs

```bash
# Stop single VM
./scripts/shutdown-virtual python

# Stop multiple VMs
./scripts/shutdown-virtual python go rust

# Stop all VMs
./scripts/shutdown-virtual all
```

---

## Build and Start All VMs

```bash
# Shutdown all, then start all
./scripts/build-and-start

# With rebuild
./scripts/build-and-start --rebuild

# With full clean rebuild
./scripts/build-and-start --rebuild --no-cache
```

---

## Add New VM Types

```bash
# Add a language (auto-detects type)
./scripts/add-vm-type zig "apt-get update -y && apt-get install -y zig"

# Add with aliases
./scripts/add-vm-type dart "apt-get update -y && apt-get install -y dart" "dartlang,flutter"

# Add a service (requires --type and --svc-port)
./scripts/add-vm-type --type service --svc-port 5672 rabbitmq \
    "apt-get install -y rabbitmq-server" "rabbit"

# Add with custom display name
./scripts/add-vm-type --display "Zig Language" zig \
    "apt-get update -y && apt-get install -y zig"

# Show help
./scripts/add-vm-type --help
```

---

## VDE AI Assistant

### Command-Line Mode

```bash
# One-shot natural language commands
./scripts/vde-ai "what VMs can I create?"
./scripts/vde-ai "start Python and PostgreSQL"
./scripts/vde-ai "what's running?"
```

### Interactive Chat Mode

```bash
./scripts/vde-chat

# In the chat session:
# [VDE] → create a Go VM
# [AI] → Creating Go VM... Done!
# [VDE] → start it
# [AI] → Starting Go VM... Done!
# [VDE] → exit
```

### Options

| Option | Purpose |
|--------|---------|
| `--ai` | Enable LLM-based parsing (requires API key) |
| `--dry-run` | Show what would happen without executing |
| `--help, -h` | Show help message |

### Environment Variables

| Variable | Purpose |
|----------|---------|
| `VDE_USE_AI` | Set to `1`, `true`, or `yes` to enable LLM-based parsing by default |
| `ANTHROPIC_AUTH_TOKEN` | Your Anthropic authentication token (highest priority) |
| `CLAUDE_API_KEY` | Your Claude API key for AI mode (legacy) |
| `ANTHROPIC_API_KEY` | Your Anthropic API key for AI mode |
| `ANTHROPIC_BASE_URL` | Custom base URL for Anthropic API (e.g., `https://api.z.ai/api/anthropic`) |
| `ANTHROPIC_MODEL` | Custom model to use (e.g., `glm-4.7`) |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | Default model for Anthropic-compatible APIs |

For more details, see [VDE AI Assistant](./vde-ai-assistant.md).

---

[← Back to README](../README.md)
