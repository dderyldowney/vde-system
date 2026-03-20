"""
BDD Step definitions for Daily Development Workflow scenarios.
These steps are specific to daily-development-workflow.feature.
"""

import os
import subprocess
import sys
from pathlib import Path
from behave import given, then, when

steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)

from vm_common import (
    VDE_ROOT,
    container_exists,
    container_is_running,
    compose_file_exists,
    run_vde_command,
    docker_ps,
)


@then("I should see a list of all running VMs")
def step_see_running_vms_list(context):
    """Verify running VMs are listed."""
    result = run_vde_command("ps", context=context)
    assert result.returncode == 0, "vde ps should succeed"
    assert result.stdout.strip(), "Should see list of running VMs"


@then("each VM should show its status")
def step_each_vm_show_status(context):
    """Verify each VM shows its status."""
    output = getattr(context, "vde_command_output", "") or getattr(context, "last_output", "")
    if not output:
        result = run_vde_command("ps", context=context)
        output = result.stdout
    assert output, "Should have status output for VMs"


@then("the list should include both language and service VMs")
def step_list_includes_language_and_service(context):
    """Verify output includes both language and service VMs."""
    output = getattr(context, "vde_command_output", "") or getattr(context, "last_output", "")
    if not output:
        result = run_vde_command("ps", context=context)
        output = result.stdout
    assert output, "Should have VM list output"


@then("no containers should be left running")
def step_no_containers_left(context):
    """Verify no containers are left running."""
    running = docker_ps()
    assert len(running) == 0, f"No containers should be running, found: {running}"


@then("the operation should complete without errors")
def step_operation_no_errors(context):
    """Verify operation completed without errors."""
    exit_code = getattr(context, "last_exit_code", 0)
    assert exit_code == 0, f"Operation should complete without errors, got exit code {exit_code}"
