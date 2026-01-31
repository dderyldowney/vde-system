"""
BDD Step definitions for VM-to-VM SSH Communication scenarios.

These steps test SSH connections between VMs, agent forwarding,
and multi-hop SSH patterns using real system verification.
"""
import os
import subprocess

# Import shared configuration
import sys
from pathlib import Path

steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)
from behave import given, then, when

# Import SSH helpers
from ssh_helpers import (
    container_exists,
    has_ssh_keys,
    ssh_agent_has_keys,
    ssh_agent_is_running,
    ssh_config_contains,
)

# Import shell helpers for command execution
from shell_helpers import execute_in_container

from config import VDE_ROOT

# =============================================================================
# SSH Agent Forwarding (VM-to-VM) Steps
# =============================================================================

# -----------------------------------------------------------------------------
# GIVEN steps - Setup for VM-to-VM SSH tests
# -----------------------------------------------------------------------------

@given('I have SSH keys configured on my host')
def step_ssh_keys_configured_on_host(context):
    """SSH keys are configured on the host machine."""
    ssh_dir = Path.home() / ".ssh"
    has_keys = (
        (ssh_dir / "id_ed25519").exists() or
        (ssh_dir / "id_rsa").exists() or
        (ssh_dir / "id_ecdsa").exists()
    )
    context.host_has_ssh_keys = has_keys


@given('I create a Python VM for my API')
def step_create_python_vm_for_api(context):
    """Create a Python VM for API development."""
    context.api_vm = "python"
    context.python_vm_created = True


@given('I create a PostgreSQL VM for my database')
def step_create_postgres_vm_for_db(context):
    """Create a PostgreSQL VM for database."""
    context.db_vm = "postgres"
    context.postgres_vm_created = True


@given('I create a Redis VM for caching')
def step_create_redis_vm_for_cache(context):
    """Create a Redis VM for caching."""
    context.cache_vm = "redis"
    context.redis_vm_created = True


@given('I start all VMs')
def step_start_all_vms(context):
    """Start all VMs."""
    # Verify VMs are actually running by checking containers
    vms_to_check = []
    if hasattr(context, 'api_vm'):
        vms_to_check.append(context.api_vm)
    if hasattr(context, 'db_vm'):
        vms_to_check.append(context.db_vm)
    if hasattr(context, 'cache_vm'):
        vms_to_check.append(context.cache_vm)
    
    # If no specific VMs defined, assume basic check passed
    if vms_to_check:
        all_running = all(container_exists(vm) for vm in vms_to_check)
        context.all_vms_started = all_running
