# Requirements

This document outlines the system requirements for running the VDE (Virtual Development Environment).

[← Back to README](../README.md)

---

## Shell Requirements (The Rule Spine)

VDE is a **ZSH-ONLY** ecosystem. Support for other shells has been deprecated to ensure absolute architectural consistency and cognitive sovereignty.

| Shell | Version | Support Level | Notes |
|-------|---------|---------------|-------|
| **zsh** | 5.0+ | **Mandatory** | Required for Rule Spine compliance and native associative arrays |

### Checking Your Shell Version

```zsh
# Check zsh version
zsh --version
```

### Mandated Shell

**zsh 5.0+** is the only supported shell. It provides the native associative array support and glob expansion required by the VDE libraries.

### Installing ZSH

**macOS:**
zsh is the default shell and pre-installed on macOS.

**Ubuntu/Debian:**
```zsh
sudo apt-get update && sudo apt-get install zsh
```

**RHEL/CentOS/Fedora:**
```zsh
sudo dnf install zsh
```

---

## System Requirements

| Requirement | Purpose | Minimum Version |
|-------------|---------|-----------------|
| **Docker** | Container runtime | Docker Desktop or Engine 20.10+ |
| **docker-compose** | Multi-container orchestration | 1.29+ or Docker Compose V2 |
| **SSH key pair** | Container authentication | `vde_student` (ed25519) |

---

## Verifying Your Setup

Run these commands to verify everything is ready:

```zsh
# Check shell version
echo "Shell: $SHELL"
zsh --version

# Check Docker is running
docker ps

# Check docker-compose is available
docker-compose --version || docker compose version

# Check for VDE SSH keys
ls -la ~/.ssh/vde/vde_student
```

If you don't have VDE SSH keys, run the bootstrap ritual:
```zsh
./bin/vde-bootstrap
```

---

## Environment Variables

VDE respects these environment variables:

| Variable | Purpose | Default |
|----------|---------|---------|
| `VDE_ROOT_DIR` | Root directory of the VDE repository | (Auto-detected) |
| `VDE_DEBUG_TIMING` | Enable performance timing output | `0` |

---

[← Back to README](../README.md)
