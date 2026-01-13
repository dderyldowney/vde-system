# Available Scripts

Overview of all scripts included with VDE.

[← Back to README](../README.md)

---

## Core Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `list-vms` | List all predefined languages and services | `./scripts/list-vms [--lang\|--svc] [search]` |
| `create-virtual-for` | Create a new language or service VM | `./scripts/create-virtual-for <name>` |
| `start-virtual` | Start one or more VMs | `./scripts/start-virtual <name> [name2] ... [--rebuild] [--no-cache]` |
| `shutdown-virtual` | Stop one or more VMs | `./scripts/shutdown-virtual <name> [name2] ...` |
| `build-and-start` | Shutdown all, then start all VMs with optional rebuild | `./scripts/build-and-start [--rebuild] [--no-cache]` |
| `add-vm-type` | Add a new language or service to the predefined list | `./scripts/add-vm-type <name> "<install-cmd>" [aliases]` |

---

## AI Assistant Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `vde-ai` | One-shot natural language commands | `./scripts/vde-ai "your command"` |
| `vde-chat` | Interactive chat interface | `./scripts/vde-chat` |

See [VDE AI Assistant](./vde-ai-assistant.md) for details.

---

## Script Locations

```
~/dev/scripts/
├── lib/                    # Shared libraries
│   ├── vm-common          # Core functions
│   ├── vde-commands       # AI-safe wrappers
│   └── vde-parser         # Natural language parser
├── templates/             # Docker Compose templates
├── data/
│   └── vm-types.conf      # VM type definitions
├── list-vms
├── create-virtual-for
├── start-virtual
├── shutdown-virtual
├── build-and-start
├── add-vm-type
├── vde-ai
└── vde-chat
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
