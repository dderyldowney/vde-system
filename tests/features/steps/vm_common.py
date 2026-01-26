"""
Shared helper functions for VM lifecycle BDD tests.
These functions are used across multiple step definition files.
"""

import os
import re
import subprocess
import sys
import time
from pathlib import Path

# Import shared configuration
# Add steps directory to path for config import
steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)
from config import VDE_ROOT as _VDE_ROOT

# VDE root directory - support both container and local environments
# Use VDE_PROJECT_ROOT if set, otherwise use shared config
project_root = os.environ.get("VDE_PROJECT_ROOT")
VDE_ROOT = Path(project_root) if project_root and Path(project_root).exists() else _VDE_ROOT
SCRIPTS_DIR = VDE_ROOT / "scripts"

# Detect if running in container vs locally on host
# In container: VDE_ROOT_DIR is set to /vde
# Locally: VDE_ROOT_DIR is not set or points to a different path
# Test mode: VDE_TEST_MODE is set to 1 (allows cleanup during local testing)
IN_CONTAINER = os.environ.get("VDE_ROOT_DIR") == "/vde"
IN_TEST_MODE = os.environ.get("VDE_TEST_MODE") == "1"
# Allow cleanup if running in container OR in test mode
ALLOW_CLEANUP = IN_CONTAINER or IN_TEST_MODE


def run_vde_command(command, timeout=120):
    """Run a VDE script and return the result.

    Args:
        command: Command as string or list (will be converted to string)
        timeout: Command timeout in seconds

    Returns:
        subprocess.CompletedResult: The result of running the command

    The command can be:
    - A direct script: 'start-virtual python' or ['start-virtual', 'python']
    - A VDE parser command: 'create go' or ['create', 'go']
    - Already formatted: './scripts/start-virtual python'
    """
    # Direct VDE scripts (called directly)
    _DIRECT_SCRIPTS = {
        'start-virtual', 'stop-virtual', 'shutdown-virtual', 'remove-virtual',
        'create-virtual-for', 'add-vm-type', 'list-vms',
    }

    # VDE parser subcommands (go through ./scripts/vde)
    _VDE_SUBCOMMANDS = {
        'create', 'start', 'stop', 'restart', 'ssh', 'remove', 'uninstall',
        'list', 'status', 'health', 'nuke', 'help',
    }

    # Handle both string and list command formats
    if isinstance(command, list):
        command_str = ' '.join(str(c) for c in command)
    else:
        command_str = str(command)

    # Parse the first word to determine command type
    parts = command_str.split()
    if not parts:
        raise ValueError("Empty command")

    first_word = parts[0]

    # Don't modify if already has a path prefix
    if '/' in first_word:
        # Already has a path, use as-is
        pass
    elif first_word in _DIRECT_SCRIPTS:
        # Direct script - add ./scripts/ prefix
        command_str = f'./scripts/{command_str}'
    elif first_word in _VDE_SUBCOMMANDS:
        # VDE parser command - use ./scripts/vde
        command_str = f'./scripts/vde {command_str}'

    full_command = f"cd {VDE_ROOT} && {command_str}"
    # Pass environment variables including VDE_TEST_MODE
    env = os.environ.copy()
    result = subprocess.run(
        full_command,
        shell=True,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )
    return result


def docker_ps(filter=None):
    """Get list of running Docker containers.

    Args:
        filter: Optional Docker filter string (e.g., "name=python-dev")

    Returns:
        set of container names
    """
    cmd = ["docker", "ps", "--format", "{{.Names}}"]
    if filter:
        cmd.extend(["--filter", filter])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return set(result.stdout.strip().split("\n")) if result.stdout.strip() else set()
    except Exception:
        pass
    return set()


def container_exists(vm_name):
    """Check if a container is running for the VM."""
    containers = docker_ps()
    # Language VMs use -dev suffix
    if f"{vm_name}-dev" in containers:
        return True
    # Service VMs use plain name
    return vm_name in containers


def wait_for_container(vm_name, timeout=60, interval=2):
    """Wait for a container to be running."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if container_exists(vm_name):
            return True
        time.sleep(interval)
    return False


def compose_file_exists(vm_name):
    """Check if docker-compose.yml exists for VM."""
    compose_path = VDE_ROOT / "configs" / "docker" / vm_name / "docker-compose.yml"
    return compose_path.exists()


def get_vm_type(vm_name):
    """Get the type of a VM (lang or service) using vde status command.

    This function calls the actual vde command that users would use,
    not internal shell libraries.
    """
    # Use vde status command - same as a user would type
    result = run_vde_command(f'status {vm_name}', timeout=30)

    if result.returncode == 0:
        output = result.stdout
        # Parse vde status output to determine type
        # Language VMs appear under "Language VMs:" section
        # Service VMs appear under "Service VMs:" section
        if 'Language VMs:' in output:
            lang_section = output.split('Language VMs:')[1]
            lang_section = lang_section.split('Service VMs:')[0] if 'Service VMs:' in lang_section else lang_section
            if vm_name in lang_section:
                return 'lang'
        if 'Service VMs:' in output:
            svc_section = output.split('Service VMs:')[1]
            if vm_name in svc_section:
                return 'service'

    # Fallback: read vm-types.conf directly
    vm_types_file = VDE_ROOT / "scripts" / "data" / "vm-types.conf"
    if not vm_types_file.exists():
        return None
    with open(vm_types_file) as f:
        for line in f:
            if line.strip().startswith("#") or not line.strip():
                continue
            parts = line.strip().split("|")
            if len(parts) >= 3 and parts[1].strip() == vm_name:
                return parts[0].strip()
    return None


def get_all_containers(include_stopped=False):
    """Get list of all Docker containers (running or all)."""
    try:
        if include_stopped:
            result = subprocess.run(
                ["docker", "ps", "-a", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                timeout=10,
            )
        else:
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


def container_is_running(container_name):
    """Check if a specific Docker container is running."""
    try:
        result = subprocess.run(
            ["docker", "inspect", "-f", "{{.State.Running}}", container_name],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode == 0 and result.stdout.strip() == "true"
    except Exception:
        return False


def container_exists_any_state(container_name):
    """Check if a container exists (running or stopped)."""
    all_containers = get_all_containers(include_stopped=True)
    return container_name in all_containers


def get_container_port_mapping(container_name, internal_port=22):
    """Get the external port mapping for a container's internal port."""
    try:
        result = subprocess.run(
            ["docker", "port", container_name, str(internal_port)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            # Parse output like "0.0.0.0:2201" or ":::2201"
            output = result.stdout.strip()
            if ":" in output:
                return output.split(":")[-1]
        return None
    except Exception:
        return None


def get_port_from_compose(vm_name):
    """Get the SSH port from docker-compose.yml by reading the file directly.

    This is a fallback for when the container isn't running.
    Reads the actual docker-compose.yml file that VDE creates.
    """
    compose_path = VDE_ROOT / "configs" / "docker" / vm_name / "docker-compose.yml"
    if compose_path.exists():
        try:
            content = compose_path.read_text()
            # Look for SSH port mapping (usually port 22)
            # Pattern: "22:2201" or "22: ${SSH_PORT:-2201}"
            match = re.search(r'22:\s*"?(\d+)', content)
            if match:
                return match.group(1)
            # Also look for port in simple format
            match = re.search(r'ports:.*?[:\s](\d{4})', content, re.DOTALL)
            if match:
                return match.group(1)
        except Exception:
            pass
    return None


def get_container_health(container_name):
    """Get the health status of a container."""
    try:
        result = subprocess.run(
            ["docker", "inspect", "-f", "{{.State.Health.Status}}", container_name],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        # Fallback: check if container is running (no health check configured)
        result = subprocess.run(
            ["docker", "inspect", "-f", "{{.State.Running}}", container_name],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip() == "true":
            return "healthy"  # Running without health check is considered healthy
        return "unhealthy"
    except Exception:
        return "unknown"


def get_container_exit_code(container_name):
    """Get the exit code of a stopped container."""
    try:
        result = subprocess.run(
            ["docker", "inspect", "-f", "{{.State.ExitCode}}", container_name],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            return int(result.stdout.strip())
        return -1
    except (ValueError, Exception):
        return -1


def get_vm_ssh_port(vm_name):
    """Get the SSH port for a VM using docker port command.

    This uses the same command a user would run to check port mappings.
    For running containers, docker port is the authoritative source.
    For stopped containers, falls back to reading docker-compose.yml.
    """
    # First try docker port command (authoritative for running containers)
    # Language VMs use -dev suffix
    container_name = f"{vm_name}-dev"
    port = get_container_port_mapping(container_name, 22)
    if port:
        return port

    # Try plain name for service VMs
    port = get_container_port_mapping(vm_name, 22)
    if port:
        return port

    # Fallback to reading docker-compose.yml (for stopped containers)
    return get_port_from_compose(vm_name)


def compose_project_path(vm_name):
    """Get the path to VM's docker-compose project directory."""
    return VDE_ROOT / "configs" / "docker" / vm_name


def get_test_containers():
    """Get only test-created containers, not user's actual VMs.

    Test containers are labeled with 'vde.test=true'. This allows tests to
    verify only their own containers without being affected by the user's
    actual development VMs.

    Returns:
        set: Set of test container names
    """
    import subprocess
    result = subprocess.run(
        ["docker", "ps", "--filter", "label=vde.test=true", "--format", "{{.Names}}"],
        capture_output=True,
        text=True,
        timeout=10
    )
    if result.returncode != 0:
        return set()

    containers = {c for c in result.stdout.strip().split('\n') if c}
    return containers


def is_test_container(container_name):
    """Check if a container is a test container by checking for the vde.test label.

    Args:
        container_name: Name of the container to check

    Returns:
        bool: True if the container has the vde.test label
    """
    import subprocess
    result = subprocess.run(
        ["docker", "inspect", "-f", "{{index .Config.Labels}}", container_name],
        capture_output=True,
        text=True,
        timeout=5
    )
    if result.returncode != 0:
        return False

    # Labels are returned as a list-like string
    labels_str = result.stdout.strip()
    return "vde.test=true" in labels_str or "vde.test" in labels_str
