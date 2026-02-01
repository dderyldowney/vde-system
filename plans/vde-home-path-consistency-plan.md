# VDE $HOME Path Consistency Plan

## Objective
Refactor VDE scripts to use `$HOME` consistently for portable path handling across Linux, WSL2, and macOS.

## Current State Analysis

### VDE_ROOT_DIR Usage (81 occurrences)
- **Set via**: `VDE_ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"` - absolute path
- **Used in**:
  - Configuration paths: `$VDE_ROOT_DIR/configs/docker/...`
  - Data paths: `$VDE_ROOT_DIR/data/...`, `$VDE_ROOT_DIR/projects/...`
  - Log paths: `$VDE_ROOT_DIR/logs/...`
  - SSH paths: `$VDE_ROOT_DIR/public-ssh-keys/...`

### $HOME Usage (4 occurrences)
- **Current locations**:
  - `scripts/lib/vm-common:1812`: `$HOME/.ssh/id_ed25519`
  - `scripts/lib/vm-common:2217`: `$HOME/.ssh/id_ed25519`
  - `scripts/lib/vde-constants:189`: `$HOME/.ssh/vde`

## Proposed Architecture

### 1. Define Home-Based Constants
In `scripts/lib/vde-constants`, add:
```zsh
# Home directory - cross-platform
readonly VDE_HOME_DIR="${HOME}"
readonly VDE_SSH_DIR="${VDE_HOME_DIR}/.ssh/vde"
readonly VDE_SSH_IDENTITY="${VDE_SSH_DIR}/id_ed25519"
readonly VDE_SSH_IDENTITY_PUB="${VDE_SSH_DIR}/id_ed25519.pub"
readonly VDE_SSH_CONFIG="${VDE_SSH_DIR}/config"
```

### 2. Calculate Relative Project Path
Extract just the project directory name (not full relative path):
```zsh
# Get absolute project root
local abs_project_root="$(cd "$(dirname "$0")/.." && pwd)"

# Calculate project name for portability
# Extract just the directory name: /home/devuser/projects/vde → vde
# This gives Docker containers a simple project identifier
local vde_project_name="${abs_project_root:t}"

# Export for use in configs and templates
export VDE_PROJECT_NAME="$vde_project_name"
export VDE_ROOT_DIR="$abs_project_root"  # Keep absolute for internal use
```

### Examples
| Installation Path | HOME | VDE_PROJECT_NAME |
|-------------------|------|------------------|
| /home/devuser/dev | /home/devuser | dev |
| /home/devuser/projects/vde | /home/devuser | vde |
| /Users/devuser/my-vde | /Users/devuser | my-vde |
| /opt/vde | /home/devuser | vde |

### 3. SSH Config Template Update
Update `scripts/templates/ssh-entry.txt` to use:
```
IdentityFile ~/.ssh/vde/id_ed25519
```
(Already done - uses tilde which is portable)

### 4. Docker Compose Environment Variables
Update docker-compose templates to use:
```yaml
environment:
  - VDE_HOME=${HOME}
  - VDE_PROJECT_NAME=${VDE_PROJECT_NAME}
  - VDE_ROOT_DIR=${VDE_ROOT_DIR}
```

### 5. Path Conversion Function
Add utility function in `scripts/lib/vde-path-utils.zsh`:
```zsh
# Convert absolute path to HOME-relative path
vde_path_to_home_rel() {
    local abs_path="$1"
    if [[ "$abs_path" == "$HOME/"* ]]; then
        echo "~${abs_path#$HOME}"
    else
        echo "$abs_path"
    fi
}

# Convert HOME-relative path to absolute
vde_path_from_home_rel() {
    local rel_path="$1"
    if [[ "$rel_path" == "~"* ]]; then
        echo "${HOME}${rel_path#~}"
    else
        echo "$rel_path"
    fi
}
```

## Files to Modify

### Core Library Files (Must Update)
| File | Current Pattern | Change To |
|------|-----------------|-----------|
| `scripts/lib/vde-constants` | `$HOME` (hardcoded) | Use `$VDE_HOME_DIR` constant |
| `scripts/lib/vm-common:1812` | `$HOME/.ssh/id_ed25519` | `$VDE_SSH_IDENTITY` |
| `scripts/lib/vm-common:2217` | `$HOME/.ssh/id_ed25519` | `$VDE_SSH_IDENTITY` |
| `scripts/lib/vm-common` | `VDE_SSH_DIR="$HOME/.ssh/vde"` | Use `$VDE_SSH_DIR` constant |

### Script Files (Should Update)
| File | Current Pattern | Change To |
|------|-----------------|-----------|
| `scripts/ssh-setup` | `$HOME` references | Use `$VDE_HOME_DIR` |
| `scripts/ssh-agent-setup` | `$HOME` references | Use `$VDE_HOME_DIR` |
| `scripts/ssh-sync` | `$HOME` references | Use `$VDE_HOME_DIR` |

### Docker Compose Templates (Must Add env vars)
| File | Add |
|------|------|
| `configs/docker/base-dev.Dockerfile` | `ENV VDE_HOME=${HOME}` |
| `configs/docker/*/docker-compose.yml` | `environment: [VDE_HOME=${HOME}, VDE_PROJECT_NAME=${VDE_PROJECT_NAME}]` |

### New Files to Create
| File | Purpose |
|------|---------|
| `scripts/lib/vde-path-utils.zsh` | Path conversion utilities (`vde_path_to_home_rel`, `vde_path_from_home_rel`) |

### Files That Should Reference $VDE_PROJECT_NAME
| File | Usage |
|------|------|
| `scripts/vde` | Export `VDE_PROJECT_NAME` to subcommands |
| `scripts/lib/vm-common` | Calculate `$VDE_PROJECT_NAME` from `$VDE_ROOT_DIR` |
| `configs/docker/*/docker-compose.yml` | Pass `VDE_PROJECT_NAME` to containers |
| `env-files/*.env` | Optionally include `VDE_PROJECT_NAME` |

## Implementation Steps

### Phase 1: Constants Refactoring
1. [ ] Update `scripts/lib/vde-constants` to define `$VDE_HOME_DIR`-based constants
2. [ ] Add validation that `$HOME` is set and exists
3. [ ] Create `scripts/lib/vde-path-utils.zsh` with path conversion functions
4. [ ] Source path utilities in core libraries

### Phase 2: Path Updates
1. [ ] Update `scripts/lib/vm-common` to use `$VDE_SSH_DIR` constants (lines 1812, 2217)
2. [ ] Update `scripts/ssh-setup` to use `$VDE_HOME_DIR`
3. [ ] Update `scripts/ssh-agent-setup` to use `$VDE_HOME_DIR`
4. [ ] Update `scripts/ssh-sync` to use `$VDE_HOME_DIR`
5. [ ] Update docker-compose templates to use `$VDE_HOME` and `$VDE_PROJECT_NAME` environment variables

### Phase 3: VDE_ROOT_DIR Enhancement
1. [ ] Modify `scripts/lib/vm-common` to calculate and export `$VDE_PROJECT_NAME`
2. [ ] Update `scripts/vde` to set `$VDE_PROJECT_NAME` in environment
3. [ ] Add `$VDE_PROJECT_NAME` to `.env` files generated for VMs
4. [ ] Update documentation to reflect new path handling

### Phase 4: Testing and Documentation
1. [ ] Test on Linux native (`/home/<user>/`)
2. [ ] Test on WSL2 (`/home/<user>/`)
3. [ ] Test on macOS (`/Users/<user>/`)
4. [ ] Update `docs/ssh-configuration.md` with new path info
5. [ ] Add path utility documentation to `docs/development-workflows.md`

## Cross-Platform Considerations

| Platform | Home Path | Example |
|----------|-----------|---------|
| Linux native | `/home/<user>/` | `/home/devuser/.ssh/vde/` |
| WSL2 | `/home/<user>/` | `/home/devuser/.ssh/vde/` |
| macOS | `/Users/<user>/` | `/Users/devuser/.ssh/vde/` |

## Backward Compatibility

- Keep `$VDE_ROOT_DIR` as absolute path for internal operations
- `$VDE_PROJECT_NAME` is new and optional
- Existing configs and data remain compatible
- No breaking changes to user workflows

## Success Criteria

1. All SSH-related paths use `$HOME` or tilde notation
2. `$VDE_PROJECT_NAME` is correctly extracted from any installation path
3. Docker containers receive `$VDE_HOME` and `$VDE_PROJECT_NAME` environment variables
4. Scripts work identically on Linux, WSL2, and macOS
5. Installation to any path (e.g., `$HOME/projects/vde`) is supported
6. Only the project directory name is exposed to containers, not full paths
