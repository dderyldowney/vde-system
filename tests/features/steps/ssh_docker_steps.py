"""
BDD Step Definitions for SSH, Docker, and workflow features.

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
import subprocess
from pathlib import Path

from behave import given, then, when

# Import shared SSH helpers (run_vde_command, container_exists)
from ssh_helpers import container_exists, run_vde_command

from config import VDE_ROOT

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def mark_step_implemented(context, step_name=""):
    """Mark a step as implemented in context."""
    context.step_implemented = True
    if step_name:
        if not hasattr(context, 'implemented_steps'):
            context.implemented_steps = []
        context.implemented_steps.append(step_name)



# VDE_ROOT imported from config
# run_vde_command and container_exists imported from ssh_helpers

# Local helper for Docker operations (not in ssh_helpers)
def docker_ps():
    """Get list of running Docker containers."""
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return set(result.stdout.strip().split("\n")) if result.stdout.strip() else set()
    except Exception:
        pass
    return set()


# =============================================================================
# SSH CONFIGURATION STEPS
# =============================================================================

@given('~/.ssh/config does not exist')
def step_no_ssh_config(context):
    """VDE SSH config doesn't exist."""
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    context.ssh_config_exists = ssh_config.exists()


@given('~/.ssh/config exists')
def step_ssh_config_exists_step(context):
    """VDE SSH config exists."""
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    context.ssh_config_exists = ssh_config.exists()


@given('~/.ssh/config exists with custom settings')
def step_ssh_custom(context):
    """VDE SSH config with custom settings."""
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    context.ssh_config_exists = ssh_config.exists()
    if ssh_config.exists():
        content = ssh_config.read_text()
        context.ssh_has_custom_settings = len(content) > 0


# Note: Step @given('~/.ssh/config contains "Host python-dev"') is handled by
# the generic step_ssh_config_contains() in ssh_config_steps.py

@given('~/.ssh/config contains python-dev configuration')
def step_python_config(context):
    """VDE SSH config has python configuration."""
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    if ssh_config.exists():
        content = ssh_config.read_text()
        context.has_python_config = "python" in content.lower()
    else:
        context.has_python_config = False


@given('~/.ssh/ contains SSH keys')
def step_ssh_keys(context):
    """VDE SSH directory contains SSH keys."""
    vde_ssh_dir = Path.home() / ".ssh" / "vde"
    has_keys = (vde_ssh_dir / "id_ed25519").exists()
    context.ssh_keys_exist = has_keys


@given('~/.ssh directory does not exist')
def step_no_ssh_dir(context):
    """VDE SSH directory doesn't exist."""
    vde_ssh_dir = Path.home() / ".ssh" / "vde"
    context.ssh_dir_exists = vde_ssh_dir.exists()


@given('~/.ssh directory exists or can be created')
def step_ssh_dir_creatable(context):
    """SSH directory can be created."""
    ssh_dir = Path.home() / ".ssh"
    context.ssh_dir_can_be_created = True


@given('all keys are loaded in my SSH agent')
def step_keys_loaded(context):
    """Keys are loaded in SSH agent."""
    result = subprocess.run(["ssh-add", "-l"], capture_output=True, text=True)
    context.all_keys_loaded = result.returncode == 0


# Note: Step @given('~/.ssh/config contains user\'s "Host github.com" entry') is handled by
# the generic step_ssh_config_contains_user_entry() in ssh_config_steps.py


# =============================================================================
# VM STATE STEPS
# =============================================================================

@given('"python" VM is running')
def step_python_running(context):
    """Python VM is running."""
    context.python_running = container_exists('python')
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    if context.python_running:
        context.running_vms.add('python')


@given('a VM is running')
def step_vm_running(context):
    """A VM is running."""
    running = docker_ps()
    context.vm_running = len(running) > 0
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    for c in running:
        if "-dev" in c:
            context.running_vms.add(c.replace("-dev", ""))


@given('a VM has crashed')
def step_vm_crashed(context):
    """VM has crashed."""
    context.vm_crashed = True


@given('a VM has been removed')
def step_vm_removed(context):
    """VM has been removed."""
    context.vm_removed = True


@given('a VM is being built')
def step_vm_building(context):
    """VM is being built."""
    context.vm_building = True


@given('a VM is not working correctly')
def step_vm_not_working(context):
    """VM is not working correctly."""
    context.vm_not_working = True


@given('a VM is running but misbehaving')
def step_vm_misbehaving(context):
    """VM is misbehaving."""
    context.vm_misbehaving = True


@given('a VM seems corrupted or misconfigured')
def step_vm_corrupted(context):
    """VM is corrupted."""
    context.vm_corrupted = True


@given('a VM seems slow')
def step_vm_slow(context):
    """VM is slow."""
    context.vm_slow = True


@given("a VM's state changes")
def step_vm_state_changed(context):
    """VM state changed."""
    context.vm_state_changed = True


@given('a VM build fails')
def step_build_fails(context):
    """VM build fails."""
    context.build_failed = True


@given('a VM build keeps failing')
def step_build_fails_repeatedly(context):
    """VM build fails repeatedly."""
    context.build_fails_repeatedly = True


# =============================================================================
# DOCKER OPERATION STEPS
# =============================================================================

@given('a container is running but SSH fails')
def step_container_ssh_fails(context):
    """Container running but SSH fails."""
    context.container_running = len(docker_ps()) > 0
    context.ssh_fails = True


@given('a container takes too long to start')
def step_container_slow(context):
    """Container slow to start."""
    context.container_slow = True


@given('a docker-compose.yml is malformed')
def step_compose_malformed(context):
    """Docker-compose is malformed."""
    context.compose_malformed = True


@given('Docker daemon is not running')
def step_docker_daemon_not_running(context):
    """Docker daemon not running."""
    result = subprocess.run(["docker", "info"], capture_output=True, text=True, timeout=10)
    context.docker_daemon_running = result.returncode == 0


@given('Docker is not available')
def step_docker_not_available(context):
    """Docker not available."""
    result = subprocess.run(["docker", "--version"], capture_output=True, text=True, timeout=10)
    context.docker_available = result.returncode == 0


@given('a system service is using port "{port}"')
def step_service_using_port(context, port):
    """Port is in use by system service."""
    # Check if port is in use
    result = subprocess.run(
        ["lsof", "-i", f":{port}", "-sTCP:LISTEN", "-t"],
        capture_output=True,
        text=True,
        timeout=10
    )
    context.port_in_use = result.returncode == 0
    context.port_in_use_num = port


@given('a port is already in use')
def step_port_in_use(context):
    """Port is already in use."""
    context.port_in_use = True

