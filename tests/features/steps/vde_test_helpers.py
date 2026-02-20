"""
VDE Test Helpers - Shared utilities for BDD tests.

This module provides helper functions to call actual VDE scripts
and verify real system state. It extends vm_common.py with additional
test-specific utilities.
"""
import os
import subprocess
import sys
import time
from pathlib import Path

# Add steps directory to path for config import
steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)

from config import VDE_ROOT
from vm_common import (
    run_vde_command as _run_vde_command_base,
    docker_ps,
    container_exists,
    wait_for_container,
    compose_file_exists,
)


# =============================================================================
# Extended VDE Test Helpers (beyond vm_common.py)
# =============================================================================

def run_vde_command(command, timeout=300, check=False):
    """
    Run a VDE script and return the result.

    This extends the base run_vde_command with optional check parameter.

    Args:
        command: Command string or list to execute
        timeout: Timeout in seconds (default: 120)
        check: If True, raise exception on non-zero exit

    Returns:
        subprocess.CompletedResult with stdout, stderr, returncode
    """
    # Use base function for command execution
    result = _run_vde_command_base(command, timeout=timeout)

    if check and result.returncode != 0:
        raise subprocess.CalledProcessError(
            result.returncode, command, result.stdout, result.stderr
        )

    return result


def wait_for_container_stop(vm_name, timeout=120, interval=1):
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


def get_ssh_port(vm_name):
    """
    Get the SSH port for a VM using docker port command.

    This uses the same command a user would run to check port mappings.
    For running containers, docker port is the authoritative source.

    Args:
        vm_name: Name of the VM

    Returns:
        Port number as integer, or None if not found
    """
    # Use vde port command (routes through VDE, uses vde- prefix)
    import subprocess as _sp
    bare_name = vm_name.replace('vde-', '')
    try:
        result = _sp.run(
            ["zsh", str(SCRIPTS_DIR / "vde-port"), bare_name],
            capture_output=True, text=True, timeout=10, cwd=str(VDE_ROOT)
        )
        if result.returncode == 0 and result.stdout.strip():
            # Output format: "0.0.0.0:2213" or "22/tcp -> 0.0.0.0:2213"
            for line in result.stdout.strip().split('\n'):
                if '22' in line:
                    port = line.strip().split(':')[-1].strip()
                    try:
                        return int(port)
                    except ValueError:
                        pass
    except Exception:
        pass

    # Fallback: read from docker-compose.yml
    try:
        compose_file = VDE_ROOT / "configs" / "docker" / bare_name / "docker-compose.yml"
        if compose_file.exists():
            import re
            content = compose_file.read_text()
            m = re.search(r'"(\d+):22"', content)
            if m:
                return int(m.group(1))
    except Exception:
        pass

    return None


def get_vm_status(vm_name):
    """
    Get comprehensive status of a VM.

    Args:
        vm_name: Name of the VM

    Returns:
        dict with keys: running, exists, compose_exists, ssh_port
    """
    return {
        'running': container_exists(vm_name),
        'exists': compose_file_exists(vm_name),
        'compose_exists': compose_file_exists(vm_name),
        'ssh_port': get_ssh_port(vm_name),
    }


# =============================================================================
# VM Lifecycle Helpers
# =============================================================================

def create_vm(vm_name, timeout=120):
    """Create a VM using create-virtual-for script."""
    result = _run_vde_command_base(['create-virtual-for', vm_name], timeout=timeout)
    return result.returncode == 0


def start_vm(vm_name, timeout=180):
    """Start a VM using start-virtual script."""
    result = _run_vde_command_base(['start-virtual', vm_name], timeout=timeout)
    if result.returncode == 0:
        wait_for_container(vm_name, timeout=60)
    return result.returncode == 0


def stop_vm(vm_name, timeout=60):
    """Stop a VM using stop-virtual script."""
    result = _run_vde_command_base(['stop-virtual', vm_name], timeout=timeout)
    return result.returncode == 0


def file_exists(path):
    """Check if a file exists."""
    return (VDE_ROOT / path).exists()


# Legacy aliases for backwards compatibility
VDE_ROOT = VDE_ROOT
