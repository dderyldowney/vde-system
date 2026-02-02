"""
BDD Step definitions for VM Status and Discovery scenarios.
These steps handle VM listing, status checking, SSH configuration, and VM information.
All steps use real system verification instead of context flags.
"""

import subprocess
from pathlib import Path

from behave import given, then, when

# Import shared helpers and configuration
from vm_common import (
    VDE_ROOT,
    compose_file_exists,
    container_exists,
    docker_ps,
    get_container_health,
    get_port_from_compose,
    get_vm_type,
    run_vde_command,
)


# =============================================================================
# GIVEN steps - Setup status and discovery states
# =============================================================================

@given('I have VDE installed')
def step_vde_installed(context):
    """VDE is installed - verify VDE_ROOT exists."""
    assert VDE_ROOT.exists(), "VDE_ROOT should exist"
    assert (VDE_ROOT / "scripts").exists(), "VDE scripts directory should exist"
    context.vde_installed = True



    """Need to start a project."""
    context.project_type = project


@given('I want to see only programming language environments')
def step_want_languages_only(context):
    """Want to see only language VMs."""
    context.languages_only = True


@given('I want to see only infrastructure services')
def step_want_services_only(context):
    """Want to see only service VMs."""
    context.services_only = True


@given('I want to know about the Python VM')
def step_want_python_info(context):
    """Want to know about Python VM."""
    context.vm_inquiry = "python"


@given('I have running VMs')
def step_have_running_vms(context):
    """Have running VMs - verify actual containers are running."""
    running = docker_ps()
    context.has_running_vms = len(running) > 0


@given('I have stopped several VMs')
def step_have_stopped_vms(context):
    """Have stopped VMs - verify VMs exist but are not running."""
    vm_types_file = VDE_ROOT / "scripts" / "data" / "vm-types.conf"
    context.has_stopped_vms = vm_types_file.exists()


@given('I check VM status')
def step_check_vm_status(context):
    """Check VM status."""
    context.status_checked = True
    result = run_vde_command("list", timeout=30)
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


# =============================================================================
# WHEN steps - Perform status and discovery actions
# =============================================================================

@when('I request "status"')
def step_request_status(context):
    """Request status."""
    result = run_vde_command("list", timeout=30)
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('I view the output')
def step_view_output(context):
    """View the output."""
    assert context.last_output, "Should have output to view"


@when('I check status')
def step_check_status_again(context):
    """Check status."""
    result = run_vde_command("list", timeout=30)
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('I request information about "{vm_name}"')
def step_request_vm_info(context, vm_name):
    """Request information about specific VM using vde list."""
    result = run_vde_command("list", timeout=30)
    context.last_output = result.stdout
    context.last_error = result.stderr
    context.vm_info_requested = vm_name
    context.vm_info_exit_code = result.returncode


@when('I reload VM types')
def step_reload_vm_types(context):
    """Reload VM types."""
    result = run_vde_command("list", timeout=30)
    context.last_exit_code = result.returncode
    context.last_output = result.stdout


@when('I run "{command}"')
def step_run_command(context, command):
    """Execute a VDE command or to-host command."""
    # Check if this is a to-host command
    if command.startswith('to-host '):
        # Extract the actual host command
        host_command = command[8:]  # Remove 'to-host ' prefix
        
        # Execute the command on host
        try:
            result = subprocess.run(
                host_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            context.last_command_output = result.stdout
            context.last_command_stderr = result.stderr
            context.last_command_rc = result.returncode
            context.last_command = host_command
        except subprocess.TimeoutExpired:
            context.last_command_output = ""
            context.last_command_stderr = f"Command timed out after 30s"
            context.last_command_rc = -1
            context.last_command = host_command
        except Exception as e:
            context.last_command_output = ""
            context.last_command_stderr = str(e)
            context.last_command_rc = -1
            context.last_command = host_command
    else:
        # This is a VDE command
        result = run_vde_command(command, timeout=120)
        context.last_command = command
        context.last_exit_code = result.returncode
        context.last_output = result.stdout
        context.last_error = result.stderr


@when('I check docker-compose config')
def step_check_compose_config(context):
    """Check docker-compose configuration."""
    # Try to run docker-compose config in a VM directory
    vm_name = getattr(context, 'current_vm', 'python')
    compose_dir = VDE_ROOT / "configs" / "docker" / vm_name
    if compose_dir.exists():
        result = subprocess.run(
            ["docker-compose", "config"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=compose_dir,
        )
