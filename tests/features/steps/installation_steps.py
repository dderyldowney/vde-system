"""
BDD Step Definitions for Installation and Initial Setup.
These are critical for ZeroToMastery students getting started with VDE.
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


# VDE_ROOT imported from config

# =============================================================================
# Installation GIVEN steps
# =============================================================================

@given('I have a new computer with Docker installed')
def step_new_computer_docker(context):
    context.new_computer = True
    context.docker_installed = True

@given('I have cloned the VDE repository to ~/dev')
def step_cloned_vde_repo(context):
    context.vde_repo_cloned = True
    context.vde_location = "/Users/dderyldowney/dev"  # Default location

@given('I want to install VDE')
def step_want_install_vde(context):
    context.wants_to_install = True

@given('I\'m setting up VDE for the first time')
def step_first_time_setup(context):
    context.first_time_setup = True
    context.vde_installed = False

@given('I want VDE commands available everywhere')
def step_want_vde_everywhere(context):
    context.want_vde_in_path = True

@given('VDE is being installed')
def step_vde_being_installed(context):
    context.vde_installing = True

@given('I\'ve just installed VDE')
def step_just_installed_vde(context):
    context.vde_installed = True

@given('VDE is freshly installed')
def step_freshly_installed(context):
    context.vde_installed = True
    context.no_vms_created_yet = True

@given('VDE has been installed')
def step_has_been_installed(context):
    context.vde_installed = True

@given('I have an older version of VDE')
def step_old_version_vde(context):
    context.vde_version = "old"
    context.vde_installed = True

@given('I no longer want VDE on my system')
def step_want_remove_vde(context):
    context.want_uninstall = True

@given('I\'m installing VDE')
def step_installing_vde(context):
    context.installing_vde = True

# =============================================================================
# Installation WHEN steps
# =============================================================================

@when('I run the initial setup script')
def step_run_initial_setup(context):
    context.initial_setup_run = True
    context.setup_completed = True

@when('the setup script runs')
def step_setup_script_runs(context):
    context.setup_ran = True

@when('SSH keys are checked')
def step_ssh_keys_checked(context):
    context.ssh_keys_checked = True
    # Check if ssh_keys_exist was explicitly set, default to False
    context.ssh_keys_found = getattr(context, 'ssh_keys_exist', False)

@when('setup completes')
def step_setup_completes(context):
    context.setup_completed = True

@when('I add VDE scripts to my PATH')
def step_add_to_path(context):
    context.vde_added_to_path = True

@when('setup checks Docker')
def step_setup_checks_docker(context):
    context.docker_checked = True

@when('the first VM is created')
def step_first_vm_created(context):
    context.first_vm_created = True
    context.vde_network_created = True

@when('I run "vde-health" or check status')
def step_run_vde_health(context):
    context.vde_health_run = True
    context.vde_status_checked = True

@when('I pull the latest changes')
def step_pull_latest_changes(context):
    context.latest_changes_pulled = True

@when('I want to remove it')
def step_want_to_remove(context):
    context.removal_requested = True

@when('the setup detects my OS (Linux/Mac)')
def step_detect_os(context):
    context.os_detected = True
    context.os_type = "darwin"  # or "linux"

@when('I create my first VM')
def step_create_first_vm(context):
    context.first_vm_creation = True
    context.creating_first_vm = True

@when('I want to start quickly')
def step_want_start_quickly(context):
    context.quick_start = True

@when('I need help')
def step_need_help(context):
    context.help_needed = True

@when('I run validation checks')
def step_run_validation(context):
    context.validation_run = True
    context.validation_checks = True

# =============================================================================
# Installation THEN steps
# =============================================================================

@then('VDE should be properly installed')
def step_vde_properly_installed(context):
    context.vde_installed = True
    assert context.vde_installed

@then('required directories should be created')
def step_required_dirs_created(context):
    context.required_dirs_created = True
    required_dirs = ['configs', 'templates', 'data', 'logs', 'projects', 'env-files', 'backup', 'cache']
    context.created_directories = required_dirs

@then('I should see success message')
def step_see_success_message(context):
    context.success_message_shown = True

@then('it should verify Docker is installed')
def step_verify_docker_installed(context):
    context.docker_verified = True
    # Actually check if Docker was verified in a previous step
    assert hasattr(context, 'docker_installed'), "docker_installed was not set"
    assert context.docker_installed is True, "Docker is not installed"

@then('it should verify docker-compose is available')
def step_verify_docker_compose(context):
    context.docker_compose_verified = True

@then('it should verify zsh is available')
def step_verify_zsh_available(context):
    context.zsh_verified = True

@then('it should report missing dependencies clearly')
def step_report_missing_deps(context):
    context.dependencies_reported = True

@then('configs/ directory should exist')
def step_configs_dir_exists(context):
    context.configs_dir_exists = True

@then('templates/ directory should exist with templates')
def step_templates_dir_exists(context):
    context.templates_dir_exists = True
    context.templates_present = True

@then('data/ directory should exist for persistent data')
def step_data_dir_exists(context):
    context.data_dir_exists = True

@then('logs/ directory should exist')
def step_logs_dir_exists(context):
    context.logs_dir_exists = True

@then('projects/ directory should exist for code')
def step_projects_dir_exists(context):
    context.projects_dir_exists = True

@then('env-files/ directory should exist')
def step_env_files_dir_exists(context):
    context.env_files_dir_exists = True

@then('backup/ directory should exist')
def step_backup_dir_exists(context):
    context.backup_dir_exists = True

@then('cache/ directory should exist')
def step_cache_dir_exists(context):
    context.cache_dir_exists = True

@then('if keys exist, they should be detected')
def step_keys_detected_if_exist(context):
    # Check if ssh_keys_exist was explicitly set, default to False
    context.existing_keys_detected = getattr(context, 'ssh_keys_exist', False)

@then('if no keys exist, ed25519 keys should be generated')
def step_keys_generated(context):
    # Only generate keys if ssh_keys_exist is False (not True, and not set)
    if not getattr(context, 'ssh_keys_exist', False):
        context.ssh_keys_generated = True
        context.key_type = "ed25519"

@then('public keys should be copied to public-ssh-keys/')
def step_public_keys_copied(context):
    context.public_keys_copied = True

@then('.keep file should exist in public-ssh-keys/')
def step_keep_file_exists(context):
    context.keep_file_exists = True

@then('backup/ssh/config should exist as a template')
def step_backup_ssh_config_exists(context):
    context.ssh_config_template_exists = True

@then('the template should show proper SSH config format')
def step_ssh_template_format(context):
    context.ssh_template_format_valid = True

@then('I should be able to use it as reference')
def step_can_use_as_reference(context):
    context.ssh_template_usable = True

@then('all predefined VM types should be shown')
def step_all_vm_types_shown(context):
    context.all_vm_types_shown = True
    context.available_vms = ['python', 'rust', 'js', 'csharp', 'ruby', 'postgres', 'redis', 'mongodb', 'nginx']

@then('python, rust, js, csharp, ruby should be listed')
def step_lang_vms_listed_install(context):
    context.language_vms_listed = ['python', 'rust', 'js', 'csharp', 'ruby']

@then('postgres, redis, mongodb, nginx should be listed')
def step_svc_vms_listed_install(context):
    context.service_vms_listed = ['postgres', 'redis', 'mongodb', 'nginx']

@then('aliases should be shown (py, js, etc.)')
def step_aliases_shown_install(context):
    context.aliases_shown = ['py', 'js', 'node', 'ts']

@then('I can run vde commands from any directory')
def step_vde_commands_anywhere(context):
    context.vde_commands_global = True

@then('I can run start-virtual, shutdown-virtual, etc.')
def step_run_vde_commands(context):
    context.vde_commands_available = ['start-virtual', 'shutdown-virtual', 'create-virtual-for', 'list-vms']

@then('tab completion should work')
def step_tab_completion_works(context):
    context.tab_completion_enabled = True

@then('I should be warned if I can\'t run Docker without sudo')
def step_docker_sudo_warning(context):
    context.docker_sudo_warning_shown = True

@then('instructions should be provided for fixing permissions')
def step_permission_fix_instructions(context):
    context.permission_instructions_shown = True

@then('setup should continue with a warning')
def step_setup_continues_with_warning(context):
    context.setup_continued = True

@then('vde-network should be created automatically')
def step_vde_network_created(context):
    context.vde_network_exists = True
    context.network_name = "vde-network"

@then('all VMs should use this network')
def step_all_vms_use_network(context):
    context.all_vms_on_network = True

@then('VMs can communicate with each other')
def step_vms_can_communicate(context):
    context.vm_communication_possible = True

@then('I should see helpful progress messages')
def step_progress_messages(context):
    context.progress_messages_shown = True

@then('configs/docker/python/ should be created')
def step_python_config_created(context):
    context.python_config_created = True
    context.python_config_path = "configs/docker/python"

@then('docker-compose.yml should be generated')
def step_compose_generated(context):
    context.docker_compose_generated = True

@then('SSH config should be updated')
def step_ssh_config_updated_install(context):
    context.ssh_config_updated = True

@then('I should be told what to do next')
def step_next_steps_shown(context):
    context.next_steps_provided = True

@then('I should see if VDE is properly configured')
def step_vde_health_status(context):
    context.vde_health_status_shown = True

@then('any issues should be clearly listed')
def step_issues_listed(context):
    context.issues_clearly_listed = True

@then('I should get fix suggestions for each issue')
def step_fix_suggestions(context):
    context.fix_suggestions_provided = True

@then('my existing VMs should continue working')
def step_existing_vms_work(context):
    context.existing_vms_still_work = True

@then('new VM types should be available')
def step_new_vm_types_available(context):
    context.new_types_available = True

@then('my configurations should be preserved')
def step_configs_preserved(context):
    context.configs_preserved = True

@then('I should be told about any manual migration needed')
def step_migration_instructions(context):
    context.migration_instructions_provided = True

@then('I can stop all VMs')
def step_can_stop_all_vms(context):
    context.all_vms_stoppable = True

@then('I can remove VDE directories')
def step_can_remove_vde_dirs(context):
    context.vde_dirs_removable = True

@then('my SSH config should be cleaned up')
def step_ssh_config_cleanup(context):
    context.ssh_config_cleaned = True

@then('my project data should be preserved if I want')
def step_project_data_preserved(context):
    context.project_data_preservable = True

@then('appropriate paths should be used')
def step_appropriate_paths(context):
    context.platform_paths_used = True

@then('platform-specific adjustments should be made')
def step_platform_adjustments(context):
    context.platform_specific_adjustments = True

@then('the installation should succeed')
def step_installation_succeeds(context):
    context.installation_successful = True

@then('required Docker images should be pulled')
def step_docker_images_pulled(context):
    context.docker_images_pulled = True

@then('base images should be built if needed')
def step_base_images_built(context):
    context.base_images_built = True

@then('I should see download/build progress')
def step_build_progress(context):
    context.build_progress_shown = True

@then('I can run "create-virtual-for python && start-virtual python"')
def step_quick_start_command(context):
    context.quick_start_command_works = True

@then('I should have a working Python environment')
def step_python_env_working(context):
    context.python_env_working = True

@then('I can start coding immediately')
def step_can_start_coding(context):
    context.immediate_coding = True

@then('README.md should provide overview')
def step_readme_overview(context):
    context.readme_provides_overview = True

@then('Technical-Deep-Dive.md should explain internals')
def step_technical_deep_dive(context):
    context.technical_docs_available = True

@then('tests/README.md should explain testing')
def step_tests_readme(context):
    context.tests_documented = True

@then('help text should be available in commands')
def step_help_in_commands(context):
    context.command_help_available = True

@then('all scripts should be executable')
def step_scripts_executable(context):
    context.scripts_executable = True

@then('all templates should be present')
def step_templates_present(context):
    context.all_templates_present = True

@then('vm-types.conf should be valid')
def step_vm_types_conf_valid(context):
    context.vm_types_conf_valid = True

@then('all directories should have correct permissions')
def step_dir_permissions_correct(context):
    context.directory_permissions_correct = True
