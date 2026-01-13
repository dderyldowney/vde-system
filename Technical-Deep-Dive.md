# VDE System: Complete Technical Deep-Dive

## Architecture Overview

The VDE (Virtual Development Environment) system is a **template-based, data-driven Docker container orchestration system**. It's designed to create isolated development environments for different programming languages and services, all accessible via SSH with consistent user configuration.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          HOST MACHINE                                   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                         ~/dev/                                  │   │
│  │                                                                  │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │   │
│  │  │   scripts/   │  │   configs/   │  │   projects/  │          │   │
│  │  │              │  │   docker/    │  │              │          │   │
│  │  │ • lib/       │  │              │  │ • python/    │◄─────┐   │   │
│  │  │ • templates/ │  │ • base-dev   │  │ • go/        │       │   │   │
│  │  │ • data/      │  │ • python/    │  │ • rust/      │       │   │   │
│  │  │ • *.vm       │  │ • go/        │  └──────────────┘       │   │   │
│  │  └──────────────┘  └──────────────┘                        │   │   │
│  │                                                             │   │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │   │   │
│  │  │  env-files/  │  │   data/      │  │    logs/     │     │   │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘     │   │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                │                                      │
│                          ┌─────▼─────┐                                │
│                          │  Docker   │                                │
│                          │  Engine   │                                │
│                          └─────┬─────┘                                │
└───────────────────────────────┼──────────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                ▼               ▼               ▼
        ┌──────────────┐ ┌──────────┐ ┌──────────────┐
        │  python-dev  │ │  go-dev  │ │  postgres    │
        │  :2222       │ │  :2205   │ │  :2400       │
        └──────────────┘ └──────────┘ └──────────────┘
                │               │               │
                └───────────────┴───────────────┘
                                │
                        ┌───────▼───────┐
                        │   dev-net     │
                        │ (Docker Net)  │
                        └───────────────┘
```

---

## Part 1: Core Data Structure (vm-types.conf)

Everything starts with the **vm-types.conf** file. This is the single source of truth for all VM types.

**File:** `scripts/data/vm-types.conf`

**Format:** Pipe-delimited records
```
type|name|aliases|display_name|install_command|service_port
```

**Example entries:**
```bash
lang|go|golang|Go|apt-get update -y && apt-get install -y golang-go|
service|postgres|postgresql|PostgreSQL|apt-get update -y && apt-get install -y postgresql-client|5432
```

**Field meanings:**

| Field | Example | Purpose |
|-------|---------|---------|
| `type` | `lang` or `service` | Determines template and naming convention |
| `name` | `go` | Primary identifier (lowercase alphanumeric) |
| `aliases` | `golang` | Alternate names for lookup |
| `display_name` | `Go` | Human-readable name for messages |
| `install_command` | Shell command | Runs during container startup |
| `service_port` | `5432` or empty | Service port(s) for containers, empty for languages |

**Why this format:**
- ✅ Simple to parse (shell built-in `read -A`)
- ✅ Human-readable and editable
- ✅ No dependencies (no JSON/YAML parsers needed)
- ✅ Easy to extend (just add a line)

---

## Part 2: The Shared Library (lib/vm-common)

When any script runs, the first thing it does is:

```bash
source "$SCRIPT_DIR/lib/vm-common"
```

This loads **508 lines** of shared functionality. Let's break down what happens:

### 2.1 Constants Initialization (Lines 9-29)

```bash
# Path calculation (zsh-compatible)
readonly VDE_ROOT_DIR="$(cd "$(dirname "${(%):-%x}")/../.." && pwd)"
readonly CONFIGS_DIR="$VDE_ROOT_DIR/configs/docker"
readonly SCRIPTS_DIR="$VDE_ROOT_DIR/scripts"
readonly TEMPLATES_DIR="$SCRIPTS_DIR/templates"
readonly DATA_DIR="$SCRIPTS_DIR/data"
readonly VM_TYPES_CONF="$DATA_DIR/vm-types.conf"

# Port ranges
readonly LANG_PORT_START=2200  # Language VMs: 2200-2299
readonly LANG_PORT_END=2299
readonly SVC_PORT_START=2400   # Service VMs: 2400-2499
readonly SVC_PORT_END=2499
```

**Key technical detail:** The path calculation uses `${(%):-%x}` which is **zsh-specific**. In bash, you'd use `${BASH_SOURCE[0]}`. This is why the scripts require zsh 5.0+.

### 2.2 Associative Array Declaration (Lines 50-54)

```bash
typeset -gA VM_TYPE       # [go]=lang, [postgres]=service
typeset -gA VM_ALIASES    # [go]=golang, [postgres]=postgresql
typeset -gA VM_DISPLAY    # [go]=Go, [postgres]=PostgreSQL
typeset -gA VM_INSTALL    # [go]=apt-get install golang-go
typeset -gA VM_SVC_PORT   # [go]=, [postgres]=5432
```

The `-gA` flags mean:
- `-g`: Global (available to functions that source this library)
- `-A`: Associative array (requires zsh 5.0+)

### 2.3 Config Loading (Lines 56-82)

```bash
load_vm_types() {
    # Clear existing arrays
    unset VM_TYPE VM_ALIASES VM_DISPLAY VM_INSTALL VM_SVC_PORT
    typeset -gA VM_TYPE VM_ALIASES VM_DISPLAY VM_INSTALL VM_SVC_PORT

    # Parse vm-types.conf line by line
    while IFS='|' read -r type name vm_aliases display install svc_port; do
        # Skip comments (#) and empty lines
        [[ "$type" =~ ^#.*$ ]] && continue
        [[ -z "$type" ]] && continue

        # Store in associative arrays
        VM_TYPE[$name]="$type"
        VM_ALIASES[$name]="$vm_aliases"
        VM_DISPLAY[$name]="$display"
        VM_INSTALL[$name]="$install"
        VM_SVC_PORT[$name]="$svc_port"
    done < "$conf_file"
}
```

**Auto-execution:** At line 507, `load_vm_types` is called automatically when the library is sourced. This means **all associative arrays are populated immediately** when any script starts.

### 2.4 Name Resolution (Lines 156-175)

```bash
resolve_vm_name() {
    local input=$1

    # Direct match: "go" -> "go"
    if is_known_vm "$input"; then
        echo "$input"
        return 0
    fi

    # Alias lookup: "golang" -> "go"
    for name in "${(@k)VM_TYPE}"; do
        local vm_aliases="${VM_ALIASES[$name]}"
        if [[ ",$vm_aliases," =~ ",$input," ]]; then
            echo "$name"
            return 0
        fi
    done

    return 1
}
```

**Why the comma trick:** `,$vm_aliases,` creates `,golang,` so searching for `,golang,` prevents false matches (e.g., "go" wouldn't match "golang").

---

## Part 3: Template System

The VDE uses **template variable substitution** to generate docker-compose.yml files.

### 3.1 Language Template (`templates/compose-language.yml`)

```yaml
services:
  {{NAME}}-dev:                    # e.g., "go-dev"
    build:
      context: ../../..
      dockerfile: configs/docker/base-dev.Dockerfile
      args:
        USERNAME: devuser
        UID: 1000
        GID: 1000
        PUBLIC_KEYS_DIR: /public-ssh-keys
    image: dev-{{NAME}}:latest      # e.g., "dev-go:latest"
    container_name: {{NAME}}-dev    # e.g., "go-dev"
    hostname: {{NAME}}-dev
    restart: unless-stopped
    command: sh -c "{{INSTALL_CMD}} && /usr/sbin/sshd -D"

    ports:
      - "{{SSH_PORT}}:22"          # e.g., "2205:22"

    volumes:
      - ../../../projects/{{NAME}}:/home/devuser/workspace
      - ../../../logs/{{NAME}}:/logs
      - ../../../public-ssh-keys:/public-ssh-keys:ro

    env_file:
      - ../../../env-files/{{NAME}}.env

    networks:
      - dev-net
```

### 3.2 Service Template (`templates/compose-service.yml`)

```yaml
services:
  {{NAME}}:                        # No "-dev" suffix!
    # ... (same build config)
    container_name: {{NAME}}        # e.g., "postgres" not "postgres-dev"

    ports:
      - "{{SSH_PORT}}:22"          # SSH access
      - "{{SERVICE_PORT}}:{{SERVICE_PORT}}"  # Service port(s)

    volumes:
      - ../../../data/{{NAME}}:/data   # Note: "data" not "projects"
      - ../../../logs/{{NAME}}:/logs
      # ...
```

### 3.3 Template Rendering (Lines 323-347)

```bash
render_template() {
    local template_file=$1
    shift  # Remaining args are var=value pairs

    local content=$(cat "$template_file")

    # Parse variable pairs
    while [[ $# -ge 2 ]]; do
        local var_name="$1"
        local var_value="$2"
        shift 2

        # Escape special characters for sed
        var_value=$(printf '%s\n' "$var_value" | sed 's/[&/\]/\\&/g')

        # Replace {{VAR_NAME}} with value
        content=$(echo "$content" | sed "s/{{$var_name}}/$var_value/g")
    done

    echo "$content"
}
```

**Usage:**
```bash
render_template "$template_file" \
    NAME "go" \
    SSH_PORT "2205" \
    INSTALL_CMD "apt-get update -y && apt-get install -y golang-go" \
    SERVICE_PORT "" \
    > "$output_file"
```

---

## Part 4: Port Allocation System

One of the most sophisticated parts of VDE is **automatic port allocation**.

### 4.1 Getting Allocated Ports (Lines 202-225)

```bash
get_allocated_ports() {
    local range_start=$1  # e.g., 2200
    local range_end=$2    # e.g., 2299

    local ports=()

    # Scan all docker-compose.yml files in configs/docker/
    for compose_dir in "$CONFIGS_DIR"/*/; do
        compose_file="$compose_dir/docker-compose.yml"

        if [[ -f "$compose_file" ]]; then
            while IFS= read -r line; do
                # Match "XXXX:22" port mapping
                if [[ "$line" =~ ([0-9]+):22 ]]; then
                    local port="$match[1]"  # Zsh regex capture

                    # Only add if in range
                    if [[ $port -ge $range_start && $port -le $range_end ]]; then
                        ports+=("$port")
                    fi
                fi
            done < "$compose_file"
        fi
    done

    # Sort, deduplicate, output
    printf '%s\n' "${ports[@]}" | sort -n | uniq
}
```

**What this does:**
1. Scans every `configs/docker/*/docker-compose.yml`
2. Finds lines like `- "2205:22"`
3. Extracts the SSH port (2205)
4. Returns sorted list of all allocated ports

### 4.2 Finding Next Available Port (Lines 227-258)

```bash
find_next_available_port() {
    local vm_type=$1  # "lang" or "service"
    local range_start range_end

    # Select range based on type
    case "$vm_type" in
        lang)  range_start=2200; range_end=2299 ;;
        service) range_start=2400; range_end=2499 ;;
    esac

    # Get all allocated ports in this range
    local -a allocated_ports
    allocated_ports=($(get_allocated_ports "$range_start" "$range_end"))

    # Find first unused port
    for ((port=range_start; port<=range_end; port++)); do
        if [[ ! " ${allocated_ports[@]} " =~ " ${port} " ]]; then
            echo "$port"
            return 0
        fi
    done

    log_error "No available ports in range $range_start-$range_end"
    return 1
}
```

**Example flow:**
```
Existing VMs:
- python-dev: SSH_PORT=2222
- js-dev: SSH_PORT=2224

get_allocated_ports 2200 2299
=> Returns: 2222, 2224

find_next_available_port lang
=> Checks 2200 (free), 2201 (free), ..., 2222 (taken)
=> Returns: 2200
```

---

## Part 5: Complete Lifecycle - Creating a Go VM

Let's trace exactly what happens when you run:

```bash
./scripts/create-virtual-for go
```

### Step 1: Script Entry (create-virtual-for:1-6)

```bash
#!/usr/bin/env zsh
set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/lib/vm-common"  # Load all functions, parse vm-types.conf
```

At this point, memory contains:
```
VM_TYPE[go]=lang
VM_ALIASES[go]=golang
VM_DISPLAY[go]=Go
VM_INSTALL[go]=apt-get update -y && apt-get install -y golang-go
VM_SVC_PORT[go]=
```

### Step 2: Validation (Lines 46-68)

```bash
VM_NAME="$1"  # "go"

validate_vm_name "$VM_NAME"
# Checks: is "go" lowercase alphanumeric? Yes.

RESOLVED_NAME=$(resolve_vm_name "$VM_NAME" || true)
# Checks: is "go" a known VM? Yes. Returns "go".

validate_vm_doesnt_exist "$VM_NAME"
# Checks: does configs/docker/go/docker-compose.yml exist? No.

validate_ssh_key_exists
# Checks: does ~/.ssh/id_ed25519 exist? Yes.
```

### Step 3: Query VM Configuration (Lines 73-76)

```bash
VM_TYPE=$(get_vm_info type "$VM_NAME")         # "lang"
VM_DISPLAY=$(get_vm_info display "$VM_NAME")   # "Go"
VM_INSTALL=$(get_vm_info install "$VM_NAME")   # "apt-get update -y && apt-get install -y golang-go"
VM_SVC_PORT=$(get_vm_info svc_port "$VM_NAME") # "" (empty for languages)
```

### Step 4: Allocate SSH Port (Lines 89-94)

```bash
SSH_PORT=$(find_next_available_port "$VM_TYPE")
# Scans configs/docker/*/docker-compose.yml
# Finds: python-dev (2222), js-dev (2224), rust-dev (2223)
# Returns: 2200 (first available in 2200-2299)

log_info "Allocated SSH port: 2200"
```

### Step 5: Create Directories (Lines 99-100)

```bash
ensure_vm_directories "$VM_NAME" "$VM_TYPE"
# Creates:
# - configs/docker/go/
# - projects/go/
# - logs/go/
```

### Step 6: Generate docker-compose.yml (Lines 105-125)

```bash
template_file="$TEMPLATES_DIR/compose-language.yml"
compose_file="$CONFIGS_DIR/$VM_NAME/docker-compose.yml"

render_template "$template_file" \
    NAME "go" \
    SSH_PORT "2200" \
    INSTALL_CMD "apt-get update -y && apt-get install -y golang-go" \
    SERVICE_PORT "" \
    > "$compose_file"
```

**Template substitution:**
```yaml
# Before:
services:
  {{NAME}}-dev:
    ports:
      - "{{SSH_PORT}}:22"
    command: sh -c "{{INSTALL_CMD}} && /usr/sbin/sshd -D"

# After:
services:
  go-dev:
    ports:
      - "2200:22"
    command: sh -c "apt-get update -y && apt-get install -y golang-go && /usr/sbin/sshd -D"
```

### Step 7: Create Environment File (Lines 130-151)

```bash
env_file="$VDE_ROOT_DIR/env-files/$VM_NAME.env"

cat > "$env_file" <<EOF
SSH_PORT=2200
EOF
```

### Step 8: Update SSH Config (Lines 156-171)

```bash
ssh_host="${VM_NAME}-dev"  # "go-dev" (language VMs get -dev suffix)

merge_ssh_config_entry "$ssh_host" "2200" "Go"
# 1. Backs up ~/.ssh/config to ~/dev/backup/ssh/config.backup.TIMESTAMP
# 2. Generates SSH entry from template
# 3. Appends to ~/.ssh/config
```

**Generated SSH entry:**
```ssh-config
# Go Dev VM
Host go-dev
    HostName localhost
    Port 2200
    User devuser
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
```

### Step 9: Summary Output

```
[SUCCESS] VM configuration complete!

Created files:
  - configs/docker/go/docker-compose.yml
  - env-files/go.env
  - projects/go/
  - logs/go/

SSH Configuration:
  - Host alias: go-dev
  - SSH port: 2200
  - Connect with: ssh go-dev

Next steps:
  1. Review and customize env-files/go.env if needed
  2. Start the VM: ./scripts/start-virtual go
  3. Connect: ssh go-dev
```

---

## Part 6: Starting the VM

Now you run:

```bash
./scripts/start-virtual go
```

### Script Flow (start-virtual)

```bash
# 1. Load library
source "$SCRIPT_DIR/lib/vm-common"

# 2. Parse arguments
VMS=()  # Array of VM names to start
rebuild=false
nocache=false

# 3. Resolve VM name
resolved=$(resolve_vm_name "go")  # Returns "go"
VMS+=("go")

# 4. Start each VM
for vm in "${VMS[@]}"; do
    start_vm "$vm" "$rebuild" "$nocache"
done
```

### start_vm Function (lib/vm-common:282-301)

```bash
start_vm() {
    local vm=$1          # "go"
    local rebuild=$2     # false
    local nocache=$3     # false

    compose_file="$CONFIGS_DIR/$vm/docker-compose.yml"

    # Build docker-compose options
    if [[ "$rebuild" == "true" ]]; then
        opts="--build"
        if [[ "$nocache" == "true" ]]; then
            opts="$opts --no-cache"
        fi
    fi

    # Start container
    docker-compose -f "$compose_file" up -d $opts
}
```

**What docker-compose does:**

1. **Build image** (if needed):
   ```bash
   docker build \
     -f configs/docker/base-dev.Dockerfile \
     --build-arg USERNAME=devuser \
     --build-arg UID=1000 \
     --build-arg GID=1000 \
     --build-arg PUBLIC_KEYS_DIR=/public-ssh-keys \
     -t dev-go:latest \
     .
   ```

2. **Create container**:
   ```bash
   docker create \
     --name go-dev \
     --hostname go-dev \
     --restart unless-stopped \
     -p 2200:22 \
     -v ~/dev/projects/go:/home/devuser/workspace \
     -v ~/dev/logs/go:/logs \
     -v ~/dev/public-ssh-keys:/public-ssh-keys:ro \
     --env-file ~/dev/env-files/go.env \
     --network dev-net \
     dev-go:latest \
     sh -c "apt-get update -y && apt-get install -y golang-go && /usr/sbin/sshd -D"
   ```

3. **Start container**: `docker start go-dev`

### Container Boot Sequence

Inside the container:

```bash
# 1. Execute the command
sh -c "apt-get update -y && apt-get install -y golang-go && /usr/sbin/sshd -D"

# 2. Install Go (takes ~30 seconds)
# - apt-get update
# - apt-get install golang-go

# 3. Start SSH daemon
/usr/sbin/sshd -D  # -D = no daemonize, run in foreground
```

Now the container is running with:
- **SSH accessible** on localhost:2200
- **Go installed** and available to devuser
- **Workspace mounted** at `/home/devuser/workspace`

---

## Part 7: SSH Connection

You can now connect:

```bash
ssh go-dev
```

### SSH Connection Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. SSH Client reads ~/.ssh/config                              │
│    Finds "Host go-dev" entry                                   │
│    - HostName: localhost                                       │
│    - Port: 2200                                                │
│    - User: devuser                                             │
│    - IdentityFile: ~/.ssh/id_ed25519                           │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. SSH connects to localhost:2200                              │
│    Port 2200 is mapped by Docker to go-dev:22                 │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. Container's sshd receives connection                        │
│    - Authenticates using public key from /public-ssh-keys      │
│    - Spawns shell as devuser                                   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. User gets zsh prompt                                        │
│    devuser@go-dev:~$                                           │
│                                                                 │
│    Environment:                                                │
│    - HOME: /home/devuser                                       │
│    - SHELL: /bin/zsh                                           │
│    - Workspace: /home/devuser/workspace (~/dev/projects/go)    │
│    - Go installed: /usr/bin/go                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Inside the Container

```bash
devuser@go-dev:~$ cd ~/workspace
devuser@go-dev:~/workspace$ ls -la
# Shows contents of ~/dev/projects/go on host

devuser@go-dev:~/workspace$ go version
# go version go1.21 debian

devuser@go-dev:~/workspace$ cat > main.go << 'EOF'
package main
import "fmt"
func main() {
    fmt.Println("Hello from VDE!")
}
EOF

devuser@go-dev:~/workspace$ go run main.go
Hello from VDE!
```

**Key point:** Files created in `~/workspace` are actually created in `~/dev/projects/go` on the host (via volume mount).

---

## Part 8: Service VMs (Different Pattern)

Service VMs (like PostgreSQL) work differently:

### Key Differences

| Aspect | Language VM | Service VM |
|--------|-------------|------------|
| Container name | `go-dev` | `postgres` (no suffix) |
| SSH host | `go-dev` | `postgres` |
| Port range | 2200-2299 | 2400-2499 |
| Volume mount | `projects/go/` | `data/postgres/` |
| Purpose | Development workspace | Persistent data |

### Example: PostgreSQL Service

**vm-types.conf entry:**
```bash
service|postgres|postgresql|PostgreSQL|apt-get update -y && apt-get install -y postgresql-client|5432
```

**Generated docker-compose.yml:**
```yaml
services:
  postgres:  # Note: no "-dev" suffix
    # ... (same build)
    container_name: postgres

    ports:
      - "2400:22"     # SSH access
      - "5432:5432"   # PostgreSQL access

    volumes:
      - ../../../data/postgres:/data  # Persistent data
      # ...
```

**Why this design:**
- **Language VMs**: You develop code in them, so they need a workspace directory
- **Service VMs**: They provide services (database, cache), so they need persistent data

---

## Part 9: Inter-Container Communication

All containers are on the `dev-net` Docker network, enabling communication:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ python-dev  │     │  postgres   │     │    redis    │
│   :2222     │     │   :2400     │     │   :2401     │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                  │                  │
       └──────────────────┴──────────────────┘
                          │
                  ┌───────▼───────┐
                  │   dev-net     │
                  │ (bridge net)  │
                  └───────────────┘
```

**From python-dev container:**
```bash
# Connect to PostgreSQL
psql -h postgres -U devuser -d mydb

# Connect to Redis
redis-cli -h redis

# SSH to another container
ssh go-dev
```

**Service discovery works via container names** because Docker's embedded DNS resolves container names to IPs.

---

## Part 10: Multi-Container Management

The scripts support managing multiple VMs at once:

```bash
# Start multiple VMs
./scripts/start-virtual python go rust postgres redis

# This internally does:
for vm in "python" "go" "rust" "postgres" "redis"; do
    start_vm "$vm" "$rebuild" "$nocache"
done
```

**Special case: `all` keyword**

```bash
./scripts/start-virtual all
```

This expands to all VMs that have been created (have docker-compose.yml files):

```bash
# Find all VMs
for compose_dir in configs/docker/*/; do
    vm_name=$(basename "$compose_dir")
    VMS+=("$vm_name")
done

# Start each
for vm in "${VMS[@]}"; do
    start_vm "$vm"
done
```

---

## Part 11: Stopping VMs

```bash
./scripts/shutdown-virtual go
```

**Internally:**
```bash
stop_vm() {
    local vm=$1
    compose_file="$CONFIGS_DIR/$vm/docker-compose.yml"

    docker-compose -f "$compose_file" down
}
```

**What `docker-compose down` does:**
1. Stops the container: `docker stop go-dev`
2. Removes the container: `docker rm go-dev`
3. **Does NOT remove** the image (dev-go:latest persists)
4. **Does NOT remove** volumes (data persists on host)

---

## Part 12: Adding New VM Types

The `add-vm-type` script appends new entries to `vm-types.conf`:

```bash
./scripts/add-vm-type zig \
    "apt-get update -y && apt-get install -y zig"
```

**Flow:**

1. **Validate** (zig doesn't exist, name is valid)
2. **Backup** vm-types.conf
3. **Append** line:
   ```bash
   lang|zig||Zig|apt-get update -y && apt-get install -y zig|
   ```
4. **Reload** VM types: `source lib/vm-common` → `load_vm_types`
5. **Show diff** of changes

Now you can:
```bash
./scripts/create-virtual-for zig
```

---

## Summary: Complete Data Flow

```
User Action:
  ./scripts/create-virtual-for go

↓

Script Entry:
  create-virtual-for sources lib/vm-common
  ↓
  load_vm_types parses vm-types.conf
  ↓
  Associative arrays populated:
    VM_TYPE[go]=lang
    VM_DISPLAY[go]=Go
    VM_INSTALL[go]=apt-get install golang-go

↓

Validation:
  validate_vm_name "go" ✓
  resolve_vm_name "go" → "go" ✓
  validate_vm_doesnt_exist "go" ✓
  validate_ssh_key_exists ✓

↓

Configuration:
  VM_TYPE=$(get_vm_info type "go") → "lang"
  VM_INSTALL=$(get_vm_info install "go") → "apt-get install golang-go"

↓

Port Allocation:
  find_next_available_port "lang"
  ↓
  Scan configs/docker/*/docker-compose.yml for SSH ports
  ↓
  Find first available in 2200-2299
  ↓
  Return: 2200

↓

File Generation:
  1. Create directories:
     - configs/docker/go/
     - projects/go/
     - logs/go/

  2. Generate docker-compose.yml:
     render_template compose-language.yml \
       NAME "go" \
       SSH_PORT "2200" \
       INSTALL_CMD "apt-get install golang-go"

  3. Create env-files/go.env:
     SSH_PORT=2200

  4. Update ~/.ssh/config:
     Append Host go-dev entry

↓

Output:
  [SUCCESS] VM configuration complete!
  Connect with: ssh go-dev

↓

Start VM:
  ./scripts/start-virtual go
  ↓
  docker-compose -f configs/docker/go/docker-compose.yml up -d
  ↓
  Docker builds image (dev-go:latest)
  ↓
  Docker creates container (go-dev)
  ↓
  Docker starts container
  ↓
  Container runs: apt-get install golang-go && /usr/sbin/sshd -D

↓

Connect:
  ssh go-dev
  ↓
  SSH connects to localhost:2200
  ↓
  Container's sshd authenticates
  ↓
  User gets shell as devuser
```

---

## Key Design Principles

1. **Data-iven**: All VM types defined in one config file
2. **Template-Based**: docker-compose.yml generated from templates
3. **Auto-Port-Allocation**: No manual port management
4. **SSH-First**: Everything accessible via SSH
5. **Volume-Mounted**: Code persists on host, containers are ephemeral
6. **Networked**: All containers on dev-net for inter-communication
7. **Extensible**: Add new languages/services by editing one file
8. **Idempotent**: Safe to run create-virtual-for multiple times (fails if exists)
9. **Zsh-Native**: Leverages zsh associative arrays (requires 5.0+)

---

## File Reference

### Core Files

| File | Lines | Purpose |
|------|-------|---------|
| `scripts/lib/vm-common` | 508 | Shared library with all core functions |
| `scripts/data/vm-types.conf` | 34 | VM type definitions (18 languages + 7 services) |
| `scripts/create-virtual-for` | 199 | Create new VM from predefined type |
| `scripts/start-virtual` | 85 | Start one or more VMs |
| `scripts/shutdown-virtual` | 65 | Stop one or more VMs |
| `scripts/add-vm-type` | 252 | Add new VM type to vm-types.conf |

### Templates

| File | Purpose |
|------|---------|
| `templates/compose-language.yml` | Template for language VM docker-compose.yml |
| `templates/compose-service.yml` | Template for service VM docker-compose.yml |
| `templates/ssh-entry.txt` | Template for SSH config entry |

### Generated Files (When VM Created)

| File | Purpose |
|------|---------|
| `configs/docker/<name>/docker-compose.yml` | Docker Compose configuration |
| `env-files/<name>.env` | Environment variables |
| `projects/<name>/` | Language VM workspace directory |
| `data/<name>/` | Service VM data directory |
| `logs/<name>/` | Log directory |
| `~/.ssh/config` | SSH configuration (entry appended) |

---

This is the complete VDE system from configuration to container runtime. Every piece serves a specific purpose in the overall architecture of providing isolated, consistent development environments.
