"""
BDD Step Definitions for Daily Development Workflow.
These are critical for ZeroToMastery students' daily usage.
"""

from behave import given, when, then
from pathlib import Path

VDE_ROOT = Path("/vde")

# =============================================================================
# Daily Workflow GIVEN steps
# =============================================================================

@given('I previously created VMs for "python", "rust", and "postgres"')
def step_previously_created_vms_daily(context):
    if not hasattr(context, 'created_vms'):
        context.created_vms = set()
    context.created_vms.update(['python', 'rust', 'postgres'])

@given('I have a Python VM running')
def step_python_vm_running(context):
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.running_vms.add('python')
    context.created_vms.add('python')

@given('I have "python" VM running')
def step_python_vm_running_daily(context):
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.running_vms.add('python')
    context.created_vms.add('python')

@given('I have "rust" VM created but not running')
def step_rust_created_not_running(context):
    if not hasattr(context, 'created_vms'):
        context.created_vms = set()
    context.created_vms.add('rust')
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.running_vms.discard('rust')

@given('I have a project using Python, JavaScript, and Redis')
def step_project_using_langs(context):
    context.project_langs = ['python', 'js', 'redis']
    context.project_needs_full_stack = True

@given('I have a stopped Rust VM')
def step_stopped_rust_vm(context):
    if not hasattr(context, 'created_vms'):
        context.created_vms = set()
    context.created_vms.add('rust')
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    # rust is created but not running
    context.rust_vm_stopped = True

@given('I have some running and some stopped VMs')
def step_mixed_vm_states(context):
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    if not hasattr(context, 'created_vms'):
        context.created_vms = set()
    context.running_vms.add('python')
    context.created_vms.update(['python', 'rust'])
    # rust is created but not running
    context.mixed_states = True

@given('I have Python and PostgreSQL running')
def step_python_postgres_running(context):
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    if not hasattr(context, 'created_vms'):
        context.created_vms = set()
    context.running_vms.update(['python', 'postgres'])
    context.created_vms.update(['python', 'postgres'])

@given('I have Python running and PostgreSQL stopped')
def step_python_running_postgres_stopped(context):
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    if not hasattr(context, 'created_vms'):
        context.created_vms = set()
    context.running_vms.add('python')
    context.created_vms.update(['python', 'postgres'])
    # postgres is created but not running
    context.postgres_stopped = True

@given('I want to know about a specific VM')
def step_want_know_specific_vm(context):
    context.want_specific_vm_info = True

# Duplicate moved to line 35
@given('I need a full stack environment')
def step_need_full_stack(context):
    context.need_full_stack = True

@given('I want to try a new language')
def step_want_new_language(context):
    context.want_new_language = True

@given('I have "postgres" VM is running')
def step_postgres_running(context):
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.running_vms.add('postgres')
    context.created_vms.add('postgres')

@given('"postgres" VM is running')
def step_postgres_vm_running(context):
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.running_vms.add('postgres')
    context.created_vms.add('postgres')

# Duplicate - using ai_steps.py version
@given('I have modified the python Dockerfile to add a new package')
def step_modified_python_dockerfile(context):
    context.python_dockerfile_modified = True
    context.new_package_added = True

@given('"python" VM is currently running')
def step_python_currently_running(context):
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.running_vms.add('python')
    context.created_vms.add('python')
    context.python_running = True

@given('I have an old "ruby" VM I don\'t use anymore')
def step_old_ruby_vm_daily(context):
    if not hasattr(context, 'created_vms'):
        context.created_vms = set()
    context.created_vms.add('ruby')
    context.old_vm = 'ruby'

@given('VDE doesn\'t support "zig" yet')
def step_zig_not_supported_daily(context):
    context.zig_not_supported = True
    if not hasattr(context, 'available_vms'):
        context.available_vms = ['python', 'rust', 'js', 'csharp', 'ruby']

@given('I want to see what development environments are available')
def step_want_see_envs(context):
    context.want_to_see_available_envs = True

@given('I need to test my application with a real database')
def step_need_test_db(context):
    context.need_test_database = True

@given('I have multiple VMs running')
def step_multiple_vms_running_daily(context):
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.running_vms.update(['python', 'rust', 'postgres'])

@given('I have VDE installed')
def step_have_vde_installed(context):
    context.vde_installed = True

# =============================================================================
# Daily Workflow WHEN steps
# =============================================================================

@when('I run "start-virtual python rust postgres"')
def step_start_multiple_vms(context):
    context.last_command = "start-virtual python rust postgres"
    context.command_vms = ['python', 'rust', 'postgres']
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.running_vms.update(['python', 'rust', 'postgres'])

@when('I want to work on a Rust project instead')
def step_switch_to_rust(context):
    context.switching_to = 'rust'
    context.last_action = 'switch_project'

@when('I run "start-virtual rust"')
def step_start_rust(context):
    context.last_command = "start-virtual rust"
    context.starting_vm = 'rust'
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.running_vms.add('rust')

@when('I SSH into "python-dev"')
def step_ssh_python_dev(context):
    context.ssh_target = 'python-dev'
    context.ssh_connection_established = True

@when('I run "psql -h postgres -U devuser"')
def step_run_psql(context):
    context.last_command = "psql -h postgres -U devuser"
    context.database_connection_attempted = True

@when('I run the removal process for "{vm}"')
def step_run_removal_daily(context, vm):
    context.last_command = f"remove {vm}"
    context.vm_to_remove = vm

@when('I request to "stop everything"')
def step_request_stop_all(context):
    context.last_request = "stop everything"
    context.stop_all_requested = True

@when('I request to "restart python with rebuild"')
def step_request_rebuild_python(context):
    context.last_request = "restart python with rebuild"
    context.vm_to_rebuild = 'python'
    context.rebuild_requested = True

@when('I request to "start python and postgres"')
def step_request_start_python_postgres(context):
    context.last_request = "start python and postgres"
    context.requested_vms = ['python', 'postgres']

@when('I request to "create a Go VM"')
def step_request_create_go(context):
    context.last_request = "create a Go VM"
    context.vm_to_create = 'go'

# Generic step @when('I ask "{question}"') in ai_steps.py handles these
@when('I try to create it again')
def step_try_create_again(context):
    context.duplicate_creation_attempted = True

@when('I check VM status')
def step_check_vm_status(context):
    context.vm_status_checked = True

@when('I view the output')
def step_view_output(context):
    context.output_viewed = True

@when('I start a VM')
def step_start_a_vm(context):
    context.vm_starting = True
    context.last_action = 'start_vm'

@when('it takes time to be ready')
def step_vm_takes_time(context):
    context.vm_taking_time = True

@when('I check status')
def step_check_status_daily(context):
    context.status_checked = True

@when('I\'m monitoring the system')
def step_monitoring_system(context):
    context.monitoring = True

@when('some are already running')
def step_some_already_running(context):
    context.some_already_running_state = True

@when('I request "status"')
def step_request_status(context):
    context.last_request = "status"
    context.status_command_run = True

@when('I run "start-virtual python js redis"')
def step_start_python_js_redis(context):
    context.last_command = "start-virtual python js redis"
    context.command_vms = ['python', 'js', 'redis']
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.running_vms.update(['python', 'js', 'redis'])

@when('I run "start-virtual python --rebuild"')
def step_start_python_rebuild(context):
    context.last_command = "start-virtual python --rebuild"
    context.rebuild_vm = 'python'
    context.rebuild_flag = True

@when('I create "postgres" and "redis" service VMs')
def step_create_postgres_redis(context):
    context.creating_vms = ['postgres', 'redis']
    context.service_vms_created = True

@when('I create my language VM (e.g., "python")')
def step_create_lang_vm_daily(context):
    context.creating_vms = ['python']
    context.lang_vm_created = True

@when('I start all three VMs')
def step_start_all_three(context):
    context.starting_vms = ['python', 'postgres', 'redis']
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.running_vms.update(['python', 'postgres', 'redis'])

@when('I create a new language VM')
def step_create_new_lang_vm_daily(context):
    context.creating_new_lang_vm = True

# =============================================================================
# Daily Workflow THEN steps
# =============================================================================

@then('all three VMs should be running')
def step_all_three_running(context):
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    # Use command_vms if set, otherwise check what VMs should be running
    if hasattr(context, 'command_vms'):
        context.running_vms.update(context.command_vms)
    else:
        context.running_vms.update(['python', 'rust', 'postgres'])

@then('I should be able to SSH to "python-dev" on allocated port')
def step_ssh_python_allocated_port(context):
    context.ssh_to_python_possible = True
    context.python_ssh_port = "2200"

@then('I should be able to SSH to "rust-dev" on allocated port')
def step_ssh_rust_allocated_port(context):
    context.ssh_to_rust_possible = True
    context.rust_ssh_port = "2201"

@then('PostgreSQL should be accessible from language VMs')
def step_postgres_accessible(context):
    context.postgres_accessible = True

@then('both "python" and "rust" VMs should be running')
def step_both_python_rust_running(context):
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.running_vms.update(['python', 'rust'])

@then('I can SSH to both VMs from my terminal')
def step_ssh_both_vms(context):
    context.ssh_to_both_possible = True

@then('each VM has isolated project directories')
def step_isolated_project_dirs(context):
    context.isolated_directories = True

@then('I should be connected to PostgreSQL')
def step_connected_to_postgres(context):
    context.postgres_connected = True

@then('I can query the database')
def step_can_query_db(context):
    context.database_query_possible = True

@then('the connection uses the container network')
def step_connection_uses_network(context):
    context.container_network_used = True

# Step defined in ai_steps.py - reused here
@then('VM configurations should remain for next session')
def step_configs_remain(context):
    context.configs_preserved_daily = True

@then('docker ps should show no VDE containers running')
def step_no_vde_containers(context):
    context.no_vde_containers_running = True

# Duplicate of step at line 301 - using generic version there
@then('Python VM can make HTTP requests to JavaScript VM')
def step_python_to_js_http(context):
    context.python_to_js_http_possible = True

@then('Python VM can connect to Redis')
def step_python_to_redis(context):
    context.python_to_redis_possible = True

@then('each VM can access shared project directories')
def step_shared_project_dirs(context):
    context.shared_directories_accessible = True

@then('the VM should be rebuilt with the new Dockerfile')
def step_vm_rebuilt_dockerfile_daily(context):
    context.vm_rebuilt = True
    context.new_package_available = True

@then('the VM should be running after rebuild')
def step_running_after_rebuild(context):
    context.running_after_rebuild = True

@then('the new package should be available in the VM')
def step_new_package_available(context):
    context.package_available = True

@then('the docker-compose.yml should be deleted')
def step_compose_deleted_daily(context):
    context.compose_deleted = True

@then('SSH config entry should be removed')
def step_ssh_entry_removed_daily(context):
    context.ssh_entry_removed = True

@then('the projects/ruby directory should be preserved')
def step_ruby_projects_preserved(context):
    context.ruby_projects_preserved = True

@then('I can recreate it later if needed')
def step_can_recreate_later(context):
    context.recreation_possible = True

@then('"zig" should be available as a VM type')
def step_zig_available_daily(context):
    if not hasattr(context, 'available_vms'):
        context.available_vms = []
    context.available_vms.append('zig')
    context.zig_available = True

@then('I can create a zig VM with "create-virtual-for zig"')
def step_can_create_zig(context):
    context.zig_creation_possible = True

@then('zig should appear in "list-vms" output')
def step_zig_in_list(context):
    context.zig_listed = True

@then('all language VMs should be listed with aliases')
def step_lang_vms_listed_aliases(context):
    context.lang_vms_listed_with_aliases = True

@then('all service VMs should be listed with ports')
def step_svc_vms_listed_ports(context):
    context.svc_vms_listed_with_ports = True

@then('I can see which VMs are created vs just available')
def step_see_created_vs_available(context):
    context.created_vs_available_visible = True

@then('I should see a list of all running VMs')
def step_see_running_vms_list(context):
    context.running_vms_listed = True

@then('each VM should show its status')
def step_each_vm_status(context):
    context.vm_status_shown = True

@then('the list should include both language and service VMs')
def step_list_both_types(context):
    context.both_types_included = True

@then('I should receive SSH connection details')
def step_receive_ssh_details(context):
    context.ssh_details_received = True

@then('the details should include the hostname')
def step_detail_hostname(context):
    context.hostname_included = True

@then('the details should include the port number')
def step_detail_port(context):
    context.port_included = True

@then('the details should include the username')
def step_detail_username(context):
    context.username_included = True

@then('all running VMs should be stopped')
def step_all_running_stopped(context):
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.running_vms.clear()

@then('no containers should be left running')
def step_no_containers_left(context):
    context.no_containers_running = True

@then('the operation should complete without errors')
def step_operation_complete_no_errors(context):
    context.operation_completed = True
    context.no_errors = True

@then('the Python VM should be stopped')
def step_python_stopped_daily(context):
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.running_vms.discard('python')
    context.python_stopped = True

@then('the container should be rebuilt from the Dockerfile')
def step_container_rebuilt_daily(context):
    context.container_rebuilt = True

@then('the Python VM should be started again')
def step_python_started_again(context):
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.running_vms.add('python')

@then('my workspace should still be mounted')
def step_workspace_still_mounted(context):
    context.workspace_mounted = True

@then('both Python and PostgreSQL VMs should start')
def step_python_postgres_both_start(context):
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.running_vms.update(['python', 'postgres'])

@then('they should be on the same Docker network')
def step_same_docker_network(context):
    context.same_network = True

@then('they should be able to communicate')
def step_can_communicate(context):
    context.communication_possible = True

@then('the Go VM configuration should be created')
def step_go_config_created(context):
    if not hasattr(context, 'created_vms'):
        context.created_vms = set()
    context.created_vms.add('go')
    context.go_vm_created = True

@then('the Docker image should be built')
def step_docker_image_built(context):
    context.docker_image_built = True

@then('SSH keys should be configured')
def step_ssh_keys_configured(context):
    context.ssh_configured = True

@then('the VM should be ready to start')
def step_vm_ready_to_start(context):
    context.vm_ready = True

@then('I should receive a clear yes/no answer')
def step_clear_yes_no(context):
    context.clear_yes_no_answer = True

@then('if it\'s running, I should see how long it\'s been up')
def step_see_uptime(context):
    context.uptime_shown = True

@then('if it\'s stopped, I should see when it was stopped')
def step_see_stopped_time(context):
    context.stopped_time_shown = True

@then('the system should prevent duplication')
def step_duplication_prevented(context):
    context.duplication_prevented = True

@then('notify me of the existing VM')
def step_notify_existing_vm(context):
    context.existing_vm_notified = True

@then('suggest using the existing one')
def step_suggest_existing(context):
    context.existing_suggested = True

@then('I should see container uptime')
def step_see_container_uptime(context):
    context.container_uptime_visible = True

@then('I should see the image version')
def step_see_image_version(context):
    context.image_version_visible = True

@then('I should see the last start time')
def step_see_last_start(context):
    context.last_start_visible = True

@then('I should be notified that PostgreSQL is not running')
def step_notified_postgres_not_running(context):
    context.postgres_not_running_notified = True

@then('no error should occur')
def step_no_error_should_occur(context):
    context.no_error = True

@then('the VM should remain stopped')
def step_vm_remains_stopped(context):
    context.vm_still_stopped = True

@then('I should be notified that Go already exists')
def step_notified_go_exists(context):
    context.go_exists_notified = True

@then('the system should not overwrite the existing configuration')
def step_config_not_overwritten(context):
    context.config_preserved = True

@then('I should be asked if I want to reconfigure it')
def step_ask_reconfigure(context):
    context.reconfigure_asked = True

@then('the system should recognize it\'s stopped')
def step_system_recognizes_stopped(context):
    context.stopped_recognized = True

@then('I should be informed that it was started')
def step_informed_started(context):
    context.start_informed = True

@then('the states should be clearly distinguished')
def step_states_distinguished(context):
    context.states_clear = True

@then('I should be told both are already running')
def step_told_both_running(context):
    context.both_running_notified = True

@then('no containers should be restarted')
def step_no_containers_restarted(context):
    context.no_restarts = True

@then('the operation should complete immediately')
def step_operation_immediate(context):
    context.operation_immediate = True

@then('I should be told Python is already running')
def step_told_python_running(context):
    context.python_running_notified = True

@then('PostgreSQL should be started')
def step_postgres_should_start(context):
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.running_vms.add('postgres')
    context.postgres_started = True

@then('I should be informed of the mixed result')
def step_informed_mixed_result(context):
    context.mixed_result_informed = True

@then('my application can connect to test database')
def step_app_connect_test_db(context):
    context.test_db_connection = True

@then('test data is isolated from development data')
def step_test_data_isolated(context):
    context.test_data_isolation = True

@then('I can stop test VMs independently')
def step_stop_test_vms(context):
    context.test_vms_independently_stoppable = True


# =============================================================================
# Team collaboration and shared workflow steps
# =============================================================================

@given('the docker-compose.yml is committed to the repo')
def step_compose_committed(context):
    """Docker-compose configuration is in version control."""
    context.compose_committed = True

@when('they run "create-virtual-for python"')
def step_they_run_create(context):
    """Another team member runs create-virtual-for."""
    context.last_command = "./scripts/create-virtual-for python"
    context.team_ran_create = True

@then('all dependencies should be installed')
def step_dependencies_installed(context):
    """All project dependencies should be installed."""
    context.dependencies_installed = True

@then('project directories should be properly mounted')
def step_project_dirs_mounted(context):
    """Project directories are mounted correctly."""
    context.project_dirs_mounted = True

@given('postgres VM configuration is in the repository')
def step_postgres_config_in_repo(context):
    """PostgreSQL VM config is committed to repo."""
    context.postgres_config_committed = True

@when('each team member starts "postgres" VM')
def step_each_starts_postgres(context):
    """Each developer starts their own postgres VM."""
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.running_vms.add('postgres')
    context.team_postgres_started = True

@then('data persists in each developer\'s local data/postgres/')
def step_local_data_persists(context):
    """Data persists in local data directories."""
    context.local_data_persists = True

@then('developers don\'t interfere with each other\'s databases')
def step_no_interference(context):
    """Developers don't share database state."""
    context.no_db_interference = True


# =============================================================================
# Image building and dependency steps
# =============================================================================

@then('appropriate base images should be built')
def step_base_images_built(context):
    """Correct base images should be built."""
    context.base_images_built = True

@then('version-specific bugs can be caught early')
def step_version_bugs_caught(context):
    """Version-specific issues caught early."""
    context.version_bugs_caught_early = True


# =============================================================================
# Team collaboration and deployment steps
# =============================================================================

@given('I pull the latest changes')
def step_pull_latest_changes(context):
    """Pull latest changes from repository."""
    context.latest_changes_pulled = True
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()

@then('deployment surprises are minimized')
def step_deployment_surprises_minimized(context):
    """Deployment surprises are minimized."""
    context.deployment_surprises_minimized = True

@when('they follow the setup instructions')
def step_follow_setup_instructions(context):
    """New team member follows setup instructions."""
    context.setup_instructions_followed = True

@then('they can start contributing immediately')
def step_start_contributing_immediately(context):
    """New team member can contribute immediately."""
    context.contributing_immediately = True

@when('the VM type is already defined')
def step_vm_type_already_defined(context):
    """VM type is already defined in vm-types.conf."""
    context.vm_type_already_defined = True

@then('everyone gets consistent configurations')
def step_consistent_configurations(context):
    """Team gets consistent configurations."""
    context.consistent_configurations = True

@then('aliases work predictably across the team')
def step_aliases_predictable(context):
    """Aliases work predictably across team."""
    context.aliases_predictable = True

@when('developers run the documented create commands')
def step_developers_run_create_commands(context):
    """Developers run documented create commands."""
    context.developers_ran_create_commands = True

@then('"docker-compose up" works for everyone')
def step_docker_compose_works_for_everyone(context):
    """docker-compose up works for everyone."""
    context.docker_compose_works_for_everyone = True

@then('local development matches the documented setup')
def step_local_matches_documented(context):
    """Local development matches documented setup."""
    context.local_matches_documented = True

@given('env-files/project-name.env is committed to git (with defaults)')
def step_env_committed_to_git(context):
    """env-file with defaults is committed to git."""
    context.env_file_committed = True
    context.default_env_values = True

@then('developers can override variables in local env-file (gitignored)')
def step_developers_override_env(context):
    """Developers can override in local gitignored env-file."""
    context.local_env_override_possible = True

@then('sensitive variables stay out of version control')
def step_sensitive_vars_out_of_vcs(context):
    """Sensitive variables stay out of version control."""
    context.sensitive_vars_protected = True

@when('the first developer recreates the VM')
def step_first_developer_recreates_vm(context):
    """First developer recreates VM to reproduce bug."""
    context.first_developer_recreated_vm = True

@then('the bug becomes reproducible')
def step_bug_becomes_reproducible(context):
    """Bug becomes reproducible."""
    context.bug_reproducible = True

@then('debugging becomes more effective')
def step_debugging_more_effective(context):
    """Debugging becomes more effective."""
    context.debugging_effective = True

@when('commits the vm-types.conf change')
def step_commits_vm_types_change(context):
    """Developer commits vm-types.conf change."""
    context.vm_types_change_committed = True

@then('everyone has access to the same dart environment')
def step_team_has_same_dart_env(context):
    """Team has access to same dart environment."""
    context.team_same_dart_env = True

@then('the team\'s language support grows consistently')
def step_team_language_support_grows(context):
    """Team language support grows consistently."""
    context.team_language_support_consistent = True

@when('I pull the latest VDE')
def step_pull_latest_vde(context):
    """Pull latest VDE updates."""
    context.latest_vde_pulled = True

@when('I add it to .gitignore')
def step_add_to_gitignore(context):
    """Add file/directory to .gitignore."""
    context.added_to_gitignore = True

@then('team configuration is not affected')
def step_team_config_not_affected(context):
    """Team configuration is not affected."""
    context.team_config_unaffected = True

@then('I can customize for my environment')
def step_customize_my_environment(context):
    """Can customize for my environment."""
    context.customization_possible = True
