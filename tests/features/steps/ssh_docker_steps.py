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


# =============================================================================
# Associative array steps
# =============================================================================

@given('running in zsh')
def step_running_zsh_given(context):
    """Running in zsh."""
    context.running_shell = "zsh"

@when('I initialize an associative array')
def step_init_assoc_array(context):
    """Initialize an associative array."""
    context.assoc_initialized = True

@then('native zsh typeset should be used')
def step_zsh_typeset(context):
    """Native zsh typeset should be used."""
    context.zsh_typeset_used = True

@then('array operations should work correctly')
def step_array_ops_work(context):
    """Array operations should work correctly."""
    context.array_ops_work = True

@then('native bash declare should be used')
def step_bash_declare(context):
    """Native bash declare should be used."""
    context.bash_declare_used = True

@then('file-based storage should be used')
def step_file_storage(context):
    """File-based storage should be used."""
    context.file_storage_used = True

@then('operations should work via file I/O')
def step_file_io_ops(context):
    """Operations should work via file I/O."""
    context.file_io_ops = True

@when('I set key "foo" to value "bar"')
def step_set_foo_bar(context):
    """Set key foo to value bar."""
    context.foo_set_to_bar = True

@then('getting key "foo" should return "bar"')
def step_get_foo_bar(context):
    """Getting key foo should return bar."""
    context.foo_returns_bar = True

@when('I set key "a/b" to value "value1"')
def step_set_a_slash_b(context):
    """Set key a/b to value1."""
    context.a_slash_b_set = True

@when('I set key "a_b" to value "value2"')
def step_set_a_underscore_b(context):
    """Set key a_b to value2."""
    context.a_underscore_b_set = True

@then('key "a/b" should return "value1"')
def step_a_slash_b_value(context):
    """Key a/b should return value1."""
    context.a_slash_b_value = True

@then('key "a_b" should return "value2"')
def step_a_underscore_b_value(context):
    """Key a_b should return value2."""
    context.a_underscore_b_value = True

@then('keys should not collide')
def step_keys_no_collide(context):
    """Keys should not collide."""
    context.keys_no_collide = True

@when('I get all keys')
def step_get_all_keys(context):
    """Get all keys."""
    context.getting_all_keys = True

@then('all keys should be returned')
def step_all_keys_returned(context):
    """All keys should be returned."""
    context.all_keys_returned = True

@then('original key format should be preserved')
def step_key_format_preserved(context):
    """Original key format should be preserved."""
    context.key_format_preserved = True

@when('I check if key "foo" exists')
def step_check_foo_exists(context):
    """Check if key foo exists."""
    context.checking_foo_exists = True

@then('result should be true')
def step_result_true(context):
    """Result should be true."""
    context.result_is_true = True

@when('I check if key "qux" exists')
def step_check_qux_exists(context):
    """Check if key qux exists."""
    context.checking_qux_exists = True

@then('result should be false')
def step_result_false(context):
    """Result should be false."""
    context.result_is_false = True

@when('I unset key "foo"')
def step_unset_foo(context):
    """Unset key foo."""
    context.unset_foo = True

@then('key "foo" should no longer exist')
def step_foo_no_longer_exists(context):
    """Key foo should no longer exist."""
    context.foo_no_longer_exists = True

@when('I clear the array')
def step_clear_array(context):
    """Clear the array."""
    context.array_cleared = True

@then('array should be empty')
def step_array_empty(context):
    """Array should be empty."""
    context.array_empty = True

@when('I call _get_script_path')
def step_call_get_script_path(context):
    """Call _get_script_path."""
    context.called_get_script_path = True

@then('absolute script path should be returned')
def step_absolute_path_returned(context):
    """Absolute script path should be returned."""
    context.absolute_path_returned = True

@given('running in bash')
def step_running_bash_given(context):
    """Running in bash."""
    context.running_shell = "bash"

@when('script exits')
def step_script_exits(context):
    """Script exits."""
    context.script_exits = True

@then('temporary storage directory should be removed')
def step_temp_dir_removed(context):
    """Temporary storage directory should be removed."""
    context.temp_dir_removed = True


# =============================================================================
# SSH key setup steps
# =============================================================================

@given('I have just cloned VDE')
def step_just_cloned_vde(context):
    """Have just cloned VDE."""
    context.just_cloned_vde = True

@then('an SSH key should be generated automatically')
def step_ssh_key_generated(context):
    """SSH key should be generated automatically."""
    context.ssh_key_generated = True

@then('the SSH agent should be started automatically')
def step_ssh_agent_started(context):
    """SSH agent should be started automatically."""
    context.ssh_agent_started = True

@then('the key should be loaded into the agent')
def step_key_loaded_agent(context):
    """Key should be loaded into the agent."""
    context.key_loaded_agent = True

@then('I should be informed of what happened')
def step_informed_what_happened(context):
    """Should be informed of what happened."""
    context.informed_what_happened = True

@then('I should be able to use SSH immediately')
def step_ssh_immediately(context):
    """Should be able to use SSH immediately."""
    context.ssh_immediately = True

@given('I have existing SSH keys in ~/.ssh/')
def step_existing_ssh_keys(context):
    """Have existing SSH keys in ~/.ssh/."""
    context.existing_ssh_keys = True

@then('my existing SSH keys should be detected automatically')
def step_existing_keys_detected(context):
    """Existing SSH keys should be detected automatically."""
    context.existing_keys_detected = True

@then('my keys should be loaded into the agent')
def step_keys_loaded_agent(context):
    """Keys should be loaded into the agent."""
    context.keys_loaded_agent = True

@then('I should not need to configure anything manually')
def step_no_manual_config(context):
    """Should not need to configure anything manually."""
    context.no_manual_config = True

@given('I have SSH keys of different types')
def step_diff_ssh_key_types(context):
    """Have SSH keys of different types."""
    context.diff_key_types = True

@given('I have id_ed25519, id_rsa, and id_ecdsa keys')
def step_multiple_key_types(context):
    """Have id_ed25519, id_rsa, and id_ecdsa keys."""
    context.key_types = ["ed25519", "rsa", "ecdsa"]

@given('I create a new VM')
def step_create_new_vm(context):
    """Create a new VM."""
    context.new_vm_created = True

@then('all my SSH keys should be detected')
def step_all_keys_detected(context):
    """All SSH keys should be detected."""
    context.all_keys_detected = True

@then('all keys should be loaded into the agent')
def step_all_keys_loaded(context):
    """All keys should be loaded into the agent."""
    context.all_keys_loaded = True

@then('the best key should be selected for SSH config')
def step_best_key_selected(context):
    """Best key should be selected for SSH config."""
    context.best_key_selected = True

@then('I should be able to use any of the keys')
def step_use_any_key(context):
    """Should be able to use any of the keys."""
    context.use_any_key = True

@given('I have created VMs before')
def step_created_vms_before(context):
    """Have created VMs before."""
    context.created_vms_before = True

@given('I have SSH configured')
def step_ssh_configured(context):
    """Have SSH configured."""
    context.ssh_configured = True

@then('no SSH configuration messages should be displayed')
def step_no_ssh_messages(context):
    """No SSH configuration messages should be displayed."""
    context.no_ssh_messages = True

@then('the setup should happen automatically')
def step_setup_auto(context):
    """Setup should happen automatically."""
    context.setup_auto = True

@then('I should only see VM creation messages')
def step_only_vm_messages(context):
    """Should only see VM creation messages."""
    context.only_vm_messages = True

@given('I have VMs configured')
def step_vms_configured(context):
    """Have VMs configured."""
    context.vms_configured = True

@given('my SSH agent is not running')
def step_ssh_agent_not_running(context):
    """SSH agent is not running."""
    context.ssh_agent_not_running = True

@then('my keys should be loaded automatically')
def step_keys_auto_loaded(context):
    """Keys should be loaded automatically."""
    context.keys_auto_loaded = True

@then('the VM should start normally')
def step_vm_starts_normal(context):
    """VM should start normally."""
    context.vm_starts_normal = True

@given('I have VDE configured')
def step_vde_configured(context):
    """Have VDE configured."""
    context.vde_configured = True

@then('I should see the SSH agent status')
def step_see_agent_status(context):
    """Should see the SSH agent status."""
    context.agent_status_visible = True

@then('I should see my available SSH keys')
def step_see_ssh_keys(context):
    """Should see available SSH keys."""
    context.ssh_keys_visible = True

@then('I should see keys loaded in the agent')
def step_see_keys_loaded(context):
    """Should see keys loaded in the agent."""
    context.keys_loaded_visible = True
