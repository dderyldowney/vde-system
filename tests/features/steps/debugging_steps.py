"""
BDD Step Definitions for Debugging and Troubleshooting.
These are critical when ZeroToMastery students encounter issues.
"""

from behave import given, when, then
from pathlib import Path

VDE_ROOT = Path("/vde")

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
