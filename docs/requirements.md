# Requirements

This document outlines the system requirements for running the VDE (Virtual Development Environment).

[← Back to README](../README.md)

---

## Shell Requirements

VDE supports multiple shells with varying levels of functionality:

| Shell | Version | Support Level | Notes |
|-------|---------|---------------|-------|
| **zsh** | 5.0+ | Full | Recommended, native associative arrays |
| **bash** | 4.0+ | Full | Native associative arrays |
| **bash** | 3.x | Limited | File-based associative array fallback (slower) |

### Checking Your Shell Version

```bash
# Check zsh version
zsh --version

# Check bash version
bash --version
```

### Recommended Shell

**zsh 5.0+** is recommended for the best experience. It ships with macOS and provides:
- Native associative array support
- Better glob expansion
- Enhanced completion

### Installing Shells

**macOS:**
```bash
# zsh is pre-installed on macOS
# To update bash (macOS ships with bash 3.x):
brew install bash
```

**Ubuntu/Debian:**
```bash
# Install zsh
sudo apt-get install zsh

# bash 4+ is typically pre-installed
```

**RHEL/CentOS/Fedora:**
```bash
# Install zsh
sudo dnf install zsh

# bash 4+ is typically pre-installed
```

---

## Shell Feature Availability

Different shells provide different levels of support for VDE features:

| Feature | zsh 5.0+ | bash 4.0+ | bash 3.x |
|---------|----------|-----------|----------|
| Core VM operations | ✅ | ✅ | ✅ |
| Associative arrays | Native | Native | File-based fallback |
| VM type caching | ✅ | ✅ | ✅ |
| Port registry | ✅ | ✅ | ✅ |
| Natural language parser | ✅ | ✅ | ✅ |
| Performance | Optimal | Optimal | Slower (I/O overhead) |

### Performance Notes

- **zsh 5.0+ / bash 4.0+**: Uses native associative arrays for O(1) lookups
- **bash 3.x**: Uses file-based key-value storage, which adds I/O overhead but maintains full functionality

---

## Other Requirements

| Requirement | Purpose | Minimum Version |
|-------------|---------|-----------------|
| **Docker** | Container runtime | Docker Desktop or Engine 20.10+ |
| **docker-compose** | Multi-container orchestration | 1.29+ or Docker Compose V2 |
| **SSH key pair** | Container authentication | Any (ed25519 recommended) |

---

## Verifying Your Setup

Run these commands to verify everything is ready:

```bash
# Check shell version
echo "Shell: $SHELL"
zsh --version 2>/dev/null || bash --version

# Check Docker is running
docker ps

# Check docker-compose is available
docker-compose --version || docker compose version

# Check for SSH keys
ls -la ~/.ssh/id_ed25519 2>/dev/null || ls -la ~/.ssh/id_rsa
```

If you don't have SSH keys, generate them:
```bash
ssh-keygen -t ed25519
```

---

## Troubleshooting Shell Issues

### "Associative array not supported" Error

If you see this error, you're running an older shell version. Options:

1. **Upgrade your shell** (recommended):
   ```bash
   # macOS
   brew install bash
   
   # Linux
   sudo apt-get install bash  # or zsh
   ```

2. **Use the file-based fallback** (automatic for bash 3.x):
   VDE automatically detects bash 3.x and uses file-based storage.

### "Command not found: setopt" Error

This indicates you're running in bash but the script expects zsh. VDE scripts now support both shells, but if you encounter this:

1. Ensure you're using the latest VDE version
2. Run the script explicitly with your preferred shell:
   ```bash
   bash ./scripts/start-virtual python
   # or
   zsh ./scripts/start-virtual python
   ```

### Performance Issues on bash 3.x

If operations seem slow on bash 3.x:

1. Consider upgrading to bash 4.0+ or zsh 5.0+
2. The file-based fallback adds I/O overhead for each associative array operation
3. VM type caching helps mitigate this for repeated operations

---

## Environment Variables

VDE respects these environment variables for shell compatibility:

| Variable | Purpose | Default |
|----------|---------|---------|
| `VDE_SKIP_COMPAT_CHECK` | Skip shell compatibility check | `0` |
| `VDE_DEBUG_TIMING` | Enable performance timing output | `0` |

---

[← Back to README](../README.md)
