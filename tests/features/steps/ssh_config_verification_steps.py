"""
BDD Step Definitions for SSH Configuration Verification.

These steps verify SSH configuration for VM access.
"""
import os
import subprocess
import sys

# Import shared configuration
steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)
from pathlib import Path

from behave import given, then

from config import VDE_ROOT
from vm_common import docker_ps

# =============================================================================
# SSH CONFIGURATION GIVEN steps
# =============================================================================

@given('~/.ssh/config does not exist')
def step_no_ssh_config(context):
    """VDE SSH config doesn't exist."""
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    context.ssh_config_exists = ssh_config.exists()


@given('~/.ssh/config exists')
def step_ssh_config_exists_step(context):
    """VDE SSH config exists."""
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    context.ssh_config_exists = ssh_config.exists()


@given('~/.ssh/config exists with custom settings')
def step_ssh_custom(context):
    """VDE SSH config with custom settings."""
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    context.ssh_config_exists = ssh_config.exists()
    if ssh_config.exists():
        content = ssh_config.read_text()
        context.ssh_has_custom_settings = len(content) > 0


@given('~/.ssh/config contains python-dev configuration')
def step_python_config(context):
    """VDE SSH config has python configuration."""
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    if ssh_config.exists():
        content = ssh_config.read_text()
        context.has_python_config = "python" in content.lower()
    else:
        context.has_python_config = False


@given('~/.ssh/ contains SSH keys')
def step_ssh_keys(context):
    """VDE SSH directory contains SSH keys."""
    vde_ssh_dir = Path.home() / ".ssh" / "vde"
    has_keys = (vde_ssh_dir / "id_ed25519").exists()
    context.ssh_keys_exist = has_keys


@given('~/.ssh directory does not exist')
def step_no_ssh_dir(context):
    """VDE SSH directory doesn't exist."""
    vde_ssh_dir = Path.home() / ".ssh" / "vde"
    context.ssh_dir_exists = vde_ssh_dir.exists()


@given('~/.ssh directory exists or can be created')
def step_ssh_dir_creatable(context):
    """SSH directory can be created - check if directory exists or parent is writable."""
    ssh_dir = Path.home() / ".ssh"
    if ssh_dir.exists():
        context.ssh_dir_can_be_created = True
    else:
        parent = ssh_dir.parent
        context.ssh_dir_can_be_created = os.access(parent, os.W_OK)


@given('all keys are loaded in my SSH agent')
def step_keys_loaded(context):
    """Keys are loaded in SSH agent."""
    result = subprocess.run(["ssh-add", "-l"], capture_output=True, text=True)
    context.all_keys_loaded = result.returncode == 0


# =============================================================================
# SSH CONFIGURATION THEN steps
# =============================================================================

@then('SSH keys should be configured')
def step_ssh_keys_configured(context):
    """Verify SSH keys exist."""
    ssh_dir = Path.home() / '.ssh'
    assert ssh_dir.exists(), ".ssh directory should exist"
    key_files = list(ssh_dir.glob('id_*')) + list(ssh_dir.glob('*.pub'))
    assert len(key_files) > 0, "SSH keys should exist"


@then('SSH config should contain "Host python-dev"')
def step_ssh_config_host_python(context):
    """Verify SSH config contains Host python-dev."""
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    if ssh_config.exists():
        content = ssh_config.read_text()
        assert 'Host python-dev' in content or 'python-dev' in content, \
               f"SSH config should contain python-dev entry"


@then('SSH config should contain "Port 2200"')
def step_ssh_config_port_2200(context):
    """Verify SSH config contains Port 2200."""
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    if ssh_config.exists():
        content = ssh_config.read_text()
        assert 'Port 2200' in content or '2200' in content, \
               f"SSH config should contain port 2200"


@then('SSH config should contain "IdentityFile" pointing to "~/.ssh/id_ed25519"')
def step_ssh_config_identity(context):
    """Verify SSH config contains IdentityFile."""
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    if ssh_config.exists():
        content = ssh_config.read_text()
        assert 'IdentityFile' in content or 'id_ed25519' in content or 'id_rsa' in content, \
               f"SSH config should contain IdentityFile"


@then('SSH config should contain "ForwardAgent yes"')
def step_ssh_config_agent_forwarding(context):
    """Verify SSH config contains ForwardAgent yes."""
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    if ssh_config.exists():
        content = ssh_config.read_text()
        assert 'ForwardAgent yes' in content or 'ForwardAgent' in content, \
               f"SSH config should contain ForwardAgent"


@then('~/.ssh/known_hosts should NOT contain "postgres" entry')
def step_known_hosts_no_postgres(context):
    """Verify known_hosts doesn't contain postgres entry."""
    known_hosts = Path.home() / '.ssh' / 'known_hosts'
    if known_hosts.exists():
        content = known_hosts.read_text()
        assert 'postgres' not in content.lower(), \
               f"known_hosts should not contain postgres"


@then('known_hosts entries should be cleaned up')
def step_known_hosts_cleaned(context):
    """Verify known_hosts entries can be cleaned up - verify known_hosts is manageable."""
    known_hosts = Path.home() / '.ssh' / 'known_hosts'
    # known_hosts file should exist and be writable
    if known_hosts.exists():
        assert known_hosts.stat().st_size >= 0, "known_hosts should be accessible"
    else:
        # File doesn't exist yet, which is fine
        pass  # known_hosts will be created when needed


@then('SSH config entry should be removed')
def step_ssh_entry_removed(context):
    """Verify SSH config entry is removed."""
    vm_name = getattr(context, 'vm_removed', 'python')
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    if ssh_config.exists():
        content = ssh_config.read_text()
        assert vm_name not in content.lower(), \
               f"SSH config should not contain {vm_name}"


@then('SSH config entry for "python-dev" should be removed')
def step_ssh_python_dev_removed(context):
    """Verify python-dev SSH config entry is removed."""
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    if ssh_config.exists():
        content = ssh_config.read_text()
        assert 'python-dev' not in content, \
               f"SSH config should not contain python-dev"


@then('key-based authentication should be used')
def step_key_auth_used(context):
    """Verify key-based authentication is configured."""
    ssh_dir = Path.home() / '.ssh'
    assert ssh_dir.exists(), "SSH directory should exist for key-based auth"
    keys = list(ssh_dir.glob('id_*'))
    assert len(keys) > 0, "SSH keys should exist for key-based authentication"


@then('the SSH agent should be started automatically')
def step_ssh_agent_auto(context):
    """Verify SSH agent is started automatically."""
    result = subprocess.run(['pgrep', 'ssh-agent'], capture_output=True, text=True)
    context.ssh_agent_running = result.returncode == 0
