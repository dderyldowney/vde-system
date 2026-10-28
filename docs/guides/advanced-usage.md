# Advanced Usage
<!-- @shared-law (Sovereign Law) -->

Advanced techniques and patterns for power users in the **Sovereign Baseline**.

[← Back to README](../../README.md)

---

## Custom Installation Commands

### Multi-Step Installation

```zsh
# Download and install from URL
    "apt-get update && apt-get install -y wget && \
```

### Install as devuser

```zsh
# Rust-style installers
vde create rust \
    "su devuser -c 'curl --proto =https --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y'"
```

---

## Multiple Service Ports

```zsh
# For services with multiple ports
vde create --type service --svc-port 80,443 nginx \
    "apt-get update -y && apt-get install -y nginx-extras"
```

---

## Custom Display Names

```zsh
# Override the auto-generated display name
vde create --display "Rust Programming Language" rust \
    "apt-get update -y && apt-get install -y rustc"
```

---

## Environment-Specific Installations

```zsh
vde create python \
    "apt-get update -y && apt-get install -y python3 python3-pip && \
     if [ \"\${VDE_PYTHON_VERSION:-latest}\" = \"3.11\" ]; then \
       apt-get install -y python3.11 python3.11-venv; \
     else \
       apt-get install -y python3.12 python3.12-venv; \
     fi"
```

Then in `env-files/python.env`:
```zsh
VDE_PYTHON_VERSION=3.11
```

---

## Custom Base Images

If a language needs a different base OS:

1. Create a new Dockerfile: `configs/docker/custom-base.Dockerfile`
2. Modify the template to use it:

**Edit `templates/compose-language.yml`:**
```yaml
services:
  {{NAME}}-dev:
    build:
      context: ../../..
      dockerfile: configs/docker/custom-base.Dockerfile
```

---

## Post-Installation Scripts

```zsh
vde create dotnet \
    "apt-get update -y && apt-get install -y wget apt-transport-https && \
     wget https://packages.microsoft.com/config/debian/12/packages-microsoft-prod.deb -O /tmp/packages-microsoft-prod.deb && \
     dpkg -i /tmp/packages-microsoft-prod.deb && rm /tmp/packages-microsoft-prod.deb && \
     apt-get update -y && apt-get install -y dotnet-sdk-8.0 aspnetcore-runtime-8.0 && \
     su devuser -c 'dotnet tool install --global dotnet-format'"
```

---

## Alias Management

Create composite VMs by adding aliases:

```zsh
# In vm-types.conf
lang|vde-js|js,javascript,node,nodejs,typescript|JavaScript|-|zsh /vde/scripts/setup/js-init.zsh|-|2211

# Now both create the same VM:
vde create js
vde create typescript
```

The install steps live in the VM's setup script (`scripts/setup/js-init.zsh`, which
configures the signed NodeSource apt repository in zsh), not inline in the
registry row. Setup scripts must stay zsh-only; the few unavoidable vendor
installers are listed in [bash-exceptions.md](../governance/bash-exceptions.md).

---

## Docker Compose Overrides

For custom container configurations, you can add overrides to the docker-compose.yml after creation:

```yaml
# configs/docker/python/docker-compose.yml (after creation)
services:
  vde-python:
    # ... existing config ...
    environment:
      - CUSTOM_VAR=value
    volumes:
      - ./custom-mount:/custom/path
```

---

## Inter-Container Communication

All containers share the `vde-net` Docker network and have SSH agent forwarding enabled.

### VM-to-VM Communication via SSH

With SSH agent forwarding, you can SSH between VMs using your host's SSH keys:

```zsh
# From Go VM, connect to Python VM
ssh vde-go
ssh vde-python                # Uses your host's SSH keys!
ssh vde-python pwd            # Run command on Python VM
scp vde-python:/data/file .   # Copy file from Python VM
```

### Full Stack Development

```zsh
# Create a full stack: API, database, cache
vde create python postgres redis
vde start python postgres redis

# From Python VM (API layer)
ssh vde-python
ssh vde-postgres psql -U devuser -c "SELECT * FROM users"
ssh vde-redis redis-cli INCR counter
```

### Microservices Architecture

```zsh
# Create microservices
vde create go python rust postgres
vde start go python rust postgres

# From Go VM (API gateway)
ssh vde-go
# Call other services
ssh vde-python svc_status
ssh vde-rust analytics
ssh vde-postgres "psql -c 'SELECT COUNT(*) FROM orders'"
```

### Service Mesh Pattern

```zsh
# Create service mesh
vde create nginx go python postgres redis
vde start nginx go python postgres redis

# From Nginx VM (edge router)
ssh vde-nginx
# Proxy requests to backend services
curl http://vde-go:8080/health
curl http://vde-python:8000/api/status
```

### Using Host Communication

Execute commands on your host from within any VM:

```zsh
# From within any VM
to-host ls ~/dev                    # List host's dev directory
to-host docker ps                   # Check host's containers
to-host tail -f logs/app.log        # View host's log files
```

### Git Operations from VMs

Use your host's SSH keys for Git operations from within any VM:

```zsh
# From within any VM
git clone github.com:user/repo      # Uses your GitHub key
git push origin main                # Authentication works automatically
```

---

## The Configurable Projects Base

Every Spoke syncs its workspace to a subfolder beneath a single **Projects base**: alias `rust` lands at `<base>/rust`, alias `python` at `<base>/python`, each bind-mounted into the Spoke at `/home/devuser/workspace`. By default the base is `$VDE_ROOT/projects`, but it is fully relocatable — a lever worth pulling if you already keep a central or shared projects tree.

### Pointing VDE at an existing central tree

The base may be **any directory you control**, inside or outside the Forge. The Forge expands `~` and environment variables, creates the directory if it is missing, and requires only that it be writable:

```zsh
# Interactive: choose it during onboarding
vde path-of-the-foundling          # the prompt accepts e.g. $HOME/Projects
```

VDE never overwrites or deletes anything already living at the base. It *adds* its own `<base>/<alias>` subfolders, and if a same-named folder already exists it is **adopted** (used as-is), never clobbered. This makes it safe to aim VDE straight at a directory where you already keep work — a shared `~/Projects`, a monorepo checkout, or a synced cloud folder.

### Non-interactive overrides (`--projects-dir`, `VDE_PROJECTS_DIR`)

For scripted or headless provisioning, skip the prompt:

```zsh
# Flag form
vde init --projects-dir "$HOME/Projects"

# Environment form (honored by init)
export VDE_PROJECTS_DIR="$HOME/code/vde"
vde init
```

Either way the Forge records your choice as an **absolute path** in the `VDE_PROJECTS_DIR` key of `.env`, which becomes the single source of truth for every Spoke.

### Re-pointing later with `vde set-projects-dir`

Change your mind after you have been working? Re-point the base in one ritual:

```zsh
vde set-projects-dir "$HOME/Projects"
```

This safely **moves** your existing alias folders from the old base to the new one, updates `.env`, and regenerates Spoke configs. Two guarantees matter: name **collisions are skipped** (if `<new-base>/python` already exists, the old one is left in place rather than overwritten or deleted), and **no image rebuild** is required — Spokes pick up the new location on their next start.

### Data integrity on teardown (`vde nuke`)

`vde nuke` erases VDE's own state — Spokes, images, the Docker network and volumes, the VDE SSH config and keys at `$HOME/.ssh/vde`, and operational directories (`logs/`, `env-files/`, caches, locks). It **never** deletes your Projects base or your database `data/`, whether they live in-tree or at an external path you configured. Before destroying anything, nuke **offers to move** your projects and data to a safe location first (or to continue as-is), and warns you if they currently sit inside the VDE folder. Removing the VDE program itself afterward is a manual step — you delete the VDE folder by hand.

See the [Getting Started](getting-started.md) and [Foundling Guide](foundling-guide.md) for the student-facing narrative of these same mechanics.

---

[← Back to README](../../README.md)
