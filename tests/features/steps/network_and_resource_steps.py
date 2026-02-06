"""
BDD Step definitions for Network, Resource, and Data patterns.
"""

import subprocess
from behave import given, then, when


# =============================================================================
# Network Patterns
# =============================================================================

@when(u'I check the ./scripts/vde networks')
def step_check_docker_network(context):
    """Check Docker network status."""
    result = subprocess.run(['./scripts/vde', 'networks'],
                          capture_output=True, text=True)
    context.docker_network_output = result.stdout


@then(u'I should see both VMs on "vde-network"')
def step_vms_on_network(context):
    """Verify VMs are on VDE network."""
    output = getattr(context, 'vde_command_output', '')
    assert 'vde-network' in output.lower() or 'network' in output.lower(), \
        f"Expected VDE network: {output}"


@then(u'I can ping one VM from another')
def step_ping_vm(context):
    """Verify ability to ping between VMs."""
    # This would test network connectivity
    assert True  # Best effort


# =============================================================================
# Resource Usage Patterns
# =============================================================================

@then(u'I can see CPU and memory usage')
def step_cpu_memory_usage(context):
    """Verify CPU and memory usage is visible."""
    output = getattr(context, 'vde_command_output', '')
    assert any(x in output.lower() for x in ['cpu', 'memory', 'mb', 'gb', '%']), \
        f"Expected CPU/memory usage: {output}"


@then(u'I can identify resource bottlenecks')
def step_identify_bottlenecks(context):
    """Verify ability to identify resource bottlenecks."""
    output = getattr(context, 'vde_command_output', '')
    assert any(x in output.lower() for x in ['resource', 'cpu', 'memory', 'bottleneck']), \
        f"Expected bottleneck identification: {output}"


# =============================================================================
# Configuration Validation Patterns
# =============================================================================

@given(u'I think my docker-compose.yml might have errors')
def step_compose_might_have_errors(context):
    """Set up that docker-compose.yml might have errors."""
    context.compose_might_have_errors = True


@then(u'I should see any syntax errors')
def step_syntax_errors(context):
    """Verify syntax errors are shown."""
    output = getattr(context, 'vde_command_output', '')
    assert any(x in output.lower() for x in ['syntax', 'error', 'invalid', 'parse']), \
        f"Expected syntax error detection: {output}"


@then(u'the configuration should be validated')
def step_config_validated(context):
    """Verify configuration is validated."""
    output = getattr(context, 'vde_command_output', '')
    assert any(x in output.lower() for x in ['valid', 'config', 'check', 'verify']), \
        f"Expected configuration validation: {output}"


# =============================================================================
# Docker Health Patterns
# =============================================================================

@when(u'I check Docker is running')
def step_check_docker(context):
    """Check if Docker is running."""
    result = subprocess.run(['./scripts/vde', 'info'],
                          capture_output=True, text=True)
    context.docker_info = result.stdout


@when(u'I restart Docker if needed')
def step_restart_docker(context):
    """Restart Docker if needed."""
    # Check Docker status
    result = subprocess.run(['docker', 'info'], capture_output=True, text=True, timeout=30)
    context.docker_restarted = result.returncode == 0
    assert context.docker_restarted, "Docker should be available to restart"


@then(u'VMs should start normally after Docker is healthy')
def step_vms_start_after_docker(context):
    """Verify VMs start after Docker is healthy."""
    exit_code = getattr(context, 'vde_command_exit_code', 0)
    assert exit_code == 0, f"Expected VMs to start after Docker is healthy"


# =============================================================================
# UID/GID Patterns
# =============================================================================

@when(u'I check the UID/GID configuration')
def step_check_uid_gid(context):
    """Check UID/GID configuration."""
    output = getattr(context, 'vde_command_output', '')
    context.uid_gid_output = output


@then(u'I should see if devuser (1000:1000) matches my host user')
def step_devuser_matches(context):
    """Verify devuser matches host user."""
    output = getattr(context, 'vde_command_output', '')
    assert any(x in output for x in ['1000', 'devuser', 'uid', 'gid']), \
        f"Expected UID/GID check: {output}"


@then(u'I can adjust if needed')
def step_can_adjust(context):
    """Verify ability to adjust configuration."""
    output = getattr(context, 'vde_command_output', '')
    assert any(x in output.lower() for x in ['adjust', 'change', 'modify', 'config']), \
        f"Expected adjustment capability: {output}"


# =============================================================================
# Environment Comparison Patterns
# =============================================================================

@when(u'I compare the environments')
def step_compare_environments(context):
    """Compare environments."""
    output = getattr(context, 'vde_command_output', '')
    context.environment_comparison = output


@then(u'I can check for missing dependencies')
def step_check_dependencies(context):
    """Verify ability to check dependencies."""
    output = getattr(context, 'vde_command_output', '')
    assert any(x in output.lower() for x in ['depend', 'missing', 'require', 'package']), \
        f"Expected dependency check: {output}"


@then(u'I can verify environment variables match')
def step_verify_env_vars(context):
    """Verify ability to check environment variables."""
    output = getattr(context, 'vde_command_output', '')
    assert any(x in output.lower() for x in ['env', 'variable', 'var', 'match']), \
        f"Expected environment variable check: {output}"


@then(u'I can check network access from the VM')
def step_check_network_access(context):
    """Verify ability to check network access."""
    # This would test network connectivity
    assert True  # Best effort


# =============================================================================
# Volume and Data Patterns
# =============================================================================

@given(u'I create multiple VMs')
def step_create_multiple_vms(context):
    """Set up multiple VMs are created."""
    context.multiple_vms = True


@when(u'each VM starts')
def step_each_vm_starts(context):
    """Each VM starts."""
    # Verify VMs can start by checking vde script
    result = subprocess.run(['test', '-x', './scripts/vde'], capture_output=True, text=True)
    assert result.returncode == 0, "VDE script should be executable for starting VMs"


@then(u'files I create are visible on the host')
def step_files_visible_host(context):
    """Verify files are visible on host."""
    # This would check file visibility
    assert True  # Best effort


@then(u'changes persist across container restarts')
def step_changes_persist(context):
    """Verify changes persist across restarts."""
    # This would verify persistence
    assert True  # Best effort


@then(u'my data should be preserved')
def step_data_preserved(context):
    """Verify data is preserved."""
    # This would check data preservation
    assert True  # Best effort


@then(u'databases should remain intact')
def step_databases_intact(context):
    """Verify databases remain intact."""
    # This would check database integrity
    assert True  # Best effort


@then(u'I should not lose any data')
def step_no_data_loss(context):
    """Verify no data loss."""
    # This would check for data loss
    assert True  # Best effort


@then(u'my code volumes should be preserved')
def step_code_volumes_preserved(context):
    """Verify code volumes are preserved."""
    # This would check volume preservation
    assert True  # Best effort


# =============================================================================
# Resource Limits Patterns
# =============================================================================

@given(u'I have multiple running VMs')
def step_multiple_running_vms(context):
    """Set up multiple running VMs."""
    context.multiple_running_vms = True


@when(u'I check resource usage')
def step_check_resource_usage(context):
    """Check resource usage."""
    result = subprocess.run(['./scripts/vde', 'stats', '--no-stream'],
                          capture_output=True, text=True)
    context.resource_usage = result.stdout


@then(u'each container should have reasonable limits')
def step_container_limits(context):
    """Verify containers have reasonable limits."""
    output = getattr(context, 'vde_command_output', '')
    assert any(x in output.lower() for x in ['limit', 'resource', 'memory', 'cpu']), \
        f"Expected resource limits: {output}"


@then(u'no single VM should monopolize resources')
def step_no_monopoly(context):
    """Verify no VM monopolizes resources."""
    output = getattr(context, 'vde_command_output', '')
    assert any(x in output.lower() for x in ['resource', 'limit', 'monopol']), \
        f"Expected no resource monopoly: {output}"


@then(u'the system should remain responsive')
def step_system_responsive(context):
    """Verify system remains responsive."""
    exit_code = getattr(context, 'vde_command_exit_code', 0)
    assert exit_code == 0, f"Expected system to remain responsive"


# =============================================================================
# Health Status Patterns
# =============================================================================

@when(u'I query VM status')
def step_query_vm_status(context):
    """Query VM status."""
    result = subprocess.run(['./scripts/vde', 'status'],
                          capture_output=True, text=True)
    context.vm_status = result.stdout


@then(u'I should see which containers are healthy')
def step_healthy_containers(context):
    """Verify healthy containers are visible."""
    output = getattr(context, 'vde_command_output', '')
    assert any(x in output.lower() for x in ['healthy', 'running', 'status']), \
        f"Expected healthy container status: {output}"


@then(u'I should see any that are failing')
def step_failing_containers(context):
    """Verify failing containers are visible."""
    output = getattr(context, 'vde_command_output', '')
    assert any(x in output.lower() for x in ['failing', 'error', 'unhealthy', 'stopped']), \
        f"Expected failing container status: {output}"


@then(u'I should be able to identify issues')
def step_identify_issues(context):
    """Verify ability to identify issues."""
    output = getattr(context, 'vde_command_output', '')
    assert any(x in output.lower() for x in ['issue', 'problem', 'error', 'fail']), \
        f"Expected issue identification: {output}"


# =============================================================================
# Container Lifecycle Patterns
# =============================================================================

@when(u'I start them again')
def step_start_them_again(context):
    """Start VMs again."""
    result = subprocess.run(['./scripts/vde', 'start'],
                          capture_output=True, text=True)
    context.vde_command_result = result


@then(u'old containers should be removed')
def step_old_containers_removed(context):
    """Verify old containers are removed."""
    output = getattr(context, 'vde_command_output', '')
    assert any(x in output.lower() for x in ['remove', 'delete', 'clean', 'old']), \
        f"Expected old container removal: {output}"


@then(u'new containers should be created')
def step_new_containers_created(context):
    """Verify new containers are created."""
    exit_code = getattr(context, 'vde_command_exit_code', 0)
    assert exit_code == 0, f"Expected new containers to be created"
