"""
BDD Step Definitions for User Workflow and Environment Scenarios.

These steps verify user environment, permissions, editor configs, and workflows.
"""
import subprocess
import sys
import os
from pathlib import Path

# Add steps directory to path for imports
steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)

from behave import given, then

from config import VDE_ROOT
from vm_common import run_vde_command, container_exists, docker_ps

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
    """Verify logged in as devuser via vde exec."""
    # Use context.last_ssh_host if available, otherwise default to python
    vm_name = getattr(context, 'last_ssh_host', 'python').replace('vde-', '')
    
    # Use vde exec to run whoami
    result = run_vde_command(f"exec {vm_name} whoami", context=context)
    
    assert result.returncode == 0, f"vde exec failed for {vm_name}: {result.stderr}"
    assert result.stdout.strip() == 'devuser', f"Expected devuser but got: {result.stdout.strip()}"
    context.user_is_devuser = True
