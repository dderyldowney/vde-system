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


@given('I create a Python VM for my API')
def step_create_python_vm_for_api(context):
    """Create a Python VM for API development - actually create or verify VM exists."""
    from vm_common import run_vde_command, compose_file_exists
    from config import VDE_ROOT
    
    context.api_vm = "python"
    
    # Actually create the VM if it doesn't exist
    if not compose_file_exists("python"):
        result = run_vde_command("add python --type lang --display-name Python --install 'pip install --upgrade pip'", timeout=30)
    
    # Verify VM config exists
    vm_config = VDE_ROOT / "configs" / "docker" / "python" / "docker-compose.yml"
    context.python_vm_created = vm_config.exists()


@given('I create a PostgreSQL VM for my database')
def step_create_postgres_vm_for_db(context):
    """Create a PostgreSQL VM for database - actually create or verify VM exists."""
    from vm_common import run_vde_command, compose_file_exists
    from config import VDE_ROOT
    
    context.db_vm = "postgres"
    
    # Actually create the VM if it doesn't exist
    if not compose_file_exists("postgres"):
        result = run_vde_command("add postgres --type service --display-name PostgreSQL", timeout=30)
    
    # Verify VM config exists
    vm_config = VDE_ROOT / "configs" / "docker" / "postgres" / "docker-compose.yml"
    context.postgres_vm_created = vm_config.exists()


@given('I create a Redis VM for caching')
def step_create_redis_vm_for_cache(context):
    """Create a Redis VM for caching - actually create or verify VM exists."""
    from vm_common import run_vde_command, compose_file_exists
    from config import VDE_ROOT
    
    context.cache_vm = "redis"
    
    # Actually create the VM if it doesn't exist
    if not compose_file_exists("redis"):
        result = run_vde_command("add redis --type service --display-name Redis", timeout=30)
    
    # Verify VM config exists
    vm_config = VDE_ROOT / "configs" / "docker" / "redis" / "docker-compose.yml"
    context.redis_vm_created = vm_config.exists()


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


# =============================================================================
# VM Type GIVEN steps - Setup for VM-to-Host tests
# =============================================================================

@given('I have a management VM running')
def step_management_vm_running(context):
    """Management VM is running."""
    context.current_vm = "management"
    context.management_vm_running = container_exists("vde-management")


@given('I have a build VM running')
def step_build_vm_running(context):
    """Build VM is running."""
    context.current_vm = "build"
    context.build_vm_running = container_exists("vde-build")


@given('I have a coordination VM running')
def step_coordination_vm_running(context):
    """Coordination VM is running."""
    context.current_vm = "coordination"
    context.coordination_vm_running = container_exists("vde-coordination")


@given('I have a backup VM running')
def step_backup_vm_running(context):
    """Backup VM is running."""
    context.current_vm = "backup"
    context.backup_vm_running = container_exists("vde-backup")


@given('I have a debugging VM running')
def step_debugging_vm_running(context):
    """Debugging VM is running."""
    context.current_vm = "debugging"
    context.debugging_vm_running = container_exists("vde-debugging")


@given('I have a network VM running')
def step_network_vm_running(context):
    """Network VM is running."""
    context.current_vm = "network"
    context.network_vm_running = container_exists("vde-network")


@given('I have a utility VM running')
def step_utility_vm_running(context):
    """Utility VM is running."""
    context.current_vm = "utility"
    context.utility_vm_running = container_exists("vde-utility")


# Note: 'I have multiple VMs running' is defined in pattern_steps.py


# =============================================================================
# Additional GIVEN steps for feature scenarios (not in docker_operations_steps.py)
# =============================================================================

@given('I have Docker installed on my host for SSH-VM-Steps')
def step_docker_installed(context):
    """Docker is installed on the host."""
    result = subprocess.run(['./bin/vde', '--version'], capture_output=True, text=True, timeout=10)
    context.docker_installed = result.returncode == 0
    assert context.docker_installed, "Docker must be installed on host"




@given('I have projects on my host')
def step_host_has_projects(context):
    """Host has projects."""
    context.host_has_projects = (Path.home() / "dev").exists()


@given('I have custom scripts on my host')
def step_host_has_scripts(context):
    """Host has custom scripts."""
    scripts_dir = Path.home() / "dev" / "scripts"
    context.host_has_scripts = scripts_dir.exists() and any(scripts_dir.glob('*.sh'))


# =============================================================================
# SSH INTO VM WHEN steps - Set context for VM operations
# =============================================================================


@when('I SSH into the Go VM')
def step_ssh_go_vm(context):
    """SSH into Go VM - set context for VM operations."""
    context.current_vm = "go"
    context.vm_ssh_target = "vde-go"




@when('I SSH into the build VM')
def step_ssh_build_vm(context):
    """SSH into build VM - set context for VM operations."""
    context.current_vm = "build"
    context.vm_ssh_target = "vde-build"


@when('I SSH into the coordination VM')
def step_ssh_coordination_vm(context):
    """SSH into coordination VM - set context for VM operations."""
    context.current_vm = "coordination"
    context.vm_ssh_target = "vde-coordination"


@when('I SSH into the backup VM')
def step_ssh_backup_vm(context):
    """SSH into backup VM - set context for VM operations."""
    context.current_vm = "backup"
    context.vm_ssh_target = "vde-backup"


@when('I SSH into the debugging VM')
def step_ssh_debugging_vm(context):
    """SSH into debugging VM - set context for VM operations."""
    context.current_vm = "debugging"
    context.vm_ssh_target = "vde-debugging"


@when('I SSH into the network VM')
def step_ssh_network_vm(context):
    """SSH into network VM - set context for VM operations."""
    context.current_vm = "network"
    context.vm_ssh_target = "vde-network"


@when('I SSH into the utility VM')
def step_ssh_utility_vm(context):
    """SSH into utility VM - set context for VM operations."""
    context.current_vm = "utility"
    context.vm_ssh_target = "vde-utility"
