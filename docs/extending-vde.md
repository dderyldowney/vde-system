# Extending VDE

VDE is designed to be easily extensible. You can add support for new programming languages, new services, or customize existing ones without modifying any scripts. The entire system is data-driven through configuration files and templates.

[← Back to README](../README.md)

---

## Understanding VDE Architecture

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

### Key Files

| File | Purpose | Edit to Extend |
|------|---------|----------------|
| `data/vm-types.conf` | Defines all VM types | ✅ **Yes** - Add new entries |
| `templates/compose-language.yml` | Language VM template | Rarely - only for structural changes |
| `templates/compose-service.yml` | Service VM template | Rarely - only for structural changes |
| `templates/ssh-entry.txt` | SSH config template | Rarely - only for format changes |
| `lib/vm-common` | Core functions | Never - use templates/config instead |

### vm-types.conf Format

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

---

## Adding New Languages

Adding a new programming language to VDE is a two-step process:

### Step 1: Add to vm-types.conf

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

### Step 2: Create the VM

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

### What Gets Created

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

### Language Installation Best Practices

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

---

## Adding New Services

Adding a service (database, cache, message queue, etc.) is similar to adding a language, with the additional requirement of specifying the service port.

### Step 1: Add to vm-types.conf

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

### Step 2: Create the Service VM

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

### What Gets Created (Different from Languages)

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

### Key Differences: Language vs Service VMs

| Aspect | Language VM | Service VM |
|--------|-------------|------------|
| Container name | `<name>-dev` | `<name>` |
| SSH config | `<name>-dev` | `<name>` |
| Port range | 2200-2299 | 2400-2499 |
| Volume mount | `projects/<name>/` | `data/<name>/` |
| Purpose | Development workspace | Persistent data |
| Example | `zig-dev`, port 2205 | `rabbitmq`, port 2405 |

### Service Installation Examples

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

---

## Advanced Extension Patterns

### Custom Container Names

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

### Multi-Language Images

For languages that work together (e.g., TypeScript + JavaScript), you can create composite VMs:

```bash
# Add TypeScript as an alias of JavaScript (same VM)
# In vm-types.conf:
lang|js|node,nodejs,typescript|JavaScript|apt-get update && curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - && apt-get install -y nodejs && npm install -g typescript|

# Now both create the same VM:
./scripts/create-virtual-for js
./scripts/create-virtual-for typescript  # Creates the same VM
```

### Custom Base Images

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

### Environment-Specific Installations

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

### Post-Installation Scripts

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

### Validation and Testing

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

[← Back to README](../README.md)
