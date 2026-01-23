"""
BDD Step Definitions for SSH, Docker, and workflow features.

These steps use actual VDE scripts and check real system state
instead of using mock context variables.
"""
import os
import sys
import time

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

# VDE_ROOT imported from config
# run_vde_command and container_exists imported from ssh_helpers

# Local helper for Docker operations (not in ssh_helpers)


def get_container_health(vm_name):
    """Get detailed container health status using docker inspect."""
    try:
        result = subprocess.run(
            ["docker", "inspect", "--format",
             "{{.State.Status}},{{.State.OOMKilled}},{{.State.Restarting}}",
             f"{vm_name}-dev"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            parts = result.stdout.strip().split(",")
            return {
                "status": parts[0] if len(parts) > 0 else "",
                "oom_killed": parts[1] == "true" if len(parts) > 1 else False,
                "restarting": parts[2] == "true" if len(parts) > 2 else False,
            }
    except Exception:
        pass
    return None
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
    """SSH directory can be created - check if directory exists or parent is writable."""
    ssh_dir = Path.home() / ".ssh"
    if ssh_dir.exists():
        context.ssh_dir_can_be_created = True
    else:
        parent = ssh_dir.parent
        context.ssh_dir_can_be_created = os.access(parent, os.W_OK)


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
    """VM has crashed - check for exited containers."""
    result = subprocess.run(
        ["docker", "ps", "-a", "--filter", "status=exited", "--format", "{{.Names}}"],
        capture_output=True,
        text=True,
        timeout=10
    )
    crashed_containers = [name for name in result.stdout.strip().split("\n") if name]
    context.vm_crashed = len(crashed_containers) > 0
    if crashed_containers:
        context.crashed_vm = crashed_containers[0].replace("-dev", "")


@given('a VM has been removed')
def step_vm_removed(context):
    """VM has been removed - check for VM where compose file is missing."""
    running = docker_ps()
    configs_dir = VDE_ROOT / "configs" / "docker"
    if configs_dir.exists():
        for vm_dir in configs_dir.iterdir():
            vm_name = vm_dir.name
            if f"{vm_name}-dev" not in running and not vm_dir.exists():
                context.vm_removed = True
                context.removed_vm = vm_name
                return
    context.vm_removed = False


@given('a VM is being built')
def step_vm_building(context):
    """VM is being built - check for docker build processes."""
    result = subprocess.run(
        ["ps", "aux"],
        capture_output=True,
        text=True,
        timeout=5
    )
    context.vm_building = "docker build" in result.stdout.lower() or "docker-compose build" in result.stdout.lower()


@given('a VM is not working correctly')
def step_vm_not_working(context):
    """VM is not working correctly - check for exited status."""
    running = docker_ps()
    if not running:
        context.vm_not_working = False
    else:
        for vm in running:
            health = get_container_health(vm.replace("-dev", ""))
            if health and health["status"] == "exited":
                context.vm_not_working = True
                return
        context.vm_not_working = False


@given('a VM is running but misbehaving')
def step_vm_misbehaving(context):
    """VM is misbehaving - check for restart loops or OOM kills."""
    running = docker_ps()
    for vm in running:
        health = get_container_health(vm.replace("-dev", ""))
        if health and (health["restarting"] or health["oom_killed"]):
            context.vm_misbehaving = True
            return
    context.vm_misbehaving = False


@given('a VM seems corrupted or misconfigured')
def step_vm_corrupted(context):
    """VM is corrupted - check for error patterns in logs."""
    running = docker_ps()
    for vm in running[:1]:  # Check first running VM
        result = subprocess.run(
            ["docker", "logs", "--tail", "20", vm],
            capture_output=True,
            text=True,
            timeout=10
        )
        error_patterns = ["error", "failed", "corrupt", "cannot start"]
        logs_lower = result.stdout.lower() + result.stderr.lower()
        context.vm_corrupted = any(pattern in logs_lower for pattern in error_patterns)
        return
    context.vm_corrupted = False


@given('a VM seems slow')
def step_vm_slow(context):
    """VM is slow - measure response time."""
    start = time.time()
    result = subprocess.run(
        ["docker", "ps"],
        capture_output=True,
        text=True,
        timeout=30
    )
    elapsed = time.time() - start
    context.vm_slow = elapsed > 5.0  # Consider slow if > 5 seconds


@given("a VM's state changes")
def step_vm_state_changed(context):
    """VM state changed - capture before/after."""
    context.vm_state_before = docker_ps()
    time.sleep(1)
    context.vm_state_after = docker_ps()
    context.vm_state_changed = context.vm_state_before != context.vm_state_after


@given('a VM build fails')
def step_build_fails(context):
    """VM build fails - check for build errors in recent containers."""
    # Check for containers with non-zero exit codes
    result = subprocess.run(
        ["docker", "ps", "-a", "--filter", "status=exited", "--format", "{{.Names}} {{.ExitCode}}"],
        capture_output=True,
        text=True,
        timeout=10
    )
    for line in result.stdout.strip().split("\n"):
        if line:
            parts = line.split()
            if len(parts) == 2:
                try:
                    exit_code = int(parts[1])
                    if exit_code != 0:
                        context.build_failed = True
                        return
                except ValueError:
                    pass
    context.build_failed = False


@given('a VM build keeps failing')
def step_build_fails_repeatedly(context):
    """VM build fails repeatedly - check for repeated restart counts."""
    result = subprocess.run(
        ["docker", "ps", "-a", "--format", "{{.Names}} {{.RestartCount}}"],
        capture_output=True,
        text=True,
        timeout=10
    )
    for line in result.stdout.strip().split("\n"):
        if line:
            parts = line.split()
            if len(parts) == 2:
                try:
                    restart_count = int(parts[1])
                    if restart_count > 3:
                        context.build_fails_repeatedly = True
                        return
                except ValueError:
                    pass
    context.build_fails_repeatedly = False


# =============================================================================
# DOCKER OPERATION STEPS
# =============================================================================

@given('a container is running but SSH fails')
def step_container_ssh_fails(context):
    """Container running but SSH fails - actually test SSH connection."""
    running = docker_ps()
    if not running:
        context.container_running = False
        context.ssh_fails = False
        return

    context.container_running = True
    # Try to SSH to the first running container
    test_vm = list(running)[0].replace("-dev", "")
    result = subprocess.run(
        ["ssh", "-o", "ConnectTimeout=5", "-o", "BatchMode=yes",
         f"{test_vm}", "echo", "test"],
        capture_output=True,
        text=True,
        timeout=10
    )
    context.ssh_fails = result.returncode != 0


@given('a container takes too long to start')
def step_container_slow(context):
    """Container slow to start - measure start time."""
    # Check for stopped containers
    result = subprocess.run(
        ["docker", "ps", "-a", "--filter", "status=exited", "--format", "{{.Names}}"],
        capture_output=True,
        text=True,
        timeout=10
    )
    exited = result.stdout.strip().split("\n") if result.stdout.strip() else []
    if exited:
        vm_name = exited[0].replace("-dev", "")
        start_time = time.time()
        subprocess.run(
            ["docker", "start", vm_name],
            capture_output=True,
            timeout=60
        )
        elapsed = time.time() - start_time
        context.container_slow = elapsed > 30.0  # Slow if > 30 seconds
    else:
        # No stopped containers - check existing
        context.container_slow = False


@given('a docker-compose.yml is malformed')
def step_compose_malformed(context):
    """Docker-compose is malformed - validate with docker-compose config."""
    configs_dir = VDE_ROOT / "configs" / "docker"
    found_malformed = False
    if configs_dir.exists():
        for vm_dir in configs_dir.iterdir():
            compose_file = vm_dir / "docker-compose.yml"
            if compose_file.exists():
                result = subprocess.run(
                    ["docker-compose", "-f", str(compose_file), "config", "--quiet"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode != 0:
                    context.compose_malformed = True
                    context.malformed_compose = str(compose_file)
                    return
    context.compose_malformed = False


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
