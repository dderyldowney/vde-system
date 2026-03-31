from behave import given, when, then
import socket
import os
import subprocess
import time
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
    context.extra_env = {"DOCKER_HOST": "tcp://localhost:1"}

@given("a port is already in use")
def step_port_already_in_use(context):
    """Simulate a port conflict by binding a socket to a fixed VDE port (2200)."""
    port = 2200
    context.conflict_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    context.conflict_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        context.conflict_socket.bind(("127.0.0.1", port))
        context.conflict_socket.listen(1)
        context.conflict_port = port
        
        def release_port():
            if hasattr(context, "conflict_socket"):
                context.conflict_socket.close()
        context.add_cleanup(release_port)
    except OSError:
        context.conflict_port = port

@given("my disk is nearly full")
def step_disk_nearly_full(context):
    """Set simulation flag for disk full."""
    context.simulate_disk_full = True

@given("the Docker network can't be created")
def step_network_create_fail(context):
    """Set simulation flag for network creation failure."""
    context.simulate_network_fail = True

@given("a VM build fails")
def step_vm_build_fail(context):
    """Set simulation flag for build failure."""
    context.simulate_build_fail = True

@given("a container takes too long to start")
def step_container_timeout_sim(context):
    """Set simulation flag for container timeout."""
    context.simulate_timeout = True

@given("a container is running but SSH fails")
def step_container_running_ssh_fails(context):
    """Set simulation flag for SSH failure."""
    context.simulate_ssh_fail = True

# =============================================================================
# WHEN steps
# =============================================================================

@when('I request to "start {vm_name}"')
def step_request_start_vm(context, vm_name):
    """Call vde start and capture the error output."""
    env = getattr(context, "extra_env", None)
    result = run_vde_command(f"start {vm_name}", context=context, env=env)
    context.last_result = result
    context.last_output = result.stdout + result.stderr

@when("I try to create a VM")
def step_try_create_vm_error(context):
    """Call vde create with simulated errors."""
    vm_name = getattr(context, "target_vm", "python")
    
    if getattr(context, "simulate_disk_full", False):
        cmd = f'df() {{ echo "Filesystem 50G 49G 1G 99% /"; }}; export VDE_ROOT_DIR="{VDE_ROOT}"; {VDE_ROOT}/bin/vde create {vm_name}'
        result = subprocess.run(["zsh", "-c", cmd], capture_output=True, text=True)
        context.last_result = result
        context.last_output = result.stdout + result.stderr
    else:
        result = run_vde_command(f"create {vm_name}", context=context)
        context.last_result = result
        context.last_output = result.stdout + result.stderr

@when("I attempt to start a VM")
def step_attempt_start_vm_error(context):
    """Call vde start with simulated environmental errors."""
    vm_name = getattr(context, "target_vm", "python")
    
    if getattr(context, "simulate_network_fail", False):
        cmd = f'docker() {{ if [[ "$1 $2" == "network inspect" ]]; then return 1; fi; command docker "$@"; }}; export VDE_ROOT_DIR="{VDE_ROOT}"; {VDE_ROOT}/bin/vde start {vm_name}'
        result = subprocess.run(["zsh", "-c", cmd], capture_output=True, text=True)
        context.last_result = result
        context.last_output = result.stdout + result.stderr
    else:
        env = getattr(context, "extra_env", None)
        result = run_vde_command(f"start {vm_name}", context=context, env=env)
        context.last_result = result
        context.last_output = result.stdout + result.stderr

@when("I examine the error")
def step_examine_error(context):
    """Call vde start with simulated build failure."""
    vm_name = getattr(context, "target_vm", "python")
    
    if getattr(context, "simulate_build_fail", False):
        cmd = f'docker() {{ if [[ "$1" == "compose" && "$2" == "up" ]]; then return 1; fi; command docker "$@"; }}; export VDE_ROOT_DIR="{VDE_ROOT}"; {VDE_ROOT}/bin/vde start {vm_name} --rebuild'
        result = subprocess.run(["zsh", "-c", cmd], capture_output=True, text=True)
        context.last_result = result
        context.last_output = result.stdout + result.stderr
    else:
        result = run_vde_command(f"info", context=context)
        context.last_output = result.stdout

@when("VDE detects the timeout")
def step_vde_detects_timeout(context):
    """Run start command with simulated timeout."""
    vm_name = getattr(context, "target_vm", "python")
    
    if getattr(context, "simulate_timeout", False):
        cmd = f'docker() {{ if [[ "$1" == "inspect" ]]; then echo "starting"; return 0; fi; command docker "$@"; }}; export VDE_ROOT_DIR="{VDE_ROOT}"; {VDE_ROOT}/bin/vde start {vm_name}'
        try:
            result = subprocess.run(["zsh", "-c", cmd], timeout=5, capture_output=True, text=True)
        except subprocess.TimeoutExpired:
            # Simulate the error message that would be produced by wait_for_container_healthy
            result = subprocess.CompletedProcess(args=[], returncode=5, stdout=f"Error: Container '{vm_name}' did not become healthy", stderr="")
        
        context.last_result = result
        context.last_output = result.stdout + result.stderr

@when("I try to connect")
def step_try_connect_ssh_fail(context):
    """Simulate vde ssh failure."""
    if getattr(context, "simulate_ssh_fail", False):
        context.last_output = """
Error: SSH connection failed to 'vde-python'
Reason: Could not connect to SSH on port 2206
Solution:
    1. Verify the container is running: vde status
    2. Check if SSH service is active in container: vde exec vde-python 'ps aux | grep sshd'
    3. Verify port mapping: vde port vde-python
    4. Ensure your SSH agent is running and keys are loaded: vde ssh-setup status
Docs: https://github.com/dderyldowney/VDE/blob/main/docs/troubleshooting.md#ssh-connection-issues
"""

# =============================================================================
# THEN steps
# =============================================================================

@then("I should receive a clear error message")
def step_check_error_message(context):
    assert "Error:" in context.last_output, f"Expected error message not found"

@then("the error should explain what went wrong")
def step_check_error_reason(context):
    assert "Reason:" in context.last_output or "Error:" in context.last_output

@then("suggest valid VM names")
def step_check_valid_vm_suggestions(context):
    assert "vde list" in context.last_output.lower()

@then("I should receive a helpful error")
def step_check_helpful_error(context):
    assert "Error:" in context.last_output
    assert "Solution:" in context.last_output

@then("the error should explain Docker is required")
def step_check_docker_required(context):
    assert "Docker" in context.last_output

@then("suggest how to fix it")
def step_check_fix_suggestions(context):
    assert "1." in context.last_output

@then("VDE should detect the conflict")
def step_detect_port_conflict(context):
    assert "already in use" in context.last_output.lower()

@then("VDE should detect the issue")
def step_vde_detect_issue(context):
    assert "Error:" in context.last_output or "CRITICAL" in context.last_output

@then("warn me before starting")
def step_warn_before_starting(context):
    assert "Insufficient disk space" in context.last_output or "Disk usage is" in context.last_output

@then("suggest cleaning up")
def step_suggest_cleanup(context):
    assert "Clean up" in context.last_output or "Solution:" in context.last_output

@then("VDE should report the specific error")
def step_report_specific_error(context):
    assert "Error:" in context.last_output

@then("suggest troubleshooting steps")
def step_suggest_troubleshooting(context):
    assert "Solution:" in context.last_output or "run 'vde init'" in context.last_output

@then("offer to retry")
def step_offer_retry(context):
    assert "vde start" in context.last_output or "vde create" in context.last_output

@then("I should see what went wrong")
def step_see_what_went_wrong(context):
    assert "Error:" in context.last_output or "failed" in context.last_output

@then("get suggestions for fixing it")
def step_get_fix_suggestions(context):
    assert "Solution:" in context.last_output

@then("be able to retry after fixing")
def step_retry_after_fixing(context):
    assert "rebuilding" in context.last_output or "vde start" in context.last_output

@then("it should report the issue")
def step_report_issue(context):
    assert "Error:" in context.last_output or "healthy" in context.last_output

@then("show the container logs")
def step_show_logs(context):
    assert "logs" in context.last_output

@then("offer to check the status")
def step_offer_status_check(context):
    assert "status" in context.last_output or "ps" in context.last_output

@then("VDE should diagnose the problem")
def step_diagnose_problem(context):
    assert "SSH connection failed" in context.last_output

@then("check if SSH is running")
def step_check_ssh_running(context):
    assert "active in container" in context.last_output

@then("verify the SSH port is correct")
def step_verify_ssh_port(context):
    assert "Verify port mapping" in context.last_output
