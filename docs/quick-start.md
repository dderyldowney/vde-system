# Quick Start

Get up and running with VDE in minutes.

[← Back to README](../README.md)

---

## First-Time Setup

```zsh
# 1. Navigate to your dev directory
cd ~/dev  # or wherever you cloned this repo

# 2. List all predefined VM types
vde list

# 3. Create a new language VM (auto-allocates SSH port)
vde create go

# 4. Start the VM
vde start go

# 5. Connect via SSH
ssh vde-go

# 6. Start working
cd ~/workspace  # Your project directory
```

---

> **💡 SSH Connection Help**
>
> If `ssh vde-go` doesn't work, you can connect manually:
>
> ```zsh
> ssh devuser@localhost -p 2213
> ```
>
> **Why?** Your computer's username (like `alex` or `sam`) is different from the container's username (`devuser`). The SSH config above handles this automatically, but the manual command needs `devuser@`.
>
> The `-p 2213` is the SSH port (each VM has its own port).

---

## What Just Happened?

When you ran `vde create go`:

1. **Port Allocation**: SSH port 2213 was automatically assigned
2. **Config Created**: `configs/docker/go/docker-compose.yml`
3. **Directories Created**: `projects/go/`, `logs/go/`
4. **Environment File**: `env-files/go.env`
5. **SSH Config**: Entry added to `~/.ssh/vde/config`
6. **SSH Agent**: Started automatically, keys loaded automatically
7. **SSH Keys**: Detected or generated automatically

When you ran `vde start go`:

1. **SSH Environment**: Agent verified, keys ready (automatic)
2. **Image Built**: Docker image built from vde-base template
3. **Container Started**: Container `vde-go` started
4. **SSH Agent Forwarding**: Enabled for VM-to-VM and external communication
5. **SSH Ready**: SSH server running on port 2213

**All SSH setup is automatic** - no manual configuration required.

---

## VM-to-VM Communication

With SSH agent forwarding, you can communicate between VMs:

```zsh
# Create and start multiple VMs
vde create python postgres
vde start python postgres

# From Python VM, connect to PostgreSQL
ssh vde-python
ssh vde-postgres psql -U devuser

# Or from your host
ssh vde-python
# Now from within Python VM:
ssh vde-postgres      # Uses your host's SSH keys!
```

See [SSH Configuration](./ssh-configuration.md) for complete details.

---

## Next Steps

- **Create more VMs**: `vde create python`
- **Start multiple VMs**: `vde start go python`
- **Stop a VM**: `vde stop go`
- **List VMs**: `vde list`
- **Use VSCode**: Connect via Remote-SSH for full IDE support

For more details, see [Command Reference](./command-reference.md).

---

[← Back to README](../README.md)
