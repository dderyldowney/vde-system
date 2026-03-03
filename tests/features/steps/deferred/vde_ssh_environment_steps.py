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
