"""
BDD Step Definitions for SSH Configuration Verification.

These steps verify SSH configuration for VM access.
"""
import os
import subprocess
import sys

# Import shared configuration
steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)
from pathlib import Path

from behave import given, then

from config import VDE_ROOT
from vm_common import docker_ps

# =============================================================================
# SSH CONFIGURATION GIVEN steps
# =============================================================================

@given('~/.ssh/config does not exist')
def step_no_ssh_config(context):
    """VDE SSH config doesn't exist."""
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    context.ssh_config_exists = ssh_config.exists()


@given('~/.ssh/config exists')
def step_ssh_config_exists_step(context):
    """VDE SSH config exists."""
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    context.ssh_config_exists = ssh_config.exists()


@given('~/.ssh/config exists with custom settings')
def step_ssh_custom(context):
    """VDE SSH config with custom settings."""
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    context.ssh_config_exists = ssh_config.exists()
    if ssh_config.exists():
        content = ssh_config.read_text()
        context.ssh_has_custom_settings = len(content) > 0


@given('~/.ssh/config contains python-dev configuration')
def step_python_config(context):
    """VDE SSH config has python configuration."""
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    if ssh_config.exists():
        content = ssh_config.read_text()
        context.has_python_config = "python" in content.lower()
