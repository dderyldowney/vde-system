# Plan 29: Docker-Required Test Remediation - Remaining Steps

## Summary
Continuation of Plan 20/21 efforts to implement BDD step definitions for docker-required tests. Current progress: 660 passing steps, ~600 undefined remaining.

## Architecture Reference

### Modular Library Structure

VDE uses a modular library architecture that separates concerns and enables code reuse:

| Library | Purpose | Dependencies |
|---------|---------|--------------|
| [`@scripts/lib/vde-constants`](scripts/lib/vde-constants) | Centralized constants (return codes, port ranges, timeouts) | None |
| [`@scripts/lib/vde-shell-compat`](scripts/lib/vde-shell-compat) | Portable shell operations (zsh/bash compatibility) | None |
| [`@scripts/lib/vde-errors`](scripts/lib/vde-errors) | Error messages with remediation steps | vde-constants |
| [`@scripts/lib/vde-log`](scripts/lib/vde-log) | Structured logging with rotation | vde-constants, vde-shell-compat |
| [`@scripts/lib/vde-core`](scripts/lib/vde-core) | Essential VDE functions (VM types, queries, caching) | vde-constants, vde-shell-compat |
| [`@scripts/lib/vm-common`](scripts/lib/vm-common) | Full VDE functionality (VM types, ports, Docker, SSH, templates) | vde-constants, vde-shell-compat |
| [`@scripts/lib/vde-commands`](scripts/lib/vde-commands) | Safe wrapper functions for VDE operations | vm-common |
| [`@scripts/lib/vde-parser`](scripts/lib/vde-parser) | Pattern-based natural language parser | vm-common, vde-commands |

### Virtual Machines

#### Language VMs (18 total, ports 2200-2299)

| Name | Aliases | Container Name | SSH Port |
|------|---------|----------------|----------|
| c | c | c-dev | 2200 |
| cpp | c++, gcc | cpp-dev | 2201 |
| asm | assembler, nasm | asm-dev | 2202 |
| python | python3 | python-dev | 2203 |
| rust | rust | rust-dev | 2204 |
| js | node, nodejs | js-dev | 2205 |
| csharp | dotnet | csharp-dev | 2206 |
| ruby | ruby | ruby-dev | 2207 |
| go | golang | go-dev | 2208 |
| java | jdk | java-dev | 2209 |
| kotlin | kotlin | kotlin-dev | 2210 |
| swift | swift | swift-dev | 2211 |
| php | php | php-dev | 2212 |
| scala | scala | scala-dev | 2213 |
| r | rlang, r | r-dev | 2214 |
| lua | lua | lua-dev | 2215 |
| flutter | dart, flutter | flutter-dev | 2216 |
| elixir | elixir | elixir-dev | 2217 |
| haskell | ghc, haskell | haskell-dev | 2218 |

#### Service VMs (7 total, ports 2400-2499)

| Name | Aliases | Container Name | SSH Port | Service Port |
|------|---------|----------------|----------|--------------|
| postgres | postgresql | postgres | 2400 | 5432 |
| redis | redis | redis | 2401 | 6379 |
| mongodb | mongo | mongodb | 2402 | 27017 |
| nginx | nginx | nginx | 2403 | 80, 443 |
| couchdb | couchdb | couchdb | 2404 | 5984 |
| mysql | mysql | mysql | 2405 | 3306 |
| rabbitmq | rabbitmq | rabbitmq | 2406 | 5672, 15672 |

### Command Parser Architecture

The parser recognizes 9 distinct intents:

| Intent | Purpose | Example Commands |
|--------|---------|------------------|
| `list_vms` | List available VMs | "what VMs can I create?", "show languages" |
| `create_vm` | Create new VMs | "create a Go VM", "make Python and PostgreSQL" |
| `start_vm` | Start VMs | "start Go", "launch everything" |
| `stop_vm` | Stop VMs | "stop Go", "shutdown everything" |
| `restart_vm` | Restart VMs | "restart Python", "rebuild and start Go" |
| `status` | Show running status | "what's running?", "show status" |
| `connect` | Get SSH connection info | "how do I connect to Python?", "SSH into Go" |
| `add_vm_type` | Add new VM types | "add a new language called Zig" |
| `help` | Show help | "help", "what can I do?" |

### Data Flow

```
User Command
    │
    ▼
Parse Intent ────────┐
    │                 │
    ▼                 ▼
Extract Entities   Generate Plan
    │                 │
    ▼                 ▼
Validate VMs ───────> Structured Plan
    │                 │
    ▼                 ▼
Route to Handler ────> Execute Plan
    │                 │
    ▼                 ▼
Call VDE Scripts ────> Result
    │
    ▼
Return to User
```

## Helper Functions

All step definitions should use helper functions from `vm_common.py`:

```python
from tests.features.steps.vm_common import run_vde_command

# Example usage
result = run_vde_command(context, "create python test-python")
```

### Key vm-common Functions for Testing

| Function | Purpose |
|----------|---------|
| `get_vm_info()` | Query VM type data (type, aliases, display, install, port) |
| `resolve_vm_name()` | Handle aliases (e.g., "nodejs" → "js") |
| `find_next_available_port()` | Auto-allocate ports (with registry for fast lookup) |
| `render_template()` | Generate configs from templates |
| `start_vm()` | Start a VM via docker-compose |
| `stop_vm()` | Stop a VM via docker-compose |
| `vm_exists()` | Check if VM config exists |
| `ensure_ssh_agent()` | Start SSH agent, load keys |
| `get_all_vms()` | List all VM names |
| `load_vm_types()` | Load VM types from config or cache |

## Current Status

| Metric | Count |
|--------|-------|
| Passing Steps | 660 |
| Scenarios Passing | 51 |
| Remaining Steps | ~600 |

## Files Modified

| File | Purpose | Status |
|------|---------|--------|
| [`@tests/features/steps/vde_command_steps.py`](tests/features/steps/vde_command_steps.py) | Natural language command patterns | Implemented |
| [`@tests/features/steps/config_and_verification_steps.py`](tests/features/steps/config_and_verification_steps.py) | Configuration patterns | Implemented |
| [`@tests/features/steps/vm_project_steps.py`](tests/features/steps/vm_project_steps.py) | VM Project patterns | Implemented |
| [`@tests/features/steps/debugging_and_port_steps.py`](tests/features/steps/debugging_and_port_steps.py) | Debug patterns | Implemented |
| [`@tests/features/steps/network_and_resource_steps.py`](tests/features/steps/network_and_resource_steps.py) | Network patterns | Implemented |
| [`@tests/features/steps/crash_recovery_steps.py`](tests/features/steps/crash_recovery_steps.py) | Crash recovery patterns | Partial |
| [`@tests/features/steps/file_verification_steps.py`](tests/features/steps/file_verification_steps.py) | File verification patterns | Implemented |
| [`@tests/features/steps/ssh_config_steps.py`](tests/features/steps/ssh_config_steps.py) | SSH config patterns | Implemented |
| [`@tests/features/steps/ssh_agent_steps.py`](tests/features/steps/ssh_agent_steps.py) | SSH agent patterns | Implemented |

## Detailed Breakdown of Remaining Steps by Category

### Category 1: VM Lifecycle Management (~120 steps remaining)
**Feature:** [`@tests/features/docker-required/vm-lifecycle.feature`](tests/features/docker-required/vm-lifecycle.feature)

| Scenario | Status | Missing Steps |
|----------|--------|---------------|
| Create a new language VM (c, cpp, asm, python, rust, js, csharp, ruby, go, java, kotlin, swift, php, scala, r, lua, flutter, elixir, haskell) | Partial | GIVEN step definitions for VM type checking |
| Create a new service VM with custom port (postgres, redis, mongodb, nginx, couchdb, mysql, rabbitmq) | Missing | All steps need implementation |
| Start a created VM | Partial | Port verification steps |
| Start multiple VMs | Missing | Multi-VM start verification |
| Start all VMs | Missing | Batch start verification |
| Stop a running VM | Partial | Container state verification |
| Stop all running VMs | Missing | All steps need implementation |
| Restart a VM | Partial | Container ID verification |
| Rebuild a VM with --rebuild flag | Missing | All steps need implementation |
| Cannot start non-existent VM | Partial | Error message verification |
| Cannot create duplicate VM | Missing | All steps need implementation |

**Priority:** P1 - Core functionality, must pass for user trust

### Category 2: Docker Operations (~100 steps remaining)
**Feature:** [`@tests/features/docker-required/docker-operations.feature`](tests/features/docker-required/docker-operations.feature)

| Scenario | Status | Missing Steps |
|----------|--------|---------------|
| Build Docker image for VM | Partial | Build verification steps |
| Start container with docker-compose up | Partial | Container state verification |
| Stop container with docker-compose down | Missing | All steps need implementation |
| Restart container | Missing | Container ID comparison |
| Rebuild with --build flag | Missing | All steps need implementation |
| Rebuild without cache with --no-cache flag | Missing | All steps need implementation |
| Parse Docker error messages | Missing | Error parsing steps |
| Retry transient failures with exponential backoff | Missing | Retry logic verification |
| Get container status | Partial | Status parsing |
| Detect running containers | Missing | Multi-container detection |
| Use correct docker-compose project name (vde-{name}) | Missing | Project name verification |
| Container naming follows convention (language: {name}-dev, service: {name}) | Missing | Naming verification |
| Volume mounts are created correctly (projects/, logs/, .ssh/) | Missing | Mount verification |
| Environment variables are passed to container (SSH_PORT, etc.) | Missing | ENV verification |

**Priority:** P1 - Core functionality, affects all VMs

### Category 3: SSH Configuration (~100 steps remaining)
**Feature:** [`@tests/features/docker-required/ssh-configuration.feature`](tests/features/docker-required/ssh-configuration.feature)

| Scenario | Status | Missing Steps |
|----------|--------|---------------|
| Automatically start SSH agent if not running | Partial | Agent start verification |
| Generate SSH key if none exists (ed25519 preferred) | Partial | Key generation verification |
| Sync public keys to VDE directory (public-ssh-keys/) | Partial | Sync verification |
| Validate public key files only | Partial | Validation steps |
| Create SSH config entry for new VM (Host {name}-dev, Port {port}) | Partial | Config generation verification |
| SSH config uses correct identity file (~/.ssh/vde/id_ed25519) | Missing | Identity file verification |
| Generate VM-to-VM SSH config entries | Missing | Multi-VM config |
| Prevent duplicate SSH config entries | Missing | Duplicate prevention |
| Atomic SSH config update prevents corruption | Missing | Atomicity verification |
| Backup SSH config before modification (backup/ssh/) | Missing | Backup verification |
| Remove SSH config entry when VM is removed | Missing | Cleanup verification |
| VM-to-VM communication uses agent forwarding | Missing | Forwarding verification |

**Priority:** P1 - Critical for SSH functionality

### Category 4: Natural Language Commands (~80 steps remaining)
**Feature:** [`@tests/features/docker-required/natural-language-commands.feature`](tests/features/docker-required/natural-language-commands.feature)

| Scenario | Status | Missing Steps |
|----------|--------|---------------|
| Simple intent commands (list_vms, create_vm, start_vm, stop_vm, restart_vm, status, connect, add_vm_type, help) | Partial | Intent recognition verification |
| Natural language variations | Missing | Variation handling |
| Multiple VMs in one command | Missing | Multi-VM parsing |
| Using aliases instead of canonical names (nodejs → js) | Missing | Alias resolution |
| Descriptive status queries | Missing | Status query handling |
| Asking for help naturally | Missing | Help generation |
| Connection help requests | Missing | Connection instructions |
| Rebuild requests (--rebuild flag) | Missing | Rebuild parsing |
| Wildcard operations | Missing | Wildcard handling |
| Stopping everything | Missing | Stop all parsing |
| Complex natural language queries | Missing | Complex query parsing |
| Troubleshooting language | Missing | Troubleshooting parsing |

**Priority:** P2 - Parser functionality, nice to have

### Category 5: Port Management (~80 steps remaining)
**Feature:** [`@tests/features/docker-required/port-management.feature`](tests/features/docker-required/port-management.feature)

| Scenario | Status | Missing Steps |
|----------|--------|---------------|
| Allocate first available port for language VM (2200-2299) | Partial | Port allocation verification |
| Allocate sequential ports for multiple language VMs | Missing | Sequential allocation |
| Allocate first available port for service VM (2400-2499) | Missing | Service port allocation |
| Skip allocated ports when finding next available | Missing | Gap handling |
| Port registry tracks all allocated ports (.cache/port-registry) | Missing | Registry verification |
| Port registry persists across script invocations | Missing | Persistence verification |
| Detect host port collision during allocation | Missing | Collision detection |
| Detect Docker port collision during allocation | Missing | Docker collision |
| Atomic port reservation prevents race conditions | Missing | Atomicity verification |
| Port ranges are respected | Missing | Range verification |
| Error when all ports in range are allocated ("No available ports") | Missing | Error handling |
| Clean up stale port locks | Missing | Lock cleanup |
| Port registry updates when VM is removed | Missing | Registry cleanup |

**Priority:** P1 - Critical for multi-VM support

### Category 6: Error Handling and Recovery (~60 steps remaining)
**Feature:** [`@tests/features/docker-required/error-handling-and-recovery.feature`](tests/features/docker-required/error-handling-and-recovery.feature)

| Scenario | Status | Missing Steps |
|----------|--------|---------------|
| Invalid VM name handling | Partial | Error message verification |
| Port conflict resolution | Missing | Conflict resolution |
| Docker daemon not running | Missing | Docker check steps |
| Insufficient disk space | Missing | Disk space check |
| Network creation failure (vde-network) | Missing | Network error handling |
| Build failure recovery | Partial | Error explanation verification |
| Container startup timeout | Missing | Timeout handling |
| SSH connection failure | Missing | SSH error handling |
| Permission denied errors | Missing | Permission handling |
| Configuration file errors (docker-compose.yml malformed) | Missing | Config error parsing |
| Graceful degradation | Missing | Degradation handling |

**Priority:** P2 - Important for reliability

### Category 7: Template System (~50 steps remaining)
**Feature:** [`@tests/features/docker-required/template-system.feature`](tests/features/docker-required/template-system.feature)

| Scenario | Status | Missing Steps |
|----------|--------|---------------|
| Render language VM template (compose-language.yml) | Partial | Template rendering verification |
| Render service VM template (compose-service.yml) | Missing | Service template rendering |
| Handle multiple service ports (nginx: 80, 443; rabbitmq: 5672, 15672) | Missing | Multi-port handling |
| Escape special characters in template values | Missing | Character escaping |
| Template includes SSH agent forwarding (SSH_AUTH_SOCK mount) | Missing | Agent forwarding verification |
| Template includes public keys volume (public-ssh-keys/) | Missing | Volume verification |
| Template uses correct network (vde-network) | Missing | Network verification |
| Template sets correct restart policy (restart: unless-stopped) | Missing | Restart policy verification |
| Template configures user correctly (devuser, UID/GID 1000) | Missing | User configuration |
| Template exposes SSH port (22 → host port) | Missing | Port exposure |
| Template includes install command | Missing | Install command |
| Handle missing template gracefully | Missing | Error handling |

**Priority:** P2 - Template generation is core functionality

### Category 8: SSH Agent VM-to-VM Forwarding (~50 steps remaining)
**Feature:** [`@tests/features/docker-required/ssh-agent-forwarding-vm-to-vm.feature`](tests/features/docker-required/ssh-agent-forwarding-vm-to-vm.feature)

| Scenario | Status | Missing Steps |
|----------|--------|---------------|
| Automatically setting up SSH environment when creating a VM (ensure_ssh_environment) | Partial | Auto-setup verification |
| Communicating between language VMs (VM1 → Host Agent → VM2) | Missing | VM-to-VM SSH |
| Communicating between language and service VMs | Missing | Language-service SSH |
| Copying files between VMs using SCP | Missing | SCP verification |
| Running commands on remote VMs (ssh {name} {command}) | Missing | Remote execution |
| Full stack development workflow (Python + PostgreSQL + Redis) | Missing | Full stack verification |
| Microservices architecture communication (Go + Python + Rust) | Missing | Microservices verification |

**Priority:** P2 - Advanced feature, affects team workflows

### Category 9: Debugging and Troubleshooting (~40 steps remaining)
**Feature:** [`@tests/features/docker-required/debugging-troubleshooting.feature`](tests/features/docker-required/debugging-troubleshooting.feature)

| Scenario | Status | Missing Steps |
|----------|--------|---------------|
| Diagnose why VM won't start | Partial | Diagnosis steps |
| View VM logs for debugging (docker logs) | Partial | Log viewing |
| Access VM shell for debugging (docker exec -it) | Missing | Shell access |
| Rebuild VM from scratch after corruption | Missing | Rebuild verification |
| Check if port is already in use | Missing | Port check |
| Verify SSH connection is working | Missing | SSH verification |
| Test database connectivity from VM | Missing | Database connectivity |
| Inspect docker-compose configuration | Partial | Configuration inspection |
| Verify volumes are mounted correctly | Missing | Volume verification |
| Clear Docker cache to fix build issues (--no-cache) | Missing | Cache clearing |

**Priority:** P2 - Important for troubleshooting

### Category 10: Team Collaboration and Maintenance (~40 steps remaining)
**Feature:** [`@tests/features/docker-required/team-collaboration-and-maintenance.feature`](tests/features/docker-required/team-collaboration-and-maintenance.feature)

| Scenario | Status | Missing Steps |
|----------|--------|---------------|
| Rebuilding after system updates | Partial | Rebuild verification |
| Troubleshooting a problematic VM | Missing | Troubleshooting steps |
| Checking system status | Partial | Status checking |
| Adding a new language to the team (add_vm_type intent) | Missing | Language addition |
| Sharing SSH configurations | Missing | Config sharing |
| Batch operations for efficiency | Missing | Batch operations |
| Stopping only development VMs | Missing | Selective stopping |
| Performing system maintenance | Missing | Maintenance steps |
| Recovering from errors | Missing | Recovery steps |
| Monitoring resource usage | Missing | Resource monitoring |

**Priority:** P3 - Team features, lower priority

## Priority Ordering

### P1 - Must Complete (Critical Path)
1. VM Lifecycle Management (120 steps) - create_vm, start_vm, stop_vm, restart_vm intents
2. Docker Operations (100 steps) - container lifecycle verification
3. SSH Configuration (100 steps) - SSH config and agent forwarding
4. Port Management (80 steps) - port allocation (2200-2299, 2400-2499)

### P2 - Should Complete (Important)
5. Error Handling and Recovery (60 steps) - error messages and remediation
6. Template System (50 steps) - template rendering for docker-compose
7. SSH Agent VM-to-VM Forwarding (50 steps) - VM-to-VM communication
8. Debugging and Troubleshooting (40 steps) - diagnostic capabilities

### P3 - Nice to Have
9. Natural Language Commands (80 steps) - parser coverage (can fallback)
10. Team Collaboration and Maintenance (40 steps) - team features

## Implementation Strategy

### Phase 1: Core VM Operations (P1 items)
1. Complete `vm_operations_steps.py` for all lifecycle operations
2. Implement `docker_operations_steps.py` for container management
3. Finish `ssh_config_steps.py` for SSH configuration
4. Implement `port_management_steps.py` for port allocation

### Phase 2: Error Handling and Templates (P2 items)
5. Complete `error_handling_steps.py` for error scenarios
6. Implement `template_steps.py` for template rendering
7. Finish `ssh_vm_steps.py` for VM-to-VM SSH
8. Complete `debugging_steps.py` for troubleshooting

### Phase 3: Advanced Features (P3 items)
9. Implement `natural_language_steps.py` for parser coverage
10. Complete `team_collaboration_steps.py` for team features

## Testing Requirements

All step definitions must:
1. Use `run_vde_command()` for real VDE execution
2. Use `docker ps` for container verification
3. Use `ssh-add -l` for SSH key verification
4. Use real file system checks for configuration verification
5. Avoid `assert True` patterns (fake tests prohibited)

## Next Steps

1. [ ] Complete P1 category implementations first
2. [ ] Verify each category with actual test runs
3. [ ] Address P2 categories once P1 is stable
4. [ ] Add P3 features as time permits
