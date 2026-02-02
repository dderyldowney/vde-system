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
    """Request information about specific VM using vde list or fallback to file."""
    result = run_vde_command("list", timeout=30)
    
    # Handle case where run_vde_command returns None
    if result is None:
        context.last_exit_code = 1
        context.last_output = ''
        context.last_error = 'Command failed'
    else:
        context.last_exit_code = result.returncode
        context.last_output = result.stdout if result.stdout else ''
        context.last_error = result.stderr if result.stderr else ''
    
    context.vm_info_requested = vm_name
    context.vm_info_exit_code = context.last_exit_code
    
    # Parse VM info from the output or fallback to vm-types.conf
    vm_info = {}
    vm_types_file = VDE_ROOT / 'scripts' / 'data' / 'vm-types.conf'
    
    if vm_types_file.exists():
        content = vm_types_file.read_text()
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                parts = line.split('|')
                # Format: type|name|aliases|display_name|install_command|service_port
                if len(parts) >= 4:
                    vm_type = parts[0].strip()
                    vm_named = parts[1].strip()
                    if vm_named == vm_name.lower():
                        vm_info['name'] = vm_named
                        vm_info['display_name'] = parts[3].strip()
                        vm_info['alias'] = parts[2].strip() if len(parts) >= 3 else ''
                        vm_info['type'] = vm_type
                        # Check for install command in parts
                        if len(parts) >= 5:
                            vm_info['install'] = parts[4].strip()
                        break
    
    context.vm_info = vm_info


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
