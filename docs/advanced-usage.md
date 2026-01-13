# Advanced Usage

Advanced techniques and patterns for power users.

[← Back to README](../README.md)

---

## Custom Installation Commands

### Multi-Step Installation

```bash
# Download and install from URL
./scripts/add-vm-type zig \
    "apt-get update && apt-get install -y wget && \
     wget https://ziglang.org/download/0.11.0/zig-linux-x86_64-0.11.0.tar.xz && \
     tar -xf zig-linux-x86_64-0.11.0.tar.xz && \
     mv zig-linux-x86_64-0.11.0 /opt/zig && \
     ln -s /opt/zig/zig /usr/local/bin/zig"
```

### Install as devuser

```bash
# Rust-style installers
./scripts/add-vm-type rust \
    "su devuser -c 'curl --proto =https --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y'"
```

---

## Multiple Service Ports

```bash
# For services with multiple ports
./scripts/add-vm-type --type service --svc-port 80,443 nginx \
    "apt-get update -y && apt-get install -y nginx-extras"
```

---

## Custom Display Names

```bash
# Override the auto-generated display name
./scripts/add-vm-type --display "Rust Programming Language" rust \
    "apt-get update -y && apt-get install -y rustc"
```

---

## Environment-Specific Installations

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

```bash
./scripts/add-vm-type dotnet \
    "apt-get update -y && apt-get install -y wget apt-transport-https && \
     wget https://packages.microsoft.com/config/debian/12/packages-microsoft-prod.deb -O /tmp/packages-microsoft-prod.deb && \
     dpkg -i /tmp/packages-microsoft-prod.deb && rm /tmp/packages-microsoft-prod.deb && \
     apt-get update -y && apt-get install -y dotnet-sdk-8.0 aspnetcore-runtime-8.0 && \
     su devuser -c 'dotnet tool install --global dotnet-format'"
```

---

## Alias Management

Create composite VMs by adding aliases:

```bash
# In vm-types.conf
lang|js|node,nodejs,typescript|JavaScript|apt-get update && curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - && apt-get install -y nodejs && npm install -g typescript|

# Now both create the same VM:
./scripts/create-virtual-for js
./scripts/create-virtual-for typescript
```

---

## Docker Compose Overrides

For custom container configurations, you can add overrides to the docker-compose.yml after creation:

```yaml
# configs/docker/python/docker-compose.yml (after creation)
services:
  python-dev:
    # ... existing config ...
    environment:
      - CUSTOM_VAR=value
    volumes:
      - ./custom-mount:/custom/path
```

---

## Inter-Container Communication

All containers share the `dev-net` Docker network:

```bash
# From python-dev, connect to postgres
ssh postgres
psql -h postgres -U devuser

# Or from within the container
docker exec python-dev psql -h postgres -U devuser
```

---

[← Back to README](../README.md)
