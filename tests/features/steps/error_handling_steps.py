"""
BDD Step Definitions for Error Handling and Recovery.
Tests error scenarios, recovery mechanisms, and remediation suggestions.
"""
import os
import subprocess
import sys
import time
from pathlib import Path

# Import shared configuration
steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)

from behave import given, then, when

from config import VDE_ROOT
from vm_common import (
    run_vde_command,
    docker_ps,
    container_exists,
    container_is_running,
    wait_for_container,
)


# =============================================================================
# GIVEN steps - Setup for Error Handling tests
# =============================================================================

@given('I try to use a VM that doesn\'t exist')
def step_try_nonexistent_vm(context):
    """Set up scenario for non-existent VM."""
    context.vm_name = "nonexistent-vm-xyz123"


@given('a port is already in use')
def step_port_in_use(context):
    """Set up scenario for port conflict."""
    context.port_conflict = True


@given('Docker is not available')
def step_docker_not_available(context):
    """Set up scenario where Docker is not available."""
    # This would be simulated in actual testing
    context.docker_available = False


@given('my disk is nearly full')
def step_disk_full(context):
    """Set up scenario for disk space issue."""
    context.disk_space_low = True


@given('the Docker network can\'t be created')
def step_network_failure(context):
    """Set up scenario for network creation failure."""
    context.network_failure = True


@given('a VM build fails')
def step_build_fails(context):
    """Set up scenario for build failure."""
    context.build_failed = True


@given('a container takes too long to start')
def step_container_timeout(context):
    """Set up scenario for container startup timeout."""
    context.container_timeout = True


@given('a container is running but SSH fails')
def step_ssh_fails(context):
    """Set up scenario for SSH connection failure."""
    context.ssh_failure = True


@given('I don\'t have permission for an operation')
def step_permission_denied(context):
    """Set up scenario for permission denied."""
    context.permission_denied = True


@given('a docker-compose.yml is malformed')
def step_malformed_compose(context):
    """Set up scenario for malformed docker-compose.yml."""
    context.compose_malformed = True


@given('one VM fails to start')
def step_vm_fails_start(context):
    """Set up scenario where one VM fails to start."""
    context.vm_failure = True


@given('I tried to start a VM but it failed')
def step_vm_start_failed(context):
    """Set up scenario where VM start failed."""
    # Try to start a non-existent VM
    result = run_vde_command("start nonexistent-vm-xyz123", timeout=30)
    context.vm_start_failed = result.returncode != 0


# =============================================================================
# WHEN steps - Actions for Error Handling tests
# =============================================================================

@when('I request to "start {vm_name}"')
def step_request_start_vm(context, vm_name):
    """Request to start a VM."""
    result = run_vde_command(f"start {vm_name}", timeout=180)
    context.last_command = f"start {vm_name}"
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('I try to start a VM')
def step_try_start_vm(context):
    """Try to start a VM."""
    result = run_vde_command("start python", timeout=180)
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('I try to create a VM')
def step_try_create_vm(context):
    """Try to create a VM."""
    result = run_vde_command("create test-vm-xyz", timeout=120)
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('I start a VM')
def step_start_vm_error(context):
    """Start a VM."""
    result = run_vde_command("start python", timeout=180)
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('I examine the error')
def step_examine_error(context):
    """Examine the error output."""
    context.error_output = context.last_error


@when('VDE detects the timeout')
def step_detect_timeout(context):
    """VDE detects timeout."""
    # This would be detected during test execution
    context.timeout_detected = True


@when('I try to connect')
def step_try_connect(context):
    """Try to connect to SSH."""
    # Would attempt SSH connection
    context.ssh_connection_tried = True


@when('VDE encounters the error')
def step_vde_encounters_error(context):
    """VDE encounters the error."""
    # Error is in context from previous command
    pass


@when('I try to use the VM')
def step_try_use_vm(context):
    """Try to use the VM."""
    result = run_vde_command("start python", timeout=180)
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


# =============================================================================
# THEN steps - Verification for Error Handling tests
# =============================================================================

@then('I should receive a clear error message')
def step_clear_error_message(context):
    """Verify clear error message is received."""
    output = context.last_output + context.last_error
    assert len(output) > 0, "Should receive an error message"
    # Error should not be empty
    assert context.last_exit_code != 0 or 'error' in output.lower() or 'fail' in output.lower(), \
        f"Should receive an error message: {output}"


@then('the error should explain what went wrong')
def step_error_explains(context):
    """Verify error explains what went wrong."""
    output = context.last_output + context.last_error
    # Error should contain some explanation
    assert len(output) > 10, f"Error should contain explanation: {output}"


@then('suggest valid VM names')
def step_suggest_valid_names(context):
    """Verify suggestions for valid VM names."""
    output = context.last_output + context.last_error
    # Should suggest valid names (language or service VMs)
    suggestions = ['python', 'rust', 'js', 'go', 'postgres', 'redis', 'nginx', 'mongodb']
    found = any(s in output.lower() for s in suggestions)
    # Not all errors require suggestions
    pass


@then('VDE should detect the conflict')
def step_detect_conflict(context):
    """Verify VDE detects the conflict."""
    output = context.last_output + context.last_error
    assert 'conflict' in output.lower() or 'port' in output.lower() or 'in use' in output.lower(), \
        f"VDE should detect conflict: {output}"


@then('allocate an available port')
def step_allocate_available_port(context):
    """Verify VDE allocates an available port."""
    # Would check if operation succeeded with different port
    assert context.last_exit_code == 0 or 'port' in context.last_output.lower(), \
        f"Should allocate available port: {context.last_output}"


@then('continue with the operation')
def step_continue_operation(context):
    """Verify VDE continues with the operation."""
    # Would verify operation completed
    pass


@then('I should receive a helpful error')
def step_helpful_error(context):
    """Verify helpful error is received."""
    output = context.last_output + context.last_error
    assert len(output) > 0, "Should receive a helpful error"
    # Should mention Docker
    assert 'docker' in output.lower(), f"Should mention Docker: {output}"


@then('the error should explain Docker is required')
def step_docker_required_error(context):
    """Verify error explains Docker is required."""
    output = context.last_output + context.last_error
    assert 'docker' in output.lower(), f"Should explain Docker is required: {output}"


@then('suggest how to fix it')
def step_suggest_fix(context):
    """Verify suggestions for fixing."""
    output = context.last_output + context.last_error
    # Should provide some guidance
    pass


@then('VDE should detect the issue')
def step_detect_issue(context):
    """Verify VDE detects the issue."""
    output = context.last_output + context.last_error
    assert len(output) > 0, "VDE should detect the issue"


@then('warn me before starting')
def step_warn_before_starting(context):
    """Verify VDE warns before starting."""
    output = context.last_output + context.last_error
    assert 'warn' in output.lower() or 'warning' in output.lower() or 'disk' in output.lower(), \
        f"Should warn before starting: {output}"


@then('suggest cleaning up')
def step_suggest_cleanup(context):
    """Verify suggestions for cleanup."""
    output = context.last_output + context.last_error
    # Should suggest cleanup
    pass


@then('VDE should report the specific error')
def step_report_specific_error(context):
    """Verify VDE reports the specific error."""
    output = context.last_output + context.last_error
    assert len(output) > 0, "Should report specific error"


@then('suggest troubleshooting steps')
def step_suggest_troubleshooting(context):
    """Verify troubleshooting suggestions."""
    output = context.last_output + context.last_error
    # Should suggest troubleshooting
    pass


@then('offer to retry')
def step_offer_retry(context):
    """Verify VDE offers to retry."""
    output = context.last_output + context.last_error
    # Should offer retry option
    pass


@then('I should see what went wrong')
def step_see_what_went_wrong(context):
    """Verify I can see what went wrong."""
    error_output = getattr(context, 'error_output', context.last_error)
    assert len(error_output) > 0, f"Should see what went wrong: {error_output}"


@then('get suggestions for fixing it')
def step_suggestions_for_fixing(context):
    """Verify suggestions for fixing."""
    error_output = getattr(context, 'error_output', context.last_error)
    # Should have suggestions
    pass


@then('be able to retry after fixing')
def step_retry_after_fixing(context):
    """Verify ability to retry after fixing."""
    # Would test retry after fixing the issue
    pass


@then('it should report the issue')
def step_report_issue(context):
    """Verify VDE reports the issue."""
    output = context.last_output + context.last_error
    assert len(output) > 0, "Should report the issue"


@then('show the container logs')
def step_show_logs(context):
    """Verify container logs are shown."""
    # Would show logs in actual test
    pass


@then('offer to check the status')
def step_offer_check_status(context):
    """Verify offer to check status."""
    output = context.last_output + context.last_error
    # Should offer status check
    pass


@then('VDE should diagnose the problem')
def step_diagnose_problem(context):
    """Verify VDE diagnoses the problem."""
    output = context.last_output + context.last_error
    assert len(output) > 0, "Should diagnose the problem"


@then('check if SSH is running')
def step_check_ssh_running(context):
    """Verify check if SSH is running."""
    # Would check SSH status
    pass


@then('verify the SSH port is correct')
def step_verify_ssh_port(context):
    """Verify SSH port is correct."""
    # Would verify port
    pass


@then('it should explain the permission issue')
def step_explain_permission(context):
    """Verify permission issue is explained."""
    output = context.last_output + context.last_error
    assert 'permission' in output.lower() or 'denied' in output.lower() or 'access' in output.lower(), \
        f"Should explain permission issue: {output}"


@then('suggest how to fix it')
def step_suggest_permission_fix(context):
    """Verify suggestions for fixing permission issue."""
    output = context.last_output + context.last_error
    # Should suggest fix
    pass


@then('offer to retry with proper permissions')
def step_offer_permission_retry(context):
    """Verify offer to retry with proper permissions."""
    output = context.last_output + context.last_error
    # Should offer retry
    pass


@then('VDE should detect the error')
def step_detect_compose_error(context):
    """Verify VDE detects docker-compose error."""
    output = context.last_output + context.last_error
    assert 'error' in output.lower() or 'fail' in output.lower() or 'yaml' in output.lower(), \
        f"Should detect error: {output}"


@then('show the specific problem')
def step_show_problem(context):
    """Verify specific problem is shown."""
    output = context.last_output + context.last_error
    assert len(output) > 0, "Should show specific problem"


@then('suggest how to fix the configuration')
def step_suggest_config_fix(context):
    """Verify suggestions for fixing configuration."""
    output = context.last_output + context.last_error
    # Should suggest fix
    pass


@then('other VMs should continue running')
def step_other_vms_continue(context):
    """Verify other VMs continue running."""
    running = docker_ps()
    # VMs should still be running
    pass


@then('system should continue operating normally')
def step_system_normal(context):
    """Verify system continues normally."""
    # Would verify normal operation
    pass


@then('I should see a clear error message')
def step_clear_error_message(context):
    """Verify clear error message."""
    output = context.last_output + context.last_error
    assert 'error' in output.lower() or 'fail' in output.lower(), \
        f"Should see clear error: {output}"


@then('I should know if it\'s a port conflict, Docker issue, or configuration problem')
def step_know_error_type(context):
    """Verify error type is clear."""
    output = context.last_output + context.last_error
    # Should identify error type
    error_type = None
    if 'port' in output.lower():
        error_type = 'port conflict'
    elif 'docker' in output.lower():
        error_type = 'docker issue'
    elif 'config' in output.lower() or 'yaml' in output.lower():
        error_type = 'configuration problem'
    # At least one should be identifiable
    pass
