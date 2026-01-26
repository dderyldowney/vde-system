"""
BDD Step Definitions for VDE SSH Commands (WHEN steps).

These steps execute VDE SSH commands and capture their output.
All steps use real system verification - no context flags or fake tests.
"""
import os
import subprocess
import sys
from pathlib import Path

# Import shared configuration
steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)

from behave import when, then
from config import VDE_ROOT


# =============================================================================
# VDE SSH Command WHEN Steps
# =============================================================================

@when('I run "vde ssh-setup status"')
def step_vde_ssh_setup_status(context):
    """Execute vde ssh-setup status and capture output.

    This step runs the status command and stores the output for
    verification in THEN steps.
    """
    result = subprocess.run(
        ["./scripts/vde", "ssh-setup", "status"],
        capture_output=True, text=True, timeout=30,
        cwd=VDE_ROOT
    )
    context.ssh_status_output = result.stdout
    context.ssh_status_exit_code = result.returncode
    context.ssh_status_stderr = result.stderr


@when('I run "vde ssh-setup init"')
def step_vde_ssh_setup_init(context):
    """Execute vde ssh-setup init and capture output.

    This step runs the init command which creates SSH keys,
    starts the agent, and generates config.
    """
    result = subprocess.run(
        ["./scripts/vde", "ssh-setup", "init"],
        capture_output=True, text=True, timeout=60,
        cwd=VDE_ROOT
    )
    context.ssh_init_output = result.stdout
    context.ssh_init_exit_code = result.returncode
    context.ssh_init_stderr = result.stderr


@when('I run "vde ssh-setup start"')
def step_vde_ssh_setup_start(context):
    """Execute vde ssh-setup start and capture output.

    This step runs the start command which starts the SSH agent
    and loads the VDE key.
    """
    result = subprocess.run(
        ["./scripts/vde", "ssh-setup", "start"],
        capture_output=True, text=True, timeout=30,
        cwd=VDE_ROOT
    )
    context.ssh_start_output = result.stdout
    context.ssh_start_exit_code = result.returncode
    context.ssh_start_stderr = result.stderr


@when('I run "vde ssh-setup generate"')
def step_vde_ssh_setup_generate(context):
    """Execute vde ssh-setup generate and capture output.

    This step runs the generate command which regenerates the
    VM SSH config.
    """
    result = subprocess.run(
        ["./scripts/vde", "ssh-setup", "generate"],
        capture_output=True, text=True, timeout=30,
        cwd=VDE_ROOT
    )
    context.ssh_generate_output = result.stdout
    context.ssh_generate_exit_code = result.returncode
    context.ssh_generate_stderr = result.stderr


@when('I run "vde ssh-sync"')
def step_vde_ssh_sync(context):
    """Execute vde ssh-sync and capture output.

    This step runs the sync command which copies the VDE public
    key to the build context.
    """
    result = subprocess.run(
        ["./scripts/vde", "ssh-sync"],
        capture_output=True, text=True, timeout=30,
        cwd=VDE_ROOT
    )
    context.ssh_sync_output = result.stdout
    context.ssh_sync_exit_code = result.returncode
    context.ssh_sync_stderr = result.stderr


@when('I run "vde start {vm} --update-ssh"')
def step_vde_start_update_ssh(context, vm):
    """Execute vde start with --update-ssh flag.

    This step starts a VM and regenerates the SSH config afterward.

    Args:
        vm: VM name to start
    """
    result = subprocess.run(
        ["./scripts/vde", "start", vm, "--update-ssh"],
        capture_output=True, text=True, timeout=120,
        cwd=VDE_ROOT
    )
    context.start_update_ssh_output = result.stdout
    context.start_update_ssh_exit_code = result.returncode
    context.start_update_ssh_stderr = result.stderr


@when('I run "vde ssh-setup {action}"')
def step_vde_ssh_setup_action(context, action):
    """Execute vde ssh-setup with a specific action.

    Generic step for any ssh-setup subcommand.

    Args:
        action: The ssh-setup subcommand (status, init, start, generate)
    """
    result = subprocess.run(
        ["./scripts/vde", "ssh-setup", action],
        capture_output=True, text=True, timeout=60,
        cwd=VDE_ROOT
    )
    context.last_command_output = result.stdout
    context.last_command_exit_code = result.returncode
    context.last_command_stderr = result.stderr


# =============================================================================
# Quick verification THEN steps (for convenience in this file)
# =============================================================================

@then('the command should succeed')
def step_command_should_succeed(context):
    """Verify the last vde SSH command exited with code 0."""
    # Check various context attributes for exit codes from SSH commands
    exit_code = None
    stderr = ""

    if hasattr(context, 'ssh_status_exit_code'):
        exit_code = context.ssh_status_exit_code
        stderr = getattr(context, 'ssh_status_stderr', '')
    elif hasattr(context, 'ssh_init_exit_code'):
        exit_code = context.ssh_init_exit_code
        stderr = getattr(context, 'ssh_init_stderr', '')
    elif hasattr(context, 'ssh_start_exit_code'):
        exit_code = context.ssh_start_exit_code
        stderr = getattr(context, 'ssh_start_stderr', '')
    elif hasattr(context, 'ssh_generate_exit_code'):
        exit_code = context.ssh_generate_exit_code
        stderr = getattr(context, 'ssh_generate_stderr', '')
    elif hasattr(context, 'ssh_sync_exit_code'):
        exit_code = context.ssh_sync_exit_code
        stderr = getattr(context, 'ssh_sync_stderr', '')
    elif hasattr(context, 'start_update_ssh_exit_code'):
        exit_code = context.start_update_ssh_exit_code
        stderr = getattr(context, 'start_update_ssh_stderr', '')
    elif hasattr(context, 'last_command_exit_code'):
        exit_code = context.last_command_exit_code
        stderr = getattr(context, 'last_command_stderr', '')

    assert exit_code is not None, \
        "No command result found in context - did you run a command step first?"
    assert exit_code == 0, \
        f"Command failed with exit code {exit_code}. stderr: {stderr}"
