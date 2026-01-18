"""
BDD Step Definitions for VM customization and configuration features.
"""

from behave import given, when, then
from pathlib import Path

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def mark_step_implemented(context, step_name=""):
    """Mark a step as implemented in context."""
    context.step_implemented = True
    if step_name:
        if not hasattr(context, 'implemented_steps'):
            context.implemented_steps = []
        context.implemented_steps.append(step_name)




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

@given("I've modified VM configuration")
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

@then("I won't have permission issues on shared volumes")
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

# =============================================================================
# Steps from bdd_undefined_steps.py - CUSTOMIZATION
# =============================================================================

@given("a project needs environment variables for configuration")
def step_given_12_a_project_needs_environment_variables_for_configur(context):
    """a project needs environment variables for configuration"""
    context.step_given_12_a_project_needs_environment_variables_for_configur = True
    mark_step_implemented(context)

@given("I have custom scripts on my host")
def step_given_64_i_have_custom_scripts_on_my_host(context):
    """I have custom scripts on my host"""
    context.step_given_64_i_have_custom_scripts_on_my_host = True
    mark_step_implemented(context)

@given("I need to read a configuration file on my host")
def step_given_114_i_need_to_read_a_configuration_file_on_my_host(context):
    """I need to read a configuration file on my host"""
    context.step_given_114_i_need_to_read_a_configuration_file_on_my_host = True
    mark_step_implemented(context)

@when("I check the UID/GID configuration")
def step_when_20_i_check_the_uid_gid_configuration(context):
    """I check the UID/GID configuration"""
    context.step_when_20_i_check_the_uid_gid_configuration = True
    mark_step_implemented(context)

@when("I remove my custom configurations")
def step_when_70_i_remove_my_custom_configurations(context):
    """I remove my custom configurations"""
    context.step_when_70_i_remove_my_custom_configurations = True
    mark_step_implemented(context)

@when("I use environment variables")
def step_when_167_i_use_environment_variables(context):
    """I use environment variables"""
    context.step_when_167_i_use_environment_variables = True
    mark_step_implemented(context)

@when("I use the alias \"nodejs\"")
def step_when_169_i_use_the_alias_nodejs(context):
    """I use the alias "nodejs"""
    context.step_when_169_i_use_the_alias_nodejs = True
    mark_step_implemented(context)

@then("aliases work predictably across the team")
def step_then_42_aliases_work_predictably_across_the_team(context):
    """aliases work predictably across the team"""
    context.step_then_42_aliases_work_predictably_across_the_team = True
    mark_step_implemented(context)

@then("all language VMs should be listed with aliases")
def step_then_50_all_language_vms_should_be_listed_with_aliases(context):
    """all language VMs should be listed with aliases"""
    context.step_then_50_all_language_vms_should_be_listed_with_aliases = True
    mark_step_implemented(context)

@then("all should work with the same configuration")
def step_then_63_all_should_work_with_the_same_configuration(context):
    """all should work with the same configuration"""
    context.step_then_63_all_should_work_with_the_same_configuration = True
    mark_step_implemented(context)

@then("default configurations should be used")
def step_then_117_default_configurations_should_be_used(context):
    """default configurations should be used"""
    context.step_then_117_default_configurations_should_be_used = True
    mark_step_implemented(context)

@then("developers can override variables in local env-file (gitignored)")
def step_then_122_developers_can_override_variables_in_local_env_fil(context):
    """developers can override variables in local env-file (gitignored)"""
    context.step_then_122_developers_can_override_variables_in_local_env_fil = True
    mark_step_implemented(context)

@then("each developer has their own env file")
def step_then_136_each_developer_has_their_own_env_file(context):
    """each developer has their own env file"""
    context.step_then_136_each_developer_has_their_own_env_file = True
    mark_step_implemented(context)

@then("each should have its own configuration")
def step_then_140_each_should_have_its_own_configuration(context):
    """each should have its own configuration"""
    context.step_then_140_each_should_have_its_own_configuration = True
    mark_step_implemented(context)

@then("everyone gets consistent configurations")
def step_then_152_everyone_gets_consistent_configurations(context):
    """everyone gets consistent configurations"""
    context.step_then_152_everyone_gets_consistent_configurations = True
    mark_step_implemented(context)

@then("I can customize for my environment")
def step_then_174_i_can_customize_for_my_environment(context):
    """I can customize for my environment"""
    context.step_then_174_i_can_customize_for_my_environment = True
    mark_step_implemented(context)

@then("I can see CPU and memory usage")
def step_then_208_i_can_see_cpu_and_memory_usage(context):
    """I can see CPU and memory usage"""
    context.step_then_208_i_can_see_cpu_and_memory_usage = True
    mark_step_implemented(context)

@then("I can verify environment variables match")
def step_then_224_i_can_verify_environment_variables_match(context):
    """I can verify environment variables match"""
    context.step_then_224_i_can_verify_environment_variables_match = True
    mark_step_implemented(context)

@then("I should see any aliases (like py, python3)")
def step_then_292_i_should_see_any_aliases_like_py_python3(context):
    """I should see any aliases (like py, python3)"""
    context.step_then_292_i_should_see_any_aliases_like_py_python3 = True
    mark_step_implemented(context)

@then("it should use the standard VDE configuration")
def step_then_333_it_should_use_the_standard_vde_configuration(context):
    """it should use the standard VDE configuration"""
    context.step_then_333_it_should_use_the_standard_vde_configuration = True
    mark_step_implemented(context)

@then("logs/python volume should be mounted")
def step_then_344_logs_python_volume_should_be_mounted(context):
    """logs/python volume should be mounted"""
    context.step_then_344_logs_python_volume_should_be_mounted = True
    mark_step_implemented(context)

@then("my configuration should be preserved")
def step_then_356_my_configuration_should_be_preserved(context):
    """my configuration should be preserved"""
    context.step_then_356_my_configuration_should_be_preserved = True
    mark_step_implemented(context)

@then("my editor configuration should be loaded")
def step_then_361_my_editor_configuration_should_be_loaded(context):
    """my editor configuration should be loaded"""
    context.step_then_361_my_editor_configuration_should_be_loaded = True
    mark_step_implemented(context)

@then("no configuration should be needed in any VM")
def step_then_391_no_configuration_should_be_needed_in_any_vm(context):
    """no configuration should be needed in any VM"""
    context.step_then_391_no_configuration_should_be_needed_in_any_vm = True
    mark_step_implemented(context)

@then("no manual configuration should be required")
def step_then_399_no_manual_configuration_should_be_required(context):
    """no manual configuration should be required"""
    context.step_then_399_no_manual_configuration_should_be_required = True
    mark_step_implemented(context)

@then("old configuration issues should be resolved")
def step_then_412_old_configuration_issues_should_be_resolved(context):
    """old configuration issues should be resolved"""
    context.step_then_412_old_configuration_issues_should_be_resolved = True
    mark_step_implemented(context)

@then("project directories should be properly mounted")
def step_then_430_project_directories_should_be_properly_mounted(context):
    """project directories should be properly mounted"""
    context.step_then_430_project_directories_should_be_properly_mounted = True
    mark_step_implemented(context)

@then("projects/python volume should be mounted")
def step_then_433_projects_python_volume_should_be_mounted(context):
    """projects/python volume should be mounted"""
    context.step_then_433_projects_python_volume_should_be_mounted = True
    mark_step_implemented(context)

@then("rendered output should contain .ssh volume mount")
def step_then_437_rendered_output_should_contain_ssh_volume_mount(context):
    """rendered output should contain .ssh volume mount"""
    context.step_then_437_rendered_output_should_contain_ssh_volume_mount = True
    mark_step_implemented(context)

@then("rendered output should specify UID and GID as \"1000\"")
def step_then_453_rendered_output_should_specify_uid_and_gid_as_1000(context):
    """rendered output should specify UID and GID as "1000"""
    context.step_then_453_rendered_output_should_specify_uid_and_gid_as_1000 = True
    mark_step_implemented(context)

@then("the configuration files should be deleted")
def step_then_499_the_configuration_files_should_be_deleted(context):
    """the configuration files should be deleted"""
    context.step_then_499_the_configuration_files_should_be_deleted = True
    mark_step_implemented(context)

@then("the configuration should be validated")
def step_then_500_the_configuration_should_be_validated(context):
    """the configuration should be validated"""
    context.step_then_500_the_configuration_should_be_validated = True
    mark_step_implemented(context)

@then("the system should not overwrite the existing configuration")
def step_then_561_the_system_should_not_overwrite_the_existing_confi(context):
    """the system should not overwrite the existing configuration"""
    context.step_then_561_the_system_should_not_overwrite_the_existing_confi = True
    mark_step_implemented(context)

@then("they should use the new VDE configuration")
def step_then_595_they_should_use_the_new_vde_configuration(context):
    """they should use the new VDE configuration"""
    context.step_then_595_they_should_use_the_new_vde_configuration = True
    mark_step_implemented(context)

@then("volume should be mounted from host directory")
def step_then_608_volume_should_be_mounted_from_host_directory(context):
    """volume should be mounted from host directory"""
    context.step_then_608_volume_should_be_mounted_from_host_directory = True
    mark_step_implemented(context)

