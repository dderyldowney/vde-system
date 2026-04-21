# Best Practices
<!-- @shared-law (Sovereign Documentation) -->

Recommended practices for working with VDE effectively.

[← Back to README](../README.md)

---

## Development Workflow

### 1. Work in Projects Directory

All code is in `projects/<lang>/` which persists on your host.

```zsh
# Good: Work in projects directory
cd ~/dev/projects/python/my-api
# Edit files, they appear in container at ~/workspace

# Access via SSH - files are mounted from host
ssh vde-python
cd ~/workspace  # Mounted from ~/dev/projects/python/
# Files persist here even after rebuild
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

```zsh
# Git repo on host
cd ~/dev/projects/python/my-api
git commit -am "Work in progress"

# Container can be rebuilt anytime
vde start python --rebuild
# Your code is still there
```

### 4. Use Service VMs

Databases and caches run in separate containers.

```zsh
# Good: Use separate service containers
vde create postgres
vde create redis

# Connect from language container
ssh vde-python
psql -h postgres -U devuser  # Works!
```

### 5. SSH Between Containers

All VMs share the `vde-net` network and have SSH agent forwarding enabled.

```zsh
# From vde-python, connect to postgres using host's SSH keys
ssh vde-postgres
psql -h localhost -U devuser

# Or use service names as hostnames
psql -h postgres -U devuser
```

**VM-to-VM Best Practices:**
- Use SSH for service-to-service communication (leverages agent forwarding)
- All VMs can authenticate using your host's SSH keys
- Git operations work from any VM using your credentials
- No need to copy keys to individual VMs

---

## Container Management

### Start Only What You Need

```zsh
# Good: Start only what you're using
vde start python postgres

# Avoid: Starting everything unless needed
vde start all  # Uses more resources
```

### Stop When Done

```zsh
# Stop VMs to free resources
vde stop python postgres

# Or stop all
vde stop all
```

### Check Status Regularly

```zsh
# See what's running
docker ps
```

---

## Configuration

### Keep SSH Config Updated

VDE automatically manages `~/.ssh/vde/config`, but verify it:

```zsh
# Check SSH entries
cat ~/.ssh/vde/config | grep -A 5 "Host "
```

### Backup Important Data

```zsh
# Service data persists on host
ls ~/data/postgres/

# Back it up regularly
tar -czf postgres-backup.tar.gz ~/data/postgres/
```

### Use Environment Variables

Store configuration in `env-files/<name>.env`:

```zsh
# env-files/python.env
SSH_PORT=2213
PYTHON_VERSION=3.11
DEBUG=true
```

---

## Performance

### Rebuild Only When Needed

See [Rebuild Guidelines](./rebuild-guidelines.md) for details.

### Monitor Resource Usage

```zsh
# Check container resource usage
docker stats

# See disk usage
docker system df
```

---

## Security

### SSH Agent Forwarding

VDE uses SSH agent forwarding for secure authentication.

**Security Model:**
- Private keys **NEVER leave** the host machine
- Only the authentication socket is forwarded to containers
- Containers cannot modify the SSH agent socket (read-only mount)
- All VMs can authenticate using your host's SSH keys

**Best Practices:**
- Let VDE handle SSH setup automatically (no manual configuration needed)
- Your SSH keys are automatically detected and loaded
- Multiple SSH key types are supported (ed25519, RSA, ECDSA, DSA)
- Use `vde ssh-setup status` to view SSH status

### Use SSH Keys Only

Password authentication is disabled. VDE automatically generates SSH keys if you don't have any.

```zsh
# VDE handles this automatically - no manual steps needed
vde create python
vde start python
# SSH keys are detected, generated if needed, and loaded automatically
```

### Keep Containers Updated

```zsh
# Rebuild with latest base image
vde start python --rebuild --no-cache
```

### Use Sudo Judiciously

You have passwordless sudo in containers, but use it carefully:

```zsh
# In container
sudo apt-get update  # Needed for system packages
# But prefer user-space tools when possible
```

---

## Troubleshooting

### Check Logs First

```zsh
# Container logs
docker logs <container-name>
```

### Verify Networking

```zsh
# Check Docker network
docker network ls | grep vde-net

# Test connectivity
docker exec vde-python ping postgres
```

### Use Verbose SSH

```zsh
# Debug SSH issues
ssh -v vde-go
```

---

## Documentation

### Keep README Updated

Each project should have its own README:

```zsh
# projects/python/my-api/README.md
# Document how to run, test, and deploy
```

---

[← Back to README](../README.md)
