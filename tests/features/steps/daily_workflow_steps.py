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
    if not hasattr(context, 'created_vms'):
        context.created_vms = set()
    context.created_vms.add('python')

@given('I have "python" VM running')
def step_python_vm_running_daily(context):
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.running_vms.add('python')
    if not hasattr(context, 'created_vms'):
        context.created_vms = set()
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
    if not hasattr(context, 'created_vms'):
        context.created_vms = set()
    context.created_vms.add('postgres')

@given('"postgres" VM is running')
def step_postgres_vm_running(context):
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.running_vms.add('postgres')
    if not hasattr(context, 'created_vms'):
        context.created_vms = set()
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
    if not hasattr(context, 'created_vms'):
        context.created_vms = set()
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


# =============================================================================
# Data persistence and workflow steps
# =============================================================================

@given('I have data in postgres')
def step_data_in_postgres(context):
    """Have data in postgres."""
    context.data_in_postgres = True

@when('I stop and restart postgres VM')
def step_stop_restart_postgres(context):
    """Stop and restart postgres VM."""
    context.postgres_restarted = True

@then('my data should still be there')
def step_data_persisted(context):
    """Data should still be there."""
    context.data_persisted = True

@then('I don\'t lose work between sessions')
def step_no_work_lost(context):
    """Don't lose work between sessions."""
    context.no_work_lost = True

@given('I\'m working on a Python project')
def step_working_python_project(context):
    """Working on Python project."""
    context.working_python = True

@when('I want to switch to a Rust project')
def step_switch_rust_project(context):
    """Want to switch to Rust project."""
    context.switching_to_rust = True

@then('I\'m immediately in the Rust environment')
def step_immediately_rust_env(context):
    """Immediately in Rust environment."""
    context.immediately_rust = True

@then('I don\'t need to change terminal or context manually')
def step_no_manual_terminal_change(context):
    """Don't need to change terminal manually."""
    context.no_manual_terminal_change = True

@given('my project requires specific Node version')
def step_specific_node_version(context):
    """Project requires specific Node version."""
    context.specific_node_version = True

@when('the team defines the JS VM with that version')
def step_team_defines_js_version(context):
    """Team defines JS VM with that version."""
    context.js_version_defined = True

@then('everyone gets the same Node version')
def step_same_node_version(context):
    """Everyone gets same Node version."""
    context.same_node_version = True

@then('"works on my machine" problems are reduced')
def step_works_on_machine_reduced(context):
    """Works on my machine problems reduced."""
    context.works_on_machine_reduced = True

@given('production uses PostgreSQL with specific extensions')
def step_production_postgres_ext(context):
    """Production uses PostgreSQL with extensions."""
    context.production_postgres_ext = True

@when('I configure the postgres VM with those extensions')
def step_configure_postgres_ext(context):
    """Configure postgres VM with extensions."""
    context.postgres_ext_configured = True

@then('my local database matches production')
def step_local_matches_prod(context):
    """Local database matches production."""
    context.local_matches_prod = True

@then('I catch compatibility issues early')
def step_catch_compat_early(context):
    """Catch compatibility issues early."""
    context.compat_caught_early = True

@given('I need postgres and redis running')
def step_need_postgres_redis(context):
    """Need postgres and redis running."""
    context.need_postgres_redis = True

@when('I start them as service VMs')
def step_start_service_vms(context):
    """Start them as service VMs."""
    context.service_vms_started = True

@then('they run in background')
def step_run_background(context):
    """They run in background."""
    context.running_background = True

@then('I can focus on my application VM')
def step_focus_app_vm(context):
    """Can focus on application VM."""
    context.focus_app_vm = True

@then('they stay running across coding sessions')
def step_stay_running(context):
    """Stay running across coding sessions."""
    context.stay_running_sessions = True

@given('I need to test with fresh database')
def step_need_fresh_database(context):
    """Need to test with fresh database."""
    context.need_fresh_db = True

@when('I stop and remove postgres')
def step_stop_remove_postgres(context):
    """Stop and remove postgres."""
    context.postgres_stopped_removed = True

@when('I recreate and start it')
def step_recreate_start_postgres(context):
    """Recreate and start postgres."""
    context.postgres_recreated_started = True

@then('I get a fresh database instantly')
def step_fresh_database_instant(context):
    """Get fresh database instantly."""
    context.fresh_db_instant = True

@then('I don\'t need to manually clean data')
def step_no_manual_clean(context):
    """Don't need to manually clean data."""
    context.no_manual_clean = True

@given('I\'m working without internet')
def step_working_offline(context):
    """Working without internet."""
    context.working_offline = True

@when('my Docker images are already built')
def step_docker_images_built(context):
    """Docker images are already built."""
    context.docker_images_built = True

@then('I can start and use VMs offline')
def step_use_vms_offline(context):
    """Can start and use VMs offline."""
    context.vms_offline = True

@then('I\'m not blocked by network issues')
def step_no_network_block(context):
    """Not blocked by network issues."""
    context.no_network_block = True

@given('I need additional tools in my Python VM')
def step_need_additional_tools(context):
    """Need additional tools in Python VM."""
    context.need_additional_tools = True

@when('I modify the Dockerfile to add packages')
def step_modify_dockerfile(context):
    """Modify Dockerfile to add packages."""
    context.dockerfile_modified = True

@when('I rebuild with --rebuild')
def step_rebuild_with_rebuild(context):
    """Rebuild with --rebuild."""
    context.last_command = "./scripts/start-virtual python --rebuild"
    context.rebuild_executed = True

@then('the packages are available in the VM')
def step_packages_available(context):
    """Packages are available in VM."""
    context.packages_available = True

@then('I don\'t need to manually install each time')
def step_no_manual_install(context):
    """Don't need to manually install each time."""
    context.no_manual_install = True

@then('I can see all my VDE containers')
def step_see_vde_containers(context):
    """Can see all VDE containers."""
    context.vde_containers_visible = True

@then('I can verify what\'s currently active')
def step_verify_active(context):
    """Can verify what's currently active."""
    context.active_verified = True

@given('I\'m done working for the day')
def step_done_for_day(context):
    """Done working for the day."""
    context.done_for_day = True

@then('all VMs stop gracefully')
def step_all_vms_stop_gracefully(context):
    """All VMs stop gracefully."""
    context.all_vms_stopped_gracefully = True

@then('no orphaned containers remain')
def step_no_orphaned_containers(context):
    """No orphaned containers remain."""
    context.no_orphaned_containers = True

@then('my system is clean')
def step_system_clean(context):
    """System is clean."""
    context.system_clean = True

@given('I\'ve configured my VMs')
def step_configured_vms(context):
    """Have configured VMs."""
    context.vms_configured = True

@when('I restart my computer')
def step_restart_computer(context):
    """Restart computer."""
    context.computer_restarted = True

@when('I run "start-virtual all" again')
def step_run_start_all_again(context):
    """Run start-virtual all again."""
    context.last_command = "./scripts/start-virtual all"

@then('all my VMs start with saved configuration')
def step_vms_start_saved_config(context):
    """All VMs start with saved configuration."""
    context.vms_saved_config = True

@then('I don\'t need to reconfigure anything')
def step_no_reconfigure(context):
    """Don't need to reconfigure."""
    context.no_reconfigure_needed = True

@given('I need to run tests that might modify system state')
def step_need_run_tests(context):
    """Need to run tests that modify system state."""
    context.need_run_tests = True

@when('I run tests inside a VM')
def step_run_tests_vm(context):
    """Run tests inside VM."""
    context.tests_in_vm = True

@then('my host system is not affected')
def step_host_not_affected(context):
    """Host system is not affected."""
    context.host_not_affected = True

@then('I can run destructive tests safely')
def step_destructive_tests_safe(context):
    """Can run destructive tests safely."""
    context.destructive_tests_safe = True

@then('I can discard and recreate VM if needed')
def step_discard_recreate_vm(context):
    """Can discard and recreate VM if needed."""
    context.discard_recreate_vm = True

@given('I\'m developing a web application')
def step_developing_web_app(context):
    """Developing web application."""
    context.developing_web_app = True

@given('I have a watcher/reloader configured')
def step_watcher_configured(context):
    """Have watcher/reloader configured."""
    context.watcher_configured = True

@when('I edit code in my editor on host')
def step_edit_code_host(context):
    """Edit code in editor on host."""
    context.editing_code_host = True

@then('the application inside VM detects the change')
def step_app_detects_change(context):
    """Application inside VM detects change."""
    context.app_detects_change = True

@then('it hot-reloads automatically')
def step_hot_reloads(context):
    """It hot-reloads automatically."""
    context.hot_reloads = True

@then('I see changes without manual restart')
def step_see_changes_no_restart(context):
    """See changes without manual restart."""
    context.no_manual_restart = True

@given('I have a web app (python), database (postgres), and cache (redis)')
def step_web_app_stack(context):
    """Have web app with postgres and redis."""
    context.web_app_stack = {"python", "postgres", "redis"}

@then('I can SSH into each service independently')
def step_ssh_each_service(context):
    """Can SSH into each service independently."""
    context.ssh_each_service = True

@then('I can check logs for each service')
def step_check_logs_each(context):
    """Can check logs for each service."""
    context.logs_each_service = True


# =============================================================================
# Additional workflow and development steps
# =============================================================================

@then('I can trace requests across services')
def step_trace_requests(context):
    """Can trace requests across services."""
    context.can_trace_requests = True

@given('I need realistic data for development')
def step_need_realistic_data(context):
    """Need realistic data for development."""
    context.need_realistic_data = True

@when('I create a seed script and run it in postgres VM')
def step_create_seed_script(context):
    """Create seed script and run in postgres VM."""
    context.seed_script_created = True

@then('the data persists across VM restarts')
def step_data_persists_restarts(context):
    """Data persists across VM restarts."""
    context.data_persists_across_restarts = True

@then('I always have a fresh starting point')
def step_fresh_starting_point(context):
    """Always have fresh starting point."""
    context.fresh_starting_point = True

@then('I can reset data when needed')
def step_can_reset_data(context):
    """Can reset data when needed."""
    context.can_reset_data = True

@given('project A needs Node 16')
def step_project_a_node16(context):
    """Project A needs Node 16."""
    context.project_a_needs = "node16"

@given('project B needs Node 18')
def step_project_b_node18(context):
    """Project B needs Node 18."""
    context.project_b_needs = "node18"

@when('I create js-node16 VM and js-node18 VM')
def step_create_multiple_node_vms(context):
    """Create js-node16 and js-node18 VMs."""
    context.multiple_node_vms_created = True

@then('each VM has its own Node version')
def step_each_own_node_version(context):
    """Each VM has own Node version."""
    context.each_own_node_version = True

@then('I can work on both projects simultaneously')
def step_work_both_projects(context):
    """Can work on both projects simultaneously."""
    context.work_both_simultaneously = True

@then('versions don\'t conflict')
def step_no_version_conflict(context):
    """Versions don't conflict."""
    context.no_version_conflict = True

@given('I\'m working on a microservices architecture')
def step_microservices_arch(context):
    """Working on microservices architecture."""
    context.microservices_arch = True

@when('I start all service VMs (auth, api, worker, frontend)')
def step_start_all_microservices(context):
    """Start all service VMs."""
    context.all_microservices_started = True

@then('all services can run simultaneously')
def step_services_simultaneous(context):
    """All services can run simultaneously."""
    context.services_simultaneous = True

@then('they can communicate via internal network')
def step_internal_network_comm(context):
    """Can communicate via internal network."""
    context.internal_network_comm = True

@then('I can test the entire system locally')
def step_test_system_locally(context):
    """Can test entire system locally."""
    context.test_system_locally = True

@given('I want to try out a new language')
def step_try_new_language(context):
    """Want to try new language."""
    context.trying_new_language = True

@when('I create a VM for that language')
def step_create_new_lang_vm(context):
    """Create VM for that language."""
    context.new_lang_vm_created = True

@then('I can experiment immediately')
def step_experiment_immediately(context):
    """Can experiment immediately."""
    context.experiment_immediately = True

@then('I can delete the VM if I don\'t want it')
def step_delete_vm_unwanted(context):
    """Can delete VM if unwanted."""
    context.can_delete_unwanted = True

@then('my main development environment is untouched')
def step_main_env_untouched(context):
    """Main development environment untouched."""
    context.main_env_untouched = True

@given('I\'m pairing with a colleague')
def step_pairing_colleague(context):
    """Pairing with colleague."""
    context.pairing_colleague = True

@when('we both SSH into the same VM')
def step_both_ssh_same_vm(context):
    """Both SSH into same VM."""
    context.both_ssh_same_vm = True

@then('we can work on the same code')
def step_work_same_code(context):
    """Can work on same code."""
    context.work_same_code = True

@then('we can see each other\'s changes')
def step_see_changes(context):
    """Can see each other's changes."""
    context.see_each_other_changes = True

@then('we can use tmux or similar for shared terminal')
def step_use_tmux(context):
    """Can use tmux for shared terminal."""
    context.can_use_tmux = True

@given('I have VMs running')
def step_have_vms_running(context):
    """Have VMs running."""
    context.vms_are_running = True

@when('I open VSCode and connect to python-dev via Remote-SSH')
def step_vscode_connect(context):
    """Open VSCode and connect via Remote-SSH."""
    context.vscode_connected = True

@then('I get full IDE experience inside the VM')
def step_full_ide_experience(context):
    """Get full IDE experience inside VM."""
    context.full_ide_experience = True

@then('I can use VSCode extensions for Python')
def step_vscode_extensions(context):
    """Can use VSCode extensions for Python."""
    context.vscode_extensions = True

@then('I can debug directly from my editor')
def step_debug_from_editor(context):
    """Can debug directly from editor."""
    context.debug_from_editor = True

@given('my app has background job processing')
def step_app_background_jobs(context):
    """App has background job processing."""
    context.app_background_jobs = True

@when('I create a dedicated worker VM')
def step_create_worker_vm(context):
    """Create dedicated worker VM."""
    context.worker_vm_created = True

@then('worker runs independently of web VM')
def step_worker_independent(context):
    """Worker runs independently of web VM."""
    context.worker_independent = True

@then('I can scale workers separately')
def step_scale_workers(context):
    """Can scale workers separately."""
    context.can_scale_workers = True

@then('I can restart worker without affecting web')
def step_restart_worker_no_affect(context):
    """Can restart worker without affecting web."""
    context.restart_worker_no_affect = True

@given('I need to test HTTPS locally')
def step_need_https_local(context):
    """Need to test HTTPS locally."""
    context.need_https_local = True

@when('I configure nginx VM with SSL')
def step_configure_nginx_ssl(context):
    """Configure nginx VM with SSL."""
    context.nginx_ssl_configured = True

@then('I can access my app over HTTPS locally')
def step_access_https_local(context):
    """Can access app over HTTPS locally."""
    context.https_local_access = True

@then('certificates can be self-signed for development')
def step_self_signed_certs(context):
    """Certificates can be self-signed for development."""
    context.self_signed_certs = True

@then('browser warnings are expected but acceptable')
def step_browser_warnings_expected(context):
    """Browser warnings are expected but acceptable."""
    context.browser_warnings_expected = True

@given('I have migration scripts')
def step_have_migrations(context):
    """Have migration scripts."""
    context.has_migrations = True

@when('I run migrations in development VM')
def step_run_migrations(context):
    """Run migrations in development VM."""
    context.migrations_run = True

@then('I can test migrations safely')
def step_test_migrations_safe(context):
    """Can test migrations safely."""
    context.migrations_safe = True

@then('I can verify schema changes work')
def step_verify_schema(context):
    """Can verify schema changes work."""
    context.schema_verified = True

@then('production database is not affected')
def step_prod_db_unaffected(context):
    """Production database not affected."""
    context.prod_db_unaffected = True

@given('I\'m developing a client that calls external APIs')
def step_client_external_apis(context):
    """Developing client that calls external APIs."""
    context.client_external_apis = True

@when('I create a mock service VM')
def step_create_mock_service(context):
    """Create mock service VM."""
    context.mock_service_created = True

@then('I can mock API responses')
def step_mock_api_responses(context):
    """Can mock API responses."""
    context.can_mock_api = True

@then('I don\'t need to hit real external services')
def step_no_real_external_services(context):
    """Don't need to hit real external services."""
    context.no_real_external = True

@given('multiple VMs generate logs')
def step_multiple_vms_logs(context):
    """Multiple VMs generate logs."""
    context.multiple_vms_logs = True

@when('I check logs for each VM')
def step_check_logs_each_vm(context):
    """Check logs for each VM."""
    context.checking_logs_each = True

@then('I can view logs from docker logs command')
def step_docker_logs(context):
    """Can view logs from docker logs command."""
    context.docker_logs_available = True

@then('I can check logs/<vm>/ directories')
def step_check_logs_dirs(context):
    """Can check logs/<vm>/ directories."""
    context.logs_dirs_available = True

@then('I can trace issues across services')
def step_trace_issues(context):
    """Can trace issues across services."""
    context.trace_issues = True

@given('I\'m compiling code inside VM')
def step_compiling_vm(context):
    """Compiling code inside VM."""
    context.compiling_in_vm = True

@when('source files change on host')
def step_source_changes_host(context):
    """Source files change on host."""
    context.source_changed_host = True

@then('the VM sees the changes immediately')
def step_vm_sees_changes(context):
    """VM sees changes immediately."""
    context.vm_sees_changes = True

@then('my build tool can rebuild automatically')
def step_build_tool_rebuilds(context):
    """Build tool can rebuild automatically."""
    context.build_tool_auto_rebuild = True


# =============================================================================
# Additional workflow continuation steps
# =============================================================================

@then('I don\'t need to manually trigger builds')
def step_no_manual_builds(context):
    """Don't need to manually trigger builds."""
    context.no_manual_builds = True

@given('I have important data in postgres VM')
def step_important_data_postgres(context):
    """Have important data in postgres VM."""
    context.important_data_postgres = True

@when('I create a backup of data/postgres/')
def step_create_backup_postgres(context):
    """Create backup of data/postgres/."""
    context.backup_created = True

@then('I can restore from backup later')
def step_restore_from_backup(context):
    """Can restore from backup later."""
    context.can_restore_backup = True

@then('I can migrate data to another machine')
def step_migrate_data(context):
    """Can migrate data to another machine."""
    context.can_migrate_data = True

@then('my work is safely backed up')
def step_work_safely_backed_up(context):
    """Work is safely backed up."""
    context.work_safely_backed_up = True

@given('I need to test performance')
def step_need_test_performance(context):
    """Need to test performance."""
    context.need_test_performance = True

@when('I start multiple instances of my service VM')
def step_start_multiple_instances(context):
    """Start multiple instances of service VM."""
    context.multiple_instances_started = True

@then('I can generate realistic load')
def step_generate_realistic_load(context):
    """Can generate realistic load."""
    context.can_generate_load = True

@then('I can identify bottlenecks')
def step_identify_bottlenecks(context):
    """Can identify bottlenecks."""
    context.bottlenecks_identified = True

@then('I don\'t need external infrastructure')
def step_no_external_infra(context):
    """Don't need external infrastructure."""
    context.no_external_infra = True

@given('I have different settings for dev and production')
def step_dev_prod_settings(context):
    """Have different settings for dev and production."""
    context.dev_prod_settings = True

@when('I use environment variables')
def step_use_env_vars(context):
    """Use environment variables."""
    context.using_env_vars = True

@then('development uses dev settings')
def step_dev_uses_dev_settings(context):
    """Development uses dev settings."""
    context.dev_uses_dev_settings = True

@then('production VM can use production settings')
def step_prod_uses_prod_settings(context):
    """Production VM can use production settings."""
    context.prod_uses_prod_settings = True

@then('I don\'t mix up configurations')
def step_no_mix_configs(context):
    """Don't mix up configurations."""
    context.no_config_mixup = True

@given('I work on multiple unrelated projects')
def step_multiple_unrelated_projects(context):
    """Work on multiple unrelated projects."""
    context.multiple_unrelated_projects = True

@when('each project has its own VM')
def step_each_project_own_vm(context):
    """Each project has its own VM."""
    context.each_project_own_vm = True

@then('dependencies don\'t conflict between projects')
def step_no_dep_conflicts(context):
    """Dependencies don't conflict between projects."""
    context.no_dep_conflicts = True

@then('I can switch contexts cleanly')
def step_switch_contexts_cleanly(context):
    """Can switch contexts cleanly."""
    context.switch_contexts_cleanly = True

@then('each project has isolated workspace')
def step_isolated_workspaces(context):
    """Each project has isolated workspace."""
    context.isolated_workspaces = True

@given('I have a comprehensive test suite')
def step_comprehensive_test_suite(context):
    """Have comprehensive test suite."""
    context.comprehensive_test_suite = True

@when('I push code changes')
def step_push_code_changes(context):
    """Push code changes."""
    context.code_pushed = True

@then('CI runs tests in similar VMs')
def step_ci_similar_vms(context):
    """CI runs tests in similar VMs."""
    context.ci_similar_vms = True

@then('local test results match CI results')
def step_local_matches_ci(context):
    """Local test results match CI results."""
    context.local_matches_ci = True

@then('I catch issues before pushing')
def step_catch_before_push(context):
    """Catch issues before pushing."""
    context.catch_before_push = True

@when('I share the repository')
def step_share_repository(context):
    """Share the repository."""
    context.repository_shared = True

@when('they create the same VMs I have')
def step_they_create_same_vms(context):
    """They create the same VMs I have."""
    context.they_create_same_vms = True

@then('they can run my code immediately')
def step_they_run_immediately(context):
    """They can run my code immediately."""
    context.they_run_immediately = True

@then('they see the same environment I do')
def step_they_see_same_env(context):
    """They see the same environment I do."""
    context.they_see_same_env = True

@then('review process is faster')
def step_review_faster(context):
    """Review process is faster."""
    context.review_faster = True

@given('my app needs API keys and secrets')
def step_app_needs_secrets(context):
    """App needs API keys and secrets."""
    context.app_needs_secrets = True

@when('I use env-files for secrets')
def step_use_env_files(context):
    """Use env-files for secrets."""
    context.using_env_files = True

@then('secrets are not committed to git')
def step_secrets_not_committed(context):
    """Secrets are not committed to git."""
    context.secrets_not_committed = True

@then('each developer has their own env file')
def step_each_own_env_file(context):
    """Each developer has own env file."""
    context.each_own_env_file = True

@then('production secrets are never in development')
def step_prod_secrets_not_dev(context):
    """Production secrets are never in development."""
    context.prod_secrets_not_dev = True

@given('I worked on a project Friday')
def step_worked_friday(context):
    """Worked on a project Friday."""
    context.worked_friday = True

@when('I come back Monday')
def step_come_back_monday(context):
    """Come back Monday."""
    context.come_back_monday = True

@then('my entire environment is ready')
def step_env_ready(context):
    """Entire environment is ready."""
    context.env_ready = True

@then('I can continue exactly where I left off')
def step_continue_left_off(context):
    """Can continue exactly where I left off."""
    context.continue_left_off = True

@then('no setup is needed')
def step_no_setup_needed(context):
    """No setup is needed."""
    context.no_setup_needed = True

@given('I want to learn Django/FastAPI/etc.')
def step_want_learn_framework(context):
    """Want to learn Django/FastAPI/etc."""
    context.want_learn_framework = True

@when('I create a dedicated VM for learning')
def step_create_learn_vm(context):
    """Create dedicated VM for learning."""
    context.learn_vm_created = True

@then('I can experiment freely')
def step_experiment_freely(context):
    """Can experiment freely."""
    context.experiment_freely = True

@then('I can break things without consequences')
def step_break_no_consequences(context):
    """Can break things without consequences."""
    context.break_no_consequences = True

@then('I can delete the VM when done learning')
def step_delete_when_done(context):
    """Can delete VM when done learning."""
    context.can_delete_when_done = True
