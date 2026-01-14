# Troubleshooting

Common issues and solutions for VDE.

[← Back to README](../README.md)

---

## Port Conflicts

**Problem:** A port is already in use.

```bash
# See what's using a port
lsof -i :2205

# Stop conflicting VM
./scripts/shutdown-virtual go

# Restart VM
./scripts/start-virtual go
```

---

## SSH Agent Issues

**Problem:** SSH agent forwarding not working.

```bash
# Check SSH agent is running
ps aux | grep ssh-agent

# Check SSH_AUTH_SOCK is set
echo $SSH_AUTH_SOCK

# View loaded keys
ssh-add -l

# Restart SSH agent (VDE does this automatically, but you can manually)
eval "$(ssh-agent -s)"
ssh-add

# Check SSH status
./scripts/ssh-agent-setup
```

**Problem:** VM-to-VM SSH not working.

```bash
# Check both VMs are running
docker ps | grep -E "python|go"

# Regenerate VM SSH config
./scripts/ssh-agent-setup

# Test SSH connection
ssh -v python-dev
```

**Problem:** Git operations fail with authentication errors.

```bash
# Verify SSH agent has keys
ssh-add -l

# Add keys if needed
ssh-add ~/.ssh/id_ed25519

# Test GitHub/GitLab SSH connection
ssh -T git@github.com
```

---

## SSH Connection Issues

**Problem:** Can't connect to a VM via SSH.

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

---

## Permission Denied

**Problem:** SSH permission denied error.

```bash
# Ensure correct permissions
chmod 600 ~/.ssh/id_ed25519
chmod 600 ~/.ssh/config
chmod 644 ~/.ssh/id_ed25519.pub
```

---

## Container Won't Start

**Problem:** Container fails to start.

```bash
# Check logs
docker logs <container-name>

# Rebuild with no cache
./scripts/start-virtual <vm-name> --rebuild --no-cache

# Check docker-compose.yml syntax
docker-compose -f configs/docker/<vm-name>/docker-compose.yml config
```

---

## VSCode Remote-SSH Can't Connect

**Problem:** VSCode can't connect via Remote-SSH.

```bash
# Verify SSH works from terminal
ssh go-dev

# Check VSCode Remote-SSH settings
# ~/.ssh/config should be readable

# Try reloading VSCode window
# Cmd+Shift+P > "Developer: Reload Window"
```

---

## VM Already Exists

**Problem:** Can't create a VM that already exists.

```bash
# Just start it instead
./scripts/start-virtual python

# Or check if it's running
./scripts/vde-ai "what's running?"
```

---

## Unknown VM Type

**Problem:** "Unknown VM" error when creating.

```bash
# Check available VMs
./scripts/list-vms

# Use exact name from list
./scripts/create-virtual-for python  # not "pyton"
```

---

## Data Persistence Issues

**Problem:** Data not persisting in service VMs.

```bash
# Check data directory exists
ls -la ~/data/postgres

# Verify volume mount in container
docker inspect postgres | grep -A 10 Mounts

# Don't remove and recreate - data is in ~/data/
```

---

## Docker Network Issues

**Problem:** Containers can't communicate.

```bash
# Check dev-net network exists
docker network ls | grep dev-net

# Recreate network if needed
docker network create dev-net

# Restart containers
./scripts/start-virtual all
```

---

## Getting Help

If you're stuck:

```bash
# Get general help
./scripts/vde-ai "help"

# Use chat mode for interactive help
./scripts/vde-chat
[VDE] → help
[VDE] → what can I do?

# Check the logs
tail -f ~/dev/logs/vde-ai.log
```

---

## Complete Reset

If something is seriously wrong and you want to start fresh:

```bash
# Stop everything
./scripts/vde-ai "stop everything"

# Remove all containers (careful!)
docker ps -a | grep -E "dev$|[a-z]+$" | awk '{print $1}' | xargs docker rm -f

# You can now recreate VMs from scratch
./scripts/vde-ai "create python"
```

---

[← Back to README](../README.md)
