# BDD Step Definitions Directory

This directory contains all BDD (Behavior-Driven Development) step definitions for the VDE test suite. Each step definition file implements the `@given`, `@when`, and `@then` decorators from the Behave framework.

## Directory Structure

After the January 2026 refactoring, step definitions are organized by topic:

### Core Infrastructure

| File | Purpose | Steps |
|------|---------|-------|
| `config.py` | Test configuration (VDE_ROOT, paths) | - |
| `vm_common.py` | Shared helper functions for VM operations | 30+ helpers |
| `ssh_helpers.py` | SSH-specific helper functions | - |

### VM Lifecycle Steps

| File | Purpose | Steps |
|------|---------|-------|
| `vm_creation_steps.py` | VM creation and setup | ~70 steps |
| `vm_status_steps.py` | VM status and health checks | ~90 steps |
| `vm_operations_steps.py` | Basic VM operations (start/stop/restart) | ~15 steps |
| `project_workflow_steps.py` | Project-based workflows | ~50 steps |

### Docker Operations Steps

| File | Purpose | Steps |
|------|---------|-------|
| `vm_docker_steps.py` | Core Docker operations (redirect to split files) | - |
| `vm_docker_build_steps.py` | Docker build and rebuild operations | ~25 steps |
| `vm_docker_network_steps.py` | Docker networking and port management | ~30 steps |
| `vm_docker_service_steps.py` | Docker service VM operations | ~35 steps |

### Installation Steps

| File | Purpose | Steps |
|------|---------|-------|
| `installation_steps.py` | Installation GIVEN/WHEN setup | ~35 steps |
| `post_install_verification_steps.py` | Post-install THEN verification | ~70 steps |
| `uninstallation_steps.py` | Uninstallation and cleanup | ~15 steps |

### SSH Configuration Steps

| File | Purpose | Steps |
|------|---------|-------|
| `ssh_config_verification_steps.py` | SSH config checks | ~20 steps |
| `vm_state_verification_steps.py` | VM state verification | ~20 steps |
| `ssh_connection_steps.py` | SSH connection testing | ~40 steps |
| `user_workflow_steps.py` | User environment and workflows | ~30 steps |

### Team Collaboration

| File | Purpose | Steps |
|------|---------|-------|
| `team_collaboration_steps.py` | Team onboarding and consistency | ~33 steps |

### Feature-Specific Steps

| File | Purpose | Steps |
|------|---------|-------|
| `port_management_steps.py` | Port allocation and collision detection | ~40 steps |
| `cache_steps.py` | Cache invalidation and persistence | ~35 steps |
| `parser_steps.py` | Natural language command parser | ~50 steps |
| `template_steps.py` | Template rendering system | ~25 steps |
| `config_steps.py` | VM configuration management | ~45 steps |
| `ssh_agent_steps.py` | SSH agent management | ~15 steps |
| `daily_workflow_steps.py` | Daily development workflows | ~80 steps |

## Shared Helpers

### vm_common.py

Core utilities for all step definitions:

```python
# Docker operations
docker_ps()                          # List running containers
container_exists(vm_name)             # Check if VM container exists
get_container_health(vm_name)         # Get container health status
wait_for_container(vm_name, timeout)  # Wait for container to be ready

# VDE command execution
run_vde_command(args, timeout)        # Run vde CLI command

# VM configuration
compose_file_exists(vm_name)          # Check docker-compose.yml exists
get_vm_type(vm_name)                  # Get VM type (lang/svc)
get_vm_types()                        # List all VM types

# System checks
check_docker_available()              # Check Docker is installed
check_docker_compose_available()      # Check docker-compose is available
check_docker_network_exists(name)     # Check Docker network exists
check_zsh_available()                 # Check zsh is installed
check_ssh_keys_exist()                # Check SSH keys exist
check_scripts_executable()            # Check scripts are executable
check_vde_script_exists(script)       # Check VDE script exists
check_directory_exists(dir)           # Check directory exists
check_file_in_vde(file)               # Check file exists in VDE

# VM state management
wait_for_container_stopped(vm_name)   # Wait for container to stop
ensure_vm_created(context, vm_name)   # Ensure VM is created
ensure_vm_running(context, vm_name)   # Ensure VM is running
ensure_vm_stopped(context, vm_name)   # Ensure VM is stopped
```

### config.py

Test configuration:

```python
VDE_ROOT = Path.home() / "dev"        # VDE installation directory
```

## Step Definition Pattern

All step definitions follow this pattern:

```python
"""
BDD Step Definitions for <feature>.

These steps verify <feature description>.
"""
from pathlib import Path
from behave import given, when, then

from config import VDE_ROOT
from vm_common import docker_ps, container_exists

@given('precondition text')
def step_precondition(context):
    """Verify precondition - real system check."""
    # Use real verification, not context flags
    context.precondition_met = actual_verification()

@when('action text')
def step_action(context):
    """Execute action and capture results."""
    result = run_vde_command(['command', 'args'])
    context.last_exit_code = result.returncode

@then('expected outcome')
def step_expected_outcome(context):
    """Verify expected outcome - real system check."""
    running = docker_ps()
    assert len(running) > 0, "At least one VM should be running"
```

## Anti-Patterns to Avoid

### Fake Testing Prohibited

```python
# ❌ WRONG - Fake testing
@then('the VM should be running')
def step_vm_running_fake(context):
    assert True, "VM is running"  # Always passes!

# ✅ CORRECT - Real verification
@then('the VM should be running')
def step_vm_running_real(context):
    running = docker_ps()
    assert len(running) > 0, f"No VMs running: {running}"
```

```python
# ❌ WRONG - Context flag without verification
@then('I should be logged in as devuser')
def step_logged_in_fake(context):
    context.user_is_devuser = True  # Assumes, doesn't verify

# ✅ CORRECT - Real verification
@then('I should be logged in as devuser')
def step_logged_in_real(context):
    running = docker_ps()
    if running:
        vm = list(running)[0]
        result = subprocess.run(
            ['docker', 'exec', vm, 'whoami'],
            capture_output=True, text=True, timeout=10
        )
        context.user_is_devuser = result.stdout.strip() == 'devuser'
```

## Adding New Step Definitions

1. **Identify the feature area** - Choose the appropriate file or create a new one
2. **Use real verification** - Always check actual system state
3. **Follow naming conventions** - `step_<description>` for function names
4. **Document the step** - Include docstring explaining what it verifies
5. **Import from vm_common** - Use shared helpers instead of duplicating code

## Testing Your Steps

```bash
# Run specific feature file
behave tests/features/your-feature.feature

# Run with debug output
behave -Dlogging-level=DEBUG tests/features/your-feature.feature

# Run only scenarios with a tag
behave -w tags=@your-tag tests/features/
```

## Refactoring History

### January 2026 - Large File Split

The following large files were split into focused modules:

- `vm_docker_steps.py` (1,913 lines) → 4 focused modules
- `daily_workflow_steps.py` (1,641 lines) → 3 focused modules + reduced core
- `installation_steps.py` (1,413 lines) → 3 focused modules
- `ssh_docker_steps.py` (1,249 lines) → 4 focused modules

Total reduction: ~6,216 lines → ~1,500 lines across focused modules.
