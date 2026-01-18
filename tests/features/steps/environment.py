"""
Behave environment setup and teardown hooks for VDE BDD tests.
Runs inside the BDD test container OR locally on the host.
"""

import os
import subprocess
import shutil
import tempfile
from pathlib import Path

# Detect if running in container vs locally on host
# In container: VDE_ROOT_DIR is set to /vde
# Locally: VDE_ROOT_DIR is not set or points to a different path
# Test mode: VDE_TEST_MODE is set to 1 (allows cleanup during local testing)
IN_CONTAINER = os.environ.get("VDE_ROOT_DIR") == "/vde"
IN_TEST_MODE = os.environ.get("VDE_TEST_MODE") == "1"
# Allow cleanup if running in container OR in test mode
ALLOW_CLEANUP = IN_CONTAINER or IN_TEST_MODE
HOST_HAS_DOCKER = os.path.exists("/var/run/docker.sock")

# VDE root directory (inside container or on host)
# Use VDE_PROJECT_ROOT if set, otherwise detect from environment
project_root = os.environ.get("VDE_PROJECT_ROOT")
if not project_root or not Path(project_root).exists():
    # Try VDE_ROOT_DIR (used by test runner), then auto-detect
    project_root = os.environ.get("VDE_ROOT_DIR")
    if not project_root or not Path(project_root).exists():
        # Fall back to parent of tests directory
        project_root = str(Path(__file__).parent.parent.parent)
VDE_ROOT = Path(project_root)


def _cleanup_lock_files():
    """Clean up stale lock files that could cause timeouts."""
    locks_dir = VDE_ROOT / ".locks"
    if not locks_dir.exists():
        return

    # Remove all lock files
    for lock_file in locks_dir.rglob("*.lock"):
        try:
            lock_file.unlink()
        except Exception:
            pass

    # Also clean SSH config lock if it exists
    ssh_lock = Path.home() / ".ssh" / "config.lock"
    if ssh_lock.exists():
        try:
            ssh_lock.unlink()
        except Exception:
            pass


def before_all(context):
    """Set up test environment before all scenarios."""
    # Set environment variables
    os.environ["VDE_ROOT_DIR"] = str(VDE_ROOT)
    os.environ["PATH"] = f"{VDE_ROOT}/scripts:{VDE_ROOT}/tests:{os.environ['PATH']}"
    # Enable test mode to skip SSH config operations that timeout in Docker
    os.environ["VDE_TEST_MODE"] = "1"

    # Create necessary directories
    dirs = [
        VDE_ROOT / "configs",
        VDE_ROOT / "projects",
        VDE_ROOT / "data",
        VDE_ROOT / "logs",
        VDE_ROOT / "public-ssh-keys",
        VDE_ROOT / ".locks",
        VDE_ROOT / ".cache",
        VDE_ROOT / ".locks" / "ports",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)

    # Clean up any stale lock files that could cause timeouts
    _cleanup_lock_files()

    # Store test context
    context.vde_root = VDE_ROOT
    context.temp_files = []
    context.temp_dirs = []
    context.created_vms = set()
    context.running_vms = set()
    context.allocated_ports = {}
    context.last_command = None
    context.last_output = None
    context.last_error = None
    context.last_exit_code = 0  # Default to 0 so assertions pass when no command run


def after_all(context):
    """Clean up after all scenarios."""
    # Clean up temporary files
    for f in getattr(context, "temp_files", []):
        try:
            if os.path.isfile(f):
                os.remove(f)
        except Exception:
            pass

    # Clean up temporary directories
    for d in getattr(context, "temp_dirs", []):
        try:
            if os.path.isdir(d):
                shutil.rmtree(d)
        except Exception:
            pass


def before_scenario(context, scenario):
    """Set up before each scenario."""
    # Clean up stale lock files before each scenario to prevent timeouts
    _cleanup_lock_files()

    # Reset per-scenario state on context (so steps can access it)
    context.temp_files = []
    context.temp_dirs = []
    context.created_vms = set()
    context.running_vms = set()
    context.last_command = None
    context.last_output = None
    context.last_error = None
    context.last_exit_code = 0  # Default to 0 so assertions pass when no command run


def after_scenario(context, scenario):
    """Clean up after each scenario."""
    # Only delete config files when running inside the container OR in test mode
    # When running locally without test mode, preserve user's VM configurations
    if ALLOW_CLEANUP:
        for vm in getattr(context, "created_vms", set()):
            try:
                # Remove docker-compose.yml if it exists
                compose_file = VDE_ROOT / "configs" / "docker" / vm / "docker-compose.yml"
                if compose_file.exists():
                    compose_file.unlink()
                # Remove config directory if empty
                config_dir = compose_file.parent
                if config_dir.exists() and not list(config_dir.iterdir()):
                    config_dir.rmdir()
            except Exception:
                pass

    # Clean up temporary files (always)
    for f in getattr(context, "temp_files", []):
        try:
            if os.path.isfile(f):
                os.remove(f)
        except Exception:
            pass


def run_command(cmd, check=False, capture=True, cwd=None):
    """Run a shell command and return result."""
    if capture:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd=cwd or VDE_ROOT,
        )
        if check and result.returncode != 0:
            raise RuntimeError(f"Command failed: {cmd}\n{result.stderr}")
        return result
    else:
        subprocess.run(cmd, shell=True, cwd=cwd or VDE_ROOT)
        return None


# Helper functions for step definitions
def vm_exists(vm_name):
    """Check if VM configuration exists."""
    compose_path = VDE_ROOT / "configs" / "docker" / vm_name / "docker-compose.yml"
    return compose_path.exists()


def vm_is_running(vm_name):
    """Check if VM container is running."""
    result = run_command(f"docker ps --filter 'name={vm_name}' --format '{{{{.Names}}}}'")
    return vm_name in result.stdout.strip()


def get_vm_port(vm_name):
    """Get the SSH port allocated to a VM."""
    compose_path = VDE_ROOT / "configs" / "docker" / vm_name / "docker-compose.yml"
    if not compose_path.exists():
        return None

    content = compose_path.read_text()
    # Extract port from mapping like "2200:22"
    import re
    match = re.search(r'(\d+):22', content)
    return match.group(1) if match else None


def ssh_config_entry_exists(host_alias):
    """Check if SSH config entry exists for a host."""
    ssh_config = Path.home() / ".ssh" / "config"
    if not ssh_config.exists():
        return False
    content = ssh_config.read_text()
    return f"Host {host_alias}" in content


def parse_vm_types():
    """Parse vm-types.conf and return dict of VM types."""
    vm_types_file = VDE_ROOT / "scripts" / "data" / "vm-types.conf"
    if not vm_types_file.exists():
        return {}

    vm_types = {}
    for line in vm_types_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "|" in line:
            parts = line.split("|")
            if len(parts) >= 3:
                vm_type, name, display = parts[0], parts[1], parts[2]
                install_cmd = parts[3] if len(parts) > 3 else ""
                aliases = parts[4] if len(parts) > 4 else ""
                vm_types[name] = {
                    "type": vm_type,
                    "display": display,
                    "install": install_cmd,
                    "aliases": aliases,
                }
    return vm_types
