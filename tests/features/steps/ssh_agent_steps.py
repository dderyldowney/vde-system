"""
BDD Step definitions for SSH Agent and Key Management scenarios.

These steps test SSH agent lifecycle, key generation, and automatic setup.
All steps use real system verification instead of mock context variables.
"""
import os
import subprocess

# Import shared configuration
import sys
import time
from pathlib import Path

steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)
from behave import given, then, when

# Import SSH helpers
from ssh_helpers import (
    ALLOW_CLEANUP,
    container_exists,
    get_ssh_keys,
    has_ssh_keys,
    run_vde_command,
    ssh_agent_has_keys,
    ssh_agent_is_running,
)

from config import VDE_ROOT

# Add parent directory to path for vde_test_helpers
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import VDE test helpers (run_vde_command and container_exists now from ssh_helpers)
from vde_test_helpers import (
    compose_file_exists,
    create_vm,
    docker_ps,
    file_exists,
    start_vm,
    stop_vm,
    wait_for_container,
)


# =============================================================================
# GIVEN steps - Setup with REAL operations
# =============================================================================



@given('SSH keys are available')
def step_ssh_keys_available(context):
    """SSH keys exist for the user."""
    ssh_dir = Path.home() / ".ssh"
    context.ssh_keys_exist = (
        (ssh_dir / "id_ed25519").exists() or
        (ssh_dir / "id_rsa").exists() or
        (ssh_dir / "id_ecdsa").exists()
    )




@given('SSH config file exists')
def step_ssh_config_exists(context):
    """SSH config file exists."""
    ssh_config = Path.home() / ".ssh" / "config"
    context.ssh_config_existed = ssh_config.exists()


@given('SSH config file does not exist')
def step_no_ssh_config(context):
    """SSH config file doesn't exist."""
    ssh_config = Path.home() / ".ssh" / "config"
    context.ssh_config_existed = not ssh_config.exists()


@given('SSH config contains entry for "{host}"')
def step_ssh_has_entry(context, host):
    """SSH config has existing entry."""
    ssh_config = Path.home() / ".ssh" / "config"
    if ssh_config.exists():
        content = ssh_config.read_text()
        context.ssh_entry_exists = host in content
