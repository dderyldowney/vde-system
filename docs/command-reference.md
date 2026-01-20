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

[← Back to README](../README.md)
