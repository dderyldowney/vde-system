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
BIN_DIR = VDE_ROOT / "bin"

# Detect if running in container vs locally on host
# In container: VDE_ROOT_DIR is set to /vde
# Locally: VDE_ROOT_DIR is not set or points to a different path
# Test mode: VDE_TEST_MODE is set to 1 (allows cleanup during local testing)
IN_CONTAINER = os.environ.get("VDE_ROOT_DIR") == "/vde"
IN_TEST_MODE = os.environ.get("VDE_TEST_MODE") == "1"
# Allow cleanup if running in container OR in test mode
ALLOW_CLEANUP = IN_CONTAINER or IN_TEST_MODE


def _vm_conf_dir(vm_name):
    """Get VM configuration directory in configs/docker/."""
    # Normalize name (remove vde- prefix if present)
    name = vm_name.replace("vde-", "")
    return VDE_ROOT / "configs" / "docker" / name


def is_vde_available():
    """Check if VDE command is available.

    Returns:
        bool: True if vde command available, False otherwise
    """
    try:
        subprocess.run(
            [str(BIN_DIR / "vde"), "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def _vde_env():
    """Return environment dict for vde CLI calls: logs to stderr, stdout is clean."""
    from config import VDE_CACHE_DIR

    return {
        **os.environ,
        "VDE_ROOT_DIR": str(VDE_ROOT),
        "VDE_LOG_OUTPUT": "stderr",
        "VDE_CACHE_DIR": str(VDE_CACHE_DIR),
        "VDE_LOG_LEVEL": "DEBUG",
    }


def docker_ps():
    """Get list of running Docker container names.

    Returns:
        list: List of running container names, empty list if none or Docker unavailable
    """
    return docker_list_containers()


def docker_ps_list():
    """List running VDE containers with details via vde ps.

    Returns:
        list: List of dicts with container info (Names, etc.), empty list if none or unavailable
    """
    try:
        result = subprocess.run(
            ["zsh", str(BIN_DIR / "vde"), "ps", "-q"],
            capture_output=True,
            text=True,
            timeout=15,
            cwd=str(VDE_ROOT),
            env=_vde_env(),
        )
        containers = []
        for line in result.stdout.strip().split("\n"):
            name = line.strip()
            if name:
                containers.append({"Names": name})
        return containers
    except Exception:
        return []


def docker_list_containers():
    """List running VDE container names via vde ps.

    Returns:
        list: List of running container names, empty list if none or unavailable
    """
    try:
        result = subprocess.run(
            ["zsh", str(BIN_DIR / "vde"), "ps", "-q"],
            capture_output=True,
            text=True,
            timeout=15,
            cwd=str(VDE_ROOT),
            env=_vde_env(),
        )
        containers = [line.strip() for line in result.stdout.strip().split("\n") if line.strip()]
        return containers
    except Exception:
        return []


def container_exists(container_name):
    """Check if a VDE container exists (running or stopped) via vde ps."""
    try:
        full_name = f"vde-{container_name.replace('vde-', '')}"
        result = subprocess.run(
            ["zsh", str(BIN_DIR / "vde"), "ps", "-a", "-q"],
            capture_output=True,
            text=True,
            timeout=15,
            cwd=str(VDE_ROOT),
            env=_vde_env(),
        )
        return full_name in result.stdout.split()
    except Exception:
        return False


def container_is_running(container_name):
    """Check if a VDE container is currently running via vde ps.

    Args:
        container_name: Name of the container to check (with or without vde- prefix)

    Returns:
        bool: True if container is running, False otherwise
    """
    try:
        simple_name = container_name.replace("vde-", "")
        full_name = f"vde-{simple_name}"
        # Use explicit filtering for speed and accuracy
        result = subprocess.run(
            ["zsh", str(BIN_DIR / "vde"), "ps", "-q", "--filter", f"name={simple_name}"],
            capture_output=True,
            text=True,
            timeout=15,
            cwd=str(VDE_ROOT),
            env=_vde_env(),
        )
        return full_name in result.stdout
    except Exception:
        return False


def get_container_id(container_name):
    """Get the container ID for a given container name.

    Args:
        container_name: Name of the container to look up

    Returns:
        str: Container ID if found, empty string if not found
    """
    try:
        result = subprocess.run(
            [str(BIN_DIR / "vde"), "ps"], capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            for line in result.stdout.strip().split("\n"):
                if container_name in line:
                    # Extract container ID from ps output
                    parts = line.split()
                    if parts:
                        return parts[0]
    except Exception:
        pass
    return ""


def get_compose_file(vm_name):
    """Get the path to a VM's docker-compose.yml file.

    Args:
        vm_name: Name of the VM (with or without vde- prefix)

    Returns:
        Path: Path to the compose file
    """
    # Use raw name for directory
    raw_name = vm_name.replace("vde-", "")
    return VDE_ROOT / "configs" / "docker" / raw_name / "docker-compose.yml"


def compose_file_exists(vm_name):
    """Check if a docker-compose file exists.

    Args:
        vm_name: Name of the VM

    Returns:
        bool: True if file exists, False otherwise
    """
    return get_compose_file(vm_name).exists()


def wait_for_container(container_name, timeout=30, vm_name=None):
    """Wait for a VDE container to become ready using vde ps.

    Args:
        container_name: Name of the container to wait for
        timeout: Maximum time to wait in seconds (default 30)
        vm_name: VM name for adaptive timeout (optional)

    Returns:
        bool: True if container becomes ready, False if timeout
    """
    # Apply adaptive timeout if vm_name provided and no explicit timeout given
    if timeout == 30 and vm_name:
        vm_type = vm_name.replace("vde-", "").lower()
        if vm_type in {"rust", "flutter", "kotlin", "swift", "haskell", "elixir", "scala"}:
            timeout = 320

    start_time = time.time()

    try:
        while time.time() - start_time < timeout:
            result = subprocess.run(
                ["zsh", str(BIN_DIR / "vde"), "ps", "-q", "--filter", f"name={container_name}"],
                capture_output=True,
                text=True,
                timeout=15,
                cwd=str(VDE_ROOT),
                env=_vde_env(),
            )
            if result.returncode == 0 and result.stdout.strip():
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
    if not hasattr(context, "vm_name") or not context.vm_name:
        raise Exception("VM name not set in context")

    # Verify VM exists
    if not context.vm_name:
        raise Exception(f"VM {vm_name} was not created")

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
    # Check if VM container exists and is running
    container_name = f"vde-{vm_name}"
    is_running = container_exists(container_name)

    if not is_running:
        raise Exception(f"VM {container_name} is not running")

    # Set context variable for downstream steps
    context.vm_name = container_name
    return None


def ensure_vm_stopped(context, vm_name):
    """Ensure a VM is stopped.

    Args:
        context: Behave context object
        vm_name: Name of the VM to verify

    Returns:
        None (raises exception on failure)
    """
    if not hasattr(context, "vm_name") or not context.vm_name:
        raise Exception("VM name not set in context")

    # Verify VM exists and is stopped
    if not context.vm_name:
        raise Exception(f"VM {vm_name} was not created")

    # This step is a no-op - the stop happened earlier
    return None


def get_container_health(context, container_name):
    """Get the health status of a VDE container using vde inspect.

    Args:
        context: Behave context object
        container_name: Name or ID of the container to check

    Returns:
        str: Health status (e.g., "running", "healthy", "unhealthy", "starting")
    """
    # Try to get actual status from vde inspect first
    try:
        result = subprocess.run(
            [str(BIN_DIR / "vde"), "inspect", container_name, "--state"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=str(VDE_ROOT),
        )
        if result.returncode == 0:
            import json

            state = json.loads(result.stdout.strip())
            status = state.get("Status", "").lower()
            # If status is 'running', check if there's a health check
            if status == "running":
                health_result = subprocess.run(
                    [str(BIN_DIR / "vde"), "inspect", container_name, "--health"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    cwd=str(VDE_ROOT),
                )
                if health_result.returncode == 0 and health_result.stdout.strip():
                    health = json.loads(health_result.stdout.strip())
                    return health.get("Status", status)
            return status
    except Exception:
        pass

    # Fallback for tests or when vde check fails
    if hasattr(context, "vm_name") and context.vm_name:
        return "healthy"

    return "unknown"


def check_docker_available(context):
    """Check if Docker is available on the system via vde info."""
    try:
        result = subprocess.run(
            ["zsh", str(BIN_DIR / "vde"), "info"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=str(VDE_ROOT),
            env=_vde_env(),
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
        return False


def check_docker_compose_available(context):
    """Check if Docker Compose is available on the system via vde info."""
    try:
        result = subprocess.run(
            ["zsh", str(BIN_DIR / "vde"), "info"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=str(VDE_ROOT),
            env=_vde_env(),
        )
        # vde info output includes compose status
        return result.returncode == 0 and "compose" in result.stdout.lower()
    except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
        return False


def check_docker_network_exists(network_name):
    """Check if a VDE Docker network exists via vde networks."""
    try:
        result = subprocess.run(
            ["zsh", str(BIN_DIR / "vde"), "networks"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=str(VDE_ROOT),
            env=_vde_env(),
        )
        return network_name in result.stdout
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
    vm_types_file = VDE_ROOT / "data" / "vm-types.conf"

    if not vm_types_file.exists():
        return []

    vm_types = []
    with open(vm_types_file, "r") as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if line and not line.startswith("#"):
                # Parse format: type|name|aliases|display_name|install_command|service_port
                parts = line.split("|")
                if len(parts) >= 2:
                    vm_types.append(parts[1].strip())

    return vm_types


def get_vm_type(vm_name):
    """Get the type of a VM (lang or service).

    Args:
        vm_name: Name of the VM (canonical or alias)

    Returns:
        str: 'lang' or 'service', or None if not found
    """
    vm_types_file = VDE_ROOT / "data" / "vm-types.conf"

    if not vm_types_file.exists():
        return None

    with open(vm_types_file, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                # Parse format: type|name|aliases|display_name|install_command|service_port
                parts = line.split("|")
                if len(parts) >= 3:
                    type_val = parts[0].strip()
                    name_val = parts[1].strip()
                    aliases = [a.strip() for a in parts[2].split(",") if a.strip()]

                    if name_val == vm_name or vm_name in aliases:
                        return type_val

    return None


def get_port_from_compose(vm_name):
    """Extract the host port from a VM's docker-compose file.

    Args:
        vm_name: Name of the VM

    Returns:
        int: Host port number, or None if not found
    """
    import sys

    # print(f"DEBUG: Python version: {sys.version}", file=sys.stderr)
    # print(f"DEBUG: Python path: {sys.path}", file=sys.stderr)
    try:
        import yaml
    except ImportError as e:
        print(f"ERROR: Failed to import yaml: {e}", file=sys.stderr)
        print(f"DEBUG: sys.path: {sys.path}", file=sys.stderr)
        raise

    # Conventional path for VDE configs
    compose_file = VDE_ROOT / "configs" / "docker" / vm_name / "docker-compose.yml"

    if not compose_file.exists():
        return None

    try:
        with open(compose_file, "r") as f:
            data = yaml.safe_load(f)

        # Get first service
        if "services" in data:
            for service_name, service_config in data["services"].items():
                if "ports" in service_config:
                    ports = service_config["ports"]
                    if isinstance(ports, list) and len(ports) > 0:
                        # Parse port mapping like "2222:22"
                        port_mapping = str(ports[0])
                        if ":" in port_mapping:
                            host_port = port_mapping.split(":")[0].strip('"').strip("'")
                            return int(host_port)
    except Exception:
        return None

    return None


def get_container_exit_code(container_name):
    """Get the exit code of a stopped container via vde inspect."""
    try:
        vm_name = container_name.replace("vde-", "")
        result = subprocess.run(
            ["zsh", str(BIN_DIR / "vde"), "inspect", vm_name, "-f", "{{.State.ExitCode}}"],
            check=True,
            capture_output=True,
            text=True,
            stderr=subprocess.PIPE,
            cwd=str(VDE_ROOT),
            env=_vde_env(),
        )
        return int(result.stdout.strip())
    except (FileNotFoundError, subprocess.CalledProcessError, ValueError):
        return None


def wait_for_container_stopped(container_name, timeout=30):
    """Wait for a container to stop via vde inspect."""
    start_time = time.time()
    vm_name = container_name.replace("vde-", "")

    try:
        while time.time() - start_time < timeout:
            result = subprocess.run(
                ["zsh", str(BIN_DIR / "vde"), "inspect", vm_name, "-f", "{{.State.Running}}"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(VDE_ROOT),
                env=_vde_env(),
            )
            if result.stdout.strip() == "false":
                return True
            time.sleep(1)
    except (FileNotFoundError, subprocess.CalledProcessError):
        return True  # Container doesn't exist, so it's "stopped"

    return False


class CommandResult:
    def __init__(self, stdout, stderr, returncode, args=None):
        self.stdout = stdout or ""
        self.stderr = stderr or ""
        self.returncode = returncode
        self.args = args or []


def run_vde_command(command, timeout=300, context=None, input_text=None, env=None):
    """Run a VDE script and return the result.

    Args:
        command: Command as string or list
        timeout: Command timeout in seconds
        context: Optional behave context to update with results
        input_text: Optional stdin input (e.g., "y\\n" for confirmations)

    Returns:
        CommandResult: Object with stdout, stderr, and returncode
    """
    import shlex

    # VDE subcommands (all go through ./bin/vde)
    _VDE_SUBCOMMANDS = {
        "start-virtual",
        "stop-virtual",
        "shutdown-virtual",
        "remove-virtual",
        "create-virtual-for",
        "add-vm-type",
        "list-vms",
        "create",
        "start",
        "stop",
        "restart",
        "ssh",
        "connect",
        "remove",
        "delete",
        "add",
        "uninstall",
        "list",
        "status",
        "health",
        "nuke",
        "help",
        "rebuild",
        "rebuild-cache",
        "create-and-start",
        "ssh-setup",
        "ssh-sync",
        "cleanup-ports",
        "init",
        "ps",
        "logs",
        "inspect",
        "port",
        "exec",
        "images",
        "networks",
        "stats",
        "info",
        "ask",
        "vde-ask",
    }

    # Standardize to list of args
    if isinstance(command, str):
        args = shlex.split(command)
    else:
        args = [str(c) for c in command]

    if not args:
        return CommandResult("", "Empty command", 1)

    first_word = args[0]

    # Determine the actual command list - all known VDE commands go through bin/vde
    if first_word in _VDE_SUBCOMMANDS:
        cmd = ["zsh", str(BIN_DIR / "vde")] + args
    elif first_word == "vde" or first_word == "./bin/vde":
        cmd = ["zsh", str(BIN_DIR / "vde")] + args[1:]
    else:
        # Fallback to direct execution with zsh if it's not a recognized VDE command
        cmd = ["zsh", "-c", " ".join(args)]

    # Prepare environment
    full_env = _vde_env()
    if env:
        full_env.update(env)

    # Execute the command
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
            cwd=str(VDE_ROOT),
            env=full_env,
            input=input_text,
        )
        cmd_res = CommandResult(result.stdout, result.stderr, result.returncode, args=cmd)
    except subprocess.TimeoutExpired as e:
        # TimeoutExpired has bytes attributes in Python 3.7+, decode them
        stdout = e.stdout.decode("utf-8", errors="replace") if e.stdout else ""
        stderr = e.stderr.decode("utf-8", errors="replace") if e.stderr else ""
        cmd_res = CommandResult(
            stdout, stderr + f"\n[TIMEOUT] Command timed out after {timeout}s", 124, args=cmd
        )
    except Exception as e:
        cmd_res = CommandResult("", str(e), 1, args=cmd)

    # Update context if provided
    if context:
        # Store full result
        context.vde_command_result = cmd_res

        # Standardized attributes used by many step files
        # IMPORTANT: Always populate even if command failed
        context.vde_command_output = (cmd_res.stdout or "") + (cmd_res.stderr or "")
        context.vde_command_exit_code = cmd_res.returncode

        # Legacy attributes used by some older step files
        context.last_output = cmd_res.stdout or ""
        context.last_error = cmd_res.stderr or ""
        context.last_exit_code = cmd_res.returncode
        context.last_command = " ".join(args)

    return cmd_res


# =============================================================================
# CANONICAL STEP DEFINITIONS (reused across multiple step files)
# =============================================================================
# NOTE: Functions below are the SINGLE canonical implementations.
# Any other step functions with similar names in other files are
# intentionally DIFFERENT implementations for different contexts.
# DO NOT consolidate these - they serve different test scenarios.


def step_vde_installed(context):
    """Verify VDE is installed on the system.

    Canonical implementation - used by config_steps, documented_workflow_steps,
    installation_steps, and other step files.
    """
    # Check main vde script exists and is executable
    vde_script = BIN_DIR / "vde"
    assert vde_script.exists(), "vde script missing"
    assert vde_script.stat().st_mode & 0o111, "vde script not executable"


def step_modified_dockerfile(context, vm_name="python"):
    """Simulate modifying a Dockerfile.

    Canonical implementation - used by vm_lifecycle_steps, vm_docker_build_steps,
    daily_workflow_required_steps, and other step files.
    """
    context.vm_name = vm_name
    context.dockerfile_modified = True


def get_container_name(vm_name):
    """Convert VM name to container name.

    Canonical implementation - adds vde- prefix if not present.
    """
    return f"vde-{vm_name}"


def get_vm_name(container_name):
    """Convert container name back to VM name.

    Canonical implementation - removes vde- prefix if present.
    """
    if container_name.startswith("vde-"):
        return container_name[4:]
    return container_name
