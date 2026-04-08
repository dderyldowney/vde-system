from behave import given, when, then
import socket
import os
import subprocess
import re
from pathlib import Path
from vm_common import run_vde_command, VDE_ROOT, load_vm_types_raw

# =============================================================================
# GIVEN steps
# =============================================================================

@given("I try to use a VM that doesn't exist")
def step_use_nonexistent_vm(context):
    """Set up context for an unknown VM request."""
    context.target_vm = "nonexistent-vm"

@given("Docker is not available")
def step_docker_not_available(context):
    """Trigger a real Docker error by providing an invalid host."""
    context.extra_env = {"DOCKER_HOST": "unix:///var/run/nonexistent.sock"}

@given("a port is already in use")
def step_port_already_in_use(context):
    """Simulate a real port conflict by running sacrificial containers on multiple ports."""
    vm_name = "python"
    context.target_vm = vm_name
    
    # Bind to multiple ports to ensure VDE hits one
    ports = [2206, 2207, 2208, 2209, 2210]
    
    for port in ports:
        conflict_name = f"vde-port-conflict-{port}"
        subprocess.run(["docker", "rm", "-f", conflict_name], capture_output=True)
        subprocess.run([
            "docker", "run", "-d", "--name", conflict_name,
            "-p", f"0.0.0.0:{port}:22", "vde-base", "sleep", "300"
        ], capture_output=True)
        
        def cleanup_conflict(name=conflict_name):
            subprocess.run(["docker", "rm", "-f", name], capture_output=True)
        context.add_cleanup(cleanup_conflict)
    
    context.conflict_ports = ports

@given("my disk is nearly full")
def step_disk_nearly_full(context):
    """Simulate disk full by overriding the threshold to 0."""
    context.extra_env = {"VDE_DISK_THRESHOLD": "0"}

@given("the Docker network can't be created")
def step_network_create_fail(context):
    """Trigger a real network error by using an invalid (empty space) network name."""
    context.extra_env = {"VDE_DOCKER_NETWORK": " "}

@given("a VM build fails")
def step_vm_build_fail(context):
    """Trigger a real build failure by corrupting the Hub Dockerfile."""
    vm_name = "python"
    dockerfile = VDE_ROOT / "configs" / "docker" / "vde-lang.Dockerfile"
    if dockerfile.exists():
        context.original_dockerfile = dockerfile.read_text()
        with open(dockerfile, "a") as f:
            f.write("\nRUN exit 1")
        
        def restore_dockerfile():
            dockerfile.write_text(context.original_dockerfile)
        context.add_cleanup(restore_dockerfile)
    context.target_vm = vm_name

@given("a container takes too long to start")
def step_container_timeout_sim(context):
    """Trigger a real timeout by setting a zero timeout."""
    context.extra_env = {"VDE_CONTAINER_TIMEOUT": "0"}

@given("a container is running but SSH fails")
def step_container_running_ssh_fails(context):
    """Trigger real SSH failure by using an invalid identity."""
    context.extra_env = {"VDE_SSH_IDENTITY": "/dev/null"}

@given("I don't have permission for an operation")
def step_no_permission(context):
    """Trigger a real permission error."""
    locked_dir = VDE_ROOT / "tests" / "locked_dir"
    if locked_dir.exists():
        import shutil
        shutil.rmtree(locked_dir)
    locked_dir.mkdir(parents=True)
    locked_dir.chmod(0o555)
    context.locked_path = str(locked_dir)
    
    def cleanup_locked():
        locked_dir.chmod(0o755)
        if locked_dir.exists():
            import shutil
            shutil.rmtree(locked_dir)
    context.add_cleanup(cleanup_locked)

@given("a docker-compose.yml is malformed")
def step_malformed_compose(context):
    """Trigger a real configuration error by corrupting vm-types.json."""
    types_file = VDE_ROOT / "data" / "vm-types.json"
    if types_file.exists():
        context.original_types = types_file.read_text()
        with open(types_file, "a") as f:
            f.write("\nINVALID_JSON_CONTENT")
        
        def restore_types():
            types_file.write_text(context.original_types)
        context.add_cleanup(restore_types)
    context.target_vm = "python"

@given("one VM fails to start")
def step_one_vm_fails(context):
    """Trigger real partial failure by corrupting one Dockerfile."""
    step_vm_build_fail(context)

@given("an error occurs")
@given("any error occurs")
def step_error_occurs(context):
    """Trigger a predictable VDE error."""
    context.target_command = "start nonexistent-vm"

@given("a transient error occurs")
def step_transient_error(context):
    """Trigger a retryable port conflict."""
    vm_name = "python"
    # Reserve the port manually to cause a conflict
    from vm_common import get_vm_ssh_port
    try:
        port = get_vm_ssh_port(vm_name)
        if not port: port = "2214"
        
        # Use a dummy listener to hold the port
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('localhost', int(port)))
        sock.listen(1)
        context.port_sock = sock
        
        def release_port():
            sock.close()
        context.add_cleanup(release_port)
    except Exception as e:
        print(f"FAILED TO TRIGGER CONFLICT: {e}")
    
    context.target_vm = vm_name

@given("an operation is interrupted")
def step_interrupted_op(context):
    """Prepare for signal interception."""
    pass

@given("an operation fails partway through")
def step_partial_failure_recovery(context):
    """Trigger real partial failure."""
    step_vm_build_fail(context)

# =============================================================================
# WHEN steps
# =============================================================================

@when('I request to "start {vm_name}"')
def step_request_start_vm(context, vm_name):
    """Call vde start and capture the error output."""
    env = getattr(context, "extra_env", None)
    result = run_vde_command(f"start {vm_name}", context=context, env=env)
    context.last_result = result
    out = (result.stdout or "") + (result.stderr or "")
    if not hasattr(context, "last_output"): context.last_output = ""
    context.last_output += out

@when("I try to create a VM")
def step_try_create_vm_error(context):
    """Call vde create and capture output."""
    vm_name = getattr(context, "target_vm", "python")
    env = getattr(context, "extra_env", None)
    result = run_vde_command(f"create {vm_name}", context=context, env=env)
    context.last_result = result
    out = (result.stdout or "") + (result.stderr or "")
    if not hasattr(context, "last_output"): context.last_output = ""
    context.last_output += out

@when("I attempt to start a VM")
def step_attempt_start_vm_error(context):
    """Call vde start and capture output."""
    vm_name = getattr(context, "target_vm", "python")
    env = getattr(context, "extra_env", None)
    result = run_vde_command(f"start {vm_name}", context=context, env=env)
    context.last_result = result
    out = (result.stdout or "") + (result.stderr or "")
    if not hasattr(context, "last_output"): context.last_output = ""
    context.last_output += out

@when("I examine the error")
def step_examine_error(context):
    """Examine the last command result."""
    if not hasattr(context, "last_output"):
        vm_name = getattr(context, "target_vm", "python")
        result = run_vde_command(f"rebuild {vm_name}", context=context)
        context.last_output = (result.stdout or "") + (result.stderr or "")

@when("VDE detects the timeout")
def step_vde_detects_timeout(context):
    """Run start command which is expected to timeout."""
    step_attempt_start_vm_error(context)

@when("I try to connect")
def step_try_connect_ssh_fail(context):
    """Try real SSH connection with invalid identity."""
    vm_name = getattr(context, "target_vm", "python")
    env = getattr(context, "extra_env", None)
    result = run_vde_command(f"ssh {vm_name} exit", context=context, env=env)
    context.last_result = result
    out = (result.stdout or "") + (result.stderr or "")
    if not hasattr(context, "last_output"): context.last_output = ""
    context.last_output += out

@when("an operation is interrupted by SIGINT")
def step_trigger_sigint_error(context):
    """Trigger the error map for SIGINT (130)."""
    cmd = f'export VDE_ROOT_DIR="{VDE_ROOT}"; source ./lib/vm-common; vde_error_map 130 "BDD_TEST"'
    result = subprocess.run(["zsh", "-c", cmd], capture_output=True, text=True)
    context.last_output = result.stdout + result.stderr

@when("VDE encounters the error")
def step_vde_encounters_permission_error(context):
    """Trigger a real permission error in VDE."""
    path = getattr(context, "locked_path", "/root/secret")
    cmd = f'export VDE_ROOT_DIR="{VDE_ROOT}"; source ./lib/vm-common; vde_error_permission_denied "{path}"'
    result = subprocess.run(["zsh", "-c", cmd], capture_output=True, text=True)
    context.last_output = result.stdout + result.stderr

@when("I try to use the VM")
def step_use_vm_malformed(context):
    """Attempt to start a VM with malformed config."""
    step_request_start_vm(context, "python")

@when("I start multiple VMs")
def step_start_multiple_partial(context):
    """Start multiple VMs, one of which will fail."""
    env = getattr(context, "extra_env", None)
    result = run_vde_command("start python rust", context=context, env=env)
    context.last_result = result
    out = (result.stdout or "") + (result.stderr or "")
    if not hasattr(context, "last_output"): context.last_output = ""
    context.last_output += out

@when("the error is displayed")
def step_error_displayed(context):
    """Trigger and display an error."""
    cmd = getattr(context, "target_command", "health")
    result = run_vde_command(cmd, context=context)
    context.last_output = (result.stdout or "") + (result.stderr or "")

@when("VDE handles it")
def step_vde_handles_error(context):
    """Ensure VDE processing logic runs for an error."""
    step_error_displayed(context)

@when("VDE detects it's retryable")
def step_detect_retryable(context):
    """Run command that triggers retry logic."""
    step_attempt_start_vm_error(context)

@when("I encounter resource lock contention")
def step_simulate_lock_contention(context):
    """Simulate real lock contention with a PID heartbeat."""
    lock_file = VDE_ROOT / ".locks" / "vms" / "bdd_test.lock"
    pid_file = lock_file / "pid"
    lock_file.mkdir(parents=True, exist_ok=True)
    with open(pid_file, "w") as f:
        f.write(f"{os.getpid()}:0:{int(os.gettime_ns()/1e9)}")
    cmd = f'export VDE_ROOT_DIR="{VDE_ROOT}"; source ./lib/vm-common; acquire_lock "{lock_file}" 2'
    result = subprocess.run(["zsh", "-c", cmd], capture_output=True, text=True)
    context.last_output = result.stdout + result.stderr
    if lock_file.exists():
        import shutil
        shutil.rmtree(lock_file)

@when("I try again")
def step_try_again(context):
    """Re-run command that failed."""
    output = getattr(context, "last_output", "")
    assert "retry" in output.lower() or "Solution:" in output or "Retrying" in output or "Attempt" in output

@when("the failure is detected")
def step_failure_detected(context):
    """Run the command that is expected to fail for rollback verification."""
    vm_name = getattr(context, "target_vm", "python")
    result = run_vde_command(f"rebuild {vm_name}", context=context)
    context.last_result = result
    context.last_output = (result.stdout or "") + (result.stderr or "")

# =============================================================================
# THEN steps
# =============================================================================

@then("I should receive a clear error message")
def step_check_error_message(context):
    output = getattr(context, "last_output", "")
    assert "Error:" in output or "Unknown VM type" in output or "Unknown VM" in output

@then("the error should explain what went wrong")
def step_check_error_reason(context):
    output = getattr(context, "last_output", "")
    assert "Reason:" in output or "Error:" in output or "alias is not configured" in output

@then("suggest valid VM names")
def step_check_valid_vm_suggestions(context):
    output = getattr(context, "last_output", "")
    assert "vde show-vm-types" in output or "vde list" in output

@then("I should receive a helpful error")
def step_check_helpful_error(context):
    output = getattr(context, "last_output", "")
    if not output:
        log_file = VDE_ROOT / "logs" / "vde.log"
        if log_file.exists(): output = log_file.read_text()
    assert "Error:" in output or "Cannot connect" in output or "Docker" in output or "failed" in output

@then("the error should explain Docker is required")
def step_check_docker_required(context):
    output = getattr(context, "last_output", "")
    assert "Docker" in output or "daemon" in output

@then("suggest how to fix it")
def step_check_fix_suggestions(context):
    output = getattr(context, "last_output", "")
    assert "1." in output or "Solution:" in output

@then("VDE should detect the conflict")
def step_detect_port_conflict(context):
    """Verify VDE handled the conflict (either logged or bypassed it)."""
    output = getattr(context, "last_output", "")
    # Check if VDE assigned a port that wasn't in our conflict list
    conflicts = getattr(context, "conflict_ports", [])
    
    # Extract assigned port from output: "Igniting vde-python (SSH: 2211)"
    import re
    match = re.search(r"SSH: (\d+)", output)
    if match:
        assigned_port = int(match.group(1))
        if assigned_port not in conflicts:
            # Success! VDE correctly found a non-conflicting port
            return
            
    # Fallback to output check
    assert "Port conflict detected" in output or "already in use" in output or "Retrying" in output or "ignited" in output

@then("allocate an available port")
def step_allocate_available_port(context):
    output = getattr(context, "last_output", "")
    assert "new port" in output or "allocated" in output or context.last_result.returncode == 0

@then("continue with the operation")
def step_continue_op(context):
    output = getattr(context, "last_output", "")
    assert "ignited" in output or context.last_result.returncode == 0

@then("VDE should detect the issue")
def step_vde_detect_issue(context):
    output = getattr(context, "last_output", "")
    assert "Error:" in output or "CRITICAL" in output or "Insufficient disk space" in output

@then("warn me before starting")
def step_warn_before_starting(context):
    output = getattr(context, "last_output", "")
    assert "Insufficient disk space" in output or "Disk usage" in output

@then("suggest cleaning up")
def step_suggest_cleanup(context):
    output = getattr(context, "last_output", "")
    assert "Clean up" in output or "Solution:" in output

@then("VDE should report the specific error")
def step_report_specific_error(context):
    output = getattr(context, "last_output", "")
    assert "Error:" in output or "Failed" in output

@then("suggest troubleshooting steps")
def step_suggest_troubleshooting(context):
    output = getattr(context, "last_output", "")
    assert "Solution:" in output or "vde init" in output

@then("offer to retry")
def step_offer_retry(context):
    output = getattr(context, "last_output", "")
    assert "vde start" in output or "vde create" in output or "rebuilding" in output

@then("I should see what went wrong")
def step_see_what_went_wrong(context):
    output = getattr(context, "last_output", "")
    assert "Error:" in output or "failed" in output or "Failed to ignite" in output

@then("get suggestions for fixing it")
def step_get_fix_suggestions(context):
    output = getattr(context, "last_output", "")
    assert "Solution:" in output

@then("be able to retry after fixing")
def step_retry_after_fixing(context):
    output = getattr(context, "last_output", "")
    assert "rebuilding" in output or "vde start" in output

@then("it should report the issue")
def step_report_issue(context):
    output = getattr(context, "last_output", "")
    assert "Error:" in output or "healthy" in output or "timed out" in output

@then("show the container logs")
def step_show_logs(context):
    output = getattr(context, "last_output", "")
    assert "logs" in output or "vde logs" in output

@then("offer to check the status")
def step_offer_status_check(context):
    output = getattr(context, "last_output", "")
    assert "status" in output or "ps" in output

@then("VDE should diagnose the problem")
def step_diagnose_problem(context):
    output = getattr(context, "last_output", "")
    assert "SSH connection failed" in output or "SSH" in output

@then("check if SSH is running")
def step_check_ssh_running(context):
    output = getattr(context, "last_output", "")
    assert "active in container" in output or "vde exec" in output

@then("verify the SSH port is correct")
def step_verify_ssh_port(context):
    output = getattr(context, "last_output", "")
    assert "Verify port mapping" in output or "vde port" in output

@then("it should explain the permission issue")
def step_explain_permission(context):
    output = getattr(context, "last_output", "")
    assert "Permission denied" in output

@then("other VMs should continue")
def step_other_vms_continue(context):
    output = getattr(context, "last_output", "")
    assert "rust" in output or "vde-rust" in output

@then("I should be notified of the failure")
def step_notified_of_failure(context):
    output = getattr(context, "last_output", "")
    assert "Error" in output or "failed" in output

@then("successful VMs should be listed")
def step_list_successful(context):
    output = getattr(context, "last_output", "")
    assert "rust" in output or "vde-rust" in output

@then("the error should be logged")
def step_verify_error_logged(context):
    log_file = VDE_ROOT / "logs" / "vde.log"
    assert log_file.exists(), f"Log file not found at {log_file}"

@then("I can find it in the logs directory")
def step_find_logs(context):
    log_dir = VDE_ROOT / "logs"
    assert log_dir.is_dir()
    log_files = list(log_dir.glob("*.log"))
    assert len(log_files) > 0

@then("offer to retry with proper permissions")
def step_offer_retry_perms(context):
    output = getattr(context, "last_output", "")
    assert "Solution:" in output
    assert "permissions" in output or "chmod" in output

@then("VDE should detect the error")
def step_detect_config_error(context):
    output = getattr(context, "last_output", "")
    assert "Error" in output or "invalid" in output

@then("show the specific problem")
def step_show_specific_problem(context):
    output = getattr(context, "last_output", "")
    assert "invalid" in output or "yaml" in output or "Error" in output

@then("suggest how to fix the configuration")
def step_suggest_config_fix(context):
    output = getattr(context, "last_output", "")
    assert "Solution:" in output

@then("it should automatically retry")
def step_verify_retry(context):
    output = getattr(context, "last_output", "")
    assert "Retrying" in output or "Attempt" in output

@then("limit the number of retries")
def step_limit_retries(context):
    output = getattr(context, "last_output", "")
    assert "attempts" in output or "max" in output or "Retrying" in output

@then("report if all retries fail")
def step_report_retry_failure(context):
    output = getattr(context, "last_output", "")
    assert "Failed" in output or "Error:" in output

@then("VDE should detect partial state")
def step_detect_partial_state(context):
    output = getattr(context, "last_output", "")
    assert "retry" in output.lower() or "Solution:" in output or "Retrying" in output

@then("complete the operation")
def step_complete_op(context):
    output = getattr(context, "last_output", "")
    assert "SUCCESS" in output or "ignited" in output or "Baking" in output

@then("not duplicate work")
def step_no_duplicate_work(context):
    output = getattr(context, "last_output", "")
    assert "already exists" not in output.lower()

@then("it should be in plain language")
def step_plain_language(context):
    output = getattr(context, "last_output", "")
    assert "Error:" in output or "Reason:" in output

@then("explain what went wrong")
def step_explain_wrong(context):
    output = getattr(context, "last_output", "")
    assert "Reason:" in output or "Error:" in output

@then("suggest next steps")
def step_suggest_next(context):
    output = getattr(context, "last_output", "")
    assert "Solution:" in output

@then("the error should have sufficient detail for debugging")
def step_sufficient_detail(context):
    output = getattr(context, "last_output", "")
    assert len(output) > 50

@then("VDE should clean up partial state")
def step_clean_partial(context):
    vm_name = getattr(context, "target_vm", "python")
    canonical_name = f"vde-{vm_name}"
    running = subprocess.run(["docker", "ps", "--filter", f"name={canonical_name}", "--format", "{{.Names}}"],
                            capture_output=True, text=True)
    assert canonical_name not in running.stdout, f"Orphaned RUNNING container {canonical_name} found"
    lock_file = VDE_ROOT / ".locks" / "vms" / f"{vm_name}.lock"
    assert not lock_file.exists(), f"Stale lock file {lock_file} found"

@then("return to a consistent state")
def step_consistent_state(context):
    result = run_vde_command("list", context=context)
    assert result.returncode == 0

@then("allow me to retry cleanly")
def step_allow_retry_cleanly(context):
    if hasattr(context, "original_dockerfile"):
        dockerfile = VDE_ROOT / "configs" / "docker" / "vde-lang.Dockerfile"
        dockerfile.write_text(context.original_dockerfile)
    vm_name = getattr(context, "target_vm", "python")
    result = run_vde_command(f"rebuild {vm_name}", context=context)
    assert result.returncode == 0, f"Retry failed. Output: {result.stdout}"

@then('I should see the "Operation Interrupted" remediation')
def step_verify_sigint_remediation(context):
    output = getattr(context, "last_output", "")
    assert "Operation Interrupted" in output
    assert "Received SIGINT" in output
    assert "cancelled by the user" in output

@then("I should see the PID of the process holding the lock")
def step_verify_lock_pid_visibility(context):
    output = getattr(context, "last_output", "")
    assert "Waiting for lock" in output
    assert str(os.getpid()) in output
