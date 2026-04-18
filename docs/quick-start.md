# Quick Start

Get up and running with VDE in minutes.

[← Back to README](../README.md)

---

## First-Time Setup

```zsh
# 1. Navigate to your dev directory
cd VDE

# 2. Ignite the Forge (Mandatory Ritual)
vde init

# 3. List all predefined VM types
vde list

# 4. Create a new language VM (auto-allocates SSH port)
vde create go

# 5. Start the VM
vde start go

# 6. Step into the Spoke
vde enter go
```

---

## What Just Happened?

When you ran `vde init`:
1. **Security Environment**: Networks created and directory permissions enforced.
2. **Environment Secrets**: `.env` instantiated from template.
3. **SSH Forgery**: `vde_student` ed25519 key pair generated.
4. **Config Priming**: Active SSH vault primed from canonical artifacts.
5. **Foundation Building**: Foundational `vde-base` image built and baked with identity.
6. **Spine Enforcement**: Git hooks installed.

When you ran `vde create go`:
1. **Port Allocation**: SSH port automatically assigned.
2. **Config Created**: `configs/docker/go/docker-compose.yml` (for documentation).
3. **Directories Created**: `projects/go/`, `logs/go/`.
4. **Environment File**: `env-files/go.env`.

When you ran `vde start go`:
1. **Spoke Ignition**: Spoke-specific Docker image built and container started.
2. **SSH Bridge**: Secure transversal bridge established.

---

## VM-to-VM Communication

With SSH agent forwarding, your Spokes can communicate seamlessly:

```zsh
# From inside your Python Spoke, connect to PostgreSQL
vde enter python
vde_ssh vde-postgres psql -U devuser
```

Your Spokes can talk to each other and external services using **your** credentials, safely forwarded through the Hub.

---

## Next Steps

- **Induction Ritual**: Run `vde path-of-the-foundling` for an interactive tour.
- **Foundling Guide**: Read `docs/FOUNDLING_GUIDE.md` for a simplified manual.
- **Advanced Usage**: Follow the `USER_GUIDE.md` for more rituals.

For more details, see [Command Reference](./command-reference.md).

---

[← Back to README](../README.md)

*[Home](../README.md) | [Quick Start](./quick-start.md) | [Documentation](./)*
