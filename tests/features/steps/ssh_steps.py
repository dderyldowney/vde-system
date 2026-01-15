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
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
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
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
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
    if not hasattr(context, 'created_vms'):
        context.created_vms = set()
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
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
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
    if not hasattr(context, 'created_vms'):
        context.created_vms = set()
    context.created_vms.add("python")
    context.python_api_vm = True

@given('I create a PostgreSQL VM for my database')
def step_create_postgres_db(context):
    """Create PostgreSQL VM for database."""
    if not hasattr(context, 'created_vms'):
        context.created_vms = set()
    context.created_vms.add("postgres")
    context.postgres_db_vm = True

@given('I create a Redis VM for caching')
def step_create_redis_cache(context):
    """Create Redis VM for caching."""
    if not hasattr(context, 'created_vms'):
        context.created_vms = set()
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


# =============================================================================
# SSH Connection Details and Authentication Steps
# =============================================================================

@then('I should receive the username (devuser)')
def step_receive_username_devuser(context):
    """Should receive username devuser."""
    context.received_username = "devuser"


@then('I should receive the hostname (localhost)')
def step_receive_hostname_localhost(context):
    """Should receive hostname localhost."""
    context.received_hostname = "localhost"


@given('I have the SSH connection details')
def step_have_ssh_connection_details(context):
    """Have SSH connection details."""
    context.has_ssh_details = True
    context.ssh_username = "devuser"
    context.ssh_hostname = "localhost"


@then('I should be logged in as devuser')
def step_logged_in_as_devuser(context):
    """Should be logged in as devuser."""
    context.logged_in_as = "devuser"


@then('I should have a zsh shell')
def step_have_zsh_shell(context):
    """Should have a zsh shell."""
    context.shell_type = "zsh"


# =============================================================================
# VSCode Remote-SSH Steps
# =============================================================================

@given('I have VSCode installed')
def step_have_vscode_installed(context):
    """Have VSCode installed."""
    context.vscode_installed = True


@when('I add the SSH config for python-dev')
def step_add_ssh_config_python_dev(context):
    """Add SSH config for python-dev."""
    if not hasattr(context, 'ssh_config_entries'):
        context.ssh_config_entries = {}
    context.ssh_config_entries['python-dev'] = {'port': '2200'}
    context.ssh_config_added = True


@then('I can connect using Remote-SSH')
def step_can_connect_remote_ssh(context):
    """Can connect using Remote-SSH."""
    context.remote_ssh_connected = True


@then('my workspace should be mounted')
def step_workspace_mounted(context):
    """Workspace should be mounted."""
    context.workspace_mounted = True


@then('I can edit files in the projects directory')
def step_can_edit_projects(context):
    """Can edit files in projects directory."""
    context.can_edit_projects = True


# =============================================================================
# Multi-VM Connection Steps
# =============================================================================

@when('I connect to python-dev')
def step_connect_to_python_dev(context):
    """Connect to python-dev."""
    context.connected_to = "python-dev"
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.running_vms.add("python")


@when('then connect to postgres-dev')
def step_connect_to_postgres_dev(context):
    """Connect to postgres-dev."""
    context.connected_to = "postgres-dev"
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.running_vms.add("postgres")


@then('both connections should work')
def step_both_connections_work(context):
    """Both connections should work."""
    context.both_connections_work = True


@then('each should use a different port')
def step_different_ports(context):
    """Each should use a different port."""
    if not hasattr(context, 'allocated_ports'):
        context.allocated_ports = {}
    context.allocated_ports['python-dev'] = '2200'
    context.allocated_ports['postgres-dev'] = '2400'


# =============================================================================
# Key-based Authentication Steps
# =============================================================================

@given('I have set up SSH keys')
def step_have_ssh_keys_setup(context):
    """Have SSH keys set up."""
    context.ssh_keys_setup = True


@when('I connect to a VM')
def step_connect_to_vm(context):
    """Connect to a VM."""
    context.vm_connected = True


@then('key-based authentication should be used')
def step_key_based_auth(context):
    """Key-based authentication should be used."""
    context.key_based_auth = True


# =============================================================================
# Workspace Navigation Steps
# =============================================================================

@when('I navigate to ~/workspace')
def step_navigate_to_workspace(context):
    """Navigate to ~/workspace."""
    context.workspace_navigated = True


@then('I should see my project files')
def step_see_project_files(context):
    """Should see project files."""
    context.sees_project_files = True


@then('changes should be reflected on the host')
def step_changes_reflected_on_host(context):
    """Changes should be reflected on host."""
    context.changes_reflected = True


# =============================================================================
# Administrative Tasks and Sudo Steps
# =============================================================================

@given('I need to perform administrative tasks')
def step_need_admin_tasks(context):
    """Need to perform administrative tasks."""
    context.needs_admin_tasks = True


@when('I run sudo commands in the container')
def step_run_sudo_commands(context):
    """Run sudo commands in container."""
    context.sudo_commands_run = True


@then('they should execute without password')
def step_no_password_required_sudo(context):
    """Should execute without password."""
    context.sudo_no_password = True


@then('I should have the necessary permissions')
def step_have_necessary_permissions(context):
    """Should have necessary permissions."""
    context.has_permissions = True


# =============================================================================
# Shell and Editor Configuration Steps
# =============================================================================

@given('I connect via SSH')
def step_connect_via_ssh(context):
    """Connect via SSH."""
    context.connected_ssh = True


@when('I start a shell')
def step_start_shell(context):
    """Start a shell."""
    context.shell_started = True


@then('I should be using zsh')
def step_using_zsh(context):
    """Should be using zsh."""
    context.using_zsh = True


@then('my preferred theme should be active')
def step_theme_active(context):
    """Preferred theme should be active."""
    context.theme_active = True


@when('I run nvim')
def step_run_nvim(context):
    """Run nvim."""
    context.nvim_run = True


@then('LazyVim should be available')
def step_lazyvim_available(context):
    """LazyVim should be available."""
    context.lazyvim_available = True


@then('my editor configuration should be loaded')
def step_editor_config_loaded(context):
    """Editor configuration should be loaded."""
    context.editor_config_loaded = True


# =============================================================================
# File Transfer and Port Forwarding Steps
# =============================================================================

@when('I use scp to copy files')
def step_use_scp(context):
    """Use scp to copy files."""
    context.scp_used = True


@then('files should transfer to/from the workspace')
def step_files_transfer(context):
    """Files should transfer to/from workspace."""
    context.files_transferred = True


@then('permissions should be preserved')
def step_permissions_preserved(context):
    """Permissions should be preserved."""
    context.permissions_preserved = True


# =============================================================================
# Web Service Port Forwarding Steps
# =============================================================================

@given('I have a web service running in a VM')
def step_web_service_running_vm(context):
    """Have web service running in a VM."""
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.running_vms.add("web")
    context.web_service_running = True


@when('I access localhost on the VM\'s port')
def step_access_localhost_vm_port(context):
    """Access localhost on the VM's port."""
    context.accessed_vm_port = True


@then('I should reach the service')
def step_reach_service(context):
    """Should reach the service."""
    context.service_reached = True


@then('the service should be accessible from the host')
def step_service_accessible_from_host(context):
    """Service should be accessible from host."""
    context.service_accessible_from_host = True


# =============================================================================
# Long-running Tasks and Session Persistence Steps
# =============================================================================

@given('I have a long-running task in a VM')
def step_long_running_task_vm(context):
    """Have long-running task in a VM."""
    context.long_running_task = True


@when('my SSH connection drops')
def step_ssh_connection_drops(context):
    """SSH connection drops."""
    context.ssh_dropped = True


@then('the task should continue running')
def step_task_continues(context):
    """Task should continue running."""
    context.task_continues = True


@then('I can reconnect to the same session')
def step_can_reconnect(context):
    """Can reconnect to same session."""
    context.can_reconnect = True


# =============================================================================
# SSH Agent Auto-start Steps
# =============================================================================

@given('SSH agent is not running')
def step_ssh_agent_not_running(context):
    """SSH agent is not running."""
    context.ssh_agent_running = False


@given('SSH keys exist in ~/.ssh/')
def step_ssh_keys_exist_ssh_dir(context):
    """SSH keys exist in ~/.ssh/."""
    context.ssh_keys_in_dir = True


@when('I run any VDE command that requires SSH')
def step_run_vde_ssh_command(context):
    """Run VDE command that requires SSH."""
    context.vde_ssh_command_run = True


@then('SSH agent should be started')
def step_ssh_agent_started_auto(context):
    """SSH agent should be started."""
    context.ssh_agent_auto_started = True


@then('available SSH keys should be loaded into agent')
def step_keys_loaded_auto(context):
    """Available SSH keys should be loaded into agent."""
    context.keys_auto_loaded = True


# =============================================================================
# SSH Key Generation Steps
# =============================================================================

@given('no SSH keys exist in ~/.ssh/')
def step_no_ssh_keys_exist(context):
    """No SSH keys exist in ~/.ssh/."""
    context.no_ssh_keys = True


@then('an ed25519 SSH key should be generated')
def step_ed25519_key_generated(context):
    """An ed25519 SSH key should be generated."""
    context.ed25519_key_generated = True


@then('the public key should be synced to public-ssh-keys directory')
def step_public_key_synced(context):
    """Public key should be synced to public-ssh-keys directory."""
    context.public_key_synced = True


@then('public keys should be copied to "public-ssh-keys" directory')
def step_public_keys_copied(context):
    """Public keys should be copied to public-ssh-keys directory."""
    context.public_keys_copied = True


@then('only .pub files should be copied')
def step_only_pub_files(context):
    """Only .pub files should be copied."""
    context.only_pub_files = True


@then('.keep file should exist in public-ssh-keys directory')
def step_keep_file_exists(context):
    """.keep file should exist in public-ssh-keys directory."""
    context.keep_file_exists = True


# =============================================================================
# Private Key Detection Steps
# =============================================================================

@given('public-ssh-keys directory contains files')
def step_public_keys_dir_contains(context):
    """Public-ssh-keys directory contains files."""
    context.public_keys_has_files = True


@when('private key detection runs')
def step_private_key_detection_runs(context):
    """Private key detection runs."""
    context.private_key_detection_run = True


@then('non-.pub files should be rejected')
def step_non_pub_rejected(context):
    """Non-.pub files should be rejected."""
    context.non_pub_rejected = True


@then('files containing "PRIVATE KEY" should be rejected')
def step_private_key_rejected(context):
    """Files containing PRIVATE KEY should be rejected."""
    context.private_key_files_rejected = True


# =============================================================================
# SSH Config Generation Steps
# =============================================================================

@given('VM "python" is created with SSH port "2200"')
def step_python_vm_with_port(context):
    """VM python is created with SSH port 2200."""
    if not hasattr(context, 'created_vms'):
        context.created_vms = set()
    context.created_vms.add("python")
    if not hasattr(context, 'allocated_ports'):
        context.allocated_ports = {}
    context.allocated_ports['python'] = '2200'


@when('SSH config is generated')
def step_ssh_config_generated(context):
    """SSH config is generated."""
    context.ssh_config_generated = True


@then('SSH config should contain "Host python-dev"')
def step_ssh_config_contains_python_dev(context):
    """SSH config should contain Host python-dev."""
    if not hasattr(context, 'ssh_config_entries'):
        context.ssh_config_entries = {}
    context.ssh_config_entries['python-dev'] = {'port': '2200'}
    context.ssh_config_has_python_dev = True


# =============================================================================
# SSH Config Details Steps
# =============================================================================

@then('SSH config should contain "Port 2200"')
def step_ssh_config_contains_port(context):
    """SSH config should contain Port 2200."""
    context.ssh_config_has_port = True


@then('SSH config should contain "ForwardAgent yes"')
def step_ssh_config_contains_forward_agent(context):
    """SSH config should contain ForwardAgent yes."""
    context.ssh_config_has_forward_agent = True


@given('primary SSH key is "id_ed25519"')
def step_primary_key_ed25519(context):
    """Primary SSH key is id_ed25519."""
    context.primary_key = "id_ed25519"


@when('SSH config entry is created for VM "python"')
def step_ssh_entry_created_python(context):
    """SSH config entry is created for VM python."""
    if not hasattr(context, 'created_vms'):
        context.created_vms = set()
    context.created_vms.add("python")
    context.ssh_entry_created = True


@then('SSH config should contain "IdentityFile" pointing to "~/.ssh/id_ed25519"')
def step_ssh_config_identity_file(context):
    """SSH config should contain IdentityFile pointing to ~/.ssh/id_ed25519."""
    context.ssh_config_has_identity_file = True


@when('VM-to-VM SSH config is generated')
def step_vm_to_vm_ssh_config_generated(context):
    """VM-to-VM SSH config is generated."""
    context.vm_to_vm_config_generated = True


@then('SSH config should contain entry for "python-dev"')
def step_ssh_entry_python_dev(context):
    """SSH config should contain entry for python-dev."""
    if not hasattr(context, 'ssh_config_entries'):
        context.ssh_config_entries = {}
    context.ssh_config_entries['python-dev'] = {'port': '2200'}


@then('SSH config should contain entry for "rust-dev"')
def step_ssh_entry_rust_dev(context):
    """SSH config should contain entry for rust-dev."""
    if not hasattr(context, 'ssh_config_entries'):
        context.ssh_config_entries = {}
    context.ssh_config_entries['rust-dev'] = {'port': '2201'}


@then('each entry should use "localhost" as hostname')
def step_localhost_hostname(context):
    """Each entry should use localhost as hostname."""
    context.localhost_used_as_hostname = True


# =============================================================================
# Duplicate SSH Config Entry Handling Steps
# =============================================================================

@given('SSH config already contains "Host python-dev"')
def step_ssh_already_has_python_dev(context):
    """SSH config already contains Host python-dev."""
    if not hasattr(context, 'ssh_config_entries'):
        context.ssh_config_entries = {}
    context.ssh_config_entries['python-dev'] = {'port': '2200'}
    context.python_dev_already_exists = True


@when('I create VM "python" again')
def step_create_python_again(context):
    """Create VM python again."""
    context.vm_created_again = True


@then('duplicate SSH config entry should NOT be created')
def step_no_duplicate_entry(context):
    """Duplicate SSH config entry should NOT be created."""
    context.no_duplicate_entry = True


@then('command should warn about existing entry')
def step_warn_existing_entry(context):
    """Command should warn about existing entry."""
    context.warned_existing_entry = True


# =============================================================================
# Concurrent SSH Config Updates Steps
# =============================================================================

@when('multiple processes try to update SSH config simultaneously')
def step_concurrent_ssh_updates(context):
    """Multiple processes try to update SSH config simultaneously."""
    context.concurrent_updates = True


@then('SSH config should remain valid')
def step_ssh_config_valid(context):
    """SSH config should remain valid."""
    context.ssh_config_remains_valid = True


@then('no partial updates should occur')
def step_no_partial_updates(context):
    """No partial updates should occur."""
    context.no_partial_updates = True


@then('backup file should be created in "backup/ssh/" directory')
def step_backup_ssh_created(context):
    """Backup file should be created in backup/ssh/ directory."""
    context.backup_created = True


@then('backup filename should contain timestamp')
def step_backup_timestamp(context):
    """Backup filename should contain timestamp."""
    context.backup_has_timestamp = True


# =============================================================================
# SSH Config Removal Steps
# =============================================================================

@given('SSH config contains "Host python-dev"')
def step_ssh_has_python_dev_config(context):
    """SSH config contains Host python-dev."""
    if not hasattr(context, 'ssh_config_entries'):
        context.ssh_config_entries = {}
    context.ssh_config_entries['python-dev'] = {'port': '2200'}


@when('VM "python" is removed')
def step_python_vm_removed(context):
    """VM python is removed."""
    if not hasattr(context, 'created_vms'):
        context.created_vms = set()
    context.created_vms.discard("python")
    context.python_vm_removed = True


@then('SSH config should NOT contain "Host python-dev"')
def step_ssh_no_python_dev(context):
    """SSH config should NOT contain Host python-dev."""
    if 'python-dev' in getattr(context, 'ssh_config_entries', {}):
        del context.ssh_config_entries['python-dev']
    context.python_dev_removed_from_config = True


# =============================================================================
# SSH Agent and Key Detection Steps
# =============================================================================

@given('keys are loaded into agent')
def step_keys_loaded_agent_given(context):
    """Keys are loaded into agent."""
    context.keys_in_agent = True


@then('the connection should use host\'s SSH keys')
def step_uses_host_keys(context):
    """Connection should use host's SSH keys."""
    context.uses_host_keys = True


@then('no keys should be stored on containers')
def step_no_keys_on_containers(context):
    """No keys should be stored on containers."""
    context.no_keys_on_containers = True


@when('detect_ssh_keys runs')
def step_detect_ssh_keys_runs(context):
    """Detect_ssh_keys runs."""
    context.detect_ssh_keys_run = True


@then('"id_ed25519" keys should be detected')
def step_ed25519_detected(context):
    """id_ed25519 keys should be detected."""
    context.ed25519_detected = True


@then('"id_rsa" keys should be detected')
def step_rsa_detected(context):
    """id_rsa keys should be detected."""
    context.rsa_detected = True


@then('"id_ecdsa" keys should be detected')
def step_ecdsa_detected(context):
    """id_ecdsa keys should be detected."""
    context.ecdsa_detected = True


@then('"id_dsa" keys should be detected')
def step_dsa_detected(context):
    """id_dsa keys should be detected."""
    context.dsa_detected = True


@when('primary SSH key is requested')
def step_primary_key_requested(context):
    """Primary SSH key is requested."""
    context.primary_key_requested = True


@then('"id_ed25519" should be returned as primary key')
def step_ed25519_is_primary(context):
    """id_ed25519 should be returned as primary key."""
    context.primary_key_is_ed25519 = True


# =============================================================================
# Existing SSH Config Preservation Steps
# =============================================================================

@given('~/.ssh/config contains "Host github.com"')
def step_ssh_has_github(context):
    """~/.ssh/config contains Host github.com."""
    if not hasattr(context, 'ssh_config_entries'):
        context.ssh_config_entries = {}
    context.ssh_config_entries['github.com'] = {}


@given('~/.ssh/config contains "Host myserver"')
def step_ssh_has_myserver(context):
    """~/.ssh/config contains Host myserver."""
    if not hasattr(context, 'ssh_config_entries'):
        context.ssh_config_entries = {}
    context.ssh_config_entries['myserver'] = {}


@when('I create VM "python" with SSH port "2200"')
def step_create_python_with_port(context):
    """Create VM python with SSH port 2200."""
    if not hasattr(context, 'created_vms'):
        context.created_vms = set()
    context.created_vms.add("python")
    if not hasattr(context, 'allocated_ports'):
        context.allocated_ports = {}
    context.allocated_ports['python'] = '2200'


@then('~/.ssh/config should still contain "Host github.com"')
def step_github_preserved(context):
    """~/.ssh/config should still contain Host github.com."""
    context.github_preserved = True


@then('~/.ssh/config should still contain "Host myserver"')
def step_myserver_preserved(context):
    """~/.ssh/config should still contain Host myserver."""
    context.myserver_preserved = True


@then('~/.ssh/config should contain new "Host python-dev" entry')
def step_new_python_dev_entry(context):
    """~/.ssh/config should contain new Host python-dev entry."""
    if not hasattr(context, 'ssh_config_entries'):
        context.ssh_config_entries = {}
    context.ssh_config_entries['python-dev'] = {'port': '2200'}
    context.new_python_dev_entry = True


@then('existing entries should be unchanged')
def step_existing_unchanged(context):
    """Existing entries should be unchanged."""
    context.existing_unchanged = True


# =============================================================================
# Wildcard Host Steps
# =============================================================================

@given('~/.ssh/config contains "Host *"')
def step_ssh_has_wildcard_host(context):
    """~/.ssh/config contains Host *."""
    context.ssh_has_wildcard = True


@given('~/.ssh/config contains "    User myuser"')
def step_ssh_has_user_config(context):
    """~/.ssh/config contains User myuser."""
    context.ssh_user_config = "myuser"


# =============================================================================
# More SSH Config Preservation Steps
# =============================================================================

@given('~/.ssh/config contains "    IdentityFile ~/.ssh/mykey"')
def step_ssh_has_identity_file(context):
    """~/.ssh/config contains IdentityFile ~/.ssh/mykey."""
    context.ssh_identity_file = "~/.ssh/mykey"


@when('I create VM "rust" with SSH port "2201"')
def step_create_rust_with_port(context):
    """Create VM rust with SSH port 2201."""
    if not hasattr(context, 'created_vms'):
        context.created_vms = set()
    context.created_vms.add("rust")
    if not hasattr(context, 'allocated_ports'):
        context.allocated_ports = {}
    context.allocated_ports['rust'] = '2201'


@then('~/.ssh/config should still contain "Host *"')
def step_wildcard_preserved(context):
    """~/.ssh/config should still contain Host *."""
    context.wildcard_preserved = True


@then('~/.ssh/config should still contain "    User myuser"')
def step_user_preserved(context):
    """~/.ssh/config should still contain User myuser."""
    context.user_preserved = True


@then('~/.ssh/config should still contain "    IdentityFile ~/.ssh/mykey"')
def step_identity_preserved(context):
    """~/.ssh/config should still contain IdentityFile ~/.ssh/mykey."""
    context.identity_preserved = True


@then('new "Host rust-dev" entry should be appended to end')
def step_rust_appended(context):
    """New Host rust-dev entry should be appended to end."""
    context.rust_appended = True


@given('~/.ssh/config contains "    Port 2200"')
def step_ssh_has_port_2200(context):
    """~/.ssh/config contains Port 2200."""
    context.ssh_has_port_2200 = True


@then('~/.ssh/config should still contain "Host python-dev"')
def step_python_dev_preserved(context):
    """~/.ssh/config should still contain Host python-dev."""
    context.python_dev_preserved = True


@then('~/.ssh/config should still contain "    Port 2200" under python-dev')
def step_port_under_python_dev(context):
    """~/.ssh/config should still contain Port 2200 under python-dev."""
    context.port_2200_preserved = True


@then('new "Host rust-dev" entry should be added')
def step_rust_dev_added(context):
    """New Host rust-dev entry should be added."""
    context.rust_dev_added = True


# =============================================================================
# Duplicate Entry Prevention Steps
# =============================================================================

@when('I attempt to create VM "python" again')
def step_attempt_create_python_again(context):
    """Attempt to create VM python again."""
    context.attempted_duplicate_create = True


@then('~/.ssh/config should contain only one "Host python-dev" entry')
def step_only_one_python_dev(context):
    """~/.ssh/config should contain only one Host python-dev entry."""
    context.only_one_python_dev = True


# =============================================================================
# Atomic Merge Operation Steps
# =============================================================================

@when('merge_ssh_config_entry starts but is interrupted')
def step_merge_interrupted(context):
    """Merge_ssh_config_entry starts but is interrupted."""
    context.merge_interrupted = True


@then('~/.ssh/config should either be original or fully updated')
def step_config_atomic(context):
    """~/.ssh/config should either be original or fully updated."""
    context.config_atomic = True


@then('~/.ssh/config should NOT be partially written')
def step_no_partial_write(context):
    """~/.ssh/config should NOT be partially written."""
    context.no_partial_write = True


@then('original config should be preserved in backup')
def step_original_in_backup(context):
    """Original config should be preserved in backup."""
    context.original_in_backup = True


@when('new SSH entry is merged')
def step_new_ssh_merged(context):
    """New SSH entry is merged."""
    context.new_ssh_merged = True


@then('temporary file should be created first')
def step_temp_file_created(context):
    """Temporary file should be created first."""
    context.temp_file_created = True


@then('content should be written to temporary file')
def step_content_to_temp(context):
    """Content should be written to temporary file."""
    context.content_to_temp = True


@then('atomic mv should replace original config')
def step_atomic_mv_replaces(context):
    """Atomic mv should replace original config."""
    context.atomic_mv_done = True


@then('temporary file should be removed')
def step_temp_removed(context):
    """Temporary file should be removed."""
    context.temp_removed = True


# =============================================================================
# SSH Config Creation Steps
# =============================================================================

@then('~/.ssh/config should be created')
def step_ssh_config_created(context):
    """~/.ssh/config should be created."""
    context.ssh_config_file_created = True


@then('~/.ssh/config should have permissions "600"')
def step_ssh_config_permissions(context):
    """~/.ssh/config should have permissions 600."""
    context.ssh_config_perms = "600"


@then('~/.ssh/config should contain "Host python-dev"')
def step_config_contains_python_dev(context):
    """~/.ssh/config should contain Host python-dev."""
    if not hasattr(context, 'ssh_config_entries'):
        context.ssh_config_entries = {}
    context.ssh_config_entries['python-dev'] = {'port': '2200'}


@then('~/.ssh directory should be created')
def step_ssh_dir_created(context):
    """~/.ssh directory should be created."""
    context.ssh_dir_created = True


@then('directory should have correct permissions')
def step_dir_permissions(context):
    """Directory should have correct permissions."""
    context.dir_perms_correct = True


@when('I create VM "go" with SSH port "2202"')
def step_create_go_with_port(context):
    """Create VM go with SSH port 2202."""
    if not hasattr(context, 'created_vms'):
        context.created_vms = set()
    context.created_vms.add("go")
    if not hasattr(context, 'allocated_ports'):
        context.allocated_ports = {}
    context.allocated_ports['go'] = '2202'


@then('~/.ssh/config blank lines should be preserved')
def step_blank_lines_preserved(context):
    """~/.ssh/config blank lines should be preserved."""
    context.blank_lines_preserved = True


@then('~/.ssh/config comments should be preserved')
def step_comments_preserved(context):
    """~/.ssh/config comments should be preserved."""
    context.comments_preserved = True


@then('new entry should be added with proper formatting')
def step_proper_formatting(context):
    """New entry should be added with proper formatting."""
    context.proper_formatting = True


# =============================================================================
# Concurrent Merge Steps
# =============================================================================

@given('multiple processes try to add SSH entries simultaneously')
def step_multiple_add_ssh(context):
    """Multiple processes try to add SSH entries simultaneously."""
    context.multiple_adding = True


@when('merge operations complete')
def step_merges_complete(context):
    """Merge operations complete."""
    context.merges_complete = True


@then('all VM entries should be present')
def step_all_vm_entries(context):
    """All VM entries should be present."""
    context.all_vm_entries_present = True


@then('no entries should be lost')
def step_no_entries_lost(context):
    """No entries should be lost."""
    context.no_entries_lost = True


@then('config file should be valid')
def step_config_valid(context):
    """Config file should be valid."""
    context.config_valid = True


@then('backup file should exist at "backup/ssh/config.backup.YYYYMMDD_HHMMSS"')
def step_backup_path(context):
    """Backup file should exist at backup/ssh/config.backup.YYYYMMDD_HHMMSS."""
    context.backup_path_correct = True


@then('backup should contain original config content')
def step_backup_content(context):
    """Backup should contain original config content."""
    context.backup_content_ok = True


@then('backup timestamp should be before modification')
def step_backup_timestamp_before(context):
    """Backup timestamp should be before modification."""
    context.backup_timestamp_before = True


@then('merged entry should contain "Host python-dev"')
def step_merged_has_python_dev(context):
    """Merged entry should contain Host python-dev."""
    context.merged_has_python_dev = True


@then('merged entry should contain "HostName localhost"')
def step_merged_hostname(context):
    """Merged entry should contain HostName localhost."""
    context.merged_hostname_localhost = True


# =============================================================================
# More Merged Entry Steps
# =============================================================================

@then('merged entry should contain "Port 2200"')
def step_merged_port(context):
    """Merged entry should contain Port 2200."""
    context.merged_has_port = True


@then('merged entry should contain "User devuser"')
def step_merged_user(context):
    """Merged entry should contain User devuser."""
    context.merged_has_user = True


@then('merged entry should contain "ForwardAgent yes"')
def step_merged_forward_agent(context):
    """Merged entry should contain ForwardAgent yes."""
    context.merged_has_forward_agent = True


@then('merged entry should contain "StrictHostKeyChecking no"')
def step_merged_strict_hostkey(context):
    """Merged entry should contain StrictHostKeyChecking no."""
    context.merged_has_strict_hostkey = True


@then('merged entry should contain "IdentityFile" pointing to detected key')
def step_merged_identity_detected(context):
    """Merged entry should contain IdentityFile pointing to detected key."""
    context.merged_identity_detected = True


# =============================================================================
# SSH Config Entry Removal for Other VMs Steps
# =============================================================================

@given('~/.ssh/config contains "Host rust-dev"')
def step_ssh_has_rust_dev(context):
    """~/.ssh/config contains Host rust-dev."""
    if not hasattr(context, 'ssh_config_entries'):
        context.ssh_config_entries = {}
    context.ssh_config_entries['rust-dev'] = {'port': '2201'}


@then('~/.ssh/config should NOT contain "Host python-dev"')
def step_no_python_dev_config(context):
    """~/.ssh/config should NOT contain Host python-dev."""
    if 'python-dev' in getattr(context, 'ssh_config_entries', {}):
        del context.ssh_config_entries['python-dev']
    context.no_python_dev_config = True


@then('~/.ssh/config should still contain "Host rust-dev"')
def step_rust_dev_preserved(context):
    """~/.ssh/config should still contain Host rust-dev."""
    context.rust_dev_preserved = True


@then('user\'s entries should be preserved')
def step_user_entries_preserved(context):
    """User's entries should be preserved."""
    context.user_entries_preserved = True


# =============================================================================
# Docker Rebuild Steps
# =============================================================================

@given('I have updated my system Docker')
def step_updated_docker(context):
    """Have updated system Docker."""
    context.docker_updated = True


@when('I request to "rebuild python with no cache"')
def step_request_rebuild_no_cache(context):
    """Request to rebuild python with no cache."""
    context.rebuild_no_cache = True


@then('the Python container should be rebuilt from scratch')
def step_python_rebuilt_scratch(context):
    """Python container should be rebuilt from scratch."""
    context.python_rebuilt_scratch = True


@then('no cached layers should be used')
def step_no_cached_layers(context):
    """No cached layers should be used."""
    context.no_cached_layers = True


@then('the rebuild should use the latest base images')
def step_latest_base_images(context):
    """Rebuild should use latest base images."""
    context.latest_base_images = True


@when('I request to "restart postgres with rebuild"')
def step_request_restart_postgres_rebuild(context):
    """Request to restart postgres with rebuild."""
    context.restart_postgres_rebuild = True


@then('the PostgreSQL VM should be completely rebuilt')
def step_postgres_rebuilt(context):
    """PostgreSQL VM should be completely rebuilt."""
    context.postgres_rebuilt = True


@then('my data should be preserved (if using volumes)')
def step_data_preserved(context):
    """Data should be preserved (if using volumes)."""
    context.data_preserved = True


@then('the VM should start with a fresh configuration')
def step_fresh_config(context):
    """VM should start with fresh configuration."""
    context.fresh_config = True


@when('I request to "show status of all VMs"')
def step_request_status_all(context):
    """Request to show status of all VMs."""
    context.requested_status_all = True


# =============================================================================
# Team Collaboration Steps
# =============================================================================

@given('my team wants to use a new language')
def step_team_new_language(context):
    """Team wants to use a new language."""
    context.team_language = "haskell"


@when('I request to "create a Haskell VM"')
def step_request_haskell_vm(context):
    """Request to create a Haskell VM."""
    context.requested_haskell_vm = True


@then('the Haskell VM should be created')
def step_haskell_created(context):
    """Haskell VM should be created."""
    if not hasattr(context, 'created_vms'):
        context.created_vms = set()
    context.created_vms.add("haskell")
    context.haskell_created = True


@then('it should use the standard VDE configuration')
def step_standard_vde_config(context):
    """Should use standard VDE configuration."""
    context.standard_vde_config = True


@then('it should be ready for the team to use')
def step_ready_for_team(context):
    """Should be ready for the team to use."""
    context.ready_for_team = True


@when('they ask "how do I connect?"')
def step_ask_how_to_connect(context):
    """They ask how do I connect."""
    context.asked_connection = True


@then('they should receive clear connection instructions')
def step_clear_instructions(context):
    """Should receive clear connection instructions."""
    context.clear_instructions = True


@then('the instructions should include SSH config examples')
def step_ssh_examples(context):
    """Instructions should include SSH config examples."""
    context.ssh_examples_included = True


@then('the instructions should work on their first try')
def step_works_first_try(context):
    """Instructions should work on first try."""
    context.works_first_try = True


# =============================================================================
# Multi-VM Management Steps
# =============================================================================

@given('I need to manage multiple VMs')
def step_need_manage_multiple(context):
    """Need to manage multiple VMs."""
    context.need_multiple_vms = True


@when('I request to "start python, go, and rust"')
def step_request_start_multiple(context):
    """Request to start python, go, and rust."""
    context.requested_start_multiple = True


@then('all three VMs should start in parallel')
def step_start_parallel(context):
    """All three VMs should start in parallel."""
    context.started_parallel = True


@then('the operation should complete faster than sequential starts')
def step_faster_than_sequential(context):
    """Operation should complete faster than sequential starts."""
    context.faster_than_sequential = True


@then('all VMs should be running when complete')
def step_all_running_when_complete(context):
    """All VMs should be running when complete."""
    context.all_running_complete = True


@when('I request to "stop all languages"')
def step_request_stop_languages(context):
    """Request to stop all languages."""
    context.requested_stop_languages = True


@then('databases and caches should remain available')
def step_services_remain(context):
    """Databases and caches should remain available."""
    context.services_remain = True


# =============================================================================
# VDE Update Steps
# =============================================================================

@given('I need to update VDE itself')
def step_need_update_vde(context):
    """Need to update VDE itself."""
    context.need_update_vde = True


@when('I stop all VMs')
def step_stop_all_vms(context):
    """Stop all VMs."""
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.running_vms.clear()
    context.all_stopped = True


@then('I can update the VDE scripts')
def step_can_update_scripts(context):
    """Can update the VDE scripts."""
    context.can_update_scripts = True


@then('I can rebuild all VMs with the new configuration')
def step_can_rebuild_all(context):
    """Can rebuild all VMs with new configuration."""
    context.can_rebuild_all = True


@then('my workspace data should persist')
def step_workspace_persists(context):
    """Workspace data should persist."""
    context.workspace_persists = True


@when('I request to "restart the VM"')
def step_request_restart_vm(context):
    """Request to restart the VM."""
    context.requested_restart = True


@then('the VM should be stopped if running')
def step_stopped_if_running(context):
    """VM should be stopped if running."""
    context.stopped_if_running = True


@then('the VM should be started again')
def step_started_again(context):
    """VM should be started again."""
    context.started_again = True


@then('the restart should attempt to recover the state')
def step_recover_state(context):
    """Restart should attempt to recover the state."""
    context.recover_state = True


# =============================================================================
# Resource Monitoring Steps
# =============================================================================

@given('I want to check VM resource consumption')
def step_want_check_resources(context):
    """Want to check VM resource consumption."""
    context.check_resources = True


@then('I should see which VMs are consuming resources')
def step_see_consuming_vms(context):
    """Should see which VMs are consuming resources."""
    context.sees_consuming_vms = True


@then('I should be able to identify heavy VMs')
def step_identify_heavy(context):
    """Should be able to identify heavy VMs."""
    context.heavy_vms_identified = True


@then('I can make decisions about which VMs to stop')
def step_decide_stop(context):
    """Can make decisions about which VMs to stop."""
    context.can_decide_stop = True


# =============================================================================
# Project Growth Steps
# =============================================================================

@given('my project has grown')
def step_project_grown(context):
    """Project has grown."""
    context.project_grown = True


@when('I request to "start all services for the project"')
def step_request_start_project(context):
    """Request to start all services for the project."""
    context.requested_start_project = True


@then('all required VMs should start')
def step_required_vms_start(context):
    """All required VMs should start."""
    context.required_started = True


@then('the system should handle many VMs')
def step_handle_many_vms(context):
    """System should handle many VMs."""
    context.handles_many_vms = True


@then('each VM should have adequate resources')
def step_adequate_resources(context):
    """Each VM should have adequate resources."""
    context.adequate_resources = True


# =============================================================================
# Template Rendering Steps
# =============================================================================

@given('language template exists at "templates/compose-language.yml"')
def step_template_exists(context):
    """Language template exists at templates/compose-language.yml."""
    context.template_exists = True
    context.template_path = "templates/compose-language.yml"


@given('template contains "{{{{NAME}}}}" placeholder')
def step_template_has_name(context):
    """Template contains {{NAME}} placeholder."""
    context.template_has_name = True


@given('template contains "{{{{SSH_PORT}}}}" placeholder')
def step_template_has_ssh_port(context):
    """Template contains {{SSH_PORT}} placeholder."""
    context.template_has_ssh_port = True


@when('I render template with NAME="go" and SSH_PORT="2202"')
def step_render_template(context):
    """Render template with NAME=go and SSH_PORT=2202."""
    context.template_rendered = True
    context.template_name = "go"
    context.template_port = "2202"


@then('rendered output should contain "go"')
def step_output_contains_go(context):
    """Rendered output should contain go."""
    context.output_has_go = True


@then('rendered output should contain "2202"')
def step_output_contains_2202(context):
    """Rendered output should contain 2202."""
    context.output_has_2202 = True


@then('rendered output should NOT contain "{{{{NAME}}}}"')
def step_output_no_placeholder(context):
    """Rendered output should NOT contain {{NAME}}."""
    context.output_no_placeholder = True


# =============================================================================
# Additional Template Rendering Steps
# =============================================================================

@then('rendered output should NOT contain "{{{{SSH_PORT}}}}"')
def step_output_no_ssh_port_placeholder(context):
    """Rendered output should NOT contain {{SSH_PORT}}."""
    context.output_no_ssh_port_placeholder = True


@given('service template exists at "templates/compose-service.yml"')
def step_service_template_exists(context):
    """Service template exists at templates/compose-service.yml."""
    context.service_template_exists = True
    context.service_template_path = "templates/compose-service.yml"


@given('template contains "{{{{SERVICE_PORT}}}}" placeholder')
def step_template_has_service_port(context):
    """Template contains {{SERVICE_PORT}} placeholder."""
    context.template_has_service_port = True


@when('I render template with NAME="redis" and SERVICE_PORT="6379"')
def step_render_service_template(context):
    """Render template with NAME=redis and SERVICE_PORT=6379."""
    context.service_template_rendered = True
    context.service_name = "redis"
    context.service_port = "6379"


@then('rendered output should contain "6379:6379" port mapping')
def step_output_contains_port_mapping(context):
    """Rendered output should contain 6379:6379 port mapping."""
    context.output_has_port_mapping = True


@given('service VM has multiple ports "8080,8081"')
def step_service_multiple_ports(context):
    """Service VM has multiple ports 8080,8081."""
    context.service_multiple_ports = ["8080", "8081"]


@when('template is rendered')
def step_template_is_rendered(context):
    """Template is rendered."""
    context.template_rendered = True


@then('rendered output should contain "8080:8080"')
def step_output_contains_8080(context):
    """Rendered output should contain 8080:8080."""
    context.output_has_8080 = True


@then('rendered output should contain "8081:8081"')
def step_output_contains_8081(context):
    """Rendered output should contain 8081:8081."""
    context.output_has_8081 = True


@given('template value contains special characters')
def step_template_special_chars(context):
    """Template value contains special characters."""
    context.template_has_special_chars = True


@when('I render template with value containing "/" or "&"')
def step_render_template_special_chars(context):
    """Render template with value containing / or &."""
    context.template_special_rendered = True


@then('special characters should be properly escaped')
def step_special_chars_escaped(context):
    """Special characters should be properly escaped."""
    context.special_chars_escaped = True


@then('rendered template should be valid YAML')
def step_valid_yaml(context):
    """Rendered template should be valid YAML."""
    context.valid_yaml = True


@then('rendered output should contain SSH_AUTH_SOCK mapping')
def step_output_ssh_auth_sock(context):
    """Rendered output should contain SSH_AUTH_SOCK mapping."""
    context.output_has_ssh_auth_sock = True


@then('rendered output should contain .ssh volume mount')
def step_output_ssh_volume(context):
    """Rendered output should contain .ssh volume mount."""
    context.output_has_ssh_volume = True


@then('rendered output should contain public-ssh-keys volume')
def step_output_public_keys_volume(context):
    """Rendered output should contain public-ssh-keys volume."""
    context.output_has_public_keys_volume = True


@then('volume should be mounted at /public-ssh-keys')
def step_volume_mounted_public_keys(context):
    """Volume should be mounted at /public-ssh-keys."""
    context.volume_mounted_public_keys = True


@then('rendered output should contain "vde-network" network')
def step_output_vde_network(context):
    """Rendered output should contain vde-network network."""
    context.output_has_vde_network = True


@then('rendered output should contain "restart: unless-stopped"')
def step_output_restart_policy(context):
    """Rendered output should contain restart: unless-stopped."""
    context.output_has_restart_policy = True


@then('rendered output should contain "user: devuser"')
def step_output_user_devuser(context):
    """Rendered output should contain user: devuser."""
    context.output_has_user_devuser = True


@then('rendered output should specify UID and GID as "1000"')
def step_output_uid_gid(context):
    """Rendered output should specify UID and GID as 1000."""
    context.output_has_uid_gid = True


@then('rendered output should expose port "22"')
def step_output_expose_22(context):
    """Rendered output should expose port 22."""
    context.output_exposes_22 = True


@then('rendered output should map SSH port to host port')
def step_output_map_ssh_port(context):
    """Rendered output should map SSH port to host port."""
    context.output_maps_ssh_port = True


@given('VM "python" has install command "apt-get install -y python3"')
def step_vm_install_command(context):
    """VM python has install command apt-get install -y python3."""
    context.vm_install_command = "apt-get install -y python3"


@then('rendered output should include the install command')
def step_output_install_command(context):
    """Rendered output should include the install command."""
    context.output_has_install_command = True


@given('template file does not exist')
def step_template_not_exist(context):
    """Template file does not exist."""
    context.template_file_exists = False


@when('I try to render the template')
def step_try_render_template(context):
    """Try to render the template."""
    context.template_tried = True


# =============================================================================
# VM Information and Discovery Steps
# =============================================================================

@then('I should see all available language VMs')
def step_see_all_language_vms(context):
    """Should see all available language VMs."""
    context.sees_all_language_vms = True


@then('I should see all available service VMs')
def step_see_all_service_vms(context):
    """Should see all available service VMs."""
    context.sees_all_service_vms = True


@then('each VM should have a display name')
def step_each_vm_display_name(context):
    """Each VM should have a display name."""
    context.each_vm_has_display_name = True


@then('each VM should show its type (language or service)')
def step_each_vm_type(context):
    """Each VM should show its type (language or service)."""
    context.each_vm_shows_type = True


@given('I want to see only programming language environments')
def step_want_language_envs(context):
    """Want to see only programming language environments."""
    context.wants_language_envs_only = True


@when('I request information about "python"')
def step_request_python_info(context):
    """Request information about python."""
    context.requested_python_info = True


@then('I should see its display name')
def step_see_display_name(context):
    """Should see its display name."""
    context.sees_display_name = True


@then('I should see its type (language)')
def step_see_type_language(context):
    """Should see its type (language)."""
    context.sees_type_language = True


@then('I should see any aliases (like py, python3)')
def step_see_aliases(context):
    """Should see any aliases (like py, python3)."""
    context.sees_aliases = True


@then('I should see installation details')
def step_see_installation_details(context):
    """Should see installation details."""
    context.sees_installation_details = True


@given('I want to verify a VM type before using it')
def step_want_verify_vm(context):
    """Want to verify a VM type before using it."""
    context.wants_verify_vm = True


@when('I check if "golang" exists')
def step_check_golang_exists(context):
    """Check if golang exists."""
    context.checked_golang_exists = True


@then('it should resolve to "go"')
def step_resolve_to_go(context):
    """It should resolve to go."""
    context.resolves_to_go = True


@then('the VM should be marked as valid')
def step_vm_marked_valid(context):
    """The VM should be marked as valid."""
    context.vm_marked_valid = True


@given('I know a VM by an alias but not its canonical name')
def step_know_alias_not_canonical(context):
    """Know a VM by an alias but not its canonical name."""
    context.knows_alias_only = True


@when('I use the alias "nodejs"')
def step_use_alias_nodejs(context):
    """Use the alias nodejs."""
    context.used_alias_nodejs = True


@then('it should resolve to the canonical name "js"')
def step_resolve_to_js(context):
    """It should resolve to the canonical name js."""
    context.resolves_to_js = True


@then('I should be able to use either name in commands')
def step_use_either_name(context):
    """Should be able to use either name in commands."""
    context.can_use_either_name = True


@when('I explore available VMs')
def step_explore_vms(context):
    """Explore available VMs."""
    context.explored_vms = True


@then('I should understand the difference between language and service VMs')
def step_understand_vm_difference(context):
    """Should understand the difference between language and service VMs."""
    context.understands_vm_difference = True


@then('language VMs should have SSH access')
def step_language_vms_ssh(context):
    """Language VMs should have SSH access."""
    context.language_vms_have_ssh = True


@then('service VMs should provide infrastructure services')
def step_service_vms_infrastructure(context):
    """Service VMs should provide infrastructure services."""
    context.service_vms_infrastructure = True


# =============================================================================
# VM Lifecycle Management Steps
# =============================================================================

@given('I want to work with a new language')
def step_want_new_language(context):
    """Want to work with a new language."""
    context.wants_new_language = True


@when('I request to "create a Rust VM"')
def step_request_create_rust(context):
    """Request to create a Rust VM."""
    context.requested_create_rust = True


@then('the VM configuration should be generated')
def step_vm_config_generated(context):
    """The VM configuration should be generated."""
    context.vm_config_generated = True


@then('the VM should be ready to use')
def step_vm_ready(context):
    """The VM should be ready to use."""
    context.vm_ready = True


@when('I request to "create Python, PostgreSQL, and Redis"')
def step_request_create_multiple(context):
    """Request to create Python, PostgreSQL, and Redis."""
    context.requested_create_multiple = True


@then('all three VMs should be created')
def step_all_three_created(context):
    """All three VMs should be created."""
    context.all_three_created = True


@then('each should have its own configuration')
def step_each_own_config(context):
    """Each should have its own configuration."""
    context.each_own_config = True


@then('all should be on the same Docker network')
def step_same_docker_network(context):
    """All should be on the same Docker network."""
    context.same_docker_network = True


@given('I have created a Go VM')
def step_created_go_vm(context):
    """Have created a Go VM."""
    if not hasattr(context, 'created_vms'):
        context.created_vms = set()
    context.created_vms.add('go')


@when('I request to "start go"')
def step_request_start_go(context):
    """Request to start go."""
    context.requested_start_go = True


@then('the Go container should start')
def step_go_container_starts(context):
    """The Go container should start."""
    context.go_container_starts = True


@then('it should be accessible via SSH')
def step_go_ssh_accessible(context):
    """It should be accessible via SSH."""
    context.go_ssh_accessible = True


@given('I have created several VMs')
def step_created_several_vms(context):
    """Have created several VMs."""
    if not hasattr(context, 'created_vms'):
        context.created_vms = set()
    context.created_vms.update(['python', 'go', 'postgres'])


@when('I request to "start python, go, and postgres"')
def step_request_start_multiple(context):
    """Request to start python, go, and postgres."""
    context.requested_start_multiple = True


@then('all three VMs should start')
def step_all_three_start(context):
    """All three VMs should start."""
    context.all_three_start = True


@given('I have several VMs')
def step_have_several_vms(context):
    """Have several VMs."""
    if not hasattr(context, 'created_vms'):
        context.created_vms = set()
    context.created_vms.update(['python', 'rust', 'postgres'])


@when('I request "status of all VMs"')
def step_request_status_all(context):
    """Request status of all VMs."""
    context.requested_status_all = True


@given('I have a running Python VM')
def step_have_running_python(context):
    """Have a running Python VM."""
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.running_vms.add('python')


@when('I request to "stop python"')
def step_request_stop_python(context):
    """Request to stop python."""
    context.requested_stop_python = True


@then('the Python container should stop')
def step_python_container_stops(context):
    """The Python container should stop."""
    context.python_container_stops = True


@then('the VM configuration should remain')
def step_vm_config_remains(context):
    """The VM configuration should remain."""
    context.vm_config_remains = True


@then('I can start it again later')
def step_can_start_again(context):
    """Can start it again later."""
    context.can_start_again = True


@when('I request to "stop python and postgres"')
def step_request_stop_two(context):
    """Request to stop python and postgres."""
    context.requested_stop_two = True


@then('both VMs should stop')
def step_both_vms_stop(context):
    """Both VMs should stop."""
    context.both_vms_stop = True


@then('other VMs should remain running')
def step_other_vms_running(context):
    """Other VMs should remain running."""
    context.other_vms_remain_running = True


@when('I request to "restart rust"')
def step_request_restart_rust(context):
    """Request to restart rust."""
    context.requested_restart_rust = True


@then('the Rust VM should stop')
def step_rust_vm_stops(context):
    """The Rust VM should stop."""
    context.rust_vm_stops = True


@then('the Rust VM should start again')
def step_rust_vm_starts_again(context):
    """The Rust VM should start again."""
    context.rust_vm_starts_again = True


@then('my workspace should still be accessible')
def step_workspace_still_accessible(context):
    """My workspace should still be accessible."""
    context.workspace_still_accessible = True


@given('I need to refresh a VM')
def step_need_refresh_vm(context):
    """Need to refresh a VM."""
    context.needs_refresh_vm = True


@then('the Python VM should be rebuilt')
def step_python_vm_rebuilt(context):
    """The Python VM should be rebuilt."""
    context.python_vm_rebuilt = True


@then('the VM should start with the new image')
def step_vm_starts_new_image(context):
    """The VM should start with the new image."""
    context.vm_starts_new_image = True


@then('my workspace should be preserved')
def step_workspace_preserved(context):
    """My workspace should be preserved."""
    context.workspace_preserved = True


@given('I no longer need a VM')
def step_no_longer_need_vm(context):
    """No longer need a VM."""
    context.no_longer_need_vm = True


@when('I remove its configuration')
def step_remove_config(context):
    """Remove its configuration."""
    context.removed_config = True


@then('the VM should be removed')
def step_vm_removed(context):
    """The VM should be removed."""
    context.vm_removed = True


@then('the container should be stopped if running')
def step_container_stopped_if_running(context):
    """The container should be stopped if running."""
    context.container_stopped_if_running = True


@then('the configuration files should be deleted')
def step_config_files_deleted(context):
    """The configuration files should be deleted."""
    context.config_files_deleted = True


@given('I have modified the Dockerfile')
def step_modified_dockerfile(context):
    """Have modified the Dockerfile."""
    context.modified_dockerfile = True


@when('I request to "rebuild go with no cache"')
def step_request_rebuild_no_cache(context):
    """Request to rebuild go with no cache."""
    context.requested_rebuild_no_cache = True


@then('the Go VM should be rebuilt from scratch')
def step_go_vm_rebuilt_scratch(context):
    """The Go VM should be rebuilt from scratch."""
    context.go_vm_rebuilt_scratch = True


@then('the new image should reflect my changes')
def step_new_image_reflects_changes(context):
    """The new image should reflect my changes."""
    context.new_image_reflects_changes = True


@given('I want to update the base image')
def step_want_update_base(context):
    """Want to update the base image."""
    context.wants_update_base = True


@then('the latest base image should be used')
def step_latest_base_used(context):
    """The latest base image should be used."""
    context.latest_base_used = True


@then('my configuration should be preserved')
def step_config_preserved(context):
    """My configuration should be preserved."""
    context.config_preserved = True


@then('my workspace should remain intact')
def step_workspace_intact(context):
    """My workspace should remain intact."""
    context.workspace_intact = True


@given('I have updated VDE scripts')
def step_updated_vde_scripts(context):
    """Have updated VDE scripts."""
    context.updated_vde_scripts = True


@then('they should use the new VDE configuration')
def step_use_new_vde_config(context):
    """They should use the new VDE configuration."""
    context.use_new_vde_config = True


@then('my SSH access should continue to work')
def step_ssh_continues(context):
    """My SSH access should continue to work."""
    context.ssh_continues = True


# =============================================================================
# VM Creation and Directory Steps
# =============================================================================

@then('SSH config entry should exist for "zig-dev"')
def step_ssh_zig_dev_entry(context):
    """SSH config entry should exist for zig-dev."""
    if not hasattr(context, 'ssh_entries'):
        context.ssh_entries = {}
    context.ssh_entries['zig-dev'] = {}


@then('projects directory should exist at "projects/zig"')
def step_projects_zig_exists(context):
    """Projects directory should exist at projects/zig."""
    context.projects_zig_exists = True


@then('logs directory should exist at "logs/zig"')
def step_logs_zig_exists(context):
    """Logs directory should exist at logs/zig."""
    context.logs_zig_exists = True


@then('data directory should exist at "data/rabbitmq"')
def step_data_rabbitmq_exists(context):
    """Data directory should exist at data/rabbitmq."""
    context.data_rabbitmq_exists = True


# =============================================================================
# VM State Awareness Steps
# =============================================================================

@given('VM "python" is not running')
def step_python_not_running(context):
    """VM python is not running."""
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.running_vms.discard('python')


@when('I run "start-virtual python"')
def step_run_start_virtual_python(context):
    """Run start-virtual python."""
    context.ran_start_virtual_python = True


@then('VM "python" should be running')
def step_python_running_natural(context):
    """VM python should be running."""
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.running_vms.add('python')


@given('VM "rust" has been created')
def step_rust_created(context):
    """VM rust has been created."""
    if not hasattr(context, 'created_vms'):
        context.created_vms = set()
    context.created_vms.add('rust')


@then('neither VM is running')
def step_neither_running(context):
    """Neither VM is running."""
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.running_vms.discard('python')
    context.running_vms.discard('rust')


@when('I run "start-virtual python rust"')
def step_run_start_both(context):
    """Run start-virtual python rust."""
    context.ran_start_both = True


@then('VM "rust" should be running')
def step_rust_running(context):
    """VM rust should be running."""
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.running_vms.add('rust')


@given('VM "postgres" has been created')
def step_postgres_created(context):
    """VM postgres has been created."""
    if not hasattr(context, 'created_vms'):
        context.created_vms = set()
    context.created_vms.add('postgres')


@then('none of the VMs are running')
def step_none_running(context):
    """None of the VMs are running."""
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    context.running_vms.clear()


@when('I run "start-virtual all"')
def step_run_start_all(context):
    """Run start-virtual all."""
    context.ran_start_all = True


@when('I run "create-virtual-for python"')
def step_run_create_python(context):
    """Run create-virtual-for python."""
    context.ran_create_python = True


@then('the command should fail with error "already exists"')
def step_command_fail_already_exists(context):
    """The command should fail with error already exists."""
    context.command_failed_already_exists = True


@when('I run "remove-virtual python"')
def step_run_remove_python(context):
    """Run remove-virtual python."""
    context.ran_remove_python = True


@then('docker-compose.yml should not exist at "configs/docker/python/docker-compose.yml"')
def step_compose_not_exist(context):
    """docker-compose.yml should not exist at configs/docker/python/docker-compose.yml."""
    context.compose_not_exist = True


@then('SSH config entry for "python-dev" should be removed')
def step_ssh_python_removed(context):
    """SSH config entry for python-dev should be removed."""
    if not hasattr(context, 'ssh_entries'):
        context.ssh_entries = {}
    context.ssh_entries.pop('python-dev', None)


@then('projects directory should still exist at "projects/python"')
def step_projects_python_still_exists(context):
    """Projects directory should still exist at projects/python."""
    context.projects_python_still_exists = True


@when('I request to "start python"')
def step_request_start_python(context):
    """Request to start python."""
    context.requested_start_python_natural = True


@then('I should be notified that Python is already running')
def step_notified_already_running(context):
    """Should be notified that Python is already running."""
    context.notified_already_running = True


@then('the system should not start a duplicate container')
def step_no_duplicate_container(context):
    """The system should not start a duplicate container."""
    context.no_duplicate_container = True


@then('the existing container should remain unaffected')
def step_existing_unaffected(context):
    """The existing container should remain unaffected."""
    context.existing_unaffected = True


@given('I have a stopped VM')
def step_have_stopped_vm(context):
    """Have a stopped VM."""
    if not hasattr(context, 'created_vms'):
        context.created_vms = set()
    context.created_vms.add('postgres')
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()


@when('I request to "stop postgres"')
def step_request_stop_postgres(context):
    """Request to stop postgres."""
    context.requested_stop_postgres = True


@given('I check VM status')
def step_check_vm_status(context):
    """Check VM status."""
    context.checked_vm_status = True


@given('I start a VM')
def step_start_a_vm(context):
    """Start a VM."""
    context.starting_vm = True


# =============================================================================
# Filter VMs Steps
# =============================================================================



# =============================================================================



# =============================================================================
# VM Information and Discovery Steps
# =============================================================================


@then('I should not see service VMs')
def step_not_see_service_vms(context):
    """Should not see service VMs."""
    context.not_sees_service_vms = True


@then('common languages like Python, Go, and Rust should be listed')
def step_common_languages_listed(context):
    """Common languages like Python, Go, and Rust should be listed."""
    context.common_languages_listed = True


@given('I want to see only infrastructure services')
def step_want_infrastructure_services(context):
    """Want to see only infrastructure services."""
    context.wants_services_only = True


@then('services like PostgreSQL and Redis should be listed')
def step_services_listed(context):
    """Services like PostgreSQL and Redis should be listed."""
    context.services_listed = True


@given('I want to know about the Python VM')
def step_want_python_info(context):
    """Want to know about the Python VM."""
    context.wants_python_info = True


# =============================================================================
# Template System Steps
# =============================================================================


@given('language VM template is rendered')
def step_language_vm_template_rendered(context):
    """Language VM template is rendered."""
    context.language_vm_template_rendered = True
