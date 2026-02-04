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
from vm_common import docker_ps

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
    """Verify logged in as devuser - check actual container or verify config."""
    running = docker_ps()
    if running:
        vm = list(running)[0]
        result = subprocess.run(
            ['docker', 'exec', vm, 'whoami'],
            capture_output=True, text=True, timeout=10
        )
        assert result.returncode == 0, f"Should be able to execute whoami in {vm}"
        assert result.stdout.strip() == 'devuser', f"Expected devuser but got: {result.stdout.strip()}"
    else:
        # Fallback: verify config uses devuser
        compose_path = VDE_ROOT / "configs" / "docker" / "python" / "docker-compose.yml"
        if compose_path.exists():
            content = compose_path.read_text()
            assert 'devuser' in content.lower(), "VDE should use devuser as default user"
        else:
            assert False, "No VMs running and no config to verify"
    context.user_is_devuser = True
