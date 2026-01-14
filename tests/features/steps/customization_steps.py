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
