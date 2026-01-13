# Best Practices

Recommended practices for working with VDE effectively.

[← Back to README](../README.md)

---

## Development Workflow

### 1. Work in Projects Directory

All code is in `projects/<lang>/` which persists on your host.

```bash
# Good: Work in projects directory
cd ~/dev/projects/python/my-api
# Edit files, they appear in container at ~/workspace

# Avoid: Editing files only in container
ssh python-dev
# Files created here may be lost on rebuild
```

### 2. Use VSCode Remote-SSH

Edit code locally with full IDE support.

```
1. Connect VSCode to VM via Remote-SSH
2. Open the workspace folder
3. Edit files with full language support
4. Use integrated terminal for commands
```

### 3. Commit Often

Your code is safe on the host, containers are ephemeral.

```bash
# Git repo on host
cd ~/dev/projects/python/my-api
git commit -am "Work in progress"

# Container can be rebuilt anytime
./scripts/start-virtual python --rebuild
# Your code is still there
```

### 4. Use Service VMs

Databases and caches run in separate containers.

```bash
# Good: Use separate service containers
./scripts/create-virtual-for postgres
./scripts/create-virtual-for redis

# Connect from language container
ssh python-dev
psql -h postgres -U devuser  # Works!
```

### 5. Leverage AI Tools

Claude Code, Cursor, Copilot all work with VDE.

```bash
# Use Claude Code with VDE
cd ~/dev/projects/python/my-api
claude
# Claude can edit files and run commands via SSH
```

### 6. SSH Between Containers

All VMs share the `dev-net` network for inter-container communication.

```bash
# From python-dev, connect to postgres
ssh postgres
psql -h localhost -U devuser

# Or use service names as hostnames
psql -h postgres -U devuser
```

---

## Container Management

### Start Only What You Need

```bash
# Good: Start only what you're using
./scripts/start-virtual python postgres

# Avoid: Starting everything unless needed
./scripts/start-virtual all  # Uses more resources
```

### Stop When Done

```bash
# Stop VMs to free resources
./scripts/shutdown-virtual python postgres

# Or use VDE AI
./scripts/vde-ai "stop everything"
```

### Check Status Regularly

```bash
# See what's running
./scripts/vde-ai "what's running?"

# Or check Docker directly
docker ps
```

---

## Configuration

### Keep SSH Config Updated

VDE automatically manages `~/.ssh/config`, but verify it:

```bash
# Check SSH entries
cat ~/.ssh/config | grep -A 5 "Host "
```

### Backup Important Data

```bash
# Service data persists on host
ls ~/data/postgres/

# Back it up regularly
tar -czf postgres-backup.tar.gz ~/data/postgres/
```

### Use Environment Variables

Store configuration in `env-files/<name>.env`:

```bash
# env-files/python.env
SSH_PORT=2200
PYTHON_VERSION=3.11
DEBUG=true
```

---

## Performance

### Use Dry Run for Testing

```bash
# Preview actions without executing
./scripts/vde-ai --dry-run "start python and postgres"
```

### Rebuild Only When Needed

See [Rebuild Guidelines](./rebuild-guidelines.md) for details.

### Monitor Resource Usage

```bash
# Check container resource usage
docker stats

# See disk usage
docker system df
```

---

## Security

### Use SSH Keys Only

Password authentication is disabled. Use SSH keys.

```bash
# Generate keys if needed
ssh-keygen -t ed25519

# Copy to VDE
cp ~/.ssh/id_ed25519.pub ~/dev/public-ssh-keys/
```

### Keep Containers Updated

```bash
# Rebuild with latest base image
./scripts/build-and-start --rebuild --no-cache
```

### Use Sudo Judiciously

You have passwordless sudo in containers, but use it carefully:

```bash
# In container
sudo apt-get update  # Needed for system packages
# But prefer user-space tools when possible
```

---

## Troubleshooting

### Check Logs First

```bash
# Container logs
docker logs <container-name>

# VDE AI logs
tail -f ~/dev/logs/vde-ai.log
```

### Verify Networking

```bash
# Check Docker network
docker network ls | grep dev-net

# Test connectivity
docker exec python-dev ping postgres
```

### Use Verbose SSH

```bash
# Debug SSH issues
ssh -v go-dev
```

---

## Documentation

### Keep README Updated

Each project should have its own README:

```bash
# projects/python/my-api/README.md
# Document how to run, test, and deploy
```

### Use VDE AI Help

```bash
# Get help anytime
./scripts/vde-ai "help"
./scripts/vde-chat
[VDE] → help
```

---

[← Back to README](../README.md)
