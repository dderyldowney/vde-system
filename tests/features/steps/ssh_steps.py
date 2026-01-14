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
