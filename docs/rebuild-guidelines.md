# Rebuild Guidelines

When and how to rebuild your VDE containers.

[← Back to README](../README.md)

---

## Rebuild Decision Matrix

| Scenario | Command | Why |
|----------|---------|-----|
| Daily development | No rebuild needed | Containers are stateless |
| Dockerfiles change | `vde start <vm> --rebuild` | Rebuild images with new Dockerfile |
| SSH keys change | `vde start <vm> --rebuild` | New keys need to be baked in |
| Environment variables change | `vde start <vm> --rebuild` | env-files are read at build time |
| Base images update | `vde start <vm> --rebuild --no-cache` | Ensure fresh base image |
| Installing system packages | `vde start <vm> --rebuild` | Packages install during build |

---

## Rebuild Commands

### Single VM

```bash
# Rebuild single VM
vde start python --rebuild

# Full clean rebuild
vde start python --rebuild --no-cache
```

### Multiple VMs

```bash
# Rebuild multiple VMs
vde start python go rust --rebuild

# Rebuild all VMs
vde start all --rebuild
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
vde start all --rebuild
```

### After Adding System Packages

```bash
# Rebuild specific VM
vde start python --rebuild
```

### After Updating SSH Keys

```bash
# Rebuild to bake in new keys
vde start all --rebuild
```

### After Base Image Update

```bash
# Full clean rebuild
vde start all --rebuild --no-cache
```

---

## Troubleshooting Rebuilds

### Rebuild Takes Too Long

```bash
# Use cached layers (faster, but may not pick up all changes)
vde start python --rebuild
```

### Rebuild Doesn't Pick Up Changes

```bash
# Force rebuild without cache
vde start python --rebuild --no-cache
```

### Container Won't Start After Rebuild

```bash
# Check logs
docker logs <container-name>

# Check docker-compose.yml syntax
docker-compose -f configs/docker/<name>/docker-compose.yml config

# Try no-cache rebuild
vde start <name> --rebuild --no-cache
```

---

[← Back to README](../README.md)
