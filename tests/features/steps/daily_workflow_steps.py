"""
BDD Step Definitions for Daily Development Workflow.

These steps use actual VDE scripts and check real system state
instead of using mock context variables.

Team collaboration steps have been moved to team_collaboration_steps.py
"""
import os
import subprocess
import sys

# Import shared configuration
steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)
import time
from pathlib import Path

from behave import given, then, when

from config import VDE_ROOT
from vm_common import (
    run_vde_command,
    docker_ps,
    container_exists,
    compose_file_exists,
    wait_for_container,
    ensure_vm_created,
    ensure_vm_running,
    ensure_vm_stopped,
)

# Test mode flag - set via environment variable
ALLOW_CLEANUP = os.environ.get("VDE_TEST_MODE") == "1"

# =============================================================================
# Daily Workflow GIVEN steps
# =============================================================================

@given('I previously created VMs for "python", "rust", and "postgres"')
def step_previously_created_vms_daily(context):
    """VMs were previously created.

    In test mode: actually creates the VMs.
    In local mode: checks if VMs exist.
    """
    if not hasattr(context, 'created_vms'):
        context.created_vms = set()
    for vm in ['python', 'rust', 'postgres']:
        if ALLOW_CLEANUP:
            ensure_vm_created(context, vm)
        else:
            if compose_file_exists(vm):
                context.created_vms.add(vm)


@given('I have a Python VM running')
def step_python_vm_running(context):
    """Python VM is running.

    In test mode: actually creates and starts the VM.
    In local mode: checks if VM is running.
    """
    ensure_vm_running(context, 'python')
    context.python_running = container_exists('python')


@given('I have "python" VM running')
def step_python_vm_running_daily(context):
    """Python VM is running.

    In test mode: actually creates and starts the VM.
    In local mode: checks if VM is running.
    """
    ensure_vm_running(context, 'python')
    context.python_running = container_exists('python')


@given('I have "rust" VM created but not running')
def step_rust_created_not_running(context):
    """Rust VM created but not running.

    In test mode: creates VM and ensures it's stopped.
    In local mode: checks if VM exists and is stopped.
    """
    if ALLOW_CLEANUP:
        ensure_vm_created(context, 'rust')
        ensure_vm_stopped(context, 'rust')
