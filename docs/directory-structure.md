# Directory Structure

The complete directory layout of a VDE installation.

[← Back to README](../README.md)

---

## Root Structure

```
$HOME/dev/
├── backup/
│   └── ssh/                    # SSH config backups
├── configs/
│   └── docker/
│       ├── base-dev.Dockerfile # Base image for all VMs
│       ├── python/             # Per-VM configs (auto-created)
│       │   └── docker-compose.yml
│       ├── rust/
│       ├── js/
│       └── ...
├── data/                       # Persistent data for services
│   ├── postgres/
│   ├── mongodb/
│   └── redis/
├── docs/                       # Documentation
│   ├── requirements.md
│   ├── quick-start.md
│   ├── command-reference.md
│   └── ...
├── env-files/                  # Environment variables per VM
│   ├── python.env
│   ├── rust.env
│   └── ...
├── logs/                       # Logs per VM
│   ├── python/
│   ├── rust/
│   └── ...
├── projects/                   # Project source code
│   ├── python/
│   ├── rust/
│   ├── js/
│   └── ...
├── public-ssh-keys/            # SSH public keys for containers
├── scripts/
│   ├── lib/
│   │   ├── vm-common           # Shared library
│   │   ├── vde-commands        # Command wrappers
│   │   └── vde-parser          # Natural language parser
│   ├── templates/              # Docker compose templates
│   │   ├── compose-language.yml
│   │   ├── compose-service.yml
│   │   └── ssh-entry.txt
│   ├── data/
│   │   └── vm-types.conf       # VM type definitions
│   ├── list-vms
│   ├── create-virtual-for
│   ├── start-virtual
│   ├── shutdown-virtual
│   ├── build-and-start
│   └── add-vm-type
├── CLAUDE.md
└── README.md
```

---

## Key Directories Explained

### `configs/docker/`

Contains Docker Compose configurations for each VM. Auto-generated when you create a VM.

**Base Image:**
- `base-dev.Dockerfile` - The base image all VMs build from

**Per-VM Configs:**
- `python/docker-compose.yml` - Python container config
- `postgres/docker-compose.yml` - PostgreSQL container config

### `projects/`

Source code for language VMs. Each language VM has its own subdirectory that's mounted into the container at `/home/devuser/workspace`.

```
projects/python/my-api/    # Mounted to python-dev:/home/devuser/workspace
projects/rust/web-service/ # Mounted to rust-dev:/home/devuser/workspace
```

### `data/`

Persistent data for service VMs (databases, caches, etc.).

```
data/postgres/    # PostgreSQL data files
data/redis/       # Redis persistence files
```

### `env-files/`

Environment variables for each VM. These are sourced by Docker Compose when starting containers.

```bash
# python.env example
SSH_PORT=2200
PYTHON_VERSION=3.11
```

### `logs/`

Application logs for each VM.

```
logs/python/    # Python app logs
logs/nginx/     # Nginx access and error logs
```

### `scripts/`

All management scripts and libraries.

| Component | Purpose |
|-----------|---------|
| `lib/vm-common` | Core VM management functions |
| `lib/vde-commands` | Command wrapper functions |
| `lib/vde-parser` | Natural language parser |
| `templates/` | Docker Compose templates |
| `data/vm-types.conf` | VM type definitions |

---

[← Back to README](../README.md)
