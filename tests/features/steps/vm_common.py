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
    """Run a VDE script and return the result."""
    full_command = f"cd {VDE_ROOT} && {command}"
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
    """Get the type of a VM (lang or service)."""
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
    """Get the SSH port from docker-compose.yml for a VM."""
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
    """Get the SSH port for a VM by checking docker-compose or container."""
    # First try to get from docker-compose file
    port = get_port_from_compose(vm_name)
    if port:
        return port

    # Then try to get from running container
    container = f"{vm_name}-dev" if get_vm_type(vm_name) == 'lang' else vm_name
    return get_container_port_mapping(container, 22)


def compose_project_path(vm_name):
    """Get the path to VM's docker-compose project directory."""
    return VDE_ROOT / "configs" / "docker" / vm_name
