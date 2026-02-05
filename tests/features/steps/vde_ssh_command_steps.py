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
