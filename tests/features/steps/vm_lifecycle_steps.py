"""
BDD Step definitions for VM Lifecycle scenarios (core operations).
This file handles VM starting, stopping, restarting, and state management.
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
    docker_ps,
    get_vm_type,
    wait_for_container,
    run_vde_command,
)


# =============================================================================
# GIVEN steps - Setup initial VM states
# =============================================================================

@given('VM "{vm_name}" is running')
def step_vm_running(context, vm_name):
    """Start a VM using the actual VDE script."""
    # First ensure it's created
    if not compose_file_exists(vm_name):
        # Import here to avoid circular dependency
        from vm_creation_steps import step_vm_created
        step_vm_created(context, vm_name)
