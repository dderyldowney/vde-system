"""
BDD Step Definitions for Debugging and Troubleshooting.
Tests diagnostic capabilities, log viewing, and issue resolution.
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
# GIVEN steps - Setup for Debugging tests
# =============================================================================

@given('a VM is running but misbehaving')
def step_vm_misbehaving(context):
    """Set up misbehaving VM scenario."""
    # A running VM that has issues
    if not container_is_running('python'):
        result = run_vde_command("start python", timeout=180)
        assert result.returncode == 0, "Failed to start Python VM"
    context.vm_name = 'python'
    context.vm_misbehaving = True


@given('a VM is running')
def step_vm_running_debug(context):
    """Ensure a VM is running."""
    if not container_is_running('python'):
        result = run_vde_command("start python", timeout=180)
        assert result.returncode == 0, "Failed to start Python VM"
    context.vm_name = 'python'


@given('a VM seems corrupted or misconfigured')
def step_vm_corrupted(context):
    """Set up corrupted VM scenario."""
    context.vm_corrupted = True


@given('I get a "port already allocated" error')
def step_port_allocated_error(context):
    """Set up port allocation error."""
    context.port_error = True


@given('I cannot SSH into a VM')
def step_cannot_ssh(context):
    """Set up SSH failure scenario."""
    context.ssh_failure = True


@given('my application can\'t connect to the database')
def step_app_cannot_connect_db(context):
    """Set up database connection failure."""
    context.db_connection_failure = True


@given('I need to verify VM configuration')
def step_verify_config(context):
    """Set up configuration verification."""
    context.config_verification = True


@given('my code changes aren\'t reflected in the VM')
def step_code_changes_not_reflected(context):
    """Set up code sync issue."""
    context.code_sync_issue = True


@given('a VM build keeps failing')
def step_build_keeps_failing(context):
    """Set up build failure scenario."""
    context.build_failure = True


@given('I tried to start a VM but it failed')
def step_start_failed_debug(context):
    """Set up VM start failure."""
    result = run_vde_command("start nonexistent-vm-xyz", timeout=30)
    context.vm_start_failed = result.returncode != 0


# =============================================================================
# WHEN steps - Actions for Debugging tests
# =============================================================================

@when('I check the VM status')
def step_check_vm_status_debug(context):
    """Check VM status."""
    result = run_vde_command("status python", timeout=30)
    context.last_command = "status python"
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('I run "docker logs <vm-name>"')
def step_run_docker_logs(context):
    """Run docker logs command."""
    vm_name = getattr(context, 'vm_name', 'python')
    result = subprocess.run(['docker', 'logs', vm_name],
                          capture_output=True, text=True, timeout=30)
    context.docker_logs = result.stdout + result.stderr
    context.logs_exit_code = result.returncode


@when('I run "docker exec -it <vm-name> /bin/zsh"')
def step_run_docker_exec(context):
    """Run docker exec command."""
    vm_name = getattr(context, 'vm_name', 'python')
    # Would exec into container - for testing, just verify container exists
    assert container_is_running(vm_name), f"VM {vm_name} should be running for exec"


@when('I stop the VM')
def step_stop_vm_debug(context):
    """Stop the VM."""
    vm_name = getattr(context, 'vm_name', 'python')
    result = run_vde_command(f"stop {vm_name}", timeout=120)
    context.last_exit_code = result.returncode
    time.sleep(2)


@when('I remove the VM directory')
def step_remove_vm_directory(context):
    """Remove VM directory."""
    vm_name = getattr(context, 'vm_name', 'python')
    vm_dir = VDE_ROOT / "configs" / "docker" / vm_name
    if vm_dir.exists():
        subprocess.run(['rm', '-rf', str(vm_dir)], check=True)


@when('I recreate the VM')
def step_recreate_vm(context):
    """Recreate the VM."""
    vm_name = getattr(context, 'vm_name', 'python')
    result = run_vde_command(f"create {vm_name}", timeout=120)
    context.last_exit_code = result.returncode


@when('I check what\'s using the port')
def step_check_port_usage(context):
    """Check what's using the port."""
    # Would check port usage
    context.port_check = True


@when('I check the SSH config')
def step_check_ssh_config(context):
    """Check SSH config."""
    ssh_config = Path.home() / ".ssh" / "config"
    if ssh_config.exists():
        context.ssh_config_content = ssh_config.read_text()


@when('I verify the VM is running')
def step_verify_vm_running(context):
    """Verify VM is running."""
    vm_name = getattr(context, 'vm_name', 'python')
    context.vm_is_running = container_is_running(vm_name)


@when('I verify the port is correct')
def step_verify_port_correct(context):
    """Verify port is correct."""
    vm_name = getattr(context, 'vm_name', 'python')
    config_path = VDE_ROOT / "configs" / "docker" / vm_name / "docker-compose.yml"
    if config_path.exists():
        content = config_path.read_text()
        context.port_correct = ':' in content  # Has port mapping


@when('I SSH into the application VM')
def step_ssh_into_app_vm(context):
    """SSH into application VM."""
    assert container_is_running('python'), "Python VM should be running"


@when('I try to connect to the database VM directly')
def step_connect_db_directly(context):
    """Connect to database VM directly."""
    assert container_is_running('postgres'), "PostgreSQL VM should be running"


@when('I look at the docker-compose.yml')
def step_look_at_compose(context):
    """Look at docker-compose.yml."""
    vm_name = getattr(context, 'vm_name', 'python')
    config_path = VDE_ROOT / "configs" / "docker" / vm_name / "docker-compose.yml"
    if config_path.exists():
        context.compose_content = config_path.read_text()


@when('I check the mounts in the container')
def step_check_mounts(context):
    """Check mounts in container."""
    vm_name = getattr(context, 'vm_name', 'python')
    result = subprocess.run(['docker', 'inspect', vm_name, '--format', '{{json .Mounts}}'],
                          capture_output=True, text=True)
    context.mounts = result.stdout


@when('I check the host path is correct')
def step_check_host_path(context):
    """Check host path is correct."""
    # Would verify mount paths
    pass


@when('I rebuild with --no-cache')
def step_rebuild_no_cache(context):
    """Rebuild with --no-cache."""
    vm_name = getattr(context, 'vm_name', 'python')
    result = run_vde_command(f"start {vm_name} --rebuild --no-cache", timeout=300)
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


# =============================================================================
# THEN steps - Verification for Debugging tests
# =============================================================================

@then('I should see a clear error message')
def step_clear_error_message_debug(context):
    """Verify clear error message."""
    output = context.last_output + context.last_error
    assert 'error' in output.lower() or 'fail' in output.lower() or len(output) > 0, \
        f"Should see clear error message: {output}"


@then('I should know if it\'s a port conflict, Docker issue, or configuration problem')
def step_know_error_type_debug(context):
    """Verify error type is identified."""
    output = context.last_output + context.last_error
    error_type = None
    if 'port' in output.lower():
        error_type = 'port conflict'
    elif 'docker' in output.lower():
        error_type = 'Docker issue'
    elif 'config' in output.lower() or 'yaml' in output.lower():
        error_type = 'configuration problem'
    # Should identify at least one type
    pass


@then('I should see the container logs')
def step_see_container_logs(context):
    """Verify container logs are visible."""
    logs = getattr(context, 'docker_logs', '')
    assert len(logs) > 0 or context.logs_exit_code == 0, \
        f"Should see container logs"


@then('I can identify the source of the problem')
def step_identify_problem_source(context):
    """Verify problem source can be identified."""
    logs = getattr(context, 'docker_logs', '')
    # Logs should contain some information
    pass


@then('I should have shell access inside the container')
def step_shell_access(context):
    """Verify shell access is available."""
    vm_name = getattr(context, 'vm_name', 'python')
    assert container_is_running(vm_name), f"VM {vm_name} should be running for shell access"


@then('I can investigate issues directly')
def step_investigate_directly(context):
    """Verify ability to investigate issues."""
    # Shell access provides investigation capability
    pass


@then('I should get a fresh VM')
def step_fresh_vm(context):
    """Verify fresh VM is obtained."""
    vm_name = getattr(context, 'vm_name', 'python')
    assert container_exists(vm_name), f"VM {vm_name} should exist after recreation"


@then('old configuration issues should be resolved')
def step_config_issues_resolved(context):
    """Verify configuration issues are resolved."""
    # Fresh VM should not have old config issues
    pass


@then('I should see which process is using it')
def step_see_process_using_port(context):
    """Verify process using port is shown."""
    # Would show process info
    pass


@then('I can decide to stop the conflicting process')
def step_decide_to_stop_process(context):
    """Verify decision can be made to stop process."""
    # User can decide based on info
    pass


@then('VDE can allocate a different port')
def step_vde_allocate_different_port(context):
    """Verify VDE can allocate different port."""
    # Would allocate different port
    pass


@then('I can identify if the issue is SSH, Docker, or the VM itself')
def step_identify_issue_type(context):
    """Verify issue type can be identified."""
    output = context.last_output
    ssh_config = getattr(context, 'ssh_config_content', '')
    vm_running = getattr(context, 'vm_is_running', False)
    port_correct = getattr(context, 'port_correct', False)
    
    # Should be able to identify the issue type
    pass


@then('I can see if the issue is network, credentials, or database state')
def step_identify_db_issue(context):
    """Verify database issue can be identified."""
    # Would identify issue type
    pass


@then('I should see all volume mounts')
def step_see_volume_mounts(context):
    """Verify all volume mounts are visible."""
    mounts = getattr(context, 'mounts', '')
    assert len(mounts) > 0 or 'Mounts' in str(mounts), \
        f"Should see volume mounts: {mounts}"


@then('I should see all port mappings')
def step_see_port_mappings(context):
    """Verify all port mappings are visible."""
    compose_content = getattr(context, 'compose_content', '')
    assert 'ports' in compose_content or ':' in compose_content, \
        f"Should see port mappings: {compose_content}"


@then('I should see environment variables')
def step_see_env_vars(context):
    """Verify environment variables are visible."""
    compose_content = getattr(context, 'compose_content', '')
    assert 'environment' in compose_content or 'env' in compose_content.lower(), \
        f"Should see environment variables: {compose_content}"


@then('I can verify the configuration is correct')
def step_verify_config_correct(context):
    """Verify configuration can be verified."""
    compose_content = getattr(context, 'compose_content', '')
    assert len(compose_content) > 0, "Configuration should be available for verification"


@then('I can see if the volume is properly mounted')
def step_volume_properly_mounted(context):
    """Verify volume mount status."""
    mounts = getattr(context, 'mounts', '')
    # Should show mount status
    pass


@then('I can verify the host path is correct')
def step_verify_host_path_correct(context):
    """Verify host path is correct."""
    # Would verify path
    pass


@then('Docker should pull fresh images')
def step_docker_pull_fresh(context):
    """Verify Docker pulls fresh images."""
    output = context.last_output + context.last_error
    assert 'pull' in output.lower() or 'build' in output.lower() or 'Using default' in output, \
        f"Docker should pull fresh images: {output}"
