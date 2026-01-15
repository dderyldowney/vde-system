"""
VDE Test Helpers - Shared utilities for BDD tests.

This module provides helper functions to call actual VDE scripts
and verify real system state, replacing mock implementations.
"""

from pathlib import Path
import subprocess
import time
import os

# VDE root directory - support both container and local environments
VDE_ROOT = Path(os.environ.get("VDE_ROOT_DIR", "/vde"))


def run_vde_command(command, timeout=120, check=False):
    """
    Run a VDE script and return the result.

    Args:
        command: Command string to execute
        timeout: Timeout in seconds (default: 120)
        check: If True, raise exception on non-zero exit

    Returns:
        subprocess.CompletedResult with stdout, stderr, returncode
    """
    full_command = f"cd {VDE_ROOT} && {command}"
    result = subprocess.run(
        full_command,
        shell=True,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return result


def docker_ps(filter=None):
    """
    Get list of running Docker containers.

    Args:
        filter: Optional filter string (e.g., "name=python-dev")

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
    """
    Check if a container is running for the VM.

    Args:
        vm_name: Name of the VM (e.g., "python", "rust")

    Returns:
        True if container is running, False otherwise
    """
    containers = docker_ps()
    # Language VMs use -dev suffix
    if f"{vm_name}-dev" in containers:
        return True
    # Service VMs use plain name
    if vm_name in containers:
        return True
    return False


def wait_for_container(vm_name, timeout=60, interval=2):
    """
    Wait for a container to be running.

    Args:
        vm_name: Name of the VM
        timeout: Maximum time to wait in seconds
        interval: Check interval in seconds

    Returns:
        True if container is running, False if timeout exceeded
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        if container_exists(vm_name):
            return True
        time.sleep(interval)
    return False


def wait_for_container_stop(vm_name, timeout=30, interval=1):
    """
    Wait for a container to stop.

    Args:
        vm_name: Name of the VM
        timeout: Maximum time to wait in seconds
        interval: Check interval in seconds

    Returns:
        True if container stopped, False if timeout exceeded
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        if not container_exists(vm_name):
            return True
        time.sleep(interval)
    return False


def compose_file_exists(vm_name):
    """Check if docker-compose.yml exists for VM."""
    compose_path = VDE_ROOT / "configs" / "docker" / vm_name / "docker-compose.yml"
    return compose_path.exists()


def get_ssh_port(vm_name):
    """
    Get the SSH port for a VM from its docker-compose.yml.

    Args:
        vm_name: Name of the VM

    Returns:
        Port number as string, or None if not found
    """
    compose_path = VDE_ROOT / "configs" / "docker" / vm_name / "docker-compose.yml"
    if compose_path.exists():
        content = compose_path.read_text()
        # Look for SSH port mapping (usually 22:XXXX)
        import re
        match = re.search(r'(\d+):22', content)
        if match:
            return match.group(1)
        # Also check for 22:XXXX format
        match = re.search(r'22:(\d+)', content)
        if match:
            return match.group(1)
    return None


def file_exists(path):
    """Check if a file exists relative to VDE_ROOT."""
    full_path = VDE_ROOT / path.lstrip("/")
    return full_path.exists()


def directory_exists(path):
    """Check if a directory exists relative to VDE_ROOT."""
    full_path = VDE_ROOT / path.lstrip("/")
    return full_path.is_dir()


def create_vm(vm_name, timeout=60):
    """
    Create a VM using the VDE script.

    Args:
        vm_name: Name of the VM to create
        timeout: Timeout in seconds

    Returns:
        subprocess result
    """
    return run_vde_command(f"./scripts/create-virtual-for {vm_name}", timeout=timeout)


def start_vm(vm_name, timeout=180):
    """
    Start a VM using the VDE script.

    Args:
        vm_name: Name of the VM to start
        timeout: Timeout in seconds

    Returns:
        subprocess result
    """
    return run_vde_command(f"./scripts/start-virtual {vm_name}", timeout=timeout)


def stop_vm(vm_name, timeout=60):
    """
    Stop a VM using the VDE script.

    Args:
        vm_name: Name of the VM to stop
        timeout: Timeout in seconds

    Returns:
        subprocess result
    """
    return run_vde_command(f"./scripts/shutdown-virtual {vm_name}", timeout=timeout)


def stop_all_vms(timeout=120):
    """Stop all VMs using the VDE script."""
    return run_vde_command("./scripts/shutdown-virtual all", timeout=timeout)


def remove_vm(vm_name, timeout=60):
    """Remove a VM using the VDE script."""
    return run_vde_command(f"./scripts/remove-virtual {vm_name}", timeout=timeout)


def list_vms(args="", timeout=30):
    """List VMs using the VDE script."""
    return run_vde_command(f"./scripts/list-vms {args}", timeout=timeout)


def cleanup_test_containers():
    """
    Clean up any test containers that might be running.
    """
    try:
        # Stop all VDE containers
        result = run_vde_command("./scripts/shutdown-virtual all", timeout=60)
        time.sleep(2)
    except Exception:
        pass
