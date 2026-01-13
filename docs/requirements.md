# Requirements

This document outlines the system requirements for running the VDE (Virtual Development Environment).

[← Back to README](../README.md)

---

## Shell Requirements

**Required:** `zsh 5.0+` (for associative array support)

To check your version:
```bash
zsh --version
```

### Installing Zsh

If you're on macOS with an older bash, these scripts use zsh which ships with macOS. If you're on Linux, you may need to install zsh:

```bash
# Ubuntu/Debian
sudo apt-get install zsh

# macOS (already installed)
brew install zsh
```

---

## Other Requirements

| Requirement | Purpose |
|-------------|---------|
| **Docker** | Desktop or Docker Engine for containerization |
| **docker-compose** | For managing multi-container applications |
| **SSH key pair** | `id_ed25519` or `id_rsa` for container access |

---

## Verifying Your Setup

Run these commands to verify everything is ready:

```bash
# Check zsh version
zsh --version

# Check Docker is running
docker ps

# Check docker-compose is available
docker-compose --version

# Check for SSH keys
ls -la ~/.ssh/id_ed25519  # or ~/.ssh/id_rsa
```

If you don't have SSH keys, generate them:
```bash
ssh-keygen -t ed25519
```

---

[← Back to README](../README.md)
