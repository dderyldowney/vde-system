# SSH Configuration

All VMs use SSH key-based authentication. The `create-virtual-for` script automatically adds entries to `~/.ssh/config`.

[← Back to README](../README.md)

---

## Manual Setup

If you need to manually configure SSH:

### 1. Generate SSH Keys

If you don't have them:

```bash
ssh-keygen -t ed25519
```

### 2. Copy Public Key for Containers

```bash
cp ~/.ssh/id_ed25519.pub ~/dev/public-ssh-keys/
```

### 3. Set Correct Permissions

```bash
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub
chmod 600 ~/.ssh/config
```

### 4. Add SSH Config Entry

Example for `go-dev`:

```ssh-config
# Go Dev VM
Host go-dev
    HostName localhost
    Port 2205
    User devuser
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
```

---

## Connecting via SSH

### Language VMs

```bash
ssh go-dev
ssh python-dev
ssh rust-dev
```

### Service VMs

```bash
ssh postgres
ssh redis
ssh mongodb
```

---

## SSH from Within Containers

All containers share the `dev-net` Docker network, so they can communicate with each other:

```bash
# From python-dev, connect to postgres
ssh postgres
psql -h localhost -U devuser
```

---

## SSH Config Template

VDE uses this template for new entries:

```
Host {{HOST}}
    HostName localhost
    Port {{SSH_PORT}}
    User devuser
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
    # {{COMMENT}}
```

---

## Troubleshooting SSH

### Permission Denied

```bash
# Ensure correct permissions
chmod 600 ~/.ssh/id_ed25519
chmod 600 ~/.ssh/config
chmod 644 ~/.ssh/id_ed25519.pub
```

### Connection Refused

```bash
# Check if container is running
docker ps | grep <name>

# Check container logs
docker logs <name>

# Restart SSHd in container
docker exec <name> /usr/sbin/sshd
```

### Verbose Debugging

```bash
ssh -v go-dev
```

---

[← Back to README](../README.md)
