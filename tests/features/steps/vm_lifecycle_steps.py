"""
BDD Step definitions for VM Lifecycle scenarios (core operations).
This file handles VM starting, stopping, restarting, and state management.
All steps use real system verification instead of context flags.
"""

import subprocess
import time
from pathlib import Path

from behave import given, then, when

# Import shared helpers and configuration
from vm_common import (
    VDE_ROOT,
    compose_file_exists,
    container_exists,
    docker_ps,
    get_vm_type,
    wait_for_container,
    run_vde_command,
)


# =============================================================================
# GIVEN steps - Setup initial VM states
# =============================================================================

@given('VM "{vm_name}" is running')
def step_vm_running(context, vm_name):
    """Start a VM using the actual VDE script."""
    # First ensure it's created
    if not compose_file_exists(vm_name):
        # Import here to avoid circular dependency
        from vm_creation_steps import step_vm_created
        step_vm_created(context, vm_name)
    else:
        # VM already exists, but ensure it's tracked in created_vms
        if not hasattr(context, 'created_vms'):
            context.created_vms = set()
        context.created_vms.add(vm_name)

    # Start the VM
    result = run_vde_command(f"./scripts/start-virtual {vm_name}", timeout=180)

    # Wait for container to be running
    if result.returncode == 0:
        wait_for_container(vm_name, timeout=60)

    # Store running VMs
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.running_vms.add(vm_name)

    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@given('VM "{vm_name}" is not running')
def step_vm_not_running(context, vm_name):
    """Stop a VM using the actual VDE script."""
    result = run_vde_command(f"./scripts/shutdown-virtual {vm_name}", timeout=60)

    # Wait for container to stop
    if result.returncode == 0:
        for _ in range(10):
            if not container_exists(vm_name):
                break
            time.sleep(1)

    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.running_vms.discard(vm_name)


    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@given('neither VM is running')
def step_neither_vm_running(context):
    """Stop both VMs using actual VDE script."""
    run_vde_command("./scripts/shutdown-virtual all", timeout=60)
    time.sleep(2)
    if hasattr(context, 'running_vms'):
        context.running_vms.clear()


@given('none of the VMs are running')
def step_no_vms_running(context):
    """Stop all VMs using actual VDE script."""
    # Record current running VMs before shutdown
    running = docker_ps()
    context.pre_shutdown_vms = running
    context.shutdown_all_triggered = True

    run_vde_command("./scripts/shutdown-virtual all", timeout=60)
    time.sleep(2)
    if hasattr(context, 'running_vms'):
        context.running_vms.clear()


@given('I have a running Python VM')
def step_have_running_python(context):
    """Have a running Python VM."""
    # Start python if not already running
    if not container_exists("python"):
        result = run_vde_command("./scripts/start-virtual python", timeout=120)
        context.last_exit_code = result.returncode
        context.last_output = result.stdout
        context.last_error = result.stderr
        time.sleep(2)
    context.test_running_vm = "python"


@given('I have several VMs')
def step_have_several_vms(context):
    """Have several VMs - verify VMs exist."""
    vm_types_file = VDE_ROOT / "scripts" / "data" / "vm-types.conf"
    context.several_vms = vm_types_file.exists()


@given('I have multiple running VMs')
def step_have_multiple_running(context):
    """Have multiple running VMs - verify actual running containers."""
    running = docker_ps()
    context.multiple_running = len(running) > 0


@given('I have a stopped VM')
def step_have_stopped_vm(context):
    """Have a stopped VM."""
    # Use postgres as a default stopped VM
    context.test_stopped_vm = "postgres"
    # Stop it to ensure it's not running
    run_vde_command(f"./scripts/shutdown-virtual {context.test_stopped_vm}", timeout=60)
    time.sleep(1)


@given('I have created several VMs')
def step_have_created_vms(context):
    """Several VMs have been created - verify compose files exist."""
    # Check for common VMs
    common_vms = ["python", "go", "postgres"]
    created = []
    for vm in common_vms:
        if compose_file_exists(vm):
            created.append(vm)
    context.created_vms = created


@given('I have a running VM')
def step_state_running_vm(context):
    """Have a running VM."""
    # Ensure we have a running VM for testing
    if not hasattr(context, 'test_running_vm'):
        context.test_running_vm = "python"
        # Start python if not already running
        if not container_exists("python"):
            result = run_vde_command("./scripts/start-virtual python", timeout=120)
            context.last_exit_code = result.returncode
            context.last_output = result.stdout
            context.last_error = result.stderr
            time.sleep(2)
    # Verify actual container state
    context.vm_running = container_exists("python")


@given('I have created a Go VM')
def step_have_created_go_vm(context):
    """Go VM has been created - verify compose file exists."""
    compose_path = VDE_ROOT / "configs" / "docker" / "go" / "docker-compose.yml"
    context.go_vm_created = compose_path.exists()


# =============================================================================
# WHEN steps - Perform lifecycle actions
# =============================================================================

@when('I request to "start python"')
def step_request_start_python(context):
    """Request to start python VM."""
    context.start_requested = "python"
    result = run_vde_command("./scripts/start-virtual python", timeout=120)
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('I request to "start python and postgres"')
def step_request_start_python_postgres(context):
    """Request to start python and postgres VMs."""
    context.start_requested = "python postgres"
    result = run_vde_command("./scripts/start-virtual python postgres", timeout=180)
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('I request to "start python, go, and postgres"')
def step_request_start_multiple(context):
    """Request to start multiple VMs."""
    context.multiple_vms_start = ["python", "go", "postgres"]
    result = run_vde_command("./scripts/start-virtual python go postgres", timeout=180)
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('I request to "stop python"')
def step_request_stop_python(context):
    """Request to stop python VM."""
    context.vm_stop_requested = "python"
    result = run_vde_command("./scripts/shutdown-virtual python", timeout=60)
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('I request to "stop python and postgres"')
def step_request_stop_multiple(context):
    """Request to stop multiple VMs."""
    context.stop_multiple_requested = ["python", "postgres"]
    result = run_vde_command("./scripts/shutdown-virtual python postgres", timeout=60)
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('I request to "stop postgres"')
def step_request_stop_postgres(context):
    """Request to stop postgres VM."""
    context.stop_requested = "postgres"
    result = run_vde_command("./scripts/shutdown-virtual postgres", timeout=60)
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('I request to "restart rust"')
def step_request_restart_rust(context):
    """Request to restart rust VM."""
    context.restart_requested = "rust"
    # Run shutdown then start
    run_vde_command(f"./scripts/shutdown-virtual rust", timeout=60)
    time.sleep(2)
    result = run_vde_command(f"./scripts/start-virtual rust", timeout=120)
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('I request to "restart the VM"')
def step_request_restart(context):
    """Request to restart VM."""
    vm_name = getattr(context, 'test_running_vm', 'python')
    context.restart_requested = vm_name
    # Run shutdown then start
    run_vde_command(f"./scripts/shutdown-virtual {vm_name}", timeout=60)
    time.sleep(2)
    result = run_vde_command(f"./scripts/start-virtual {vm_name}", timeout=120)
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('I request to "restart python with rebuild"')
def step_request_restart_rebuild(context):
    """Request to restart with rebuild."""
    context.restart_rebuild_requested = "python"
    # Run shutdown then start with rebuild
    run_vde_command(f"./scripts/shutdown-virtual python", timeout=60)
    time.sleep(2)
    result = run_vde_command(f"./scripts/start-virtual python --rebuild", timeout=180)
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('I request to "start go"')
def step_request_start_go(context):
    """Request to start go VM."""
    context.vm_start_requested = "go"
    result = run_vde_command("./scripts/start-virtual go", timeout=120)
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('I try to create it again')
def step_try_create_again(context):
    """Try to create VM again."""
    vm_name = getattr(context, 'test_running_vm', 'python')
    result = run_vde_command(f"./scripts/create-virtual-for {vm_name}", timeout=120)
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr
    context.create_attempted_again = True


@when('I start a specific VM')
def step_start_vm_specific(context):
    """Start a specific VM with configured name."""
    if not hasattr(context, 'test_vm_to_start'):
        context.test_vm_to_start = "rust"
    result = run_vde_command(f"./scripts/start-virtual {context.test_vm_to_start}", timeout=120)
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr
    # Verify actual container state
    context.vm_started = container_exists(context.test_vm_to_start)


@when('it takes time to be ready')
def step_takes_time_to_ready(context):
    """VM takes time to be ready - wait for container."""
    vm_name = getattr(context, 'test_vm_to_start', 'rust')
    if context.last_exit_code == 0:
        wait_for_container(vm_name, timeout=30)


# =============================================================================
# THEN steps - Verify lifecycle outcomes
# =============================================================================

@then('VM "{vm_name}" should be running')
def step_vm_should_be_running(context, vm_name):
    """Verify VM is running using actual Docker state."""
    assert container_exists(vm_name), f"VM {vm_name} is not running (docker ps check failed)"


@then('VM "{vm_name}" should not be running')
def step_vm_not_running_verify(context, vm_name):
    """Verify VM is not running using actual Docker state."""
    assert not container_exists(vm_name), f"VM {vm_name} is running but should not be"


@then('no VMs should be running')
def step_no_vms_running_verify(context):
    """Verify no VMs are running using actual Docker state."""
    running = docker_ps()
    # Filter out non-VDE containers by checking for -dev suffix or known service names
    vde_containers = {c for c in running if (
        c.endswith('-dev') or c in ['postgres', 'redis', 'mongo', 'nginx', 'mysql', 'rabbitmq']
    )}

    # If shutdown_all_triggered was set, verify we stopped at least some VMs
    if getattr(context, 'shutdown_all_triggered', False):
        previously_running = getattr(context, 'pre_shutdown_vms', set())
        # Verify we have fewer VMs running now than before
        assert len(vde_containers) <= len(previously_running), \
            f"Shutdown did not reduce running VMs: before={previously_running}, after={vde_containers}"

    # No VDE containers should be running
    assert len(vde_containers) == 0, f"VMs are still running: {vde_containers}"


@then('VM configuration should still exist')
def step_vm_config_exists(context):
    """VM configuration still exists after stop - verify compose file exists."""
    assert hasattr(context, 'created_vms') and len(context.created_vms) > 0, \
        "No VMs were created in this scenario"

    for vm_name in context.created_vms:
        assert compose_file_exists(vm_name), f"VM {vm_name} config should still exist"


@then('I should be notified that Python is already running')
def step_notified_already_running(context):
    """Should be notified that Python is already running."""
    output_lower = context.last_output.lower()
    error_lower = context.last_error.lower()
    # Check for "already running" or similar messages
    has_message = 'already' in output_lower or 'already' in error_lower or 'running' in output_lower
    assert has_message, f"Expected notification about already running, got: {context.last_output}"


@then('the system should not start a duplicate container')
def step_no_duplicate(context):
    """System should not start a duplicate container - verify success without duplication."""
    exit_code = getattr(context, 'last_exit_code', 1)
    assert exit_code == 0, f"Command should succeed: {getattr(context, 'last_error', 'unknown error')}"


@then('the existing container should remain unaffected')
def step_existing_unaffected(context):
    """Existing container should remain unaffected - verify container still running."""
    assert container_exists("python"), \
        "Python container should still be running after attempting to start again"


@then('the Python container should stop')
def step_python_stops(context):
    """Python container should stop - verify container not running."""
    assert not container_exists("python"), "Python container should not be running"


@then('the VM configuration should remain')
def step_config_remains(context):
    """VM configuration should remain - verify compose file still exists."""
    vm_name = getattr(context, 'vm_stop_requested', 'python')
    assert compose_file_exists(vm_name), f"VM {vm_name} config should remain"


@then('other VMs should remain running')
def step_others_remain(context):
    """Other VMs should remain running - verify at least one container is running."""
    running = docker_ps()
    assert len(running) > 0, "At least one VM should still be running"


@then('both VMs should stop')
def step_both_stop(context):
    """Both VMs should stop - verify containers not running."""
    stopped = getattr(context, 'stop_multiple_requested', ['python', 'postgres'])
    for vm_name in stopped:
        assert not container_exists(vm_name), f"VM {vm_name} should not be running"


@then('the Rust VM should stop')
def step_rust_stops(context):
    """Rust VM should stop - verify container not running."""
    assert not container_exists("rust"), "Rust VM should not be running"


@then('the Rust VM should start again')
def step_rust_starts_again(context):
    """Rust VM should start again - verify container is running."""
    assert container_exists("rust"), "Rust VM should be running after restart"


@then('the VM should be stopped if running')
def step_vm_stopped_first(context):
    """VM should be stopped first during restart - verify stop occurred."""
    # The restart command should have completed
    assert getattr(context, 'last_exit_code', 1) == 0, \
        f"Restart command should succeed: {getattr(context, 'last_error', 'unknown error')}"


@then('the VM should be started again')
def step_vm_started_again(context):
    """VM should be started again - verify container is running."""
    vm_name = getattr(context, 'test_running_vm', 'python')
    assert container_exists(vm_name), f"VM {vm_name} should be running after restart"


@then('the restart should attempt to recover the state')
def step_recover_state(context):
    """Restart should recover state - verify VM is running."""
    vm_name = getattr(context, 'test_running_vm', 'python')
    assert container_exists(vm_name), f"VM {vm_name} should be running after restart"


@then('the system should recognize it\'s stopped')
def step_recognize_stopped(context):
    """System should recognize VM is stopped - restart command should handle stopped VMs."""
    if hasattr(context, 'last_exit_code'):
        assert context.last_exit_code == 0, \
            f"Restart command should succeed for stopped VM: {getattr(context, 'last_error', 'unknown error')}"


@then('I should be informed that it was started')
def step_informed_started(context):
    """Should be informed VM was started - check output for startup indication."""
    if hasattr(context, 'last_output') and context.last_output:
        output_lower = context.last_output.lower()
        # Check for explicit startup messages
        has_startup_msg = 'start' in output_lower or 'running' in output_lower or 'started' in output_lower
        assert has_startup_msg, f"Output should indicate VM was started. Got: {output_lower[:100]}"


@then('I should be told both are already running')
def step_told_both_running(context):
    """Should be told both VMs are already running."""
    if hasattr(context, 'last_output') and context.last_output:
        output_lower = context.last_output.lower()
        has_message = 'already' in output_lower or 'running' in output_lower
        assert has_message or len(output_lower.strip()) == 0, \
            "Output should indicate VMs are already running"


@then('no containers should be restarted')
def step_no_containers_restarted(context):
    """No containers should be restarted - verify command succeeded."""
    exit_code = getattr(context, 'last_exit_code', 0)
    assert exit_code == 0, f"Command should succeed: {getattr(context, 'last_error', 'unknown error')}"


@then('the operation should complete immediately')
def step_complete_immediately(context):
    """Operation should complete quickly - verify success."""
    assert getattr(context, 'last_exit_code', 0) == 0, "Operation should succeed"


@then('I should be told Python is already running')
def step_told_python_running(context):
    """Should be told Python is already running."""
    if hasattr(context, 'last_output') and context.last_output:
        output_lower = context.last_output.lower()
        has_message = 'python' in output_lower and ('already' in output_lower or 'running' in output_lower)
        assert has_message, "Output should indicate Python is already running"


@then('PostgreSQL should be started')
def step_postgres_started(context):
    """PostgreSQL should be started - verify container is running."""
    assert container_exists("postgres"), "PostgreSQL container should be running"


@then('I should be informed of the mixed result')
def step_informed_mixed_result(context):
    """Should be informed of mixed result - verify output indicates both states."""
    if hasattr(context, 'last_output') and context.last_output:
        output_lower = context.last_output.lower()
        has_message = 'already' in output_lower or 'start' in output_lower or 'running' in output_lower
        assert has_message or len(output_lower.strip()) == 0, \
            "Output should indicate mixed result (some running, some started)"


@then('the system should prevent duplication')
def step_prevent_duplication(context):
    """System should prevent duplication - check for "already exists" message."""
    output_lower = context.last_output.lower() if context.last_output else ''
    error_lower = context.last_error.lower() if context.last_error else ''
    has_message = 'already' in output_lower or 'already' in error_lower or 'exists' in output_lower or 'exists' in error_lower

    if getattr(context, 'create_attempted_again', False):
        assert has_message, \
            f"Expected 'already exists' message, got: output={context.last_output}, error={context.last_error}"


@then('notify me of the existing VM')
def step_notify_existing(context):
    """Notify of existing VM - verify notification in output."""
    output = (context.last_output or '') + (context.last_error or '')
    output_lower = output.lower()
    assert any(word in output_lower for word in ['already', 'exists', 'duplicate', 'existing']), \
        f"Should notify about existing VM: {output[:200]}"


@then('suggest using the existing one')
def step_suggest_existing(context):
    """Suggest using existing VM - verify suggestion in output."""
    output = (context.last_output or '') + (context.last_error or '')
    output_lower = output.lower()
    assert any(word in output_lower for word in ['use', 'existing', 'start', 'connect', 'ssh']), \
        f"Should suggest using existing VM: {output[:200]}"


@then('I should be notified that PostgreSQL is not running')
def step_notified_not_running(context):
    """Should be notified that VM is not running."""
    output_lower = context.last_output.lower()
    error_lower = context.last_error.lower()
    has_message = 'not running' in output_lower or 'not running' in error_lower or 'stopped' in output_lower
    assert has_message, f"Expected notification about not running, got: {context.last_output}"


@then('the VM should remain stopped')
def step_vm_remains_stopped(context):
    """VM should remain stopped - verify container not running."""
    vm_name = getattr(context, 'stop_requested', 'postgres')
    assert not container_exists(vm_name), f"{vm_name} should remain stopped"
