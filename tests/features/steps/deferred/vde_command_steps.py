"""
BDD Step definitions for VDE Natural Language Commands.
Implements common patterns like "I request to '...'" for VM lifecycle operations.
"""

import os
import subprocess
import sys
from pathlib import Path

from behave import given, then, when

# Get VDE_ROOT from environment or calculate
VDE_ROOT_STR = os.environ.get('VDE_ROOT_DIR')
if not VDE_ROOT_STR:
    try:
        from config import VDE_ROOT as config_root
        VDE_ROOT_STR = str(config_root)
    except ImportError:
        VDE_ROOT_STR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

VDE_ROOT = Path(VDE_ROOT_STR)
VDE_SCRIPT = os.path.join(VDE_ROOT, 'scripts/vde')

# All known VM types
_ALL_VMS = {
    'js', 'python', 'go', 'rust', 'nginx', 'postgres', 'redis',
    'mongodb', 'mysql', 'rabbitmq', 'couchdb', 'flutter', 'r',
    'c', 'cpp', 'csharp', 'java', 'kotlin', 'swift', 'php',
    'ruby', 'scala', 'haskell', 'lua', 'elixir', 'zig', 'asm'
}


def _run_vde_command(args):
    """Run a VDE command and return result."""
    cmd = [VDE_SCRIPT] + args.split()
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    return result


def _get_container_name(vm_name):
    """Convert VM name to container name."""
    service_vms = {'postgres', 'redis', 'mongodb', 'mysql', 'nginx', 'rabbitmq', 'couchdb'}
    if vm_name in service_vms:
        return vm_name
    return f"{vm_name}-dev"


def _container_exists(container_name):
    """Check if container exists (running or stopped)."""
    result = subprocess.run(
        ['docker', 'ps', '-a', '--format', '{{.Names}}'],
        capture_output=True, text=True
    )
    return container_name in result.stdout


def _container_is_running(container_name):
    """Check if container is running."""
    result = subprocess.run(
        ['docker', 'ps', '--format', '{{.Names}}'],
        capture_output=True, text=True
    )
    return container_name in result.stdout


def _extract_vms_from_command(command):
    """Extract VM names from a natural language command."""
    vms = []
    command_lower = command.lower()

    # Split by various delimiters
    parts = []
    if ' and ' in command_lower:
        parts = command_lower.split(' and ')
    elif ',' in command_lower:
        parts = command_lower.split(',')

    if parts:
        for part in parts:
            part = part.strip()
            # Check each word against known VMs
            words = part.split()
            for word in words:
                word = word.strip().rstrip('.').rstrip(',')
                if word in _ALL_VMS:
                    vms.append(word)
    else:
        # Check each word
        words = command_lower.split()
        for word in words:
            word = word.strip().rstrip('.').rstrip(',')
            if word in _ALL_VMS:
                vms.append(word)

    return vms


def _execute_vde_command(args):
    """Execute a VDE command and return result."""
    cmd = [VDE_SCRIPT] + args.split()
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    return result


def _execute_vde_create_and_start(vm_name):
    """Execute vde create and vde start for a VM, handling removed containers."""
    # First try to start - if it fails because not created, create and start
    result = subprocess.run([VDE_SCRIPT, 'start', vm_name],
                          capture_output=True, text=True)
    
    if result.returncode != 0 and 'not_created' in result.stderr:
        # Container doesn't exist, need to create it
        result = subprocess.run([VDE_SCRIPT, 'create', vm_name],
                              capture_output=True, text=True)
    
    return result


# =============================================================================
# I request to "..." - Natural Language Command Patterns
# =============================================================================

@when(u'I request to "{command}"')
def step_request_command(context, command):
    """Execute a natural language VDE command."""
    command_lower = command.lower()
    all_results = []
    all_stdout = []
    all_stderr = []

    # Handle multi-part commands: "stop all and start X and Y"
    if 'stop all' in command_lower and 'start' in command_lower:
        # Stop all first
        result = subprocess.run([VDE_SCRIPT, 'stop', 'all'],
                              capture_output=True, text=True)
        all_results.append(result)
        all_stdout.append(result.stdout)
        all_stderr.append(result.stderr)

        # Extract VMs to start and recreate if needed
        vms = _extract_vms_from_command(command)
        for vm in vms:
            result = _execute_vde_create_and_start(vm)
            all_results.append(result)
            all_stdout.append(result.stdout)
            all_stderr.append(result.stderr)

        context.vde_command_result = all_results[-1]
        context.vde_command_output = '\n'.join(all_stdout) + '\n'.join(all_stderr)
        context.vde_command_exit_code = max(r.returncode for r in all_results)
        return

    # Handle "start all services"
    if 'start all services' in command_lower:
        service_vms = ['go', 'rust', 'nginx']
        for vm in service_vms:
            result = _execute_vde_create_and_start(vm)
            all_results.append(result)
            all_stdout.append(result.stdout)
            all_stderr.append(result.stderr)

        context.vde_command_result = all_results[-1]
        context.vde_command_output = '\n'.join(all_stdout) + '\n'.join(all_stderr)
        context.vde_command_exit_code = max(r.returncode for r in all_results)
        return

    # Handle "stop all" / "stop everything"
    if 'stop all' in command_lower or 'stop everything' in command_lower:
        result = subprocess.run([VDE_SCRIPT, 'stop', 'all'],
                              capture_output=True, text=True)
        context.vde_command_result = result
        context.vde_command_output = result.stdout + result.stderr
        context.vde_command_exit_code = result.returncode
        return

    # Handle "start X and Y" pattern
    if command_lower.startswith('start ') and (' and ' in command_lower or ',' in command_lower):
        vms = _extract_vms_from_command(command)
        if vms:
            for vm in vms:
                result = _execute_vde_create_and_start(vm)
                all_results.append(result)
                all_stdout.append(result.stdout)
                all_stderr.append(result.stderr)

            context.vde_command_result = all_results[-1]
            context.vde_command_output = '\n'.join(all_stdout) + '\n'.join(all_stderr)
            context.vde_command_exit_code = max(r.returncode for r in all_results)
            return

    # Handle "create X and Y" pattern
    if command_lower.startswith('create ') and (' and ' in command_lower or ',' in command_lower):
        vms = _extract_vms_from_command(command)
        if vms:
            for vm in vms:
                result = subprocess.run([VDE_SCRIPT, 'create', vm],
                                      capture_output=True, text=True)
                all_results.append(result)
                all_stdout.append(result.stdout)
                all_stderr.append(result.stderr)

            context.vde_command_result = all_results[-1]
            context.vde_command_output = '\n'.join(all_stdout) + '\n'.join(all_stderr)
            context.vde_command_exit_code = max(r.returncode for r in all_results)
            return

    # Default: simple command
    cmd = [VDE_SCRIPT] + command.split()
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    context.vde_command_result = result
    context.vde_command_output = result.stdout + result.stderr
    context.vde_command_exit_code = result.returncode


# =============================================================================
# I should see ... - Verification Patterns
# =============================================================================

@then(u'I should see which VMs are stopped')
def step_should_see_stopped(context):
    """Verify stopped VMs are shown in output."""
    output = getattr(context, 'vde_command_output', '')
    assert 'stopped' in output.lower() or 'not running' in output.lower(), \
        f"Expected to see stopped VMs in output: {output}"
