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
BuildKit cannot scope that to VDE: it clears **all unused build cache on the selected
Docker daemon, including cache that belongs to your other projects**, which will start
cold on their next build too. VDE prints which Docker context it is cleaning. The cost
is that the *next* rebuild starts cold and takes longer. If you are iterating
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

Whether a plain `vde rebuild python` keeps the CPython you already have depends on
whether Docker still holds the cached hydration layer. Reuse of that layer holds only
while the build inputs are unchanged (the `python-init.zsh` hydration script, anything
under `lib/`, and the `vde-base` image) **and** the cached layer is still present.
VDE cleans Docker's build cache after every successful rebuild (see "Rebuild Takes
Too Long"), so by default the layer is **gone** and a plain rebuild re-runs the
hydration layer; pyenv then resolves the newest stable CPython, and the interpreter
can advance as a side effect. Editing those inputs, updating `vde-base`, pruning the
cache yourself, or building on a fresh host do the same. To see what you actually
have, run `python --version` inside the Spoke.

To keep the interpreter you have, rebuild with `--keep-cache`. The cache from that
build stays, so the next rebuild can reuse the cached layer:

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
