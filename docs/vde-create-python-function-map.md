# Function Map: `vde create python` Execution Trace

## Context

This document provides a complete execution trace of the `vde create python` command, mapping every function call, library dependency, and file operation from user input to command completion. This provides comprehensive architectural understanding of VDE's VM creation pipeline.

**Command:** `vde create python`
**Entry Point:** [`scripts/vde`](../scripts/vde)
**Completion:** Docker container `vde-python` running, SSH config updated, state saved

---

## Phase 0: Entry Point & Bootstrap

**File**: [`scripts/vde`](../scripts/vde)

**Execution Flow**:
```
1. User executes: vde create python
2. Shebang invoked: #!/usr/bin/env zsh
3. VDE_ROOT_DIR="${0:a:h:h}" → ~/dev
4. Source libraries (lines 35-41):
   ├─ vde-shell-compat
   ├─ vde-constants
   ├─ vde-errors
   ├─ vde-log
   ├─ vde-core
   ├─ vm-common
   └─ vde-docker-state
5. vde_log_init() → Initialize logging system
```

**Functions Called**:
- `vde_log_init()` ([vde-log:44](../scripts/lib/vde-log#L44))

**Files Read**:
- [`scripts/lib/vde-shell-compat`](../scripts/lib/vde-shell-compat)
- [`scripts/lib/vde-constants`](../scripts/lib/vde-constants)
- [`scripts/lib/vde-errors`](../scripts/lib/vde-errors)
- [`scripts/lib/vde-log`](../scripts/lib/vde-log)
- [`scripts/lib/vde-core`](../scripts/lib/vde-core)
- [`scripts/lib/vm-common`](../scripts/lib/vm-common)
- [`scripts/lib/vde-docker-state`](../scripts/lib/vde-docker-state)

---

## Phase 1: Argument Parsing

**File**: [`scripts/vde`](../scripts/vde) (lines 314-427)

**Execution Flow**:
```
1. Parse global options (-v, --verbose, -q, --quiet, --help, --version)
2. CMD="create", shift to remaining args
3. Special create handling (lines 368-427):
   ├─ Check for --rebuild or --nocache flags
   ├─ If present: two-step process (create + start with rebuild)
   └─ If absent: normal create process
4. vde_run_command("create", "python")
   └─ vde_find_command_script("create") → returns scripts/create-virtual-for
   └─ Execute: scripts/create-virtual-for python
```

**Functions Called**:
- `vde_run_command()` ([vde:277](../scripts/vde#L277))
  - `vde_find_command_script()` ([vde:180](../scripts/vde#L180))
  - `vde_log_info()` (vde-log)

**Files Read**: None (conditional logic only)

---

## Phase 2: Create Virtual For Script - Initialization

**File**: [`scripts/create-virtual-for`](../scripts/create-virtual-for)

**Execution Flow**:
```
1. Shebang: #!/usr/bin/env zsh
2. set -e (strict error handling)
3. Source vm-common (line 14)
   ├─ vm-common sources:
   │  ├─ vde-log
   │  ├─ vde-shell-compat
   │  ├─ vde-constants
   │  ├─ vde-errors
   │  ├─ vde-naming
   │  ├─ vde-security
   │  ├─ vde-path-utils
   │  └─ vde-core
   └─ vm-common lazy-loads:
      ├─ vde-ssh (on first SSH operation)
      ├─ vde-docker (on first Docker operation)
      └─ vde-templates (on first template render)

4. Conditionally source UX libraries (lines 17-19):
   ├─ vde-progress (if exists)
   ├─ vde-errors (if not already loaded)
   └─ vde-naming (if not already loaded)
```

**Functions Called**: None yet (library loading only)

**Files Read**:
- [`scripts/lib/vm-common`](../scripts/lib/vm-common)
- [`scripts/lib/vde-progress`](../scripts/lib/vde-progress) (conditional)
- [`scripts/lib/vde-naming`](../scripts/lib/vde-naming) (if not loaded by vm-common)
- [`scripts/lib/vde-security`](../scripts/lib/vde-security)
- [`scripts/lib/vde-path-utils`](../scripts/lib/vde-path-utils)
- [`scripts/lib/vde-ssh`](../scripts/lib/vde-ssh) (lazy)
- [`scripts/lib/vde-docker`](../scripts/lib/vde-docker) (lazy)
- [`scripts/lib/vde-templates`](../scripts/lib/vde-templates) (lazy)

---

## Phase 3: VM Name Resolution & Validation

**File**: [`scripts/create-virtual-for`](../scripts/create-virtual-for) (lines 114-144)

**Execution Flow**:
```
1. vde_progress_info("Validating VM name: python")
2. resolve_vm_name("python")
   ├─ Check if "python" matches canonical name pattern
   ├─ Check if "vde-python" exists in VM_TYPES
   ├─ Check VM_ALIASES map for "python" → "vde-python"
   └─ Return: "vde-python"

3. If resolution fails:
   ├─ vde_error_alias_not_found("python")
   └─ show_known_vms()
      ├─ get_lang_vms() → [list of language VMs]
      └─ get_service_vms() → [list of service VMs]

4. Load VM configuration:
   get_vm_info("vde-python")
   └─ load_vm_types() (first call, cached thereafter)
      ├─ Read: $VDE_ROOT_DIR/scripts/data/vm-types.json
      ├─ Parse JSON with jq
      ├─ Cache in associative arrays:
      │  ├─ VM_TYPES_NAME[vde-python]="vde-python"
      │  ├─ VM_TYPES_TYPE[vde-python]="lang"
      │  ├─ VM_TYPES_DISPLAY[vde-python]="Python Language Development"
      │  ├─ VM_TYPES_INSTALL[vde-python]="apt-get install -y python3..."
      │  └─ VM_TYPES_PORT[vde-python]=""
      └─ Return VM metadata

5. Validate VM name format:
   validate_vm_name("vde-python")
   └─ vde_validate_name("vde-python") (from vde-naming)
      ├─ Check: starts with "vde-"
      ├─ Check: lowercase alphanumeric + hyphens only
      ├─ Check: no consecutive hyphens
      └─ Return: 0 (success)

6. Check if VM already exists:
   vm_exists("vde-python")
   ├─ Check Docker container exists:
   │  └─ docker ps -a --format '{{.Names}}' | grep -q "^vde-python$"
   ├─ Check config directory exists:
   │  └─ test -d configs/docker/python
   └─ Check docker-state file exists:
      └─ test -f .docker-state/python.json
   If any exist: vde_error_container_exists("vde-python") → exit
```

**Functions Called**:
- `vde_progress_info()` (vde-progress)
- `resolve_vm_name()` ([vm-common:829](../scripts/lib/vm-common#L829))
- `vde_error_alias_not_found()` (vde-errors) [conditional]
- `show_known_vms()` ([vm-common:1169](../scripts/lib/vm-common#L1169)) [conditional]
  - `get_lang_vms()` (vm-common)
  - `get_service_vms()` (vm-common)
- `get_vm_info()` ([vm-common:677](../scripts/lib/vm-common#L677))
  - `load_vm_types()` (vm-common) [first call only]
- `validate_vm_name()` ([vm-common:865](../scripts/lib/vm-common#L865))
  - `vde_validate_name()` (vde-naming)
- `vm_exists()` ([vm-common:782](../scripts/lib/vm-common#L782))
  - `vm_container_exists()` (vde-docker-state)
- `vde_error_container_exists()` (vde-errors) [conditional on exists]

**Files Read**:
- [`scripts/data/vm-types.json`](../scripts/data/vm-types.json)

**Files Checked** (existence):
- `configs/docker/python/` (directory)
- `.docker-state/python.json`

**External Commands**:
- `docker ps -a --format '{{.Names}}'` (via vm_container_exists)

---

## Phase 4: Port Allocation

**File**: [`scripts/create-virtual-for`](../scripts/create-virtual-for) (lines 150-158)

**Execution Flow**:
```
1. find_next_available_port("vde-python", "lang")
   ├─ Determine port range based on VM type:
   │  └─ type="lang" → range 2200-2299 (VDE_LANG_PORT_START to VDE_LANG_PORT_END)
   └─ find_available_port(2200, 2299)
      ├─ For port in {2200..2299}:
      │  ├─ _is_port_in_use(port)
      │  │  ├─ Try: sockstat -l | awk '{print $3}' | grep -q "^$port$"
      │  │  ├─ Fallback: lsof -i ":$port"
      │  │  └─ Fallback: netstat -tan | grep ":$port "
      │  └─ If not in use: return port
      └─ Return: 2213 (first available)

2. SSH_PORT=2213
```

**Functions Called**:
- `find_next_available_port()` ([vm-common:944](../scripts/lib/vm-common#L944))
  - `find_available_port()` ([vm-common:969](../scripts/lib/vm-common#L969))
    - `_is_port_in_use()` (vde-docker)

**External Commands**:
- `sockstat -l | awk '{print $3}' | grep -q "^2213$"` [or lsof/netstat fallback]

---

## Phase 5: Directory Creation

**File**: [`scripts/create-virtual-for`](../scripts/create-virtual-for) (lines 162-164)

**Execution Flow**:
```
1. ensure_vm_directories("vde-python", "lang")
   ├─ vde_normalize_name("vde-python") → "python" (raw name)
   ├─ Create directories for type="lang":
   │  ├─ mkdir -p configs/docker/python
   │  ├─ mkdir -p projects/python
   │  └─ mkdir -p logs/python
   └─ Return 0
```

**Functions Called**:
- `ensure_vm_directories()` ([vm-common:1141](../scripts/lib/vm-common#L1141))
  - `vde_normalize_name()` (vde-naming)

**Directories Created**:
- `$VDE_ROOT_DIR/configs/docker/python/`
- `$VDE_ROOT_DIR/projects/python/`
- `$VDE_ROOT_DIR/logs/python/`

---

## Phase 6: Docker Compose File Generation

**File**: [`scripts/create-virtual-for`](../scripts/create-virtual-for) (lines 169-219)

**Execution Flow**:
```
1. vde_normalize_name("vde-python") → RAW_NAME="python"

2. Select template based on VM type:
   ├─ type="lang" → template_file="templates/compose-language.yml"
   └─ type="service" → template_file="templates/compose-service.yml"

3. render_template()
   ├─ Lazy-load vde-templates library (if not already loaded)
   ├─ Read template file: templates/compose-language.yml
   ├─ Perform substitutions:
   │  ├─ {{NAME}} → "python"
   │  ├─ {{SSH_PORT}} → "2213"
   │  ├─ {{INSTALL_CMD}} → "apt-get install -y python3 python3-pip python3-venv..."
   │  └─ {{SERVICE_PORT}} → "" (empty for language VMs)
   ├─ Handle SERVICE_PORTS (lines 194-212):
   │  └─ For lang VMs: Remove ##SERVICE_PORTS## line
   └─ Write output: configs/docker/python/docker-compose.yml

4. If VDE_TEST_MODE set:
   └─ cat configs/docker/python/docker-compose.yml (for test verification)
```

**Functions Called**:
- `vde_normalize_name()` (vde-naming)
- `render_template()` ([vde-templates:49](../scripts/lib/vde-templates#L49))
  - Internal: `_substitute_variables()` (vde-templates)
  - Internal: `_handle_service_ports()` (vde-templates)

**Files Read**:
- [`scripts/templates/compose-language.yml`](../scripts/templates/compose-language.yml)

**Files Written**:
- [`configs/docker/python/docker-compose.yml`](../configs/docker/python/docker-compose.yml)

---

## Phase 7: Environment File Creation

**File**: [`scripts/create-virtual-for`](../scripts/create-virtual-for) (lines 224-248)

**Execution Flow**:
```
1. Create env file directory:
   mkdir -p env-files

2. Generate environment variables:
   ├─ SSH_PORT=2213
   ├─ DATABASE_URL=postgresql://devuser:SuperSecretPassword123!@postgres:5432/python_dev_db
   ├─ REDIS_HOST=redis
   └─ REDIS_PORT=6379

3. Write to file: env-files/python.env
```

**Directories Created**:
- `$VDE_ROOT_DIR/env-files/`

**Files Written**:
- [`env-files/python.env`](../env-files/python.env)

---

## Phase 8: SSH Configuration

**File**: [`scripts/create-virtual-for`](../scripts/create-virtual-for) (lines 253-268)

**Execution Flow**:
```
1. vde_get_ssh_host("vde-python") → "vde-python"
   └─ vde_get_container_name("vde-python")
      ├─ Check: name starts with "vde-" → return as-is
      └─ Else: return "vde-" + name

2. merge_ssh_config_entry()
   ├─ Lazy-load vde-ssh library
   ├─ Parameters:
   │  ├─ host_alias="vde-python"
   │  ├─ ssh_port=2213
   │  ├─ display_name="Python Language Development"
   │  └─ identity_file="~/.ssh/vde/vde_rsa"
   ├─ Backup existing config:
   │  └─ cp ~/.ssh/vde/config ~/.ssh/vde/config.vde-backup-$(date +%Y%m%d_%H%M%S)
   ├─ Remove existing entry for "vde-python" (if present)
   ├─ Append new SSH host entry:
   │  Host vde-python
   │      HostName localhost
   │      Port 2213
   │      User devuser
   │      IdentityFile ~/.ssh/vde/vde_rsa
   │      StrictHostKeyChecking no
   │      UserKnownHostsFile ~/.ssh/vde/known_hosts
   │      ForwardAgent yes
   │      LogLevel ERROR
   └─ Write to: ~/.ssh/vde/config

3. Copy SSH config to project configs:
   cp ~/.ssh/vde/config configs/ssh/config
```

**Functions Called**:
- `vde_get_ssh_host()` ([vde-naming:71](../scripts/lib/vde-naming#L71))
  - `vde_get_container_name()` (vde-naming)
- `merge_ssh_config_entry()` ([vde-ssh:299](../scripts/lib/vde-ssh#L299))
  - Internal: `_remove_ssh_entry()` (vde-ssh)
  - Internal: `_append_ssh_entry()` (vde-ssh)

**Files Read**:
- `~/.ssh/vde/config` (existing SSH config)

**Files Written**:
- `~/.ssh/vde/config.vde-backup-20260219_123045` (backup)
- `~/.ssh/vde/config` (updated)
- [`configs/ssh/config`](../configs/ssh/config) (copy)

---

## Phase 9: VM Startup (Docker Compose)

**File**: [`scripts/create-virtual-for`](../scripts/create-virtual-for) (lines 273-299)

**Execution Flow**:
```
1. If START_VM="true" (default):
   ├─ compose_file="configs/docker/python/docker-compose.yml"
   ├─ vde_progress_info("Starting VM: vde-python")
   ├─ Execute Docker Compose:
   │  └─ docker-compose -f configs/docker/python/docker-compose.yml up -d
   │     ├─ Pull base image: ubuntu:24.04
   │     ├─ Build container with:
   │     │  ├─ Install SSH server
   │     │  ├─ Execute INSTALL_CMD (Python installation)
   │     │  ├─ Configure devuser account
   │     │  └─ Set up SSH keys
   │     └─ Start container in detached mode
   │
   └─ If success:
      ├─ save_docker_state("vde-python", state_data)
      │  ├─ Create JSON object:
      │  │  {
      │  │    "vm_name": "vde-python",
      │  │    "vm_type": "lang",
      │  │    "display_name": "Python Language Development",
      │  │    "ssh_port": 2213,
      │  │    "service_port": "",
      │  │    "created_at": "2026-02-19T12:30:45Z",
      │  │    "status": "running"
      │  │  }
      │  └─ Write to: .docker-state/python.json
      └─ vde_success("VM vde-python started successfully")

   If failure:
      └─ vde_error_docker_build_failed("vde-python") → exit 1
```

**Functions Called**:
- `vde_progress_info()` (vde-progress)
- `save_docker_state()` ([vm-common:1076](../scripts/lib/vm-common#L1076))
  - `vde_normalize_name()` (vde-naming)
  - `_date_iso8601()` (vde-shell-compat)
- `vde_success()` (vde-errors)
- `vde_error_docker_build_failed()` (vde-errors) [conditional]

**External Commands**:
- `docker-compose -f configs/docker/python/docker-compose.yml up -d`
  - Internal Docker operations:
    - `docker pull ubuntu:24.04`
    - `docker build` (container creation)
    - `docker run` (container startup)

**Files Written**:
- [`.docker-state/python.json`](../.docker-state/python.json)

---

## Phase 10: Summary Display

**File**: [`scripts/create-virtual-for`](../scripts/create-virtual-for) (lines 304-322)

**Execution Flow**:
```
1. vde_success("VM vde-python created and configured successfully")

2. Display created resources:
   ├─ Docker Compose file: configs/docker/python/docker-compose.yml
   ├─ Environment file: env-files/python.env
   ├─ Project directory: projects/python/
   └─ Logs directory: logs/python/

3. Display SSH configuration:
   ├─ SSH host: vde-python
   ├─ SSH port: 2213
   └─ Connection command: ssh vde-python

4. Exit with status 0 (VDE_SUCCESS)
```

**Functions Called**:
- `vde_success()` (vde-errors)
- `vde_log_info()` (vde-log)

---

## Complete Function Call Graph

```
vde (main)
├─ vde_log_init()
├─ vde_run_command()
│  ├─ vde_find_command_script()
│  └─ vde_log_info()
└─ Execute: create-virtual-for
   ├─ vde_progress_info()
   ├─ resolve_vm_name()
   │  └─ [conditional] vde_error_alias_not_found()
   │     └─ show_known_vms()
   │        ├─ get_lang_vms()
   │        └─ get_service_vms()
   ├─ get_vm_info()
   │  └─ load_vm_types() [first call only]
   ├─ validate_vm_name()
   │  └─ vde_validate_name()
   ├─ vm_exists()
   │  ├─ vm_container_exists()
   │  └─ [conditional] vde_error_container_exists()
   ├─ find_next_available_port()
   │  └─ find_available_port()
   │     └─ _is_port_in_use()
   ├─ ensure_vm_directories()
   │  └─ vde_normalize_name()
   ├─ vde_normalize_name()
   ├─ render_template()
   │  ├─ _substitute_variables()
   │  └─ _handle_service_ports()
   ├─ vde_get_ssh_host()
   │  └─ vde_get_container_name()
   ├─ merge_ssh_config_entry()
   │  ├─ _remove_ssh_entry()
   │  └─ _append_ssh_entry()
   ├─ [Docker Compose execution]
   ├─ save_docker_state()
   │  ├─ vde_normalize_name()
   │  └─ _date_iso8601()
   ├─ vde_success()
   └─ vde_log_info()
```

---

## Library Dependency Chain

```
vde (entry point)
├─ vde-shell-compat (bootstrap - no dependencies)
├─ vde-constants (bootstrap - no dependencies)
├─ vde-errors (uses vde-constants)
├─ vde-log (uses vde-constants, vde-shell-compat)
├─ vde-core (uses vde-shell-compat, vde-constants)
├─ vm-common (uses all above + below)
│  ├─ vde-naming
│  ├─ vde-security
│  ├─ vde-path-utils
│  └─ Lazy-loads:
│     ├─ vde-ssh
│     ├─ vde-docker
│     └─ vde-templates
└─ vde-docker-state (uses vde-constants)

create-virtual-for
├─ Inherits all from vm-common
├─ vde-progress (optional UX)
└─ Triggers lazy-loads:
   ├─ vde-templates (for render_template)
   └─ vde-ssh (for merge_ssh_config_entry)
```

---

## All Files Read

1. [`scripts/lib/vde-shell-compat`](../scripts/lib/vde-shell-compat)
2. [`scripts/lib/vde-constants`](../scripts/lib/vde-constants)
3. [`scripts/lib/vde-errors`](../scripts/lib/vde-errors)
4. [`scripts/lib/vde-log`](../scripts/lib/vde-log)
5. [`scripts/lib/vde-core`](../scripts/lib/vde-core)
6. [`scripts/lib/vm-common`](../scripts/lib/vm-common)
7. [`scripts/lib/vde-docker-state`](../scripts/lib/vde-docker-state)
8. [`scripts/lib/vde-progress`](../scripts/lib/vde-progress)
9. [`scripts/lib/vde-naming`](../scripts/lib/vde-naming)
10. [`scripts/lib/vde-security`](../scripts/lib/vde-security)
11. [`scripts/lib/vde-path-utils`](../scripts/lib/vde-path-utils)
12. [`scripts/lib/vde-ssh`](../scripts/lib/vde-ssh)
13. [`scripts/lib/vde-docker`](../scripts/lib/vde-docker)
14. [`scripts/lib/vde-templates`](../scripts/lib/vde-templates)
15. [`scripts/data/vm-types.json`](../scripts/data/vm-types.json)
16. [`scripts/templates/compose-language.yml`](../scripts/templates/compose-language.yml)
17. `~/.ssh/vde/config`

---

## All Files Written

1. [`configs/docker/python/docker-compose.yml`](../configs/docker/python/docker-compose.yml)
2. [`env-files/python.env`](../env-files/python.env)
3. `~/.ssh/vde/config.vde-backup-<timestamp>`
4. `~/.ssh/vde/config` (updated)
5. [`configs/ssh/config`](../configs/ssh/config)
6. [`.docker-state/python.json`](../.docker-state/python.json)

---

## All Directories Created

1. [`configs/docker/python/`](../configs/docker/python/)
2. [`projects/python/`](../projects/python/)
3. [`logs/python/`](../logs/python/)
4. [`env-files/`](../env-files/)

---

## All External Commands Executed

1. `docker ps -a --format '{{.Names}}'` (container existence check)
2. `sockstat -l | awk '{print $3}' | grep -q "^2213$"` (port availability)
3. `docker-compose -f configs/docker/python/docker-compose.yml up -d` (VM creation)
   - Internally triggers: `docker pull`, `docker build`, `docker run`

---

## Complete Function List by Library

### vde-shell-compat (24 functions)
- `_detect_shell()`, `_shell_version()`, `_is_zsh()`, `_shell_supports_native_assoc()`
- `_get_script_path()`, `_get_script_dir()`
- `_assoc_init()`, `_assoc_set()`, `_assoc_get()`, `_assoc_keys()`, `_assoc_has_key()`, `_assoc_unset()`, `_assoc_clear()`, `_assoc_cleanup()`
- `_array_length()`, `_array_append()`, `_array_contains()`
- `_string_split()`, `_string_trim()`, `_read_array()`
- `_check_shell_compatibility()`, `_require_shell()`
- `_declare_global()`, `_date_iso8601()`, `_date_epoch()`

### vde-constants (0 functions, pure constants)
- Port ranges, timeouts, paths, error codes

### vde-errors (14 functions)
- `vde_error_set_verbose()`, `vde_error_is_verbose()`, `_vde_error_format_block()`
- `vde_error_show()`, `vde_error_simple()`, `vde_error_with_code()`
- `vde_error_docker_not_running()`, `vde_error_port_in_use()`, `vde_error_ssh_key_missing()`
- `vde_error_container_exists()`, `vde_error_permission_denied()`, `vde_error_vm_not_found()`
- `vde_error_vm_not_running()`, `vde_error_docker_build_failed()`, `vde_error_invalid_vm_name()`, `vde_error_alias_not_found()`
- `vde_success()`

### vde-log (20 functions)
- `vde_log_init()`, `vde_log_set_level()`, `vde_log_get_level()`, `vde_log_set_format()`
- `vde_log_to_file()`, `vde_log_to_stdout()`, `vde_log_to_stderr()`
- `vde_log()`, `vde_log_debug()`, `vde_log_info()`, `vde_log_warn()`, `vde_log_error()`
- `vde_log_format_json()`, `vde_log_format_syslog()`, `vde_log_format_text()`
- `vde_log_check_rotation()`, `vde_log_rotate()`, `vde_log_cleanup()`
- `vde_log_recent()`, `vde_log_grep()`, `vde_log_errors()`
- `vde_log_function()`, `vde_log_function_return()`, `vde_log_export()`

### vde-core (15 functions)
- `_vde_core_ensure_cache_dir()`, `_vde_core_get_mtime()`, `_vde_core_save_cache()`, `_vde_core_load_cache()`
- `vde_core_load_types()`, `vde_core_get_all_vms()`, `vde_core_get_vm_type()`, `vde_core_is_known_vm()`
- `vde_require_ssh()`, `vde_require_docker()`, `vde_require_template()`
- `vde_check_schema_integrity()`, `vde_validate_json_schema()`, `vde_validate_or_regenerate()`
- `vde_get_schema_for_json()`, `vde_check_schema_compatibility()`, `vde_detect_schema_changes()`
- `vde_backup_config()`, `vde_validate_and_update()`, `vde_get_config_version()`, `vde_get_schema_version()`
- `log_info()`, `log_error()`, `log_success()`, `log_warning()`
- `vde_time_start()`, `vde_time_end()`

### vm-common (45+ functions)
- `load_vm_types()`, `load_docker_config()`, `get_docker_config()`, `regenerate_vm_types_cache()`, `validate_vm_types_config()`
- `get_vm_info()`, `get_vms_by_type()`, `get_lang_vms()`, `get_service_vms()`, `get_all_vms()`
- `is_known_vm()`, `vm_is_created()`, `vm_template_exists()`, `vm_exists()`, `validate_vm_doesnt_exist()`, `validate_vm_type()`, `validate_vm_name()`
- `get_vm_type()`, `get_vm_display_name()`, `get_vm_install()`, `resolve_vm_name()`
- `get_allocated_ports()`, `find_next_available_port()`, `find_available_port()`, `allocate_port_for_vm()`, `get_or_allocate_port()`
- `get_vm_ssh_port()`, `get_port_from_registry()`, `save_port_to_registry()`, `remove_port_from_registry()`, `clear_port_registry()`
- `save_docker_state()`, `load_docker_state()`, `clear_docker_state()`, `get_docker_state_dir()`
- `ensure_vm_directories()`, `create_backup()`, `show_known_vms()`, `_is_cache_valid()`

### vde-docker-state (6 functions)
- `_get_container_name()`, `vm_container_exists()`, `vm_container_status()`
- `vm_is_container_running()`, `vm_is_container_stopped()`
- `list_running_containers()`, `list_all_containers()`

### vde-naming (functions used)
- `vde_normalize_name()`, `vde_validate_name()`, `vde_get_ssh_host()`, `vde_get_container_name()`

### vde-ssh (functions used)
- `merge_ssh_config_entry()`, `_remove_ssh_entry()`, `_append_ssh_entry()`

### vde-templates (functions used)
- `render_template()`, `_substitute_variables()`, `_handle_service_ports()`

### vde-progress (functions used)
- `vde_progress_info()`

---

## Execution Time Estimates

**Typical execution time for `vde create python`**: 30-90 seconds

**Phase breakdown**:
- Initialization & validation: <1 second
- Port allocation: <1 second
- File generation: <1 second
- SSH config update: <1 second
- Docker operations: 25-85 seconds
  - Image pull: 10-60 seconds (network dependent)
  - Container build: 10-20 seconds (Python installation)
  - Container startup: 5 seconds
- State persistence: <1 second

---

## Verification

To verify this function map, execute with tracing:

```bash
# Enable function tracing
export VDE_LOG_LEVEL="DEBUG"
export VDE_ERRORS_VERBOSE=1

# Run with zsh tracing
zsh -x scripts/vde create python 2>&1 | tee vde-trace.log

# Analyze function calls
grep -E '^\+' vde-trace.log | grep -E '\(\)' | awk '{print $2}' | sort | uniq
```

Expected output: All functions listed in this document should appear in the trace.
