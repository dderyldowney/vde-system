from behave import given, when, then
import socket
import os
from vm_common import run_vde_command, VDE_ROOT

# =============================================================================
# GIVEN steps
# =============================================================================

@given("I try to use a VM that doesn't exist")
def step_use_nonexistent_vm(context):
    """Set up context for an unknown VM request."""
    context.target_vm = "nonexistent-vm"

@given("Docker is not available")
def step_docker_not_available(context):
    """Simulate Docker unavailability by setting a fake DOCKER_HOST."""
    # This triggers vde_error_docker_not_running in scripts that call docker
    context.extra_env = {"DOCKER_HOST": "tcp://localhost:1"}

@given("a port is already in use")
def step_port_already_in_use(context):
    """Simulate a port conflict by binding a socket to a fixed VDE port (2200)."""
    # Port 2200 is used by vde-asm
    port = 2200
    context.conflict_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    context.conflict_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        context.conflict_socket.bind(("127.0.0.1", port))
        context.conflict_socket.listen(1)
        context.conflict_port = port
        
        # Ensure cleanup
        def release_port():
            if hasattr(context, "conflict_socket"):
                context.conflict_socket.close()
        context.add_cleanup(release_port)
    except OSError:
        # If already bound, that's fine for our test
        context.conflict_port = port

# =============================================================================
# WHEN steps
# =============================================================================

@when('I request to "start {vm_name}"')
def step_request_start_vm(context, vm_name):
    """Call vde start and capture the error output."""
    # We expect this to fail if VM doesn't exist
    env = getattr(context, "extra_env", None)
    result = run_vde_command(f"start {vm_name}", context=context, env=env)
    context.last_result = result
    context.last_output = result.stdout + result.stderr

@when("I try to start a VM")
def step_try_start_vm(context):
    """Attempt to start a standard VM (e.g., python)."""
    step_request_start_vm(context, "python")

# =============================================================================
# THEN steps
# =============================================================================

@then("I should receive a clear error message")
def step_check_error_message(context):
    """Verify that the output contains the 'Error:' tag from lib/vde-errors."""
    assert "Error:" in context.last_output, f"Expected error message not found in output: {context.last_output}"

@then("the error should explain what went wrong")
def step_check_error_reason(context):
    """Verify that the output contains the 'Reason:' tag from lib/vde-errors."""
    assert "Reason:" in context.last_output, f"Expected 'Reason:' not found in output: {context.last_output}"

@then("suggest valid VM names")
def step_check_valid_vm_suggestions(context):
    """Verify that the solution suggests running 'vde list'."""
    # Matches '1. List available VMs: vde list' in vde_error_vm_not_found
    assert "vde list" in context.last_output.lower(), "Suggested fix 'vde list' not found in output"

@then("I should receive a helpful error")
def step_check_helpful_error(context):
    """Verify high-level error indicators."""
    step_check_error_message(context)
    # Ensure it's not a generic shell error but a VDE formatted one
    assert "Solution:" in context.last_output, "No solution provided in the error message"

@then("the error should explain Docker is required")
def step_check_docker_required(context):
    """Verify Docker-specific error messaging."""
    assert "Docker daemon is not running" in context.last_output, "Docker requirement not mentioned"

@then("suggest how to fix it")
def step_check_fix_suggestions(context):
    """Verify that a numbered solution list is provided."""
    assert "1." in context.last_output, "Numbered solution steps not found"

@then("VDE should detect the conflict")
def step_detect_port_conflict(context):
    """Verify port conflict detection message."""
    # Triggered by vde_error_port_in_use
    assert "already in use" in context.last_output.lower(), "Port conflict not detected in output"
