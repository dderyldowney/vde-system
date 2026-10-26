# Rebuild Guidelines
<!-- @shared-law (Sovereign Law) -->

When and how to rebuild containers in the **Sovereign Baseline (1.5.6)**.

[← Back to README](../../README.md)

---

## Rebuild Decision Matrix

| Scenario | Command | Why |
|----------|---------|-----|
| Daily development | No rebuild needed | Containers are stateless |
| Dockerfiles change | `vde rebuild <vm>` | Rebuild images with new Dockerfile |
| SSH keys change | `vde rebuild <vm>` | New keys need to be baked in |
| Environment variables change | `vde rebuild <vm>` | env-files are read at build time |
| Base images update | `vde rebuild --no-cache <vm>` | Ensure fresh base image |
| Advance Python interpreter (pyenv) | `vde rebuild --no-cache python` | Re-resolves & recompiles the latest stable CPython; a plain rebuild keeps the pinned version while build inputs are unchanged |
| Installing system packages | `vde rebuild <vm>` | Packages install during build |

---

## Rebuild Commands

### Single VM

```zsh
# Rebuild single VM
vde rebuild python

# Full clean rebuild
vde rebuild --no-cache python
```

### Multiple VMs

```zsh
# Rebuild multiple VMs
vde rebuild python go rust

# Rebuild all VMs
vde rebuild all
```

---

## What Rebuild Affects

### Preserved Across Rebuilds

- Source code in `$HOME/workspace/` (synced to `projects/<name>/` on Hub)
- Data in `data/<name>/` (for services)
- SSH configuration entries
- Environment files (unless you edit them)

### Rebuilt

- Docker images
- Container filesystem (outside of workspace/data)
- Installed system packages
- User configuration inside container (outside of persisted volumes)

---

## Common Rebuild Scenarios

### After Changing vde-base.Dockerfile

```zsh
# Rebuild all VMs that use the base image
vde rebuild all
```

### After Adding System Packages

```zsh
# Rebuild specific VM
vde rebuild python
```

### After Updating SSH Keys

```zsh
# Rebuild to bake in new keys
vde rebuild all
```

### After Base Image Update

```zsh
# Full clean rebuild
vde rebuild --no-cache all
```

---

## Troubleshooting Rebuilds

### Rebuild Takes Too Long

If you are iterating quickly and want to use cache:

```zsh
# Start with rebuild (inherits Docker cache)
vde start python --rebuild
```

### Rebuild Doesn't Pick Up Changes

Ensure you are using the standard ritual:

```zsh
vde rebuild <vm>
```

#### Python interpreter does not advance (pyenv)

`vde-python`'s CPython is compiled from source by pyenv when the image's hydration
layer is built. The version installed is whatever pyenv resolves as the newest
stable CPython **at the moment that layer actually builds** — there is no pinned
version file.

A plain `vde rebuild python` normally keeps the CPython you already have, because
Docker reuses the cached hydration layer. That reuse is not guaranteed: it holds
only while the build inputs are unchanged (the `python-init.zsh` hydration script,
anything under `lib/`, and the `vde-base` image) **and** the cached layer is still
present. Editing those inputs, updating `vde-base`, pruning the Docker build cache,
or building on a fresh host re-runs the hydration layer, and pyenv then resolves the
newest stable CPython — so a plain rebuild can advance the interpreter as a side
effect. To see what you actually have, run `python --version` inside the Spoke.

To advance `vde-python` to the latest stable CPython deliberately, force a clean
build so the resolver always re-runs:

```zsh
vde rebuild --no-cache python
```

This recompiles CPython from source (slower). Use it when you intend to move the
interpreter forward.

### Container Won't Start After Rebuild

```zsh
# Check logs
vde logs <alias>

# Check container info
vde info <alias>
```

---

[← Back to README](../../README.md)
**This is the Way.**
