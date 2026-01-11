
Development Environment

This directory defines a multi-language Docker-based development environment intended
for daily engineering work using SSH and VSCode Remote-SSH.

Languages and services supported:
- Python 3.14
- Rust (latest)
- JavaScript
- PostgreSQL (shared database VM)

All containers use a consistent non-root user named "devuser".

-----------------------------------------------------------------------

BASE DIRECTORY

All content lives under:

$HOME/dev

This directory is the root of the entire environment.

-----------------------------------------------------------------------

DIRECTORY STRUCTURE

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
│   └── todowrite
└── scripts
    ├── build-and-start-dev.sh
    ├── start-virtual.sh
    └── shutdown-virtual.sh

-----------------------------------------------------------------------

USER MODEL

All containers run as:
- Username: devuser
- Group: sudo
- Authentication: SSH key only
- Password login: disabled

This applies to all language VMs and the PostgreSQL VM.

-----------------------------------------------------------------------

SSH KEY LAYOUT

Host (Mac):
- Private key: ~/.ssh/id_ed25519
- Public key copied into containers from:
  $HOME/dev/public-ssh-keys/id_ed25519.pub

Required permissions:
- chmod 600 ~/.ssh/id_ed25519
- chmod 644 ~/.ssh/id_ed25519.pub
- chmod 600 ~/.ssh/config

-----------------------------------------------------------------------

SSH CONFIGURATION

A working SSH config file is stored at:
$HOME/dev/backup/ssh/config

Copy it to:
~/.ssh/config
Ensure the file permissions above are correct.


Example entries:

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

These entries work for both command-line SSH and VSCode Remote-SSH.

-----------------------------------------------------------------------

POSTGRESQL DATA PERSISTENCE

PostgreSQL database files live on the host at:
$HOME/dev/data/postgres

This directory is mounted into the container and persists across rebuilds.

Initial database creation is handled by:
configs/postgres/01-create-dev-dbs.sql

-----------------------------------------------------------------------

SCRIPTS OVERVIEW

All scripts live in:
$HOME/dev/scripts

build-and-start-dev.sh
- Builds all images
- Starts all containers
- Intended for first-time setup

start-virtual.sh
- Starts containers without rebuilding by default
- Supports optional rebuild flags

Examples:
./scripts/start-virtual.sh all
./scripts/start-virtual.sh python
./scripts/start-virtual.sh rust --rebuild
./scripts/start-virtual.sh rust --rebuild --no-cache

shutdown-virtual.sh
- Stops and removes containers
- Volumes are preserved

Examples:
./scripts/shutdown-virtual.sh all
./scripts/shutdown-virtual.sh postgres

-----------------------------------------------------------------------

REBUILD GUIDELINES

No rebuild needed:
- Daily development
- Restarting containers

Use --rebuild when:
- Dockerfiles change
- SSH public keys change
- Environment variables change

Use --rebuild --no-cache only when:
- Base images change
- You want a fully clean rebuild

-----------------------------------------------------------------------

VSCODE REMOTE-SSH

1. Install the VSCode Remote-SSH extension
2. Ensure ~/.ssh/config is installed with correct permissions
3. Connect using:
   python-dev
   rust-dev
   js-dev
   postgres-dev

Each container behaves like a lightweight VM suitable for full development workflows.

