# Available Scripts

Overview of all scripts included with VDE.

[← Back to README](../README.md)

---

## Core Scripts

### VDE Unified Command (Recommended)

The `vde` command provides a single entry point for all VDE operations:

| Command | Purpose | Usage |
|---------|---------|-------|
| `vde create <vm>` | Create a new VM | `vde create python` |
| `vde start <vm>` | Start a VM | `vde start python-dev` |
| `vde stop <vm>` | Stop a VM | `vde stop postgres` |
| `vde restart <vm>` | Restart a VM | `vde restart rust-dev` |
| `vde remove <vm>` | Remove a VM instance | `vde remove rust` |
| `vde uninstall <type>` | Uninstall a language/service completely | `vde uninstall elixir` |
| `vde list` | List all VMs | `vde list` |
| `vde status` | Show VM status | `vde status` |
| `vde health` | Run system health check | `vde health` |
| `vde nuke` | Remove all of VDE (prompts for backup) | `vde nuke` |
| `vde help` | Show help message | `vde help` |

### Legacy Direct Scripts

Individual scripts are still available but `vde` is the recommended interface:

| Script | Purpose | Usage |
|--------|---------|-------|
| `list-vms` | List all predefined languages and services | `./scripts/list-vms [--lang|--svc] [search]` |
| `create-virtual-for` | Create a new language or service VM | `./scripts/create-virtual-for <name>` |
| `start-virtual` | Start one or more VMs | `./scripts/start-virtual <name> [name2] ... [--rebuild] [--no-cache]` |
| `shutdown-virtual` | Stop one or more VMs | `./scripts/shutdown-virtual <name> [name2] ...` |
| `build-and-start` | Shutdown all, then start all VMs with optional rebuild | `./scripts/build-and-start [--rebuild] [--no-cache]` |
| `add-vm-type` | Add a new language or service to the predefined list | `./scripts/add-vm-type <name> "<install-cmd>" [aliases]` |

---

## Script Locations

```
~/dev/scripts/
├── vde                     # Unified command entry point (RECOMMENDED)
├── lib/                    # Shared libraries
│   ├── vm-common          # Core functions
│   ├── vde-commands       # Command wrappers
│   ├── vde-parser         # Pattern-based command parser
│   ├── vde-constants      # Constants and configuration
│   ├── vde-errors         # Error handling
│   ├── vde-log            # Logging utilities
│   ├── vde-core           # Core operations
│   └── vde-shell-compat   # Shell compatibility layer
├── templates/             # Docker Compose templates
├── data/
│   └── vm-types.conf      # VM type definitions
├── list-vms               # List available VMs
├── create-virtual-for     # Create a new VM
├── start-virtual          # Start VMs
├── shutdown-virtual       # Stop VMs
├── remove-virtual         # Remove VM instances
├── uninstall-vm-type      # Uninstall language/service
├── build-and-start        # Rebuild and start all VMs
├── vde-health             # Health check script
├── nuke-vde               # Remove all of VDE
└── add-vm-type            # Add new VM type definitions
```

---

## Making Scripts Executable

If you encounter "permission denied" errors:

```bash
chmod +x ~/dev/scripts/*
chmod +x ~/dev/scripts/lib/*
```

---

[← Back to README](../README.md)
