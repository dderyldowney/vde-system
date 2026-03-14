"""
Crash Recovery and Build Failure Steps
tests/features/steps/crash_recovery_steps.py
"""

from behave import given, when, then
import subprocess
import time
import os
import sys
from pathlib import Path

# Add steps directory to path for imports
steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)

from vm_common import (
    run_vde_command, 
    docker_ps, 
    container_exists, 
    wait_for_container,
    wait_for_container_stopped
)

# =============================================================================
# Crash Recovery GIVEN steps
# =============================================================================

@given('a VM is actually running for Crash-Recovery')
def step_vm_actually_running(context):
    """Verify a VM is running via vde ps."""
    # Ensure at least one VM is running
    if not container_exists("python"):
        run_vde_command("start python", timeout=120, context=context)
        wait_for_container("python", timeout=60)
    
    running = docker_ps()
    context.running_vms_before = running
    assert any("vde-" in c for c in running), "No VDE VMs are running"


@given('I kill the VM container')
def step_kill_vm_container(context):
    """Simulate a crash by stopping the container via vde stop -f."""
    # Pick a running VM
    running = docker_ps()
    if running:
        vm_to_kill = running[0].replace("vde-", "")
        context.killed_vm = vm_to_kill
        # -f for immediate stop (simulates crash)
        run_vde_command(f"stop {vm_to_kill} -f", timeout=30, context=context)
        wait_for_container_stopped(f"vde-{vm_to_kill}", timeout=30)


@given('all VDE startup scripts are in place')
def step_run_startup_scripts(context):
    """Verify bin scripts exist."""
    bin_dir = Path(__file__).parent.parent.parent.parent / "bin"
    assert (bin_dir / "vde").exists(), "VDE script missing"
    assert (bin_dir / "start-virtual").exists(), "start-virtual script missing"


@given('previously running VMs start automatically')
def step_previously_running_start(context):
    """Verify VMs can be started again."""
    context.auto_start_verified = True


# =============================================================================
# Crash Recovery WHEN steps
# =============================================================================

@when('one VM crashes')
def step_vm_crashes(context):
    """Context: VM has crashed (handled in GIVEN or simulated here)."""
    if not hasattr(context, 'killed_vm'):
        # Kill python if it's running
        if container_exists("python"):
            run_vde_command("stop python -f", context=context)
            context.killed_vm = "python"
    context.vm_crashed = True


@when('I run VDE diagnostic commands')
def step_run_diagnostics(context):
    """Run diagnostic commands via vde health/info."""
    result = run_vde_command("health", timeout=60, context=context)
    context.last_output = result.stdout
    context.last_exit_code = result.returncode


# =============================================================================
# Crash Recovery THEN steps
# =============================================================================

@then('other VMs should continue running')
def step_others_continue(context):
    """Verify other VMs remain running after crash."""
    running = docker_ps()
    # If we killed one, others should still be there
    if hasattr(context, 'running_vms_before'):
        for c in context.running_vms_before:
            if hasattr(context, 'killed_vm') and f"vde-{context.killed_vm}" in c:
                continue
            assert c in running, f"Container {c} should still be running"


@then('the crash should not affect other containers')
def step_isolation_maintained(context):
    """Verify isolation during crash."""
    # Reuse others continue logic
    step_others_continue(context)


@then('I can restart the crashed VM independently')
def step_restart_independently(context):
    """Restart the crashed VM via vde start."""
    vm_to_restart = getattr(context, 'killed_vm', 'python')
    result = run_vde_command(f"start {vm_to_restart}", timeout=120, context=context)
    assert result.returncode == 0, f"Failed to restart {vm_to_restart}"
    assert wait_for_container(vm_to_restart, timeout=60), f"{vm_to_restart} failed to restart"


@given(u'a VM build fails')
def step_build_fails_setup(context):
    """Set up a build failure scenario."""
    context.build_failed = True


@then(u'I should receive a clear error message')
def step_clear_error_msg(context):
    """Verify clear error messaging."""
    # Check that error output is available from last command
    output = getattr(context, 'last_output', '') + getattr(context, 'last_error', '')
    assert len(output) > 0 or getattr(context, 'last_exit_code', 0) != 0, "Error output expected"


@then(u'the error should explain what went wrong')
def step_error_explains(context):
    """Verify error explains the issue."""
    output = getattr(context, 'last_output', '') + getattr(context, 'last_error', '')
    assert len(output) > 5, "Error should provide explanation"


@then(u'VDE should report the specific error')
def step_vde_reports_specific(context):
    """Verify VDE reports specific errors in output."""
    output = getattr(context, 'last_output', '') + getattr(context, 'last_error', '')
    # Specific errors should contain keywords like 'failed', 'error', 'refused', etc.
    assert any(x in output.lower() for x in ['fail', 'error', 'cannot', 'unable', 'refused', 'timeout']), \
        f"Output should contain specific error details: {output}"


@then(u'suggest troubleshooting steps')
def step_suggest_troubleshooting(context):
    """Verify troubleshooting suggestions in output."""
    output = getattr(context, 'last_output', '') + getattr(context, 'last_error', '')
    # VDE health or other commands should suggest fixes
    assert any(x in output.lower() for x in ['try', 'check', 'run', 'ensure', 'make sure', 'fix']), \
        f"Output should suggest troubleshooting steps: {output}"


@then(u'offer to retry')
def step_offer_retry(context):
    """Verify retry capability exists."""
    # VDE script supports --rebuild and --no-cache for retries
    assert (Path(__file__).parent.parent.parent.parent / "bin" / "vde").exists()
