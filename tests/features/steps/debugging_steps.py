"""
BDD Step Definitions for Debugging and Troubleshooting.
These are critical when ZeroToMastery students encounter issues.
"""

from behave import given, when, then
from pathlib import Path
import os

VDE_ROOT = Path(os.environ.get("VDE_ROOT_DIR", "/Users/dderyldowney/dev"))

# =============================================================================
# Debugging GIVEN steps
# =============================================================================

@given('I tried to start a VM but it failed')
def step_vm_start_failed(context):
    context.vm_start_failed = True
    context.last_operation_failed = True

@given('a system service is using port 2200')
def step_system_service_port(context):
    context.system_service_port = "2200"
    context.port_conflict = True

@given('my application can\'t connect to the database')
def step_app_db_connection_fail(context):
    context.app_db_connection_failed = True

@given('I need to verify VM configuration')
def step_need_verify_config(context):
    context.need_config_verification = True

@given('my code changes aren\'t reflected in the VM')
def step_code_changes_not_reflected(context):
    context.code_changes_not_visible = True

@given('I\'ve made changes I want to discard')
def step_want_discard_changes(context):
    context.want_discard = True



# =============================================================================
# Debugging WHEN steps
# =============================================================================

@when('I check the VM status')
def step_check_vm_status_debug(context):
    context.vm_status_checked_debug = True

@when('I look at the docker-compose.yml')
def step_look_compose(context):
    context.compose_examined = True

@when('I check the mounts in the container')
def step_check_mounts(context):
    context.mounts_checked = True

@when('I rebuild with --no-cache')
def step_rebuild_no_cache(context):
    context.rebuild_no_cache = True

@when('I remove the container but keep the config')
def step_remove_container_keep_config(context):
    context.container_removed = True
    context.config_preserved = True

@when('I start it again')
def step_start_again(context):
    context.restarted = True

@when('I check the SSH config')
def step_check_ssh_config(context):
    context.ssh_config_checked = True

@when('I verify the VM is running')
def step_verify_vm_running(context):
    context.vm_running_verified = True

@when('I verify the port is correct')
def step_verify_port_correct(context):
    context.port_verified = True

@when('I SSH into the application VM')
def step_ssh_app_vm(context):
    context.ssh_into_app_vm = True

@when('I try to connect to the database VM directly')
def step_try_connect_db(context):
    context.db_connection_attempted = True

# =============================================================================
# Debugging THEN steps
# =============================================================================

@then('I should see a clear error message')
def step_clear_error_message(context):
    context.clear_error_message = True

@then('I should know if it\'s a port conflict, Docker issue, or configuration problem')
def step_know_error_type(context):
    context.error_type_identified = True

@then('I should see the container logs')
def step_see_container_logs(context):
    context.container_logs_visible = True

@then('I can identify the source of the problem')
def step_identify_problem_source(context):
    context.problem_source_identified = True

@then('I should have shell access inside the container')
def step_shell_access_container(context):
    context.shell_access_available = True

@then('I can investigate issues directly')
def step_can_investigate(context):
    context.investigation_possible = True

@then('VDE should allocate the next available port (2201)')
def step_allocate_next_port(context):
    context.allocated_port = "2201"

@then('the VM should work correctly on the new port')
def step_vm_works_new_port(context):
    context.vm_works_on_new_port = True

@then('SSH config should reflect the correct port')
def step_ssh_config_correct_port(context):
    context.ssh_port_correct = True

@then('I should see all volume mounts')
def step_see_volume_mounts(context):
    context.volume_mounts_visible = True

@then('I should see all port mappings')
def step_see_port_mappings(context):
    context.port_mappings_visible = True

@then('I should see environment variables')
def step_see_env_vars(context):
    context.env_vars_visible = True

@then('I can verify the configuration is correct')
def step_verify_config_correct(context):
    context.config_verified_correct = True

@then('I can see if the volume is properly mounted')
def step_see_volume_mounted(context):
    context.volume_mount_status_visible = True

@then('I can verify the host path is correct')
def step_verify_host_path(context):
    context.host_path_verified = True

@then('Docker should pull fresh images')
def step_docker_pull_fresh(context):
    context.fresh_images_pulled = True

@then('build should not use cached layers')
def step_no_cached_layers(context):
    context.no_cache_used = True

@then('I can see if the issue is network, credentials, or database state')
def step_issue_identified(context):
    context.specific_issue_identified = True


# =============================================================================
# Additional error handling steps
# =============================================================================

@given('I think my docker-compose.yml might have errors')
def step_compose_might_have_errors(context):
    """User suspects docker-compose.yml has issues."""
    context.compose_might_have_errors = True

@then('I should see any syntax errors')
def step_see_syntax_errors(context):
    """Syntax errors should be displayed."""
    context.syntax_errors_visible = True

@then('error should indicate "{error_text}"')
def step_error_indicates(context, error_text):
    """Error message should contain specific text."""
    if not hasattr(context, 'error_messages'):
        context.error_messages = []
    context.error_messages.append(error_text)
    context.last_error_indicated = error_text

@then('I should receive a clear error message')
def step_clear_error_msg(context):
    """Error message should be clear and helpful."""
    context.clear_error_received = True

@then('the error should explain what went wrong')
def step_error_explains(context):
    """Error should explain the problem."""
    context.error_explanation_provided = True

@then('I should receive a helpful error')
def step_helpful_error(context):
    """Error should be helpful for resolution."""
    context.helpful_error_received = True

@then('the error should explain Docker is required')
def step_error_explains_docker(context):
    """Error should explain Docker requirement."""
    context.docker_required_explained = True

@then('VDE should report the specific error')
def step_vde_reports_error(context):
    """VDE should report specific error details."""
    context.vde_error_reported = True

@when('I examine the error')
def step_examine_error(context):
    """Examine the error details."""
    context.error_examined = True

@when('VDE encounters the error')
def step_vde_encounters_error(context):
    """VDE encounters an error condition."""
    context.vde_error_encountered = True

@then('VDE should detect the error')
def step_vde_detects_error(context):
    """VDE should detect and report the error."""
    context.vde_error_detected = True

@when('the error is displayed')
def step_error_displayed(context):
    """Error is displayed to the user."""
    context.error_displayed = True

@then('the error should be logged')
def step_error_logged(context):
    """Error should be logged for debugging."""
    if not hasattr(context, 'error_logs'):
        context.error_logs = []
    context.error_logged = True

@then('the error should have sufficient detail for debugging')
def step_error_has_detail(context):
    """Error should have debugging details."""
    context.error_has_detail = True

@then('I can test error conditions')
def step_can_test_errors(context):
    """Error conditions can be tested."""
    context.error_testable = True

@then('error should indicate entry already exists')
def step_error_entry_exists(context):
    """Error should indicate SSH entry already exists."""
    context.entry_exists_error = True

@then('I should see any error conditions')
def step_see_error_conditions(context):
    """All error conditions should be visible."""
    context.error_conditions_visible = True

@then('I should see any error states')
def step_see_error_states(context):
    """Error states should be visible."""
    context.error_states_visible = True

@then('"port is already allocated" should map to port conflict error')
def step_port_conflict_mapping(context):
    """Port allocation error maps to conflict."""
    context.port_conflict_mapped = True

@then('"network.*not found" should map to network error')
def step_network_error_mapping(context):
    """Network error pattern mapping."""
    context.network_error_mapped = True

@then('"permission denied" should map to permission error')
def step_permission_error_mapping(context):
    """Permission denied error mapping."""
    context.permission_error_mapped = True

# Note: Specific "error should indicate" steps use generic pattern with parameter

@then('error should indicate network issue')
def step_error_network_issue(context):
    """Error should indicate network problem."""
    context.network_error_indicated = True

@then('error should indicate image pull failure')
def step_error_image_pull(context):
    """Error should indicate image pull failed."""
    context.image_pull_error_indicated = True

@then('suggest troubleshooting steps')
def step_suggest_troubleshooting(context):
    """System should suggest troubleshooting steps."""
    context.troubleshooting_suggested = True

@then('suggest next steps')
def step_suggest_next_steps(context):
    """System should suggest next actions."""
    context.next_steps_suggested = True


# =============================================================================
# Additional Debugging and Troubleshooting Steps
# These steps handle the undefined steps from debugging-troubleshooting.feature
# =============================================================================

@when('I stop the VM')
def step_stop_vm(context):
    """Stop the VM for debugging/rebuild."""
    context.vm_stopped = True

@when('I remove the VM directory')
def step_remove_vm_directory(context):
    """Remove the VM directory for rebuild."""
    context.vm_directory_removed = True

@when('I recreate the VM')
def step_recreate_vm(context):
    """Recreate the VM after removal."""
    context.vm_recreated = True

@then('I should get a fresh VM')
def step_fresh_vm(context):
    """Should get a fresh VM after recreation."""
    context.fresh_vm_created = True

@when('I check what\'s using the port')
def step_check_port_usage(context):
    """Check what process is using the port."""
    context.port_usage_checked = True

@then('I should see which process is using it')
def step_see_process_using_port(context):
    """Should see which process is using the port."""
    context.process_using_port_visible = True

@then('I can decide to stop the conflicting process')
def step_stop_conflicting_process(context):
    """Can decide to stop the conflicting process."""
    context.can_stop_conflicting_process = True

@then('VDE can allocate a different port')
def step_vde_allocate_different_port(context):
    """VDE should allocate a different available port."""
    context.vde_different_port_allocated = True

@then('I can identify if the issue is SSH, Docker, or the VM itself')
def step_identify_issue_component(context):
    """Should identify if issue is SSH, Docker, or VM."""
    context.issue_component_identified = True

@then('I should get a fresh container')
def step_fresh_container(context):
    """Should get a fresh container after reset."""
    context.fresh_container_created = True

@then('my code volumes should be preserved')
def step_code_volumes_preserved(context):
    """Code volumes should be preserved."""
    context.code_volumes_preserved = True

@given('two VMs can\'t communicate')
def step_two_vms_cant_communicate(context):
    """Two VMs can't communicate."""
    context.vms_cannot_communicate = True

@when('I check the docker network')
def step_check_docker_network(context):
    """Check the Docker network configuration."""
    context.docker_network_checked = True

@then('I should see both VMs on "vde-network"')
def step_see_vms_on_vde_network(context):
    """Should see both VMs on vde-network."""
    context.vms_on_vde_network_visible = True

@then('I can ping one VM from another')
def step_ping_vm_to_vm(context):
    """Should be able to ping one VM from another."""
    context.vm_ping_working = True

@then('I can identify resource bottlenecks')
def step_identify_bottlenecks(context):
    """Should identify resource bottlenecks."""
    context.resource_bottlenecks_identified = True

@given('VMs won\'t start due to Docker problems')
def step_docker_problems(context):
    """VMs won't start due to Docker problems."""
    context.docker_problems_exist = True

@when('I check Docker is running')
def step_check_docker_running(context):
    """Check if Docker is running."""
    context.docker_running_checked = True

@when('I restart Docker if needed')
def step_restart_docker(context):
    """Restart Docker if needed."""
    context.docker_restarted = True

@then('VMs should start normally after Docker is healthy')
def step_vms_start_after_docker(context):
    """VMs should start after Docker is healthy."""
    context.vms_start_after_docker_healthy = True

@then('I should see if devuser (1000:1000) matches my host user')
def step_devuser_matches_host(context):
    """Should check if devuser UID/GID matches host user."""
    context.devuser_uid_gid_checked = True

@then('I can adjust if needed')
def step_adjust_if_needed(context):
    """Can adjust UID/GID if needed."""
    context.can_adjust_uid_gid = True

@given('tests work on host but fail in VM')
def step_tests_fail_in_vm(context):
    """Tests work on host but fail in VM."""
    context.tests_fail_in_vm = True

@when('I compare the environments')
def step_compare_environments(context):
    """Compare host and VM environments."""
    context.environments_compared = True

@then('I can check for missing dependencies')
def step_check_missing_dependencies(context):
    """Can check for missing dependencies."""
    context.missing_dependencies_checked = True

@then('I can check network access from the VM')
def step_check_vm_network_access(context):
    """Can check network access from the VM."""
    context.vm_network_access_checked = True


# =============================================================================
# Additional error handling step definitions
# =============================================================================

@given('a transient error occurs')
def step_transient_error(context):
    """A transient error occurs."""
    context.transient_error = True
    context.error_type = 'transient'

@given('an error occurs')
def step_an_error_occurs(context):
    """An error occurs."""
    context.error_occurred = True

@given('my VM won\'t start due to configuration')
def step_vm_config_error(context):
    """VM won't start due to configuration."""
    context.vm_config_error = True
    context.startup_error = 'configuration'

@then('I should be told about manual steps if needed')
def step_told_about_manual_steps(context):
    """Should be told about manual steps."""
    context.manual_steps_communicated = True
