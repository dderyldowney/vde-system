# Command Reference

Complete reference for all VDE commands.

[← Back to README](../README.md)

---

## List Available VMs

```bash
# List all VMs
vde list

# List only language VMs
vde list --lang

# List only service VMs
vde list --svc

# Search for specific VMs
vde list python
vde list --lang script
```

---

## Create New VMs

```bash
# Create a language VM
vde create go

# Create a service VM
vde create postgres

# Create using alias
vde create nodejs      # Same as 'js'
vde create postgresql  # Same as 'postgres'

# Show help
vde create --help
```

### What `vde create` does:

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
vde start python

# Start multiple VMs
vde start python go rust

# Start all VMs
vde start all

# Start with rebuild (when Dockerfiles change)
vde start python --rebuild

# Start with full clean rebuild
vde start all --rebuild --no-cache

# Mix languages and services
vde start python postgres redis
```

---

## Stop VMs

```bash
# Stop single VM
vde stop python

# Stop multiple VMs
vde stop python go rust

# Stop all VMs
vde stop all
```

---

## Build and Start All VMs

```bash
# Shutdown all, then start all
vde create-and-start all

# With rebuild
vde create-and-start all --rebuild

# With full clean rebuild
vde create-and-start all --rebuild --no-cache
```

---

## Add New VM Types

```bash
# Add a language (auto-detects type)
vde create zig "apt-get update -y && apt-get install -y zig"

# Add with aliases
vde create dart "apt-get update -y && apt-get install -y dart" "dartlang,flutter"

# Add a service (requires --type and --svc-port)
vde create --type service --svc-port 5672 rabbitmq \
    "apt-get install -y rabbitmq-server" "rabbit"

# Add with custom display name
vde create --display "Zig Language" zig \
    "apt-get update -y && apt-get install -y zig"

# Show help
vde create --help
```

---

[← Back to README](../README.md)
