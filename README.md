# VDE - Virtual Development Environment

A modular, template-based Docker development environment supporting 18+ programming languages and 7+ services, all accessible via SSH with consistent user configuration. Designed for daily development work with VSCode Remote-SSH and AI CLI tools.

## Table of Contents

- [Requirements](#requirements)
- [Quick Start](#quick-start)
- [Available Scripts](#available-scripts)
- [Predefined VM Types](#predefined-vm-types)
- [Command Reference](#command-reference)
- [Extending VDE](#extending-vde)
  - [Understanding VDE Architecture](#understanding-vde-architecture)
  - [Adding New Languages](#adding-new-languages)
  - [Adding New Services](#adding-new-services)
  - [Advanced Extension Patterns](#advanced-extension-patterns)
- [SSH Configuration](#ssh-configuration)
- [VSCode Remote-SSH](#vscode-remote-ssh)
- [AI CLI Integration](#ai-cli-integration)
  - [Claude Code Deep Dive](#claude-code-deep-dive)
  - [Other AI CLI Tools](#other-ai-cli-tools)
- [Development Workflows](#development-workflows)
- [Directory Structure](#directory-structure)
- [User Model](#user-model)
- [Troubleshooting](#troubleshooting)
- [Architecture](#architecture)

---

## Requirements

**Shell:** `zsh 5.0+` (for associative array support)

To check your version:
```bash
zsh --version
```

If you're on macOS with an older bash, these scripts use zsh which ships with macOS. If you're on Linux, you may need to install zsh:
```bash
# Ubuntu/Debian
sudo apt-get install zsh

# macOS (already installed)
brew install zsh
```

**Other Requirements:**
- Docker Desktop or Docker Engine
- docker-compose
- SSH key pair (`id_ed25519` or `id_rsa`)

---

## Quick Start

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

## Available Scripts

| Script | Purpose |
|--------|---------|
| `list-vms` | List all predefined languages and services |
| `create-virtual-for` | Create a new language or service VM |
| `start-virtual` | Start one or more VMs |
| `shutdown-virtual` | Stop one or more VMs |
| `build-and-start` | Shutdown all, then start all VMs with optional rebuild |
| `add-vm-type` | Add a new language or service to the predefined list |

---

## Predefined VM Types

### Language VMs (18 total, ports 2200-2299)

| Name | Aliases | Display Name | Container Name | SSH Host | Install Command |
|------|---------|--------------|----------------|----------|-----------------|
| c | c | C | c-dev | c-dev | gcc, make, cmake, gdb |
| cpp | c++, gcc | C++ | cpp-dev | cpp-dev | g++, make, cmake, gdb |
| asm | assembler, nasm | Assembler | asm-dev | asm-dev | nasm, yasm, gdb |
| python | python3 | Python | python-dev | python-dev | python3, python3-pip |
| rust | rust | Rust | rust-dev | rust-dev | rustup (via install script) |
| js | node, nodejs | JavaScript | js-dev | js-dev | Node.js LTS |
| csharp | dotnet | C# | csharp-dev | csharp-dev | dotnet-sdk-8.0 |
| ruby | ruby | Ruby | ruby-dev | ruby-dev | ruby-full |
| go | golang | Go | go-dev | go-dev | golang-go |
| java | jdk | Java | java-dev | java-dev | default-jdk, maven, gradle |
| kotlin | kotlin | Kotlin | kotlin-dev | kotlin-dev | kotlin, SDKMAN |
| swift | swift | Swift | swift-dev | swift-dev | binutils, git, libc6-dev, curl |
| php | php | PHP | php-dev | php-dev | php, php-cli, composer |
| scala | scala | Scala | scala-dev | scala-dev | scala-defaults, sbt |
| r | rlang, r | R | r-dev | r-dev | r-base, r-cran-littler |
| lua | lua | Lua | lua-dev | lua-dev | lua5.4, luarocks |
| flutter | dart, flutter | Flutter | flutter-dev | flutter-dev | flutter SDK |
| elixir | elixir | Elixir | elixir-dev | elixir-dev | elixir, erlang |
| haskell | ghc, haskell | Haskell | haskell-dev | haskell-dev | ghc, cabal-install |

### Service VMs (7 total, ports 2400-2499)

| Name | Aliases | Display Name | Container Name | SSH Host | Service Port | Purpose |
|------|---------|--------------|----------------|----------|--------------|---------|
| postgres | postgresql | PostgreSQL | postgres | postgres | 5432 | PostgreSQL database |
| redis | redis | Redis | redis | redis | 6379 | Key-value store |
| mongodb | mongo | MongoDB | mongodb | mongodb | 27017 | Document database |
| nginx | nginx | Nginx | nginx | nginx | 80, 443 | Web server |
| couchdb | couchdb | CouchDB | couchdb | couchdb | 5984 | NoSQL database |
| mysql | mysql | MySQL | mysql | mysql | 3306 | MySQL database |
| rabbitmq | rabbitmq | RabbitMQ | rabbitmq | rabbitmq | 5672, 15672 | Message queue |

---

## Command Reference

### List Available VMs

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

### Create New VMs

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

**What `create-virtual-for` does:**
1. Validates the VM name exists in predefined list
2. Auto-allocates SSH port (2200-2299 for languages, 2400-2499 for services)
3. Creates `configs/docker/<name>/docker-compose.yml` from template
4. Creates directories: `projects/<name>/` or `data/<name>/`, `logs/<name>/`
5. Creates `env-files/<name>.env`
6. Adds SSH config entry to `~/.ssh/config` (with backup)

### Start VMs

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

### Stop VMs

```bash
# Stop single VM
./scripts/shutdown-virtual python

# Stop multiple VMs
./scripts/shutdown-virtual python go rust

# Stop all VMs
./scripts/shutdown-virtual all
```

### Build and Start All VMs

```bash
# Shutdown all, then start all
./scripts/build-and-start

# With rebuild
./scripts/build-and-start --rebuild

# With full clean rebuild
./scripts/build-and-start --rebuild --no-cache
```

### Add New VM Types

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

## Extending VDE

VDE is designed to be easily extensible. You can add support for new programming languages, new services, or customize existing ones without modifying any scripts. The entire system is data-driven through configuration files and templates.

### Understanding VDE Architecture

Before extending VDE, it helps to understand how it works:

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Request                            │
│                    ./create-virtual-for zig                     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  vm-common (Shared Library)                     │
│  • Parses vm-types.conf                                         │
│  • Resolves aliases (ziglang → zig)                             │
│  • Allocates SSH port (2200-2299 for lang)                      │
│  • Validates configuration                                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Template Rendering                          │
│  • Reads templates/compose-language.yml                         │
│  • Substitutes: {{NAME}}, {{SSH_PORT}}, {{INSTALL_CMD}}        │
│  • Writes to: configs/docker/<name>/docker-compose.yml          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      File Creation                              │
│  • configs/docker/<name>/docker-compose.yml                     │
│  • env-files/<name>.env                                         │
│  • projects/<name>/ (or data/<name>/ for services)              │
│  • logs/<name>/                                                 │
│  • ~/.ssh/config (appends entry)                                │
└─────────────────────────────────────────────────────────────────┘
```

**Key Files:**

| File | Purpose | Edit to Extend |
|------|---------|----------------|
| `data/vm-types.conf` | Defines all VM types | ✅ **Yes** - Add new entries |
| `templates/compose-language.yml` | Language VM template | Rarely - only for structural changes |
| `templates/compose-service.yml` | Service VM template | Rarely - only for structural changes |
| `templates/ssh-entry.txt` | SSH config template | Rarely - only for format changes |
| `lib/vm-common` | Core functions | Never - use templates/config instead |

**vm-types.conf Format:**
```
type|name|aliases|display_name|install_command|service_port
```

| Field | Description | Example |
|-------|-------------|---------|
| `type` | `lang` or `service` | `lang` |
| `name` | Primary name (lowercase, alphanumeric) | `zig` |
| `aliases` | Comma-separated alternate names | `ziglang,z` |
| `display_name` | Human-readable name | `Zig` |
| `install_command` | Shell command to install | `apt-get update -y && apt-get install -y zig` |
| `service_port` | Port number (services only, empty for lang) | `5432` |

### Adding New Languages

Adding a new programming language to VDE is a two-step process:

#### Step 1: Add to vm-types.conf

You can do this manually or with the `add-vm-type` script.

**Option A: Using add-vm-type (Recommended)**

```bash
# Basic language addition
./scripts/add-vm-type zig \
    "apt-get update -y && apt-get install -y zig"

# With aliases
./scripts/add-vm-type zig \
    "apt-get update -y && apt-get install -y zig" \
    "ziglang,z"

# With custom display name
./scripts/add-vm-type --display "Zig Language" zig \
    "apt-get update -y && apt-get install -y zig"
```

**Option B: Manual Entry**

Edit `data/vm-types.conf` and add a line:

```bash
# Format: lang|name|aliases|display|install|service_port
lang|zig|ziglang,z|Zig|apt-get update -y && apt-get install -y zig|
```

**Important:** For languages, the `service_port` field must be empty (just a trailing `|`).

#### Step 2: Create the VM

```bash
# Create the Zig VM
./scripts/create-virtual-for zig

# Verify it was created
./scripts/list-vms zig

# Start the VM
./scripts/start-virtual zig

# Connect
ssh zig-dev
```

**What gets created:**

```
configs/docker/zig/
└── docker-compose.yml     # Container: zig-dev, SSH: zig-dev

env-files/
└── zig.env                 # SSH_PORT=2205 (or next available)

projects/zig/               # Empty workspace directory

logs/zig/                   # Empty log directory

~/.ssh/config               # New entry appended:
                            # Host zig-dev
                            #     HostName localhost
                            #     Port 2205
                            #     User devuser
                            #     IdentityFile ~/.ssh/id_ed25519
                            #     IdentitiesOnly yes
```

#### Language Installation Best Practices

**Simple apt packages:**
```bash
./scripts/add-vm-type zig \
    "apt-get update -y && apt-get install -y zig"
```

**Language version managers:**
```bash
# Using SDKMAN (for Java/Kotlin/scala variants)
./scripts/add-vm-type gradle \
    "apt-get update -y && apt-get install -y curl && \
     su devuser -c 'curl -s \"https://get.sdkman.io\" | bash' && \
     su devuser -c 'source ~/.sdkman/bin/sdkman-init.sh && sdk install gradle'"

# Using asdf (multi-language version manager)
./scripts/add-vm-type terraform \
    "apt-get update -y && apt-get install -y curl git && \
     su devuser -c 'git clone https://github.com/asdf-vm/asdf.git ~/.asdf --depth 1' && \
     su devuser -c '~/.asdf/bin/asdf plugin-add terraform && \
                      ~/.asdf/bin/asdf install terraform latest'"
```

**Download and install from URL:**
```bash
# Download binary, extract, symlink
./scripts/add-vm-type zig \
    "apt-get update -y && apt-get install -y xz-utils wget && \
     wget https://ziglang.org/download/0.11.0/zig-linux-x86_64-0.11.0.tar.xz -O /tmp/zig.tar.xz && \
     tar -xf /tmp/zig.tar.xz -C /tmp && \
     mv /tmp/zig-linux-x86_64-0.11.0 /opt/zig && \
     ln -s /opt/zig/zig /usr/local/bin/zig && \
     rm /tmp/zig.tar.xz"
```

**Install as devuser (for user-scoped tools):**
```bash
# Rust-style installers
./scripts/add-vm-type rust \
    "su devuser -c 'curl --proto =https --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y'"

# Node.js via nvm
./scripts/add-vm-type node \
    "apt-get update -y && apt-get install -y curl && \
     su devuser -c 'curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash' && \
     su devuser -c 'export NVM_DIR=\"\$HOME/.nvm\" && \
                      [ -s \"\$NVM_DIR/nvm.sh\" ] && \\. \"\$NVM_DIR/nvm.sh\" && \
                      nvm install --lts'"
```

### Adding New Services

Adding a service (database, cache, message queue, etc.) is similar to adding a language, with the additional requirement of specifying the service port.

#### Step 1: Add to vm-types.conf

**Option A: Using add-vm-type (Recommended)**

```bash
# Basic service (single port)
./scripts/add-vm-type --type service --svc-port 5672 rabbitmq \
    "apt-get update -y && apt-get install -y rabbitmq-server"

# With aliases
./scripts/add-vm-type --type service --svc-port 5672 rabbitmq \
    "apt-get update -y && apt-get install -y rabbitmq-server" \
    "rabbit,rabbitmq-server"

# Multiple ports (comma-separated)
./scripts/add-vm-type --type service --svc-port 5672,15672 rabbitmq \
    "apt-get update -y && apt-get install -y rabbitmq-server" \
    "rabbit"
```

**Option B: Manual Entry**

Edit `data/vm-types.conf` and add a line:

```bash
# Format: service|name|aliases|display|install|service_port
service|rabbitmq|rabbit,rabbitmq-server|RabbitMQ|apt-get update -y && apt-get install -y rabbitmq-server|5672,15672
```

**Important:** For services, the `service_port` field is **required**.

#### Step 2: Create the Service VM

```bash
# Create the RabbitMQ VM
./scripts/create-virtual-for rabbitmq

# Verify it was created
./scripts/list-vms --svc rabbitmq

# Start the VM
./scripts/start-virtual rabbitmq

# Connect
ssh rabbitmq
```

**What gets created (different from languages):**

```
configs/docker/rabbitmq/
└── docker-compose.yml     # Container: rabbitmq (no -dev suffix)
                            # Ports: SSH_PORT:22, 5672:5672, 15672:15672

env-files/
└── rabbitmq.env           # SSH_PORT=2405 (or next available)

data/rabbitmq/              # Persistent data directory (not projects/)
logs/rabbitmq/              # Empty log directory

~/.ssh/config               # New entry appended:
                            # Host rabbitmq
                            #     HostName localhost
                            #     Port 2405
                            #     User devuser
                            #     IdentityFile ~/.ssh/id_ed25519
                            #     IdentitiesOnly yes
```

**Key Differences: Language vs Service VMs**

| Aspect | Language VM | Service VM |
|--------|-------------|------------|
| Container name | `<name>-dev` | `<name>` |
| SSH config | `<name>-dev` | `<name>` |
| Port range | 2200-2299 | 2400-2499 |
| Volume mount | `projects/<name>/` | `data/<name>/` |
| Purpose | Development workspace | Persistent data |
| Example | `zig-dev`, port 2205 | `rabbitmq`, port 2405 |

#### Service Installation Examples

**Database with client tools only:**
```bash
# PostgreSQL client (connects to external Postgres)
./scripts/add-vm-type --type service --svc-port 5432 postgres-client \
    "apt-get update -y && apt-get install -y postgresql-client"
```

**Full database server:**
```bash
# MySQL server
./scripts/add-vm-type --type service --svc-port 3306 mysql \
    "apt-get update -y && apt-get install -y default-mysql-server && \
     service mysql start"

# MongoDB
./scripts/add-vm-type --type service --svc-port 27017 mongodb \
    "apt-get update -y && apt-get install -y mongodb-org && \
     service mongod start"
```

**Message queue:**
```bash
# RabbitMQ
./scripts/add-vm-type --type service --svc-port 5672,15672 rabbitmq \
    "apt-get update -y && apt-get install -y erlang-nox && \
     wget https://github.com/rabbitmq/rabbitmq-server/releases/download/v3.12/rabbitmq-server_3.12-1_all.deb && \
     dpkg -i rabbitmq-server_3.12-1_all.deb && \
     service rabbitmq-server start"
```

**Web server:**
```bash
# Nginx with HTTP and HTTPS
./scripts/add-vm-type --type service --svc-port 80,443 nginx \
    "apt-get update -y && apt-get install -y nginx-extras && \
     service nginx start"
```

**Cache server:**
```bash
# Memcached
./scripts/add-vm-type --type service --svc-port 11211 memcached \
    "apt-get update -y && apt-get install -y memcached && \
     service memcached start"
```

### Advanced Extension Patterns

#### Custom Container Names

By default, language VMs get a `-dev` suffix. To customize this, edit the templates:

**Edit `templates/compose-language.yml`:**
```yaml
# Change container_name from {{NAME}}-dev to your preferred pattern
container_name: {{NAME}}-workspace  # or just {{NAME}}
```

**Edit `templates/ssh-entry.txt`:**
```ssh
# Update the Host entry to match
Host {{HOST}}  # Pass a custom HOST variable during creation
```

#### Multi-Language Images

For languages that work together (e.g., TypeScript + JavaScript), you can create composite VMs:

```bash
# Add TypeScript as an alias of JavaScript (same VM)
# In vm-types.conf:
lang|js|node,nodejs,typescript|JavaScript|apt-get update && curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - && apt-get install -y nodejs && npm install -g typescript|

# Now both create the same VM:
./scripts/create-virtual-for js
./scripts/create-virtual-for typescript  # Creates the same VM
```

#### Custom Base Images

If a language needs a different base OS:

1. Create a new Dockerfile: `configs/docker/custom-base.Dockerfile`
2. Modify the template to use it:

**Edit `templates/compose-language.yml`:**
```yaml
services:
  {{NAME}}-dev:
    build:
      context: ../../..
      dockerfile: configs/docker/custom-base.Dockerfile  # Changed from base-dev
```

#### Environment-Specific Installations

Install different tools based on environment variables:

```bash
./scripts/add-vm-type python \
    "apt-get update -y && apt-get install -y python3 python3-pip && \
     if [ \"\${VDE_PYTHON_VERSION:-latest}\" = \"3.11\" ]; then \
       apt-get install -y python3.11 python3.11-venv; \
     else \
       apt-get install -y python3.12 python3.12-venv; \
     fi"
```

Then in `env-files/python.env`:
```bash
VDE_PYTHON_VERSION=3.11
```

#### Post-Installation Scripts

For complex setups, you can add a post-install script:

```bash
./scripts/add-vm-type dotnet \
    "apt-get update -y && apt-get install -y wget apt-transport-https && \
     wget https://packages.microsoft.com/config/debian/12/packages-microsoft-prod.deb -O /tmp/packages-microsoft-prod.deb && \
     dpkg -i /tmp/packages-microsoft-prod.deb && rm /tmp/packages-microsoft-prod.deb && \
     apt-get update -y && apt-get install -y dotnet-sdk-8.0 aspnetcore-runtime-8.0 && \
     # Post-install: Enable global tools
     su devuser -c 'dotnet tool install --global dotnet-format'"
```

#### Validation and Testing

After adding a new language or service, validate it:

```bash
# 1. Verify it appears in the list
./scripts/list-vms <name>

# 2. Create the VM
./scripts/create-virtual-for <name>

# 3. Check the generated files
cat configs/docker/<name>/docker-compose.yml
cat env-files/<name>.env
cat ~/.ssh/config | grep -A 5 "<name>"

# 4. Start the VM
./scripts/start-virtual <name>

# 5. Verify container is running
docker ps | grep <name>

# 6. Connect and test the installation
ssh <name>
<test the language or service>

# 7. Verify service port (if applicable)
docker port <name>
```

---

## SSH Configuration

All VMs use SSH key-based authentication. The `create-virtual-for` script automatically adds entries to `~/.ssh/config`.

### Manual Setup

If you need to manually configure SSH:

1. **Generate SSH keys** (if you don't have them):
```bash
ssh-keygen -t ed25519
```

2. **Copy public key for containers:**
```bash
cp ~/.ssh/id_ed25519.pub ~/dev/public-ssh-keys/
```

3. **Set correct permissions:**
```bash
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub
chmod 600 ~/.ssh/config
```

4. **Add SSH config entry** (example for `go-dev`):
```ssh-config
# Go Dev VM
Host go-dev
    HostName localhost
    Port 2205
    User devuser
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
```

### Connecting via SSH

```bash
# Connect to language VM
ssh go-dev
ssh python-dev
ssh rust-dev

# Connect to service VM
ssh postgres
ssh redis
ssh mongodb
```

### SSH from Within Containers

All containers share the `dev-net` Docker network, so they can communicate with each other:

```bash
# From python-dev, connect to postgres
ssh postgres
psql -h localhost -U devuser
```

---

## VSCode Remote-SSH

### Setup

1. Install the [Remote-SSH extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-ssh)

2. Press `Cmd+Shift+P` (macOS) or `Ctrl+Shift+P` (Windows/Linux)

3. Type "Remote-SSH: Connect to Host"

4. Select your VM (e.g., `python-dev`, `rust-dev`, `postgres`)

### Recommended VSCode Extensions

Install these extensions inside your VMs for the best experience:

**Language-Specific:**
- Python: Python, Pylance
- Rust: rust-analyzer
- Go: Go
- JavaScript/TypeScript: ESLint, Prettier
- C/C++: C/C++
- Java: Extension Pack for Java

**General:**
- GitLens
- Docker
- Remote - SSH
- Remote - SSH: Editing Configuration Files

### VSCode Workflow

1. **Connect** to VM via Remote-SSH
2. **Open** your project: `File > Open Folder > /home/devuser/workspace`
3. **Edit** files with full IDE support
4. **Run** tests using the integrated terminal
5. **Debug** using VSCode's debugger

---

## AI CLI Integration

VDE is designed to work seamlessly with AI-powered CLI tools. These tools can help you write code faster, debug issues, and understand your codebase - all while respecting the VDE architecture.

### Claude Code Deep Dive

Claude Code (Anthropic's CLI coding assistant) has excellent integration with VDE. This section provides a comprehensive guide to using Claude Code effectively with your VDE setup.

#### Understanding Claude Code + VDE Integration

There are **three main patterns** for using Claude Code with VDE:

```
┌─────────────────────────────────────────────────────────────────────┐
│ Pattern 1: Host-Based (Recommended for Most Use Cases)              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   Host Machine          SSH              VDE Container               │
│  ┌──────────┐         ┌──────┐         ┌──────────┐                │
│  │ Claude   │ ──────> │ :2222│ ──────> │ python-dev│               │
│  │  Code    │  edit  │      │  run    │          │                │
│  │          │ files  │      │ commands│          │                │
│  └──────────┘         └──────┘         └──────────┘                │
│                                                                     │
│  ✓ Claude edits files directly on host                              │
│  ✓ Claude runs commands via SSH                                     │
│  ✓ Best for: Most development work                                 │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ Pattern 2: Container-Based (VSCode Remote-SSH)                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   VDE Container (connected via VSCode Remote-SSH)                   │
│  ┌──────────────────────────────────────────┐                      │
│  │ VSCode ──────────────────> Claude Code    │                      │
│  │  │                    ──>  (npx)          │                      │
│  │  │                                      │                      │
│  │  └──> Integrated Terminal                │                      │
│  └──────────────────────────────────────────┘                      │
│                                                                     │
│  ✓ Claude runs inside the container                                 │
│  ✓ Direct access to all language tools                             │
│  ✓ Best for: Large codebases, complex debugging                    │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ Pattern 3: Hybrid (Advanced)                                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Run Claude on host, but use it to manage multiple containers       │
│                                                                     │
│  Host: claude                                                       │
│    └─> "Start the python-dev container"                             │
│    └─> "Run tests in python-dev"                                    │
│    └─> "Check postgres logs"                                        │
│    └─> "Build the rust service"                                     │
│                                                                     │
│  ✓ Best for: Multi-service architectures, microservices            │
└─────────────────────────────────────────────────────────────────────┘
```

#### Pattern 1: Host-Based Claude Code (Recommended)

This is the **most common pattern**. Claude Code runs on your host machine and interacts with VDE containers via SSH.

**Setup:**

```bash
# 1. Navigate to your project directory (on host)
cd ~/dev/projects/python/my-api

# 2. Start Claude Code
claude

# Or if installed via npx
npx @anthropics/claude-code
```

**Configuration:**

Create a `.claude/project.md` file in your project directory:

```markdown
# VDE Python API Project

This is a FastAPI project running in the VDE python-dev container.

## VM Information
- **SSH Host**: `python-dev` (localhost:2222)
- **Container Name**: `python-dev`
- **Project Path**: `/home/devuser/workspace` (mounted from `~/dev/projects/python/`)
- **Host Path**: `~/dev/projects/python/my-api/`

## Available Services
- **PostgreSQL**: Host `postgres`, Port 5432, User `devuser`
  - Connect: `ssh postgres "psql -h localhost -U devuser"`
  - From container: `psql -h postgres -U devuser`

- **Redis**: Host `redis`, Port 6379
  - Connect: `ssh redis "redis-cli -h localhost"`
  - From container: `redis-cli -h redis`

## Development Commands
All commands should be run via SSH in the python-dev container:

**Environment Setup:**
```bash
ssh python-dev "cd ~/workspace && source .venv/bin/activate"
```

**Run Tests:**
```bash
ssh python-dev "cd ~/workspace && pytest"
```

**Run Server:**
```bash
ssh python-dev "cd ~/workspace && uvicorn main:app --reload --host 0.0.0.0"
```

**Install Dependencies:**
```bash
ssh python-dev "cd ~/workspace && pip install -r requirements.txt"
```

**Code Quality:**
```bash
ssh python-dev "cd ~/workspace && ruff check ."
ssh python-dev "cd ~/workspace && mypy ."
```

## Project Structure
```
.
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI app entry point
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints.py
│   │       └── models.py
│   ├── core/
│   │   ├── config.py     # Settings from environment
│   │   └── security.py
│   └── db/
│       ├── session.py    # Database session
│       └── models.py     # SQLAlchemy models
├── tests/
│   ├── test_api.py
│   └── test_db.py
├── .venv/                # Virtual environment
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Important Notes for Claude
1. **Always run commands via SSH** when executing in the container
2. **Files are edited on the host** - Claude can edit directly
3. **Use absolute paths** when running commands via SSH
4. **Services are accessible via Docker network** - use service names as hostnames
5. **Data persists on the host** in `~/dev/` directories
```

**Example Session:**

```bash
# On your host machine
cd ~/dev/projects/python/my-api
claude
```

```
# Inside Claude Code:

You: Create a new FastAPI endpoint for user registration

Claude: I'll create a user registration endpoint. Let me:
1. Add the User model
2. Create the registration endpoint
3. Add input validation
4. Create tests

[Creates files on host, shows preview]

You: Run the tests in the python-dev container

Claude: [Running tests via SSH]
ssh python-dev "cd ~/workspace && pytest tests/test_api.py -v"

[Shows test output]

You: One test is failing. Fix it.

Claude: The failing test is checking for a 201 status code but we're returning 200.
Let me fix that...

[Edits main.py on host]

You: Now add a Redis cache layer for user lookups

Claude: I'll add Redis caching. First, let me install the Redis client:
ssh python-dev "cd ~/workspace && pip install redis"

[Adds caching logic, creates cache utility module]

You: Check if the redis container is running

Claude: [Checking]
docker ps | grep redis

The redis container is running on port 2498.

You: Connect to postgres and create the users table

Claude: I'll create the table by running migrations:
ssh python-dev "cd ~/workspace && alembic upgrade head"

Then I'll verify the table was created:
ssh postgres "psql -h localhost -U devuser -d mydb -c '\dt users'"
```

**Best Practices for Host-Based Pattern:**

1. **Use SSH for all container commands**:
   ```bash
   # Good
   ssh python-dev "pytest"

   # Bad (requires entering container first)
   ssh python-dev
   pytest
   ```

2. **Quote complex commands**:
   ```bash
   ssh python-dev "cd ~/workspace && source .venv/bin/activate && pytest"
   ```

3. **Use project.md for context**:
   - Keep it updated with your current commands
   - Document service dependencies
   - Include common workflows

4. **Leverage Claude's file editing**:
   - Claude edits files directly on the host
   - Changes are immediately visible in the container (via volume mount)
   - No need to copy files back and forth

#### Pattern 2: Container-Based Claude Code

Run Claude Code inside the container for maximum tool access.

**Setup:**

```bash
# 1. Connect via VSCode Remote-SSH
# In VSCode: Cmd+Shift+P > "Remote-SSH: Connect to Host" > python-dev

# 2. Open the integrated terminal in VSCode

# 3. Navigate to workspace
cd ~/workspace

# 4. Start Claude Code
npx @anthropics/claude-code
```

**When to Use This Pattern:**

- Large codebases where network latency matters
- When you need direct access to language tools (type checkers, linters)
- Debugging complex issues that require multiple tool runs
- When working offline or with limited host resources

**Example Session:**

```bash
# Inside the container, connected via VSCode Remote-SSH
cd ~/workspace
npx @anthropics/claude-code
```

```
# Inside Claude Code:

You: Run the type checker and fix any errors

Claude: [Running mypy directly in the container]
mypy app/.

[Shows type errors, fixes them in real-time]

You: Create a new migration for the orders table

Claude: [Using alembic installed in the container]
alembic revision --autogenerate -m "Add orders table"

[Creates migration file]

You: Apply the migration

Claude: alembic upgrade head
[Successfully applied migration]
```

#### Pattern 3: Multi-Container Management

Use Claude Code on the host to manage a microservices architecture.

**Setup:**

```bash
# On host, in the monorepo root
cd ~/dev
claude
```

**Example `.claude/project.md` for Monorepo:**

```markdown
# VDE Microservices Monorepo

This is a microservices application using multiple VDE containers.

## Services Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│  API Gateway│ ───> │  User Svc    │ ───> │  PostgreSQL │
│  (Python)   │      │  (Go)        │      │             │
└─────────────┘      └──────────────┘      └─────────────┘
       │                    │
       ▼                    ▼
┌─────────────┐      ┌──────────────┐
│   Redis     │ ◀─── │  Analytics   │
│             │      │  (Rust)      │
└─────────────┘      └──────────────┘
```

## Container Management

**Start all services:**
```bash
./scripts/start-virtual python go rust postgres redis
```

**Stop all services:**
```bash
./scripts/shutdown-virtual python go rust postgres redis
```

**View logs:**
```bash
docker logs python-dev
docker logs go-dev
docker logs rust-dev
docker logs postgres
docker logs redis
```

## Service-Specific Commands

**API Gateway (Python):**
```bash
ssh python-dev "cd ~/workspace && uvicorn main:app --reload"
ssh python-dev "cd ~/workspace && pytest"
```

**User Service (Go):**
```bash
ssh go-dev "cd ~/workspace && go run main.go"
ssh go-dev "cd ~/workspace && go test ./..."
```

**Analytics Service (Rust):**
```bash
ssh rust-dev "cd ~/workspace && cargo run"
ssh rust-dev "cd ~/workspace && cargo test"
```

**PostgreSQL:**
```bash
ssh postgres "createdb analytics"
ssh postgres "psql -h localhost -U devuser -d analytics"
```

**Redis:**
```bash
ssh redis "redis-cli FLUSHALL"
ssh redis "redis-cli KEYS '*'"
```
```

**Example Session:**

```
# Inside Claude Code:

You: Start all the services

Claude: [Starting services]
./scripts/start-virtual python go rust postgres redis

[Waiting for containers to be ready...]
All services started successfully.

You: Check if all services are healthy

Claude: [Checking service health]
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

[Shows all services running]

You: The user service is failing to connect to the database. Investigate.

Claude: [Checking go-dev logs]
docker logs go-dev --tail 50

I see connection errors. Let me check if postgres is accepting connections:
ssh postgres "pg_isready"

Postgres is ready. The issue might be the connection string. Let me check:
ssh go-dev "cat ~/workspace/config/database.yaml"

The hostname is set to 'localhost' but should be 'postgres' (the Docker service name).
Let me fix that...

[Edits the config file]

You: Restart the user service

Claude: ./scripts/shutdown-virtual go && ./scripts/start-virtual go

Service restarted. Checking logs...
docker logs go-dev --tail 20

Connection successful!
```

#### Advanced Claude Code + VDE Patterns

**1. CI/CD Integration:**

```bash
# Create a test script that Claude can use
cat > ~/dev/scripts/test-all.sh << 'EOF'
#!/bin/bash
set -e

echo "Testing Python API..."
ssh python-dev "cd ~/workspace && pytest"

echo "Testing Go service..."
ssh go-dev "cd ~/workspace && go test ./..."

echo "Testing Rust service..."
ssh rust-dev "cd ~/workspace && cargo test"

echo "All tests passed!"
EOF

chmod +x ~/dev/scripts/test-all.sh
```

Now Claude can run all tests with:
```bash
./scripts/test-all.sh
```

**2. Database Seeding:**

```bash
# Create seed scripts for each environment
cat > ~/dev/scripts/seed-db.sh << 'EOF'
#!/bin/bash

echo "Seeding database..."

# Create database
ssh postgres "createdb devdb || true"

# Run migrations
ssh python-dev "cd ~/workspace && alembic upgrade head"

# Seed data
ssh python-dev "cd ~/workspace && python scripts/seed.py"

echo "Database seeded!"
EOF

chmod +x ~/dev/scripts/seed-db.sh
```

**3. Service Dependency Management:**

Create a `.claude/deps.md` file:

```markdown
# Service Dependencies

## Startup Order
1. postgres (database)
2. redis (cache)
3. go-dev (user service - depends on postgres)
4. rust-dev (analytics - depends on postgres, redis)
5. python-dev (API gateway - depends on all above)

## Health Checks

**PostgreSQL:**
```bash
ssh postgres "pg_isready"
```

**Redis:**
```bash
ssh redis "redis-cli ping"
```

**User Service:**
```bash
curl http://localhost:8001/health
```

**Analytics Service:**
```bash
curl http://localhost:8002/health
```

**API Gateway:**
```bash
curl http://localhost:8000/health
```
```

**4. Automated Workflows:**

Create a `Makefile` that Claude can use:

```makefile
# VDE Makefile for Claude Code

.PHONY: test build start stop clean

start:
	./scripts/start-virtual python go rust postgres redis

stop:
	./scripts/shutdown-virtual python go rust postgres redis

restart: stop start

test:
	@echo "Running all tests..."
	ssh python-dev "cd ~/workspace && pytest"
	ssh go-dev "cd ~/workspace && go test ./..."
	ssh rust-dev "cd ~/workspace && cargo test"

build:
	@echo "Building all services..."
	ssh go-dev "cd ~/workspace && go build -o /tmp/user-service"
	ssh rust-dev "cd ~/workspace && cargo build --release"

logs:
	docker logs python-dev --tail 50 -f

clean:
	./scripts/shutdown-virtual all
	docker system prune -f

seed:
	./scripts/seed-db.sh

migrate:
	ssh python-dev "cd ~/workspace && alembic upgrade head"
```

Now Claude can use simple commands:
```bash
make test
make logs
make seed
```

#### Claude Code Tips for VDE

**1. Always specify the container in commands:**

```
# Good
You: Run pytest in the python-dev container

# Bad
You: Run pytest
[Claude might run it on the host where it won't work]
```

**2. Use Claude's understanding of the architecture:**

```
You: The analytics service needs to read from the user service's API.
How should it connect?

Claude: Since both services are on the dev-net Docker network, the
analytics service should connect to 'go-dev:8001' (using the container
name as the hostname). Let me update the configuration...
```

**3. Leverage SSH for debugging:**

```
You: I'm getting a connection error. Debug this.

Claude: Let me check a few things:

1. Is the container running?
docker ps | grep postgres

2. Can we connect from the python container?
ssh python-dev "pg_isready -h postgres"

3. Let's check the postgres logs:
docker logs postgres --tail 50

I see the issue - postgres is listening on 127.0.0.1 but should be
listening on all interfaces. Let me fix that...
```

**4. Use Claude for multi-step operations:**

```
You: Set up a new development environment for a JavaScript project
with Redis and PostgreSQL

Claude: I'll set this up step by step:

1. Create the JS VM:
./scripts/create-virtual-for js

2. Create the service VMs:
./scripts/create-virtual-for redis
./scripts/create-virtual-for postgres

3. Start all VMs:
./scripts/start-virtual js redis postgres

4. Create the project:
mkdir -p ~/dev/projects/js/myapp
cd ~/dev/projects/js/myapp

5. Initialize the project:
ssh js-dev "cd ~/workspace && npm init -y"

6. Install dependencies:
ssh js-dev "cd ~/workspace && npm install express pg redis"

7. Set up the database:
ssh postgres "createdb myapp"

8. Create environment file:
cat > ~/dev/env-files/js.env << EOF
NODE_ENV=development
DB_HOST=postgres
REDIS_HOST=redis
EOF

9. Create a starter app:
[Creates app.js]

All set! You can now:
- Connect: ssh js-dev
- Run: ssh js-dev "cd ~/workspace && node app.js"
```

### Other AI CLI Tools

#### Aider

Aider is a GPT-powered coding assistant that works well with VDE.

**Setup:**

```bash
# Install aider
pip install aider-chat

# Navigate to your project
cd ~/dev/projects/python/my-api

# Run aider (host-based)
aider --ssh python-dev

# Aider will connect to the container and edit files
```

**Aider + VDE Workflow:**

```bash
# 1. Start aider with SSH connection
aider --ssh python-dev

# 2. Aider drops you into a chat interface
# 3. Give it commands:
> Add user authentication
> Write tests for the API
> Fix the failing test in test_auth.py
```

**Benefits:**
- Direct file editing in the container
- Built-in git integration
- Good for pair programming

#### Cursor

Cursor is a fork of VSCode with AI integration built in.

**Setup:**

```bash
# 1. Install Cursor from cursor.sh

# 2. Open Cursor and connect to your VM via Remote-SSH
# File > Connect to Host... > python-dev

# 3. Open your project: /home/devuser/workspace

# 4. Use Cursor's AI features:
# - Cmd+L for chat
# - Cmd+K for inline editing
# - Cmd+I for code generation
```

**Cursor + VDE Workflow:**

```
1. Connect Cursor to python-dev via Remote-SSH
2. Open the workspace folder
3. Select code and press Cmd+K
4. Give instructions: "Add error handling"
5. Cursor edits the file in the container
```

**Benefits:**
- Native VSCode experience
- Direct container access
- Great for refactoring and code exploration

#### GitHub Copilot

GitHub Copilot integrates with VSCode Remote-SSH.

**Setup:**

```bash
# 1. Install GitHub Copilot extension in VSCode

# 2. Connect to VM via Remote-SSH

# 3. Open a file in the workspace

# 4. Copilot works automatically:
# - Press Tab to accept suggestions
# - Ctrl+Enter for multi-line suggestions
# - Ctrl+Shift+Alt+/ for copilot chat
```

**Copilot + VDE Workflow:**

```
1. Connect VSCode to python-dev
2. Create a new file: tests/test_user.py
3. Start typing:
   def test_create_user():

4. Copilot suggests the rest based on your codebase

5. Or use Copilot Chat:
   Ctrl+Shift+Alt+/
   > "Write tests for the User model"
   > "Add error handling to this function"
   > "Explain how this code works"
```

**Benefits:**
- Familiar VSCode interface
- Context-aware suggestions
- Good for boilerplate and documentation

#### Comparison Table

| Tool | VDE Integration | Best For | Setup Complexity |
|------|----------------|----------|------------------|
| **Claude Code** | Excellent (3 patterns) | Complex tasks, architecture | Medium |
| **Aider** | Good (SSH mode) | Git workflows, pair programming | Low |
| **Cursor** | Excellent (Remote-SSH) | Refactoring, exploration | Low |
| **Copilot** | Good (VSCode extension) | Boilerplate, completion | Low |

**Recommendation:** Start with **Claude Code** for its flexibility with VDE's multi-container architecture.

---

## Development Workflows

### Example 1: Python API with PostgreSQL

```bash
# 1. Create Python VM
./scripts/create-virtual-for python

# 2. Create PostgreSQL VM
./scripts/create-virtual-for postgres

# 3. Start both VMs
./scripts/start-virtual python postgres

# 4. Connect to Python VM
ssh python-dev

# 5. Set up project
cd ~/workspace
python -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn psycopg2-binary

# 6. Test database connection
ssh postgres
createdb testdb
exit

psql -h postgres -U devuser -d testdb

# 7. Run your API
uvicorn main:app --reload
```

### Example 2: Full-Stack JavaScript with Redis

```bash
# 1. Create VMs
./scripts/create-virtual-for js
./scripts/create-virtual-for redis

# 2. Start VMs
./scripts/start-virtual js redis

# 3. Connect to JS VM
ssh js-dev

# 4. Set up Express app
cd ~/workspace
npm init -y
npm install express redis

# 5. Create app (in VSCode Remote-SSH or edit locally)
cat > app.js << 'EOF'
const express = require('express');
const redis = require('redis');
const app = express();

const client = redis.createClient({
  host: 'redis',
  port: 6379
});

app.get('/', (req, res) => {
  res.send('Hello from VDE!');
});

app.listen(3000, () => {
  console.log('Server running on port 3000');
});
EOF

# 6. Run app
node app.js
```

### Example 3: Microservices with Multiple Languages

```bash
# 1. Create VMs for each service
./scripts/create-virtual-for python   # API Gateway
./scripts/create-virtual-for go       # Payment Service
./scripts/create-virtual-for rust     # Analytics Service
./scripts/create-virtual-for postgres # Database
./scripts/create-virtual-for redis    # Cache

# 2. Start all VMs
./scripts/start-virtual python go rust postgres redis

# 3. Each service runs in its own VM
# Python: ssh python-dev
# Go: ssh go-dev
# Rust: ssh rust-dev

# 4. Services communicate via Docker network
# python-dev can access: postgres, redis
# go-dev can access: postgres, redis
# etc.
```

---

## Directory Structure

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
└── scripts/
    ├── lib/
    │   └── vm-common           # Shared library
    ├── templates/              # Docker compose templates
    ├── data/
    │   └── vm-types.conf       # VM type definitions
    ├── list-vms
    ├── create-virtual-for
    ├── start-virtual
    ├── shutdown-virtual
    ├── build-and-start
    └── add-vm-type
```

---

## User Model

All containers run as:
- **Username:** `devuser`
- **UID:** `1000`
- **GID:** `1000`
- **Shell:** `/bin/zsh` with oh-my-zsh
- **Editor:** neovim with LazyVim
- **Sudo:** Passwordless sudo access

### Home Directory Structure

Inside each VM:
```
/home/devuser/
├── .ssh/              # SSH keys and known_hosts
├── .zshrc            # Zsh configuration with oh-my-zsh
├── .zprofile         # PATH configuration
├── .config/nvim/      # LazyVim configuration
└── workspace/         # Your project directory (mounted from host)
```

### Modifying User Setup

To modify user setup across all containers, edit: `configs/docker/base-dev.Dockerfile`

Then rebuild:
```bash
./scripts/build-and-start --rebuild
```

---

## Naming Conventions

### Language VMs
- **Container:** `<name>-dev` (e.g., `python-dev`)
- **SSH Host:** `<name>-dev` (e.g., `python-dev`)
- **Port Range:** 2200-2299
- **Project Directory:** `projects/<name>/`
- **Volume Mount:** `/home/devuser/workspace`

### Service VMs
- **Container:** `<name>` (e.g., `postgres`)
- **SSH Host:** `<name>` (e.g., `postgres`)
- **Port Range:** 2400-2499
- **Data Directory:** `data/<name>/`
- **Service Port:** Container-specific (5432 for postgres, etc.)

---

## Troubleshooting

### Port Conflicts

```bash
# See what's using a port
lsof -i :2205

# Stop conflicting VM
./scripts/shutdown-virtual go

# Restart VM
./scripts/start-virtual go
```

### SSH Connection Issues

```bash
# Check SSH config
ssh -v go-dev

# Verify container is running
docker ps | grep go-dev

# Check container logs
docker logs go-dev

# Restart SSHd in container
docker exec go-dev /usr/sbin/sshd
```

### Permission Denied

```bash
# Ensure correct permissions
chmod 600 ~/.ssh/id_ed25519
chmod 600 ~/.ssh/config
chmod 644 ~/.ssh/id_ed25519.pub
```

### Container Won't Start

```bash
# Check logs
docker logs <container-name>

# Rebuild with no cache
./scripts/start-virtual <vm-name> --rebuild --no-cache

# Check docker-compose.yml syntax
docker-compose -f configs/docker/<vm-name>/docker-compose.yml config
```

### VSCode Remote-SSH Can't Connect

```bash
# Verify SSH works from terminal
ssh go-dev

# Check VSCode Remote-SSH settings
# ~/.ssh/config should be readable

# Try reloading VSCode window
# Cmd+Shift+P > "Developer: Reload Window"
```

---

## Architecture

### Template System

**Templates:**
- `templates/compose-language.yml` - Template for language VM docker-compose.yml
- `templates/compose-service.yml` - Template for service VM docker-compose.yml
- `templates/ssh-entry.txt` - Template for SSH config entries

**Data-Driven Configuration:**
- `data/vm-types.conf` - All VM types defined here (pipe-delimited)
- Format: `type|name|aliases|display_name|install_command|service_port`

### Shared Library

**File:** `scripts/lib/vm-common`

**Key Functions:**
- `get_vm_info()` - Query VM type data
- `resolve_vm_name()` - Handle aliases
- `find_next_available_port()` - Auto-allocate ports
- `render_template()` - Generate configs from templates
- `merge_ssh_config_entry()` - Safely add SSH entries

### Base Image

All VMs build from `configs/docker/base-dev.Dockerfile` which includes:
- System updates
- SSH server
- sudo access
- zsh with oh-my-zsh
- neovim with LazyVim
- Common tools (git, curl, wget, etc.)

---

## Advanced Usage

### Custom Installation Commands

```bash
# Multi-step installation
./scripts/add-vm-type zig \
    "apt-get update && apt-get install -y wget && \
     wget https://ziglang.org/download/0.11.0/zig-linux-x86_64-0.11.0.tar.xz && \
     tar -xf zig-linux-x86_64-0.11.0.tar.xz && \
     mv zig-linux-x86_64-0.11.0 /opt/zig && \
     ln -s /opt/zig/zig /usr/local/bin/zig"

# Install as devuser
./scripts/add-vm-type rust \
    "su devuser -c 'curl --proto =https --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y'"
```

### Multiple Service Ports

```bash
# For services with multiple ports
./scripts/add-vm-type --type service --svc-port 80,443 nginx \
    "apt-get update -y && apt-get install -y nginx-extras"
```

### Custom Display Names

```bash
# Override the auto-generated display name
./scripts/add-vm-type --display "Rust Programming Language" rust \
    "apt-get update -y && apt-get install -y rustc"
```

---

## Rebuild Guidelines

| Scenario | Command |
|----------|---------|
| Daily development | No rebuild needed |
| Dockerfiles change | `--rebuild` |
| SSH keys change | `--rebuild` |
| Environment variables change | `--rebuild` |
| Base images update | `--rebuild --no-cache` |

---

## Best Practices

1. **Work in projects directory**: All code is in `projects/<lang>/` which persists on your host
2. **Use VSCode Remote-SSH**: Edit code locally with full IDE support
3. **Commit often**: Your code is safe on the host, containers are ephemeral
4. **Use service VMs**: Databases and caches run in separate containers
5. **Leverage AI tools**: Claude Code, Cursor, Copilot all work with VDE
6. **SSH between containers**: All VMs share the `dev-net` network for inter-container communication

---

## Support

For issues or questions:
1. Check `./scripts/list-vms` to see available VMs
2. Review `~/.ssh/config` for SSH entries
3. Check `docker ps` for running containers
4. Review `docker logs <container>` for errors
5. Ensure you're using zsh 5.0+

---

## License

This VDE system is provided as-is for development purposes.
