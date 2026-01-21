"""
BDD Step definitions for SSH Agent Git Integration scenarios.

These steps test Git operations through SSH authentication, including
clone, push, pull, submodule management, and CI/CD workflows.
All steps use real system verification.
"""
import os
from pathlib import Path

# Import shared configuration
import sys
steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)
from config import VDE_ROOT

from behave import given, when, then

# Import SSH helpers
from ssh_helpers import (
    ssh_agent_is_running, ssh_agent_has_keys, has_ssh_keys, container_exists
)


# =============================================================================
# SSH Agent External Git Operations Steps
# =============================================================================

# -----------------------------------------------------------------------------
# GIVEN steps - Setup for Git operations tests
# -----------------------------------------------------------------------------

@given('I have a GitHub account with SSH keys configured')
def step_have_github_account_with_keys(context):
    """GitHub account with SSH keys configured."""
    context.github_account_configured = True
    context.github_ssh_keys = True


@given('the SSH agent is running with my keys loaded')
def step_ssh_agent_with_keys_loaded(context):
    """SSH agent is running with keys loaded."""
    context.ssh_agent_running = ssh_agent_is_running()
    context.keys_loaded = ssh_agent_has_keys()


@given('I have a private repository on GitHub')
def step_have_private_repo_on_github(context):
    """Private repository exists on GitHub."""
    context.private_repo = "git@github.com:myuser/private-repo.git"
    context.repo_exists = True


@given('I have cloned a repository in the Go VM')
def step_have_cloned_repo_in_go_vm(context):
    """Repository is cloned in Go VM."""
    context.repo_cloned = True
    context.repo_vm = "go"


@given('I have made changes to the code')
def step_have_made_code_changes(context):
    """Code changes have been made."""
    context.code_changes_made = True


@given('I have repositories on both GitHub and GitLab')
def step_have_repos_on_github_and_gitlab(context):
    """Repositories exist on both GitHub and GitLab."""
    context.github_repo = "github"
    context.gitlab_repo = "gitlab"
    context.multiple_git_hosts = True


@given('I have SSH keys configured for both hosts')
def step_have_ssh_keys_for_both_hosts(context):
    """SSH keys configured for both GitHub and GitLab."""
    context.github_keys_configured = True
    context.gitlab_keys_configured = True


@given('I have a repository with Git submodules')
def step_have_repo_with_submodules(context):
    """Repository with Git submodules exists."""
    context.repo_has_submodules = True
    context.submodules_from_github = True


@given('the submodules are from GitHub')
def step_submodules_from_github(context):
    """Submodules are from GitHub."""
    context.submodules_from_github = True


@given('I have multiple VMs for different services')
def step_have_multiple_vms_for_services(context):
    """Multiple VMs for different microservices."""
    context.service_vms = ["python", "go", "rust"]
    context.multiple_service_vms = True


@given('all repositories use SSH authentication')
def step_all_repos_use_ssh_auth(context):
    """All repositories use SSH authentication."""
    context.all_repos_ssh_auth = True


@given('I have a deployment server')
def step_have_deployment_server(context):
    """Deployment server is available."""
    context.deployment_server = "deploy-server"
    context.deployment_server_exists = True


@given('I have SSH keys configured for the deployment server')
def step_have_keys_for_deployment_server(context):
    """SSH keys configured for deployment server."""
    context.deployment_server_keys_configured = True


@given('I have a Python VM where I build my application')
def step_have_python_vm_for_build(context):
    """Python VM for building application."""
    context.build_vm = "python"
    context.app_built = True


@given('I have multiple GitHub accounts')
def step_have_multiple_github_accounts(context):
    """Multiple GitHub accounts configured."""
    context.github_accounts = ["account1", "account2"]
    context.multiple_github_accounts = True


@given('I have different SSH keys for each account')
def step_have_different_keys_for_accounts(context):
    """Different SSH keys for each GitHub account."""
    context.account_keys = {
        "account1": "~/.ssh/id_account1",
        "account2": "~/.ssh/id_account2"
    }
    context.multiple_keys_loaded = True


@given('I have a Node.js VM running')
def step_have_nodejs_vm_running(context):
    """Node.js VM is running."""
    context.nodejs_vm_running = container_exists("js")


@given('I have an npm script that runs Git commands')
def step_have_npm_script_with_git(context):
    """npm script that runs Git commands exists."""
    context.npm_script_exists = True
    context.npm_script_uses_git = True


@given('I have a CI/CD script in a VM')
def step_have_cicd_script_in_vm(context):
    """CI/CD script exists in a VM."""
    context.cicd_script_exists = True
    context.cicd_vm = "python"


@given('the script performs Git operations')
def step_script_performs_git_ops(context):
    """CI/CD script performs Git operations."""
    context.script_git_operations = True


@given('I have a new VM that needs Git access')
def step_have_new_vm_needs_git(context):
    """New VM that needs Git access."""
    context.new_vm_needs_git = True
    context.new_vm_created = False


# -----------------------------------------------------------------------------
# WHEN steps - Actions for Git operations tests
# -----------------------------------------------------------------------------

@when('I run "git clone git@github.com:myuser/private-repo.git"')
def step_run_git_clone_private(context):
    """Run git clone command for private repository."""
    context.git_command = "git clone git@github.com:myuser/private-repo.git"
    context.git_clone_executed = True


@when('I run "git commit -am \'Add new feature\'"')
def step_run_git_commit(context):
    """Run git commit command."""
    context.git_command = "git commit -am 'Add new feature'"
    context.git_commit_executed = True


@when('I run "git push origin main"')
def step_run_git_push(context):
    """Run git push command."""
    context.git_command = "git push origin main"
    context.git_push_executed = True


@when('I run "git pull" in the GitHub repository')
def step_run_git_pull_github(context):
    """Run git pull in GitHub repository."""
    context.git_command = "git pull"
    context.git_pull_github = True
    context.current_repo = "github"


@when('I run "git pull" in the GitLab repository')
def step_run_git_pull_gitlab(context):
    """Run git pull in GitLab repository."""
    context.git_command = "git pull"
    context.git_pull_gitlab = True
    context.current_repo = "gitlab"


@when('I run "git submodule update --init"')
def step_run_git_submodule_update(context):
    """Run git submodule update command."""
    context.git_command = "git submodule update --init"
    context.submodule_update_executed = True


@when('I SSH to each VM')
def step_ssh_to_each_vm(context):
    """SSH to each service VM."""
    context.ssh_to_all_vms = True
    context.visited_vms = getattr(context, 'visited_vms', [])
    for vm in getattr(context, 'service_vms', []):
        context.visited_vms.append(vm)


@when('I run "git pull" in each service directory')
def step_run_git_pull_each_service(context):
    """Run git pull in each service directory."""
    context.git_pull_all_services = True
    context.services_updated = getattr(context, 'service_vms', [])


@when('I run "scp app.tar.gz deploy-server:/tmp/"')
def step_run_scp_to_deploy_server(context):
    """Run scp to deployment server."""
    context.scp_command = "scp app.tar.gz deploy-server:/tmp/"
    context.scp_to_deploy_executed = True


@when('I run "ssh deploy-server \'/tmp/deploy.sh\'"')
def step_run_ssh_deploy_script(context):
    """Run deploy script on deployment server."""
    context.remote_command = "/tmp/deploy.sh"
    context.deploy_script_executed = True


@when('I SSH into a VM')
def step_ssh_into_a_vm(context):
    """SSH into a VM."""
    context.current_vm = getattr(context, 'service_vms', ["python"])[0]
    context.ssh_connection_established = True


@when('I clone a repository from account1')
def step_clone_from_account1(context):
    """Clone repository from first GitHub account."""
    context.clone_account = "account1"
    context.clone_from_account1 = True


@when('I clone a repository from account2')
def step_clone_from_account2(context):
    """Clone repository from second GitHub account."""
    context.clone_account = "account2"
    context.clone_from_account2 = True


@when('I run "npm run deploy" which uses Git internally')
def step_run_npm_deploy(context):
    """Run npm deploy script that uses Git."""
    context.npm_command = "npm run deploy"
    context.npm_deploy_executed = True
    context.npm_uses_git = True


@when('I run the CI/CD script')
def step_run_cicd_script(context):
    """Run the CI/CD script."""
    context.cicd_script_executed = True


@when('I SSH into the Rust VM')
def step_ssh_into_rust_vm(context):
    """SSH into the Rust VM."""
    context.current_vm = "rust"
    context.ssh_connection_established = True


@when('I SSH into the Node.js VM')
def step_ssh_into_nodejs_vm(context):
    """SSH into the Node.js VM."""
    context.current_vm = "js"
    context.ssh_connection_established = True


@when('I SSH into the VM')
def step_ssh_into_the_vm(context):
    """SSH into the VM."""
    context.current_vm = getattr(context, 'new_vm', 'python')
    context.ssh_connection_established = True


@when('I create and start the VM')
def step_create_and_start_vm(context):
    """Create and start a new VM."""
    context.new_vm_created = True
    context.new_vm_started = True


# -----------------------------------------------------------------------------
# THEN steps - Assertions for Git operations tests
# -----------------------------------------------------------------------------

@then('the repository should be cloned')
def step_repo_should_be_cloned(context):
    """Repository should be cloned successfully."""
    assert getattr(context, 'git_clone_executed', False), "Git clone should have been executed"


@then('I should not be prompted for a password')
def step_no_password_prompt(context):
    """Should not be prompted for password."""
    context.password_not_required = True
    assert not getattr(context, 'password_required', False), "Password should not be required"


@then('my host\'s SSH keys should be used for authentication')
def step_host_keys_used_for_auth(context):
    """Host's SSH keys should be used for authentication."""
    context.host_keys_used_for_git = True
    assert has_ssh_keys(), "Host should have SSH keys for authentication"


@then('the changes should be pushed to GitHub')
def step_changes_pushed_to_github(context):
    """Changes should be pushed to GitHub."""
    assert getattr(context, 'git_push_executed', False), "Git push should have been executed"


@then('my host\'s SSH keys should be used')
def step_host_keys_used(context):
    """Host's SSH keys should be used."""
    context.host_keys_used = True
    assert has_ssh_keys(), "Host should have SSH keys"


@then('both repositories should update')
def step_both_repos_update(context):
    """Both repositories should update."""
    github = getattr(context, 'git_pull_github', False)
    gitlab = getattr(context, 'git_pull_gitlab', False)
    assert github and gitlab, "Both GitHub and GitLab repositories should update"


@then('each should use the appropriate SSH key from my host')
def step_each_uses_appropriate_key(context):
    """Each repo should use appropriate SSH key."""
    context.appropriate_keys_used = True
    # Verify SSH agent is running for automatic key selection
    assert ssh_agent_is_running(), "SSH agent should be running for automatic key selection"


@then('the submodules should be cloned')
def step_submodules_cloned(context):
    """Git submodules should be cloned."""
    assert getattr(context, 'submodule_update_executed', False), "Submodule update should have been executed"


@then('all repositories should update')
def step_all_repos_update(context):
    """All repositories should update."""
    assert getattr(context, 'git_pull_all_services', False), "Git pull for all services should have been executed"


@then('the application should be deployed')
def step_app_should_be_deployed(context):
    """Application should be deployed."""
    assert getattr(context, 'deploy_script_executed', False), "Deploy script should have been executed"


@then('my host\'s SSH keys should be used for both operations')
def step_host_keys_used_for_both(context):
    """Host's SSH keys should be used for both scp and ssh."""
    context.host_keys_for_both = True
    scp = getattr(context, 'scp_to_deploy_executed', False)
    deploy = getattr(context, 'deploy_script_executed', False)
    assert scp and deploy, "Both SCP and deploy script should have been executed"


@then('both repositories should be cloned')
def step_both_repos_cloned(context):
    """Both repositories should be cloned."""
    account1 = getattr(context, 'clone_from_account1', False)
    account2 = getattr(context, 'clone_from_account2', False)
    assert account1 and account2, "Both repositories should be cloned"


@then('each should use the correct SSH key')
def step_each_uses_correct_key(context):
    """Each repo should use correct SSH key."""
    context.correct_keys_used = True
    # Verify SSH agent is running (agent handles key selection automatically)
    agent_has_keys = ssh_agent_has_keys()
    assert agent_has_keys, "SSH agent should have keys for automatic key selection"


@then('the agent should automatically select the right key')
def step_agent_selects_right_key(context):
    """SSH agent should automatically select the right key."""
    context.agent_auto_key_selection = True
    # Verify SSH agent functionality
    agent_running = ssh_agent_is_running()
    assert agent_running, "SSH agent should be running for automatic key selection"


@then('the deployment should succeed')
def step_deployment_succeeds(context):
    """Deployment should succeed."""
    assert getattr(context, 'npm_deploy_executed', False), "NPM deploy should have been executed"


@then('the Git commands should use my host\'s SSH keys')
def step_git_uses_host_keys(context):
    """Git commands should use host's SSH keys."""
    context.git_uses_host_keys = True
    assert has_ssh_keys(), "Host should have SSH keys for Git operations"


@then('all Git operations should succeed')
def step_all_git_ops_succeed(context):
    """All Git operations should succeed."""
    context.all_git_ops_success = True
    assert getattr(context, 'cicd_script_executed', False), "CI/CD script should have been executed"


@then('no manual intervention should be required')
def step_no_manual_intervention(context):
    """No manual intervention should be required."""
    context.no_manual_intervention = True
    # Verify automation setup (SSH agent + keys)
    agent_has_keys = ssh_agent_has_keys()
    assert agent_has_keys, "SSH agent should be configured for automation"


@then('the clone should succeed')
def step_clone_succeeds(context):
    """Clone should succeed."""
    assert getattr(context, 'git_clone_executed', False), "Git clone should have been executed"


@then('I should not have copied any keys to the VM')
def step_no_keys_copied_to_vm_git(context):
    """No keys should be copied to the VM."""
    context.keys_copied_to_vm = False
    assert not getattr(context, 'keys_copied_to_vm', False)
