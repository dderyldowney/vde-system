# VDE VM Docker Configuration
<!-- @shared-law (Sovereign Law) -->

Centralized Docker configuration for all VDE VMs including compose file locations, environment files, and mount paths.

## Overview

The VM Docker configuration system provides:
- **Centralized settings** for all language and service VMs
- **Docker compose file** locations
- **Environment file** paths
- **Container naming** conventions
- **Volume mount** configurations
- **Automatic validation** against JSON schema

## Configuration Files

### vm-docker-config.json

**Location:** `data/vm-docker-config.json`

**Structure:**
```json
{
  "version": "1.0",
  "base_settings": {
    "context": "../../..",
    "base_dockerfile": "configs/docker/vde-base.Dockerfile",
    "network": "vde-net",
    "username": "devuser",
    "uid": 1000,
    "gid": 1000
  },
  "languages": {
    "python": {
      "compose_file": "configs/docker/python/docker-compose.yml",
      "env_file": "env-files/python.env",
      "image": "dev-python:latest",
      "container_name": "vde-python",
      "workspace_mount": "projects/python:/home/devuser/workspace",
      "logs_mount": "logs/python:/logs"
    }
  },
  "services": {
    "postgres": {
      "compose_file": "configs/docker/postgres/docker-compose.yml",
      "env_file": "env-files/postgres.env",
      "image": "dev-postgres:latest",
      "container_name": "postgres",
      "data_mount": "data/postgres:/data",
      "logs_mount": "logs/postgres:/logs"
    }
  }
}
```

### vm-docker-config.schema.json

**Location:** `data/vm-docker-config.schema.json`

**Validates:**
- Base settings structure
- Language VM requirements
- Service VM requirements
- File path patterns
- Container naming conventions

## Fields

### Base Settings

Shared across all VMs:

| Field | Type | Description |
|-------|------|-------------|
| `context` | string | Docker build context path |
| `base_dockerfile` | string | Path to base Dockerfile |
| `network` | string | Docker network name |
| `username` | string | Container username |
| `uid` | integer | User ID (≥1000) |
| `gid` | integer | Group ID (≥1000) |

### Language VM Config

Each language VM has:

| Field | Type | Pattern | Description |
|-------|------|---------|-------------|
| `compose_file` | string | `configs/docker/{lang}/docker-compose.yml` | Docker compose file location |
| `env_file` | string | `env-files/{lang}.env` | Environment variables file |
| `image` | string | `dev-{lang}:latest` | Docker image name |
| `container_name` | string | `{lang}-dev` | Container name (must end with `-dev`) |
| `workspace_mount` | string | `projects/{lang}:/home/devuser/workspace` | Workspace volume mount |
| `logs_mount` | string | `logs/{lang}:/logs` | Logs volume mount |

### Service VM Config

Each service VM has:

| Field | Type | Pattern | Description |
|-------|------|---------|-------------|
| `compose_file` | string | `configs/docker/{service}/docker-compose.yml` | Docker compose file location |
| `env_file` | string | `env-files/{service}.env` | Environment variables file |
| `image` | string | `dev-{service}:latest` | Docker image name |
| `container_name` | string | `{service}` | Container name (no `-dev` suffix) |
| `data_mount` | string | `data/{service}:/data` | Data volume mount |
| `logs_mount` | string | `logs/{service}:/logs` | Logs volume mount |

## Usage

### Load Docker Config

```zsh
source lib/vm-common
load_docker_config
```

Output:
```
[INFO] Loading VM Docker configuration...
[INFO] Validating docker config against schema...
[INFO] Schema validation passed
[INFO] Docker config loaded successfully
[INFO]   Language configs: 20
[INFO]   Service configs: 7
```

### Access Configuration

**Using associative arrays:**
```zsh
echo ${VM_COMPOSE_FILE[python]}
# Output: configs/docker/python/docker-compose.yml

echo ${VM_ENV_FILE[python]}
# Output: env-files/python.env

echo ${VM_CONTAINER_NAME[python]}
# Output: vde-python

echo ${VM_WORKSPACE_MOUNT[python]}
# Output: projects/python:/home/devuser/workspace
```

**Using helper function:**
```zsh
get_docker_config COMPOSE_FILE python
# Output: configs/docker/python/docker-compose.yml

get_docker_config ENV_FILE postgres
# Output: env-files/postgres.env

get_docker_config DATA_MOUNT postgres
# Output: data/postgres:/data
```

### Available Arrays

**All VMs:**
- `VM_COMPOSE_FILE` - Docker compose file paths
- `VM_ENV_FILE` - Environment file paths
- `VM_IMAGE` - Docker image names
- `VM_CONTAINER_NAME` - Container names
- `VM_LOGS_MOUNT` - Logs mount configurations

**Language VMs only:**
- `VM_WORKSPACE_MOUNT` - Workspace mount configurations

**Service VMs only:**
- `VM_DATA_MOUNT` - Data mount configurations

## Schema Validation

### Automatic Validation

Validation happens automatically when loading:

```zsh
load_docker_config
# Validates against vm-docker-config.schema.json
```

### Manual Validation

```zsh
# Using validation script
./bin/validate-schemas.zsh

# Using vde-core directly
source lib/vde-core
schema=$(vde_get_schema_for_json "data/vm-docker-config.json")
vde_validate_json_schema "data/vm-docker-config.json" "$schema"
```

## Validation Rules

### Language VMs

- ✓ Container name must end with `-dev`
- ✓ Must have `workspace_mount` (not `data_mount`)
- ✓ Compose file: `configs/docker/{lang}/docker-compose.yml`
- ✓ Env file: `env-files/{lang}.env`
- ✓ Image: `dev-{lang}:latest`

### Service VMs

- ✓ Container name must NOT end with `-dev`
- ✓ Must have `data_mount` (not `workspace_mount`)
- ✓ Compose file: `configs/docker/{service}/docker-compose.yml`
- ✓ Env file: `env-files/{service}.env`
- ✓ Image: `dev-{service}:latest`

## Examples

### Example 1: Get Compose File Path

```zsh
source lib/vm-common
load_docker_config

compose_file=$(get_docker_config COMPOSE_FILE python)
echo "Python compose file: $compose_file"
# Output: Python compose file: configs/docker/python/docker-compose.yml
```

### Example 2: Launch Container with Config

```zsh
source lib/vm-common
load_docker_config

vm_name="python"
compose_file="${VM_COMPOSE_FILE[$vm_name]}"
env_file="${VM_ENV_FILE[$vm_name]}"

docker-compose -f "$compose_file" --env-file "$env_file" up -d
```

### Example 3: Check All Language VMs

```zsh
source lib/vm-common
load_docker_config load_vm_types

for vm in "${(@k)VM_TYPE}"; do
    if [[ "${VM_TYPE[$vm]}" == "lang" ]]; then
        echo "$vm: ${VM_COMPOSE_FILE[$vm]}"
    fi
done
```

### Example 4: Validate Mount Paths

```zsh
source lib/vm-common
load_docker_config

for vm in python rust go; do
    workspace="${VM_WORKSPACE_MOUNT[$vm]}"
    logs="${VM_LOGS_MOUNT[$vm]}"
    echo "$vm workspace: $workspace"
    echo "$vm logs: $logs"
done
```

## Integration with VM Types

The Docker config complements the VM types config:

**vm-types.json** provides:
- VM metadata (name, display, aliases)
- Installation commands
- Service ports
- VM type (lang/service)

**vm-docker-config.json** provides:
- Docker compose file locations
- Environment file paths
- Container names
- Volume mounts
- Image names

**Together they provide complete VM configuration.**

## File Structure

```
VDE Project Root
├── data/
│   ├── vm-types.json              # VM metadata
│   ├── vm-types.schema.json       # VM types schema
│   ├── vm-docker-config.json      # Docker config (NEW)
│   └── vm-docker-config.schema.json  # Docker config schema (NEW)
├── configs/docker/
│   ├── python/
│   │   └── docker-compose.yml     # Referenced by config
│   ├── postgres/
│   │   └── docker-compose.yml     # Referenced by config
│   └── ...
└── env-files/
    ├── python.env                 # Referenced by config
    ├── postgres.env               # Referenced by config
    └── ...
```

## Benefits

1. **Single Source of Truth**: All Docker paths in one place
2. **Type Safety**: Schema validation prevents errors
3. **Consistency**: Enforces naming conventions
4. **Maintainability**: Easy to add new VMs
5. **Integration**: Works with existing VM types config
6. **Validation**: Automatic schema validation

## Adding New VMs

### Add Language VM

```json
{
  "newlang": {
    "compose_file": "configs/docker/newlang/docker-compose.yml",
    "env_file": "env-files/newlang.env",
    "image": "dev-newlang:latest",
    "container_name": "vde-newlang",
    "workspace_mount": "projects/newlang:/home/devuser/workspace",
    "logs_mount": "logs/newlang:/logs"
  }
}
```

### Add Service VM

```json
{
  "newservice": {
    "compose_file": "configs/docker/newservice/docker-compose.yml",
    "env_file": "env-files/newservice.env",
    "image": "dev-newservice:latest",
    "container_name": "newservice",
    "data_mount": "data/newservice:/data",
    "logs_mount": "logs/newservice:/logs"
  }
}
```

### Validation After Changes

```zsh
# Validate schema
./bin/validate-schemas.zsh

# Test loading
zsh -c "source lib/vm-common && load_docker_config"
```

## Troubleshooting

### "Docker config validation failed"

**Cause**: Config doesn't match schema

**Solution**:
1. Check JSON syntax: `jq . data/vm-docker-config.json`
2. Verify required fields present
3. Check naming patterns (container names, file paths)
4. Run validation: `./bin/validate-schemas.zsh`

### "Docker config not found"

**Cause**: Missing config file

**Solution**:
```zsh
# Check file exists
ls -la data/vm-docker-config.json

# Regenerate if missing
# (File must be created manually, no auto-generation)
```

### "Field not found for VM"

**Cause**: VM not in docker config

**Solution**:
1. Check VM exists: `jq '.languages, .services | keys' data/vm-docker-config.json`
2. Add VM to config if missing
3. Reload config: `load_docker_config`

## References

- **JSON Schema Spec**: https://json-schema.org/
- **VM Types Config**: `data/README.md`
- **Schema Validation**: `docs/ARCHITECTURE.md`
- **Validation Tool**: `bin/validate-schemas.zsh`
