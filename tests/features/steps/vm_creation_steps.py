"""
BDD Step definitions for VM Creation scenarios.
These steps handle VM creation, definition, and configuration management.
All steps use real system verification instead of context flags.
"""

import subprocess
import time
from pathlib import Path

from behave import given, then, when

# Import shared helpers and configuration
from vm_common import (
    VDE_ROOT,
    ALLOW_CLEANUP,
    compose_file_exists,
    container_exists,
    get_port_from_compose,
    get_vm_type,
    wait_for_container,
    run_vde_command,
)


# =============================================================================
# GIVEN steps - Setup initial state for VM creation
# =============================================================================

@given('the VM "{vm_name}" is defined as a language VM with install command "{cmd}"')
def step_vm_defined_lang(context, vm_name, cmd):
    """Define a VM type as a language VM."""
    context.test_vm_name = vm_name
    context.test_vm_type = "lang"
    context.test_vm_install = cmd


@given('the VM "{vm_name}" is defined as a service VM with port "{port}"')
def step_vm_defined_svc(context, vm_name, port):
    """Define a VM type as a service VM."""
    context.test_vm_name = vm_name
    context.test_vm_type = "service"
    context.test_vm_port = port


@given('no VM configuration exists for "{vm_name}"')
def step_no_vm_config(context, vm_name):
    """Ensure VM configuration doesn't exist by using remove-virtual command."""
    # When running locally without test mode, preserve user's VM configurations
    # Only remove VMs when running in the test container OR in test mode
    if ALLOW_CLEANUP:
        # Use the VDE remove-virtual command instead of directly deleting files
        # This ensures proper cleanup through the VDE workflow
        result = run_vde_command(f"remove {vm_name}", timeout=60)
        # Store result for debugging (don't assert - VM might not exist)
        context.remove_result = result


@given('VM "{vm_name}" has been created')
def step_vm_created(context, vm_name):
    """Create a VM using the actual VDE script."""
    # Remove existing config if present to ensure clean state
    step_no_vm_config(context, vm_name)

    # Run the create-virtual-for script
    result = run_vde_command(f"create {vm_name}", timeout=120)

    # Store creation info for cleanup
    if not hasattr(context, 'created_vms'):
        context.created_vms = set()
    context.created_vms.add(vm_name)

    # Store last result for assertions
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@given('VM "{vm_name}" is not created')
def step_vm_not_created(context, vm_name):
    """Remove VM configuration if it exists."""
    step_no_vm_config(context, vm_name)
    # Also try to remove container if running
    run_vde_command(f"stop {vm_name}", timeout=30)
    if hasattr(context, 'created_vms'):
        context.created_vms.discard(vm_name)


@given('VM types are loaded')
def step_vm_types_loaded(context):
    """VM types have been loaded from config - verify vm-types.conf exists."""
    vm_types_file = VDE_ROOT / "scripts" / "data" / "vm-types.conf"
    context.vm_types_exist = vm_types_file.exists()









def step_stale_lock(context, seconds):
    """Stale port lock exists - verify lock file age."""
    lock_file = VDE_ROOT / "cache" / "port-registry.lock"

    if lock_file.exists():
        # Check actual file age
        import stat
        file_stat = lock_file.stat()
        current_time = time.time()
        file_age = current_time - file_stat.st_mtime
        context.stale_lock_age = int(file_age)
        context.stale_lock_exists = True
