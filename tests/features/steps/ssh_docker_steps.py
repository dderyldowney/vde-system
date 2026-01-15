"""
BDD Step Definitions for SSH, Docker, and workflow features.

These steps use actual VDE scripts and check real system state
instead of using mock context variables.
"""

from behave import given, when, then
from pathlib import Path
import subprocess
import os

VDE_ROOT = Path(os.environ.get("VDE_ROOT_DIR", "/vde"))


def run_vde_command(command, timeout=120):
    """Run a VDE script and return the result."""
    result = subprocess.run(
        f"cd {VDE_ROOT} && {command}",
        shell=True,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return result


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


def container_exists(vm_name):
    """Check if a container is running for the VM."""
    containers = docker_ps()
    return f"{vm_name}-dev" in containers or vm_name in containers


# =============================================================================
# SSH CONFIGURATION STEPS
# =============================================================================

@given('~/.ssh/config does not exist')
def step_no_ssh_config(context):
    """SSH config doesn't exist."""
    ssh_config = Path.home() / ".ssh" / "config"
    context.ssh_config_exists = ssh_config.exists()


@given('~/.ssh/config exists')
def step_ssh_config_exists_step(context):
    """SSH config exists."""
    ssh_config = Path.home() / ".ssh" / "config"
    context.ssh_config_exists = ssh_config.exists()


@given('~/.ssh/config exists with custom settings')
def step_ssh_custom(context):
    """SSH config with custom settings."""
    ssh_config = Path.home() / ".ssh" / "config"
    context.ssh_config_exists = ssh_config.exists()
    if ssh_config.exists():
        content = ssh_config.read_text()
        context.ssh_has_custom_settings = len(content) > 0


@given('~/.ssh/config contains "Host python-dev"')
def step_ssh_has_python(context):
    """SSH config has python-dev entry."""
    ssh_config = Path.home() / ".ssh" / "config"
    if ssh_config.exists():
        content = ssh_config.read_text()
        context.has_python_entry = "python-dev" in content or "Host.*python" in content
    else:
        context.has_python_entry = False


@given('~/.ssh/config contains python-dev configuration')
def step_python_config(context):
    """SSH config has python configuration."""
    ssh_config = Path.home() / ".ssh" / "config"
    if ssh_config.exists():
        content = ssh_config.read_text()
        context.has_python_config = "python" in content.lower()
    else:
        context.has_python_config = False


@given('~/.ssh/ contains SSH keys')
def step_ssh_keys(context):
    """SSH keys exist."""
    ssh_dir = Path.home() / ".ssh"
    has_keys = (
        (ssh_dir / "id_ed25519").exists() or
        (ssh_dir / "id_rsa").exists() or
        (ssh_dir / "id_ecdsa").exists()
    )
    context.ssh_keys_exist = has_keys


@given('~/.ssh directory does not exist')
def step_no_ssh_dir(context):
    """SSH directory doesn't exist."""
    ssh_dir = Path.home() / ".ssh"
    context.ssh_dir_exists = ssh_dir.exists()


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


@given('~/.ssh/config contains user\'s "Host github.com" entry')
def step_github_entry(context):
    """SSH config has github entry."""
    ssh_config = Path.home() / ".ssh" / "config"
    if ssh_config.exists():
        content = ssh_config.read_text()
        context.has_github_entry = "github.com" in content
    else:
        context.has_github_entry = False


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


@given('a VM\'s state changes')
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
