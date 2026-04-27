# VDE API Reference
<!-- @shared-law (Sovereign Law) -->

**Version:** 1.5.1 (The Sovereign Baseline)
**Status:** AUTHORITATIVE

This document provides the complete API reference for the Virtual Development Environment (VDE) system.

---

## 1. Overview (The Rule Spine)

VDE is a **ZSH-ONLY** Docker-based container orchestration system. All libraries and scripts are designed for native ZSH execution.

### Architecture

```
VDE Root Directory
├── bin/
│   ├── lib/              # Hardened Library modules
│   │   ├── vde-constants
│   │   ├── vde-errors
│   │   ├── vde-log
│   │   ├── vde-core
│   │   ├── vm-common
│   │   ├── vde-commands
│   │   └── vde-parser
│   ├── data/             # The Beskar Vault
│   │   └── vm-types.conf
│   └── templates/        # Docker Compose templates
├── configs/              # Generated VM configs
├── projects/             # User workspace
├── data/                 # Persistent data
├── logs/                 # Hardened logs
└── env-files/            # Environment templates
```

### Supported Environment

- **Shell:** zsh 5.0+ (Mandatory)
- **Platform:** macOS (Darwin), Linux
- **Requirements:** Docker Desktop or Engine 20.10+

---

## 2. Scripts Reference

### `vde` - Unified Orchestrator

The main entry point for all VDE operations. Supervised by `vde-enforce-uap.zsh`.

**Usage:**
```zsh
vde <command> [options] [args]
```

**Core Commands:**

| Command | Description |
|---------|-------------|
| `create <vm>` | Create a new VM from templates |
| `start <vm>` | Ignite a VM (Deterministic) |
| `stop <vm>` | Shutdown a VM (Graceful) |
| `restart <vm>` | Cycle a VM (Supports --rebuild) |
| `list` | List available Spokes |
| `status` | Show real-time Hub status |
| `health` | Execute Sovereign Audit |
| `ask <text>` | Natural Language Interface |

---

## 3. Library API

### vde-constants

Standardized constants for VDE operations.

**Return Codes (Exit Codes):**

| Constant | Value | Description |
|----------|-------|-------------|
| `VDE_SUCCESS` | 0 | Operation complete |
| `VDE_ERR_GENERAL` | 1 | General failure |
| `VDE_ERR_INVALID_INPUT` | 2 | Validation failure |
| `VDE_ERR_NOT_FOUND` | 3 | Resource missing |
| `VDE_ERR_EXISTS` | 4 | Resource conflict |
| `VDE_ERR_DOCKER` | 5 | Docker daemon error |
| `VDE_ERR_SSH` | 6 | SSH bridge failure |
| `VDE_ERR_PORT` | 7 | Allocation conflict |
| `VDE_ERR_LOCK` | 9 | Spinlock failure |

**Identity Configuration:**

| Constant | Value | Description |
|----------|-------|-------------|
| `VDE_SSH_IDENTITY` | `~/.ssh/vde/vde_student` | Mission identity key |
| `VDE_SSH_KEY_TYPES` | "vde_student id_ecdsa id_rsa" | Preferred key types |

---

### vde-naming (Security Hardened)

**Core Functions:**

| Function | Description |
|----------|-------------|
| `vde_normalize_name <name>` | Strips prefix and non-alphanumeric chars (Path Traversal Protection) |
| `vde_validate_name <name>` | Enforces `^[a-z0-9-]+$` pattern |
| `vde_get_container_name <name>` | Returns `vde-<name>` |

---

### vde-log (Structured)

**Output Control:**

```zsh
vde_log_to_stdout               # Default output
vde_log_set_level <LEVEL>       # DEBUG, INFO, WARN, ERROR
```

**Logging:**

```zsh
vde_log_info "Message" "component"
vde_log_error "Failure" "component"
```

---

## 4. Port Allocation (Atomic)

Ports are managed via atomic spinlocks in `.cache/port-registry/`.

| Range | Usage |
|-------|-------|
| 2200-2299 | Language VM SSH |
| 2400-2499 | Service VM SSH |

---

## 5. Environment Variables

| Variable | Purpose |
|----------|---------|
| `VDE_ROOT_DIR` | Repository root authority |
| `VDE_DEBUG_TIMING` | Enable millisecond performance tracing |

---

[← Back to README](../README.md)
