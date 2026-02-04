# Docker-Required Test Suite Implementation Plan

## Executive Summary

The docker-required test suite contains **~200+ scenarios** across **18+ feature files** requiring Docker daemon access. Current status shows many undefined steps (`None`) and TypeError bugs in assertion helpers. This plan outlines a phased approach to implement and fix the infrastructure with automatic Docker detection and full VDE command support.

## Docker Detection and Setup

Since Docker is **installed and available** on this host, all VM operations are usable:
- `create-virtual-for <vm>` - Create new VM
- `start-virtual <vm>` - Start VM
- `shutdown-virtual <vm>` - Stop VM
- `restart-virtual <vm>` - Restart VM
- `remove-virtual <vm>` - Delete VM
- `start-virtual <vm> --rebuild` - Rebuild VM from scratch
- `start-virtual all` - Start all VMs
- `shutdown-virtual all` - Stop all VMs

### Automatic Docker Detection Pattern

```python
# In environment.py or docker_helpers.py
def detect_docker_and_vde():
    """
    Automatically detect Docker availability and VDE setup.
    Returns tuple: (docker_available, vde_available, message)
    """
    # Check Docker
    try:
        result = subprocess.run(
            ['docker', 'version', '--format', '{{.Server.Version}}'],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            return False, False, "Docker daemon not running"
        docker_version = result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False, False, "Docker not installed"
    
    # Check VDE scripts
    vde_scripts = ['create-virtual-for', 'start-virtual', 'shutdown-virtual']
    for script in vde_scripts:
        if not os.path.exists(f'scripts/{script}.zsh'):
            return True, False, f"VDE script scripts/{script}.zsh not found"
    
    # Check vm-types.conf
    if not os.path.exists('scripts/data/vm-types.conf'):
        return True, False, "VM types config not found"
    
    return True, True, f"Docker {docker_version} + VDE ready"
```

### Behave Environment Hook

```python
# In environment.py
import subprocess
import os
import sys

def before_all(context):
    """Initialize Docker and VDE detection."""
    docker_ok, vde_ok, message = detect_docker_and_vde()
    
    if not docker_ok:
        print(f"⚠️  Docker not available: {message}")
        print("Running docker-free tests only...")
        # Could set a context flag to skip @requires-docker-host tests
    
    if not vde_ok:
        print(f"⚠️  VDE not properly configured: {message}")
    
    context.docker_available = docker_ok
    context.vde_available = vde_ok
    print(f"🐳 Docker: {'✓' if docker_ok else '✗'} | VDE: {'✓' if vde_ok else '✗'}")

def after_all(context):
    """Cleanup test artifacts."""
    # Optionally cleanup test VMs created during testing
    pass
```

### VM Cleanup Fixture

```python
# In environment.py
import uuid

@pytest.fixture(scope="scenario")
def cleanup_vm(context):
    """Automatically cleanup VM after scenario."""
    created_vms = []
    
    def _create_cleanup(vm_name):
        created_vms.append(vm_name)
    
    yield _create_cleanup
    
    # Teardown: remove created VMs
    for vm_name in created_vms:
        try:
            subprocess.run(
                ['zsh', 'scripts/remove-virtual.zsh', vm_name],
                capture_output=True, timeout=30
            )
            print(f"🧹 Cleaned up VM: {vm_name}")
        except Exception as e:
            print(f"⚠️  Failed to cleanup {vm_name}: {e}")
```

## Current State Analysis

### Feature Files (18 total)
| Feature File | Scenarios | Status |
|--------------|-----------|--------|
| `vm-lifecycle.feature` | 17 | Partial implementation, TypeErrors |
| `vm-lifecycle-management.feature` | 12 | Many undefined steps |
| `vm-state-awareness.feature` | 14 | All undefined |
| `docker-operations.feature` | 12 | All undefined |
| `docker-and-container-management.feature` | 13 | All undefined |
| `error-handling-and-recovery.feature` | 16 | All undefined |
| `installation-setup.feature` | 17 | Partial, context bugs |
| `configuration-management.feature` | 18 | All undefined |
| `daily-development-workflow.feature` | 10 | All undefined |
| `daily-workflow.feature` | 10 | All undefined |
| `multi-project-workflow.feature` | 9 | All undefined |
| `natural-language-commands.feature` | 13 | All undefined |
| `port-management.feature` | 13 | All undefined |
| `productivity-features.feature` | 5 | All undefined |
| `ssh-agent-automatic-setup.feature` | 11 | All undefined |
| `ssh-agent-external-git-operations.feature` | 10 | All undefined |
| `ssh-agent-forwarding-vm-to-vm.feature` | 10 | All undefined |
| `ssh-agent-vm-to-host-communication.feature` | 10 | All undefined |
| `ssh-and-remote-access.feature` | 12 | Partial, TypeErrors |
| `team-collaboration-and-maintenance.feature` | 10 | All undefined |
| `template-system.feature` | 12 | All undefined |
| `debugging-troubleshooting.feature` | 14 | All undefined |
| `collaboration-workflow.feature` | 11 | All undefined |

### Critical Bugs Identified

**TypeError: 'bool' object is not iterable**
```python
# In vm_lifecycle_assertion_steps.py
def step_vm_should_be_running(context, vm_name):
    vm_containers = [c for c in running if vm_name in c.get('names', '')]
# Problem: `running` is a boolean, not a list
```

**Missing Context Arguments**
```python
# In installation_steps.py
context.docker_installed = check_docker_available()  # Missing: context parameter
```

## Root Cause Analysis

1. **Context Variable Pattern**: Steps expect `context.running` to be a list of containers, but it's being set to a boolean elsewhere
2. **Helper Function Signatures**: Functions like `check_docker_available()` require context but are called without it
3. **Missing Implementations**: Most THEN assertions are not implemented (marked as "None")

## Implementation Strategy

### Phase 1: Docker Detection + Critical Bugs

#### Step 1.1: Add Automatic Docker Detection
**File**: `tests/features/environment.py`

```python
def detect_docker():
    """Check Docker availability and return status."""
    try:
        result = subprocess.run(
            ['docker', 'version', '--format', '{{.Server.Version}}'],
            capture_output=True, text=True, timeout=10
        )
        return {
            'available': True,
            'version': result.stdout.strip(),
            'containers': get_docker_containers()
        }
    except Exception as e:
        return {
            'available': False,
            'error': str(e),
            'containers': []
        }

def get_docker_containers():
    """Get list of running containers."""
    try:
        result = subprocess.run(
            ['docker', 'ps', '--format', '{{json .}}'],
            capture_output=True, text=True, timeout=10
        )
        if not result.stdout.strip():
            return []
        return [json.loads(line) for line in result.stdout.strip().split('\n')]
    except Exception:
        return []
```

#### Step 1.2: Fix vm_lifecycle_assertion_steps.py TypeErrors
**File**: `tests/features/steps/vm_lifecycle_assertion_steps.py`

**Issues to Fix**:
- Line 139: `step_vm_should_be_running`
- Line 147: `step_vm_not_running`
- Line 162: `step_all_vms_running`
- Line 178: `step_no_vms_running`

**Fix Pattern**:
```python
@when("I run \"start-virtual {vm_name}\"")
def step_start_vm(context, vm_name):
    """Start a VM and update running containers list."""
    result = subprocess.run(
        ['zsh', 'scripts/start-virtual.zsh', vm_name],
        capture_output=True, text=True, timeout=120
    )
    if result.returncode != 0:
        raise AssertionError(f"Failed to start {vm_name}: {result.stderr}")
    
    # Update context.running with actual container list
    context.running = get_docker_containers()
    context.created_vms = getattr(context, 'created_vms', [])
    context.created_vms.append(vm_name)
```

#### Step 1.3: Fix installation_steps.py Context Bug
**File**: `tests/features/steps/installation_steps.py`

```python
def check_docker_available(context=None):
    """Check if Docker is available with optional context."""
    try:
        result = subprocess.run(
            ['docker', 'version', '--format', '{{.Server.Version}}'],
            capture_output=True, text=True, timeout=10
        )
        docker_ok = result.returncode == 0
        if context is not None:
            context.docker_available = docker_ok
        return docker_ok
    except (subprocess.TimeoutExpired, FileNotFoundError):
        if context is not None:
            context.docker_available = False
        return False
```

### Phase 2: Implement Core Docker Helpers

#### Step 2.1: Enhanced docker_helpers.py
**File**: `tests/features/steps/docker_helpers.py`

```python
def verify_container_running(container_name: str) -> Dict[str, str]:
    """Verify container is running using docker ps."""
    result = subprocess.run(
        ['docker', 'ps', '--filter', f'name={container_name}', '--format', '{{json .}}'],
        capture_output=True, text=True, timeout=10
    )
    if not result.stdout.strip():
        raise DockerVerificationError(f"Container {container_name} not running")
    return json.loads(result.stdout.strip())

def is_container_running(container_name: str) -> bool:
    """Quick check if container is running."""
    try:
        verify_container_running(container_name)
        return True
    except DockerVerificationError:
        return False

def get_container_by_name(containers: List[Dict], name: str) -> Optional[Dict]:
    """Find container in list by name."""
    for c in containers:
        if name in c.get('Names', ''):
            return c
    return None

def wait_for_container(container_name: str, timeout: int = 60) -> bool:
    """Wait for container to be running."""
    start = time.time()
    while time.time() - start < timeout:
        if is_container_running(container_name):
            return True
        time.sleep(1)
    return False

def cleanup_vm(vm_name: str) -> bool:
    """Remove VM using VDE remove-virtual script."""
    try:
        result = subprocess.run(
            ['zsh', 'scripts/remove-virtual.zsh', vm_name],
            capture_output=True, text=True, timeout=60
        )
        return result.returncode == 0
    except Exception:
        return False

def reset_vm(vm_name: str) -> bool:
    """Reset VM (stop + remove + create)."""
    subprocess.run(['zsh', 'scripts/shutdown-virtual.zsh', vm_name], capture_output=True)
    subprocess.run(['zsh', 'scripts/remove-virtual.zsh', vm_name], capture_output=True)
    result = subprocess.run(
        ['zsh', 'scripts/create-virtual-for.zsh', vm_name],
        capture_output=True, timeout=120
    )
    return result.returncode == 0

def rebuild_vm(vm_name: str) -> bool:
    """Rebuild VM with --rebuild flag."""
    result = subprocess.run(
        ['zsh', 'scripts/start-virtual.zsh', vm_name, '--rebuild'],
        capture_output=True, timeout=300
    )
    return result.returncode == 0

def create_vm(vm_name: str) -> bool:
    """Create VM using create-virtual-for."""
    result = subprocess.run(
        ['zsh', 'scripts/create-virtual-for.zsh', vm_name],
        capture_output=True, timeout=120
    )
    return result.returncode == 0
```

### Phase 3: VM Lifecycle Steps

#### Step 3.1: VM Creation with Docker Verification
**File**: `tests/features/steps/vm_creation_steps.py`

```python
@given("VM \"{vm_name}\" is defined as a language VM with install command \"{install_cmd}\"")
def step_vm_language_defined(context, vm_name, install_cmd):
    """Verify VM type exists in vm-types.conf."""
    context.vm_types = load_vm_types()
    assert vm_name in context.vm_types['lang'], f"VM {vm_name} not found in lang types"
    context.vm_name = vm_name

@given("no VM configuration exists for \"{vm_name}\"")
def step_no_config(context, vm_name):
    """Ensure VM config doesn't exist."""
    config_path = f'configs/docker/{vm_name}/docker-compose.yml'
    if os.path.exists(config_path):
        subprocess.run(['zsh', 'scripts/remove-virtual.zsh', vm_name], capture_output=True)
    assert not os.path.exists(config_path)

@when("I run \"create-virtual-for {vm_name}\"")
def step_create_vm(context, vm_name):
    """Create VM using VDE script."""
    result = subprocess.run(
        ['zsh', 'scripts/create-virtual-for.zsh', vm_name],
        capture_output=True, text=True, timeout=120
    )
    context.create_result = result
    if result.returncode != 0:
        raise AssertionError(f"Failed to create {vm_name}: {result.stderr}")

@then("a docker-compose.yml file should be created at \"{path}\"")
def step_verify_compose(context, path):
    """Verify docker-compose.yml was created."""
    assert os.path.exists(path), f"docker-compose.yml not found at {path}"
```

#### Step 3.2: VM Start/Stop with Docker Verification
**File**: `tests/features/steps/vm_lifecycle_steps.py`

```python
@given("VM \"{vm_name}\" is not running")
def step_vm_not_running(context, vm_name):
    """Ensure VM is stopped."""
    subprocess.run(['zsh', 'scripts/shutdown-virtual.zsh', vm_name], capture_output=True)
    # Verify not running
    assert not is_container_running(f'{vm_name}-dev'), f"VM {vm_name} still running"

@when("I run \"start-virtual {vm_name}\"")
def step_start_vm(context, vm_name):
    """Start VM using VDE script."""
    result = subprocess.run(
        ['zsh', 'scripts/start-virtual.zsh', vm_name],
        capture_output=True, text=True, timeout=120
    )
    context.start_result = result
    if result.returncode != 0:
        raise AssertionError(f"Failed to start {vm_name}: {result.stderr}")
    
    # Update context with running containers
    context.running = get_docker_containers()

@then("VM \"{vm_name}\" should be running")
def step_verify_running(context, vm_name):
    """Verify VM container is running."""
    container_name = f'{vm_name}-dev'
    assert is_container_running(container_name), f"VM {vm_name} not running"
    
    # Also verify in context.running if present
    if hasattr(context, 'running'):
        found = get_container_by_name(context.running, container_name)
        assert found is not None, f"{vm_name} not in running containers list"
```

### Phase 4: Port Management

**File**: `tests/features/steps/port_management_steps.py`

```python
@given("no language VMs are created")
def step_no_language_vms(context):
    """Ensure no language VMs exist."""
    for vm in ['python', 'go', 'rust', 'js']:
        subprocess.run(['zsh', 'scripts/remove-virtual.zsh', vm], capture_output=True)

@when("I create a language VM")
def step_create_language_vm(context):
    """Create Python VM for testing."""
    result = subprocess.run(
        ['zsh', 'scripts/create-virtual-for.zsh', 'python'],
        capture_output=True, text=True, timeout=120
    )
    context.create_result = result
    assert result.returncode == 0, f"Failed: {result.stderr}"

@then("the VM should be allocated port \"{expected_port}\"")
def step_verify_port(context, expected_port):
    """Verify port allocation."""
    # Check port registry
    registry_path = '.cache/port-registry'
    if os.path.exists(registry_path):
        with open(registry_path) as f:
            registry = json.load(f)
            assert 'python' in registry, "Python not in port registry"
            assert str(registry['python']) == expected_port, \
                f"Expected port {expected_port}, got {registry['python']}"
```

### Phase 5: SSH Configuration

**File**: `tests/features/steps/ssh_config_steps.py`

```python
@given("SSH config file exists")
def step_ssh_config_exists(context):
    """Ensure SSH config exists."""
    ssh_dir = os.path.expanduser('~/.ssh')
    os.makedirs(ssh_dir, exist_ok=True)
    
    config_path = os.path.join(ssh_dir, 'config')
    if not os.path.exists(config_path):
        Path(config_path).touch()
    assert os.path.exists(config_path)

@then("SSH config should contain \"{content}\"")
def step_verify_ssh_config(context, content):
    """Verify SSH config contains expected content."""
    config_path = os.path.expanduser('~/.ssh/config')
    with open(config_path) as f:
        config = f.read()
    assert content in config, f"SSH config missing: {content}"
```

## Dependency Graph

```
Phase 1 (Docker Detection + Bugs)
├── environment.py (Docker detection hooks)
├── vm_lifecycle_assertion_steps.py (TypeError fixes)
└── installation_steps.py (context bug fixes)

Phase 2 (Docker Helpers)
├── docker_helpers.py (enhanced helpers)
├── vm_creation_steps.py
└── vm_lifecycle_steps.py

Phase 3 (VM Lifecycle)
├── vm_creation_steps.py
├── vm_lifecycle_steps.py
└── vm_lifecycle_assertion_steps.py

Phase 4 (Port Management)
├── port_management_steps.py
└── docker_helpers.py (port helpers)

Phase 5 (SSH Config)
├── ssh_config_steps.py
├── ssh_connection_steps.py
└── ssh_helpers.py

Phase 6 (Templates)
└── template_steps.py

Phase 7+ (Features)
├── configuration_steps.py
├── error_handling_steps.py
├── debugging_steps.py
└── [other feature files]
```

## Available VDE Commands

All commands work on this host with Docker available:

| Command | Purpose | Example |
|---------|---------|---------|
| `create-virtual-for <vm>` | Create new VM | `create-virtual-for python` |
| `start-virtual <vm>` | Start VM | `start-virtual python` |
| `shutdown-virtual <vm>` | Stop VM | `shutdown-virtual python` |
| `restart-virtual <vm>` | Restart VM | `restart-virtual python` |
| `remove-virtual <vm>` | Delete VM | `remove-virtual python` |
| `start-virtual <vm> --rebuild` | Rebuild from scratch | `start-virtual python --rebuild` |
| `start-virtual all` | Start all VMs | `start-virtual all` |
| `shutdown-virtual all` | Stop all VMs | `shutdown-virtual all` |
| `list-vms` | List VM types | `list-vms` |
| `list-vms --lang` | List language VMs | `list-vms --lang` |
| `list-vms --svc` | List service VMs | `list-vms --svc` |

## Testing Commands

```bash
# Run docker-required tests (requires Docker)
behave tests/features/docker-required/vm-lifecycle.feature

# Run all docker-required tests
behave tests/features/docker-required/ --tags=@requires-docker-host

# Run specific scenario
behave tests/features/docker-required/vm-lifecycle.feature:32

# Skip docker-required tests
behave tests/features/ --tags=~@requires-docker-host

# Run with verbose output
behave tests/features/docker-required/ -v
```

## Success Criteria

### Phase 1 Complete
- [ ] Docker detection works in environment.py
- [ ] No TypeErrors in vm_lifecycle_assertion_steps.py
- [ ] No context argument bugs in installation_steps.py
- [ ] All helpers return correct types

### Phase 2 Complete
- [ ] get_docker_containers() returns list[dict]
- [ ] create_vm(), start_vm(), stop_vm(), remove_vm() work
- [ ] rebuild_vm(), reset_vm() work
- [ ] DockerTestContext handles cleanup

### Phase 3 Complete
- [ ] VM creation scenarios pass
- [ ] VM start/stop scenarios pass
- [ ] Port allocation scenarios pass

### Phase 4+ Complete
- [ ] All docker-required features implemented
- [ ] No undefined steps (None)
- [ ] All scenarios pass with real Docker

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Docker not available | Auto-detect, skip with message |
| Test flakiness | Wait for container, unique names |
| Long execution | Parallel tests, layer caching |
| VM conflicts | Cleanup fixture per scenario |

## Next Steps

1. **Immediate**: Implement Phase 1 (Docker detection + bug fixes)
2. **Short-term**: Implement Phase 2-3 (Helpers + Lifecycle)
3. **Medium-term**: Implement remaining phases
4. **Long-term**: Full docker-required test suite pass

---

**Plan Created**: 2026-02-04
**Docker Available**: ✓
**VDE Commands**: ✓ (create, start, stop, restart, remove, rebuild)
**Status**: Ready for Implementation
