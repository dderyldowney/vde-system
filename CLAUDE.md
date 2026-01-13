# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a **Virtual Development Environment (VDE)** providing Docker-based development containers for multiple programming languages (Python, Rust, JavaScript, C#, Ruby) with shared infrastructure services (PostgreSQL, Redis, MongoDB, Nginx). All containers use SSH for access and are designed for use with VSCode Remote-SSH.

## Architecture

**Container Setup:**
- Each language has its own development container accessible via SSH
- All containers run as `devuser` (non-root) with sudo privileges
- SSH key-based authentication only (password auth disabled)
- Shared services (PostgreSQL, Redis, MongoDB, Nginx) accessible from all language containers

**Supported Languages:**
| Language       | SSH Port | Host Alias      |
|----------------|----------|-----------------|
| Python 3.14    | 2200     | python-dev      |
| Rust (latest)  | 2201     | rust-dev        |
| JavaScript/Node| 2202     | js-dev          |
| C#             | 2203     | csharp-dev      |
| Ruby           | 2204     | ruby-dev        |
| PostgreSQL     | 2400     | postgres        |
| Redis          | 2401     | redis           |
| MongoDB        | 2402     | mongodb         |
| Nginx          | 2403     | nginx           |

## Container Management

### Starting Containers

```bash
# Start all VMs
./scripts/start-virtual.sh all

# Start specific VM
./scripts/start-virtual.sh python
./scripts/start-virtual.sh rust

# Start with rebuild (when Dockerfiles change)
./scripts/start-virtual.sh python --rebuild

# Full rebuild with no cache
./scripts/start-virtual.sh python --rebuild --no-cache
```

### Stopping Containers

```bash
# Stop all VMs
./scripts/shutdown-virtual.sh all

# Stop specific VM
./scripts/shutdown-virtual.sh python
./scripts/shutdown-virtual.sh postgres
```

### Initial Setup

```bash
# First-time setup: build and start all containers
./scripts/build-and-start-dev.sh

# Rebuild all containers
./scripts/build-and-start-dev.sh --rebuild

# Full clean rebuild
./scripts/build-and-start-dev.sh --rebuild --no-cache
```

## SSH Configuration

**Requirements:**
- SSH private key: `~/.ssh/id_ed25519` (or your key)
- SSH public key must be in: `$HOME/dev/public-ssh-keys/`
- SSH config: Copy from `backup/ssh/config` to `~/.ssh/config`

**Key Permissions:**
```bash
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub
chmod 600 ~/.ssh/config
```

**SSH Config Example:**
```
Host python-dev
  HostName localhost
  Port 2200
  User devuser
  IdentityFile ~/.ssh/id_ed25519
  IdentitiesOnly yes

Host rust-dev
  HostName localhost
  Port 2201
  User devuser
  IdentityFile ~/.ssh/id_ed25519
  IdentitiesOnly yes
```

**Connecting:**
```bash
# Command line
ssh python-dev
ssh rust-dev
ssh js-dev
ssh csharp-dev
ssh ruby-dev
ssh postgres
ssh nginx

# VSCode Remote-SSH
# Use connection name: python-dev, rust-dev, js-dev, csharp-dev, ruby-dev, postgres, nginx
```

## Directory Structure

```
$HOME/dev/
├── backup/ssh/config           # SSH config template
├── configs/                    # Configuration files
│   ├── docker/                # Docker configurations
│   │   ├── base-dev.Dockerfile # Base image for all dev VMs
│   │   ├── python/            # Python container config
│   │   ├── rust/              # Rust container config
│   │   ├── js/                # JavaScript container config
│   │   ├── csharp/            # C# container config
│   │   ├── ruby/              # Ruby container config
│   │   ├── postgres/          # PostgreSQL container config
│   │   ├── redis/             # Redis container config
│   │   ├── mongodb/           # MongoDB container config
│   │   └── nginx/             # Nginx container config
│   └── nginx/                 # Nginx configuration files
├── data/                       # Persistent data volumes
│   ├── postgres/              # PostgreSQL data (persisted)
│   ├── mongodb/               # MongoDB data
│   └── redis/                 # Redis data
├── env-files/                  # Environment variable files
├── logs/                       # Application and access logs
│   └── nginx/                 # Nginx access and error logs
├── projects/                   # Project source code
│   ├── python/                # Python projects
│   ├── rust/                  # Rust projects
│   ├── js/                    # JavaScript projects
│   ├── csharp/                # C# projects
│   └── ruby/                  # Ruby projects
├── public-ssh-keys/           # SSH public keys for containers
└── scripts/                   # Management scripts
    ├── start-virtual.sh
    ├── shutdown-virtual.sh
    └── build-and-start-dev.sh
```

## User Model

**All containers use:**
- Username: `devuser`
- Shell: `/bin/zsh` with oh-my-zsh (agnoster theme)
- Editor: `neovim` with LazyVim configuration
- Sudo: Passwordless sudo access
- Authentication: SSH key only

**Base Image:** All language containers extend `configs/docker/base-dev.Dockerfile`

To modify user setup across all containers, edit the base Dockerfile.

## Shared Services

### PostgreSQL (Port 2400)

PostgreSQL data persists in `data/postgres/` on the host.

**Connection from language containers:**
```bash
# From python-dev, rust-dev, etc.
psql -h postgres -U devuser
```

**Initial database setup:**
Databases are created via `configs/postgres/01-create-dev-dbs.sql`

### Redis

Redis is available as a shared service for caching and data structures.

### Nginx (Port 2403)

Nginx is available as a reverse proxy and web server.

**Configuration:**
- Config files: `configs/nginx/` (mounted to `/etc/nginx/conf.d`)
- Logs: `logs/nginx/` (access and error logs)
- Ports: 80 (HTTP), 443 (HTTPS) exposed on the host

**Example proxy configuration:**
```nginx
# Proxy to a Python backend
location /api/ {
    proxy_pass http://python-dev:8000/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

## Rebuild Guidelines

**When to rebuild:**

| Change Type                     | Command                        |
|---------------------------------|--------------------------------|
| Daily development              | No rebuild needed              |
| Dockerfile modified            | `--rebuild`                    |
| SSH keys changed               | `--rebuild`                    |
| Environment variables changed  | `--rebuild`                    |
| Base images updated            | `--rebuild --no-cache`         |

## Development Workflow

1. **Start containers:** `./scripts/start-virtual.sh all`
2. **Connect via SSH:** `ssh python-dev` or use VSCode Remote-SSH
3. **Work in projects:** All code in `projects/<language>/` persists on host
4. **Stop containers:** `./scripts/shutdown-virtual.sh all` (when done)

**Data Persistence:**
- All code in `projects/` persists on the host
- PostgreSQL data in `data/postgres/` persists across container restarts
- Container state is ephemeral (rebuilds create fresh containers)

## Common Commands

```bash
# Check running containers
docker ps

# View logs for a container
docker logs python-dev
docker logs postgres

# Execute command in running container
docker exec -it python-dev /bin/zsh

# View container resource usage
docker stats
```

## Notes

- Each project under `projects/<language>/` may have its own CLAUDE.md with project-specific guidance
- The VDE provides the infrastructure; individual projects define their own workflows
- All containers share the same Docker network for inter-container communication
- PostgreSQL is accessible from all language containers via hostname `postgres`
