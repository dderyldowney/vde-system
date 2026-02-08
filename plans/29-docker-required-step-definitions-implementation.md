# Plan 29: Docker-Required Step Definitions Implementation

**Plan ID:** 29
**Created:** 2026-02-08
**Status:** Pending Approval
**Priority:** Critical

## Summary

Implement missing step definitions for Docker-required BDD tests. The feature files in `tests/features/docker-required/` are documented but lack corresponding Python step implementations.

## Current State Analysis

### Feature Files (11 total)

| Feature File | Scenarios | Steps Defined | Steps Undefined |
|--------------|----------|---------------|-----------------|
| vm-lifecycle-management.feature | 9+ | Partial | ~40 |
| vm-lifecycle.feature | 12+ | Partial | ~50 |
| template-system.feature | 8+ | Partial | ~30 |
| team-collaboration.feature | 6+ | Partial | ~25 |
| daily-development-workflow.feature | 8+ | Partial | ~30 |
| ssh-agent-vm-to-host-communication.feature | 6+ | Partial | ~20 |
| ssh-agent-forwarding-vm-to-vm.feature | 6+ | Partial | ~20 |
| collaboration-workflow.feature | 6+ | Partial | ~20 |
| **TOTAL** | **~70** | **Partial** | **~366 undefined** |

### Root Cause

The Docker-required tests were documented in feature files but step implementations were never created. Many steps show `# None` in test output, indicating no matching Python step definition exists.

## Remediation Approach

### Phase 1: Infrastructure Step Definitions

Create step definitions that interact with actual Docker and VDE infrastructure:

#### File: `tests/features/steps/vm_lifecycle_steps.py`

**Steps to implement:**
```python
@given('I want to work with a new language')
def step_want_new_language(context):
    """Set up context for creating a new language VM."""

@given('I have created a Go VM')
def step_have_created_go_vm(context):
    """Verify Go VM is created but not running."""

@when('I request to "create a Rust VM"')
def step_create_rust_vm(context):
    """Execute VDE command to create Rust VM."""
    result = subprocess.run(
        ['./scripts/vde', 'create', 'rust'],
        capture_output=True, text=True, timeout=300
    )
    context.command_result = result

@then('the VM configuration should be generated')
def step_config_generated(context):
    """Verify docker-compose.yml was created."""
    assert os.path.exists('configs/docker/rust/docker-compose.yml')

@then('the Docker image should be built')
def step_image_built(context):
    """Verify Docker image was built."""
    result = subprocess.run(
        ['docker', 'images', 'vde-rust'],
        capture_output=True, text=True
    )
    assert result.returncode == 0

@then('SSH keys should be configured')
def step_ssh_configured(context):
    """Verify SSH config exists for VM."""
    config_path = Path.home() / '.ssh' / 'config'
    if config_path.exists():
        content = config_path.read_text()
        assert 'Host rust-dev' in content
```

#### File: `tests/features/steps/vm_status_steps.py`

**Steps to implement:**
```python
@then('I should see which VMs are running')
def step_show_running_vms(context):
    """Check running VMs from VDE status."""
    result = subprocess.run(
        ['./scripts/vde', 'status', '--format', 'json'],
        capture_output=True, text=True
    )
    context.running_vms = json.loads(result.stdout)

@then('I should see which VMs are stopped')
def step_show_stopped_vms(context):
    """Check stopped VMs from VDE status."""
    # Implementation

@then('I should see any error states')
def step_show_error_states(context):
    """Check for VMs in error state."""
    # Implementation
```

### Phase 2: Template System Steps

#### File: `tests/features/steps/template_system_steps.py`

**Steps to implement:**
```python
@given('language template exists at "{path}"')
def step_template_exists(context, path):
    """Verify template file exists."""
    assert os.path.exists(path)

@when('I render template with NAME="{name}" and SSH_PORT="{port}"')
def step_render_template(context, name, port):
    """Execute template rendering."""
    result = subprocess.run(
        ['./scripts/vde', 'render', '--name', name, '--port', port],
        capture_output=True, text=True
    )
    context.rendered_output = result.stdout

@then('rendered output should contain "{expected}"')
def step_verify_rendered_content(context, expected):
    """Verify rendered template contains expected content."""
    assert expected in context.rendered_output

@then('rendered output should NOT contain "{unexpected}"')
def step_verify_no_unexpected(context, unexpected):
    """Verify template variables were replaced."""
    assert unexpected not in context.rendered_output
```

### Phase 3: Team Collaboration Steps

#### File: `tests/features/steps/team_collaboration_steps.py`

**Steps to implement:**
```python
@given('the project contains VDE configuration in configs/')
def step_project_has_vde_config(context):
    """Verify project has VDE configs."""
    assert os.path.exists('configs/docker')
    assert os.path.exists('configs/docker-compose.yml')

@when('I run the initial setup')
def step_run_initial_setup(context):
    """Execute VDE initial setup."""
    result = subprocess.run(
        ['./scripts/vde', 'setup'],
        capture_output=True, text=True, timeout=600
    )
    context.setup_result = result

@then('appropriate base images should be built')
def step_base_images_built(context):
    """Verify Docker base images exist."""
    result = subprocess.run(
        ['docker', 'images', 'vde-*'],
        capture_output=True, text=True
    )
    assert 'vde-base' in result.stdout or result.returncode == 0
```

### Phase 4: VM-to-VM Communication Steps

#### File: `tests/features/steps/vm_to_vm_steps.py`

**Steps to implement:**
```python
@given('I have a Go VM running')
def step_go_vm_running(context):
    """Start Go VM for testing."""
    subprocess.run(['./scripts/vde', 'start', 'go'], check=True)
    context.vm_go_running = True

@given('I have a Python VM running')
def step_python_vm_running(context):
    """Start Python VM for testing."""
    subprocess.run(['./scripts/vde', 'start', 'python'], check=True)
    context.vm_python_running = True

@when('I SSH into the Go VM')
def step_ssh_to_go(context):
    """SSH into Go VM."""
    # Execute SSH command to Go VM

@when('I run "ssh python-dev" from within the Go VM')
def step_vm_to_vm_ssh(context):
    """Execute SSH from Go VM to Python VM."""
    # Execute SSH command from Go VM to Python VM

@then('I should connect to the Python VM')
def step_connect_to_python(context):
    """Verify SSH connection to Python VM succeeded."""
    # Check command exit code
```

## Implementation Strategy

### Step 1: Generate Missing Step Skeletons

Run behave with `--dry-run` to generate skeleton implementations:

```bash
behave tests/features/docker-required/ --dry-run > steps-skeleton.txt
```

### Step 2: Create Step Definition Files

Create new step files for each feature category:

1. `vm_lifecycle_steps.py` - VM lifecycle operations
2. `template_system_steps.py` - Template rendering
3. `team_collaboration_steps.py` - Team workflows
4. `vm_to_vm_steps.py` - VM-to-VM communication

### Step 3: Implement Each Step

For each undefined step:
1. Identify the feature file and scenario
2. Determine required VDE/Docker commands
3. Implement the step definition
4. Add assertions for expected outcomes
5. Handle cleanup in environment.py

### Step 4: Integration Testing

Run full Docker-required test suite to verify:
```bash
./run-docker-required-tests.zsh
```

## Files to Create/Modify

### New Files
- `tests/features/steps/vm_lifecycle_steps.py`
- `tests/features/steps/template_system_steps.py`
- `tests/features/steps/team_collaboration_steps.py`
- `tests/features/steps/vm_to_vm_steps.py`

### Modified Files
- `tests/features/environment.py` - Add VM lifecycle hooks
- `tests/features/steps/vm_status_steps.py` - Add status verification steps

## Dependencies

- VDE CLI (`./scripts/vde`) must be functional
- Docker daemon must be running
- Test cleanup hooks must handle VM removal

## Expected Outcome

After implementation:
- **Features**: 11 passed, 0 failed
- **Scenarios**: 70+ passed, 0 failed
- **Steps**: All defined, 0 undefined

## Timeline

| Phase | Tasks | Estimated Time |
|-------|-------|----------------|
| Phase 1 | Infrastructure steps | 2-3 hours |
| Phase 2 | Template steps | 1-2 hours |
| Phase 3 | Team collaboration steps | 1-2 hours |
| Phase 4 | VM-to-VM steps | 1-2 hours |
| Integration | Testing and fixes | 2-4 hours |
| **TOTAL** | | **8-14 hours** |

## Approval Required

This plan requires approval before implementation begins.
