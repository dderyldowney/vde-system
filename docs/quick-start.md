# Quick Start

Get up and running with VDE in minutes.

[← Back to README](../README.md)

---

## First-Time Setup

```bash
# 1. Navigate to your dev directory
cd ~/dev  # or wherever you cloned this repo

# 2. List all predefined VM types
./scripts/list-vms

# 3. Create a new language VM (auto-allocates SSH port)
./scripts/create-virtual-for go

# 4. Start the VM
./scripts/start-virtual go

# 5. Connect via SSH
ssh go-dev

# 6. Start working
cd ~/workspace  # Your project directory
```

---

## What Just Happened?

When you ran `create-virtual-for go`:

1. **Port Allocation**: SSH port 2200 was automatically assigned
2. **Config Created**: `configs/docker/go/docker-compose.yml`
3. **Directories Created**: `projects/go/`, `logs/go/`
4. **Environment File**: `env-files/go.env`
5. **SSH Config**: Entry added to `~/.ssh/config`

When you ran `start-virtual go`:

1. **Image Built**: Docker image built from base-dev template
2. **Container Started**: Container `go-dev` started
3. **SSH Ready**: SSH server running on port 2200

---

## Next Steps

- **Create more VMs**: `./scripts/create-virtual-for python`
- **Start multiple VMs**: `./scripts/start-virtual go python`
- **Use VSCode**: Connect via Remote-SSH for full IDE support
- **Try AI Assistant**: `./scripts/vde-ai "start python"`

For more details, see [Command Reference](./command-reference.md) or [VDE AI Assistant](./vde-ai-assistant.md).

---

[← Back to README](../README.md)
