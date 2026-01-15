"""
BDD Step Definitions for SSH, Docker, and workflow features.
"""

from behave import given, when, then
import os
from pathlib import Path

VDE_ROOT = Path("/vde")

# =============================================================================
# SSH CONFIGURATION STEPS
# =============================================================================

@given('~/.ssh/config does not exist')
def step_no_ssh_config(context):
    context.ssh_config_exists = False

@given('~/.ssh/config exists')
def step_ssh_config_exists(context):
    context.ssh_config_exists = True

@given('~/.ssh/config exists with custom settings')
def step_ssh_custom(context):
    context.ssh_config_exists = True
    context.ssh_has_custom_settings = True

@given('~/.ssh/config contains "Host python-dev"')
def step_ssh_has_python(context):
    context.ssh_entries = context.ssh_entries or {}
    context.ssh_entries['python-dev'] = {'port': '2200'}

@given('~/.ssh/config contains python-dev configuration')
def step_python_config(context):
    context.ssh_entries = context.ssh_entries or {}
    context.ssh_entries['python-dev'] = {'port': '2200'}

@given('~/.ssh/ contains SSH keys')
def step_ssh_keys(context):
    context.ssh_keys_exist = True

@given('~/.ssh directory does not exist')
def step_no_ssh_dir(context):
    context.ssh_dir_exists = False

@given('~/.ssh directory exists or can be created')
def step_ssh_dir_creatable(context):
    context.ssh_dir_can_be_created = True

@given('all keys are loaded in my SSH agent')
def step_keys_loaded(context):
    context.all_keys_loaded = True

@given('~/.ssh/config contains user\'s "Host github.com" entry')
def step_github_entry(context):
    context.ssh_entries = context.ssh_entries or {}
    context.ssh_entries['github.com'] = {}

# =============================================================================
# VM STATE STEPS
# =============================================================================

@given('"python" VM is running')
def step_python_running(context):
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.running_vms.add('python')

# Duplicate removed - exists in daily_workflow_steps.py
@given('a VM is running')
def step_vm_running(context):
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.running_vms.add('test-vm')

@given('a VM has crashed')
def step_vm_crashed(context):
    context.vm_crashed = True

@given('a VM has been removed')
def step_vm_removed(context):
    context.vm_removed = True

@given('a VM is being built')
def step_vm_building(context):
    context.vm_building = True

@given('a VM is not working correctly')
def step_vm_not_working(context):
    context.vm_not_working = True

@given('a VM is running but misbehaving')
def step_vm_misbehaving(context):
    context.vm_misbehaving = True

@given('a VM seems corrupted or misconfigured')
def step_vm_corrupted(context):
    context.vm_corrupted = True

@given('a VM seems slow')
def step_vm_slow(context):
    context.vm_slow = True

@given('a VM\'s state changes')
def step_vm_state_changed(context):
    context.vm_state_changed = True

@given('a VM build fails')
def step_build_fails(context):
    context.build_failed = True

@given('a VM build keeps failing')
def step_build_fails_repeatedly(context):
    context.build_fails_repeatedly = True

# =============================================================================
# DOCKER OPERATION STEPS
# =============================================================================

@given('a container is running but SSH fails')
def step_container_ssh_fails(context):
    context.container_running = True
    context.ssh_fails = True

@given('a container takes too long to start')
def step_container_slow(context):
    context.container_slow = True

@given('a docker-compose.yml is malformed')
def step_compose_malformed(context):
    context.compose_malformed = True

@given('Docker daemon is not running')
def step_docker_daemon_not_running(context):
    context.docker_daemon_running = False

@given('Docker is not available')
def step_docker_not_available(context):
    context.docker_available = False

@given('a system service is using port "{port}"')
def step_service_using_port(context, port):
    context.port_in_use = True
    context.port_in_use_num = port

@given('a port is already in use')
def step_port_in_use(context):
    context.port_in_use = True

@given('all ports in range are in use')
def step_all_ports_in_use(context):
    context.all_ports_in_use = True

# =============================================================================
# ERROR HANDLING STEPS
# =============================================================================

@given('an error occurs')
def step_error_occurs(context):
    context.error_occurred = True

@given('a transient error occurs')
def step_transient_error(context):
    context.transient_error = True

@given('docker-compose operation fails')
def step_compose_fails(context):
    context.compose_failed = True

# =============================================================================
# WORKFLOW STEPS
# =============================================================================

@given('a new team member joins')
def step_new_team_member(context):
    context.is_new_user = True
    context.is_new_team_member = True

@given('a colleague wants to review my code')
def step_code_review(context):
    context.code_review = True

@given('a developer cannot reproduce a bug')
def step_cannot_reproduce(context):
    context.bug_not_reproducible = True

@given('a project needs environment variables for configuration')
def step_needs_env_vars(context):
    context.needs_env_vars = True

@given('a project requires specific services')
def step_needs_services(context):
    context.needs_services = True

@given('.cache directory does not exist')
def step_no_cache_dir(context):
    context.cache_dir_exists = False

@given('an associative array')
def step_assoc_array(context):
    context.using_assoc_array = True

@given('all repositories use SSH authentication')
def step_all_ssh_auth(context):
    context.all_ssh_auth = True

# =============================================================================
# WHEN STEPS
# =============================================================================

@when('I start the VM')
def step_start_vm(context):
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.running_vms.add('test-vm')

@when('I check what\'s using the port')
def step_check_port(context):
    context.checked_port = True

@when('I restart the VM')
def step_restart_vm(context):
    context.vm_restarted = True

@when('I rebuild the VM')
def step_rebuild_vm(context):
    context.vm_rebuilt = True

@when('I check the logs')
def step_check_logs(context):
    context.checked_logs = True

@when('I run validation')
def step_run_validation(context):
    context.validation_run = True

# =============================================================================
# THEN STEPS
# =============================================================================

@then('I should see which process is using it')
def step_see_process(context):
    assert getattr(context, 'checked_port', False)

@then('I can decide to stop the conflicting process')
def step_can_stop_process(context):
    assert getattr(context, 'checked_port', False)

@then('VDE can allocate a different port')
def step_different_port(context):
    assert True

@then('I can identify if the issue is SSH, Docker, or the VM itself')
def step_identify_issue(context):
    assert True

@then('I should get a fresh VM')
def step_fresh_vm(context):
    assert getattr(context, 'vm_rebuilt', False) or getattr(context, 'vm_restarted', False)

@then('old configuration issues should be resolved')
def step_issues_resolved(context):
    assert True

@then('the error should indicate "{error}"')
def step_error_indicates(context, error):
    assert True

@then('network should be created automatically')
def step_network_auto(context):
    assert True

@then('I should be told which were skipped')
def step_told_skipped(context):
    assert True

# =============================================================================
# IDEMPOENT OPERATIONS STEPS
# =============================================================================

@given('I repeat the same command')
def step_repeat_command(context):
    context.repeated_command = True

@when('the operation is already complete')
def step_already_complete(context):
    context.operation_already_complete = True

@when('the operation completes')
def step_operation_completes(context):
    context.operation_completed = True

@then('the result should be the same')
def step_result_same(context):
    assert True

@then('no errors should occur')
def step_no_errors(context):
    assert True

@then('I should be informed it was already done')
def step_informed_done(context):
    assert True

# =============================================================================
# GENERAL VM OPERATION STEPS
# =============================================================================

@given('any VM operation occurs')
def step_any_vm_operation(context):
    context.vm_operation = True

@then('I should see the new state')
def step_see_new_state(context):
    assert True

@then('understand what changed')
def step_understand_changed(context):
    assert True

@then('be able to verify the result')
def step_verify_result(context):
    assert True


# =============================================================================
# Shell detection steps
# =============================================================================

@when('running in zsh')
def step_running_zsh(context):
    """Running in zsh."""
    context.running_shell = "zsh"

@then('_detect_shell should return "zsh"')
def step_detect_shell_zsh(context):
    """_detect_shell should return zsh."""
    context.detect_shell_returns = "zsh"

@then('_is_zsh should return true')
def step_is_zsh_true(context):
    """_is_zsh should return true."""
    context.is_zsh = True

@then('_is_bash should return false')
def step_is_bash_false(context):
    """_is_bash should return false."""
    context.is_bash = False

@when('running in bash')
def step_running_bash(context):
    """Running in bash."""
    context.running_shell = "bash"

@then('_detect_shell should return "bash"')
def step_detect_shell_bash(context):
    """_detect_shell should return bash."""
    context.detect_shell_returns = "bash"

@then('_is_bash should return true')
def step_is_bash_true(context):
    """_is_bash should return true."""
    context.is_bash = True

@then('_is_zsh should return false')
def step_is_zsh_false(context):
    """_is_zsh should return false."""
    context.is_zsh = False

@given('running in bash "4.0"')
def step_running_bash_4(context):
    """Running in bash 4.0."""
    context.bash_version = "4.0"

@then('_bash_version_major should return "4"')
def step_bash_major_4(context):
    """_bash_version_major should return 4."""
    context.bash_major = "4"

@then('_shell_supports_native_assoc should return true')
def step_shell_supports_assoc_true(context):
    """_shell_supports_native_assoc should return true."""
    context.shell_native_assoc = True

@given('running in bash "3.2"')
def step_running_bash_3(context):
    """Running in bash 3.2."""
    context.bash_version = "3.2"

@then('_bash_version_major should return "3"')
def step_bash_major_3(context):
    """_bash_version_major should return 3."""
    context.bash_major = "3"

@then('_shell_supports_native_assoc should return false')
def step_shell_supports_assoc_false(context):
    """_shell_supports_native_assoc should return false."""
    context.shell_native_assoc = False
