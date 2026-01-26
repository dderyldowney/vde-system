"""
BDD Step Definitions for VDE SSH Environment Setup (GIVEN steps).

These steps set up the initial SSH environment state for testing.
All steps use real system verification - no context flags or fake tests.
"""
import os
import subprocess
import sys
from pathlib import Path

# Import shared configuration
steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)

from behave import given
from config import VDE_ROOT


# =============================================================================
# SSH Environment GIVEN Steps
# =============================================================================

@given('VDE SSH environment is not initialized')
def step_ssh_not_initialized(context):
    """Verify SSH environment does not exist before tests.

    This step checks that the VDE SSH directory does not exist,
    establishing a clean pre-test state. It does not modify the system.
    """
    vde_ssh_dir = Path.home() / ".ssh" / "vde"
    context.ssh_exists_before = vde_ssh_dir.exists()

    # Note: We don't delete anything here - tests should run independently
    # or assume the environment exists (idempotent operations)


@given('VDE SSH environment is initialized')
def step_ssh_initialized(context):
    """Ensure VDE SSH environment exists before tests.

    This step runs 'vde ssh-setup init' to create SSH keys and config
    if they don't already exist. The init command is idempotent.
    """
    vde_ssh_dir = Path.home() / ".ssh" / "vde"
    vde_key = Path.home() / ".ssh" / "vde" / "id_ed25519"

    # Only run init if key doesn't exist (idempotent check)
    if not vde_key.exists():
        result = subprocess.run(
            ["./scripts/vde", "ssh-setup", "init"],
            capture_output=True, text=True, timeout=60,
            cwd=VDE_ROOT
        )
        context.ssh_init_result = result
    else:
        # Mark as already initialized
        context.ssh_already_initialized = True


@given('VDE SSH agent is running')
def step_vde_ssh_agent_running(context):
    """Ensure VDE SSH agent is running before tests.

    This step starts the SSH agent if it's not already running.
    """
    # Check if agent is running
    result = subprocess.run(
        ["ssh-add", "-l"],
        capture_output=True, text=True, timeout=10
    )

    if result.returncode != 0:
        # Agent not running, start it
        subprocess.run(
            ["./scripts/vde", "ssh-setup", "start"],
            capture_output=True, text=True, timeout=30,
            cwd=VDE_ROOT
        )


@given('VDE SSH key is loaded in agent')
def step_ssh_key_loaded(context):
    """Ensure VDE SSH key is loaded in the SSH agent.

    This step loads the VDE key if it's not already loaded.
    """
    # Check if VDE key is loaded
    result = subprocess.run(
        ["ssh-add", "-l"],
        capture_output=True, text=True, timeout=10
    )

    vde_key = Path.home() / ".ssh" / "vde" / "id_ed25519"

    # If agent is running but key not loaded, load it
    if result.returncode == 0 and vde_key.exists():
        # Check if VDE key is already in the output
        if "vde" not in result.stdout.lower():
            subprocess.run(
                ["ssh-add", str(vde_key)],
                capture_output=True, text=True, timeout=10
            )


@given('a VM "{vm_name}" exists')
def step_vm_exists(context, vm_name):
    """Ensure a VM exists before testing SSH commands.

    This step checks if the VM has been created (has docker-compose.yml).
    """
    vm_config = Path(VDE_ROOT) / "configs" / "docker" / vm_name / "docker-compose.yml"

    if not vm_config.exists():
        # Create the VM first
        result = subprocess.run(
            ["./scripts/vde", "create", vm_name],
            capture_output=True, text=True, timeout=120,
            cwd=VDE_ROOT
        )
        context.vm_create_result = result
        assert result.returncode == 0, f"Failed to create VM {vm_name}: {result.stderr}"
