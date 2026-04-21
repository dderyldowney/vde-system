# QUICK-START
<!-- @shared-law (Sovereign Documentation) -->
<!-- @armor (Student Documentation) -->
# Quick Start

Get up and running with VDE in minutes.

[← Back to README](../README.md)

---

## First-Time Setup

```zsh
# 1. Navigate to your dev directory
cd VDE

# 2. Ignite the Forge (The Path of the Foundling)
vde path-of-the-foundling

# 3. Create your first VM (e.g., Go)
vde create go

# 4. Start and Enter the Spoke
vde start go
vde enter go
```

---

## What Just Happened?

When you ran `vde path-of-the-foundling`:
1. **Interactive Induction**: A step-by-step ritual guided you through project initialization.
2. **Infrastructure Smelting**: Networks created and directory permissions enforced.
3. **Identity Forgery**: `vde_student` SSH keys generated and agent primed.
4. **Foundation Building**: Foundational `vde-base` image built and baked with identity.
5. **Spine Check**: Core Tetrad (Zsh, Git, Docker, SSH) verified and Git hooks installed.

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
