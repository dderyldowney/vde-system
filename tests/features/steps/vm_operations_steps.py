"""
BDD Step Definitions for Basic VM Operations.

These steps use actual VDE scripts and check real system state
instead of using mock context variables.
"""
import os
import subprocess
import sys
import time

# Import shared configuration
steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)
from pathlib import Path

from behave import given, then, when

from config import VDE_ROOT
from vm_common import (
    run_vde_command,
    docker_ps,
    container_exists,
    compose_file_exists,
    wait_for_container,
    wait_for_container_stopped,
)

# =============================================================================
# VM Operations WHEN steps
# =============================================================================

@when('I run "start-virtual all"')
def step_start_all(context):
    """Start all VMs using vde start --all command."""
    result = run_vde_command("start --all", timeout=300)
    context.last_command = "vde start --all"
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('I run "shutdown-virtual all"')
def step_shutdown_all(context):
    """Shutdown all VMs using vde stop --all command."""
    result = run_vde_command("stop --all", timeout=120)
    context.last_command = "vde stop --all"
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('I run "list-vms"')
def step_list_vms(context):
    """List VMs using vde list command."""
    result = run_vde_command("list", timeout=30)
    context.last_command = "vde list"
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('I start a language VM')
def step_start_lang_vm(context):
    """Start a language VM using vde start command."""
    result = run_vde_command("start python", timeout=180)
    context.last_exit_code = result.returncode


@when('I stop a VM')
def step_stop_vm(context):
    """Stop a VM using vde stop command."""
    result = run_vde_command("stop python", timeout=60)
    context.last_exit_code = result.returncode


@when('I restart a VM')
def step_restart_vm(context):
    """Restart a VM using vde restart command."""
    result = run_vde_command("restart python", timeout=180)
    context.last_exit_code = result.returncode


@when('I create a new VM type')
def step_create_vm_type(context):
    """Create new VM type using vde add command."""
    result = run_vde_command("add zig --type lang --display-name Zig --install 'apt-get install -y zig'", timeout=30)
    context.last_exit_code = result.returncode


@when('I remove an old VM')
def step_remove_old_vm(context):
    """Remove old VM using vde remove command."""
    result = run_vde_command("remove ruby", timeout=60)
    context.last_exit_code = result.returncode
    context.removed_vm_name = 'ruby'


# =============================================================================
# VM Operations THEN steps
# =============================================================================

@then('all my VMs should start')
def step_all_vms_start(context):
    """All VMs should start."""
    assert context.last_exit_code == 0, f"Failed to start VMs: {context.last_error}"


@then('I should see running VMs')
def step_see_running(context):
    """Should see running VMs."""
    running = docker_ps()
    vde_running = [c for c in running if "-dev" in c or c in ['postgres', 'redis', 'nginx', 'mongodb']]
    assert len(vde_running) > 0, "No VMs are running"


@then('my VMs should shut down cleanly')
def step_vms_shutdown(context):
    """VMs should shutdown cleanly."""
    assert context.last_exit_code == 0, f"Failed to shutdown VMs: {context.last_error}"
    # Check VMs are actually stopped
    time.sleep(2)
    running = docker_ps()
    vde_running = [c for c in running if "-dev" in c]
    # All VMs should be stopped after shutdown command
    assert len(vde_running) == 0, f"VMs should be stopped after shutdown, but found: {vde_running}"


@then('I should see a list of available VMs')
def step_see_vm_list(context):
    """Should see VM list."""
    assert context.last_exit_code == 0, f"Failed to list VMs: {context.last_error}"
    assert len(context.last_output) > 0, "No VM list output"


@then('the VM should start')
def step_vm_starts(context):
    """VM should start."""
    assert context.last_exit_code == 0, f"Failed to start VM: {context.last_error}"
    # Check VM is actually running with wait
    assert wait_for_container('python', timeout=60), "Python VM is not running (waited 60s)"


@then('the VM should stop')
def step_vm_stops(context):
    """VM should stop."""
    assert context.last_exit_code == 0, f"Failed to stop VM: {context.last_error}"
    time.sleep(2)
    assert not container_exists('python'), "Python VM is still running"


@then('the new VM type should be added')
def step_vm_type_added(context):
    """VM type should be added."""
    vm_types_file = VDE_ROOT / "scripts" / "data" / "vm-types.conf"
    assert vm_types_file.exists(), "vm-types.conf should exist"
    content = vm_types_file.read_text()
    assert "zig" in content.lower(), "zig VM type should be added to vm-types.conf"


@then('the VM should be removed')
def step_vm_removed_check(context):
    """VM should be removed."""
    # Get the VM name from context (set by the WHEN step that removed it)
    removed_vm = getattr(context, 'removed_vm_name', 'ruby')
    # Verify the removal command succeeded
    exit_code = getattr(context, 'last_exit_code', None)
    if exit_code is not None:
        assert exit_code == 0, f"Failed to remove VM: {getattr(context, 'last_error', 'unknown error')}"
    # Verify compose file was actually removed
    assert not compose_file_exists(removed_vm), f"{removed_vm} VM config still exists"
    # Verify container was removed
    running = docker_ps()
    vm_containers = [c for c in running if removed_vm in c.lower()]
    assert len(vm_containers) == 0, f"{removed_vm} containers still running: {vm_containers}"


@then('I can reconnect to my running VMs')
def step_can_reconnect(context):
    """Can reconnect to running VMs."""
    running = docker_ps()
    vde_running = [c for c in running if "-dev" in c]
    assert len(vde_running) > 0, "Should have running VMs to reconnect to"
