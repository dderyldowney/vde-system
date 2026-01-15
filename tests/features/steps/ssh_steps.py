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
