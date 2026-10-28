# Command Reference
<!-- @shared-law (Sovereign Law) -->

Complete reference for all VDE commands in the **Sovereign Baseline (1.5.6)**.

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
- No image rebuild is required; Spokes pick up the new base on their next start.
- Reports exactly what was moved and what was skipped.

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
```

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

### The Pruning Ritual
```zsh
# Archive old plans/scripts and purge aged logs
vde prune
```

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
