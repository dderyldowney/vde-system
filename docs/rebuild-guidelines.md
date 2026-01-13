# Rebuild Guidelines

When and how to rebuild your VDE containers.

[← Back to README](../README.md)

---

## Rebuild Decision Matrix

| Scenario | Command | Why |
|----------|---------|-----|
| Daily development | No rebuild needed | Containers are stateless |
| Dockerfiles change | `--rebuild` | Rebuild images with new Dockerfile |
| SSH keys change | `--rebuild` | New keys need to be baked in |
| Environment variables change | `--rebuild` | env-files are read at build time |
| Base images update | `--rebuild --no-cache` | Ensure fresh base image |
| Installing system packages | `--rebuild` | Packages install during build |

---

## Rebuild Commands

### Single VM

```bash
# Rebuild single VM
./scripts/start-virtual python --rebuild

# Full clean rebuild
./scripts/start-virtual python --rebuild --no-cache
```

### Multiple VMs

```bash
# Rebuild multiple VMs
./scripts/start-virtual python go rust --rebuild

# Rebuild all VMs
./scripts/start-virtual all --rebuild
```

### Using VDE AI

```bash
# Natural language rebuild
./scripts/vde-ai "rebuild python"
./scripts/vde-ai "rebuild everything with no cache"
./scripts/vde-ai "restart Go with rebuild"
```

---

## What Rebuild Affects

### Preserved Across Rebuilds

- Source code in `projects/<name>/`
- Data in `data/<name>/` (for services)
- SSH configuration entries
- Environment files (unless you edit them)

### Rebuilt

- Docker images
- Container filesystem
- Installed packages
- User configuration inside container

---

## Common Rebuild Scenarios

### After Changing base-dev.Dockerfile

```bash
# Rebuild all VMs that use the base image
./scripts/build-and-start --rebuild
```

### After Adding System Packages

```bash
# Rebuild specific VM
./scripts/start-virtual python --rebuild
```

### After Updating SSH Keys

```bash
# Rebuild to bake in new keys
./scripts/start-virtual all --rebuild
```

### After Base Image Update

```bash
# Full clean rebuild
./scripts/build-and-start --rebuild --no-cache
```

---

## Troubleshooting Rebuilds

### Rebuild Takes Too Long

```bash
# Use cached layers (faster, but may not pick up all changes)
./scripts/start-virtual python --rebuild
```

### Rebuild Doesn't Pick Up Changes

```bash
# Force rebuild without cache
./scripts/start-virtual python --rebuild --no-cache
```

### Container Won't Start After Rebuild

```bash
# Check logs
docker logs <container-name>

# Check docker-compose.yml syntax
docker-compose -f configs/docker/<name>/docker-compose.yml config

# Try no-cache rebuild
./scripts/start-virtual <name> --rebuild --no-cache
```

---

[← Back to README](../README.md)
