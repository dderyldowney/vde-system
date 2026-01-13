# User Model & Naming Conventions

Information about the user account inside containers and VDE naming conventions.

[← Back to README](../README.md)

---

## User Account

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

## Home Directory Structure

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

## Modifying User Setup

To modify user setup across all containers, edit: `configs/docker/base-dev.Dockerfile`

Then rebuild:
```bash
./scripts/build-and-start --rebuild
```

---

## Naming Conventions

### Language VMs

| Aspect | Convention | Example |
|--------|------------|---------|
| **Container** | `<name>-dev` | `python-dev` |
| **SSH Host** | `<name>-dev` | `python-dev` |
| **Port Range** | 2200-2299 | 2200, 2201, 2202... |
| **Project Directory** | `projects/<name>/` | `projects/python/` |
| **Volume Mount** | `/home/devuser/workspace` | (from `projects/python/`) |

### Service VMs

| Aspect | Convention | Example |
|--------|------------|---------|
| **Container** | `<name>` | `postgres` |
| **SSH Host** | `<name>` | `postgres` |
| **Port Range** | 2400-2499 | 2400, 2401, 2402... |
| **Data Directory** | `data/<name>/` | `data/postgres/` |
| **Service Port** | Container-specific | 5432 for postgres |

---

## Container Examples

| Type | Name | Container | SSH Host | SSH Port | Service Port |
|------|------|-----------|----------|----------|-------------|
| Language | python | python-dev | python-dev | 2200 | - |
| Language | rust | rust-dev | rust-dev | 2201 | - |
| Language | go | go-dev | go-dev | 2202 | - |
| Service | postgres | postgres | postgres | 2400 | 5432 |
| Service | redis | redis | redis | 2401 | 6379 |
| Service | mongodb | mongodb | mongodb | 2402 | 27017 |

---

[← Back to README](../README.md)
