# Rebuild Guidelines
<!-- @shared-law (Sovereign Law) -->

When and how to rebuild containers in the **Sovereign Baseline (1.5.7)**.

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

## Base Image or Spoke: Which One to Rebuild

Every Spoke image is built **on top of** the base image, `vde-base`. Knowing which layer a change lives in tells you what to rebuild.

- **`vde-base`** holds the operating system (Debian), the `devuser` account, zsh and oh-my-zsh, the Spoke SSH config (`configs/ssh/config.spoke`), and the scripts every Spoke starts with: `scripts/vde-entrypoint.zsh`, `scripts/vde-motd.zsh`, `scripts/vde-usb-map.zsh`.
- **A Spoke** is `FROM vde-base`, plus `lib/` and its own `scripts/setup/<spoke>-init.zsh` hydration script.

Two facts follow from that:

1. **A Spoke keeps the base it was built on.** Rebuilding the base does not touch your existing Spokes; each one must be rebuilt to pick the new base up.
2. **A plain `vde rebuild <spoke>` reuses the base image already on your machine.** It never refreshes the base. To refresh the base, name `base` first.

| What changed | Rebuild | Command |
|--------------|---------|---------|
| `vde-base.Dockerfile`, `vde-entrypoint.zsh`, `vde-motd.zsh`, `vde-usb-map.zsh` or `config.spoke` | The base, **then every Spoke you use** | `vde rebuild base <spoke> [<spoke> ...]` |
| `lib/`, a `scripts/setup/<spoke>-init.zsh`, a Spoke Dockerfile | Only the Spokes you use | `vde rebuild <spoke> [<spoke> ...]` |
| Documentation or tests only | Nothing | |
| You want newer operating-system packages | The base from scratch, then your Spokes | `vde rebuild --no-cache --pull base <spoke> [<spoke> ...]` |

Naming `base` before the Spokes rebuilds the base once, then each Spoke in order. `--no-cache` ignores Docker's layer cache; `--pull` also asks Docker for a newer Debian image.

### After `vde upgrade`

`vde upgrade` reads the Dockerfiles in the version you just installed and tells you which case you are in:

- **"REBUILD YOUR BASE IMAGE"**: the update changed something baked into `vde-base`. Rebuild the base and then every Spoke you use. Until you do, your Spokes keep running the old base, and a running Spoke keeps its old image until it is rebuilt and restarted.
- **"REBUILD YOUR SPOKES"**: the update changed how Spokes are built but not the base. Rebuild the Spokes you use; a plain `vde rebuild <spoke>` is right here.
- **"nothing to rebuild"**: the update touched no image inputs.

When in doubt after an upgrade, rebuild the base and your Spokes: `vde rebuild base <spoke> [<spoke> ...]`. It costs time, never correctness.

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
