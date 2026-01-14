"""
Behave environment setup and teardown hooks for VDE BDD tests.
Runs inside the BDD test container.
"""

import os
import subprocess
import shutil
import tempfile
from pathlib import Path

# VDE root directory (inside container)
VDE_ROOT = Path("/vde")


def before_all(context):
    """Set up test environment before all scenarios."""
    # Set environment variables
    os.environ["VDE_ROOT_DIR"] = str(VDE_ROOT)
    os.environ["PATH"] = f"{VDE_ROOT}/scripts:{VDE_ROOT}/tests:{os.environ['PATH']}"

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

    # Store test context
    context.vde_root = VDE_ROOT
    context.temp_files = []
    context.temp_dirs = []
    context.created_vms = set()
    context.running_vms = set()
    context.allocated_ports = {}


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
    # Reset per-scenario state on context (so steps can access it)
    context.temp_files = []
    context.temp_dirs = []
    context.created_vms = set()
    context.running_vms = set()
    context.last_command = None
    context.last_output = None
    context.last_error = None


def after_scenario(context, scenario):
    """Clean up after each scenario."""
    # Clean up any test VMs that were created
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

    # Clean up temporary files
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
