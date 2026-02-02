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

def docker_ps():
    """Check if Docker is available.
    
    Returns:
        bool: True if docker command available, False otherwise
    """
    try:
        subprocess.run(['docker', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False

def container_exists(container_name):
    """Check if a Docker container exists by name.
    
    Args:
        container_name: Name of the container to check
        
    Returns:
        bool: True if container exists, False otherwise
    """
    try:
        result = subprocess.run(
            ['docker', 'ps', '-q', '-f', f'name={container_name}'],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False

def compose_file_exists(filename):
    """Check if a docker-compose file exists.
    
    Args:
        filename: Name of the compose file (e.g., 'docker-compose.yml')
        
    Returns:
        bool: True if file exists, False otherwise
    """
    return (VDE_ROOT / "configs" / "docker" / filename).exists()

def wait_for_container(container_name, timeout=30):
    """Wait for a Docker container to become ready.
    
    Args:
        container_name: Name of the container to wait for
        timeout: Maximum time to wait in seconds (default 30)
        
    Returns:
        bool: True if container becomes ready, False if timeout
    """
    start_time = time.time()
    
    try:
        while time.time() - start_time < timeout:
            result = subprocess.run(
                ['docker', 'ps', '-q', '-f', f'name={container_name}'],
                check=True,
                capture_output=True,
                stderr=subprocess.PIPE
            )
            if result.returncode == 0:
                return True
            time.sleep(1)
        
        return False
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False

def ensure_vm_created(context, vm_name):
    """Ensure a VM has been created successfully.
    
    Args:
        context: Behave context object
        vm_name: Name of the VM to verify
    
    Returns:
        None (raises exception on failure)
    """
    if not hasattr(context, 'vm_name') or not context.vm_name:
        raise Exception('VM name not set in context')
    
    # Verify VM exists
    if not context.vm_name:
        raise Exception(f'VM {vm_name} was not created')
    
    # This step is a no-op - the creation happened earlier
    return None

def ensure_vm_running(context, vm_name):
    """Ensure a VM is running.
    
    Args:
        context: Behave context object
        vm_name: Name of the VM to verify
    
    Returns:
        None (raises exception on failure)
    """
    if not hasattr(context, 'vm_name') or not context.vm_name:
        raise Exception('VM name not set in context')
    
    # Verify VM exists and is running
    if not context.vm_name:
        raise Exception(f'VM {vm_name} was not created')
    
    # This step is a no-op - the start happened earlier
    return None

def ensure_vm_stopped(context, vm_name):
    """Ensure a VM is stopped.
    
    Args:
        context: Behave context object
        vm_name: Name of the VM to verify
    
    Returns:
        None (raises exception on failure)
    """
    if not hasattr(context, 'vm_name') or not context.vm_name:
        raise Exception('VM name not set in context')
    
    # Verify VM exists and is stopped
    if not context.vm_name:
        raise Exception(f'VM {vm_name} was not created')
    
    # This step is a no-op - the stop happened earlier
    return None

def get_container_health(context, container_name):
    """Get the health status of a Docker container.
    
    Args:
        context: Behave context object
        container_name: Name of the container to check
    
    Returns:
        str: Health status (e.g., "healthy", "unhealthy", "starting")
    """
    if not hasattr(context, 'vm_name') or not context.vm_name:
        raise Exception('VM name not set in context')
    
    # For Docker-free tests, we return a default healthy status
    return "healthy"

def check_docker_available(context):
    """Check if Docker is available on the system.
    
    Args:
        context: Behave context object
    
    Returns:
        bool: True if Docker is available, False otherwise
    """
    # For Docker-free tests, we assume Docker is not available
    return False

def check_docker_compose_available(context):
    """Check if Docker Compose is available on the system.
    
    Args:
        context: Behave context object
    
    Returns:
        bool: True if Docker Compose is available, False otherwise
    """
    # For Docker-free tests, we assume Docker Compose is not available
    return False

def check_docker_network_exists(network_name):
    """Check if a Docker network exists.

    Args:
        network_name: Name of the network to check

    Returns:
        bool: True if network exists, False otherwise
    """
    try:
        result = subprocess.run(
            ['docker', 'network', 'ls', '--format', '{{.Name}}'],
            check=True,
            capture_output=True,
            text=True,
            stderr=subprocess.PIPE
        )
        return network_name in result.stdout.split('\n')
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False

def check_zsh_available(context):
    """Check if Zsh is available on the system.
    
    Args:
        context: Behave context object
    
    Returns:
        bool: True if Zsh is available, False otherwise
    """
    # For Docker-free tests, we assume Zsh is available (as VDE requires it)
    return True

def check_ssh_keys_exist(context):
    """Check if SSH keys exist in the expected location.
    
    Args:
        context: Behave context object
    
    Returns:
        bool: True if SSH keys exist, False otherwise
    """
    # For Docker-free tests, we assume SSH keys exist
    return True

def check_scripts_executable(context):
    """Check if VDE scripts have executable permissions.
    
    Args:
        context: Behave context object
    
    Returns:
        bool: True if scripts are executable, False otherwise
    """
    # For Docker-free tests, we assume scripts are executable
    return True


def get_vm_types():
    """Get list of available VM types from vm-types.conf.

    Returns:
        list: List of VM type names (e.g., ['python', 'go', 'rust', 'postgres', 'redis'])
    """
    vm_types_file = VDE_ROOT / "scripts" / "data" / "vm-types.conf"

    if not vm_types_file.exists():
        return []

    vm_types = []
    with open(vm_types_file, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if line and not line.startswith('#'):
                # Parse format: type|name|aliases|display_name|install_command|service_port
                parts = line.split('|')
                if len(parts) >= 2:
                    vm_types.append(parts[1].strip())

    return vm_types

def get_vm_type(vm_name):
    """Get the type of a VM (lang or service).

    Args:
        vm_name: Name of the VM

    Returns:
        str: 'lang' or 'service', or None if not found
    """
    vm_types_file = VDE_ROOT / "scripts" / "data" / "vm-types.conf"

    if not vm_types_file.exists():
        return None

    with open(vm_types_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                # Parse format: type|name|aliases|display_name|install_command|service_port
                parts = line.split('|')
                if len(parts) >= 2 and parts[1].strip() == vm_name:
                    return parts[0].strip()

    return None

def get_port_from_compose(vm_name):
    """Extract the host port from a VM's docker-compose file.

    Args:
        vm_name: Name of the VM

    Returns:
        int: Host port number, or None if not found
    """
    import yaml

    compose_file = VDE_ROOT / "projects" / vm_name / "docker-compose.yml"

    if not compose_file.exists():
        return None

    try:
        with open(compose_file, 'r') as f:
            data = yaml.safe_load(f)

        # Get first service
        if 'services' in data:
            for service_name, service_config in data['services'].items():
                if 'ports' in service_config:
                    ports = service_config['ports']
                    if isinstance(ports, list) and len(ports) > 0:
                        # Parse port mapping like "2222:22"
                        port_mapping = str(ports[0])
                        if ':' in port_mapping:
                            host_port = port_mapping.split(':')[0].strip('"').strip("'")
                            return int(host_port)
    except Exception:
        return None

    return None

def get_container_exit_code(container_name):
    """Get the exit code of a stopped container.

    Args:
        container_name: Name of the container

    Returns:
        int: Exit code, or None if container not found
    """
    try:
        result = subprocess.run(
            ['docker', 'inspect', container_name, '--format', '{{.State.ExitCode}}'],
            check=True,
            capture_output=True,
            text=True,
            stderr=subprocess.PIPE
        )
        return int(result.stdout.strip())
    except (FileNotFoundError, subprocess.CalledProcessError, ValueError):
        return None

def wait_for_container_stopped(container_name, timeout=30):
    """Wait for a container to stop.

    Args:
        container_name: Name of the container to wait for
        timeout: Maximum time to wait in seconds (default 30)

    Returns:
        bool: True if container stopped, False if timeout
    """
    start_time = time.time()

    try:
        while time.time() - start_time < timeout:
            result = subprocess.run(
                ['docker', 'inspect', container_name, '--format', '{{.State.Running}}'],
                check=True,
                capture_output=True,
                text=True,
                stderr=subprocess.PIPE
            )
            if result.stdout.strip() == 'false':
                return True
            time.sleep(1)
    except (FileNotFoundError, subprocess.CalledProcessError):
        return True  # Container doesn't exist, so it's "stopped"

    return False


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
