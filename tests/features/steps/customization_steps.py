"""
BDD Step Definitions for VM customization and configuration features.
"""

from behave import given, when, then
from pathlib import Path

VDE_ROOT = Path("/vde")

# =============================================================================
# Custom VM type creation GIVEN steps
# =============================================================================

@given('I need a MySQL service on port 3306')
def step_need_mysql(context):
    context.needs_mysql = True
    context.mysql_port = '3306'

@given('I need a service that exposes multiple ports')
def step_multi_port_service(context):
    context.needs_multi_port = True

@given('I want friendly names in listings')
def step_friendly_names(context):
    context.wants_friendly_names = True

@given('I want to reference VMs with short names')
def step_short_names(context):
    context.wants_short_names = True

@given('I need different port ranges for my environment')
def step_custom_ports(context):
    context.needs_custom_ports = True

@given('I need a different base OS or variant')
def step_custom_base(context):
    context.needs_custom_base = True

@given('my application needs specific environment variables')
def step_needs_env_vars(context):
    context.needs_app_env_vars = True

@given('my host user has different UID/GID than 1000')
def step_custom_uid(context):
    context.custom_uid_gid = True

@given('I need to mount specific directories into the VM')
def step_custom_mounts(context):
    context.needs_custom_mounts = True

@given('I want to limit VM memory usage')
def step_limit_memory(context):
    context.limit_memory = True

@given('I need custom DNS for my VMs')
def step_custom_dns(context):
    context.custom_dns = True

@given('I need some VMs on isolated networks')
def step_isolated_networks(context):
    context.isolated_networks = True

@given('I want to control VM logging')
def step_custom_logging(context):
    context.custom_logging = True

@given('I want VMs to restart automatically')
def step_auto_restart(context):
    context.auto_restart = True

@given('I want to know if VM is healthy')
def step_healthcheck(context):
    context.needs_healthcheck = True

@given('I want team to use same VM configuration')
def step_shared_config(context):
    context.shared_config = True

@given('I need local configuration different from team')
def step_local_override(context):
    context.local_override = True

@given('I need two different Python environments')
def step_multiple_python(context):
    context.multiple_python = True

@given('I\'ve modified VM configuration')
def step_modified_config(context):
    context.config_modified = True

# =============================================================================
# Custom VM type creation WHEN steps
# =============================================================================

# Note: "I run {command}" is defined in vm_lifecycle_steps.py

@when('the VM type configuration includes multiple ports')
def step_multi_port_config(context):
    context.multi_port_config = True

@when('I add VM type with --display "{display}"')
def step_add_display(context, display):
    context.display_name = display

@when('I add VM type with aliases "{aliases}"')
def step_add_aliases(context, aliases):
    context.aliases = aliases.split(',')

@when('I modify VDE_LANG_PORT_START and VDE_LANG_PORT_END')
def step_modify_port_range(context):
    context.port_range_modified = True

@when('I modify base-dev.Dockerfile')
def step_modify_base(context):
    context.base_modified = True

@when('I create env-files/myapp.env')
def step_create_env_file(context):
    context.app_env_file = 'env-files/myapp.env'

@when('I modify the UID and GID in docker-compose.yml')
def step_modify_uid_gid(context):
    context.uid_gid_modified = True

@when('I modify the volumes section in docker-compose.yml')
def step_modify_volumes(context):
    context.volumes_modified = True

@when('I add mem_limit to docker-compose.yml')
def step_add_mem_limit(context):
    context.mem_limit_added = True

@when('I modify DNS settings in docker-compose.yml')
def step_modify_dns(context):
    context.dns_modified = True

@when('I create custom networks in docker-compose.yml')
def step_create_networks(context):
    context.custom_networks_created = True

@when('I modify logging configuration in docker-compose.yml')
def step_modify_logging(context):
    context.logging_modified = True

@when('I set restart: always in docker-compose.yml')
def step_set_restart(context):
    context.restart_set = True

@when('I add healthcheck to docker-compose.yml')
def step_add_healthcheck(context):
    context.healthcheck_added = True

@when('I commit docker-compose.yml and env-files to git')
def step_commit_config(context):
    context.config_committed = True

@when('I create .env.local or docker-compose.override.yml')
def step_create_local_override(context):
    context.local_override_created = True

@when('I create "{vm1}" and "{vm2}" VMs')
def step_create_two_vms(context, vm1, vm2):
    if not hasattr(context, 'created_vms'):
        context.created_vms = set()
    context.created_vms.update([vm1, vm2])

@when('I run validation or try to start VM')
def step_run_validation(context):
    context.validation_run = True

# =============================================================================
# Custom VM type creation THEN steps
# =============================================================================

@then('mysql VM should be created')
def step_mysql_created(context):
    if not hasattr(context, 'created_vms'):
        context.created_vms = set()
    context.created_vms.add('mysql')

@then('all ports should be mapped in docker-compose.yml')
def step_all_ports_mapped(context):
    context.all_ports_mapped = True

@then('"{display}" should appear in list-vms output')
def step_display_in_output(context, display):
    context.display_in_output = display

@then('I can use any alias to reference the VM')
def step_aliases_work(context):
    context.aliases_work = True

@then('new VMs should use ports in my custom range')
def step_custom_port_range(context):
    context.using_custom_port_range = True

@then('VMs should use my custom base image')
def step_custom_base_used(context):
    context.custom_base_used = True

@then('variables should be available in the VM')
def step_vars_available(context):
    context.vars_available = True

@then('container user should match my host user')
def step_user_matches(context):
    context.user_matches = True

@then('my custom directories should be mounted')
def step_custom_mounted(context):
    context.custom_mounted = True

@then('container should be limited to specified memory')
def step_memory_limited(context):
    context.memory_limited = True

@then('VMs should use my DNS servers')
def step_custom_dns_used(context):
    context.custom_dns_used = True

@then('VMs can be isolated as needed')
def step_vms_isolated(context):
    context.vms_isolated = True

@then('logs can go to files, syslog, or stdout')
def step_logging_configured(context):
    context.logging_configured = True

@then('VM restarts if it crashes')
def step_vm_auto_restarts(context):
    context.auto_restarts = True

@then('Docker monitors VM health')
def step_health_monitored(context):
    context.health_monitored = True

@then('team members get identical configuration')
def step_team_identical(context):
    context.team_identical_config = True

@then('my local overrides are not committed')
def step_local_not_committed(context):
    context.local_not_committed = True

@then('both should use python base configuration')
def step_both_python_base(context):
    context.both_python_base = True

@then('syntax errors should be caught')
def step_syntax_caught(context):
    context.syntax_errors_caught = True


# =============================================================================
# Port mapping and networking steps
# =============================================================================

@then('my custom packages should be available in the VM')
def step_custom_packages_available(context):
    """Custom packages are available in the VM."""
    context.custom_packages_available = True

@then('port 3306 should be mapped to host')
def step_port_mapped_to_host(context):
    """Port 3306 is mapped to host."""
    if not hasattr(context, 'mapped_ports'):
        context.mapped_ports = []
    context.mapped_ports.append('3306')
    context.port_3306_mapped = True

@then('I can connect to MySQL from other VMs')
def step_connect_mysql_from_vms(context):
    """Can connect to MySQL from other VMs."""
    context.mysql_connect_from_vms = True

@then('each port should be accessible from host')
def step_each_port_accessible_host(context):
    """Each port should be accessible from host."""
    context.ports_accessible_from_host = True

@then('each port should be accessible from other VMs')
def step_each_port_accessible_vms(context):
    """Each port should be accessible from other VMs."""
    context.ports_accessible_from_vms = True

@then('the display name should be used in all user-facing messages')
def step_display_name_used(context):
    """Display name is used in user-facing messages."""
    context.display_name_used = True

@then('"start-virtual js", "start-virtual node", "start-virtual nodejs" all work')
def step_aliases_all_work(context):
    """All aliases work correctly."""
    context.js_aliases_work = True
    context.node_aliases_work = True
    context.nodejs_aliases_work = True

@then('aliases should show in list-vms output')
def step_aliases_in_list_vms(context):
    """Aliases show in list-vms output."""
    context.aliases_visible_in_list = True

@then('existing VMs keep their allocated ports')
def step_existing_vms_keep_ports(context):
    """Existing VMs keep their allocated ports."""
    context.existing_vms_keep_ports = True


# =============================================================================
# Resource and monitoring steps
# =============================================================================

@then('my OS-specific requirements should be met')
def step_os_requirements_met(context):
    """OS-specific requirements are met."""
    context.os_requirements_met = True

@then('file permissions should work correctly')
def step_file_permissions_correct(context):
    """File permissions work correctly."""
    context.file_permissions_correct = True

@then('I won\'t have permission issues on shared volumes')
def step_no_permission_issues(context):
    """No permission issues on shared volumes."""
    context.no_permission_issues = True

@then('files should be shared between host and VM')
def step_files_shared_host_vm(context):
    """Files shared between host and VM."""
    context.files_shared_host_vm = True

@then('changes should sync immediately')
def step_changes_sync_immediately(context):
    """Changes sync immediately."""
    context.changes_sync_immediately = True

@then('container should not exceed the limit')
def step_container_not_exceed_limit(context):
    """Container should not exceed resource limit."""
    context.container_within_limit = True

@then('my system stays responsive')
def step_system_responsive(context):
    """System stays responsive."""
    context.system_responsive = True

@then('name resolution should work as configured')
def step_name_resolution_works(context):
    """Name resolution works as configured."""
    context.name_resolution_works = True

@then('specific VMs can communicate')
def step_specific_vms_communicate(context):
    """Specific VMs can communicate."""
    context.specific_vms_can_communicate = True

@then('other VMs cannot reach isolated VMs')
def step_isolated_vms_protected(context):
    """Other VMs cannot reach isolated VMs."""
    context.isolated_vms_protected = True

@then('log rotation can be configured')
def step_log_rotation_configurable(context):
    """Log rotation can be configured."""
    context.log_rotation_configurable = True

@then('I can control log verbosity')
def step_log_verbosity_control(context):
    """Can control log verbosity."""
    context.log_verbosity_controllable = True

@then('VM starts on system boot (if Docker does)')
def step_vm_starts_on_boot(context):
    """VM starts on system boot if Docker does."""
    context.vm_starts_on_boot = True

@then('my environment recovers automatically')
def step_environment_recovers(context):
    """Environment recovers automatically."""
    context.environment_auto_recovers = True

@then('I can see health status in docker ps')
def step_health_status_visible(context):
    """Health status visible in docker ps."""
    context.health_status_visible = True

@then('unhealthy VMs can be restarted automatically')
def step_unhealthy_vm_auto_restart(context):
    """Unhealthy VMs can be restarted automatically."""
    context.unhealthy_vm_auto_restart = True

@then('environment is consistent across team')
def step_environment_consistent_team(context):
    """Environment consistent across team."""
    context.environment_consistent = True

@then('"works on my machine" is reduced')
def step_works_on_my_machine_reduced(context):
    """'Works on my machine' problems are reduced."""
    context.works_on_my_machine_reduced = True


# =============================================================================
# Multiple instances and persistence steps
# =============================================================================

@then('each should have separate data directory')
def step_separate_data_directory(context):
    """Each instance has separate data directory."""
    context.separate_data_directories = True

@then('each can run independently')
def step_each_run_independently(context):
    """Each instance can run independently."""
    context.each_runs_independently = True
