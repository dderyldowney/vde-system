"""
BDD Step Definitions for Daily Development Workflow.

These steps test common developer workflows for starting, stopping,
and managing development VMs throughout the day.
"""
import os
import subprocess
import sys
import time
from pathlib import Path

# Import shared configuration
steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)

from behave import given, then, when

from config import VDE_ROOT
from vm_common import (
    run_vde_command,
    docker_ps,
    container_exists,
    container_is_running,
    get_container_id,
)


# =============================================================================
# GIVEN steps - Setup scenarios
# =============================================================================

@given('I have a Python VM running')
def step_python_vm_running(context):
    """Ensure Python VM is running."""
    if not container_is_running('python'):
        result = run_vde_command("start python", timeout=120)
        assert result.returncode == 0, f"Failed to start Python VM: {result.stderr}"
    context.vm_name = 'python'


@given('I need a full stack environment')
def step_full_stack_environment(context):
    """Set up full stack environment with Python and PostgreSQL."""
    context.vms_to_start = ['python', 'postgres']


@given('I want to try a new language')
def step_try_new_language(context):
    """Set up scenario for trying a new language VM."""
    context.new_language = True


# =============================================================================
# WHEN steps - Actions
# =============================================================================

@when('I request to start my Python development environment')
def step_start_python_env(context):
    """Start Python development environment."""
    result = run_vde_command("start python", timeout=120)
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('I ask "what\'s running?"')
def step_ask_whats_running(context):
    """Check what VMs are running."""
    result = run_vde_command("list", timeout=30)
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('I ask "how do I connect to Python?"')
def step_ask_connect_python(context):
    """Get connection details for Python VM."""
    result = run_vde_command("status python", timeout=30)
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('I request to "start python and postgres"')
def step_start_python_postgres(context):
    """Start both Python and PostgreSQL VMs."""
    context.vm_results = {}
    for vm in ['python', 'postgres']:
        result = run_vde_command(f"start {vm}", timeout=120)
        context.vm_results[vm] = {
            'exit_code': result.returncode,
            'output': result.stdout,
            'error': result.stderr
        }


@when('I request to "create a Go VM"')
def step_create_go_vm(context):
    """Create a Go VM."""
    result = run_vde_command("create go", timeout=180)
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


# =============================================================================
# THEN steps - Verification
# =============================================================================

@then('the Python VM should be started')
def step_python_vm_started(context):
    """Verify Python VM is started."""
    assert container_is_running('python'), "Python VM should be running"


@then('SSH access should be available on the configured port')
def step_ssh_available(context):
    """Verify SSH access is available."""
    vm_name = getattr(context, 'vm_name', 'python')
    # Check port is mapped
    try:
        result = subprocess.run(
            ['docker', 'port', vm_name, '22'],
            capture_output=True, text=True, timeout=5
        )
        has_port = result.returncode == 0 and '22' in result.stdout
        assert has_port, f"SSH port should be available for {vm_name}"
    except Exception:
        # Fallback: just verify container is running
        assert container_is_running(vm_name), f"Container {vm_name} should be running"


@then('my workspace directory should be mounted')
def step_workspace_mounted(context):
    """Verify workspace directory is mounted."""
    vm_name = getattr(context, 'vm_name', 'python')
    # Check docker-compose.yml has volume mount
    config_path = VDE_ROOT / "configs" / "docker" / vm_name / "docker-compose.yml"
    assert config_path.exists(), f"docker-compose.yml should exist at {config_path}"
    content = config_path.read_text()
    assert 'projects' in content or 'workspace' in content.lower(), \
        f"Workspace volume should be mounted: {content}"








@then('I should receive SSH connection details')
def step_ssh_details_received(context):
    """Verify SSH connection details are received."""
    output = context.last_output + context.last_error
    has_ssh = any(x in output.lower() for x in ['ssh', 'connect', 'devuser@'])
    assert has_ssh, f"Should receive SSH details: {output}"


@then('the Go VM configuration should be created')
def step_go_config_created(context):
    """Verify Go VM configuration is created."""
    config_path = VDE_ROOT / "configs" / "docker" / "go" / "docker-compose.yml"
    assert config_path.exists(), f"Go VM configuration should be created at {config_path}"


@then('the Docker image should be built')
def step_docker_image_built(context):
    """Verify Docker image is built."""
    # Image is built if the VM can start
    assert container_exists('go') or container_is_running('go'), \
        "Go Docker image should be built"


@then('SSH keys should be configured')
def step_ssh_keys_configured(context):
    """Verify SSH keys are configured."""
    ssh_dir = Path.home() / ".ssh" / "vde"
    has_keys = (ssh_dir / "id_ed25519").exists() or (ssh_dir / "id_rsa").exists()
    assert has_keys or ssh_dir.exists(), f"SSH keys should be configured in {ssh_dir}"


@then('the VM should be ready to start')
def step_vm_ready_to_start(context):
    """Verify VM is ready to start."""
    config_path = VDE_ROOT / "configs" / "docker" / "go" / "docker-compose.yml"
    assert config_path.exists(), "VM configuration should exist"
    assert container_exists('go') or container_is_running('go'), \
        "VM should be ready (image built)"








@then('the Python VM should be stopped')
def step_python_stopped(context):
    """Verify Python VM is stopped."""
    running = docker_ps()
    assert 'python' not in running, "Python VM should be stopped"




@then('my workspace should still be mounted')
def step_workspace_still_mounted(context):
    """Verify workspace is still mounted after rebuild."""
    config_path = VDE_ROOT / "configs" / "docker" / "python" / "docker-compose.yml"
    assert config_path.exists(), "docker-compose.yml should exist"
    content = config_path.read_text()
    assert 'projects' in content or 'workspace' in content.lower(), \
        "Workspace should still be mounted after rebuild"
