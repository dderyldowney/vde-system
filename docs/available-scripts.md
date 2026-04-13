# Available Scripts

Overview of all scripts included with VDE.

[← Back to README](../README.md)

---

## Core Scripts

### VDE Unified Command (Recommended)

The `vde` command is the canonical entry point for the **Sovereign Evolution (1.3.0)**. It wraps all infrastructure logic in the `vde_run` safety layer, ensuring Zsh purity and system integrity.

| Command | Purpose | Usage |
|---------|---------|-------|
| `vde init` | **The Initialization Ritual**: Hydrate infrastructure, SSH keys, and networks. | `vde init` |
| `vde create <vm>` | Create a new VM Spoke from the Beskar Registry. | `vde create python` |
| `vde rebuild <vm>` | Re-forge a Spoke's Docker image (defaults to no-cache). | `vde rebuild python` |
| `vde start <vm>` | Ignite a VM Spoke. Performs "System Breath" resource check. | `vde start python` |
| `vde stop <vm>` | Quench (stop) a running VM. | `vde stop postgres` |
| `vde restart <vm>` | Restart one or more active Spokes. | `vde restart rust` |
| `vde remove <vm>` | Dissolve (remove) a VM instance and its locks. (Aliases: `rm`, `delete`) | `vde remove rust` |
| `vde nuke` | **The Great Quench**: Remove all VDE artifacts (prompts for backup). | `vde nuke` |
| `vde exec <vm> <cmd>` | Execute a command inside a Spoke without a full login shell. | `vde exec go "go version"` |
| `vde enter <vm>` | The Sovereign Handshake: Enter a Spoke's login shell. (Alias: `ssh`) | `vde enter rust` |
| `vde add <name>` | Dynamic Expansion: Register a new Spoke type. | `vde add --pkgs "htop" myvm` |
| `vde uninstall <vm>` | Permanent Removal: Remove a Spoke type from the Registry. | `vde uninstall elixir` |
| `vde list` | Audit all predefined and custom Spokes. | `vde list` |
| `vde ps` | List all running VDE-managed containers. (Alias: `status`) | `vde ps` |
| `vde vision` | **The Archivist’s Vision**: Real-time Markdown-based status grid. | `vde vision` |
| `vde inspect <vm>` | Inspect container metadata and labels. | `vde inspect python` |
| `vde logs <vm>` | Tail the logs of a specific Spoke. | `vde logs redis` |
| `vde images` | List all VDE-managed Docker images. | `vde images` |
| `vde stats` | View real-time resource usage of active Spokes. | `vde stats` |
| `vde health` | Run the System Spine health check. | `vde health` |
| `vde cluster <cmd>` | Orchestrate multi-VM clusters (Tech Stacks). | `vde cluster start python-stack` |
| `vde networks` | Audit and manage the `vde-net` Docker bridges. | `vde networks` |
| `vde validate` | Verify the integrity of the Beskar Registry (JSON schemas). | `vde validate` |
| `vde rebuild-cache` | Force a re-smelt of the internal VM cache. | `vde rebuild-cache` |
| `vde sync-version` | Synchronize versioning across the Hub and Spokes. | `vde sync-version` |
| `vde port <alias>` | Retrieve the assigned SSH port for a Spoke. | `vde port python` |
| `vde info` | Detailed system and environment diagnostic dump. | `vde info` |

---

## Script Locations

The VDE repository follows a strict structural mandate. All binaries reside in `bin/` and rely on the libraries in `lib/`.

```
VDE_ROOT/
├── bin/
│   ├── vde                     # Unified Command Entry Point (THE WAY)
│   ├── vde-init                # Infrastructure Ritual Logic
│   ├── vde-rebuild             # Image Re-forging Logic
│   ├── vde-vision              # Observability Dashboard Logic
│   ├── vde-networks            # Bridge Management
│   ├── vde-ps / vde-logs       # Docker Proxy Tools
│   ├── vde-enforce-uap.zsh     # The Rule Spine (Compliance)
│   ├── install-githooks        # Activation Ritual for Forge Laws
│   └── ...                     # Specialized lifecycle scripts
├── githooks/
│   ├── pre-commit              # The Pre-Strike Sentinel (Purity Gate)
│   └── ...                     # Tracked Git hooks
├── lib/
│   ├── vde-core                # Core Versioning & Pathing
│   ├── vde-ssh                 # The Sovereign Handshake (SSH Bridge)
│   ├── vde-lock                # FIFO Lock-Queue Model
│   ├── vde-errors              # Deterministic Error Translation
│   ├── vm-common               # Registry & Registry Operations
│   └── ...                     # Shared Zsh modules
├── data/
│   ├── vm-types.conf           # The Raw Beskar (Source)
│   └── vm-types.json           # The Pure Beskar (Registry)
├── scripts/
│   └── setup/                  # USP Hydration Rituals (-init.zsh)
└── templates/                  # Compose & Config Blueprints
```

---

## Making Scripts Executable

The Rule Spine mandates that all scripts must be Zsh-compliant and executable. VDE enforces this automatically during `init`, but you can strike them manually if needed:

```zsh
# Inside VDE_ROOT
chmod +x bin/*
chmod +x scripts/setup/*.zsh
```

---

[← Back to README](../README.md)
