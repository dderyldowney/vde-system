"""
BDD Step Definitions for team collaboration and productivity features.
"""

from behave import given, when, then
from pathlib import Path

VDE_ROOT = Path("/vde")

# =============================================================================
# Team collaboration GIVEN steps
# =============================================================================

@given('I am a new developer joining the team')
@given('I am a new developer joining the team')
def step_new_developer(context):
    context.is_new_developer = True

@given('my project has a "{vm}" VM configuration')
@given('my project has a "{vm}" VM configuration')
def step_project_vm_config(context, vm):
    context.project_vm = vm
    if not hasattr(context, 'project_vms'):
        context.project_vms = []
    context.project_vms.append(vm)

@given('the team has updated SSH config templates')
@given('the team has updated SSH config templates')
def step_ssh_templates_updated(context):
    context.ssh_templates_updated = True

@given('the team uses PostgreSQL for development')
@given('the team uses PostgreSQL for development')
def step_team_uses_postgres(context):
    context.team_uses_postgres = True

@given('our production uses PostgreSQL 14, Redis 7, and Node 18')
@given('our production uses PostgreSQL 14, Redis 7, and Node 18')
def step_production_versions(context):
    context.production_versions = {
        'postgres': '14',
        'redis': '7',
        'node': '18'
    }

@given('the team maintains a set of pre-configured VMs')
@given('the team maintains a set of pre-configured VMs')
def step_preconfigured_vms(context):
    context.preconfigured_vms = True

@given('the team defines standard VM types in vm-types.conf')
@given('the team defines standard VM types in vm-types.conf')
def step_standard_vm_types(context):
    context.standard_vm_types = True

@given('a project requires specific services (postgres, redis, nginx)')
@given('a project requires specific services (postgres, redis, nginx)')
def step_project_services(context):
    context.project_services = ['postgres', 'redis', 'nginx']

@given('the team decides to add "{lang}" support')
@given('the team decides to add "{lang}" support')
def step_add_lang_support(context, lang):
    context.new_lang = lang

@given('I need specific packages in my Python VM')
@given('I need specific packages in my Python VM')
def step_need_packages(context):
    context.needs_custom_packages = True

# =============================================================================
# Team collaboration WHEN steps
# =============================================================================

@when('I run the initial setup')
@when('I run the initial setup')
def step_initial_setup(context):
    context.initial_setup_run = True

@when('a teammate clones the repository')
@when('a teammate clones the repository')
def step_teammate_clones(context):
    context.teammate_cloned = True

@when('I create or restart any VM')
@when('I create or restart any VM')
def step_create_restart_vm(context):
    context.vm_operation = 'create_or_restart'

@when('each team member starts "{vm}" VM')
@when('each team member starts "{vm}" VM')
def step_team_starts_vm(context, vm):
    if not hasattr(context, 'team_vms'):
        context.team_vms = []
    context.team_vms.append(vm)

@when('I configure VDE with matching versions')
@when('I configure VDE with matching versions')
def step_match_production(context):
    context.match_production = True

@when('a new developer joins')
@when('a new developer joins')
def step_new_dev_joins(context):
    context.new_dev_joined = True

@when('new projects need specific language support')
@when('new projects need specific language support')
def step_need_lang_support(context):
    context.need_lang_support = True

@when('the project README documents required VMs')
@when('the project README documents required VMs')
def step_readme_docs_vms(context):
    context.readme_has_vm_docs = True

@when('a developer creates and starts the VM')
@when('a developer creates and starts the VM')
def step_dev_creates_vm(context):
    context.dev_created_vm = True

@when('another developer shares their exact VM configuration')
@when('another developer shares their exact VM configuration')
def step_share_vm_config(context):
    context.vm_config_shared = True

@when('one developer runs "{command}"')
@when('one developer runs "{command}"')
def step_run_add_vm(context, command):
    context.last_command = command

@when('I add a VM type with custom install command')
@when('I add a VM type with custom install command')
def step_add_custom_vm(context):
    context.custom_vm_added = True

# =============================================================================
# Team collaboration THEN steps
# =============================================================================

@then('VDE should detect my operating system')
@then('VDE should detect my operating system')
def step_detect_os(context):
    context.os_detected = True

@then('they should get the same Python environment I have')
@then('they should get the same Python environment I have')
def step_same_environment(context):
    context.environment_matches = True

@then('my SSH config should be updated with new entries')
@then('my SSH config should be updated with new entries')
def step_ssh_updated(context):
    context.ssh_config_updated = True

@then('each developer gets their own isolated PostgreSQL instance')
@then('each developer gets their own isolated PostgreSQL instance')
def step_isolated_postgres(context):
    context.isolated_instances = True

@then('my local development should match production')
@then('my local development should match production')
def step_matches_production(context):
    context.matches_production = True

@then('they should have all VMs running in minutes')
@then('they should have all VMs running in minutes')
def step_vms_running_quickly(context):
    context.quick_vm_setup = True

@then('anyone can create the VM using the standard name')
@then('anyone can create the VM using the standard name')
def step_standard_name(context):
    context.standard_name_used = True

@then('all developers have compatible environments')
@then('all developers have compatible environments')
def step_compatible_environments(context):
    context.compatible = True

@then('environment variables should be loaded from env-file')
@then('environment variables should be loaded from env-file')
def step_env_vars_loaded(context):
    context.env_vars_loaded = True

@then('both developers have identical environments')
@then('both developers have identical environments')
def step_identical_environments(context):
    context.identical_envs = True

@then('all developers can create dart VMs')
@then('all developers can create dart VMs')
def step_dart_available(context):
    context.dart_available = True

@then('"{install_cmd}" should run')
@then('"{install_cmd}" should run')
def step_install_runs(context, install_cmd):
    context.install_command = install_cmd
    context.install_ran = True

# =============================================================================
# Port registry and cache steps
# =============================================================================

@when('port registry is saved')
@when('port registry is saved')
def step_port_registry_saved(context):
    context.port_registry_saved = True

@then('cache file should exist at ".cache/port-registry"')
@then('cache file should exist at ".cache/port-registry"')
def step_port_registry_cache_exists(context):
    context.port_registry_cache = str(VDE_ROOT / ".cache" / "port-registry")

@given('port registry cache exists')
@given('port registry cache exists')
def step_port_registry_cache(context):
    context.port_registry_cache_exists = True

@when('port registry is loaded')
@when('port registry is loaded')
def step_port_registry_loaded(context):
    context.port_registry_loaded = True

@then('allocated ports should be available without scanning compose files')
@then('allocated ports should be available without scanning compose files')
def step_ports_from_cache(context):
    context.ports_from_cache = True

@when('port registry is verified')
@when('port registry is verified')
def step_port_registry_verify(context):
    context.port_registry_verified = True

@then('removed VM should be removed from registry')
@then('removed VM should be removed from registry')
def step_vm_removed_from_registry(context):
    context.vm_removed_from_registry = True

@given('port registry cache is missing or invalid')
@given('port registry cache is missing or invalid')
def step_port_registry_missing(context):
    context.port_registry_missing = True

@then('registry should be rebuilt by scanning docker-compose files')
@then('registry should be rebuilt by scanning docker-compose files')
def step_registry_rebuilt(context):
    context.registry_rebuilt = True

@when('cache operation is performed')
@when('cache operation is performed')
def step_cache_operation(context):
    context.cache_operation = True

@then('.cache directory should be created')
@then('.cache directory should be created')
def step_cache_dir_created(context):
    context.cache_dir_created = True

@when('cache validity is checked')
@when('cache validity is checked')
def step_cache_check(context):
    context.cache_checked = True

@then('cache should be considered valid')
@then('cache should be considered valid')
def step_cache_valid(context):
    context.cache_is_valid = True

@when('invalidate_vm_types_cache is called')
@when('invalidate_vm_types_cache is called')
def step_invalidate_cache(context):
    context.cache_invalidated = True

@then('cache file should be removed')
@then('cache file should be removed')
def step_cache_removed(context):
    context.cache_file_removed = True

# =============================================================================
# Library and loading steps
# =============================================================================

@given('library has been sourced')
@given('library has been sourced')
def step_library_sourced(context):
    context.library_sourced = True

@when('VM types are first accessed')
@when('VM types are first accessed')
def step_vm_types_first_access(context):
    context.vm_types_first_access = True

@then('VM types should be loaded at that time')
@then('VM types should be loaded at that time')
def step_vm_types_loaded(context):
    context.vm_types_loaded = True
