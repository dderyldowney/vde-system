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

> **💡 SSH Connection Help**
>
> If `ssh go-dev` doesn't work, you can connect manually:
>
> ```bash
> ssh devuser@localhost -p 2200
> ```
>
> **Why?** Your computer's username (like `alex` or `sam`) is different from the container's username (`devuser`). The SSH config above handles this automatically, but the manual command needs `devuser@`.
>
> The `-p 2200` is the SSH port (each VM has its own port).

---

## What Just Happened?

When you ran `create-virtual-for go`:

1. **Port Allocation**: SSH port 2200 was automatically assigned
2. **Config Created**: `configs/docker/go/docker-compose.yml`
3. **Directories Created**: `projects/go/`, `logs/go/`
4. **Environment File**: `env-files/go.env`
5. **SSH Config**: Entry added to `~/.ssh/config`
6. **SSH Agent**: Started automatically, keys loaded automatically
7. **SSH Keys**: Detected or generated automatically

When you ran `start-virtual go`:

1. **SSH Environment**: Agent verified, keys ready (automatic)
2. **Image Built**: Docker image built from base-dev template
3. **Container Started**: Container `go-dev` started
4. **SSH Agent Forwarding**: Enabled for VM-to-VM and external communication
5. **SSH Ready**: SSH server running on port 2200

**All SSH setup is automatic** - no manual configuration required.

---

## VM-to-VM Communication

With SSH agent forwarding, you can communicate between VMs:

```bash
# Create and start multiple VMs
./scripts/create-virtual-for python postgres
./scripts/start-virtual python postgres

# From Python VM, connect to PostgreSQL
ssh python-dev
ssh postgres-dev psql -U devuser

# Or from your host
ssh python-dev
# Now from within Python VM:
ssh postgres-dev      # Uses your host's SSH keys!
```

See [SSH Configuration](./ssh-configuration.md) for complete details.

---

## Next Steps

- **Create more VMs**: `./scripts/create-virtual-for python`
- **Start multiple VMs**: `./scripts/start-virtual go python`
- **Use VSCode**: Connect via Remote-SSH for full IDE support

For more details, see [Command Reference](./command-reference.md).

---

[← Back to README](../README.md)
