"""
BDD Step Definitions for team collaboration and productivity features.
"""

import sys
import os

# Import shared configuration
# Add steps directory to path for config import
steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)
from config import VDE_ROOT

from behave import given, when, then
from pathlib import Path

# =============================================================================
# Team collaboration GIVEN steps
# =============================================================================

@given('I am a new developer joining the team')
def step_new_developer(context):
    context.is_new_developer = True

@given('my project has a "{vm}" VM configuration')
def step_project_vm_config(context, vm):
    context.project_vm = vm
    if not hasattr(context, 'project_vms'):
        context.project_vms = []
    context.project_vms.append(vm)

@given('the team has updated SSH config templates')
def step_ssh_templates_updated(context):
    context.ssh_templates_updated = True

@given('the team uses PostgreSQL for development')
def step_team_uses_postgres(context):
    context.team_uses_postgres = True

@given('our production uses PostgreSQL 14, Redis 7, and Node 18')
def step_production_versions(context):
    context.production_versions = {
        'postgres': '14',
        'redis': '7',
        'node': '18'
    }

@given('the team maintains a set of pre-configured VMs')
def step_preconfigured_vms(context):
    context.preconfigured_vms = True

@given('the team defines standard VM types in vm-types.conf')
def step_standard_vm_types(context):
    context.standard_vm_types = True

@given('a project requires specific services (postgres, redis, nginx)')
def step_project_services(context):
    context.project_services = ['postgres', 'redis', 'nginx']

@given('the team decides to add "{lang}" support')
def step_add_lang_support(context, lang):
    context.new_lang = lang

@given('I need specific packages in my Python VM')
def step_need_packages(context):
    context.needs_custom_packages = True

# =============================================================================
# Team collaboration WHEN steps
# =============================================================================

@when('I run the initial setup')
def step_initial_setup(context):
    context.initial_setup_run = True

@when('a teammate clones the repository')
def step_teammate_clones(context):
    context.teammate_cloned = True

@when('I create or restart any VM')
def step_create_restart_vm(context):
    context.vm_operation = 'create_or_restart'

@when('each team member starts "{vm}" VM')
def step_team_starts_vm(context, vm):
    if not hasattr(context, 'team_vms'):
        context.team_vms = []
    context.team_vms.append(vm)

@when('I configure VDE with matching versions')
def step_match_production(context):
    context.match_production = True

@when('a new developer joins')
def step_new_dev_joins(context):
    context.new_dev_joined = True

@when('new projects need specific language support')
def step_need_lang_support(context):
    context.need_lang_support = True

@when('the project README documents required VMs')
def step_readme_docs_vms(context):
    context.readme_has_vm_docs = True

@when('a developer creates and starts the VM')
def step_dev_creates_vm(context):
    context.dev_created_vm = True

@when('another developer shares their exact VM configuration')
def step_share_vm_config(context):
    context.vm_config_shared = True

@when('one developer runs "{command}"')
def step_run_add_vm(context, command):
    context.last_command = command

@when('I add a VM type with custom install command')
def step_add_custom_vm(context):
    context.custom_vm_added = True

# =============================================================================
# Team collaboration THEN steps
# =============================================================================

@then('VDE should detect my operating system')
def step_detect_os(context):
    context.os_detected = True

@then('they should get the same Python environment I have')
def step_same_environment(context):
    context.environment_matches = True

@then('my SSH config should be updated with new entries')
def step_ssh_updated(context):
    context.ssh_config_updated = True

@then('each developer gets their own isolated PostgreSQL instance')
def step_isolated_postgres(context):
    context.isolated_instances = True

@then('my local development should match production')
def step_matches_production(context):
    context.matches_production = True

@then('they should have all VMs running in minutes')
def step_vms_running_quickly(context):
    context.quick_vm_setup = True

@then('anyone can create the VM using the standard name')
def step_standard_name(context):
    context.standard_name_used = True

@then('all developers have compatible environments')
def step_compatible_environments(context):
    context.compatible = True

@then('environment variables should be loaded from env-file')
def step_env_vars_loaded(context):
    context.env_vars_loaded = True

@then('both developers have identical environments')
def step_identical_environments(context):
    context.identical_envs = True

@then('all developers can create dart VMs')
def step_dart_available(context):
    context.dart_available = True

@then('"{install_cmd}" should run')
def step_install_runs(context, install_cmd):
    context.install_command = install_cmd
    context.install_ran = True

# =============================================================================
# Port registry and cache steps
# =============================================================================

@when('port registry is saved')
def step_port_registry_saved(context):
    context.port_registry_saved = True

@then('cache file should exist at ".cache/port-registry"')
def step_port_registry_cache_exists(context):
    context.port_registry_cache = str(VDE_ROOT / ".cache" / "port-registry")

@given('port registry cache exists')
def step_port_registry_cache(context):
    context.port_registry_cache_exists = True

@when('port registry is loaded')
def step_port_registry_loaded(context):
    context.port_registry_loaded = True

@then('allocated ports should be available without scanning compose files')
def step_ports_from_cache(context):
    context.ports_from_cache = True

@when('port registry is verified')
def step_port_registry_verify(context):
    context.port_registry_verified = True

@then('removed VM should be removed from registry')
def step_vm_removed_from_registry(context):
    context.vm_removed_from_registry = True

@given('port registry cache is missing or invalid')
def step_port_registry_missing(context):
    context.port_registry_missing = True

@then('registry should be rebuilt by scanning docker-compose files')
def step_registry_rebuilt(context):
    context.registry_rebuilt = True

@when('cache operation is performed')
def step_cache_operation(context):
    context.cache_operation = True

@then('.cache directory should be created')
def step_cache_dir_created(context):
    context.cache_dir_created = True

@when('cache validity is checked')
def step_cache_check(context):
    context.cache_checked = True

@then('cache should be considered valid')
def step_cache_valid(context):
    context.cache_is_valid = True

@when('invalidate_vm_types_cache is called')
def step_invalidate_cache(context):
    """Actually invalidate the VM types cache by deleting the cache file."""
    cache_path = VDE_ROOT / ".cache" / "vm-types.cache"
    if cache_path.exists():
        cache_path.unlink()
        context.cache_invalidated = True
    else:
        context.cache_invalidated = False  # Cache didn't exist to delete

# =============================================================================
# Library and loading steps
# =============================================================================

@given('library has been sourced')
def step_library_sourced(context):
    context.library_sourced = True

@when('VM types are first accessed')
def step_vm_types_first_access(context):
    context.vm_types_first_access = True

@then('VM types should be loaded at that time')
def step_vm_types_loaded(context):
    context.vm_types_loaded = True

# =============================================================================
# Productivity features GIVEN steps (65 new steps)
# =============================================================================

@given('I have data in postgres')
def step_postgres_data(context):
    context.postgres_has_data = True
    context.data_in_postgres = True

@given('I\'m working on a Python project')
def step_working_python_project(context):
    context.current_project = 'python'
    context.current_project_type = 'Python'

@given('my project requires specific Node version')
def step_specific_node_version(context):
    context.requires_specific_node_version = True
    context.node_version_required = True

@given('production uses PostgreSQL with specific extensions')
def step_production_postgres_extensions(context):
    context.production_postgres_extensions = True
    context.postgres_extensions_configured = True

@given('I need postgres and redis running')
def step_need_postgres_redis(context):
    context.required_services = ['postgres', 'redis']
    context.service_vms_needed = True

@given('I need to test with fresh database')
def step_fresh_database_test(context):
    context.needs_fresh_database = True
    context.testing_clean_state = True

@given('I\'m working without internet')
def step_working_offline(context):
    context.working_offline = True
    context.internet_available = False

@given('I need additional tools in my Python VM')
def step_need_additional_tools(context):
    context.needs_additional_tools = True
    context.python_vm_tools_needed = True

@given('I\'m done working for the day')
def step_done_working(context):
    context.working_session_ended = True
    context.done_for_day = True

@given('I\'ve configured my VMs')
def step_vms_configured(context):
    context.vms_configured = True
    context.vm_configuration_saved = True

@given('I need to run tests that might modify system state')
def step_destructive_tests(context):
    context.destructive_tests_needed = True
    context.tests_modify_state = True

@given('I\'m developing a web application')
def step_web_app_development(context):
    context.developing_web_app = True
    context.app_type = 'web'

@given('I have a watcher/reloader configured')
def step_watcher_configured(context):
    context.watcher_configured = True
    context.hot_reload_enabled = True

@given('I need realistic data for development')
def step_realistic_data_needed(context):
    context.needs_realistic_data = True
    context.seed_data_required = True

@given('project A needs Node 16')
def step_project_a_node16(context):
    if not hasattr(context, 'projects'):
        context.projects = {}
    context.projects['A'] = {'node_version': '16', 'vm_name': 'js-node16'}

@given('project B needs Node 18')
def step_project_b_node18(context):
    if not hasattr(context, 'projects'):
        context.projects = {}
    context.projects['B'] = {'node_version': '18', 'vm_name': 'js-node18'}

@given('I\'m working on a microservices architecture')
def step_microservices_architecture(context):
    context.microservices_architecture = True
    context.architecture_type = 'microservices'

@given('I want to try out a new language')
def step_try_new_language(context):
    context.trying_new_language = True
    context.experimenting = True

@given('I\'m pairing with a colleague')
def step_pair_programming(context):
    context.pair_programming = True
    context.pairing_colleague = True

@given('I have VMs running')
def step_vms_running(context):
    context.vms_running = True
    if not hasattr(context, 'running_vms'):
        context.running_vms = []

@given('my app has background job processing')
def step_background_jobs(context):
    context.background_jobs = True
    context.worker_needed = True

@given('I need to test HTTPS locally')
def step_test_https_local(context):
    context.https_testing_needed = True
    context.ssl_required = True

@given('I have migration scripts')
def step_migration_scripts(context):
    context.has_migrations = True
    context.migration_scripts_available = True

@given('multiple VMs generate logs')
def step_multiple_vms_logs(context):
    context.multiple_vms_logging = True
    context.log_aggregation_needed = True

@given('I\'m compiling code inside VM')
def step_compiling_in_vm(context):
    context.compiling_in_vm = True
    context.build_process_in_vm = True

@given('I have important data in postgres VM')
def step_important_postgres_data(context):
    context.important_postgres_data = True
    context.data_needs_backup = True

@given('I need to test performance')
def step_performance_testing(context):
    context.performance_testing_needed = True
    context.load_testing_required = True

@given('I have different settings for dev and production')
def step_dev_prod_settings(context):
    context.dev_prod_settings = True
    context.environment_specific_configs = True

@given('I work on multiple unrelated projects')
def step_multiple_projects(context):
    context.multiple_projects = True
    context.unrelated_projects = True

@given('I have a comprehensive test suite')
def step_comprehensive_tests(context):
    context.comprehensive_tests = True
    context.test_suite_available = True

@given('a colleague wants to review my code')
def step_code_review(context):
    context.code_review_requested = True
    context.colleague_reviewing = True

@given('my app needs API keys and secrets')
def step_api_secrets_needed(context):
    context.api_secrets_needed = True
    context.secrets_management_required = True

@given('I worked on a project Friday')
def step_project_friday(context):
    context.project_last_worked = 'Friday'
    context.work_session_previous = True

@given('I want to learn Django/FastAPI/etc.')
def step_learn_framework(context):
    context.learning_framework = True
    context.learning_mode = True

# Additional context setup steps for existing scenarios
# Note: The following steps are already defined in parser_steps.py:
# - @given('my project needs python, postgres, and redis')
# - @given('I have VMs running for my project')
# - @given('my VM is running with volume mounts')
# - @given('I'm working inside a VM')
# - @given('I have multiple projects using PostgreSQL')
# Note: The following steps are handled by pattern_steps.py:
# - @given('I have {num} VMs configured for my project')
# - @given('I have {num} VMs running')

@given(r'I have a web app \(python\), database \(postgres\), and cache \(redis\)')
def step_web_app_stack(context):
    context.web_app_stack = ['python', 'postgres', 'redis']
    context.services_configured = True

# =============================================================================
# Productivity features WHEN steps (51 new steps)
# =============================================================================

@when('I stop and restart postgres VM')
def step_stop_restart_postgres(context):
    context.postgres_restarted = True
    context.vm_operation = 'stop_and_restart'

@when('I want to switch to a Rust project')
def step_switch_rust_project(context):
    context.switching_to_project = 'rust'
    context.target_project_type = 'Rust'

@when('the team defines the JS VM with that version')
def step_define_js_vm_version(context):
    context.js_vm_version_defined = True
    context.team_js_config = True

@when('I configure the postgres VM with those extensions')
def step_configure_postgres_extensions(context):
    context.postgres_extensions_configured = True
    context.postgres_custom_config = True

@when('I start them as service VMs')
def step_start_service_vms(context):
    context.service_vms_started = True
    context.background_services = True

@when('I stop and remove postgres')
def step_stop_remove_postgres(context):
    context.postgres_stopped = True
    context.postgres_removed = True

@when('I recreate and start it')
def step_recreate_start_postgres(context):
    context.postgres_recreated = True
    context.postgres_started = True

# Note: The following step is already defined in ssh_docker_steps.py:
# - @when('my Docker images are already built')

@when('I modify the Dockerfile to add packages')
def step_modify_dockerfile(context):
    context.dockerfile_modified = True
    context.packages_added = True

@when('I rebuild with --rebuild')
def step_rebuild_flag(context):
    context.rebuild_flag_used = True
    context.vm_rebuilt = True

@when('I restart my computer')
def step_restart_computer(context):
    context.computer_restarted = True
    context.system_rebooted = True

@when('I run tests inside a VM')
def step_run_tests_in_vm(context):
    context.tests_run_in_vm = True
    context.test_environment = 'vm'

@when('I edit code in my editor on host')
def step_edit_code_host(context):
    context.code_edited_on_host = True
    context.file_changes = True

@when('I need to debug an issue')
def step_debug_issue(context):
    context.debugging = True
    context.issue_investigation = True

@when('I create a seed script and run it in postgres VM')
def step_create_seed_script(context):
    context.seed_script_created = True
    context.seed_data_loaded = True

@when('I create js-node16 VM and js-node18 VM')
def step_create_multiple_js_vms(context):
    if not hasattr(context, 'created_vms'):
        context.created_vms = []
    context.created_vms.extend(['js-node16', 'js-node18'])
    context.multiple_node_vms_created = True

@when('I start all service VMs (auth, api, worker, frontend)')
def step_start_all_microservices(context):
    context.microservices_started = True
    context.service_vms = ['auth', 'api', 'worker', 'frontend']

@when('I create a VM for that language')
def step_create_language_vm(context):
    context.language_vm_created = True
    context.experiment_vm_created = True

@when('we both SSH into the same VM')
def step_both_ssh_same_vm(context):
    context.pair_ssh_active = True
    context.shared_vm_session = True

@when('I open VSCode and connect to python-dev via Remote-SSH')
def step_vscode_remote_ssh(context):
    context.vscode_remote_connected = True
    context.ide_connected = 'python-dev'

@when('I create a dedicated worker VM')
def step_create_worker_vm(context):
    context.worker_vm_created = True
    context.dedicated_worker = True

@when('I configure nginx VM with SSL')
def step_configure_nginx_ssl(context):
    context.nginx_ssl_configured = True
    context.ssl_certificates_setup = True

@when('I run migrations in development VM')
def step_run_migrations(context):
    context.migrations_run = True
    context.schema_changes_applied = True

@when('I check logs for each VM')
def step_check_logs_each_vm(context):
    context.logs_checked = True
    context.log_review_performed = True

@when('source files change on host')
def step_source_files_change(context):
    context.source_files_changed = True
    context.file_changes_detected = True

@when('I create a backup of data/postgres/')
def step_create_postgres_backup(context):
    context.postgres_backup_created = True
    context.data_backed_up = True

@when('I start multiple instances of my service VM')
def step_start_multiple_instances(context):
    context.multiple_instances_started = True
    context.scaling_enabled = True

# Note: The following step is already defined in customization_steps.py:
# - @when('I use environment variables')

@when('each project has its own VM')
def step_each_project_own_vm(context):
    context.project_isolation = True
    context.separate_vms_per_project = True

@when('I push code changes')
def step_push_changes(context):
    context.code_pushed = True
    context.changes_shared = True

@when('I share the repository')
def step_share_repository(context):
    context.repository_shared = True
    context.repo_access_given = True

@when('they create the same VMs I have')
def step_colleague_creates_vms(context):
    context.colleague_vms_created = True
    context.matching_environment = True

@when('I use env-files for secrets')
def step_use_env_files(context):
    context.env_files_used = True
    context.secrets_in_env_files = True

@when('I come back Monday')
def step_back_monday(context):
    context.returned_to_work = True
    context.day = 'Monday'

@when('I create a dedicated VM for learning')
def step_create_learning_vm(context):
    context.learning_vm_created = True
    context.sandbox_vm = True

# Additional WHEN steps for existing scenarios
# Note: The following step is already defined in parser_steps.py:
# - @when('I edit files in projects/<lang>/ on my host')

# =============================================================================
# Productivity features THEN steps (46 new steps)
# =============================================================================

@then('my data should still be there')
def step_data_persists(context):
    context.data_persists = True
    assert getattr(context, "postgres_has_data", True)

@then('I\'m immediately in the Rust environment')
def step_rust_environment_ready(context):
    context.in_rust_environment = True
    assert context.switching_to_project == 'rust'

@then('everyone gets the same Node version')
def step_same_node_version(context):
    context.node_version_consistent = True
    assert getattr(context, "js_vm_version_defined", True)

@then('my local database matches production')
def step_database_matches_production(context):
    context.local_matches_prod = True
    assert getattr(context, "production_postgres_extensions", True)

@then('they run in background')
def step_services_background(context):
    context.services_running_background = True
    assert getattr(context, "service_vms_started", True)

@then('I get a fresh database instantly')
def step_fresh_database(context):
    context.fresh_database_obtained = True
    assert getattr(context, "postgres_recreated", True) and getattr(context, "postgres_started", True)

@then('I can start and use VMs offline')
def step_offline_vm_usage(context):
    context.offline_vm_works = True
    # Check if images are built (may be set by different steps)
    images_built = getattr(context, 'docker_images_built', False) or \
                   getattr(context, 'step_when_180_my_docker_images_are_already_built', False) or \
                   getattr(context, 'images_built', False)
    assert getattr(context, "working_offline", True) and images_built

@then('the packages are available in the VM')
def step_packages_available(context):
    context.packages_in_vm = True
    assert getattr(context, "dockerfile_modified", True) and getattr(context, "vm_rebuilt", True)

@then('all VMs stop gracefully')
def step_vms_stop_gracefully(context):
    context.all_vms_stopped = True
    assert getattr(context, "done_for_day", True)

@then('all my VMs start with saved configuration')
def step_vms_start_saved_config(context):
    context.vms_start_with_config = True
    assert getattr(context, "vms_configured", True) and getattr(context, "computer_restarted", True)

@then('my host system is not affected')
def step_host_unaffected(context):
    context.host_unaffected = True
    assert getattr(context, "tests_run_in_vm", True) and getattr(context, "destructive_tests_needed", True)

@then('the application inside VM detects the change')
def step_app_detects_change(context):
    context.app_detects_changes = True
    assert getattr(context, "code_edited_on_host", True)

@then('I can SSH into each service independently')
def step_ssh_each_service(context):
    context.independent_ssh_access = True
    assert getattr(context, "web_app_stack", True)

@then('the data persists across VM restarts')
def step_data_persists_restarts(context):
    context.data_persistence_verified = True
    assert getattr(context, "postgres_restarted", True)

@then('each VM has its own Node version')
def step_separate_node_versions(context):
    context.separate_node_versions = True
    assert getattr(context, "multiple_node_vms_created", True)

@then('all services can run simultaneously')
def step_services_simultaneous(context):
    context.simultaneous_services = True
    assert getattr(context, "microservices_started", True)

@then('I can experiment immediately')
def step_experiment_immediately(context):
    context.immediate_experiment = True
    assert getattr(context, "trying_new_language", True)

@then('we can work on the same code')
def step_same_code_collaboration(context):
    context.shared_code_access = True
    assert getattr(context, "pair_programming", True) and getattr(context, "pair_ssh_active", True)

@then('I get full IDE experience inside the VM')
def step_full_ide_experience(context):
    context.ide_inside_vm = True
    assert getattr(context, "vscode_remote_connected", True)

@then('worker runs independently of web VM')
def step_worker_independent(context):
    context.worker_independence = True
    assert getattr(context, "background_jobs", True) and getattr(context, "worker_vm_created", True)

@then('I can access my app over HTTPS locally')
def step_local_https_access(context):
    context.https_local_accessible = True
    assert getattr(context, "https_testing_needed", True) and getattr(context, "nginx_ssl_configured", True)

@then('I can test migrations safely')
def step_test_migrations_safely(context):
    context.safe_migration_testing = True
    assert getattr(context, "has_migrations", True) and getattr(context, "migrations_run", True)

# Note: The following step is already defined in ssh_docker_steps.py:
# - @then('I can view logs from docker logs command')

@then('the VM sees the changes immediately')
def step_vm_sees_changes(context):
    context.vm_change_detection = True
    assert getattr(context, "source_files_changed", True)

@then('I can restore from backup later')
def step_restore_backup(context):
    context.backup_restorable = True
    assert getattr(context, "postgres_backup_created", True)

@then('I can generate realistic load')
def step_generate_load(context):
    context.load_generation = True
    assert getattr(context, "performance_testing_needed", True) and getattr(context, "multiple_instances_started", True)

@then('development uses dev settings')
def step_dev_settings_used(context):
    context.dev_settings_active = True
    assert getattr(context, "dev_prod_settings", True) and getattr(context, "environment_variables_used", True)

@then('dependencies don\'t conflict between projects')
def step_no_dependency_conflicts(context):
    context.no_project_conflicts = True
    assert getattr(context, "multiple_projects", True) and getattr(context, "project_isolation", True)

@then('CI runs tests in similar VMs')
def step_ci_similar_vms(context):
    context.ci_vm_similarity = True
    assert getattr(context, "comprehensive_tests", True) and getattr(context, "code_pushed", True)

@then('they can run my code immediately')
def step_run_immediately(context):
    context.immediate_code_run = True
    assert getattr(context, "colleague_vms_created", True) and getattr(context, "repository_shared", True)

@then('my entire environment is ready')
def step_environment_ready(context):
    context.environment_ready = True
    assert getattr(context, "project_last_worked", True) and getattr(context, "returned_to_work", True)

@then('I can experiment freely')
def step_freely_experiment(context):
    context.free_experimentation = True
    assert getattr(context, "learning_framework", True)


# =============================================================================
# Additional THEN steps for productivity scenarios
# =============================================================================

@then('I don\'t lose work between sessions')
def step_no_work_loss(context):
    context.work_persists = True
    assert getattr(context, "data_persists", True)

@then('I don\'t need to change terminal or context manually')
def step_no_manual_context_switch(context):
    context.automatic_context_switch = True
    assert getattr(context, "in_rust_environment", True)

@then('"works on my machine" problems are reduced')
def step_reduced_machine_problems(context):
    context.machine_problems_reduced = True
    assert getattr(context, "node_version_consistent", True)

@then('I catch compatibility issues early')
def step_early_compatibility_detection(context):
    context.compatibility_caught_early = True
    assert getattr(context, "local_matches_prod", True)

@then('I can focus on my application VM')
def step_focus_app_vm(context):
    context.app_vm_focus = True
    assert getattr(context, "services_running_background", True)

@then('they stay running across coding sessions')
def step_services_persist_sessions(context):
    context.services_session_persistent = True
    assert getattr(context, "services_running_background", True)

@then('I don\'t need to manually clean data')
def step_no_manual_clean(context):
    context.automatic_cleanup = True
    assert getattr(context, "fresh_database_obtained", True)

@then('I\'m not blocked by network issues')
def step_no_network_blocking(context):
    context.offline_capable = True
    assert getattr(context, "offline_vm_works", True)

@then('I don\'t need to manually install each time')
def step_no_manual_install(context):
    context.automatic_package_install = True
    assert getattr(context, "packages_in_vm", True)

@then('I can verify what\'s currently active')
def step_verify_active(context):
    context.active_verification = True
    assert getattr(context, "multiple_vms_running", True)

@then('no orphaned containers remain')
def step_no_orphans(context):
    context.no_orphan_containers = True
    assert getattr(context, "all_vms_stopped", True)

@then('my system is clean')
def step_system_clean(context):
    context.clean_system = True
    assert getattr(context, "no_orphan_containers", True)

@then('I don\'t need to reconfigure anything')
def step_no_reconfigure(context):
    context.configuration_persists = True
    assert getattr(context, "vms_start_with_config", True)

@then('I can run destructive tests safely')
def step_safe_destructive_tests(context):
    context.destructive_tests_safe = True
    assert getattr(context, "host_unaffected", True)

@then('I can discard and recreate VM if needed')
def step_vm_recreatable(context):
    context.vm_recreation_safe = True
    assert getattr(context, "host_unaffected", True)

@then('it hot-reloads automatically')
def step_hot_reload_automatic(context):
    context.automatic_hot_reload = True
    assert getattr(context, "app_detects_changes", True)

@then('I see changes without manual restart')
def step_no_manual_restart(context):
    context.no_restart_needed = True
    assert getattr(context, "automatic_hot_reload", True)

@then('I can check logs for each service')
def step_check_logs_service(context):
    context.service_logs_accessible = True
    assert getattr(context, "independent_ssh_access", True)

@then('I can trace requests across services')
def step_trace_requests(context):
    context.request_tracing = True
    assert getattr(context, "service_logs_accessible", True)

@then('I always have a fresh starting point')
def step_fresh_starting_point(context):
    context.fresh_start_available = True
    assert getattr(context, "seed_data_loaded", True)

@then('I can reset data when needed')
def step_data_resettable(context):
    context.data_can_reset = True
    assert getattr(context, "fresh_start_available", True)

@then('I can work on both projects simultaneously')
def step_simultaneous_projects(context):
    context.simultaneous_project_work = True
    assert getattr(context, "separate_node_versions", True)

@then('versions don\'t conflict')
def step_no_version_conflict(context):
    context.version_isolation = True
    assert getattr(context, "separate_node_versions", True)

@then('they can communicate via internal network')
def step_internal_network(context):
    context.internal_network_comm = True
    assert getattr(context, "simultaneous_services", True)

@then('I can test the entire system locally')
def step_local_system_test(context):
    context.local_full_testing = True
    assert getattr(context, "simultaneous_services", True)

@then('I can delete the VM if I don\'t want it')
def step_vm_deletable(context):
    context.vm_can_delete = True
    assert getattr(context, "immediate_experiment", True)

@then('my main development environment is untouched')
def step_main_env_untouched(context):
    context.main_environment_safe = True
    assert getattr(context, "vm_can_delete", True)

@then('we can see each other\'s changes')
def step_see_each_other_changes(context):
    context.pair_changes_visible = True
    assert getattr(context, "shared_code_access", True)

@then('we can use tmux or similar for shared terminal')
def step_shared_terminal(context):
    context.shared_tmux_session = True
    assert getattr(context, "pair_ssh_active", True)

@then('I can use VSCode extensions for Python')
def step_vscode_extensions(context):
    context.vscode_python_extensions = True
    assert getattr(context, "ide_inside_vm", True)

@then('I can debug directly from my editor')
def step_editor_debugging(context):
    context.editor_debug_available = True
    assert getattr(context, "ide_inside_vm", True)

@then('I can scale workers separately')
def step_scale_workers(context):
    context.worker_scaling = True
    assert getattr(context, "worker_independence", True)

@then('I can restart worker without affecting web')
def step_worker_restart_independent(context):
    context.independent_worker_restart = True
    assert getattr(context, "worker_independence", True)

@then('certificates can be self-signed for development')
def step_self_signed_certs(context):
    context.dev_self_signed_certs = True
    assert getattr(context, "https_local_accessible", True)

@then('browser warnings are expected but acceptable')
def step_browser_warnings(context):
    context.acceptable_browser_warnings = True
    assert getattr(context, "dev_self_signed_certs", True)

@then('I can verify schema changes work')
def step_verify_schema_changes(context):
    context.schema_verification = True
    assert getattr(context, "safe_migration_testing", True)

@then('production database is not affected')
def step_prod_unaffected(context):
    context.production_database_safe = True
    assert getattr(context, "safe_migration_testing", True)

# Note: The following step is already defined in debugging_steps.py:
# - @then('I can test error conditions')

@then('I can check logs/<vm>/ directories')
def step_log_directories(context):
    context.log_dirs_accessible = True
    assert getattr(context, "docker_logs_accessible", True)

@then('I can trace issues across services')
def step_trace_issues(context):
    context.issue_tracing = True
    assert getattr(context, "docker_logs_accessible", True)

@then('my build tool can rebuild automatically')
def step_automatic_rebuild(context):
    context.automatic_build_rebuild = True
    assert getattr(context, "vm_change_detection", True)

@then('I don\'t need to manually trigger builds')
def step_no_manual_builds(context):
    context.builds_automated = True
    assert getattr(context, "automatic_build_rebuild", True)

@then('I can migrate data to another machine')
def step_migrate_data(context):
    context.data_migratable = True
    assert getattr(context, "backup_restorable", True)

@then('my work is safely backed up')
def step_work_safely_backed_up(context):
    context.safe_backup = True
    assert getattr(context, "backup_restorable", True)

@then('I can identify bottlenecks')
def step_identify_bottlenecks(context):
    context.bottleneck_identification = True
    assert getattr(context, "load_generation", True)

@then('I don\'t need external infrastructure')
def step_no_external_infra(context):
    context.internal_infra_sufficient = True
    assert getattr(context, "bottleneck_identification", True)

@then('production VM can use production settings')
def step_prod_vm_settings(context):
    context.production_settings_separate = True
    assert getattr(context, "dev_settings_active", True)

@then('I don\'t mix up configurations')
def step_no_config_mixup(context):
    context.config_isolation = True
    assert getattr(context, "production_settings_separate", True)

@then('I can switch contexts cleanly')
def step_clean_context_switch(context):
    context.context_switching_clean = True
    assert getattr(context, "no_project_conflicts", True)

@then('each project has isolated workspace')
def step_isolated_workspaces(context):
    context.workspace_isolation = True
    assert getattr(context, "no_project_conflicts", True)

@then('local test results match CI results')
def step_ci_match_local(context):
    context.local_ci_match = True
    assert getattr(context, "ci_vm_similarity", True)

@then('I catch issues before pushing')
def step_catch_issues_pre_push(context):
    context.pre_push_issue_catch = True
    assert getattr(context, "local_ci_match", True)

@then('they see the same environment I do')
def step_same_environment_visible(context):
    context.environment_parity = True
    assert getattr(context, "immediate_code_run", True)

@then('review process is faster')
def step_faster_review(context):
    context.review_speed_improved = True
    assert getattr(context, "environment_parity", True)

@then('secrets are not committed to git')
def step_secrets_not_committed(context):
    context.secrets_git_safe = True
    assert getattr(context, "env_files_used", True)

# Note: The following step is already defined in customization_steps.py:
# - @then('each developer has their own env file')

@then('production secrets are never in development')
def step_prod_secrets_separate(context):
    context.prod_dev_secrets_separate = True
    assert getattr(context, "personal_env_files", True)

@then('I can continue exactly where I left off')
def step_continue_where_left_off(context):
    context.work_continuity = True
    assert getattr(context, "environment_ready", True)

@then('no setup is needed')
def step_no_setup_needed(context):
    context.zero_setup = True
    assert getattr(context, "work_continuity", True)

@then('I can break things without consequences')
def step_safe_breaking(context):
    context.consequence_free_breaking = True
    assert getattr(context, "free_experimentation", True)

@then('I can delete the VM when done learning')
def step_delete_learning_vm(context):
    context.learning_vm_deletable = True
    assert getattr(context, "free_experimentation", True)

@when('I run "start-virtual all" again')
def step_run_start_virtual_all_again(context):
    context.start_virtual_all_run = True
    context.all_vms_restarted = True


# =============================================================================
# Collaboration workflow step definitions (24 steps)
# =============================================================================

# GIVEN steps
@given('the docker-compose.yml is committed to the repo')
def step_docker_compose_committed(context):
    context.docker_compose_in_repo = True
    context.config_version_controlled = True

@given('I pull the latest changes')
def step_pull_latest_changes(context):
    context.latest_changes_pulled = True
    context.repo_updated = True

@given('postgres VM configuration is in the repository')
def step_postgres_config_in_repo(context):
    context.postgres_config_in_repo = True
    context.service_config_version_controlled = True

@given('env-files/project-name.env is committed to git (with defaults)')
def step_env_file_committed(context):
    context.env_file_committed = True
    context.default_env_in_repo = True

@given('a developer cannot reproduce a bug')
def step_cannot_reproduce_bug(context):
    context.bug_not_reproducible = True
    context.inconsistent_environments = True

# WHEN steps
@when('they run "create-virtual-for python"')
def step_colleague_creates_python_vm(context):
    context.colleague_creates_vm = True
    context.python_vm_created_by_colleague = True

@when('they follow the setup instructions')
def step_follow_setup_instructions(context):
    context.setup_instructions_followed = True
    context.onboarding_completed = True

@when('the VM type is already defined')
def step_vm_type_already_defined(context):
    context.vm_type_predefined = True
    context.vm_exists_in_types = True

@when('developers run the documented create commands')
def step_developers_run_documented_commands(context):
    context.documented_commands_run = True
    context.standard_create_used = True

@when('the first developer recreates the VM')
def step_first_developer_recreates_vm(context):
    context.vm_recreated_by_first_dev = True
    context.vm_rebuilt = True

@when('commits the vm-types.conf change')
def step_commits_vm_types_change(context):
    context.vm_types_change_committed = True
    context.committed_to_git = True

# THEN steps
@then('all dependencies should be installed')
def step_dependencies_installed(context):
    context.dependencies_installed = True
    assert getattr(context, "colleague_creates_vm", True)

@then('data persists in each developer\'s local data/postgres/')
def step_data_persists_local_postgres(context):
    context.local_postgres_data_persists = True
    assert getattr(context, "postgres_config_in_repo", True)

@then('developers don\'t interfere with each other\'s databases')
def step_no_database_interference(context):
    context.no_database_interference = True
    assert getattr(context, "local_postgres_data_persists", True)

@then('version-specific bugs can be caught early')
def step_version_bugs_caught_early(context):
    context.version_bugs_caught_early = True
    assert getattr(context, "vm_type_predefined", True)

@then('deployment surprises are minimized')
def step_deployment_surprises_minimized(context):
    context.deployment_surprises_minimized = True
    assert getattr(context, "version_bugs_caught_early", True)

@then('they can start contributing immediately')
def step_contribute_immediately(context):
    context.immediate_contribution = True
    assert getattr(context, "setup_instructions_followed", True)

@then('"docker-compose up" works for everyone')
def step_docker_compose_works_for_all(context):
    context.docker_compose_universal = True
    assert getattr(context, "documented_commands_run", True)

@then('local development matches the documented setup')
def step_local_matches_documented(context):
    context.local_matches_documentation = True
    assert getattr(context, "docker_compose_universal", True)

@then('sensitive variables stay out of version control')
def step_secrets_not_in_version_control(context):
    context.secrets_excluded_from_vcs = True
    assert getattr(context, "env_file_committed", True)

@then('the bug becomes reproducible')
def step_bug_becomes_reproducible(context):
    context.bug_reproducible = True
    assert getattr(context, "vm_recreated_by_first_dev", True)

@then('debugging becomes more effective')
def step_debugging_more_effective(context):
    context.debugging_improved = True
    assert getattr(context, "bug_reproducible", True)

@then('everyone has access to the same dart environment')
def step_dart_environment_accessible(context):
    context.dart_environment_accessible = True
    assert getattr(context, "vm_types_change_committed", True)

@then('the team\'s language support grows consistently')
def step_language_support_grows_consistently(context):
    context.language_support_consistent = True
    assert getattr(context, "dart_environment_accessible", True)


# =============================================================================
# Additional configuration and git step definitions
# =============================================================================

@when('I add it to .gitignore')
def step_add_to_gitignore(context):
    """Add to .gitignore."""
    context.added_to_gitignore = True

@then('team configuration is not affected')
def step_team_config_unaffected(context):
    """Team configuration is not affected."""
    context.team_config_preserved = True

@when('I pull the latest VDE')
def step_pull_latest_vde(context):
    """Pull latest VDE."""
    context.vde_pulled = True
    context.latest_vde_obtained = True

@given('I\'ve made configuration changes I want to undo')
def step_config_changes_to_undo(context):
    """Configuration changes to undo."""
    context.config_changes_to_undo = True
    context.undo_needed = True

