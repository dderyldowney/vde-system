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
| Base images update | `vde rebuild --no-cache base <vm>` | A named-Spoke rebuild reuses vde-base; include `base` to re-forge it first, then the Spoke |
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

**The build cache is cleaned after every successful rebuild or create.** Docker's
build cache grows by tens of gigabytes over a few `--no-cache` rebuilds and fills the
disk, so once every build in a command has succeeded VDE removes it
(`docker builder prune --all -f`, which never touches images, containers or volumes).
The cost is that the *next* rebuild starts cold and takes longer. If you are iterating
and want fast incremental rebuilds, keep the cache and clean it yourself later:

```zsh
vde rebuild --keep-cache python     # keep Docker's build cache after this build
vde clean --dry-run                 # how much would be freed?
vde clean                           # free it (the same cleanup, on demand)
```

A build that fails keeps its cache so the retry is fast.

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

Because VDE now cleans the build cache after every successful rebuild (see "Rebuild
Takes Too Long"), the cached hydration layer is normally already gone, so a plain
`vde rebuild python` re-runs the hydration layer and **may advance the interpreter**.
To keep the interpreter you have, rebuild with `--keep-cache` (and the cache from that
build stays, so the next plain rebuild can reuse it):

```zsh
vde rebuild --keep-cache python
```

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
