# Function Map: `vde create python`

**Command:** `vde create python`  
**Entry Point:** [`scripts/vde`](../scripts/vde)  
**Completion:** Docker container `vde-python` running, SSH config updated, state saved

---

## Phase 0: Shell Startup & Library Loading

When the user hits Enter, the OS forks a new zsh process and executes [`scripts/vde`](../scripts/vde).

### Files Sourced (in order)

| # | File | Guard Variable | Purpose |
|---|------|---------------|---------|
| 1 | [`scripts/lib/vde-shell-compat`](../scripts/lib/vde-shell-compat) | `_VDE_SHELL_COMPAT_LOADED` | Portable shell operations |
| 2 | [`scripts/lib/vde-constants`](../scripts/lib/vde-constants) | `_VDE_CONSTANTS_LOADED` | All constants, port ranges, SSH dirs |
| 3 | [`scripts/lib/vde-errors`](../scripts/lib/vde-errors) | `_VDE_ERRORS_LOADED` | Error message functions |
| 4 | [`scripts/lib/vde-log`](../scripts/lib/vde-log) | `_VDE_LOG_LOADED` | Structured logging |
| 5 | [`scripts/lib/vde-core`](../scripts/lib/vde-core) | `_VDE_CORE_GUARD_LOADED` | Core VM type queries, schema validation |
| 6 | [`scripts/lib/vm-common`](../scripts/lib/vm-common) | `_VM_COMMON_LOADED` | Full VM management (sources 7–12 below) |
| 7 | ↳ [`scripts/lib/vde-log`](../scripts/lib/vde-log) | (already loaded) | |
| 8 | ↳ [`scripts/lib/vde-shell-compat`](../scripts/lib/vde-shell-compat) | (already loaded) | |
| 9 | ↳ [`scripts/lib/vde-constants`](../scripts/lib/vde-constants) | (already loaded) | |
| 10 | ↳ [`scripts/lib/vde-errors`](../scripts/lib/vde-errors) | (already loaded) | |
| 11 | ↳ [`scripts/lib/vde-naming`](../scripts/lib/vde-naming) | `_VDE_NAMING_LOADED` | `vde-` prefix enforcement |
| 12 | ↳ [`scripts/lib/vde-security`](../scripts/lib/vde-security) | `_VDE_SECURITY_LOADED` | Security policy enforcement |
| 13 | ↳ [`scripts/lib/vde-path-utils`](../scripts/lib/vde-path-utils) | `_VDE_PATH_UTILS_LOADED` | Path utilities |
| 14 | ↳ [`scripts/lib/vde-core`](../scripts/lib/vde-core) | (already loaded) | |
| 15 | [`scripts/lib/vde-docker-state`](../scripts/lib/vde-docker-state) | `_VDE_DOCKER_STATE_LOADED` | Docker state persistence |

**vm-common auto-initialization (at source time):**

| Function | File | Purpose |
|----------|------|---------|
| `load_vm_types()` | [`scripts/lib/vm-common`](../scripts/lib/vm-common:248) | Load VM type definitions from JSON/cache |
| ↳ `_is_cache_valid()` | [`scripts/lib/vm-common`](../scripts/lib/vm-common:216) | Check if `.cache/vm-types.cache` is fresh |
| ↳ `vde_get_schema_for_json()` | [`scripts/lib/vde-core`](../scripts/lib/vde-core) | Find JSON schema file |
| ↳ `vde_validate_json_schema()` | [`scripts/lib/vde-core`](../scripts/lib/vde-core) | Validate `vm-types.json` against schema |
| `_vm_common_load_modular_libs()` | [`scripts/lib/vm-common`](../scripts/lib/vm-common:155) | Lazy-load SSH, Docker, Templates libs |
| ↳ `_vde_ssh_source()` | [`scripts/lib/vm-common`](../scripts/lib/vm-common:130) | Source [`scripts/lib/vde-ssh`](../scripts/lib/vde-ssh) |
| ↳ `_vde_docker_source()` | [`scripts/lib/vm-common`](../scripts/lib/vm-common:138) | Source [`scripts/lib/vde-docker`](../scripts/lib/vde-docker) |
| ↳ `_vde_templates_source()` | [`scripts/lib/vm-common`](../scripts/lib/vm-common:146) | Source [`scripts/lib/vde-templates`](../scripts/lib/vde-templates) |

**Files read during `load_vm_types()`:**

| File | Condition |
|------|-----------|
| [`scripts/data/vm-types.json`](../scripts/data/vm-types.json) | Always (primary config) |
| [`.cache/vm-types.cache`](../.cache/vm-types.cache) | If cache is valid (skips JSON parse) |
| [`.cache/vm-types.cache`](../.cache/vm-types.cache) | Written if cache was stale/missing |

---

## Phase 1: `scripts/vde` — Argument Parsing & Dispatch

### Functions Called in `scripts/vde`

| Step | Function | File | Purpose |
|------|----------|------|---------|
| 1 | `vde_log_init()` | [`scripts/lib/vde-log`](../scripts/lib/vde-log:46) | Initialize log directory and file |
| 2 | *(argument parsing loop)* | [`scripts/vde`](../scripts/vde:319) | Parse `create` and `python` from `$@` |
| 3 | `vde_find_command_script()` | [`scripts/vde`](../scripts/vde:181) | Map `"create"` → `scripts/create-virtual-for` |
| 4 | `vde_run_command()` | [`scripts/vde`](../scripts/vde:278) | Validate script exists, make executable |
| 5 | `vde_log_info()` | [`scripts/lib/vde-log`](../scripts/lib/vde-log:222) | Log `"Running command: create python"` |
| 6 | *(exec)* | [`scripts/vde`](../scripts/vde:306) | Fork: `scripts/create-virtual-for python` |

**Files touched:**
- [`logs/vde.log`](../logs/vde.log) — written by `vde_log_init()` and `vde_log_info()`

---

## Phase 2: `scripts/create-virtual-for python` — VM Creation

### 2a. Library Loading (create-virtual-for sources vm-common)

| File | Purpose |
|------|---------|
| [`scripts/lib/vm-common`](../scripts/lib/vm-common) | (all libs above, already loaded via source guard) |
| [`scripts/lib/vde-progress`](../scripts/lib/vde-progress) | Progress indicators |
| [`scripts/lib/vde-errors`](../scripts/lib/vde-errors) | Error messages |
| [`scripts/lib/vde-naming`](../scripts/lib/vde-naming) | Naming convention helpers |

### 2b. Validation Phase

| Step | Function | File | Purpose |
|------|----------|------|---------|
| 1 | `vde_progress_info()` | [`scripts/lib/vde-progress`](../scripts/lib/vde-progress:356) | Print "Validating configuration for 'python'..." |
| 2 | `resolve_vm_name()` | [`scripts/lib/vm-common`](../scripts/lib/vm-common:832) | Resolve `"python"` → canonical name (checks `VM_TYPE`, aliases) |
| 3 | `get_vm_info()` | [`scripts/lib/vm-common`](../scripts/lib/vm-common:677) | Get `type` field → `"lang"` |
| 4 | `get_vm_info()` | [`scripts/lib/vm-common`](../scripts/lib/vm-common:677) | Get `display` field → `"Python"` |
| 5 | `get_vm_info()` | [`scripts/lib/vm-common`](../scripts/lib/vm-common:677) | Get `install` field → install command |
| 6 | `get_vm_info()` | [`scripts/lib/vm-common`](../scripts/lib/vm-common:677) | Get `svc_port` field → `""` (lang VM has none) |
| 7 | `validate_vm_name()` | [`scripts/lib/vm-common`](../scripts/lib/vm-common:865) → `vde_validate_name()` | Validate name format |
| 8 | `vde_validate_name()` | [`scripts/lib/vde-naming`](../scripts/lib/vde-naming:21) | Check `^[a-z0-9-]+$` pattern |
| 9 | `vm_exists()` | [`scripts/lib/vm-common`](../scripts/lib/vm-common:782) → `vm_is_created()` | Check `.docker-state/python.json` |
| 10 | `vm_is_created()` | [`scripts/lib/vm-common`](../scripts/lib/vm-common:756) | Check if `.docker-state/python.json` exists |
| 11 | `get_docker_state_dir()` | [`scripts/lib/vm-common`](../scripts/lib/vm-common:1070) | Returns `$VDE_ROOT_DIR/.docker-state` |

**Files read:**
- [`.docker-state/python.json`](../.docker-state/python.json) — checked for existence (must NOT exist)

### 2c. Port Allocation

| Step | Function | File | Purpose |
|------|----------|------|---------|
| 1 | `vde_progress_info()` | [`scripts/lib/vde-progress`](../scripts/lib/vde-progress:356) | Print "Allocating SSH port..." |
| 2 | `find_next_available_port()` | [`scripts/lib/vm-common`](../scripts/lib/vm-common:944) | Find next free port in 2200-2299 |
| 3 | `find_available_port()` | [`scripts/lib/vm-common`](../scripts/lib/vm-common:969) | Iterate ports, check each |
| 4 | `_is_port_in_use()` | [`scripts/lib/vde-docker`](../scripts/lib/vde-docker:212) | `nc -z localhost $port` or check registry |

**Files read:**
- [`.cache/port-registry/`](../.cache/port-registry/) — per-VM `.port` files checked

### 2d. Directory Creation

| Step | Function | File | Purpose |
|------|----------|------|---------|
| 1 | `vde_progress_info()` | [`scripts/lib/vde-progress`](../scripts/lib/vde-progress:356) | Print "Creating directory structure..." |
| 2 | `ensure_vm_directories()` | [`scripts/lib/vm-common`](../scripts/lib/vm-common:1141) | Create required dirs |
| 3 | `vde_normalize_name()` | [`scripts/lib/vde-naming`](../scripts/lib/vde-naming:54) | Strip `vde-` prefix → `"python"` |

**Files/directories created:**
- [`configs/docker/python/`](../configs/docker/python/) — config dir (if absent)
- [`projects/python/`](../projects/python/) — workspace dir (if absent)
- [`logs/python/`](../logs/python/) — log dir (if absent)

### 2e. Docker Compose File Generation

| Step | Function | File | Purpose |
|------|----------|------|---------|
| 1 | `vde_progress_info()` | [`scripts/lib/vde-progress`](../scripts/lib/vde-progress:356) | Print "Creating docker-compose.yml..." |
| 2 | `vde_normalize_name()` | [`scripts/lib/vde-naming`](../scripts/lib/vde-naming:54) | `"python"` → `"python"` (raw name for path) |
| 3 | `render_template()` | [`scripts/lib/vde-templates`](../scripts/lib/vde-templates:49) | Render `compose-language.yml` with vars |
| 4 | `vde_progress_done()` | [`scripts/lib/vde-progress`](../scripts/lib/vde-progress:345) | Print "Created: configs/docker/python/docker-compose.yml" |

**Files read:**
- [`scripts/templates/compose-language.yml`](../scripts/templates/compose-language.yml) — template source

**Files written:**
- [`configs/docker/python/docker-compose.yml`](../configs/docker/python/docker-compose.yml) — rendered compose file

### 2f. Environment File Creation

| Step | Function | File | Purpose |
|------|----------|------|---------|
| 1 | `vde_progress_info()` | [`scripts/lib/vde-progress`](../scripts/lib/vde-progress:356) | Print "Creating environment file..." |
| 2 | *(heredoc write)* | [`scripts/create-virtual-for`](../scripts/create-virtual-for:229) | Write env vars to file |
| 3 | `vde_progress_done()` | [`scripts/lib/vde-progress`](../scripts/lib/vde-progress:345) | Print "Created: env-files/python.env" |

**Files written:**
- [`env-files/python.env`](../env-files/python.env) — SSH_PORT, DATABASE_URL, REDIS_HOST, etc.

### 2g. SSH Config Update

| Step | Function | File | Purpose |
|------|----------|------|---------|
| 1 | `vde_progress_info()` | [`scripts/lib/vde-progress`](../scripts/lib/vde-progress:356) | Print "Updating SSH configuration..." |
| 2 | `vde_get_ssh_host()` | [`scripts/lib/vde-naming`](../scripts/lib/vde-naming:72) | Returns `"vde-python"` |
| 3 | `merge_ssh_config_entry()` | [`scripts/lib/vde-ssh`](../scripts/lib/vde-ssh:299) | Atomically add SSH Host block |

**Inside `merge_ssh_config_entry()`:**

| Step | Function | File | Purpose |
|------|----------|------|---------|
| 1 | *(backup)* | [`scripts/lib/vde-ssh`](../scripts/lib/vde-ssh) | `cp ~/.ssh/vde/config → backup/ssh/config.backup.TIMESTAMP` |
| 2 | *(duplicate check)* | [`scripts/lib/vde-ssh`](../scripts/lib/vde-ssh) | `grep "^Host vde-python"` in config |
| 3 | *(atomic write)* | [`scripts/lib/vde-ssh`](../scripts/lib/vde-ssh) | `mktemp` → append → `mv` → `chmod 600` |

**Files read/written:**
- [`~/.ssh/vde/config`](~/.ssh/vde/config) — VDE SSH config (read + written)
- [`backup/ssh/config.backup.TIMESTAMP`](../backup/ssh/) — timestamped backup (written)
- [`configs/ssh/config`](../configs/ssh/config) — project reference copy (written via `cp`)

### 2h. VM Start (default: `START_VM=true`)

| Step | Function | File | Purpose |
|------|----------|------|---------|
| 1 | `vde_progress_info()` | [`scripts/lib/vde-progress`](../scripts/lib/vde-progress:356) | Print "Starting VM..." |
| 2 | *(exec)* | [`scripts/create-virtual-for`](../scripts/create-virtual-for:278) | `docker-compose -f configs/docker/python/docker-compose.yml up -d` |
| 3 | `vde_progress_done()` | [`scripts/lib/vde-progress`](../scripts/lib/vde-progress:345) | Print "Started VM: python" |
| 4 | `save_docker_state()` | [`scripts/lib/vm-common`](../scripts/lib/vm-common:1076) | Write state JSON to `.docker-state/` |
| 5 | `get_docker_state_dir()` | [`scripts/lib/vm-common`](../scripts/lib/vm-common:1070) | Returns `.docker-state/` path |
| 6 | `vde_normalize_name()` | [`scripts/lib/vde-naming`](../scripts/lib/vde-naming:54) | `"python"` → `"python"` for filename |

**Files written:**
- [`.docker-state/python.json`](../.docker-state/python.json) — VM state (name, type, port, status, created_at)

### 2i. Summary Output

| Step | Function | File | Purpose |
|------|----------|------|---------|
| 1 | `vde_success()` | [`scripts/lib/vde-errors`](../scripts/lib/vde-errors:299) | Print "VM configuration complete!" |

---

## Complete Function Call Tree

```
vde create python
│
├── [scripts/vde]
│   ├── source vde-shell-compat
│   ├── source vde-constants
│   ├── source vde-errors
│   ├── source vde-log
│   ├── source vde-core
│   │   ├── source vde-shell-compat (guard: skip)
│   │   └── source vde-constants (guard: skip)
│   ├── source vm-common
│   │   ├── source vde-log (guard: skip)
│   │   ├── source vde-shell-compat (guard: skip)
│   │   ├── source vde-constants (guard: skip)
│   │   ├── source vde-errors (guard: skip)
│   │   ├── source vde-naming          ← NEW
│   │   ├── source vde-security        ← NEW
│   │   ├── source vde-path-utils
│   │   ├── source vde-core (guard: skip)
│   │   ├── load_vm_types()
│   │   │   ├── _is_cache_valid()
│   │   │   ├── vde_get_schema_for_json()
│   │   │   ├── vde_validate_json_schema()
│   │   │   └── [writes .cache/vm-types.cache if stale]
│   │   └── _vm_common_load_modular_libs()
│   │       ├── _vde_ssh_source() → source vde-ssh
│   │       ├── _vde_docker_source() → source vde-docker
│   │       └── _vde_templates_source() → source vde-templates
│   ├── source vde-docker-state
│   ├── vde_log_init()
│   ├── [parse args: CMD="create", args=["python"]]
│   ├── vde_find_command_script("create") → "scripts/create-virtual-for"
│   ├── vde_run_command("create", "python")
│   │   └── vde_log_info("Running command: create python")
│   └── exec: scripts/create-virtual-for python
│
└── [scripts/create-virtual-for python]
    ├── source vm-common (guard: skip — already loaded)
    ├── source vde-progress
    ├── source vde-errors (guard: skip)
    ├── source vde-naming (guard: skip)
    │
    ├── vde_progress_info("Validating...")
    ├── resolve_vm_name("python")
    │   └── [checks VM_TYPE["python"], VM_TYPE["vde-python"], aliases]
    ├── get_vm_info("type", "python") → "lang"
    ├── get_vm_info("display", "python") → "Python"
    ├── get_vm_info("install", "python") → install cmd
    ├── get_vm_info("svc_port", "python") → ""
    ├── validate_vm_name("python", "lang")
    │   └── vde_validate_name("python")
    ├── vm_exists("python")
    │   └── vm_is_created("python")
    │       └── get_docker_state_dir() → ".docker-state"
    │           [reads: .docker-state/python.json — must NOT exist]
    │
    ├── vde_progress_info("Allocating SSH port...")
    ├── find_next_available_port("lang")
    │   └── find_available_port(2200, 2299)
    │       └── _is_port_in_use(2213..N)
    │           [reads: .cache/port-registry/*.port, nc -z localhost PORT]
    │
    ├── vde_progress_info("Creating directory structure...")
    ├── ensure_vm_directories("python", "lang")
    │   └── vde_normalize_name("python") → "python"
    │   [creates: configs/docker/python/, projects/python/, logs/python/]
    │
    ├── vde_progress_info("Creating docker-compose.yml...")
    ├── vde_normalize_name("python") → "python"
    ├── render_template("scripts/templates/compose-language.yml", NAME=python, ...)
    │   [reads: scripts/templates/compose-language.yml]
    │   [writes: configs/docker/python/docker-compose.yml]
    ├── vde_progress_done("Created: configs/docker/python/docker-compose.yml")
    │
    ├── vde_progress_info("Creating environment file...")
    │   [writes: env-files/python.env]
    ├── vde_progress_done("Created: env-files/python.env")
    │
    ├── vde_progress_info("Updating SSH configuration...")
    ├── vde_get_ssh_host("python") → "vde-python"
    ├── merge_ssh_config_entry("vde-python", PORT, "Python", IDENTITY)
    │   [reads: ~/.ssh/vde/config]
    │   [writes: backup/ssh/config.backup.TIMESTAMP]
    │   [writes: ~/.ssh/vde/config (atomic: mktemp → mv → chmod 600)]
    │   [writes: configs/ssh/config (cp of updated config)]
    │
    ├── vde_progress_info("Starting VM...")
    ├── docker-compose -f configs/docker/python/docker-compose.yml up -d
    ├── vde_progress_done("Started VM: python")
    ├── save_docker_state("python", JSON)
    │   ├── get_docker_state_dir() → ".docker-state"
    │   └── vde_normalize_name("python") → "python"
    │   [writes: .docker-state/python.json]
    │
    └── vde_success("VM configuration complete!")
```

---

## All Files Touched

### Read
| File | Phase | Purpose |
|------|-------|---------|
| [`scripts/lib/vde-shell-compat`](../scripts/lib/vde-shell-compat) | 0 | Sourced |
| [`scripts/lib/vde-constants`](../scripts/lib/vde-constants) | 0 | Sourced |
| [`scripts/lib/vde-errors`](../scripts/lib/vde-errors) | 0 | Sourced |
| [`scripts/lib/vde-log`](../scripts/lib/vde-log) | 0 | Sourced |
| [`scripts/lib/vde-core`](../scripts/lib/vde-core) | 0 | Sourced |
| [`scripts/lib/vm-common`](../scripts/lib/vm-common) | 0 | Sourced |
| [`scripts/lib/vde-naming`](../scripts/lib/vde-naming) | 0 | Sourced via vm-common |
| [`scripts/lib/vde-security`](../scripts/lib/vde-security) | 0 | Sourced via vm-common |
| [`scripts/lib/vde-path-utils`](../scripts/lib/vde-path-utils) | 0 | Sourced via vm-common |
| [`scripts/lib/vde-ssh`](../scripts/lib/vde-ssh) | 0 | Sourced via vm-common |
| [`scripts/lib/vde-docker`](../scripts/lib/vde-docker) | 0 | Sourced via vm-common |
| [`scripts/lib/vde-templates`](../scripts/lib/vde-templates) | 0 | Sourced via vm-common |
| [`scripts/lib/vde-docker-state`](../scripts/lib/vde-docker-state) | 0 | Sourced by vde |
| [`scripts/lib/vde-progress`](../scripts/lib/vde-progress) | 2 | Sourced by create-virtual-for |
| [`scripts/data/vm-types.json`](../scripts/data/vm-types.json) | 0 | VM type definitions |
| [`.cache/vm-types.cache`](../.cache/vm-types.cache) | 0 | VM type cache (if valid) |
| [`.cache/port-registry/*.port`](../.cache/port-registry/) | 2c | Port allocation check |
| [`.docker-state/python.json`](../.docker-state/python.json) | 2b | Existence check (must be absent) |
| [`scripts/templates/compose-language.yml`](../scripts/templates/compose-language.yml) | 2e | Docker compose template |
| [`~/.ssh/vde/config`](~/.ssh/vde/config) | 2g | SSH config (read before merge) |

### Written / Created
| File | Phase | Purpose |
|------|-------|---------|
| [`logs/vde.log`](../logs/vde.log) | 1 | Command execution log |
| [`.cache/vm-types.cache`](../.cache/vm-types.cache) | 0 | Regenerated if stale |
| [`configs/docker/python/`](../configs/docker/python/) | 2d | Config directory |
| [`projects/python/`](../projects/python/) | 2d | Workspace directory |
| [`logs/python/`](../logs/python/) | 2d | Log directory |
| [`configs/docker/python/docker-compose.yml`](../configs/docker/python/docker-compose.yml) | 2e | Rendered compose file |
| [`env-files/python.env`](../env-files/python.env) | 2f | Environment variables |
| [`backup/ssh/config.backup.TIMESTAMP`](../backup/ssh/) | 2g | SSH config backup |
| [`~/.ssh/vde/config`](~/.ssh/vde/config) | 2g | Updated SSH config |
| [`configs/ssh/config`](../configs/ssh/config) | 2g | Project reference copy |
| [`.docker-state/python.json`](../.docker-state/python.json) | 2h | VM state record |

### External Processes Spawned
| Process | Phase | Purpose |
|---------|-------|---------|
| `nc -z localhost PORT` | 2c | Port availability check |
| `jq` | 0 | JSON parsing of vm-types.json |
| `zsh -n .cache/vm-types.cache` | 0 | Cache syntax validation |
| `docker-compose up -d` | 2h | Start the container |
| `docker network inspect vde-net` | 0* | Network check (via vde-security) |

*`vde_security_init()` is called when `vde-security` is sourced via `vm-common`, which triggers `vde_security_ensure_network()` → `docker network inspect vde-net`.

---

## Summary: All Functions Fired

| # | Function | Library | Phase |
|---|----------|---------|-------|
| 1 | `vde_log_init()` | `vde-log` | 1 |
| 2 | `vde_find_command_script()` | `vde` | 1 |
| 3 | `vde_run_command()` | `vde` | 1 |
| 4 | `vde_log_info()` | `vde-log` | 1 |
| 5 | `load_vm_types()` | `vm-common` | 0 |
| 6 | `_is_cache_valid()` | `vm-common` | 0 |
| 7 | `vde_get_schema_for_json()` | `vde-core` | 0 |
| 8 | `vde_validate_json_schema()` | `vde-core` | 0 |
| 9 | `_vm_common_load_modular_libs()` | `vm-common` | 0 |
| 10 | `_vde_ssh_source()` | `vm-common` | 0 |
| 11 | `_vde_docker_source()` | `vm-common` | 0 |
| 12 | `_vde_templates_source()` | `vm-common` | 0 |
| 13 | `vde_security_init()` | `vde-security` | 0* |
| 14 | `vde_security_ensure_network()` | `vde-security` | 0* |
| 15 | `vde_security_enforce_permissions()` | `vde-security` | 0* |
| 16 | `vde_security_enforce_network_isolation()` | `vde-security` | 0* |
| 17 | `vde_progress_info()` | `vde-progress` | 2 |
| 18 | `resolve_vm_name()` | `vm-common` | 2b |
| 19 | `get_vm_info()` | `vm-common` | 2b |
| 20 | `validate_vm_name()` | `vm-common` | 2b |
| 21 | `vde_validate_name()` | `vde-naming` | 2b |
| 22 | `vm_exists()` | `vm-common` | 2b |
| 23 | `vm_is_created()` | `vm-common` | 2b |
| 24 | `get_docker_state_dir()` | `vm-common` | 2b |
| 25 | `find_next_available_port()` | `vm-common` | 2c |
| 26 | `find_available_port()` | `vm-common` | 2c |
| 27 | `_is_port_in_use()` | `vde-docker` | 2c |
| 28 | `ensure_vm_directories()` | `vm-common` | 2d |
| 29 | `vde_normalize_name()` | `vde-naming` | 2d, 2e, 2h |
| 30 | `render_template()` | `vde-templates` | 2e |
| 31 | `vde_progress_done()` | `vde-progress` | 2e, 2f, 2h |
| 32 | `vde_get_ssh_host()` | `vde-naming` | 2g |
| 33 | `merge_ssh_config_entry()` | `vde-ssh` | 2g |
| 34 | `save_docker_state()` | `vm-common` | 2h |
| 35 | `vde_success()` | `vde-errors` | 2i |

*Phase 0 = triggered at library source time, before argument parsing.
