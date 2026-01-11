# VDE - Virtual Development Environment

This VDE defines a multi-language Docker-based development environment intended for daily engineering work using SSH and VSCode Remote-SSH.

## Supported Languages/Services

| Language/Service | Port | Description |
|------------------|------|-------------|
| Python 3.14 | 2222 | Python development VM |
| Rust (latest) | 2223 | Rust development VM |
| JavaScript/Node.js | 2224 | JavaScript/Node.js development VM |
| C# | - | C# development VM |
| Ruby | - | Ruby development VM |
| PostgreSQL | 2225 | Shared database VM |
| Redis | - | Redis key-value store |

All containers use a consistent non-root user named `devuser`.

## Directory Structure

```
$HOME/dev
├── backup
│   └── ssh
│       └── config                  SSH config backup (copy to ~/.ssh/config)
├── configs
│   ├── docker
│   │   └── base-dev.Dockerfile     Base image for all dev VMs
│   ├── postgres
│   │   ├── Dockerfile
│   │   ├── docker-compose.yml
│   │   └── 01-create-dev-dbs.sql
│   ├── nginx
│   └── redis
├── data
│   ├── mongodb
│   ├── postgres                    Persistent PostgreSQL data directory
│   └── redis
├── env-files
├── logs
│   ├── access-logs
│   └── app-logs
├── projects
│   ├── c-sharp
│   ├── javascript
│   ├── python
│   ├── ruby
│   ├── rust
├── public-ssh-keys
└── scripts
    ├── build-and-start-dev.sh
    ├── start-virtual.sh
    └── shutdown-virtual.sh
```

### Condensed Version

```
       * backup/ - SSH config backups and Docker state
       * configs/ - Docker configurations per language, PostgreSQL, Redis, nginx
       * data/ - Persistent data directories (MongoDB, PostgreSQL, Redis)
       * env-files/ - Environment variable files for each VM
       * logs/ - Application and access logs
       * projects/ - Project directories mounted into containers
       * public-ssh-keys/ - SSH public keys for container authentication
       * scripts/ - Management scripts (start, shutdown, build)
```

## User Model

Dockerfile for base user is located at: [configs/docker/base-dev.Dockerfile](configs/docker/base-dev.Dockerfile)
Need to modify your user across all virtuals? That's your file.

All containers run as:
- **Username:** devuser
- **Group:** sudo
- **Authentication:** SSH key only
- **Password login:** disabled

This applies to all language VMs and the PostgreSQL VM.

## SSH Key Layout

**Host (Mac): (Example Only - Use your own keyset!**
- Private key: `~/.ssh/id_ed25519`
- Public key copied into containers from: `$HOME/dev/public-ssh-keys/id_ed25519.pub`

**Required permissions:**
```bash
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub
chmod 600 ~/.ssh/config
```

## SSH Configuration

A working SSH config file is stored at: `$HOME/dev/backup/ssh/config`

Copy it to: `~/.ssh/config`

**Example entries:**

```ssh-config
Host python-dev
  HostName localhost
  Port 2222
  User devuser
  IdentityFile ~/.ssh/id_ed25519
  IdentitiesOnly yes

Host rust-dev
  HostName localhost
  Port 2223
  User devuser
  IdentityFile ~/.ssh/id_ed25519
  IdentitiesOnly yes

Host js-dev
  HostName localhost
  Port 2224
  User devuser
  IdentityFile ~/.ssh/id_ed25519
  IdentitiesOnly yes

Host postgres-dev
  HostName localhost
  Port 2225
  User devuser
  IdentityFile ~/.ssh/id_ed25519
  IdentitiesOnly yes
```

These entries work for both command-line SSH and VSCode Remote-SSH.

## PostgreSQL Data Persistence

PostgreSQL database files live on the host at: `$HOME/dev/data/postgres`

This directory is mounted into the container and persists across rebuilds.

Initial database creation is handled by: `configs/postgres/01-create-dev-dbs.sql`

## Command Reference

### Start Containers

```bash
# Start all VMs
./scripts/start-virtual.sh all

# Start specific VM
./scripts/start-virtual.sh python
./scripts/start-virtual.sh rust

# Start with rebuild (rebuilds images)
./scripts/start-virtual.sh rust --rebuild

# Start with full clean rebuild
./scripts/start-virtual.sh rust --rebuild --no-cache
```

### Shutdown Containers

```bash
# Stop all VMs
./scripts/shutdown-virtual.sh all

# Stop specific VM
./scripts/shutdown-virtual.sh postgres
./scripts/shutdown-virtual.sh python
```

### Initial Setup

```bash
# Build and start all VMs (first-time setup)
./scripts/build-and-start-dev.sh

# Rebuild all and start
./scripts/build-and-start-dev.sh --rebuild

# Full clean rebuild and start
./scripts/build-and-start-dev.sh --rebuild --no-cache
```

## Rebuild Guidelines

**No rebuild needed:**
- Daily development
- Restarting containers

**Use `--rebuild` when:**
- Dockerfiles change
- SSH public keys change
- Environment variables change

**Use `--rebuild --no-cache` only when:**
- Base images change
- You want a fully clean rebuild

## VSCode Remote-SSH

1. Install the VSCode Remote-SSH extension
2. Ensure `~/.ssh/config` is installed with correct permissions
3. Connect using host names:
   - `python-dev`
   - `rust-dev`
   - `js-dev`
   - `postgres-dev`

Each container behaves like a lightweight VM suitable for full development workflows.
