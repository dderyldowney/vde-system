# VDE Test Coverage Analysis

**Generated:** 2026-02-24
**Test Run Summary:** 195 scenarios passed, 42 failed, 42 error, 210 skipped

---

## 1. Library Function Unit Testing Coverage

### Coverage Summary

| Library | Functions | Test File | Test Functions | Coverage |
|---------|-----------|-----------|----------------|----------|
| vde-audit | 18 | vde-audit.test.zsh | 6 | Partial |
| vde-commands | 22 | **MISSING** | - | ❌ None |
| vde-constants | 0* | vde-constants.test.zsh | 27 | ✅ Full |
| vde-core | 30 | vde-core.test.zsh | 49 | ✅ Full |
| vde-docker | 21 | vde-docker.test.zsh | 7 | Partial |
| vde-docker-state | 7 | vde-docker-state.test.zsh | 7 | ✅ Full |
| vde-errors | 21 | vde-errors.test.zsh | 7 | Partial |
| vde-health | 6 | vde-health.test.zsh | 7 | ✅ Full |
| vde-log | 25 | vde-log.test.zsh | 8 | Partial |
| vde-metrics | 19 | vde-metrics.test.zsh | 6 | Partial |
| vde-naming | 8 | vde-naming.test.zsh | 21 | ✅ Full |
| vde-parser | 18 | vde-parser.test.zsh | 9 | Partial |
| vde-path-utils | 7 | vde-path-utils.test.zsh | 39 | ✅ Full |
| vde-progress | 20 | vde-progress.test.zsh | 7 | Partial |
| vde-security | 5 | vde-security.test.zsh | 23 | ✅ Full |
| vde-shell-compat | 31 | vde-shell-compat.test.zsh | 21 | Partial |
| vde-ssh | 24 | vde-ssh.test.zsh | 19 | Partial |
| vde-templates | 7 | vde-templates.test.zsh | 9 | ✅ Full |
| vm-common | 44 | vm-common.test.zsh | 5 | ❌ Minimal |

*Note: vde-constants defines constants, not functions.

### 1.1 Library Responsibilities

| Library | Purpose | Key Functions |
|---------|---------|---------------|
| **vde-audit** | Audit logging for security and compliance | `vde_audit_log()`, `vde_audit_create_vm()`, `vde_audit_query()` |
| **vde-commands** | High-level command wrappers for all VDE operations | `vde_list_vms()`, `vde_create_vm()`, `vde_start_vm()`, `vde_stop_vm()` |
| **vde-constants** | Centralized constants, magic numbers, configuration values | `VDE_SUCCESS`, `VDE_ERR_*`, port ranges, directory paths |
| **vde-core** | Essential functions: logging, constants, VM type loading | `log_info()`, `log_error()`, `vde_core_load_types()`, `invalidate_vm_types_cache()` |
| **vde-docker** | Docker container lifecycle management | `start_vm()`, `stop_vm()`, `get_vm_ssh_port()`, `allocate_ssh_port()` |
| **vde-docker-state** | Real-time Docker container state queries | `vm_container_exists()`, `vm_is_container_running()`, `list_running_containers()` |
| **vde-errors** | Contextual error messages with remediation steps | `vde_error_show()`, `vde_error_docker_not_running()`, `vde_error_port_in_use()` |
| **vde-health** | Container health checks (SSH, ports, language tools) | `vde_check_container_running()`, `vde_check_ssh_port()`, `vde_health_check()` |
| **vde-log** | Structured logging (JSON/text) with rotation | `vde_log()`, `vde_log_info()`, `vde_log_error()`, `vde_log_rotate()` |
| **vde-metrics** | Performance metrics, latency tracking, error rates | `vde_metrics_record()`, `vde_metrics_timing_start()`, `vde_metrics_get_cache_hit_rate()` |
| **vde-naming** | VM naming conventions and validation | `vde_validate_name()`, `vde_normalize_name()`, `vde_get_container_name()` |
| **vde-parser** | Natural language parsing for VDE commands | `detect_intent()`, `extract_vm_names()`, `generate_plan()`, `execute_plan()` |
| **vde-path-utils** | Path conversion for cross-platform portability | `vde_path_to_home_rel()`, `vde_path_normalize()`, `vde_make_portable()` |
| **vde-progress** | Progress bars, spinners, timing feedback | `vde_progress_spinner_start()`, `vde_progress_bar_update()` |
| **vde-security** | Isolation enforcement, permissions, network segmentation | `vde_security_enforce_permissions()`, `vde_security_ensure_network()` |
| **vde-shell-compat** | Zsh-native abstractions for shell features | `_assoc_set()`, `_assoc_get()`, `_detect_shell()`, `_get_script_dir()` |
| **vde-ssh** | SSH key management and configuration | `detect_ssh_keys()`, `setup_ssh_for_vm()`, `add_ssh_config_entry()`, `ensure_ssh_agent()` |
| **vde-templates** | Template rendering and VM creation | `render_template()`, `create_vm_from_template()`, `list_templates()` |
| **vm-common** | Core VM management: type loading, port management | `get_all_vms()`, `resolve_vm_name()`, `get_vm_info()`, `get_vm_type()` |

### Missing Test Files
- **vde-commands** - 22 functions with NO unit test file

### Low Coverage Libraries
- **vm-common** - 44 functions, only 5 test functions (core library with minimal testing)
- **vde-parser** - 18 functions, only 9 test functions (critical for natural language commands)
- **vde-ssh** - 24 functions, 19 test functions (partial coverage)

---

## 2. Script-to-Function Call Chains

### Primary Scripts and Their Library Dependencies

#### `scripts/vde` (Main Entry Point)
Sources libraries in order:
1. `vde-shell-compat` - Shell compatibility layer
2. `vde-constants` - Constants and configuration
3. `vde-errors` - Error handling
4. `vde-log` - Logging infrastructure
5. `vde-core` - Core functionality
6. `vm-common` - VM common functions
7. `vde-docker-state` - Docker state management

#### `scripts/start-virtual`
Sources:
- `vm-common` → `get_all_vms()`, `resolve_vm_name()`, `get_vm_info()`
- `vde-docker-state` → `vm_container_exists()`, `vm_is_container_running()`
- `vde-ssh` → `setup_ssh_for_vm()`, `ensure_ssh_agent()`

#### `scripts/remove-virtual`
Sources:
- `vm-common` → `get_vm_info()`, `log_info()`, `log_error()`

#### `scripts/delete-virtual`
Sources:
- `vm-common` → Core VM operations
- `vde-naming` → `vde_get_container_name()`, `vde_normalize_name()`
- `vde-ssh` → `remove_ssh_config_entry()`, `remove_known_hosts_entry()`
- `vde-docker` → `get_compose_file()`, Docker operations

### Function Call Chain Example: `vde start python`

```
vde (script)
  └─→ sources vde-core, vm-common, vde-docker-state
  └─→ dispatches to start-virtual
       └─→ sources vm-common, vde-docker-state, vde-ssh
       └─→ resolve_vm_name() [vm-common]
       └─→ vm_container_exists() [vde-docker-state]
           └─→ docker ps -a (direct Docker CLI)
       └─→ start_vm() [vm-common]
           └─→ docker-compose up -d (direct Docker CLI)
       └─→ setup_ssh_for_vm() [vde-ssh]
           └─→ add_ssh_config_entry()
```

---

## 3. Docker-to-Host Interconnect Break Points

### Critical Integration Points

#### Where Docker Calls Break (Library → Docker CLI)

| Library | Function | Docker Command | Failure Mode |
|---------|----------|----------------|--------------|
| vde-docker-state | `vm_container_exists()` | `docker ps -a` | Silent failure returns false |
| vde-docker-state | `vm_is_container_running()` | `docker ps` | Silent failure returns false |
| vde-docker | `container_exists()` | `docker ps -a` | Returns false on error |
| vde-docker | `is_vm_running()` | `docker ps` | Returns false on error |
| vde-docker | `get_container_id()` | `docker ps` | Returns empty string |
| vde-docker | `get_container_ip()` | `docker inspect` | Returns empty string |
| vde-health | `vde_check_container_running()` | `docker ps` | Returns false on error |
| vde-security | `vde_security_ensure_network()` | `docker network` | Graceful handling |

### Test Infrastructure Break Points

#### Python Test Helpers (tests/features/steps/vm_common.py)

```python
# Key integration functions:
run_vde_command()     # Line 538 - Bridges Python tests to Zsh scripts
container_exists()    # Line 94 - Uses vde-ps to check containers
container_is_running() # Line 107 - Uses vde-ps to check status
wait_for_container()  # Line 176 - Polls vde-ps for readiness
```

#### Known Failure Scenarios

1. **SSH Agent Forwarding Tests** (42 error scenarios)
   - Break point: VM-to-host SSH communication
   - Files: `ssh-agent-*.feature` files
   - Root cause: SSH agent socket not properly forwarded into containers

2. **Natural Language Parser Tests** (42 failed scenarios)
   - Break point: Parser intent detection
   - Files: `parser.feature`, `natural-language-commands.feature`
   - Root cause: `detect_intent()` not handling all variations

3. **Daily Workflow Tests** (multiple failures)
   - Break point: Multi-VM orchestration
   - Files: `daily-workflow.feature`, `daily-development-workflow.feature`
   - Root cause: State management between operations

---

## 4. Test Suite Architecture

### Test Types

| Type | Location | Count | Purpose |
|------|----------|-------|---------|
| Unit Tests | `tests/unit/*.test.zsh` | 23 files | Library function testing |
| BDD Features | `tests/features/*.feature` | 20 files | Integration testing |
| Step Definitions | `tests/features/steps/*.py` | 25+ files | Test implementation |

### Test Execution Flow

```
Behave (Python)
  └─→ Feature files (*.feature)
  └─→ Step definitions (*.py)
       └─→ vm_common.py helpers
            └─→ run_vde_command()
                 └─→ subprocess.run(["zsh", "scripts/vde", ...])
                      └─→ Zsh scripts
                           └─→ Library functions (scripts/lib/*)
                                └─→ Docker CLI commands
```

---

## 5. Recommendations

### High Priority

1. **Create `vde-commands.test.zsh`** - 22 functions with zero unit test coverage
2. **Expand `vm-common.test.zsh`** - Core library with only 5 tests for 44 functions
3. **Fix SSH agent forwarding** - 42 error scenarios blocked by this issue

### Medium Priority

1. Expand parser tests for edge cases
2. Add integration tests for Docker-to-host communication
3. Mock Docker CLI for unit tests to enable Docker-free testing

### Low Priority

1. Add performance benchmarks
2. Add stress tests for concurrent operations
3. Add security-focused tests for SSH key handling
