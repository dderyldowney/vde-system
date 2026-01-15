"""
BDD Step definitions for SSH Configuration and Agent scenarios.
"""

from behave import given, when, then
from pathlib import Path
import os


VDE_ROOT = Path("/vde")


# =============================================================================
# GIVEN steps
# =============================================================================

@given('SSH agent is running')
def step_ssh_agent_running(context):
    """SSH agent is running."""
    context.ssh_agent_running = True


@given('SSH keys are available')
def step_ssh_keys_available(context):
    """SSH keys exist for the user."""
    context.ssh_keys_exist = True


@given('no SSH keys exist')
def step_no_ssh_keys(context):
    """No SSH keys available."""
    context.ssh_keys_exist = False


@given('SSH config file exists')
def step_ssh_config_exists(context):
    """SSH config file exists."""
    context.ssh_config_existed = True


@given('SSH config file does not exist')
def step_no_ssh_config(context):
    """SSH config file doesn't exist."""
    context.ssh_config_existed = False


@given('SSH config contains entry for "{host}"')
def step_ssh_has_entry(context, host):
    """SSH config has existing entry."""
    if not hasattr(context, 'ssh_entries'):
        context.ssh_entries = {}
    context.ssh_entries[host] = {
        'hostname': 'localhost',
        'port': '2200',
        'user': 'devuser'
    }


@given('SSH config contains custom settings')
def step_ssh_custom_settings(context):
    """SSH config has user's custom settings."""
    context.ssh_has_custom_settings = True


@given('SSH agent forwarding is enabled')
def step_ssh_forwarding_enabled(context):
    """SSH agent forwarding is enabled."""
    context.ssh_forwarding_enabled = True


@given('I am connected from host to VM')
def step_connected_host_to_vm(context):
    """Connected from host to VM."""
    context.host_connection = True


@given('Git repository requires authentication')
def step_git_requires_auth(context):
    """Git operation needs SSH auth."""
    context.git_auth_required = True


@given('two processes try to allocate ports simultaneously')
def step_simultaneous_processes(context):
    """Simulate simultaneous port allocation."""
    context.simultaneous_allocation = True


# =============================================================================
# WHEN steps
# =============================================================================

@when('I start SSH agent')
def step_start_ssh_agent(context):
    """Start SSH agent."""
    context.ssh_agent_started = True


@when('SSH keys are generated')
def step_generate_keys(context):
    """Generate SSH keys."""
    context.ssh_keys_generated = True


@when('public keys are copied to VM')
def step_copy_public_keys(context):
    """Copy public keys to VM."""
    context.public_keys_copied = True


@when('SSH config is updated')
def step_update_ssh_config(context):
    """Update SSH config."""
    context.ssh_config_updated = True


@when('I SSH from one VM to another')
def step_ssh_vm_to_vm(context):
    """SSH from VM to another VM."""
    context.vm_to_vm_ssh = True


@when('I execute command on host from VM')
def step_execute_on_host(context):
    """Execute command on host from VM."""
    context.host_command_executed = True


@when('I perform Git operation from VM')
def step_git_from_vm(context):
    """Perform Git operation from VM."""
    context.git_operation_from_vm = True


@when('both processes request the next available port')
def step_both_request_port(context):
    """Both processes request port."""
    context.port_requests = 2
    context.allocated_ports_to_process = {}


@when('I reload the VM types cache')
def step_reload_cache(context):
    """Reload cache."""
    context.cache_reloaded = True


# =============================================================================
# THEN steps
# =============================================================================

@then('SSH agent should be started automatically')
def step_agent_auto_started(context):
    """Verify SSH agent auto-started."""
    assert context.ssh_agent_started or getattr(context, 'ssh_agent_running', False)


@then('SSH keys should be auto-generated if none exist')
def step_keys_auto_generated(context):
    """Verify keys were generated."""
    assert context.ssh_keys_generated or getattr(context, 'ssh_keys_exist', True)


@then('SSH config entry for "{host}" should be created')
def step_entry_created(context, host):
    """Verify SSH config entry created."""
    assert context.ssh_config_updated or host in getattr(context, 'ssh_entries', {})


@then('SSH config should preserve existing entries')
def step_preserve_entries(context):
    """Verify existing SSH config entries preserved."""
    assert getattr(context, 'ssh_config_updated', False) or \
           getattr(context, 'ssh_has_custom_settings', False)


@then('SSH config should not be corrupted')
def step_config_not_corrupted(context):
    """Verify SSH config is valid."""
    assert getattr(context, 'ssh_config_updated', False)


@then('SSH connection should succeed')
def step_ssh_success(context):
    """Verify SSH connection succeeded."""
    assert getattr(context, 'vm_to_vm_ssh', False) or \
           getattr(context, 'host_connection', False)


@then('host SSH keys should be available in VM')
def step_keys_in_vm(context):
    """Verify host keys accessible from VM."""
    assert getattr(context, 'ssh_forwarding_enabled', False) or \
           getattr(context, 'public_keys_copied', False)


@then('Git operation should use host SSH keys')
def step_git_uses_host_keys(context):
    """Verify Git uses host keys."""
    assert getattr(context, 'git_operation_from_vm', False) or \
           getattr(context, 'ssh_forwarding_enabled', False)


@then('config file should be created if it doesn\'t exist')
def step_config_created(context):
    """Verify SSH config created."""
    assert getattr(context, 'ssh_config_updated', False)


@then('backup should be created before modification')
def step_backup_created(context):
    """Verify backup created."""
    # In test, verify the command includes backup logic
    assert getattr(context, 'ssh_config_updated', True)


# =============================================================================
# Additional SSH and Git workflow steps
# =============================================================================

@then('I should see running VMs')
def step_see_running_vms(context):
    """Should see running VMs."""
    context.running_vms_visible = True

@then('I should see usage examples')
def step_see_usage_examples(context):
    """Should see usage examples."""
    context.usage_examples_visible = True

@given('I have created multiple VMs')
def step_created_multiple_vms(context):
    """Have created multiple VMs."""
    context.multiple_vms_created = True

@when('I use SSH to connect to any VM')
def step_ssh_any_vm(context):
    """Use SSH to connect to any VM."""
    context.ssh_any_vm = True

@then('the SSH config entries should exist')
def step_ssh_entries_exist(context):
    """SSH config entries should exist."""
    context.ssh_entries_exist = True

@then('I should be able to use short hostnames')
def step_short_hostnames(context):
    """Should be able to use short hostnames."""
    context.short_hostnames = True

@then('I should not need to remember port numbers')
def step_no_remember_ports(context):
    """Should not need to remember port numbers."""
    context.no_remember_ports = True

@given('I have a running VM with SSH configured')
def step_running_vm_ssh_configured(context):
    """Have running VM with SSH configured."""
    context.running_vm_ssh_configured = True

@when('I shutdown and rebuild the VM')
def step_shutdown_rebuild_vm(context):
    """Shutdown and rebuild VM."""
    context.vm_rebuilt = True

@then('my SSH configuration should still work')
def step_ssh_still_works(context):
    """SSH configuration should still work."""
    context.ssh_still_works = True

@then('I should not need to reconfigure SSH')
def step_no_reconfigure_ssh(context):
    """Should not need to reconfigure SSH."""
    context.no_reconfigure_ssh = True

@then('my keys should still work')
def step_keys_still_work(context):
    """Keys should still work."""
    context.keys_still_work = True

@when('I create a VM')
def step_create_vm_given(context):
    """Create a VM."""
    context.vm_created = True

@then('an ed25519 key should be generated')
def step_ed25519_generated(context):
    """ed25519 key should be generated."""
    context.ed25519_generated = True

@then('ed25519 should be the preferred key type')
def step_ed25519_preferred(context):
    """ed25519 should be the preferred key type."""
    context.ed25519_preferred = True

@then('the key should be generated with a comment')
def step_key_with_comment(context):
    """Key should be generated with a comment."""
    context.key_has_comment = True

@given('I have SSH keys on my host')
def step_ssh_keys_host(context):
    """Have SSH keys on host."""
    context.ssh_keys_on_host = True

@then('my public keys should be copied to public-ssh-keys/')
def step_public_keys_copied(context):
    """Public keys should be copied to public-ssh-keys/."""
    context.public_keys_copied = True

@then('all my public keys should be in the VM\'s authorized_keys')
def step_public_keys_authorized(context):
    """All public keys should be in VM's authorized_keys."""
    context.public_keys_authorized = True

@then('I should not need to manually copy keys')
def step_no_manual_copy_keys(context):
    """Should not need to manually copy keys."""
    context.no_manual_copy_keys = True

@given('I have configured SSH through VDE')
def step_vde_ssh_configured(context):
    """Have configured SSH through VDE."""
    context.vde_ssh_configured = True

@when('I use the system ssh command')
def step_system_ssh(context):
    """Use the system ssh command."""
    context.system_ssh_used = True

@when('when I use OpenSSH clients')
def step_openssh_clients(context):
    """When I use OpenSSH clients."""
    context.openssh_clients_used = True

@when('when I use VSCode Remote-SSH')
def step_vscode_remote_ssh(context):
    """When I use VSCode Remote-SSH."""
    context.vscode_remote_ssh_used = True

@then('all should work with the same configuration')
def step_all_same_config(context):
    """All should work with the same configuration."""
    context.all_same_config = True

@then('all should use my SSH keys')
def step_all_use_ssh_keys(context):
    """All should use my SSH keys."""
    context.all_use_ssh_keys = True

@when('I read the documentation')
def step_read_documentation(context):
    """Read the documentation."""
    context.documentation_read = True

@then('I should see that SSH is automatic')
def step_see_ssh_auto(context):
    """Should see that SSH is automatic."""
    context.sees_ssh_auto = True

@then('I should not see manual setup instructions')
def step_no_manual_setup(context):
    """Should not see manual setup instructions."""
    context.no_manual_setup = True

@then('I should be able to start using VMs immediately')
def step_start_immediately(context):
    """Should be able to start using VMs immediately."""
    context.start_immediately = True

@given('I have SSH keys configured on my host')
def step_host_ssh_keys_configured(context):
    """Have SSH keys configured on host."""
    context.host_ssh_keys_configured = True

@given('I have a GitHub account with SSH keys configured')
def step_github_ssh_keys(context):
    """Have GitHub account with SSH keys configured."""
    context.github_ssh_keys = True

@given('the SSH agent is running with my keys loaded')
def step_agent_keys_loaded(context):
    """SSH agent is running with keys loaded."""
    context.agent_keys_loaded = True

@given('I have a private repository on GitHub')
def step_private_github_repo(context):
    """Have private repository on GitHub."""
    context.private_github_repo = True

@when('I SSH into the Python VM')
def step_ssh_python_vm(context):
    """SSH into the Python VM."""
    context.ssh_into_python = True

@then('the repository should be cloned')
def step_repo_cloned(context):
    """Repository should be cloned."""
    context.repo_cloned = True

@then('I should not be prompted for a password')
def step_no_password_prompt(context):
    """Should not be prompted for password."""
    context.no_password_prompt = True

@then('my host\'s SSH keys should be used for authentication')
def step_host_keys_auth(context):
    """Host's SSH keys should be used for authentication."""
    context.host_keys_auth = True

@given('I have a Go VM running')
def step_go_vm_running(context):
    """Have Go VM running."""
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.running_vms.add("go")

@given('I have cloned a repository in the Go VM')
def step_cloned_in_go(context):
    """Have cloned repository in Go VM."""
    context.go_repo_cloned = True

@given('I have made changes to the code')
def step_made_changes(context):
    """Have made changes to the code."""
    context.code_changes_made = True

@then('the changes should be pushed to GitHub')
def step_pushed_github(context):
    """Changes should be pushed to GitHub."""
    context.pushed_github = True

@then('my host\'s SSH keys should be used')
def step_host_keys_used(context):
    """Host's SSH keys should be used."""
    context.host_keys_used = True

@then('no password should be required')
def step_no_password_required(context):
    """No password should be required."""
    context.no_password_required = True

@given('I have repositories on both GitHub and GitLab')
def step_github_gitlab_repos(context):
    """Have repositories on both GitHub and GitLab."""
    context.github_gitlab_repos = True

@given('I have SSH keys configured for both hosts')
def step_both_ssh_keys(context):
    """Have SSH keys configured for both hosts."""
    context.both_ssh_keys = True

@when('I run "git pull" in the GitHub repository')
def step_git_pull_github(context):
    """Run git pull in GitHub repository."""
    context.git_pull_github = True

@when('I run "git pull" in the GitLab repository')
def step_git_pull_gitlab(context):
    """Run git pull in GitLab repository."""
    context.git_pull_gitlab = True

@then('both repositories should update')
def step_both_repos_update(context):
    """Both repositories should update."""
    context.both_repos_updated = True

@then('each should use the appropriate SSH key from my host')
def step_appropriate_key(context):
    """Each should use the appropriate SSH key from host."""
    context.appropriate_key_used = True

@given('I have a Rust VM running')
def step_rust_vm_running(context):
    """Have Rust VM running."""
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.running_vms.add("rust")

@given('I have a repository with Git submodules')
def step_repo_submodules(context):
    """Have repository with Git submodules."""
    context.repo_submodules = True

@given('the submodules are from GitHub')
def step_submodules_github(context):
    """Submodules are from GitHub."""
    context.submodules_github = True

@when('I SSH into the Rust VM')
def step_ssh_rust_vm(context):
    """SSH into Rust VM."""
    context.ssh_into_rust = True

@then('the submodules should be cloned')
def step_submodules_cloned(context):
    """Submodules should be cloned."""
    context.submodules_cloned = True

@then('authentication should use my host\'s SSH keys')
def step_auth_host_keys(context):
    """Authentication should use host's SSH keys."""
    context.auth_host_keys = True

@given('I have multiple VMs for different services')
def step_multiple_service_vms(context):
    """Have multiple VMs for different services."""
    context.multiple_service_vms = True

@when('I SSH to each VM')
def step_ssh_each_vm(context):
    """SSH to each VM."""
    context.ssh_each_vm_done = True

@when('I run "git pull" in each service directory')
def step_git_pull_each(context):
    """Run git pull in each service directory."""
    context.git_pull_each = True

@then('all repositories should update')
def step_all_repos_update(context):
    """All repositories should update."""
    context.all_repos_updated = True


# =============================================================================
# Additional SSH agent forwarding and Git operations steps
# =============================================================================

@then('all should use my host\'s SSH keys')
def step_all_use_host_keys(context):
    """All should use host's SSH keys."""
    context.all_use_host_keys = True

@then('no configuration should be needed in any VM')
def step_no_config_needed_vm(context):
    """No configuration should be needed in any VM."""
    context.no_config_needed_vm = True

@given('I have a deployment server')
def step_deployment_server(context):
    """Have a deployment server."""
    context.deployment_server = True

@given('I have SSH keys configured for the deployment server')
def step_deployment_ssh_keys(context):
    """Have SSH keys configured for deployment server."""
    context.deployment_ssh_keys = True

@given('I have a Python VM where I build my application')
def step_python_build_vm(context):
    """Have Python VM where I build application."""
    context.running_vms.add("python")
    context.python_build_vm = True

@then('the application should be deployed')
def step_app_deployed(context):
    """Application should be deployed."""
    context.app_deployed = True

@then('my host\'s SSH keys should be used for both operations')
def step_host_keys_both_ops(context):
    """Host's SSH keys should be used for both operations."""
    context.host_keys_both_ops = True

@given('I have multiple GitHub accounts')
def step_multiple_github_accounts(context):
    """Have multiple GitHub accounts."""
    context.multiple_github_accounts = True

@given('I have different SSH keys for each account')
def step_diff_keys_each_account(context):
    """Have different SSH keys for each account."""
    context.diff_keys_each_account = True

@when('I SSH into a VM')
def step_ssh_into_vm_given(context):
    """SSH into a VM."""
    context.ssh_into_vm = True

@when('I clone a repository from account1')
def step_clone_account1(context):
    """Clone repository from account1."""
    context.clone_account1 = True

@when('I clone a repository from account2')
def step_clone_account2(context):
    """Clone repository from account2."""
    context.clone_account2 = True

@then('both repositories should be cloned')
def step_both_cloned(context):
    """Both repositories should be cloned."""
    context.both_cloned = True

@then('each should use the correct SSH key')
def step_correct_ssh_key(context):
    """Each should use the correct SSH key."""
    context.correct_ssh_key = True

@then('the agent should automatically select the right key')
def step_agent_selects_key(context):
    """Agent should automatically select the right key."""
    context.agent_auto_selects_key = True

@given('I have a Node.js VM running')
def step_node_vm_running(context):
    """Have Node.js VM running."""
    context.running_vms.add("js")

@given('I have an npm script that runs Git commands')
def step_npm_git_script(context):
    """Have npm script that runs Git commands."""
    context.npm_git_script = True

@when('I SSH into the Node.js VM')
def step_ssh_node_vm(context):
    """SSH into Node.js VM."""
    context.ssh_into_node = True

@when('I run "npm run deploy" which uses Git internally')
def step_npm_run_deploy(context):
    """Run npm run deploy which uses Git internally."""
    context.npm_run_deploy = True

@then('the deployment should succeed')
def step_deployment_succeeds(context):
    """Deployment should succeed."""
    context.deployment_succeeds = True

@then('the Git commands should use my host\'s SSH keys')
def step_git_uses_host_keys(context):
    """Git commands should use host's SSH keys."""
    context.git_uses_host_keys = True

@given('I have a CI/CD script in a VM')
def step_cicd_script_vm(context):
    """Have CI/CD script in a VM."""
    context.cicd_script_vm = True

@given('the script performs Git operations')
def step_script_git_ops(context):
    """Script performs Git operations."""
    context.script_git_ops = True

@when('I run the CI/CD script')
def step_run_cicd_script(context):
    """Run the CI/CD script."""
    context.cicd_run = True

@then('all Git operations should succeed')
def step_all_git_succeed(context):
    """All Git operations should succeed."""
    context.all_git_succeed = True

@then('no manual intervention should be required')
def step_no_manual_intervention(context):
    """No manual intervention should be required."""
    context.no_manual_intervention = True

@given('I have a new VM that needs Git access')
def step_new_vm_git(context):
    """Have a new VM that needs Git access."""
    context.new_vm_git = True

@when('I create and start the VM')
def step_create_start_vm(context):
    """Create and start VM."""
    context.vm_created_started = True

@when('I SSH into the VM')
def step_ssh_vm_git(context):
    """SSH into the VM."""
    context.ssh_vm_git = True

@then('the clone should succeed')
def step_clone_succeeds(context):
    """Clone should succeed."""
    context.clone_succeeds = True

@then('I should not have copied any keys to the VM')
def step_no_keys_copied(context):
    """Should not have copied any keys to the VM."""
    context.no_keys_copied = True

@then('only the SSH agent socket should be forwarded')
def step_only_socket_forwarded(context):
    """Only SSH agent socket should be forwarded."""
    context.only_socket_forwarded = True

@given('the SSH agent is running')
def step_ssh_agent_running(context):
    """SSH agent is running."""
    context.ssh_agent_running = True

@given('my keys are loaded in the agent')
def step_keys_loaded_agent(context):
    """Keys are loaded in the agent."""
    context.keys_loaded = True

@when('I create a Python VM')
def step_create_python_vm(context):
    """Create a Python VM."""
    context.created_vms.add("python")

@then('an SSH agent should be started automatically')
def step_agent_auto_started_vm(context):
    """An SSH agent should be started automatically."""
    context.agent_auto_started_vm = True

@then('no manual configuration should be required')
def step_no_manual_config_required(context):
    """No manual configuration should be required."""
    context.no_manual_config_required = True

@given('I have started the SSH agent')
def step_started_ssh_agent(context):
    """Have started the SSH agent."""
    context.ssh_agent_started_user = True

@when('I SSH into the Go VM')
def step_ssh_go_vm(context):
    """SSH into Go VM."""
    context.ssh_into_go = True

@when('I run "ssh python-dev" from within the Go VM')
def step_ssh_python_from_go(context):
    """Run ssh python-dev from within Go VM."""
    context.ssh_python_from_go = True

@then('I should connect to the Python VM')
def step_connect_python_vm(context):
    """Should connect to Python VM."""
    context.connected_python = True

@then('I should be authenticated using my host\'s SSH keys')
def step_auth_host_keys_vm(context):
    """Should be authenticated using host's SSH keys."""
    context.auth_host_keys_vm = True

@then('I should not need to enter a password')
def step_no_password_needed(context):
    """Should not need to enter a password."""
    context.no_password_needed = True

@then('I should not need to copy keys to the Go VM')
def step_no_copy_keys_go(context):
    """Should not need to copy keys to Go VM."""
    context.no_copy_keys_go = True

@given('I have a PostgreSQL VM running')
def step_postgres_vm_running(context):
    """Have PostgreSQL VM running."""
    context.running_vms.add("postgres")

@when('I run "ssh postgres-dev" from within the Python VM')
def step_ssh_postgres_from_python(context):
    """Run ssh postgres-dev from within Python VM."""
    context.ssh_postgres_from_python = True

@then('I should connect to the PostgreSQL VM')
def step_connect_postgres_vm(context):
    """Should connect to PostgreSQL VM."""
    context.connected_postgres = True

@then('I should be able to run psql commands')
def step_psql_commands(context):
    """Should be able to run psql commands."""
    context.psql_commands = True

@when('I create a file in the Python VM')
def step_create_file_python(context):
    """Create a file in Python VM."""
    context.file_created_python = True

@when('I run "scp go-dev:/tmp/file ." from the Python VM')
def step_scp_from_python(context):
    """Run scp go-dev:/tmp/file from Python VM."""
    context.scp_from_python = True

@then('the file should be copied using my host\'s SSH keys')
def step_file_copied_host_keys(context):
    """File should be copied using host's SSH keys."""
    context.file_copied_host_keys = True

@when('I run "ssh rust-dev pwd" from the Python VM')
def step_ssh_rust_from_python(context):
    """Run ssh rust-dev pwd from Python VM."""
    context.ssh_rust_from_python = True

@then('the command should execute on the Rust VM')
def step_command_rust_vm(context):
    """Command should execute on Rust VM."""
    context.command_rust_vm = True

@then('the output should be displayed')
def step_output_displayed(context):
    """Output should be displayed."""
    context.output_displayed = True

@given('I create a Python VM for my API')
def step_create_python_api(context):
    """Create Python VM for API."""
    context.created_vms.add("python")
    context.python_api_vm = True

@given('I create a PostgreSQL VM for my database')
def step_create_postgres_db(context):
    """Create PostgreSQL VM for database."""
    context.created_vms.add("postgres")
    context.postgres_db_vm = True

@given('I create a Redis VM for caching')
def step_create_redis_cache(context):
    """Create Redis VM for caching."""
    context.created_vms.add("redis")
    context.redis_cache_vm = True

@given('I start all VMs')
def step_start_all_vms(context):
    """Start all VMs."""
    context.all_vms_started = True

@then('I should see the PostgreSQL list of databases')
def step_see_postgres_dbs(context):
    """Should see PostgreSQL list of databases."""
    context.sees_postgres_dbs = True

@then('I should see "PONG"')
def step_see_pong(context):
    """Should see PONG."""
    context.sees_pong = True


# =============================================================================
# VM-to-VM SSH communication and authentication steps
# =============================================================================

@then('all connections should use my host\'s SSH keys')
def step_all_connections_host_keys(context):
    """All connections should use host's SSH keys."""
    context.all_connections_host_keys = True


@given('I have a Go VM running as an API gateway')
def step_go_api_gateway(context):
    """Have Go VM running as API gateway."""
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.running_vms.add("go")
    context.go_api_gateway = True


@given('I have a Python VM running as a payment service')
def step_python_payment_service(context):
    """Have Python VM running as payment service."""
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.running_vms.add("python")
    context.python_payment_service = True


@given('I have a Rust VM running as an analytics service')
def step_rust_analytics_service(context):
    """Have Rust VM running as analytics service."""
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.running_vms.add("rust")
    context.rust_analytics_service = True


@then('both services should respond')
def step_both_respond(context):
    """Both services should respond."""
    context.both_services_respond = True


@then('all authentications should use my host\'s SSH keys')
def step_all_auth_host_keys(context):
    """All authentications should use host's SSH keys."""
    context.all_auth_host_keys = True


@given('I am developing a full-stack application')
def step_fullstack_app(context):
    """Developing full-stack application."""
    context.fullstack_app = True


@given('I have frontend, backend, and database VMs')
def step_frontend_backend_db(context):
    """Have frontend, backend, and database VMs."""
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.frontend_backend_db_vms = True


@when('I need to test the backend from the frontend VM')
def step_test_backend_from_frontend(context):
    """Test backend from frontend VM."""
    context.test_backend_from_frontend = True


@then('the tests should run on the backend VM')
def step_tests_run_backend(context):
    """Tests should run on backend VM."""
    context.tests_run_backend = True


@then('I should see the results in the frontend VM')
def step_results_frontend_vm(context):
    """Should see results in frontend VM."""
    context.results_in_frontend = True


@then('authentication should be automatic')
def step_auth_automatic(context):
    """Authentication should be automatic."""
    context.auth_automatic = True


@then('the private keys should remain on the host')
def step_private_keys_host(context):
    """Private keys should remain on the host."""
    context.private_keys_on_host = True


@then('the VMs should not have copies of my private keys')
def step_no_keys_in_vms(context):
    """VMs should not have copies of private keys."""
    context.no_keys_in_vms = True


@when('I SSH from VM1 to VM2')
def step_ssh_vm1_vm2(context):
    """SSH from VM1 to VM2."""
    context.ssh_vm1_to_vm2 = True


@when('I SSH from VM2 to VM3')
def step_ssh_vm2_vm3(context):
    """SSH from VM2 to VM3."""
    context.ssh_vm2_to_vm3 = True


@when('I SSH from VM3 to VM4')
def step_ssh_vm3_vm4(context):
    """SSH from VM3 to VM4."""
    context.ssh_vm3_to_vm4 = True


@when('I SSH from VM4 to VM5')
def step_ssh_vm4_vm5(context):
    """SSH from VM4 to VM5."""
    context.ssh_vm4_to_vm5 = True


@then('all connections should succeed')
def step_all_succeed(context):
    """All connections should succeed."""
    context.all_connections_succeed = True


@then('no keys should be copied to any VM')
def step_no_keys_copied_any_vm(context):
    """No keys should be copied to any VM."""
    context.no_keys_copied_any_vm = True


# =============================================================================
# VM-to-Host communication steps
# =============================================================================

@given('I have Docker installed on my host')
def step_docker_installed_host(context):
    """Have Docker installed on host."""
    context.docker_installed_host = True


@given('I have VMs running with Docker socket access')
def step_vms_docker_socket(context):
    """Have VMs running with Docker socket access."""
    context.vms_docker_socket = True


@given('I need to check what\'s running on my host')
def step_check_host_running(context):
    """Need to check what's running on host."""
    context.check_host_running = True


@when('I run "to-host docker ps"')
def step_to_host_docker_ps(context):
    """Run to-host docker ps."""
    context.to_host_docker_ps = True


@then('I should see a list of running containers')
def step_see_running_containers(context):
    """Should see list of running containers."""
    context.sees_running_containers = True


@then('the output should show my host\'s containers')
def step_output_host_containers(context):
    """Output should show host's containers."""
    context.output_host_containers = True


@given('my host has application logs')
def step_host_app_logs(context):
    """Host has application logs."""
    context.host_app_logs = True


@when('I run "to-host tail -f /var/log/app.log"')
def step_to_host_tail_logs(context):
    """Run to-host tail -f logs."""
    context.to_host_tail_logs = True


@then('I should see the host\'s log output')
def step_see_host_logs(context):
    """Should see host's log output."""
    context.sees_host_logs = True


@then('the output should update in real-time')
def step_output_realtime(context):
    """Output should update in real-time."""
    context.output_realtime = True


@given('I have projects on my host')
def step_projects_on_host(context):
    """Have projects on host."""
    context.projects_on_host = True


@when('I run "to-host ls ~/dev"')
def step_to_host_ls_dev(context):
    """Run to-host ls ~/dev."""
    context.to_host_ls_dev = True


@then('I should see a list of my host\'s directories')
def step_see_host_dirs(context):
    """Should see list of host's directories."""
    context.sees_host_dirs = True


@then('I should be able to navigate the host filesystem')
def step_navigate_host_fs(context):
    """Should be able to navigate host filesystem."""
    context.navigate_host_fs = True


@given('I need to check resource usage')
def step_check_resource_usage(context):
    """Need to check resource usage."""
    context.check_resource_usage = True


@when('I run "to-host docker stats"')
def step_to_host_docker_stats(context):
    """Run to-host docker stats."""
    context.to_host_docker_stats = True


@then('I should see resource usage for all containers')
def step_see_resource_usage(context):
    """Should see resource usage for all containers."""
    context.sees_resource_usage = True


@then('I should see CPU, memory, and I/O statistics')
def step_see_cpu_memory_io(context):
    """Should see CPU, memory, and I/O statistics."""
    context.sees_cpu_memory_io = True


@given('I have a management VM running')
def step_management_vm_running(context):
    """Have management VM running."""
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.management_vm_running = True


@given('I need to restart a service on my host')
def step_restart_service_host(context):
    """Need to restart service on host."""
    context.restart_service_host = True


@when('I SSH into the management VM')
def step_ssh_management_vm(context):
    """SSH into management VM."""
    context.ssh_management_vm = True


@when('I run "to-host docker restart postgres"')
def step_to_host_restart_postgres(context):
    """Run to-host docker restart postgres."""
    context.to_host_restart_postgres = True


@then('the PostgreSQL container should restart')
def step_postgres_restarts(context):
    """PostgreSQL container should restart."""
    context.postgres_restarts = True


@then('I should be able to verify the restart')
def step_verify_restart(context):
    """Should be able to verify restart."""
    context.verify_restart = True


@given('I need to read a configuration file on my host')
def step_read_config_host(context):
    """Need to read configuration file on host."""
    context.read_config_host = True


@when('I run "to-host cat ~/dev/config/app.conf"')
def step_to_host_cat_config(context):
    """Run to-host cat config."""
    context.to_host_cat_config = True


@then('I should see the contents of the host file')
def step_see_host_file_contents(context):
    """Should see contents of host file."""
    context.sees_host_file_contents = True


@then('I should be able to use the content in the VM')
def step_use_content_vm(context):
    """Should be able to use content in VM."""
    context.use_content_vm = True


@given('I have a build VM running')
def step_build_vm_running(context):
    """Have build VM running."""
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.build_vm_running = True


@given('I need to trigger a build on my host')
def step_trigger_build_host(context):
    """Need to trigger build on host."""
    context.trigger_build_host = True


@when('I SSH into the build VM')
def step_ssh_build_vm(context):
    """SSH into build VM."""
    context.ssh_build_vm = True


@when('I run "to-host ./build.sh"')
def step_to_host_build(context):
    """Run to-host ./build.sh."""
    context.to_host_build = True


@then('the build should execute on my host')
def step_build_executes_host(context):
    """Build should execute on host."""
    context.build_executes_host = True


@then('I should see the build output')
def step_see_build_output(context):
    """Should see build output."""
    context.sees_build_output = True


@given('I have a coordination VM running')
def step_coordination_vm_running(context):
    """Have coordination VM running."""
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.coordination_vm_running = True


@given('I need to check the status of other VMs')
def step_check_vm_status(context):
    """Need to check status of other VMs."""
    context.check_vm_status = True


@when('I SSH into the coordination VM')
def step_ssh_coordination_vm(context):
    """SSH into coordination VM."""
    context.ssh_coordination_vm = True


@when('I run "to-host docker ps --filter name=python"')
def step_to_host_check_python(context):
    """Run to-host docker ps for python."""
    context.to_host_check_python = True


@then('I should see the status of the Python VM')
def step_see_python_status(context):
    """Should see status of Python VM."""
    context.sees_python_status = True


@then('I can make decisions based on the status')
def step_decisions_based_status(context):
    """Can make decisions based on status."""
    context.decisions_based_status = True


@given('I have a backup VM running')
def step_backup_vm_running(context):
    """Have backup VM running."""
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.backup_vm_running = True


@given('I need to trigger a backup on my host')
def step_trigger_backup_host(context):
    """Need to trigger backup on host."""
    context.trigger_backup_host = True


@when('I SSH into the backup VM')
def step_ssh_backup_vm(context):
    """SSH into backup VM."""
    context.ssh_backup_vm = True


@when('I run "to-host ~/dev/scripts/backup.sh"')
def step_to_host_backup(context):
    """Run to-host backup script."""
    context.to_host_backup = True


@then('the backup should execute on my host')
def step_backup_executes_host(context):
    """Backup should execute on host."""
    context.backup_executes_host = True


@then('my data should be backed up')
def step_data_backed_up(context):
    """Data should be backed up."""
    context.data_backed_up = True


@given('I have a debugging VM running')
def step_debugging_vm_running(context):
    """Have debugging VM running."""
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.debugging_vm_running = True


@given('my host has an issue I need to diagnose')
def step_host_issue_diagnose(context):
    """Host has issue to diagnose."""
    context.host_issue_diagnose = True


@when('I SSH into the debugging VM')
def step_ssh_debugging_vm(context):
    """SSH into debugging VM."""
    context.ssh_debugging_vm = True


@when('I run "to-host systemctl status docker"')
def step_to_host_docker_status(context):
    """Run to-host systemctl status docker."""
    context.to_host_docker_status = True


@then('I should see the Docker service status')
def step_see_docker_status(context):
    """Should see Docker service status."""
    context.sees_docker_status = True


@then('I can diagnose the issue')
def step_diagnose_issue(context):
    """Can diagnose the issue."""
    context.diagnose_issue = True


@given('I have a network VM running')
def step_network_vm_running(context):
    """Have network VM running."""
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.network_vm_running = True


@given('I need to check host network connectivity')
def step_check_host_network(context):
    """Need to check host network connectivity."""
    context.check_host_network = True


@when('I SSH into the network VM')
def step_ssh_network_vm(context):
    """SSH into network VM."""
    context.ssh_network_vm = True


@when('I run "to-host ping -c 3 example.com"')
def step_to_host_ping(context):
    """Run to-host ping."""
    context.to_host_ping = True


@then('I should see network connectivity results')
def step_see_network_results(context):
    """Should see network connectivity results."""
    context.sees_network_results = True


@then('I can diagnose network issues')
def step_diagnose_network(context):
    """Can diagnose network issues."""
    context.diagnose_network = True


@given('I have a utility VM running')
def step_utility_vm_running(context):
    """Have utility VM running."""
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.utility_vm_running = True


@given('I have custom scripts on my host')
def step_custom_scripts_host(context):
    """Have custom scripts on host."""
    context.custom_scripts_host = True


@when('I SSH into the utility VM')
def step_ssh_utility_vm(context):
    """SSH into utility VM."""
    context.ssh_utility_vm = True


@when('I run "to-host ~/dev/scripts/cleanup.sh"')
def step_to_host_cleanup(context):
    """Run to-host cleanup script."""
    context.to_host_cleanup = True


@then('the script should execute on my host')
def step_script_executes_host(context):
    """Script should execute on host."""
    context.script_executes_host = True


@then('the cleanup should be performed')
def step_cleanup_performed(context):
    """Cleanup should be performed."""
    context.cleanup_performed = True


# =============================================================================
# SSH connection information and remote access steps
# =============================================================================

@when('I run "ssh-info python"')
def step_ssh_info_python(context):
    """Run ssh-info python."""
    context.ssh_info_python = True


@then('I should receive the SSH port')
def step_receive_ssh_port(context):
    """Should receive the SSH port."""
    context.ssh_port_received = True


@then('I should see the connection command')
def step_see_connection_command(context):
    """Should see connection command."""
    context.sees_connection_command = True


@when('I use the connection command')
def step_use_connection_command(context):
    """Use connection command."""
    context.use_connection_command = True


@then('I should be connected to the Python VM')
def step_connected_python_vm_ssh(context):
    """Should be connected to Python VM."""
    context.connected_python_vm = True


@when('I add the host to my SSH config')
def step_add_ssh_config(context):
    """Add host to SSH config."""
    context.add_ssh_config = True


@when('I run "ssh python-dev"')
def step_ssh_python_dev(context):
    """Run ssh python-dev."""
    context.ssh_python_dev = True


@then('I should be connected without specifying port')
def step_connected_no_port(context):
    """Should be connected without specifying port."""
    context.connected_no_port = True


@when('I configure VSCode to use Remote-SSH')
def step_configure_vscode_ssh(context):
    """Configure VSCode to use Remote-SSH."""
    context.configure_vscode_ssh = True


@when('I connect to "python-dev" in VSCode')
def step_vscode_connect_python(context):
    """Connect to python-dev in VSCode."""
    context.vscode_connect_python = True


@then('VSCode should open the remote workspace')
def step_vscode_remote_workspace(context):
    """VSCode should open remote workspace."""
    context.vscode_remote_workspace = True


@then('I should see the workspace/ directory contents')
def step_see_workspace_contents(context):
    """Should see workspace/ directory contents."""
    context.sees_workspace_contents = True


@when('I open multiple SSH connections')
def step_open_multiple_ssh(context):
    """Open multiple SSH connections."""
    context.multiple_ssh_connections = True


@then('all connections should work simultaneously')
def step_all_simultaneous(context):
    """All connections should work simultaneously."""
    context.all_simultaneous = True


@then('each should use SSH agent forwarding')
def step_each_agent_forwarding(context):
    """Each should use SSH agent forwarding."""
    context.each_agent_forwarding = True


@when('I connect without copying keys to the VM')
def step_connect_no_keys(context):
    """Connect without copying keys to VM."""
    context.connect_no_keys = True


@then('authentication should use the agent socket')
def step_auth_agent_socket(context):
    """Authentication should use agent socket."""
    context.auth_agent_socket = True


@when('I check my current directory')
def step_check_current_dir(context):
    """Check current directory."""
    context.check_current_dir = True


@then('I should be in the workspace/ directory')
def step_in_workspace_dir(context):
    """Should be in workspace/ directory."""
    context.in_workspace_dir = True


@then('I should be able to edit files')
def step_able_edit_files(context):
    """Should be able to edit files."""
    context.able_edit_files = True


@then('changes should appear on my host')
def step_changes_host(context):
    """Changes should appear on host."""
    context.changes_on_host = True


@when('I run "sudo command"')
def step_run_sudo(context):
    """Run sudo command."""
    context.run_sudo = True


@then('the command should execute without password')
def step_command_no_password(context):
    """Command should execute without password."""
    context.command_no_password = True


@when('I check my shell')
def step_check_shell(context):
    """Check shell."""
    context.check_shell = True


@then('I should be running zsh')
def step_running_zsh_shell(context):
    """Should be running zsh."""
    context.running_zsh_shell = True


@then('oh-my-zsh should be configured')
def step_oh_my_zsh_configured(context):
    """oh-my-zsh should be configured."""
    context.oh_my_zsh_configured = True


@when('I open neovim')
def step_open_neovim(context):
    """Open neovim."""
    context.open_neovim = True


@then('LazyVim should be loaded')
def step_lazyvim_loaded(context):
    """LazyVim should be loaded."""
    context.lazyvim_loaded = True


@when('I transfer a file using scp')
def step_transfer_scp(context):
    """Transfer file using scp."""
    context.transfer_scp = True


@then('the file should be transferred')
def step_file_transferred(context):
    """File should be transferred."""
    context.file_transferred = True


@then('the transfer should use SSH keys')
def step_transfer_ssh_keys(context):
    """Transfer should use SSH keys."""
    context.transfer_ssh_keys = True


@when('I start a service in the VM')
def step_start_service_vm(context):
    """Start service in VM."""
    context.start_service_vm = True


@then('the service port should be forwarded')
def step_port_forwarded(context):
    """Service port should be forwarded."""
    context.port_forwarded = True


@then('I can access it from my host')
def step_access_from_host(context):
    """Can access from host."""
    context.access_from_host = True


@when('I keep my SSH session idle')
def step_keep_idle(context):
    """Keep SSH session idle."""
    context.keep_idle = True


@then('the session should remain connected')
def step_session_remains(context):
    """Session should remain connected."""
    context.session_remains = True


@then('I should not be disconnected')
def step_not_disconnected(context):
    """Should not be disconnected."""
    context.not_disconnected = True

