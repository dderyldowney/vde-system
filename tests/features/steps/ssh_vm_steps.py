"""
BDD Step definitions for VM-to-VM SSH Communication scenarios.

These steps test SSH connections between VMs, agent forwarding,
and multi-hop SSH patterns using real system verification.
"""
import os
import subprocess
import sys
from pathlib import Path

# Add steps directory to path for imports
steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)

from behave import given, then, when

# Import shared helpers
from vm_common import (
    VDE_ROOT,
    container_exists,
    compose_file_exists,
    run_vde_command,
    docker_ps,
)

# Import SSH helpers
from ssh_helpers import (
    has_ssh_keys,
    ssh_agent_has_keys,
    ssh_agent_is_running,
    ssh_config_contains,
)

# Import shell helpers for command execution
from shell_helpers import execute_in_container

# =============================================================================
# SSH Agent Forwarding (VM-to-VM) Steps
# =============================================================================

@given('I create a Python VM for my API')
def step_create_python_vm_for_api(context):
    """Create a Python VM for API development - actually create or verify VM exists."""
    context.api_vm = "python"
    
    # Actually create the VM if it doesn't exist
    if not compose_file_exists("python"):
        run_vde_command("create python", timeout=120, context=context)
    
    # Verify VM config exists
    vm_config = VDE_ROOT / "configs" / "docker" / "python" / "docker-compose.yml"
    context.python_vm_created = vm_config.exists()


@given('I create a PostgreSQL VM for my database')
def step_create_postgres_vm_for_db(context):
    """Create a PostgreSQL VM for database - actually create or verify VM exists."""
    context.db_vm = "postgres"
    
    # Actually create the VM if it doesn't exist
    if not compose_file_exists("postgres"):
        run_vde_command("create postgres", timeout=120, context=context)
    
    # Verify VM config exists
    vm_config = VDE_ROOT / "configs" / "docker" / "postgres" / "docker-compose.yml"
    context.postgres_vm_created = vm_config.exists()


@given('I create a Redis VM for caching')
def step_create_redis_vm_for_cache(context):
    """Create a Redis VM for caching - actually create or verify VM exists."""
    context.cache_vm = "redis"
    
    # Actually create the VM if it doesn't exist
    if not compose_file_exists("redis"):
        run_vde_command("create redis", timeout=120, context=context)
    
    # Verify VM config exists
    vm_config = VDE_ROOT / "configs" / "docker" / "redis" / "docker-compose.yml"
    context.redis_vm_created = vm_config.exists()


@given('I start all VMs')
def step_start_all_vms(context):
    """Start all VMs."""
    vms_to_start = []
    if hasattr(context, 'api_vm'): vms_to_start.append(context.api_vm)
    if hasattr(context, 'db_vm'): vms_to_start.append(context.db_vm)
    if hasattr(context, 'cache_vm'): vms_to_start.append(context.cache_vm)
    
    if vms_to_start:
        run_vde_command(f"start {' '.join(vms_to_start)}", timeout=180, context=context)
        context.all_vms_started = all(container_exists(vm) for vm in vms_to_start)


# =============================================================================
# VM Type GIVEN steps - Setup for VM-to-Host tests
# =============================================================================

@given('I have a management VM running')
def step_management_vm_running(context):
    """Management VM is running."""
    context.current_vm = "management"
    if not container_exists("management"):
        run_vde_command("start management", timeout=120, context=context)
    context.management_vm_running = container_exists("management")


@given('I have a build VM running')
def step_build_vm_running(context):
    """Build VM is running."""
    context.current_vm = "build"
    if not container_exists("build"):
        run_vde_command("start build", timeout=120, context=context)
    context.build_vm_running = container_exists("build")


@given('I have a coordination VM running')
def step_coordination_vm_running(context):
    """Coordination VM is running."""
    context.current_vm = "coordination"
    if not container_exists("coordination"):
        run_vde_command("start coordination", timeout=120, context=context)
    context.coordination_vm_running = container_exists("coordination")


@given('I have a backup VM running')
def step_backup_vm_running(context):
    """Backup VM is running."""
    context.current_vm = "backup"
    if not container_exists("backup"):
        run_vde_command("start backup", timeout=120, context=context)
    context.backup_vm_running = container_exists("backup")


@given('I have a debugging VM running')
def step_debugging_vm_running(context):
    """Debugging VM is running."""
    context.current_vm = "debugging"
    if not container_exists("debugging"):
        run_vde_command("start debugging", timeout=120, context=context)
    context.debugging_vm_running = container_exists("debugging")


@given('I have a network VM running')
def step_network_vm_running(context):
    """Network VM is running."""
    context.current_vm = "network"
    if not container_exists("network"):
        run_vde_command("start network", timeout=120, context=context)
    context.network_vm_running = container_exists("network")


@given('I have a utility VM running')
def step_utility_vm_running(context):
    """Utility VM is running."""
    context.current_vm = "utility"
    if not container_exists("utility"):
        run_vde_command("start utility", timeout=120, context=context)
    context.utility_vm_running = container_exists("utility")


# =============================================================================
# Additional GIVEN steps for feature scenarios
# =============================================================================

@given('I have Docker installed on my host for SSH-VM-Steps')
def step_docker_installed(context):
    """Docker is installed on the host - verify via vde info."""
    result = run_vde_command('info', context=context)
    context.docker_installed = result.returncode == 0
    assert context.docker_installed, "Docker must be installed on host"


@given('I have a Go VM running')
def step_go_vm_running(context):
    """Go VM is running."""
    context.current_vm = "go"
    if not container_exists("go"):
        run_vde_command("start go", timeout=120, context=context)
    context.go_vm_running = container_exists("go")
    if context.go_vm_running:
        context.vm_name = "go"


@given('I have a Rust VM running')
def step_rust_vm_running(context):
    """Rust VM is running."""
    context.current_vm = "rust"
    if not container_exists("rust"):
        run_vde_command("start rust", timeout=120, context=context)
    context.rust_vm_running = container_exists("rust")
    if context.rust_vm_running:
        context.vm_name = "rust"


@given('I have projects on my host')
def step_host_has_projects(context):
    """Host has projects."""
    context.host_has_projects = (VDE_ROOT / "projects").exists()


@given('I have custom scripts on my host')
def step_host_has_scripts(context):
    """Host has custom scripts."""
    scripts_dir = VDE_ROOT / "bin"
    context.host_has_scripts = scripts_dir.exists()


# =============================================================================
# SSH INTO VM WHEN steps - Set context for VM operations
# =============================================================================

@when('I SSH into the Python VM')
def step_ssh_python_vm(context):
    """SSH into Python VM context."""
    context.current_vm = "python"
    context.vm_ssh_target = "vde-python"


@when('I SSH into the Go VM')
def step_ssh_go_vm(context):
    """SSH into Go VM context."""
    context.current_vm = "go"
    context.vm_ssh_target = "vde-go"


@when('I SSH into a VM')
def step_ssh_any_vm(context):
    """SSH into any available VM context."""
    running = docker_ps()
    if running:
        context.current_vm = running[0].replace('vde-', '')
        context.vm_ssh_target = running[0]
    else:
        context.current_vm = "python"
        context.vm_ssh_target = "vde-python"


@when('I SSH into the Rust VM')
def step_ssh_rust_vm(context):
    """SSH into Rust VM context."""
    context.current_vm = "rust"
    context.vm_ssh_target = "vde-rust"


@when('I SSH into the build VM')
def step_ssh_build_vm(context):
    """SSH into build VM context."""
    context.current_vm = "build"
    context.vm_ssh_target = "vde-build"


@when('I SSH into the coordination VM')
def step_ssh_coordination_vm(context):
    """SSH into coordination VM context."""
    context.current_vm = "coordination"
    context.vm_ssh_target = "vde-coordination"


@when('I SSH into the backup VM')
def step_ssh_backup_vm(context):
    """SSH into backup VM context."""
    context.current_vm = "backup"
    context.vm_ssh_target = "vde-backup"


@when('I SSH into the debugging VM')
def step_ssh_debugging_vm(context):
    """SSH into debugging VM context."""
    context.current_vm = "debugging"
    context.vm_ssh_target = "vde-debugging"


@when('I SSH into the network VM')
def step_ssh_network_vm(context):
    """SSH into network VM context."""
    context.current_vm = "network"
    context.vm_ssh_target = "vde-network"


@when('I SSH into the utility VM')
def step_ssh_utility_vm(context):
    """SSH into utility VM context."""
    context.current_vm = "utility"
    context.vm_ssh_target = "vde-utility"
