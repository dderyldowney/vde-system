# Command Reference
<!-- @shared-law (Sovereign Law) -->

Complete reference for all VDE commands in the **Sovereign Baseline (1.5.7)**.

[← Back to README](../../README.md)

---

## General Management

### List Available VMs

```zsh
# List all predefined and custom VMs
vde list

# Filter by type
vde list --lang
vde list --svc

# Search by alias or name
vde list python
```

### Process Status

```zsh
# List all running VDE-managed containers
vde list

# Check status of specific VMs
vde list python postgres
```

### Detailed Information

```zsh
# Inspect container metadata and labels
vde inspect python

# Audit the configuration of a specific Spoke
vde info rust
```

### The Archivist’s Vision

```zsh
# View real-time Markdown-based status grid
vde vision
```

---

## Lifecycle Operations

### Infrastructure Initialization

```zsh
# Hydrate infrastructure, generate vde_student keys, and build base image
vde init

# Force a clean overwrite of all configurations
vde init --force

# Set the Projects base directory without prompting
vde init --projects-dir "$HOME/Projects"
vde init --projects-dir=/srv/students/projects
```

**Projects base precedence** (highest wins): `--projects-dir <path>` flag → exported
`VDE_PROJECTS_DIR` → existing `VDE_PROJECTS_DIR` in `.env` → interactive prompt →
default `${VDE_ROOT_DIR}/projects`.

### Re-point the Projects Base

```zsh
# Move the Projects base to a new location (prompts if path omitted)
vde set-projects-dir "$HOME/Projects"
vde set-projects-dir
```

**Details**:

- Resolves, creates, and validates the new base (expands `~` and env vars,
  absolutizes the path, and requires it to be writable).
- **Moves** each existing per-alias subfolder from the old base to the new one.
  Any name collision is **SKIPPED** — an existing target is never overwritten or
  deleted.
- Updates the `.env` key `VDE_PROJECTS_DIR` and regenerates Spoke compose configs.
- **Refuses** (exit 1, nothing created or moved, `.env` unchanged) while a Spoke of
  an alias that would be moved is running; stop it (`vde stop <name>`) and re-run.
  A running Spoke of an alias that is skipped (collision) or unregistered does not block.
  It also refuses (exit 1) when Docker cannot be queried (missing, not running, not
  permitted, or silent for 20 s where the `timeout` command exists, which stock macOS
  lacks; `VDE_SPD_DOCKER_TIMEOUT` overrides), and (exit 4) when
  `.env` or the directory holding it is not writable, both before anything moves.
  Moving `python` is also blocked by a running `vde-jupyterlab` (its notebooks live in
  `python/jupyterlabs`). A Spoke that starts while a cross-filesystem copy is running is
  detected once the copy finishes: the copy is discarded and the source kept.
  While it runs it holds the per-Spoke locks that `vde start` takes (`.locks/vms/`), so
  a start of an affected Spoke waits and then fails instead of mounting a folder that is
  being moved, and two re-points cannot overlap; a busy lock refuses the re-point
  (exit 9) before anything moves. Known limit: nothing stops a host editor writing to a
  folder while it is copied; close such tools first.
- A move across filesystems copies to `<alias>.vde-moving`, renames it to `<alias>`
  only after the copy succeeded, then deletes the source. A failed copy leaves the
  source whole and removes its own temp; a leftover temp from an earlier interrupted
  run is discarded and retried; a temp that is a symbolic link is refused. A move
  within one filesystem is a plain rename.
- On INT/TERM/HUP (Ctrl-C, kill, closed terminal) it prints how to finish. Re-running the same command completes an
  interrupted move (moved aliases are absent at the old base; `.env` is written after
  the moves). Do not start Spokes in between: they would mount the old base. One
  exception: an interrupt while the old copy of a cross-filesystem move is being
  deleted leaves that old folder behind. The message names it; delete it by hand
  (a re-run skips it as already existing).
- No image rebuild is required; Spokes pick up the new base on their next start.
- Warns (stderr) when an exported `VDE_PROJECTS_DIR` differs from the `.env` value,
  because the exported value outranks `.env`; `vde start` warns the same way.
  Run `unset VDE_PROJECTS_DIR` to use `.env`. Precedence itself is unchanged.
- Reports exactly what was moved and what was skipped. If a folder could not be moved,
  the command leaves `.env` on the old base, prints `ACTION REQUIRED` and exits 1; fix
  the cause and run the same command again (folders already moved are not touched).
  `.env` is rewritten through a temporary file and a rename, so a failed write cannot
  truncate it.

### Spoke Creation

```zsh
# Create configuration and directories for a VM
vde create python
```

**Details**:

- **Atomic Port Allocation**: Automatically reserves a unique SSH port and records it in the Beskar Registry.
- **Workspace Initialization**: Syncs `$HOME/workspace/` to the host's `projects/` directory.

### Ignition and Quenching

```zsh
# Start VMs (ignite)
vde start python
vde start all

# Stop VMs (quench)
vde stop python
vde stop all

# Restart active Spokes
vde restart rust
```

### Maintenance and Re-forging

```zsh
# Rebuild a Spoke's Docker image (refreshes image)
vde rebuild python

# Full clean rebuild without cache
vde rebuild --no-cache python

# Keep Docker's build cache after the build (it is cleaned by default)
vde rebuild --keep-cache python
```

### Freeing Disk Space

```zsh
# How much Docker build cache is there? (changes nothing)
vde clean --dry-run

# Free Docker's build cache. Removes NO images, containers or volumes.
vde clean

# The same command, under the names a first guess might use
vde cleanup
vde cache clean
```

`vde rebuild` and `vde create` already clean the build cache once every build in the
command has succeeded, so `vde clean` is for when that did not happen: you passed
`--keep-cache`, or a build was interrupted. It prints which Docker context it is
cleaning, and reports how much it freed. Cache that a running build is using is left
alone. The next build after a clean starts cold, so it takes longer once. It clears
all unused build cache on that Docker daemon, including cache from your other projects,
because BuildKit cannot scope the clean to VDE. `--dry-run` reports the total as an
upper bound, since cache in use by a running build is skipped.

### Dissolution

```zsh
# Remove a VM instance and its locks
vde remove rust
vde rm rust
```

---

## Execution & Connectivity

### Sovereign Handshake (SSH)

```zsh
# Enter a Spoke's login shell as devuser
vde enter python
```

### Command Execution

```zsh
# Execute a single command inside a Spoke
vde exec go "go version"
```

### Port Identification

```zsh
# Retrieve the assigned SSH port for a Spoke
vde port python
```

### Logs

```zsh
# Tail the logs of a specific Spoke
vde logs redis
```

---

## Orchestration & Clusters

### Tech Stack Clusters

```zsh
# Orchestrate multi-VM tech stacks
vde cluster list
vde cluster start python-stack
vde cluster stop mean-stack
```

### DNS Handshake

```zsh
# Verify cross-Spoke DNS resolution within vde-net
vde dns-check python postgres

# Optional third argument: TCP port to probe (default 22)
vde dns-check python postgres 5432
```

Exit status: 0 when every probe passes, 1 when a probe fails, 2 when `<source_vm>` or `<target_vm>` is missing
(usage is printed).

---

## Usage Errors and Exit Status

```zsh
vde                # prints the usage text, exit 2
vde help           # prints the usage text, exit 0
vde frobnicate     # "Unknown command 'frobnicate'. Run 'vde help' for usage." on stderr, exit 2
```

Put flags after the command: `vde start -q python` works, `vde -q start python` is reported as an unknown
command `-q`. `vde stop`, `restart` and `remove` exit 0 when every target was handled or is already stopped/absent,
and 1 on any unknown alias or failed docker operation. Full table:
[Router and action handlers](../development/router-handlers.md#4-exit-status-of-vde).

---

## Dynamic Expansion

### Register New Spoke Types

```zsh
# Add a new Spoke type to the Beskar Registry
vde add --pkgs "htop,tree" my-custom-vm

# Add a service VM with specific ports
vde add --type service --port 5000 my-api
```

### Permanent Removal

```zsh
# Remove a Spoke type from the Registry
vde uninstall my-custom-vm --skip-confirm
```

### Registry Integrity

```zsh
# Verify Beskar Registry against JSON schemas
vde validate

# Force a re-smelt of the internal VM cache
vde rebuild-cache
```

---

## Onboarding & Maintenance

### Path of the Foundling

```zsh
# Interactive induction ritual for new students
bin/vde path-of-the-foundling
```

### System Health

```zsh
# Run System Spine health checks (Spine Check)
vde health
```

### Upgrading VDE

```zsh
# See what an upgrade would bring in; changes nothing in your working tree
vde upgrade --dry-run

# Bring this install up to date with the branch it is on
vde upgrade
```

`vde upgrade` finds your install from where the script lives, so it works from any directory. It fetches the branch you are on (most installs follow `stable`) and fast-forwards to it. It never merges, rebases or rewrites your history.

- It refuses, and changes nothing, if the install is not a git clone, `HEAD` is detached, there is no `origin` or `origin` lacks your branch, your branch has diverged from `origin`, or you have edited a file the update also changes. Edits to other files are kept.
- It tells you what to rebuild. If the update changes something baked into the base image (`vde-base`) it says **REBUILD YOUR BASE IMAGE**: rebuild the base, then every Spoke you use, with `vde rebuild base <spoke> [<spoke> ...]`. If it changes only how Spokes are built it says to rebuild the Spokes; otherwise nothing. A plain `vde rebuild <spoke>` reuses your existing base image. See [Rebuild Guidelines](../operations/rebuild-guidelines.md#base-image-or-spoke-which-one-to-rebuild).
- Exit status: `0` done or already current, `2` bad option, `3` this install cannot be updated, `13` your copy and `origin` disagree.

### The Pruning Ritual

```zsh
# Print a plan; make no changes by default
vde prune
vde prune --dry-run

# Apply the plan only after confirmation, or skip the prompt
vde prune --apply
vde prune --apply --yes
```

Supported timeframes are `7d` (default), `3d`, `24h`, and `12h`.

- `vde prune` and `vde prune --dry-run` print a plan and change nothing.
- `vde prune --apply` archives old plans, scripts, and release records and deletes old repository housekeeping files; it requires confirmation unless `--yes` is supplied. The current baseline release remains protected.
- Student `logs/` and `backup/` data are excluded from pruning.
- Use `vde clean` to free Docker build-cache disk space.

### The Great Quench

```zsh
# Safe removal of VDE's own state (preserves projects + data)
vde nuke
```

**Details**:

- **Preserves** both the Projects base (`projects/` or `VDE_PROJECTS_DIR`) and the
  database `data/` directory — in-tree or external, they are never deleted.
- Offers to move `projects/` and `data/` to a safe location before proceeding.
- Removes VDE's own state: Spokes, images, the Docker network and volumes, SSH
  config and keys at `$HOME/.ssh/vde`, and the `logs/`, `env-files/`, caches, and
  lock directories.

---

[← Back to README](../../README.md)
**This is the Way.**
