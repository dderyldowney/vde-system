"""
BDD Step Definitions for User Workflow and Environment Scenarios.

These steps verify user environment, permissions, editor configs, and workflows.
"""
import subprocess
import sys

# Import shared configuration
steps_dir = sys.path.insert(0, steps_dir) if (steps_dir := __import__('os').path.dirname(__import__('os').path.abspath(__file__))) not in sys.path else None
from pathlib import Path

from behave import given, then

from config import VDE_ROOT
from ssh_helpers import container_exists
from vm_common import docker_list_containers

# =============================================================================
# SSH CONNECTION CONTEXT GIVEN steps
# =============================================================================

@given('I have the SSH connection details')
def step_have_ssh_connection_details(context):
    """Context: User has SSH connection details."""
    context.ssh_details_available = True
    # Verify SSH config exists
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    context.ssh_config_exists = ssh_config.exists()


# =============================================================================
# USER ENVIRONMENT THEN steps
# =============================================================================

@then('I should be logged in as devuser')
def step_logged_in_devuser(context):
    """Verify logged in as devuser via SSH."""
    # Use context.last_ssh_host if available, otherwise default to vde-python
    ssh_host = getattr(context, 'last_ssh_host', 'vde-python')
    
    # Use the isolated VDE SSH config
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    
    # Use SSH to connect and run whoami as devuser
    cmd = ['ssh']
    if ssh_config.exists():
        cmd.extend(['-F', str(ssh_config)])
        
    cmd.extend([
        '-o', 'StrictHostKeyChecking=no', 
        '-o', 'UserKnownHostsFile=/dev/null',
        '-o', 'BatchMode=yes',
        ssh_host, 'whoami'
    ])
    
    print(f"DEBUG: Executing SSH command: {' '.join(cmd)}")
    result = subprocess.run(
        cmd,
        capture_output=True, text=True, timeout=30
    )
    print(f"DEBUG: SSH result RC={result.returncode}")
    if result.returncode != 0:
        print(f"DEBUG: SSH error: {result.stderr}")
        # Fallback to python-dev if vde-python failed and wasn't explicitly requested
        if ssh_host == 'vde-python' and not hasattr(context, 'last_ssh_host'):
             # Try python-dev as fallback
             cmd[-2] = 'python-dev'
             result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    assert result.returncode == 0, f"SSH connection failed to {ssh_host}: {result.stderr}"
    assert result.stdout.strip() == 'devuser', f"Expected devuser but got: {result.stdout.strip()}"
    context.user_is_devuser = True
