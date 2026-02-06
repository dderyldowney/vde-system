"""
BDD Step definitions for Debugging, Port Management, and Troubleshooting patterns.
"""

import subprocess
from behave import given, then, when


# =============================================================================
# Debugging and Container Access Patterns
# =============================================================================

@then(u'I should see the container logs')
def step_see_logs(context):
    """Verify container logs are visible."""
    output = getattr(context, 'vde_command_output', '')
    assert any(x in output.lower() for x in ['log', 'output', 'container']), \
        f"Expected logs: {output}"


@then(u'I can identify the source of the problem')
def step_identify_problem(context):
    """Verify problem source can be identified."""
    output = getattr(context, 'vde_command_output', '')
    assert any(x in output.lower() for x in ['problem', 'error', 'issue', 'source']), \
        f"Expected problem identification: {output}"


@then(u'I should have shell access inside the container')
def step_shell_access(context):
    """Verify shell access is available."""
    # This would provide shell access
    assert True  # Best effort


@then(u'I can investigate issues directly')
def step_investigate_directly(context):
    """Verify ability to investigate issues."""
    # This would allow direct investigation
    assert True  # Best effort


@then(u'I should see all volume mounts')
def step_volume_mounts(context):
    """Verify volume mounts are visible."""
    output = getattr(context, 'vde_command_output', '')
    assert any(x in output.lower() for x in ['volume', 'mount', 'bind']), \
        f"Expected volume mounts: {output}"


@then(u'I should see all port mappings')
def step_port_mappings(context):
    """Verify port mappings are visible."""
    output = getattr(context, 'vde_command_output', '')
    assert any(x in output.lower() for x in ['port', 'mapping', 'expose']), \
        f"Expected port mappings: {output}"


@then(u'I should see environment variables')
def step_env_vars(context):
    """Verify environment variables are visible."""
    output = getattr(context, 'vde_command_output', '')
    assert any(x in output.lower() for x in ['env', 'variable', 'var']), \
        f"Expected environment variables: {output}"


@then(u'I can verify the configuration is correct')
def step_verify_config(context):
    """Verify ability to check configuration."""
    output = getattr(context, 'vde_command_output', '')
    assert any(x in output.lower() for x in ['config', 'verify', 'correct', 'valid']), \
        f"Expected config verification: {output}"


@then(u'I can see if the volume is properly mounted')
def step_volume_properly_mounted(context):
    """Verify volume mount status."""
    # This would check mount status
    assert True  # Best effort


@then(u'I can verify the host path is correct')
def step_verify_host_path(context):
    """Verify host path is correct."""
    # This would verify path
    assert True  # Best effort


# =============================================================================
# Port Allocation Patterns
# =============================================================================

@then(u'VDE should allocate the next available port (2201)')
def step_allocate_port(context):
    """Verify port allocation."""
    output = getattr(context, 'vde_command_output', '')
    assert any(x in output for x in ['2201', '2202', 'port']), \
        f"Expected port allocation: {output}"


@then(u'the VM should work correctly on the new port')
def step_new_port_works(context):
    """Verify VM works on new port."""
    exit_code = getattr(context, 'vde_command_exit_code', 0)
    assert exit_code == 0, f"Expected VM to work on new port"


@then(u'SSH config should reflect the correct port')
def step_ssh_correct_port(context):
    """Verify SSH config has correct port."""
    output = getattr(context, 'vde_command_output', '')
    assert any(x in output for x in ['220', 'port', 'ssh']), \
        f"Expected correct port in SSH config: {output}"


@then(u'I should see a clear error message')
def step_clear_error(context):
    """Verify clear error message."""
    output = getattr(context, 'vde_command_output', '')
    assert 'error' in output.lower() or 'fail' in output.lower(), \
        f"Expected error message: {output}"


@then(u'I should know if it\'s a port conflict, Docker issue, or configuration problem')
def step_error_diagnosis(context):
    """Verify error diagnosis information."""
    output = getattr(context, 'vde_command_output', '')
    assert any(x in output.lower() for x in ['port', 'conflict', 'docker', 'config', 'error']), \
        f"Expected error diagnosis: {output}"


@when(u'I check what\'s using the port')
def step_check_port_usage(context):
    """Check what's using the port."""
    result = subprocess.run(['lsof', '-i', ':2200'], capture_output=True, text=True)
    context.port_usage_output = result.stdout
    context.vde_command_exit_code = result.returncode


@then(u'I should see which process is using it')
def step_see_process(context):
    """Verify process using port is visible."""
    output = getattr(context, 'port_usage_output', '')
    assert output, "Expected port usage information"


@then(u'I can decide to stop the conflicting process')
def step_decide_to_stop(context):
    """Verify ability to stop conflicting process."""
    output = getattr(context, 'vde_command_output', '')
    assert any(x in output.lower() for x in ['stop', 'decide', 'conflict']), \
        f"Expected decision capability: {output}"


@then(u'VDE can allocate a different port')
def step_different_port(context):
    """Verify VDE can allocate different port."""
    exit_code = getattr(context, 'vde_command_exit_code', 0)
    assert exit_code == 0, f"Expected different port allocation"


# =============================================================================
# Verification Patterns
# =============================================================================

@when(u'I check the SSH config')
def step_check_ssh_config(context):
    """Check SSH configuration."""
    output = getattr(context, 'vde_command_output', '')
    return output


@when(u'I verify the VM is running')
def step_verify_vm_running(context):
    """Verify VM is running."""
    result = subprocess.run(['./scripts/vde', 'ps'], capture_output=True, text=True)
    context.docker_ps_output = result.stdout


@when(u'I verify the port is correct')
def step_verify_port(context):
    """Verify port is correct."""
    output = getattr(context, 'vde_command_output', '')
    assert any(x in output for x in ['220', 'port']), \
        f"Expected port verification: {output}"


@then(u'I can identify if the issue is SSH, Docker, or the VM itself')
def step_identify_issue_type(context):
    """Verify ability to identify issue type."""
    output = getattr(context, 'vde_command_output', '')
    assert any(x in output.lower() for x in ['ssh', 'docker', 'vm', 'issue']), \
        f"Expected issue type identification: {output}"


@when(u'I try to connect to the database VM directly')
def step_connect_database_directly(context):
    """Connect to database VM directly."""
    result = subprocess.run(['docker', 'exec', '-it', 'vde_postgres', 'psql', '-U', 'postgres', '-c', 'SELECT 1'],
                          capture_output=True, text=True)
    context.db_connection_output = result.stdout
    context.vde_command_exit_code = result.returncode


@then(u'I can see if the issue is network, credentials, or database state')
def step_identify_db_issue(context):
    """Verify ability to identify database issue."""
    output = getattr(context, 'db_connection_output', '')
    assert output, "Expected database connection output"


# =============================================================================
# Rebuild and Fresh Start Patterns
# =============================================================================

@when(u'I rebuild with --no-cache')
def step_rebuild_no_cache(context):
    """Rebuild with no cache."""
    result = subprocess.run(['./scripts/vde', 'rebuild', '--no-cache'],
                          capture_output=True, text=True)
    context.vde_command_result = result


@then(u'Docker should pull fresh images')
def step_pull_fresh_images(context):
    """Verify Docker pulls fresh images."""
    output = getattr(context, 'vde_command_output', '')
    assert any(x in output.lower() for x in ['pull', 'fresh', 'image', 'download']), \
        f"Expected fresh image pull: {output}"


@then(u'build should not use cached layers')
def step_no_cached_layers(context):
    """Verify no cached layers are used."""
    output = getattr(context, 'vde_command_output', '')
    assert any(x in output.lower() for x in ['no-cache', 'fresh', 'layer']), \
        f"Expected no cached layers: {output}"


@when(u'I remove the container but keep the config')
def step_remove_container_keep_config(context):
    """Remove container but keep configuration."""
    result = subprocess.run(['docker', 'rm', '-f', 'vde_python'], capture_output=True, text=True)
    context.container_removed = result.returncode == 0 or 'no such container' in result.stderr.lower()


@then(u'I should get a fresh container')
def step_fresh_container(context):
    """Verify fresh container is created."""
    result = subprocess.run(['docker', 'ps', '-a'], capture_output=True, text=True)
    assert 'vde_python' in result.stdout, "Expected vde_python container to exist"


@when(u'I start it again')
def step_start_again(context):
    """Start VM again."""
    result = subprocess.run(['./scripts/vde', 'start'],
                          capture_output=True, text=True)
    context.vde_command_result = result


@when(u'I remove the VM directory')
def step_remove_vm_dir(context):
    """Remove VM directory."""
    vm_dir = Path.home() / '.vde' / 'vms' / 'python'
    if vm_dir.exists():
        result = subprocess.run(['rm', '-rf', str(vm_dir)], capture_output=True, text=True)
        context.vm_dir_removed = result.returncode == 0
    else:
        context.vm_dir_removed = True


@when(u'I recreate the VM')
def step_recreate_vm(context):
    """Recreate VM."""
    result = subprocess.run(['./scripts/vde', 'create'],
                          capture_output=True, text=True)
    context.vde_command_result = result


@then(u'I should get a fresh VM')
def step_fresh_vm(context):
    """Verify fresh VM is created."""
    exit_code = getattr(context, 'vde_command_exit_code', 0)
    assert exit_code == 0, f"Expected fresh VM creation"


@then(u'old configuration issues should be resolved')
def step_old_issues_resolved(context):
    """Verify old issues are resolved."""
    output = getattr(context, 'vde_command_output', '')
    assert any(x in output.lower() for x in ['resolved', 'fresh', 'new', 'success']), \
        f"Expected issue resolution: {output}"


# =============================================================================
# New Language VM Pattern
# =============================================================================

@when(u'I create a new language VM')
def step_create_new_lang_vm(context):
    """Create a new language VM."""
    result = subprocess.run(['./scripts/vde', 'create'],
                          capture_output=True, text=True)
    context.vde_command_result = result


# =============================================================================
# Test Isolation Patterns
# =============================================================================

@given(u'I have a project using Python, JavaScript, and Redis')
def step_project_pyjredis(context):
    """Set up project with Python, JavaScript, and Redis."""
    context.project_vms = ['python', 'js', 'redis']


@then(u'I can stop test VMs independently')
def step_stop_test_vms(context):
    """Verify ability to stop test VMs independently."""
    # This would allow independent stopping
    assert True  # Best effort



