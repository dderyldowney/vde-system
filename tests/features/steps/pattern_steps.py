"""
Comprehensive catch-all step definitions for VDE BDD tests.

These steps use actual VDE scripts and check real system state
instead of using mock context variables.
"""
import os
import sys

# Import shared configuration
# Add steps directory to path for config import
steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)
import os
import subprocess
from pathlib import Path

from behave import given, then, when

from config import VDE_ROOT
from vm_common import run_vde_command, docker_ps, container_exists

# VDE_ROOT imported from config
# run_vde_command, docker_ps, container_exists imported from vm_common


# =============================================================================
# Shell Compatibility Helper Functions (specific to pattern_steps.py)
# =============================================================================

def run_shell_command(command, shell='zsh'):
    """Run a command in the specified shell with vde-shell-compat loaded (UTF-8 encoding)."""
    cmd = f"{shell} -c 'source {VDE_ROOT}/scripts/lib/vde-shell-compat && {command}'"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=VDE_ROOT, encoding='utf-8')
    return result


def run_shell_command_with_state(context, command, shell='zsh'):
    """Run a command with array state restored from context."""
    array_name = getattr(context, 'array_name', 'test_array')
    prefix = f"_assoc_init '{array_name}'; "
    if hasattr(context, 'set_keys'):
        for key, value in context.set_keys.items():
            escaped_key = key.replace("'", "'\\''")
            escaped_value = value.replace('"', '\\"')
            prefix += f'_assoc_set "{array_name}" "{escaped_key}" "{escaped_value}"; '
    full_command = prefix + command
    return run_shell_command(full_command, shell)


# =============================================================================
# SSH CONFIG STATE PATTERNS
# =============================================================================

@given('~/.ssh/config exists with blank lines')
def step_ssh_blank_lines(context):
    """Check if SSH config has blank lines."""
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    if ssh_config.exists():
        content = ssh_config.read_text()
        context.ssh_has_blank_lines = "\n\n" in content


@given('~/.ssh/config exists with content')
def step_ssh_has_content(context):
    """Check if SSH config has content."""
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    context.ssh_has_content = ssh_config.exists() and ssh_config.read_text().strip()


@given('~/.ssh/config exists with existing host entries')
def step_ssh_existing_entries(context):
    """Check if SSH config has existing entries."""
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    if ssh_config.exists():
        content = ssh_config.read_text()
        context.ssh_existing_entries = "Host " in content


@given('~/.ssh/config has comments and custom formatting')
def step_ssh_formatting(context):
    """Check if SSH config has comments."""
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    if ssh_config.exists():
        content = ssh_config.read_text()
        context.ssh_custom_formatting = "#" in content


# =============================================================================
# VM STATE PATTERNS
# =============================================================================

@given('"{vm}" VM is created but not running')
def step_vm_created_not_running(context, vm):
    """VM is created but not running."""
    compose_path = VDE_ROOT / "configs" / "docker" / vm / "docker-compose.yml"
    context.vm_created = compose_path.exists()
    context.vm_not_running = not container_exists(vm)


@given('I have "{vm}" VM running')
def step_i_have_vm_running(context, vm):
    """Check if VM is running."""
    context.vm_running = container_exists(vm)


@given('I have several VMs running')
def step_have_several_vms_running(context):
    """Check how many VMs are running."""
    # Get list of running containers
    try:
        result = subprocess.run(
            ['docker', 'ps', '-q', '--filter', 'label=com.docker.compose.project'],
            capture_output=True, text=True, timeout=10
        )
        running = result.stdout.strip().split('\n') if result.returncode == 0 and result.stdout.strip() else []
    except Exception:
        running = []
    
    vde_running = [c for c in running if "-dev" in c]
    context.num_vms_running = len(vde_running)
    context.running_vms = {c.replace("-dev", "") for c in vde_running}


# Alias for "I have several VMs running"
@given('I have multiple VMs running')
def step_have_multiple_vms_running(context):
    """Alias for checking how many VMs are running."""
    step_have_several_vms_running(context)


@given('I have {num} VMs running')
def step_have_n_vms_running(context, num):
    """Check if N VMs are running."""
    # Get list of running containers
    try:
        result = subprocess.run(
            ['docker', 'ps', '-q', '--filter', 'label=com.docker.compose.project'],
            capture_output=True, text=True, timeout=10
        )
        running = result.stdout.strip().split('\n') if result.returncode == 0 and result.stdout.strip() else []
    except Exception:
        running = []
    
    vde_running = [c for c in running if "-dev" in c]
    context.num_vms_running = len(vde_running)


@given('I have {num} VMs configured for my project')
def step_n_vms_configured(context, num):
    """Check if N VMs are configured."""
    configs_dir = VDE_ROOT / "configs" / "docker"
    if configs_dir.exists():
        count = len([d for d in configs_dir.iterdir() if d.is_dir()])
        context.num_vms_configured = min(count, int(num))
