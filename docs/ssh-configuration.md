# SSH Configuration & Agent Forwarding

VDE provides **automatic SSH configuration** and **SSH agent forwarding** for seamless VM-to-VM, VM-to-Host, and VM-to-External communication.

[← Back to README](../README.md)

---

## Overview

VDE handles all SSH setup automatically through the `vm-common` library and related SSH functions:

- **Automatic SSH key detection**: Finds and uses all your SSH keys (ed25519, RSA, ECDSA, DSA, security keys)
- **Automatic SSH agent management**: Starts agent, loads keys, no manual configuration
- **Automatic SSH config generation**: Creates entries for all VMs in `~/.ssh/config`
- **SSH agent forwarding**: VMs access your host's SSH keys securely (keys never leave the host)
- **Port-based authentication**: Each VM gets a unique SSH port for isolation

**No manual setup required** - VDE handles everything when you create or start VMs.

### SSH Key Types Supported

VDE automatically detects and uses any of these key types (in priority order):

- **id_ed25519** (preferred, most secure)
- **id_ecdsa_sk** (security key)
- **id_ed25519_sk** (security key)
- **id_ecdsa**
- **id_rsa**
- **id_dsa** (legacy)

Priority order: ed25519 > ecdsa-sk > ed25519-sk > ecdsa > rsa > dsa

---

## How It Works

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Host Machine                            │
│                                                                  │
│  ┌──────────────┐         ┌──────────────────────────────────┐ │
│  │ SSH Keys     │         │ SSH Agent                        │ │
│  │ ~/.ssh/      │◄────────┤ • Holds private keys             │ │
│  │ id_ed25519  │         │ • Never exposes keys directly     │ │
│  │ id_rsa      │         │ • Socket: $SSH_AUTH_SOCK         │ │
│  │ ...         │         └──────────────▲───────────────────┘ │
│  └──────────────┘                        │                     │
│                                          │ Socket Forwarding   │
│                                          ▼                     │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ Docker Container (VM)                                     │ │
│  │                                                           │ │
│  │  • SSH_AUTH_SOCK=/ssh-agent/sock                          │ │
│  │  • Socket mounted read-only from host                     │ │
│  │  • Can use host's SSH keys for authentication             │ │
│  └──────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Security Model

- **Private keys NEVER leave the host**: Only the authentication socket is forwarded
- **Read-only mount**: Containers cannot modify the SSH agent socket
- **Automatic key management**: All your keys are detected and loaded automatically
- **No manual configuration**: VDE handles agent startup and key loading

---

## Automatic SSH Setup

### What Happens Automatically

When you run `create-virtual-for` or `start-virtual`, VDE automatically:

1. **Starts SSH agent** if not running
2. **Detects all SSH keys** in `~/.ssh/`
3. **Generates a key** if you don't have one (ed25519)
4. **Loads all keys** into the agent
5. **Generates SSH config** entries for VM-to-VM communication

### No Manual Steps Required

```bash
# Just create and start VMs - SSH is handled automatically
./scripts/create-virtual-for python
./scripts/start-virtual python
ssh python-dev  # Works immediately, no setup needed
```

### SSH Key Types Supported

VDE automatically detects and uses any of these key types:

- **id_ed25519** (preferred)
- **id_ecdsa**
- **id_rsa**
- **id_ecdsa_sk**
- **id_ed25519_sk**
- **id_dsa** (legacy)

Priority order: ed25519 > ecdsa > rsa > dsa

---

## VM-to-VM Communication

SSH from one VM to another using your host's SSH keys:

### Basic Examples

```bash
# From your host
ssh go-dev                    # Connect to Go VM

# From within Go VM
ssh python-dev                # SSH to Python VM
ssh rust-dev pwd              # Run command on Rust VM
scp python-dev:/data/file .   # Copy file from Python VM
```

### Full Stack Example

```bash
# Create and start VMs
./scripts/create-virtual-for python postgres redis
./scripts/start-virtual python postgres redis

# From Python VM, connect to services
ssh python-dev
ssh postgres-dev psql -U devuser    # Connect to PostgreSQL
ssh redis-dev redis-cli             # Connect to Redis
```

### Microservices Example

```bash
# Create microservices architecture
./scripts/create-virtual-for go python rust postgres
./scripts/start-virtual go python rust postgres

# From Go VM (API gateway)
ssh go-dev
ssh python-dev svc_status           # Call Python service
ssh rust-dev analytics              # Call Rust analytics
ssh postgres-dev "psql -c 'SELECT * FROM users'"  # Query database
```

### SSH Config for VM-to-VM

VDE automatically generates these entries in `~/.ssh/config`:

```ssh-config
# Python Dev VM
Host python-dev
    HostName localhost
    Port 2200
    User devuser
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes

# Go Dev VM
Host go-dev
    HostName localhost
    Port 2205
    User devuser
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
```

This allows VMs to SSH to each other via `localhost:<port>`.

---

## VM-to-Host Communication

Execute commands on your host from within any VM:

### Using the `to-host` Helper

```bash
# From within any VM
to-host ls ~/dev                    # List host's dev directory
to-host tail -f logs/app.log        # View host's log files
to-host docker ps                   # Check host's containers
```

### Direct Docker Commands

```bash
# From within any VM
docker exec python-dev ls           # Execute in Python VM
docker exec postgres-dev psql       # Execute in PostgreSQL
```

---

## VM-to-External Communication

Use your host's SSH keys for external services from within any VM:

### Git Operations

```bash
# From within any VM - uses your GitHub/GitLab keys
git clone github.com:user/repo
git push origin main
```

### External SSH

```bash
# From within any VM - uses your host keys
ssh user@external-server.com
scp user@external-server.com:/path/file .
```

---

## Checking SSH Status

### View SSH Status

```bash
# Interactive status display
./scripts/ssh-agent-setup
# OR using vde CLI
vde health  # Includes SSH status check
```

This shows:
- SSH agent running status
- Available SSH keys
- Keys loaded in agent
- Running VMs
- Usage examples

### Manual Commands

```bash
# Check if SSH agent is running
ps aux | grep ssh-agent

# View loaded keys
ssh-add -l

# View SSH config
cat ~/.ssh/config

# Test SSH connection
ssh -v python-dev
```

---

## Manual SSH Operations (Optional)

While VDE handles everything automatically, you can perform manual operations if needed:

### Add a New Key to Agent

```bash
ssh-add ~/.ssh/new_key
```

### Start SSH Agent Manually

```bash
eval "$(ssh-agent -s)"
ssh-add
```

### Stop Agent

```bash
ssh-agent -k
```

### Restart Agent

```bash
eval "$(ssh-agent -s)" && ssh-add
```

---

## Troubleshooting

### SSH Agent Not Running

**Symptom**: `SSH_AUTH_SOCK` not set or agent not found

**Solution**: VDE starts agent automatically, but you can manually start:

```bash
eval "$(ssh-agent -s)"
ssh-add
```

### Keys Not Loaded in Agent

**Symptom**: `ssh-add -l` shows "no identities"

**Solution**: Add your keys:

```bash
ssh-add ~/.ssh/id_ed25519
# Or add all keys
for key in ~/.ssh/id_*; do [ -f "$key" ] && ssh-add "$key"; done
```

### VM-to-VM SSH Not Working

**Symptom**: Can't SSH from one VM to another

**Solution**: Check that both VMs are running:

```bash
docker ps | grep -E "python|go"
```

Regenerate VM SSH config:

```bash
./scripts/ssh-agent-setup
```

### Permission Denied (Publickey)

**Symptom**: `Permission denied (publickey)`

**Solutions**:

1. Check key permissions:
```bash
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub
```

2. Verify key is in agent:
```bash
ssh-add -l
```

3. Check SSH config:
```bash
cat ~/.ssh/config
```

4. Rebuild VM with updated keys:
```bash
./scripts/shutdown-virtual python
./scripts/start-virtual python --rebuild
```

### Connection Refused

**Symptom**: `ssh: connect to host localhost port 2200: Connection refused`

**Solutions**:

1. Check if container is running:
```bash
docker ps | grep python
```

2. Check container logs:
```bash
docker logs python-dev
```

3. Restart container:
```bash
./scripts/shutdown-virtual python
./scripts/start-virtual python
```

### Verbose Debugging

```bash
# Enable verbose SSH output
ssh -v python-dev

# More verbose
ssh -vv python-dev

# Maximum verbosity
ssh -vvv python-dev
```

---

## Migration from Manual Setup

If you previously set up SSH manually:

### Old Way (Manual)

```bash
# 1. Generate key
ssh-keygen -t ed25519

# 2. Copy to VDE
cp ~/.ssh/id_ed25519.pub ~/dev/public-ssh-keys/

# 3. Create SSH entry manually
cat >> ~/.ssh/config << 'EOF'
Host python-dev
    HostName localhost
    Port 2200
    User devuser
    IdentityFile ~/.ssh/id_ed25519
EOF
```

### New Way (Automatic)

```bash
# Just create VM - everything else is automatic
./scripts/create-virtual-for python
./scripts/start-virtual python
```

All manual steps are now handled by VDE automatically.

---

## Best Practices

1. **Let VDE handle SSH setup**: Don't manually configure SSH agent or keys
2. **Use VM aliases**: Use `python-dev` instead of `localhost -p 2200`
3. **Use the vde CLI**: Prefer `vde create/start/stop` over direct script calls
4. **Check status with vde health**: Run `vde health` for comprehensive system status
5. **Multiple keys are supported**: All your keys are automatically detected and loaded
6. **Security keys work too**: YubiKey and other security keys are automatically detected
7. **Keys never leave the host**: Agent forwarding is secure by design
8. **VM-to-VM communication**: Use SSH for service-to-service communication

---

## Related Documentation

- [Quick Start](quick-start.md) - Getting started with VDE
- [Advanced Usage](advanced-usage.md) - VM-to-VM communication patterns
- [Architecture](architecture.md) - Technical architecture details
- [Troubleshooting](troubleshooting.md) - Common issues and solutions

---

[← Back to README](../README.md)
