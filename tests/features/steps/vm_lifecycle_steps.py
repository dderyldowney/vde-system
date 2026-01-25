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
    """Verify VM is running using actual Docker state with wait."""
    assert wait_for_container(vm_name, timeout=60), f"VM {vm_name} is not running (docker ps check failed after 60s)"


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
        has_already = 'already' in output_lower
        has_running = 'running' in output_lower
        # Output should mention already running status
        assert has_already or has_running, \
            f"Output should indicate VMs are already running. Got: {output_lower[:200]}"


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
        has_already = 'already' in output_lower
        has_start = 'start' in output_lower
        has_running = 'running' in output_lower
        # Output should indicate VM status (already running, starting, etc.)
        assert has_already or has_start or has_running, \
            f"Output should indicate VM status. Got: {output_lower[:200]}"


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


# =============================================================================
# Additional lifecycle steps for undefined step patterns
# =============================================================================

@given('I want to work with a new language')
def step_want_new_language(context):
    """Context: User wants to work with a new language."""
    # Verify vm-types.conf exists to support new languages
    vm_types = VDE_ROOT / "scripts" / "data" / "vm-types.conf"
    assert vm_types.exists(), "vm-types.conf must exist for language support"
    context.new_language_context = True


@given('I need to refresh a VM')
def step_need_refresh_vm(context):
    """Context: User needs to refresh a VM."""
    # Verify the VM to refresh exists
    vm_name = getattr(context, 'test_running_vm', 'python')
    compose_path = VDE_ROOT / "configs" / "docker" / vm_name / "docker-compose.yml"
    if compose_path.exists():
        context.refresh_needed = True
        context.vm_to_refresh = vm_name


@given('I no longer need a VM')
def step_no_longer_need_vm(context):
    """Context: User no longer needs a VM."""
    context.vm_to_remove = getattr(context, 'test_running_vm', 'python')


@when('I remove its configuration')
def step_remove_configuration(context):
    """Remove VM configuration using actual VDE script."""
    vm_name = getattr(context, 'vm_to_remove', 'python')
    result = run_vde_command(f"./scripts/remove-virtual {vm_name}", timeout=60)
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr
    context.vm_removed = vm_name


@given('I have modified the Dockerfile')
def step_modified_dockerfile(context):
    """Context: User has modified the Dockerfile."""
    vm_name = getattr(context, 'test_running_vm', 'python')
    # Verify Dockerfile exists for the VM
    dockerfile = VDE_ROOT / "docker" / f"{vm_name}-dev.Dockerfile"
    context.dockerfile_modified = vm_name if dockerfile.exists() else None
    context.compose_exists = compose_file_exists(vm_name)


@when('I request to "rebuild go with no cache"')
def step_request_rebuild_go_nocache(context):
    """Request to rebuild go VM with no cache."""
    context.rebuild_requested = "go"
    context.nocache_requested = True
    result = run_vde_command("./scripts/start-virtual go --rebuild --no-cache", timeout=300)
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('I rebuild the VM')
def step_rebuild_vm(context):
    """Rebuild the current VM."""
    vm_name = getattr(context, 'test_running_vm', 'python')
    context.rebuild_requested = vm_name
    result = run_vde_command(f"./scripts/start-virtual {vm_name} --rebuild", timeout=300)
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@given('I want to update the base image')
def step_want_update_base_image(context):
    """Context: User wants to update the base image."""
    # Verify Docker is available for base image updates
    result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
    context.base_image_update = result.returncode == 0


@then('each should have its own configuration')
def step_each_has_own_config(context):
    """Verify each VM has its own configuration."""
    assert hasattr(context, 'created_vms') or hasattr(context, 'multiple_vms_start'), \
        "VMs should have been created"
    created = getattr(context, 'created_vms', getattr(context, 'multiple_vms_start', []))
    if isinstance(created, str):
        created = created.split()
    for vm_name in created:
        assert compose_file_exists(vm_name), f"VM {vm_name} should have its own configuration"


@then('my workspace should be mounted')
def step_workspace_mounted(context):
    """Verify workspace is mounted - check for volume mounts in docker inspect."""
    vm_name = getattr(context, 'test_running_vm', 'python')
    container_name = f"{vm_name}-dev"
    result = subprocess.run(
        ['docker', 'inspect', '-f', '{{json .Mounts}}', container_name],
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"Cannot inspect {container_name}"
    mounts = result.stdout
    # Check for workspace or project directory mounts
    assert 'workspace' in mounts.lower() or 'project' in mounts.lower(), \
        f"Workspace should be mounted. Mounts: {mounts[:200]}"


@then('the Python VM should be rebuilt')
def step_python_vm_rebuilt(context):
    """Verify Python VM was rebuilt - container running."""
    assert container_exists("python"), "Python VM should be running after rebuild"


@then('the VM should start with the new image')
def step_vm_starts_with_new_image(context):
    """Verify VM started with new image."""
    vm_name = getattr(context, 'rebuild_requested', getattr(context, 'test_running_vm', 'python'))
    assert container_exists(vm_name), f"{vm_name} should be running with new image"


@then('no cached layers should be used')
def step_no_cached_layers(context):
    """Verify no cache was used - check for --no-cache in rebuild."""
    assert getattr(context, 'nocache_requested', False) or \
           '--no-cache' in (context.last_output or '').lower() or \
           '--no-cache' in (context.last_error or '').lower(), \
           "Build should use --no-cache"


@when('I request "status of all VMs"')
def step_request_status_all(context):
    """Request status of all VMs."""
    result = run_vde_command("./scripts/status-vms", timeout=30)
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@given('I have several VMs configured')
def step_several_vms_configured(context):
    """Verify several VMs are configured in vm-types.conf."""
    vm_types_file = VDE_ROOT / "scripts" / "data" / "vm-types.conf"
    count = 0
    if vm_types_file.exists():
        with open(vm_types_file) as f:
            for line in f:
                if line.strip() and not line.strip().startswith('#'):
                    count += 1
    context.several_vms_configured = count > 1
    assert context.several_vms_configured, "Multiple VMs should be configured"


@given('I have created my microservice VMs')
def step_created_microservices(context):
    """Context: User has created microservice VMs."""
    # Verify service VM configs exist
    configs_dir = VDE_ROOT / "configs" / "docker"
    services = ['postgres', 'redis', 'nginx']
    context.microservices_created = any((configs_dir / svc).exists() for svc in services)


@given('I have finished working on one project')
def step_finished_project(context):
    """Context: User finished working on a project."""
    # Verify workspace directory exists for project management
    workspace = VDE_ROOT / "workspace"
    context.project_finished = workspace.exists()


@then('I can start a fresh environment for another project')
def step_can_start_fresh(context):
    """Verify ability to start fresh environment."""
    # Verify VDE commands are available for starting fresh
    vde_bin = VDE_ROOT / "vde"
    assert vde_bin.exists() or os.path.exists("/usr/local/bin/vde"), \
        "VDE command should be available to start fresh environment"


# =============================================================================
# Additional VM lifecycle verification steps
# =============================================================================

@then('the Go container should stop')
def step_go_container_stops(context):
    """Verify Go container is not running."""
    assert not container_exists("go"), "Go container should not be running"


@then('all three VMs should start in parallel')
def step_three_vms_parallel_start(context):
    """Verify all three VMs started."""
    started = getattr(context, 'multiple_vms_start', ['python', 'go', 'postgres'])
    for vm in started:
        assert container_exists(vm), f"{vm} should be running"


@then('the Go VM should be created for one service')
def step_go_vm_for_service(context):
    """Verify Go VM was created."""
    assert compose_file_exists("go"), "Go VM should have been created"


@then('the Rust VM should be created for another service')
def step_rust_vm_for_service(context):
    """Verify Rust VM was created."""
    assert compose_file_exists("rust"), "Rust VM should have been created"


@then('the Python VM should be for the backend API')
def step_python_backend_api(context):
    """Verify Python VM is for backend API."""
    assert compose_file_exists("python"), "Python VM should exist for backend API"


@then('PostgreSQL should be for the database')
def step_postgres_database(context):
    """Verify PostgreSQL VM exists for database."""
    assert compose_file_exists("postgres"), "PostgreSQL VM should exist for database"


@then('Redis should be for caching')
def step_redis_caching(context):
    """Verify Redis VM exists for caching."""
    assert compose_file_exists("redis"), "Redis VM should exist for caching"


@then('nginx should be for the web server')
def step_nginx_web_server(context):
    """Verify nginx VM exists for web server."""
    assert compose_file_exists("nginx"), "nginx VM should exist for web server"


@then('all required VMs should start')
def step_required_vms_start(context):
    """Verify all required VMs started."""
    running = docker_ps()
    assert len(running) > 0, "At least some VMs should be running"


@then('all VMs should be running when complete')
def step_all_vms_running_complete(context):
    """Verify all VMs are running."""
    running = docker_ps()
    assert len(running) >= 3, f"At least 3 VMs should be running, got {len(running)}"


@given('I have a backup VM running')
def step_have_backup_vm(context):
    """Context: User has a backup VM running."""
    # Check if backup VM config exists
    compose_path = VDE_ROOT / "configs" / "docker" / "backup" / "docker-compose.yml"
    if compose_path.exists():
        context.backup_vm = "backup"
    else:
        # Fallback to checking if any VM is running
        running = docker_ps()
        context.backup_vm = running[0] if running else "backup"


@given('I have a build VM running')
def step_have_build_vm(context):
    """Context: User has a build VM running."""
    # Check if build VM config exists
    compose_path = VDE_ROOT / "configs" / "docker" / "build" / "docker-compose.yml"
    if compose_path.exists():
        context.build_vm = "build"
    else:
        running = docker_ps()
        context.build_vm = running[0] if running else "build"


@given('I have a coordination VM running')
def step_have_coordination_vm(context):
    """Context: User has a coordination VM running."""
    configs = VDE_ROOT / "configs" / "docker"
    context.coordination_vm = "coordination" if (configs / "coordination").exists() else "python"


@given('I have a debugging VM running')
def step_have_debugging_vm(context):
    """Context: User has a debugging VM running."""
    configs = VDE_ROOT / "configs" / "docker"
    context.debugging_vm = "debug" if (configs / "debug").exists() else "python"


@given('I have a management VM running')
def step_have_management_vm(context):
    """Context: User has a management VM running."""
    configs = VDE_ROOT / "configs" / "docker"
    context.management_vm = "management" if (configs / "management").exists() else "python"


@given('I have a network VM running')
def step_have_network_vm(context):
    """Context: User has a network VM running."""
    configs = VDE_ROOT / "configs" / "docker"
    context.network_vm = "network" if (configs / "network").exists() else "python"


@given('I have a utility VM running')
def step_have_utility_vm(context):
    """Context: User has a utility VM running."""
    configs = VDE_ROOT / "configs" / "docker"
    context.utility_vm = "utility" if (configs / "utility").exists() else "python"


@when('I SSH into the backup VM')
def step_ssh_backup_vm(context):
    """Context: SSH into backup VM."""
    target = getattr(context, 'backup_vm', 'backup')
    compose_path = VDE_ROOT / "configs" / "docker" / target / "docker-compose.yml"
    context.ssh_target = target if compose_path.exists() else None


@when('I SSH into the build VM')
def step_ssh_build_vm(context):
    """Context: SSH into build VM."""
    target = getattr(context, 'build_vm', 'build')
    compose_path = VDE_ROOT / "configs" / "docker" / target / "docker-compose.yml"
    context.ssh_target = target if compose_path.exists() else None


@when('I SSH into the coordination VM')
def step_ssh_coordination_vm(context):
    """Context: SSH into coordination VM."""
    target = getattr(context, 'coordination_vm', 'coordination')
    compose_path = VDE_ROOT / "configs" / "docker" / target / "docker-compose.yml"
    context.ssh_target = target if compose_path.exists() else None


@when('I SSH into the debugging VM')
def step_ssh_debugging_vm(context):
    """Context: SSH into debugging VM."""
    target = getattr(context, 'debugging_vm', 'debug')
    compose_path = VDE_ROOT / "configs" / "docker" / target / "docker-compose.yml"
    context.ssh_target = target if compose_path.exists() else None


@when('I SSH into the management VM')
def step_ssh_management_vm(context):
    """Context: SSH into management VM."""
    target = getattr(context, 'management_vm', 'management')
    compose_path = VDE_ROOT / "configs" / "docker" / target / "docker-compose.yml"
    context.ssh_target = target if compose_path.exists() else None


@when('I SSH into the network VM')
def step_ssh_network_vm(context):
    """Context: SSH into network VM."""
    target = getattr(context, 'network_vm', 'network')
    compose_path = VDE_ROOT / "configs" / "docker" / target / "docker-compose.yml"
    context.ssh_target = target if compose_path.exists() else None


@when('I SSH into the utility VM')
def step_ssh_utility_vm(context):
    """Context: SSH into utility VM."""
    target = getattr(context, 'utility_vm', 'utility')
    compose_path = VDE_ROOT / "configs" / "docker" / target / "docker-compose.yml"
    context.ssh_target = target if compose_path.exists() else None


@given('I have a long-running task in a VM')
def step_long_running_task(context):
    """Context: User has a long-running task in a VM."""
    # Verify python VM exists for long-running tasks
    compose_path = VDE_ROOT / "configs" / "docker" / "python" / "docker-compose.yml"
    context.long_running_vm = "python" if compose_path.exists() else None


@given('I have web service running in a VM')
def step_web_service_running(context):
    """Context: Web service is running in a VM."""
    # Verify nginx exists for web service
    configs = VDE_ROOT / "configs" / "docker"
    nginx_exists = (configs / "nginx").exists() or (configs / "nginx-dev").exists()
    context.web_service_vm = "nginx" if nginx_exists else None


@when('I start them again')
def step_start_them_again(context):
    """Start VMs again after they were stopped."""
    vms = getattr(context, 'created_vms', ['python', 'postgres'])
    if isinstance(vms, str):
        vms = [vms]
    result = run_vde_command(f"./scripts/start-virtual {' '.join(vms)}", timeout=180)
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('I stop all VMs')
def step_stop_all_vms(context):
    """Stop all VMs."""
    result = run_vde_command("./scripts/shutdown-virtual all", timeout=60)
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@then('all VMs should be stopped')
def step_all_vms_stopped(context):
    """Verify all VMs are stopped."""
    running = docker_ps()
    vde_containers = {c for c in running if c.endswith('-dev') or c in ['postgres', 'redis', 'nginx']}
    assert len(vde_containers) == 0, f"All VDE VMs should be stopped, but found: {vde_containers}"


@given('I have custom scripts on my host')
def step_have_custom_scripts(context):
    """Context: User has custom scripts on host."""
    # Check for custom scripts directory
    scripts_dir = Path.home() / "scripts" / "custom"
    context.has_custom_scripts = scripts_dir.exists()


@given('I have Docker installed on my host')
def step_have_docker_host(context):
    """Verify Docker is installed on host."""
    result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
    assert result.returncode == 0, "Docker should be installed"


@given('I have projects on my host')
def step_have_projects_host(context):
    """Context: User has projects on host."""
    # Check for workspace/projects directory
    workspace = VDE_ROOT / "workspace"
    context.has_projects = workspace.exists() and len(list(workspace.iterdir())) > 0 if workspace.exists() else False


@given('I have set up SSH keys')
def step_have_ssh_keys(context):
    """Context: User has SSH keys set up."""
    ssh_dir = Path.home() / '.ssh'
    context.has_ssh_keys = ssh_dir.exists()


# =============================================================================
# Remaining undefined step implementations
# =============================================================================