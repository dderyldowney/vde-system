# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Working Directory Constraints

**IMPORTANT:** The working directory for this project is `/Users/dderyldowney/dev`.

When running commands, always assume you are in this directory. Use relative paths from here.

**Allowed directories to access outside the project:**
- `/Users/dderyldowney/.ssh` - For SSH key management
- `/Users/dderyldowney/.claude` - For Claude Code internal files
- `/tmp` - For temporary files

**Do NOT access other directories outside `/Users/dderyldowney/dev` without explicit user request.**

## Session Startup Context

**CRITICAL: Always read session state files first, then explore codebase**

When starting a new session in this project:

1. **Read session state files:**
   - **`SESSION_STATE.md`** - Session progress, test status, work completed
   - **`TODO.md`** - Current tasks, priorities, and pending work

2. **Use available installed plugins**
   - Use available plugins such as claude-mem:go and lyra:lyra

3. **Perform comprehensive codebase examination:**
   - Explore the full codebase structure to understand current implementation
   - Use the Explore agent to get familiar with architecture and patterns
   - Examine key files: scripts/lib/, tests/, configs/
   - Understand the VDE system before making changes

These files track the VDE Test Coverage Improvement project and contain critical context about:
- Current test status (docker-free: 94/94 passing, docker-required: 47/397 passing)
- User Guide integrity requirements
- Tagging system for scenarios
- Next steps and priorities

**Read these files AND explore the codebase BEFORE making any changes to understand what work is in progress.**

## Overview

This is a **Virtual Development Environment (VDE)** - a sophisticated Docker-based container orchestration system providing isolated development environments for multiple programming languages (Python, Rust, JavaScript, C#, Ruby) with shared infrastructure services (PostgreSQL, Redis, MongoDB, Nginx).

**Key Capabilities:**
- Template-based container creation with data-driven configuration
- Automatic SSH setup with agent forwarding for VM-to-VM communication
- Natural language control via AI assistant interface
- Cross-shell compatibility (zsh 5.0+, bash 4.0+, bash 3.x)
- Comprehensive error handling and structured logging

## Architecture

### Container Types

**Language VMs** (SSH ports 2200-2299):
- Each language has its own development container accessible via SSH
- All containers run as `devuser` (non-root) with sudo privileges
- SSH key-based authentication only (password auth disabled)
- Workspace mounted at `/home/devuser/workspace`

**Service VMs** (SSH ports 2400-2499):
- Shared services accessible from all language containers
- Data persisted on host in `data/` directory

**Predefined Language VMs** (19 total, ports 2200-2218):
| Type      | SSH Port | Aliases              | Host Alias    |
|-----------|----------|----------------------|---------------|
| C         | 2200     | c                    | c-dev         |
| C++       | 2201     | cpp, c++, gcc        | cpp-dev       |
| Assembler | 2202     | asm, assembler, nasm | asm-dev       |
| Python    | 2203     | python, python3      | python-dev    |
| Rust      | 2204     | rust                 | rust-dev      |
| JavaScript| 2205     | js, node, nodejs     | js-dev        |
| C#        | 2206     | csharp, dotnet       | csharp-dev    |
| Ruby      | 2207     | ruby                 | ruby-dev      |
| Go        | 2208     | go, golang           | go-dev        |
| Java      | 2209     | java, jdk            | java-dev      |
| Kotlin    | 2210     | kotlin               | kotlin-dev    |
| Swift     | 2211     | swift                | swift-dev     |
| PHP       | 2212     | php                  | php-dev       |
| Scala     | 2213     | scala                | scala-dev     |
| R         | 2214     | r, rlang             | r-dev         |
| Lua       | 2215     | lua                  | lua-dev       |
| Flutter   | 2216     | flutter, dart        | flutter-dev   |
| Elixir    | 2217     | elixir               | elixir-dev    |
| Haskell   | 2218     | haskell, ghc         | haskell-dev   |

**Predefined Service VMs** (7 total, ports 2400-2406):
| Type     | SSH Port | Service Port   | Aliases           |
|----------|----------|----------------|-------------------|
| PostgreSQL| 2400    | 5432           | postgres, postgresql |
| Redis    | 2401     | 6379           | redis             |
| MongoDB  | 2402     | 27017          | mongodb, mongo    |
| Nginx    | 2403     | 80, 443        | nginx             |
| CouchDB  | 2404     | 5984           | couchdb           |
| MySQL    | 2405     | 3306           | mysql             |
| RabbitMQ | 2406     | 5672, 15672    | rabbitmq          |

### Modular Library System

All core functionality is organized under `scripts/lib/`:

| Library        | Purpose                          |
|----------------|----------------------------------|
| `vde-constants`| Centralized config (return codes, ports, timeouts) |
| `vde-shell-compat`| Cross-shell compatibility layer |
| `vde-errors`   | Structured error handling with remediation |
| `vde-log`      | JSON/text/syslog logging with rotation |
| `vde-core`     | Basic VDE operations (VM status, SSH checks) |
| `vm-common`    | Full VM management (Docker, SSH, templates) |
| `vde-commands` | Safe wrapper functions for AI/CLI validation |
| `vde-parser`   | Natural language intent detection |

## Container Management

### Primary Commands

```bash
# Create a new VM (generates docker-compose.yml from template)
./scripts/create-virtual-for <vm-name>

# Start VM(s)
./scripts/start-virtual <vm-name>           # Start specific VM
./scripts/start-virtual all                  # Start all VMs
./scripts/start-virtual python --rebuild     # Rebuild before starting

# Stop VM(s)
./scripts/shutdown-virtual <vm-name>
./scripts/shutdown-virtual all

# List available and running VMs
./scripts/list-vms

# Unified CLI entry point (newer approach)
./scripts/vde <command> [options]
```

### AI Assistant Interface

```bash
# Natural language control (single command)
./scripts/vde-ai "start the python and rust vms"

# Interactive AI chat mode
./scripts/vde-chat
```

**Supported Intents:**
- `list_vms` - List available VMs
- `create_vm` - Create new VMs
- `start_vm`/`stop_vm`/`restart_vm` - Container lifecycle
- `status` - Show running status
- `connect` - Get SSH connection info
- `add_vm_type` - Add new VM types dynamically

### Rebuild Guidelines

| Change Type                     | Command                        |
|---------------------------------|--------------------------------|
| Daily development              | No rebuild needed              |
| Dockerfile modified            | `--rebuild`                    |
| SSH keys changed               | `--rebuild`                    |
| Environment variables changed  | `--rebuild`                    |
| Base images updated            | `--rebuild --no-cache`         |

## SSH Configuration

### Automatic SSH Setup

VDE handles all SSH configuration automatically:
- SSH agent is started and keys are loaded automatically
- SSH keys are detected automatically (ed25519, RSA, ECDSA, DSA)
- SSH key is generated if none exists
- SSH config entries are created automatically
- No manual configuration required

### SSH Agent Forwarding

**VM-to-VM Communication:**
VMs can SSH to each other using your host's SSH keys (private keys never leave the host):
```bash
# From within any VM
ssh python-dev                # SSH to Python VM using host keys
ssh rust-dev pwd              # Run command on Rust VM
scp postgres-dev:/data/file . # Copy from PostgreSQL VM
```

**VM-to-Host Communication:**
Execute commands on host from within any VM via `to-host` wrapper:
```bash
# From within any VM
to-host ls ~/dev              # List host's dev directory
to-host docker ps             # Check host's containers
```

**VM-to-External Communication:**
Use your host's SSH keys for external services:
```bash
# From within any VM
git clone github.com:user/repo  # Uses your GitHub keys
git push origin main
```

**Key Types Supported:**
VDE automatically detects and uses any of these: `id_ed25519`, `id_ecdsa`, `id_rsa`, `id_ecdsa_sk`, `id_ed25519_sk`, `id_dsa`

## Directory Structure

```
$HOME/dev/
├── backup/                     # Configuration backups
│   └── ssh/config             # SSH config template
├── configs/                    # Configuration files
│   ├── docker/                # Docker configurations
│   │   ├── base-dev.Dockerfile # Base image for all dev VMs
│   │   ├── python/            # Language container configs
│   │   ├── rust/
│   │   ├── js/
│   │   ├── csharp/
│   │   ├── ruby/
│   │   ├── go/
│   │   ├── postgres/          # Service container configs
│   │   ├── redis/
│   │   ├── mongodb/
│   │   └── nginx/
│   └── nginx/                 # Nginx reverse proxy configs
├── data/                       # Persistent data volumes
│   ├── postgres/              # PostgreSQL data (persisted)
│   ├── mongodb/               # MongoDB data
│   └── redis/                 # Redis data
├── docs/                       # Complete documentation
│   ├── ARCHITECTURE.md         # System architecture details
│   ├── USER_GUIDE.md           # User guide with BDD scenarios
│   └── API.md                  # Internal API documentation
├── env-files/                  # Environment variable files per VM
├── logs/                       # Application and access logs
│   └── nginx/                 # Nginx access and error logs
├── projects/                   # Project source code (excluded from VDE core)
│   ├── python/                # Python projects
│   ├── rust/                  # Rust projects
│   ├── js/                    # JavaScript projects
│   ├── csharp/                # C# projects
│   ├── ruby/                  # Ruby projects
│   └── go/                    # Go projects
├── public-ssh-keys/           # SSH public keys for containers
├── scripts/                   # Management scripts and libraries
│   ├── lib/                   # Core modular libraries
│   │   ├── vde-constants      # Centralized constants
│   │   ├── vde-shell-compat   # Shell compatibility layer
│   │   ├── vde-errors         # Error handling
│   │   ├── vde-log            # Logging system
│   │   ├── vde-core           # Core operations
│   │   ├── vm-common          # VM management
│   │   ├── vde-commands       # Safe wrappers
│   │   └── vde-parser         # NL parser
│   ├── templates/             # Docker Compose templates
│   │   ├── language-compose.yml.template
│   │   └── service-compose.yml.template
│   ├── data/                  # VM type configuration
│   │   └── vm-types.conf      # Data-driven VM definitions
│   ├── vde                    # Unified CLI entry point
│   ├── create-virtual-for     # Create new VMs
│   ├── start-virtual          # Start VMs
│   ├── shutdown-virtual       # Stop VMs
│   ├── list-vms               # List VMs
│   ├── vde-ai                 # AI command interface
│   └── vde-chat               # Interactive AI chat
└── tests/                     # Comprehensive test suite
    ├── features/              # Behave BDD feature specs
    │   ├── docker-free/       # Fast tests (no Docker required)
    │   └── docker-required/   # Slow tests (Docker VM operations)
    ├── scripts/               # Test utilities
    │   └── generate_user_guide.py  # Auto-generate docs from scenarios
    └── steps/                 # Behave step definitions
```

## Data-Driven Configuration

### VM Types Configuration

VM types are defined in `scripts/data/vm-types.conf` (pipe-delimited format):

```
vm_type|display_name|category|dockerfile_dir|default_ssh_port|service_port|image_prefix
```

**Adding New VM Types:**
Simply add a line to `vm-types.conf` - no code changes required:
```bash
# Example: Add Elixir VM
echo "elixir|Elixir|language|elixir|2206||elixir-dev" >> scripts/data/vm-types.conf
```

### Template System

Docker Compose files are generated from templates in `scripts/templates/`:
- `language-compose.yml.template` - For language VMs
- `service-compose.yml.template` - For service VMs

Templates use placeholder variables that are replaced during VM creation.

## User Model

**All containers use:**
- Username: `devuser`
- Shell: `/bin/zsh` with oh-my-zsh (agnoster theme)
- Editor: `neovim` with LazyVim configuration
- Sudo: Passwordless sudo access
- Authentication: SSH key only
- SSH agent: Forwarded from host for VM-to-VM communication

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

### Redis (Port 2401)

Redis is available as a shared service for caching and data structures.
Data persists in `data/redis/` on the host.

### MongoDB (Port 2402)

MongoDB is available as a document database service.
Data persists in `data/mongodb/` on the host.

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

## Development Workflow

1. **Create VM:** `./scripts/create-virtual-for <vm-name>` (first time only)
2. **Start VMs:** `./scripts/start-virtual all`
3. **Connect:** `ssh python-dev` or use VSCode Remote-SSH
4. **Work:** All code in `projects/<language>/` persists on host
5. **Stop:** `./scripts/shutdown-virtual all` (when done)

**Data Persistence:**
- All code in `projects/` persists on the host
- Service data in `data/` persists across container restarts
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

# List all VMs (available and running)
./scripts/list-vms
```

## Port Allocation

**Language VMs:** Ports 2200-2299 (sequentially allocated)
**Service VMs:** Ports 2400-2499 (sequentially allocated)

Port allocation is managed via a registry system to prevent conflicts. Ports are tracked in `scripts/data/port-registry` and cached for performance.

## Error Handling

All VDE functions return structured exit codes:
- `0` - Success
- `1` - General error
- `2` - VM not found
- `3` - Port conflict
- `4` - Docker error
- `5` - SSH error
- `6` - Permission denied
- `7` - Invalid input

Error messages include remediation suggestions where applicable.

## Logging

The `vde-log` library provides:
- Multiple output formats: JSON, text, syslog
- Log rotation support
- Configurable log levels
- Structured logging with metadata

Logs are written to `logs/vde.log` by default.

## Critical Requirements

### SSH Key Management and Testing Artifacts

**MUST-DO: Clean up test artifacts before committing**

The `public-ssh-keys/` directory must ONLY contain:
- `.keep` - Git tracking file (empty)
- Actual user SSH public keys (id_ed25519.pub, id_rsa.pub, etc.)

**Prohibited in public-ssh-keys/:**
- Test keys (test_id_ed25519, etc.)
- Temporary testing keys
- Private keys (NEVER commit private keys)
- Any keys that don't match the user's actual ~/.ssh/ keys

**Before committing, always verify:**
```bash
# Check what's in public-ssh-keys/
ls -la public-ssh-keys/

# Should only show:
# - .keep (empty file for git tracking)
# - *.pub files matching your actual ~/.ssh/*.pub keys

# If you see test artifacts, remove them:
rm -f public-ssh-keys/test_*
```

**Why this matters:** The Dockerfile reads from `public-ssh-keys/` during container build to populate `authorized_keys`. Test artifacts cause authentication failures and contaminate the SSH key chain.

### SSH Key Synchronization

**MUST-DO: Ensure SSH keys are synchronized before building VMs**

Before running `create-virtual-for` or `start-virtual`, ensure your SSH keys exist and are synchronized:

```bash
# The scripts handle this automatically via ensure_ssh_environment(), but verify:
./scripts/start-virtual <vm-name>  # This calls ensure_ssh_environment automatically
```

If you regenerate your SSH keys, you must:
1. Delete old public keys from `public-ssh-keys/`
2. Run any VDE script (they call `sync_ssh_keys_to_vde()`)
3. Rebuild affected VMs with `--rebuild`

### User Guide Preservation

**CRITICAL: DO NOT break User Guide generation when modifying tests**

The `docs/USER_GUIDE.md` is automatically generated from **passing** BDD scenarios.

**RULES:**
1. **NEVER delete or rename feature files** - Breaks User Guide sections
2. **Preserve scenario titles and structure** - Used as section headers
3. **Maintain scenario context** - Given/When/Then becomes documentation
4. **Keep scenario descriptions intact** - Narrative becomes user-facing docs
5. **Test against User Guide generation** - Verify after modifications

**IMPORTANT: User Guide only includes PASSING scenarios**
- Scenarios without step definitions → NOT in User Guide
- Scenarios that fail → NOT in User Guide
- **Implementing steps EXPANDS User Guide coverage**
- Currently: 47 passing → 47 scenarios documented
- Target: 251 passing → 251 scenarios documented (+204 scenarios to add!)

**Some "duplicates" may be intentional for different user contexts - consider documentation purpose before removing.**

**Before committing test changes:**
```bash
# Verify User Guide still generates correctly
behave --format json --o tests/behave-results.json
python3 tests/scripts/generate_user_guide.py
```

## Testing

The system includes comprehensive BDD tests organized by Docker requirements:

### Test Organization

**Docker-Free Tests (Fast):**
- Location: `tests/features/docker-free/`
- Runner: `./tests/run-bdd-fast.sh`
- Duration: ~1 second
- Status: **94/94 PASSING (100%)**
- Features (5): cache-system, documented-development-workflows, vm-information-and-discovery, natural-language-parser, shell-compatibility

**Docker-Required Tests (Slow):**
- Location: `tests/features/docker-required/`
- Runner: `./tests/run-bdd-tests.sh`
- Duration: Several minutes
- Status: **47/397 passing** (step definitions being implemented)
- Features (26): All VM lifecycle, SSH, configuration, and workflow features

### Running Tests

```bash
# Run fast tests (docker-free only)
./tests/run-bdd-fast.sh

# Run specific docker-free feature
./tests/run-bdd-fast.sh cache-system

# Run all tests (docker-required)
./tests/run-bdd-tests.sh

# Run docker-required tests with @requires-docker-host scenarios (local only)
./tests/run-bdd-tests.sh --include-docker

# Generate User Guide from PASSING scenarios
behave --format json --o tests/behave-results.json
python3 tests/scripts/generate_user_guide.py
```

**Test Levels:**
- Feature Tests: BDD-style Gherkin specifications (Behave)
- Unit Tests: Individual library function tests (if available)
- Integration Tests: End-to-end workflow validation

### @user-guide-* Tagging System

All feature files use explicit tags to control User Guide generation:

```
@user-guide-installation       -> Section 1: Installation
@user-guide-ssh-keys           -> Section 2: SSH Keys
@user-guide-first-vm           -> Section 3: Your First VM
@user-guide-understanding      -> Section 4: Understanding
@user-guide-starting-stopping  -> Section 5: Starting and Stopping
@user-guide-cluster            -> Section 6: Your First Cluster
@user-guide-connecting         -> Section 7: Connecting
@user-guide-databases          -> Section 8: Working with Databases
@user-guide-daily-workflow     -> Section 9: Daily Workflow
@user-guide-more-languages     -> Section 10: Adding More Languages
@user-guide-troubleshooting    -> Section 11: Troubleshooting
@user-guide-internal           -> Excluded from User Guide
```

**Tag Usage Rules:**
- Each feature should have exactly one @user-guide-* tag
- Internal features use @user-guide-internal
- Tags override keyword-based matching in User Guide generator
- When adding features, tag them appropriately for documentation

### User Guide Generation

**CRITICAL:** The User Guide (`docs/USER_GUIDE.md`) is auto-generated from **PASSING** scenarios only.

**How it works:**
1. Run tests with JSON output: `behave --format json --o tests/behave-results.json`
2. Generate guide: `python3 tests/scripts/generate_user_guide.py`
3. Only PASSING scenarios appear in the guide
4. Scenarios without step definitions → NOT in guide
5. Scenarios that fail → NOT in guide

**Implication:** Implementing step definitions EXPANDS User Guide coverage. Currently 47 passing scenarios produce 47 documented scenarios.

### Docker-in-Docker Limitations

**IMPORTANT:** Some scenarios are tagged with `@requires-docker-host` because they cannot run in Docker-in-Docker environments.

**Why:** These scenarios test actual Docker container creation/management. When run inside a test container, inner containers try to mount paths like `/vde/projects/python`, but Docker on the host only knows about host paths like `/Users/dderyldowney/dev/projects/python`.

**Result:** `@requires-docker-host` scenarios:
- **CAN** be run locally with `--include-docker` flag (Docker is available on host)
- **CANNOT** be run in GitHub CI (no Docker-in-Docker support for these operations)
- Must use shell-based integration tests (`tests/integration/*.test.sh`) instead

**Test Architecture:**
- Fast tests (`run-bdd-fast.sh`) run on GitHub CI (docker-free)
- Full tests (`run-bdd-tests.sh` without `--include-docker`) run on GitHub CI (docker-required without host operations)
- Host tests (`run-bdd-tests.sh --include-docker`) run locally only

## Cross-Shell Compatibility

**CRITICAL: VDE scripts must use bash 4.0+ or zsh 5.0+ - NOT sh**

The VDE system uses specific features of bash and zsh that are NOT available in POSIX sh:
- Arrays (bash 4.0+ native, bash 3.x emulated)
- Certain parameter expansions
- Process substitution
- Other shell-specific features

**Supported shells:**
- **zsh 5.0+** - Full support
- **bash 4.0+** - Full support with native arrays
- **bash 3.x** - Fallback support with emulated arrays

**NOT supported:**
- **sh** - Do NOT use `#!/usr/bin/env sh` or `#!/bin/sh` as shebangs

The `vde-shell-compat` library provides a unified interface for shell-specific operations.

### Shell References

**Authoritative Shell Manuals:**
This project uses **Zsh 5.x** as the primary shell, with **Bash 4.x** as a secondary supported shell. The official shell manuals are located at:

- **Zsh 5.x**: `$project_root/docs/shell_manuals/zsh/`
  - `zsh_5_9_us.pdf` - Authoritative PDF reference
  - `zsh_5_9_us.md` - Searchable Markdown version (for AI/human reading)
- **Bash 4.x**: `$project_root/docs/shell_manuals/bash/`
  - `bash_5_3_us.pdf` - Authoritative PDF reference
  - `bash_5_3_us.md` - Searchable Markdown version (for AI/human reading)

The PDFs are the **authoritative references** for writing shell code in this project. Markdown versions are provided for easy searching and AI consumption.

**Script Features:**
The shell scripts in this project leverage advanced features from both shells:
- **Associative arrays** - `typeset -g array_name` (Zsh 5.x & Bash 4.x)
- **Key-value hash maps** - `( $k "${(@)array[@]}"` (Zsh 5.x & Bash 4.x)
- **Pattern matching** - `${var:pattern}` (Zsh 5.x & Bash 4.x)
- **Process substitution** - `${var:pattern}` (Zsh 5.x & Bash 4.x)

**Command / Function / Script Modification Rules**
You MUST triple check every aspect of how a command/function/script works 
before modifying them. You must thoroughly understand how that 
command/function/script operates before modifying it. This can not be overriden.

**Shell Compatibility:**
All scripts MUST use `#!/usr/bin/env zsh` shebang for Zsh scripts.

POSIX compliance is NOT a priority. Use modern shell features that work in both Zsh 5.x and Bash 4.x.

**Resources:**
- **Zsh Guide**: https://zsh.sourceforge.io/Guide/zshguide.pdf
- **Bash Guide**: https://tiswww.tis.org/files/bash/bashref.pdf

## Notes

- Each project under `projects/<language>/` may have its own CLAUDE.md with project-specific guidance
- The VDE provides the infrastructure; individual projects define their own workflows
- All containers share the same Docker network (`vde-network`) for inter-container communication
- PostgreSQL is accessible from all language containers via hostname `postgres`

## Documentation Guidelines

### USER_GUIDE.md Requirements

**CRITICAL:** When generating or modifying USER_GUIDE.md, ALL scenarios MUST show the commands being tested.

Each scenario must include:
1. **The scenario** (Given/When/Then in Gherkin syntax)
2. **The actual command** being tested
3. **The expected output/result**

**Example format:**
```
**Scenario: Verifying VM status**

Given I started my Python VM
When I run "list-vms"
Then I should see which VMs are running
And Python should show as "running"

**Check status:**
```bash
./scripts/list-vms
```

**You should see:**
- python: **running** (on port 2200)
```

This allows users to learn what commands to run directly from the scenarios.

**Script Names (no .sh extension):**
- `./scripts/build-and-start` (not build-and-start-dev.sh)
- `./scripts/start-virtual` (not start-virtual.sh)
- `./scripts/shutdown-virtual` (not shutdown-virtual.sh)
- `./scripts/create-virtual-for` (not create-virtual-for.sh)

### Branding Guidelines

- VDE is for **anyone**, not specific to any single group
- Avoid "ZeroToMastery", "students", or other exclusive language
- Use inclusive terms: "users", "developers", "you"
