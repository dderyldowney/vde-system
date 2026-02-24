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
