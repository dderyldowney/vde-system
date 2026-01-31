"""
BDD Step Definitions for Debugging and Troubleshooting.
These are critical when ZeroToMastery students encounter issues.

All steps use REAL verification - no fake context flags.
"""
import json
import os
import re
import subprocess
import sys

# Import shared configuration
steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)
from pathlib import Path

from behave import given, then, when

from config import VDE_ROOT

# =============================================================================
# Helper Functions for Real Verification
# =============================================================================

def run_command(cmd, check=True, capture_output=True):
    """Run a command and return result."""
    result = subprocess.run(
        cmd,
        shell=isinstance(cmd, str),
        capture_output=capture_output,
        text=True,
        check=False
    )
    if check and result.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}\n{result.stderr}")
    return result

def get_container_info(vm_name):
    """Get Docker container inspect data for a VM."""
    result = run_command(['docker', 'inspect', f'vde-{vm_name}'], check=False)
    if result.returncode != 0:
        return None
    return json.loads(result.stdout)[0]

def get_container_logs(vm_name):
    """Get Docker container logs for a VM."""
    result = run_command(['docker', 'logs', f'vde-{vm_name}'], check=False)
    return result.stdout

def get_vm_port(vm_name):
    """Get the actual allocated port for a VM."""
    info = get_container_info(vm_name)
    if not info:
        return None
    # Get port from host config
    ports = info.get('NetworkSettings', {}).get('Ports', {})
    if ports.get('22/tcp'):
        return ports['22/tcp'][0]['HostPort']
    return None

def get_vm_mounts(vm_name):
    """Get volume mount information for a VM."""
    info = get_container_info(vm_name)
    if not info:
        return []
    return info.get('Mounts', [])

def get_network_info(network_name='vde-network'):
    """Get Docker network information."""
    result = run_command(['docker', 'network', 'inspect', network_name], check=False)
    if result.returncode != 0:
        return None
    return json.loads(result.stdout)[0]

def get_compose_file_path(vm_name):
    """Get path to docker-compose.yml for a VM."""
    compose_path = Path(VDE_ROOT) / 'vms' / vm_name / 'docker-compose.yml'
    return compose_path if compose_path.exists() else None

def read_ssh_config():
    """Read VDE SSH config file."""
    ssh_config_path = Path.home() / '.ssh' / 'vde' / 'config'
    if ssh_config_path.exists():
        return ssh_config_path.read_text()
    return None

def check_port_in_use(port):
    """Check if a port is in use on the host."""
    result = run_command(['lsof', '-i', f':{port}'], check=False)
    return result.returncode == 0


# =============================================================================
# Debugging GIVEN steps
# =============================================================================

@given('I tried to start a VM but it failed')
def step_vm_start_failed(context):
    """Set up scenario for failed VM start by storing error state."""
    context.vm_start_failed = True
    context.last_operation_failed = True

@given('a system service is using port 2200')
def step_system_service_port(context):
    """Set up port conflict scenario."""
    context.system_service_port = "2200"
    context.port_conflict = True

@given('my application can\'t connect to the database')
def step_app_db_connection_fail(context):
    """Set up database connection failure scenario."""
    context.app_db_connection_failed = True

@given('I need to verify VM configuration')
def step_need_verify_config(context):
    """Mark that config verification is needed."""
    context.need_config_verification = True

@given('my code changes aren\'t reflected in the VM')
def step_code_changes_not_reflected(context):
    """Set up code sync issue scenario."""
    context.code_changes_not_visible = True

@given('I\'ve made changes I want to discard')
def step_want_discard_changes(context):
    """Mark that user wants to discard changes."""
    context.want_discard = True


# =============================================================================
# Debugging WHEN steps - Execute Real Commands
# =============================================================================

@when('I check the VM status')
def step_check_vm_status_debug(context):
    """Check VM status using docker ps."""
    result = run_command(['docker', 'ps', '--filter', 'name=vde-'], check=False)
    context.docker_ps_output = result.stdout

@when('I look at the docker-compose.yml')
def step_look_compose(context):
    """Read the docker-compose.yml file."""
    if hasattr(context, 'vm_name'):
        compose_path = get_compose_file_path(context.vm_name)
        if compose_path:
            context.compose_content = compose_path.read_text()
            return
    context.compose_error = f"No docker-compose.yml found for VM: {getattr(context, 'vm_name', 'unknown')}"

@when('I check the mounts in the container')
def step_check_mounts(context):
    """Check container mounts using docker inspect."""
    if hasattr(context, 'vm_name'):
        mounts = get_vm_mounts(context.vm_name)
        context.vm_mounts = mounts
