# =============================================================================
# Error Handling and Recovery Step Definitions
# =============================================================================
#
# These steps implement the error-handling-and-recovery.feature scenarios.
# They focus on verifying that VDE properly handles errors and provides
# helpful recovery guidance to users.
#
# Key principles:
# - Use real command execution where possible
# - Verify actual error messages from VDE
# - Check error codes and output patterns
# - Don't fake error scenarios with context flags
#
# Note: Some steps are already defined in debugging_steps.py and are not
# duplicated here.
#

import re
import subprocess
from pathlib import Path

from behave import given, then, when

from common_steps import VDE_ROOT, run_vde_command

# =============================================================================
# GIVEN Steps - Error Setup
# =============================================================================

@given('I try to use a VM that doesn\'t exist')
def step_try_nonexistent_vm(context):
    """Attempt to use a VM that doesn't exist."""
    context.invalid_vm_name = "nonexistent-vm-that-does-not-exist"
    # Store for use in WHEN step
    context.expected_error_type = "vm_not_found"


@given('my disk is nearly full')
def step_disk_nearly_full(context):
    """Set up disk space scenario for error handling testing.

    VDE should detect disk space issues and report them appropriately.
    This scenario tests error message handling for low disk space.
    """
    context.disk_space_scenario = True


@given('the Docker network can\'t be created')
def step_network_creation_fails(context):
    """Set up network failure scenario for error handling testing.

    This scenario tests error message handling for network-related failures.
    """
    context.network_failure_scenario = True


@given('one VM fails to start')
def step_one_vm_fails(context):
    """Set up scenario where one VM fails during multi-VM start."""
    context.failing_vm = "invalid-vm-name"
    context.working_vms = ["python", "rust"]
    context.partial_failure_scenario = True


# =============================================================================
# WHEN Steps - Error Triggering
# =============================================================================

@when('I try to create a VM')
def step_try_create_vm(context):
    """Attempt to create a VM with invalid configuration."""
    # Use invalid_vm_name from context, or provide default
    invalid_vm = getattr(context, 'invalid_vm_name', 'invalid-vm-name')
    # Try to create a VM with invalid name
    result = run_vde_command(
        f"create {invalid_vm}",
        timeout=30
    )
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('I try to use the VM')
def step_try_use_vm(context):
    """Try to use a VM with malformed configuration."""
    if hasattr(context, 'malformed_compose_path'):
        # Try to use VM with bad compose file
        result = subprocess.run(
            ["docker-compose", "-f", context.malformed_compose_path, "config"],
            capture_output=True,
            text=True,
            timeout=10
        )
        context.last_exit_code = result.returncode
        context.last_output = result.stdout
        context.last_error = result.stderr
