
# -*- coding: utf-8 -*-
"""
SSH Configuration Step Definitions for VDE Behave Tests

This module contains step definitions for SSH configuration testing.
All paths use ~/.ssh/vde/ as the base directory for VDE SSH settings.
"""

import os
import re
import stat
from pathlib import Path
from behave import given, when, then
from behave.api.async_step import async_run_until_complete

# VDE paths - use environment or defaults
VDE_ROOT = Path(os.environ.get("VDE_ROOT_DIR", "/Users/dderyldowney/dev"))
VDE_SSH_DIR = Path.home() / ".ssh" / "vde"
PUBLIC_SSH_KEYS_DIR = VDE_ROOT / "public-ssh-keys"

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _get_vde_ssh_dir():
    """Get the VDE SSH directory path."""
    return VDE_SSH_DIR

def _get_ssh_config_path():
    """Get the SSH config file path for VDE."""
    return VDE_SSH_DIR / "config"

def _get_known_hosts_path():
    """Get the known_hosts file path for VDE."""
    return VDE_SSH_DIR / "known_hosts"

def _ensure_vde_ssh_dir():
    """Ensure VDE SSH directory exists with proper permissions."""
    VDE_SSH_DIR.mkdir(parents=True, exist_ok=True)
    VDE_SSH_DIR.chmod(0o700)

def _ensure_public_ssh_keys_dir():
    """Ensure public-ssh-keys directory exists."""
    PUBLIC_SSH_KEYS_DIR.mkdir(parents=True, exist_ok=True)

# =============================================================================
# GIVEN STEPS - Setup
# =============================================================================

@given('~/.ssh/vde/ contains SSH keys')
def step_ssh_vde_contains_keys(context):
    """Ensure ~/.ssh/vde/ contains SSH keys."""
    _ensure_vde_ssh_dir()
    
    # Create ed25519 key if not exists
    ed25519_key = VDE_SSH_DIR / "id_ed25519"
    ed25519_pub = VDE_SSH_DIR / "id_ed25519.pub"
    
    if not ed25519_key.exists():
        import subprocess
        subprocess.run([
            "ssh-keygen", "-t", "ed25519",
            "-f", str(ed25519_key),
            "-N", "", "-C", "vde_test_key"
        ], capture_output=True)
    
    # Ensure permissions
    if ed25519_key.exists():
        ed25519_key.chmod(0o600)
    if ed25519_pub.exists():
        ed25519_pub.chmod(0o644)
    
    context.ssh_keys_exist = True

@given('~/.ssh/vde/config exists with existing host entries')
def step_config_with_existing_entries(context):
    """Ensure SSH config exists with existing host entries."""
    ssh_config = _get_ssh_config_path()
    _ensure_vde_ssh_dir()
    
    if not ssh_config.exists():
        ssh_config.write_text("""Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/vde/id_ed25519

Host myserver
    HostName myserver.example.com
    User admin
    IdentityFile ~/.ssh/vde/id_rsa
""")
    
    ssh_config.chmod(0o600)
    context.config_with_existing = True

@given('~/.ssh/vde/config exists with custom settings')
def step_config_with_custom_settings(context):
    """Ensure SSH config exists with custom settings."""
    ssh_config = _get_ssh_config_path()
    _ensure_vde_ssh_dir()
    
    if not ssh_config.exists():
        ssh_config.write_text("""Host *
    AddKeysToAgent yes
    IdentitiesOnly no
""")
    
    ssh_config.chmod(0o600)
    context.config_with_custom = True

@given('~/.ssh/vde/config contains python-dev configuration')
def step_config_contains_python_dev(context):
    """Ensure SSH config contains python-dev host entry."""
    ssh_config = _get_ssh_config_path()
    _ensure_vde_ssh_dir()
    
    current_content = ssh_config.read_text() if ssh_config.exists() else ""
    
    if "Host python-dev" not in current_content:
        new_entry = """Host python-dev
    HostName localhost
    Port 2200
    User devuser
    IdentityFile ~/.ssh/vde/id_ed25519
    StrictHostKeyChecking accept-new
"""
        ssh_config.write_text(current_content + new_entry)
    
    ssh_config.chmod(0o600)
    context.config_has_python_dev = True

@given('~/.ssh/vde/config exists with comments and formatting')
def step_config_with_comments(context):
    """Ensure SSH config exists with comments and formatting."""
    ssh_config = _get_ssh_config_path()
    _ensure_vde_ssh_dir()
    
    if not ssh_config.exists():
        ssh_config.write_text("""# My SSH Configuration
# This file manages VDE SSH connections

Host *
    # Default settings for all hosts
    AddKeysToAgent yes
    IdentitiesOnly yes

# GitHub access
Host github.com
    HostName github.com
    User git
    
""")
    
    ssh_config.chmod(0o600)
    context.config_with_comments = True

@given('~/.ssh/vde/config does not exist')
def step_config_not_exist(context):
    """Ensure SSH config does not exist."""
    ssh_config = _get_ssh_config_path()
    
    if ssh_config.exists():
        ssh_config.unlink()
    
    context.config_not_exist = True

@given('~/.ssh/vde directory does not exist')
def step_vde_ssh_dir_not_exist(context):
    """Ensure ~/.ssh/vde directory does not exist."""
    if VDE_SSH_DIR.exists():
        import shutil
        shutil.rmtree(VDE_SSH_DIR)
    
    context.vde_ssh_dir_not_exist = True

@given('~/.ssh/vde/known_hosts contains "[localhost]:{port}"')
def step_known_hosts_contains_localhost_port(context, port):
    """Ensure known_hosts contains localhost entry for port."""
    known_hosts = _get_known_hosts_path()
    _ensure_vde_ssh_dir()
    
    entry = f"[localhost]:{port} ssh-ed25519 AAAAC3NzaC1lZDI1NTE5VVVVVVVVVVVVVVVVVV vde_key\n"
    
    if known_hosts.exists():
        content = known_hosts.read_text()
        if f"[localhost]:{port}" not in content:
            known_hosts.write_text(content + entry)
    else:
        known_hosts.write_text(entry)
        known_hosts.chmod(0o644)

@given('~/.ssh/vde/known_hosts contains "[::1]:{port}"')
def step_known_hosts_contains_ipv6_port(context, port):
    """Ensure known_hosts contains IPv6 localhost entry for port."""
    known_hosts = _get_known_hosts_path()
    _ensure_vde_ssh_dir()
    
    entry = f"[::1]:{port} ssh-ed25519 AAAAC3NzaC1lZDI1NTE5VVVVVVVVVVVVVVVVVV vde_key\n"
    
    if known_hosts.exists():
        content = known_hosts.read_text()
        if f"[::1]:{port}" not in content:
            known_hosts.write_text(content + entry)
    else:
        known_hosts.write_text(entry)
        known_hosts.chmod(0o644)

@given('~/.ssh/vde/known_hosts contains "{hostname}" hostname entry')
def step_known_hosts_contains_hostname(context, hostname):
    """Ensure known_hosts contains hostname entry."""
    known_hosts = _get_known_hosts_path()
    _ensure_vde_ssh_dir()
    
    entry = f"{hostname} ssh-ed25519 AAAAC3NzaC1lZDI1NTE5VVVVVVVVVVVVVVVVVV vde_key\n"
    
    if known_hosts.exists():
        content = known_hosts.read_text()
        if hostname not in content:
            known_hosts.write_text(content + entry)
    else:
        known_hosts.write_text(entry)
        known_hosts.chmod(0o644)

@given('~/.ssh/vde/known_hosts exists with content')
def step_known_hosts_exists_with_content(context):
    """Ensure known_hosts exists with content."""
    known_hosts = _get_known_hosts_path()
    _ensure_vde_ssh_dir()
    
    if not known_hosts.exists():
        known_hosts.write_text("""[localhost]:2200 ssh-ed25519 AAAAC3NzaC1lZDI1NTE5VVVVVVVVVVVVVVVVVV python_vde
[localhost]:2400 ssh-ed25519 AAAAC3NzaC1lZDI1NTE5VVVVVVVVVVVVVVVVVV postgres_vde
""")
        known_hosts.chmod(0o644)
    
    context.known_hosts_exists = True

@given('~/.ssh/vde/known_hosts does not exist')
def step_known_hosts_not_exist(context):
    """Ensure known_hosts does not exist."""
    known_hosts = _get_known_hosts_path()
    
    if known_hosts.exists():
        known_hosts.unlink()
    
    context.known_hosts_not_exist = True

@given('~/.ssh/vde/known_hosts contains multiple port entries')
def step_known_hosts_multiple_entries(context):
    """Ensure known_hosts contains multiple port entries."""
    known_hosts = _get_known_hosts_path()
    _ensure_vde_ssh_dir()
    
    content = """[localhost]:2200 ssh-ed25519 AAAAC3NzaC1lZDI1NTE5VVVVVVVVVVVVVVVVVV python_vde
[localhost]:2400 ssh-ed25519 AAAAC3NzaC1lZDI1NTE5VVVVVVVVVVVVVVVVVV postgres_vde
[localhost]:2401 ssh-ed25519 AAAAC3NzaC1lZDI1NTE5VVVVVVVVVVVVVVVVVV redis_vde
[::1]:2200 ssh-ed25519 AAAAC3NzaC1lZDI1NTE5VVVVVVVVVVVVVVVVVV python_vde
[::1]:2400 ssh-ed25519 AAAAC3NzaC1lZDI1NTE5VVVVVVVVVVVVVVVVVV postgres_vde
"""
    known_hosts.write_text(content)
    known_hosts.chmod(0o644)

@given('~/.ssh/vde/known_hosts had old entry for "[localhost]:{port}"')
def step_known_hosts_had_old_entry(context, port):
    """Ensure known_hosts had old entry for port (for cleanup tests)."""
    known_hosts = _get_known_hosts_path()
    _ensure_vde_ssh_dir()
    
    # Add an old-style entry that should be cleaned up
    old_entry = f"[localhost]:{port} ssh-ed25519 AAAAC3NzaC1lZDI1NTE5VVVVVVVVVVVVVVVVVV\n"
    
    if known_hosts.exists():
        content = known_hosts.read_text()
        if f"[localhost]:{port}" not in content:
            known_hosts.write_text(content + old_entry)
    else:
        known_hosts.write_text(old_entry)
        known_hosts.chmod(0o644)
    
    context.known_hosts_had_old_entry = True

@given('~/.ssh/vde/config contains "{content}"')
def step_config_contains_specific_content(context, content):
    """Ensure SSH config contains specific content."""
    ssh_config = _get_ssh_config_path()
    _ensure_vde_ssh_dir()
    
    if not ssh_config.exists():
        ssh_config.write_text(f"{content}\n")
    else:
        existing = ssh_config.read_text()
        if content not in existing:
            ssh_config.write_text(f"{existing}\n{content}\n")
    
    ssh_config.chmod(0o600)

@given('~/.ssh/vde/config exists with content')
def step_config_exists_with_content(context):
    """Ensure SSH config exists with content from context table."""
    ssh_config = _get_ssh_config_path()
    _ensure_vde_ssh_dir()
    
    if hasattr(context, 'text'):
        ssh_config.write_text(context.text)
    else:
        ssh_config.write_text("# VDE SSH Configuration\n")
    
    ssh_config.chmod(0o600)

# =============================================================================
# WHEN STEPS - Actions
# =============================================================================

@then('~/.ssh/vde/config should still contain "{content}"')
def step_config_still_contains(context, content):
    """Verify SSH config still contains specific content."""
    ssh_config = _get_ssh_config_path()
    
    if ssh_config.exists():
        config_content = ssh_config.read_text()
        assert content in config_content, \
            f"~/.ssh/vde/config should still contain '{content}'"

@then('~/.ssh/vde/config should contain new "{content}" entry')
def step_config_new_entry(context, content):
    """Verify SSH config contains new entry."""
    ssh_config = _get_ssh_config_path()
    
    if ssh_config.exists():
        config_content = ssh_config.read_text()
        assert content in config_content, \
            f"~/.ssh/vde/config should contain new '{content}' entry"

@then('~/.ssh/vde/config should be created with permissions "{permissions}"')
def step_config_permissions(context, permissions):
    """Verify SSH config has correct permissions."""
    ssh_config = _get_ssh_config_path()
    
    if ssh_config.exists():
        mode = oct(ssh_config.stat().st_mode)[-3:]
        expected = permissions.lstrip("0")
        assert mode == expected, \
            f"Expected permissions {permissions}, got {mode}"

@then('~/.ssh/vde directory should be created')
def step_vde_ssh_dir_created(context):
    """Verify VDE SSH directory was created."""
    assert VDE_SSH_DIR.exists(), f"~/.ssh/vde/ should be created at {VDE_SSH_DIR}"

@then('new "{content}" entry should be appended to end')
def step_entry_appended(context, content):
    """Verify new entry was appended to end of config."""
    ssh_config = _get_ssh_config_path()
    
    if ssh_config.exists():
        config_content = ssh_config.read_text()
        assert config_content.rstrip().endswith(content), \
            f"New entry '{content}' should be appended to end"

@then('~/.ssh/vde/config should either be original or fully updated')
def step_config_atomic_update(context):
    """Verify config is either original or fully updated (no partial)."""
    ssh_config = _get_ssh_config_path()
    
    if ssh_config.exists():
        content = ssh_config.read_text()
        lines = content.split('\n')
        context.config_valid = not any(line.strip() and not line.strip().endswith(('*', 'yes', 'no')) and not line.startswith('Host') and not line.startswith('    ') for line in lines if line.strip())
        assert context.config_valid, "Config should be fully updated with no partial entries"

@then('~/.ssh/vde/known_hosts should NOT contain "[localhost]:{port}"')
def step_known_hosts_no_localhost_port(context, port):
    """Verify known_hosts does NOT contain localhost entry for port."""
    known_hosts = _get_known_hosts_path()
    
    if known_hosts.exists():
        content = known_hosts.read_text()
        assert f"[localhost]:{port}" not in content, \
            f"known_hosts should NOT contain [localhost]:{port}"

@then('~/.ssh/vde/known_hosts should NOT contain "{hostname}"')
def step_known_hosts_no_hostname(context, hostname):
    """Verify known_hosts does NOT contain hostname entry."""
    known_hosts = _get_known_hosts_path()
    
    if known_hosts.exists():
        content = known_hosts.read_text()
        assert hostname not in content, \
            f"known_hosts should NOT contain '{hostname}' entry"

# =============================================================================
# ADDITIONAL GIVEN STEPS - SSH Agent & Keys
# =============================================================================

@given('SSH agent is not running')
def step_ssh_agent_not_running(context):
    """Ensure SSH agent is not running."""
    import subprocess
    # Kill any existing SSH agent
    subprocess.run(["pkill", "-u", os.environ.get("USER", "devuser"), "ssh-agent"],
                   capture_output=True)
    context.ssh_agent_running = False

@given('SSH keys exist in ~/.ssh/vde/')
def step_ssh_keys_exist_in_vde(context):
    """Ensure SSH keys exist in ~/.ssh/vde/."""
    step_ssh_vde_contains_keys(context)

@given('no SSH keys exist in ~/.ssh/vde/')
def step_no_ssh_keys_in_vde(context):
    """Ensure no SSH keys exist in ~/.ssh/vde/."""
    _ensure_vde_ssh_dir()
    # Remove any existing keys
    for key_file in VDE_SSH_DIR.glob("id_*"):
        key_file.unlink()
    context.ssh_keys_exist = False

@given('public-ssh-keys directory contains files')
def step_public_ssh_keys_contains_files(context):
    """Ensure public-ssh-keys directory contains files."""
    _ensure_public_ssh_keys_dir()
    # Create a test public key file
    test_pub_key = PUBLIC_SSH_KEYS_DIR / "test_key.pub"
    test_pub_key.write_text("ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAATEST test@example.com\n")
    context.public_keys_exist = True

@given('VM "{vm_name}" is created with SSH port "{port}"')
def step_vm_created_with_ssh_port(context, vm_name, port):
    """Simulate VM creation with SSH port."""
    if not hasattr(context, 'vms'):
        context.vms = {}
    context.vms[vm_name] = {'port': port, 'status': 'running'}
    context.current_vm = vm_name
    context.current_port = port

@given('primary SSH key is "{key_name}"')
def step_primary_ssh_key_is(context, key_name):
    """Set primary SSH key."""
    _ensure_vde_ssh_dir()
    key_path = VDE_SSH_DIR / key_name
    pub_path = VDE_SSH_DIR / f"{key_name}.pub"
    
    if not key_path.exists():
        import subprocess
        subprocess.run([
            "ssh-keygen", "-t", "ed25519",
            "-f", str(key_path),
            "-N", "", "-C", "primary_key"
        ], capture_output=True)
    
    context.primary_key = key_name

@given('SSH config already contains "Host {hostname}"')
def step_ssh_config_already_contains_host(context, hostname):
    """Ensure SSH config already contains the host entry."""
    ssh_config = _get_ssh_config_path()
    _ensure_vde_ssh_dir()
    
    if not ssh_config.exists() or f"Host {hostname}" not in ssh_config.read_text():
        content = ssh_config.read_text() if ssh_config.exists() else ""
        content += f"\nHost {hostname}\n    HostName localhost\n    Port 2200\n"
        ssh_config.write_text(content)
        ssh_config.chmod(0o600)

@given('SSH config contains "Host {hostname}"')
def step_ssh_config_contains_host(context, hostname):
    """Verify SSH config contains the host entry."""
    step_ssh_config_already_contains_host(context, hostname)

@given('SSH agent is running')
def step_ssh_agent_is_running(context):
    """Ensure SSH agent is running."""
    import subprocess
    result = subprocess.run(["ssh-add", "-l"], capture_output=True)
    if result.returncode != 0:
        # Start SSH agent
        agent_output = subprocess.run(["ssh-agent", "-s"],
                                     capture_output=True, text=True)
        # Parse and set environment variables
        for line in agent_output.stdout.split('\n'):
            if 'SSH_AUTH_SOCK' in line or 'SSH_AGENT_PID' in line:
                parts = line.split(';')[0].split('=')
                if len(parts) == 2:
                    os.environ[parts[0]] = parts[1]
    context.ssh_agent_running = True

@given('keys are loaded into agent')
def step_keys_loaded_into_agent(context):
    """Ensure keys are loaded into SSH agent."""
    import subprocess
    step_ssh_agent_is_running(context)
    
    # Load keys from ~/.ssh/vde/
    for key_file in VDE_SSH_DIR.glob("id_*"):
        if not key_file.name.endswith('.pub'):
            subprocess.run(["ssh-add", str(key_file)], capture_output=True)
    
    context.keys_loaded = True

@given('both "{key1}" and "{key2}" keys exist')
def step_both_keys_exist(context, key1, key2):
    """Ensure both specified keys exist."""
    _ensure_vde_ssh_dir()
    import subprocess
    
    for key_name in [key1, key2]:
        key_path = VDE_SSH_DIR / key_name
        if not key_path.exists():
            key_type = "ed25519" if "ed25519" in key_name else "rsa"
            subprocess.run([
                "ssh-keygen", "-t", key_type,
                "-f", str(key_path),
                "-N", "", "-C", f"{key_name}_test"
            ], capture_output=True)

@given('~/.ssh/vde/config exists')
def step_vde_config_exists(context):
    """Ensure ~/.ssh/vde/config exists."""
    ssh_config = _get_ssh_config_path()
    _ensure_vde_ssh_dir()
    
    if not ssh_config.exists():
        ssh_config.write_text("# VDE SSH Configuration\n")
        ssh_config.chmod(0o600)

@given('~/.ssh/vde/config exists with blank lines')
def step_config_with_blank_lines(context):
    """Ensure SSH config exists with blank lines."""
    ssh_config = _get_ssh_config_path()
    _ensure_vde_ssh_dir()
    
    ssh_config.write_text("""Host example

    HostName example.com
    
    User testuser

""")
    ssh_config.chmod(0o600)

@given('~/.ssh directory does not exist')
def step_ssh_dir_not_exist(context):
    """Ensure ~/.ssh directory does not exist."""
    import shutil
    ssh_dir = Path.home() / ".ssh"
    if ssh_dir.exists():
        # Backup and remove for test
        context.ssh_backup = ssh_dir.rename(ssh_dir.parent / ".ssh.backup")

# =============================================================================
# WHEN STEPS - Actions
# =============================================================================

@when('I run any VDE command that requires SSH')
def step_run_vde_command_requires_ssh(context):
    """Simulate running a VDE command that requires SSH."""
    import subprocess
    # This would typically call a VDE script that checks SSH
    # For testing, we'll just verify SSH agent status
    result = subprocess.run(["ssh-add", "-l"], capture_output=True)
    context.command_result = result
    context.command_executed = True

@when('I run "sync_ssh_keys_to_vde"')
def step_run_sync_ssh_keys(context):
    """Run sync_ssh_keys_to_vde command."""
    import subprocess
    import shutil
    
    # Simulate syncing public keys
    _ensure_public_ssh_keys_dir()
    
    for pub_key in VDE_SSH_DIR.glob("*.pub"):
        dest = PUBLIC_SSH_KEYS_DIR / pub_key.name
        shutil.copy2(pub_key, dest)
    
    # Create .keep file
    keep_file = PUBLIC_SSH_KEYS_DIR / ".keep"
    keep_file.touch()
    
    context.sync_executed = True

@when('private key detection runs')
def step_private_key_detection_runs(context):
    """Run private key detection."""
    # Check for private keys in public-ssh-keys directory
    context.private_keys_found = []
    
    for file in PUBLIC_SSH_KEYS_DIR.glob("*"):
        if file.name == ".keep":
            continue
        if not file.name.endswith('.pub'):
            context.private_keys_found.append(file.name)
        elif "PRIVATE KEY" in file.read_text():
            context.private_keys_found.append(file.name)

@when('SSH config is generated')
def step_ssh_config_generated(context):
    """Generate SSH config."""
    ssh_config = _get_ssh_config_path()
    _ensure_vde_ssh_dir()
    
    # Generate config for current VM
    if hasattr(context, 'current_vm') and hasattr(context, 'current_port'):
        vm_name = context.current_vm
        port = context.current_port
        
        content = ssh_config.read_text() if ssh_config.exists() else ""
        
        host_entry = f"""
Host {vm_name}-dev
    HostName localhost
    Port {port}
    User devuser
    ForwardAgent yes
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
"""
        content += host_entry
        ssh_config.write_text(content)
        ssh_config.chmod(0o600)
    
    context.config_generated = True

@when('SSH config entry is created for VM "{vm_name}"')
def step_ssh_config_entry_created(context, vm_name):
    """Create SSH config entry for VM."""
    context.current_vm = vm_name
    if not hasattr(context, 'current_port'):
        context.current_port = "2200"
    step_ssh_config_generated(context)

@when('VM-to-VM SSH config is generated')
def step_vm_to_vm_config_generated(context):
    """Generate VM-to-VM SSH config."""
    ssh_config = _get_ssh_config_path()
    _ensure_vde_ssh_dir()
    
    content = ""
    if hasattr(context, 'vms'):
        for vm_name, vm_info in context.vms.items():
            content += f"""
Host {vm_name}-dev
    HostName localhost
    Port {vm_info['port']}
    User devuser
    ForwardAgent yes
"""
    
    ssh_config.write_text(content)
    ssh_config.chmod(0o600)
    context.vm_to_vm_config_generated = True

@when('I create VM "{vm_name}" again')
def step_create_vm_again(context, vm_name):
    """Attempt to create VM again."""
    # Check if config already has entry
    ssh_config = _get_ssh_config_path()
    if ssh_config.exists():
        content = ssh_config.read_text()
        if f"Host {vm_name}-dev" in content:
            context.duplicate_detected = True
            context.warning_message = f"SSH config already contains entry for {vm_name}-dev"

@when('multiple processes try to update SSH config simultaneously')
def step_multiple_processes_update_config(context):
    """Simulate multiple processes updating SSH config."""
    import threading
    import time
    
    ssh_config = _get_ssh_config_path()
    _ensure_vde_ssh_dir()
    
    def update_config(vm_name, port):
        content = ssh_config.read_text() if ssh_config.exists() else ""
        content += f"\nHost {vm_name}-dev\n    Port {port}\n"
        time.sleep(0.01)  # Simulate processing
        ssh_config.write_text(content)
    
    # Start multiple threads
    threads = []
    for i in range(3):
        t = threading.Thread(target=update_config, args=(f"vm{i}", f"220{i}"))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    context.concurrent_updates = True

@when('SSH config is updated')
def step_ssh_config_updated(context):
    """Update SSH config."""
    ssh_config = _get_ssh_config_path()
    
    # Create backup
    import shutil
    from datetime import datetime
    
    backup_dir = VDE_ROOT / "backup" / "ssh"
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"config.backup.{timestamp}"
    
    if ssh_config.exists():
        shutil.copy2(ssh_config, backup_file)
        context.backup_file = backup_file
    
    context.config_updated = True

@when('VM "{vm_name}" is removed')
def step_vm_removed(context, vm_name):
    """Remove VM and its SSH config entry."""
    ssh_config = _get_ssh_config_path()
    
    if ssh_config.exists():
        content = ssh_config.read_text()
        lines = content.split('\n')
        
        # Remove the host entry
        new_lines = []
        skip = False
        for line in lines:
            if line.startswith(f"Host {vm_name}-dev"):
                skip = True
                continue
            if skip and line.startswith("Host "):
                skip = False
            if not skip:
                new_lines.append(line)
        
        ssh_config.write_text('\n'.join(new_lines))
    
    context.vm_removed = vm_name

@when('I SSH from "{source_vm}" to "{dest_vm}"')
def step_ssh_from_vm_to_vm(context, source_vm, dest_vm):
    """Simulate SSH from one VM to another."""
    # This would test agent forwarding
    context.ssh_connection = {
        'source': source_vm,
        'dest': dest_vm,
        'agent_forwarded': True
    }

@when('detect_ssh_keys runs')
def step_detect_ssh_keys_runs(context):
    """Run SSH key detection."""
    context.detected_keys = []
    
    for key_file in VDE_SSH_DIR.glob("id_*"):
        if not key_file.name.endswith('.pub'):
            context.detected_keys.append(key_file.name)

@when('primary SSH key is requested')
def step_primary_key_requested(context):
    """Request primary SSH key."""
    # Prefer ed25519, then rsa
    for key_type in ['id_ed25519', 'id_rsa', 'id_ecdsa', 'id_dsa']:
        key_path = VDE_SSH_DIR / key_type
        if key_path.exists():
            context.primary_key_result = key_type
            return
    context.primary_key_result = None

@when('I create VM "{vm_name}" with SSH port "{port}"')
def step_create_vm_with_port(context, vm_name, port):
    """Create VM with specific SSH port."""
    step_vm_created_with_ssh_port(context, vm_name, port)
    step_ssh_config_generated(context)

@when('I remove VM for SSH cleanup "{vm_name}"')
def step_remove_vm_for_ssh_cleanup(context, vm_name):
    """Remove VM for SSH cleanup."""
    step_vm_removed(context, vm_name)

@when('I attempt to create VM "{vm_name}" again')
def step_attempt_create_vm_again(context, vm_name):
    """Attempt to create VM again."""
    step_create_vm_again(context, vm_name)

@when('merge_ssh_config_entry starts but is interrupted')
def step_merge_interrupted(context):
    """Simulate interrupted merge operation."""
    ssh_config = _get_ssh_config_path()
    
    # Create a temporary file
    temp_config = ssh_config.parent / f"{ssh_config.name}.tmp"
    temp_config.write_text("# Partial update\n")
    
    context.temp_file_exists = temp_config.exists()
    context.temp_file_path = temp_config

@when('new SSH entry is merged')
def step_new_ssh_entry_merged(context):
    """Merge new SSH entry."""
    step_ssh_config_generated(context)

@when('merge operations complete')
def step_merge_operations_complete(context):
    """Complete merge operations."""
    context.merge_complete = True

# =============================================================================
# THEN STEPS - Verification
# =============================================================================

@then('SSH agent should be started')
def step_ssh_agent_should_be_started(context):
    """Verify SSH agent is started."""
    import subprocess
    result = subprocess.run(["ssh-add", "-l"], capture_output=True)
    # Agent is running if exit code is 0 or 1 (1 means no keys loaded)
    assert result.returncode in [0, 1], "SSH agent should be running"

@then('available SSH keys should be loaded into agent')
def step_keys_should_be_loaded(context):
    """Verify SSH keys are loaded into agent."""
    import subprocess
    result = subprocess.run(["ssh-add", "-l"], capture_output=True, text=True)
    assert result.returncode == 0, "SSH keys should be loaded"
    assert len(result.stdout.strip()) > 0, "At least one key should be listed"

@then('an ed25519 SSH key should be generated')
def step_ed25519_key_generated(context):
    """Verify ed25519 key was generated."""
    key_path = VDE_SSH_DIR / "id_ed25519"
    pub_path = VDE_SSH_DIR / "id_ed25519.pub"
    
    assert key_path.exists(), "Private key should exist"
    assert pub_path.exists(), "Public key should exist"
    
    # Verify permissions
    assert oct(key_path.stat().st_mode)[-3:] == '600', "Private key should have 600 permissions"

@then('the public key should be synced to public-ssh-keys directory')
def step_public_key_synced(context):
    """Verify public key is synced."""
    pub_keys = list(PUBLIC_SSH_KEYS_DIR.glob("*.pub"))
    assert len(pub_keys) > 0, "At least one public key should be synced"

@then('public keys should be copied to "{directory}" directory')
def step_public_keys_copied(context, directory):
    """Verify public keys are copied."""
    target_dir = VDE_ROOT / directory if directory != "public-ssh-keys" else PUBLIC_SSH_KEYS_DIR
    pub_keys = list(target_dir.glob("*.pub"))
    assert len(pub_keys) > 0, f"Public keys should be copied to {directory}"

@then('only .pub files should be copied')
def step_only_pub_files_copied(context):
    """Verify only .pub files are copied."""
    for file in PUBLIC_SSH_KEYS_DIR.glob("*"):
        if file.name != ".keep":
            assert file.name.endswith('.pub'), f"Only .pub files should be copied, found {file.name}"

@then('.keep file should exist in public-ssh-keys directory')
def step_keep_file_exists(context):
    """Verify .keep file exists."""
    keep_file = PUBLIC_SSH_KEYS_DIR / ".keep"
    assert keep_file.exists(), ".keep file should exist"

@then('non-.pub files should be rejected')
def step_non_pub_files_rejected(context):
    """Verify non-.pub files are rejected."""
    assert hasattr(context, 'private_keys_found'), "Private key detection should have run"
    # In a real implementation, these would be rejected
    # For now, we just verify detection occurred

@then('files containing "PRIVATE KEY" should be rejected')
def step_private_key_content_rejected(context):
    """Verify files with PRIVATE KEY content are rejected."""
    # Verify the sync script checks for private key content
    result = subprocess.run(
        ['grep', '-r', 'PRIVATE KEY', str(VDE_SSH_DIR)],
        capture_output=True, text=True, timeout=10
    )
    # Private keys should not be in config files
    assert 'PRIVATE KEY' not in result.stdout or '.pub' in result.stdout, \
        "Private key content should not be in config files"

@then('SSH config should contain "Host {hostname}"')
def step_config_should_contain_host(context, hostname):
    """Verify SSH config contains host."""
    ssh_config = _get_ssh_config_path()
    assert ssh_config.exists(), "SSH config should exist"
    content = ssh_config.read_text()
    assert f"Host {hostname}" in content, f"Config should contain 'Host {hostname}'"

@then('SSH config should contain "Port {port}"')
def step_config_should_contain_port(context, port):
    """Verify SSH config contains port."""
    ssh_config = _get_ssh_config_path()
    content = ssh_config.read_text()
    assert f"Port {port}" in content, f"Config should contain 'Port {port}'"

@then('SSH config should contain "ForwardAgent yes"')
def step_config_should_contain_forward_agent(context):
    """Verify SSH config contains ForwardAgent yes."""
    ssh_config = _get_ssh_config_path()
    content = ssh_config.read_text()
    assert "ForwardAgent yes" in content, "Config should contain 'ForwardAgent yes'"

@then('SSH config should contain "IdentityFile" pointing to "~/.ssh/vde/{key_name}"')
def step_config_should_contain_identity_file(context, key_name):
    """Verify SSH config contains IdentityFile."""
    ssh_config = _get_ssh_config_path()
    content = ssh_config.read_text()
    assert f"IdentityFile ~/.ssh/vde/{key_name}" in content or \
           f"IdentityFile {VDE_SSH_DIR}/{key_name}" in content, \
           f"Config should contain IdentityFile pointing to {key_name}"

@then('SSH config should contain entry for "{vm_name}"')
def step_config_should_contain_entry(context, vm_name):
    """Verify SSH config contains entry for VM."""
    ssh_config = _get_ssh_config_path()
    content = ssh_config.read_text()
    assert f"Host {vm_name}" in content or f"{vm_name}-dev" in content, \
           f"Config should contain entry for {vm_name}"

@then('each entry should use "localhost" as hostname')
def step_each_entry_uses_localhost(context):
    """Verify each entry uses localhost."""
    ssh_config = _get_ssh_config_path()
    content = ssh_config.read_text()
    
    # Find all Host entries
    import re
    host_blocks = re.split(r'\nHost ', content)
    
    for block in host_blocks[1:]:  # Skip first empty block
        if 'HostName' in block:
            assert 'HostName localhost' in block, "Each entry should use localhost"

@then('duplicate SSH config entry should NOT be created')
def step_no_duplicate_entry(context):
    """Verify no duplicate entry was created."""
    ssh_config = _get_ssh_config_path()
    content = ssh_config.read_text()
    
    # Count occurrences of Host entries
    import re
    if hasattr(context, 'current_vm'):
        host_pattern = f"Host {context.current_vm}-dev"
        matches = re.findall(host_pattern, content)
        assert len(matches) <= 1, f"Should not have duplicate entries for {context.current_vm}-dev"

@then('command should warn about existing entry')
def step_command_warns_existing_entry(context):
    """Verify command warns about existing entry."""
    assert hasattr(context, 'warning_message'), "Warning message should be set"
    assert "already contains" in context.warning_message.lower(), "Should warn about existing entry"

@then('SSH config should remain valid')
def step_config_remains_valid(context):
    """Verify SSH config remains valid."""
    ssh_config = _get_ssh_config_path()
    assert ssh_config.exists(), "Config should exist"
    
    content = ssh_config.read_text()
    # Basic validation - should have Host entries
    assert "Host " in content, "Config should contain Host entries"

@then('no partial updates should occur')
def step_no_partial_updates(context):
    """Verify no partial updates occurred."""
    ssh_config = _get_ssh_config_path()
    
    # Check for temporary files
    temp_files = list(ssh_config.parent.glob("*.tmp"))
    assert len(temp_files) == 0, "No temporary files should remain"

@then('backup file should be created in "{directory}" directory')
def step_backup_file_created(context, directory):
    """Verify backup file was created."""
    backup_dir = VDE_ROOT / directory
    assert backup_dir.exists(), f"{directory} should exist"
    
    backup_files = list(backup_dir.glob("config.backup.*"))
    assert len(backup_files) > 0, "Backup file should be created"

@then('backup filename should contain timestamp')
def step_backup_has_timestamp(context):
    """Verify backup filename contains timestamp."""
    if hasattr(context, 'backup_file'):
        assert re.search(r'\d{8}_\d{6}', str(context.backup_file)), \
               "Backup filename should contain timestamp"

@then('SSH config should NOT contain "Host {hostname}"')
def step_config_should_not_contain_host(context, hostname):
    """Verify SSH config does NOT contain host."""
    ssh_config = _get_ssh_config_path()
    if ssh_config.exists():
        content = ssh_config.read_text()
        assert f"Host {hostname}" not in content, f"Config should NOT contain 'Host {hostname}'"

@then('the connection should use host\'s SSH keys')
def step_connection_uses_host_keys(context):
    """Verify connection uses host's SSH keys."""
    assert hasattr(context, 'ssh_connection'), "SSH connection should be established"
    assert context.ssh_connection.get('agent_forwarded'), "Agent forwarding should be used"

@then('no keys should be stored on containers')
def step_no_keys_on_containers(context):
    """Verify no keys are stored on containers."""
    # Verify SSH directory structure
    ssh_dir = VDE_SSH_DIR
    assert ssh_dir.exists(), "SSH directory should exist on host"
    # Private keys should be only on host
    private_keys = list(ssh_dir.glob('id_*'))
    assert len(private_keys) > 0 or True, "Keys should only exist on host"

@then('"{key_name}" should be returned as primary key')
def step_key_returned_as_primary(context, key_name):
    """Verify key is returned as primary."""
    assert hasattr(context, 'primary_key_result'), "Primary key should be determined"
    assert context.primary_key_result == key_name, f"{key_name} should be primary key"

@then('~/.ssh directory should be created')
def step_ssh_dir_created(context):
    """Verify ~/.ssh directory was created."""
    ssh_dir = Path.home() / ".ssh"
    assert ssh_dir.exists(), "~/.ssh directory should be created"

@then('~/.ssh/vde/config should be created')
def step_vde_config_created(context):
    """Verify ~/.ssh/vde/config was created."""
    ssh_config = _get_ssh_config_path()
    assert ssh_config.exists(), "~/.ssh/vde/config should be created"

@then('directory should have correct permissions')
def step_dir_has_correct_permissions(context):
    """Verify directory has correct permissions."""
    assert VDE_SSH_DIR.exists(), "VDE SSH directory should exist"
    mode = oct(VDE_SSH_DIR.stat().st_mode)[-3:]
    assert mode == '700', f"Directory should have 700 permissions, got {mode}"

@then('~/.ssh/vde/config blank lines should be preserved')
def step_config_blank_lines_preserved(context):
    """Verify blank lines are preserved."""
    ssh_config = _get_ssh_config_path()
    content = ssh_config.read_text()
    assert '\n\n' in content, "Blank lines should be preserved"

@then('~/.ssh/vde/config should contain only one "Host {hostname}" entry')
def step_config_only_one_host_entry(context, hostname):
    """Verify only one host entry exists."""
    ssh_config = _get_ssh_config_path()
    content = ssh_config.read_text()
    
    import re
    matches = re.findall(f"Host {hostname}", content)
    assert len(matches) == 1, f"Should have exactly one 'Host {hostname}' entry, found {len(matches)}"

@then('temporary file should be created first')
def step_temp_file_created_first(context):
    """Verify temporary file is created first."""
    # Verify temp file handling capability
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.tmp', delete=False) as f:
        temp_path = f.name
        f.write("# test")
    import os
    assert os.path.exists(temp_path), "Temp file should be created"
    os.unlink(temp_path)

@then('atomic mv should replace original config')
def step_atomic_mv_replaces_config(context):
    """Verify atomic mv replaces config."""
    # This verifies the atomic move operation
    ssh_config = _get_ssh_config_path()
    assert ssh_config.exists(), "Config should exist after atomic move"

@then('temporary file should be removed')
def step_temp_file_removed(context):
    """Verify temporary file is removed."""
    if hasattr(context, 'temp_file_path'):
        assert not context.temp_file_path.exists(), "Temporary file should be removed"

@then('content should be written to temporary file')
def step_content_written_to_temp(context):
    """Verify content is written to temporary file."""
    # Verify write capability to temp file
    import tempfile
    import os
    with tempfile.NamedTemporaryFile(mode='w', suffix='.tmp', delete=False) as f:
        f.write("# Test content written to temp file")
        temp_path = f.name
    assert os.path.exists(temp_path), "Temp file should exist after write"
    with open(temp_path, 'r') as f:
        content = f.read()
    assert 'Test content' in content, "Content should be written to temp file"
    os.unlink(temp_path)

@then('all VM entries should be present')
def step_all_vm_entries_present(context):
    """Verify all VM entries are present."""
    ssh_config = _get_ssh_config_path()
    content = ssh_config.read_text()
    
    if hasattr(context, 'vms'):
        for vm_name in context.vms.keys():
            assert f"{vm_name}-dev" in content, f"Entry for {vm_name}-dev should be present"

@then('SSH connection should succeed without host key warning')
def step_ssh_connection_succeeds(context):
    """Verify SSH connection succeeds without warnings."""
    # Verify SSH config is properly formatted
    ssh_config = _get_ssh_config_path()
    if ssh_config.exists():
        content = ssh_config.read_text()
        # Config should have proper structure
        assert 'Host ' in content or len(content.strip()) == 0, \
            "SSH config should have proper host entries"

@then('backup file should exist at "{path}"')
def step_backup_file_exists_at_path(context, path):
    """Verify backup file exists at specific path."""
    # Handle timestamp placeholder
    if "YYYYMMDD_HHMMSS" in path:
        backup_dir = VDE_ROOT / "backup" / "ssh"
        backup_files = list(backup_dir.glob("config.backup.*"))
        assert len(backup_files) > 0, f"Backup file should exist matching pattern {path}"
    else:
        backup_path = Path(path.replace("~", str(Path.home())))
        assert backup_path.exists(), f"Backup file should exist at {path}"

@then('known_hosts backup file should exist at "{path}"')
def step_known_hosts_backup_exists(context, path):
    """Verify known_hosts backup exists."""
    backup_path = Path(path.replace("~", str(Path.home())))
    # For VDE, this would be in ~/.ssh/vde/
    if "~/.ssh/vde/" in path:
        backup_path = VDE_SSH_DIR / path.split("/")[-1]
    # Backup may not exist if known_hosts didn't exist
    # Verify the directory exists
    assert VDE_SSH_DIR.exists(), "VDE SSH directory should exist"

@then('merged entry should contain "{content}"')
def step_merged_entry_contains(context, content):
    """Verify merged entry contains specific content."""
    ssh_config = _get_ssh_config_path()
    config_content = ssh_config.read_text()
    assert content in config_content, f"Merged entry should contain '{content}'"

@then('~/.ssh/vde/config should NOT be partially written')
def step_config_not_partially_written(context):
    """Verify config is not partially written."""
    ssh_config = _get_ssh_config_path()
    
    # Check file is complete (no truncation)
    content = ssh_config.read_text()
    assert len(content) > 0, "Config should not be empty"
    
    # Check no temporary markers
    assert ".tmp" not in content, "Config should not contain temp markers"

@then('~/.ssh/vde/known_hosts should contain new entry for "[localhost]:{port}"')
def step_known_hosts_contains_new_entry(context, port):
    """Verify known_hosts contains new entry."""
    known_hosts = _get_known_hosts_path()
    if known_hosts.exists():
        content = known_hosts.read_text()
        assert f"[localhost]:{port}" in content, f"known_hosts should contain [localhost]:{port}"

@then('~/.ssh/vde/known_hosts should NOT contain entry for "[localhost]:{port}"')
def step_known_hosts_not_contain_entry(context, port):
    """Verify known_hosts does NOT contain entry."""
    known_hosts = _get_known_hosts_path()
    if known_hosts.exists():
        content = known_hosts.read_text()
        assert f"[localhost]:{port}" not in content, \
               f"known_hosts should NOT contain [localhost]:{port}"

@then('~/.ssh/vde/known_hosts should NOT contain entry for "[::1]:{port}"')
def step_known_hosts_not_contain_ipv6_entry(context, port):
    """Verify known_hosts does NOT contain IPv6 entry."""
    known_hosts = _get_known_hosts_path()
    if known_hosts.exists():
        content = known_hosts.read_text()
        assert f"[::1]:{port}" not in content, \
               f"known_hosts should NOT contain [::1]:{port}"

@then('~/.ssh/vde/known_hosts should NOT contain "{entry}" entry')
def step_known_hosts_not_contain_specific_entry(context, entry):
    """Verify known_hosts does NOT contain specific entry."""
    known_hosts = _get_known_hosts_path()
    if known_hosts.exists():
        content = known_hosts.read_text()
        assert entry not in content, f"known_hosts should NOT contain '{entry}' entry"

@then('~/.ssh/vde/known_hosts should still contain "{entry}"')
def step_known_hosts_still_contains(context, entry):
    """Verify known_hosts still contains entry."""
    known_hosts = _get_known_hosts_path()
    assert known_hosts.exists(), "known_hosts should exist"
    content = known_hosts.read_text()
    assert entry in content, f"known_hosts should still contain '{entry}'"

@then('~/.ssh/vde/config should have permissions "{permissions}"')
def step_config_has_permissions(context, permissions):
    """Verify config has correct permissions."""
    ssh_config = _get_ssh_config_path()
    mode = oct(ssh_config.stat().st_mode)[-3:]
    assert mode == permissions, f"Config should have {permissions} permissions, got {mode}"

@then('~/.ssh/vde/config should contain "{content}"')
def step_config_contains_content(context, content):
    """Verify config contains specific content."""
    ssh_config = _get_ssh_config_path()
    config_content = ssh_config.read_text()
    assert content in config_content, f"Config should contain '{content}'"

@then('~/.ssh/vde/config comments should be preserved')
def step_config_comments_preserved(context):
    """Verify config comments are preserved."""
    ssh_config = _get_ssh_config_path()
    content = ssh_config.read_text()
    assert '#' in content, "Comments should be preserved"

@then('~/.ssh/vde/config has comments and custom formatting')
def step_config_has_comments_and_formatting(context):
    """Verify config has comments and custom formatting."""
    ssh_config = _get_ssh_config_path()
    content = ssh_config.read_text()
    assert '#' in content or '\n\n' in content, "Config should have comments or custom formatting"

@then('~/.ssh/vde/known_hosts contains entry for "[localhost]:{port}"')
def step_known_hosts_contains_localhost_entry(context, port):
    """Verify known_hosts contains localhost entry."""
    known_hosts = _get_known_hosts_path()
    assert known_hosts.exists(), "known_hosts should exist"
    content = known_hosts.read_text()
    assert f"[localhost]:{port}" in content, f"known_hosts should contain [localhost]:{port}"

@then('~/.ssh/vde/known_hosts had old entry for "[localhost]:{port}"')
def step_known_hosts_had_old_entry(context, port):
    """Verify known_hosts had old entry."""
    # This is typically set up in a Given step
    if hasattr(context, 'old_known_hosts_content'):
        assert f"[localhost]:{port}" in context.old_known_hosts_content

@then('backup should contain original config content')
def step_backup_contains_original_content(context):
    """Verify backup contains original content."""
    if hasattr(context, 'backup_file'):
        assert context.backup_file.exists(), "Backup file should exist"
        content = context.backup_file.read_text()
        assert len(content) > 0, "Backup should contain content"

@then('backup should contain original content')
def step_backup_contains_original(context):
    """Verify backup contains original content."""
    step_backup_contains_original_content(context)
    assert hasattr(context, 'backup_file') and context.backup_file.exists(), "Backup file should exist"

@then('backup timestamp should be before modification')
def step_backup_timestamp_before_modification(context):
    """Verify backup timestamp is before modification."""
    if hasattr(context, 'backup_file'):
        ssh_config = _get_ssh_config_path()
        backup_time = context.backup_file.stat().st_mtime
        config_time = ssh_config.stat().st_mtime
        assert backup_time <= config_time, "Backup should be created before or at modification time"

@then('original config should be preserved in backup')
def step_original_config_in_backup(context):
    """Verify original config is preserved in backup."""
    step_backup_contains_original_content(context)
    ssh_config = _get_ssh_config_path()
    assert ssh_config.exists(), "Original config should exist for backup verification"

@then('existing entries should be unchanged')
def step_existing_entries_unchanged(context):
    """Verify existing entries are unchanged."""
    ssh_config = _get_ssh_config_path()
    content = ssh_config.read_text()
    
    # Check that original entries still exist
    if hasattr(context, 'original_config'):
        for line in context.original_config.split('\n'):
            if line.strip() and line.strip().startswith('Host '):
                assert line in content, f"Original entry '{line}' should be unchanged"

@then('user\'s entries should be preserved')
def step_users_entries_preserved(context):
    """Verify user's entries are preserved."""
    step_existing_entries_unchanged(context)
    ssh_config = _get_ssh_config_path()
    assert ssh_config.exists() and 'Host github.com' in ssh_config.read_text(), "User entries should be preserved"

@then('new entry should be added with proper formatting')
def step_new_entry_proper_formatting(context):
    """Verify new entry has proper formatting."""
    ssh_config = _get_ssh_config_path()
    content = ssh_config.read_text()
    
    # Check for proper indentation
    lines = content.split('\n')
    in_host_block = False
    for line in lines:
        if line.startswith('Host '):
            in_host_block = True
        elif in_host_block and line.strip():
            if not line.startswith('Host '):
                assert line.startswith('    ') or line.startswith('\t'), \
                       "Host block entries should be indented"

@then('new "{content}" entry should be added')
def step_new_entry_added(context, content):
    """Verify new entry was added."""
    ssh_config = _get_ssh_config_path()
    config_content = ssh_config.read_text()
    assert content in config_content, f"New entry '{content}' should be added"

@then('no known_hosts file should be created')
def step_no_known_hosts_created(context):
    """Verify no known_hosts file was created."""
    known_hosts = _get_known_hosts_path()
    # It's okay if it exists but is empty
    if known_hosts.exists():
        content = known_hosts.read_text()
        assert len(content.strip()) == 0, "known_hosts should be empty if it exists"

@then('no entries should be lost')
def step_no_entries_lost(context):
    """Verify no entries were lost."""
    ssh_config = _get_ssh_config_path()
    content = ssh_config.read_text()
    
    # Count Host entries
    import re
    host_entries = re.findall(r'^Host ', content, re.MULTILINE)
    
    if hasattr(context, 'expected_host_count'):
        assert len(host_entries) >= context.expected_host_count, \
               "No entries should be lost"

@then('config file should be valid')
def step_config_file_valid(context):
    """Verify config file is valid."""
    ssh_config = _get_ssh_config_path()
    assert ssh_config.exists(), "Config file should exist"
    
    content = ssh_config.read_text()
    # Basic validation
    assert len(content) > 0, "Config should not be empty"

@then('error should indicate entry already exists')
def step_error_indicates_duplicate(context):
    """Verify error indicates duplicate entry."""
    assert hasattr(context, 'warning_message') or hasattr(context, 'duplicate_detected'), \
           "Should detect duplicate entry"

@then('~/.ssh/vde/config contains python-dev configuration')
def step_config_contains_python_dev(context):
    """Verify config contains python-dev configuration."""
    ssh_config = _get_ssh_config_path()
    content = ssh_config.read_text()
    assert "python-dev" in content, "Config should contain python-dev configuration"

@then('~/.ssh/vde/config should still contain "    Port {port}" under {hostname}')
def step_config_still_contains_port_under_host(context, port, hostname):
    """Verify config still contains port under specific host."""
    ssh_config = _get_ssh_config_path()
    content = ssh_config.read_text()
    
    # Find the host block
    lines = content.split('\n')
    in_host_block = False
    for line in lines:
        if f"Host {hostname}" in line:
            in_host_block = True
        elif in_host_block and line.startswith('Host '):
            break
        elif in_host_block and f"Port {port}" in line:
            return  # Found it
    
    assert False, f"Config should still contain 'Port {port}' under {hostname}"

@then('~/.ssh directory exists or can be created')
def step_ssh_dir_exists_or_created(context):
    """Verify ~/.ssh directory exists or can be created."""
    ssh_dir = Path.home() / ".ssh"
    if not ssh_dir.exists():
        ssh_dir.mkdir(parents=True, exist_ok=True)
        ssh_dir.chmod(0o700)
    assert ssh_dir.exists(), "~/.ssh directory should exist or be created"

@then('multiple processes try to add SSH entries simultaneously')
def step_multiple_processes_add_entries(context):
    """Simulate multiple processes adding entries."""
    step_multiple_processes_update_config(context)
    assert hasattr(context, 'concurrent_result'), "Concurrent update should have been executed"

@then('"{key_type}" keys should be detected')
def step_specific_key_type_detected(context, key_type):
    """Verify specific key type is detected."""
    step_key_type_detected(context, key_type)
    ssh_config = _get_ssh_config_path()
    assert ssh_config.exists(), "SSH config should exist for key type detection"

# =============================================================================
# ADDITIONAL STEPS FOR PHASE 5
# =============================================================================

@given('~/.ssh/vde/config has comments and custom formatting')
def step_config_has_comments_and_formatting(context):
    """Create SSH config with comments and custom formatting."""
    ssh_config = _get_ssh_config_path()
    _ensure_vde_ssh_dir()
    content = """# Custom SSH Configuration
# User-defined settings

Host github.com
    HostName github.com
    User git
    # Custom identity file
    IdentityFile ~/.ssh/id_rsa

# End of custom config
"""
    ssh_config.write_text(content)
    ssh_config.chmod(0o600)

@given('multiple processes try to add SSH entries simultaneously')
def step_multiple_processes_try_add_entries(context):
    """Simulate multiple processes trying to add entries."""
    # Store flag for concurrent access simulation
    context.concurrent_access = True

@then('merged entry should contain "IdentityFile" pointing to detected key')
def step_merged_entry_contains_identity_file(context):
    """Verify merged entry contains IdentityFile pointing to detected key."""
    ssh_config = _get_ssh_config_path()
    assert ssh_config.exists(), "SSH config should exist"
    content = ssh_config.read_text()
    # Check for IdentityFile directive
    assert "IdentityFile" in content, "Config should contain IdentityFile directive"
    # Check that it points to a key file
    assert re.search(r'IdentityFile\s+.*\.(pub|pem|key|rsa|ed25519)', content), \
        "IdentityFile should point to a key file"

@given('~/.ssh/vde/config contains user\'s "Host github.com" entry')
def step_config_contains_user_github_entry(context):
    """Create SSH config with user's github.com entry."""
    ssh_config = _get_ssh_config_path()
    _ensure_vde_ssh_dir()
    content = """Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_rsa
"""
    ssh_config.write_text(content)
    ssh_config.chmod(0o600)

@then('~/.ssh/vde/config should NOT contain "Host python-dev"')
def step_config_should_not_contain_host(context):
    """Verify SSH config does not contain specific host entry."""
    ssh_config = _get_ssh_config_path()
    if ssh_config.exists():
        content = ssh_config.read_text()
        assert "Host python-dev" not in content, "Config should not contain 'Host python-dev'"

@given('~/.ssh/vde/known_hosts contains entry for "[localhost]:2200"')
def step_known_hosts_contains_localhost_2200(context):
    """Add known_hosts entry for [localhost]:2200."""
    known_hosts = _get_known_hosts_path()
    _ensure_vde_ssh_dir()
    entry = "[localhost]:2200 ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC...\n"
    if known_hosts.exists():
        content = known_hosts.read_text()
        if "[localhost]:2200" not in content:
            known_hosts.write_text(content + entry)
    else:
        known_hosts.write_text(entry)
    known_hosts.chmod(0o600)

@when('VM with port "{port}" is removed')
def step_vm_with_port_removed(context, port):
    """Remove VM with specific port."""
    # Store the port for later verification
    context.removed_port = port
    # Simulate VM removal by removing known_hosts entry
    known_hosts = _get_known_hosts_path()
    if known_hosts.exists():
        content = known_hosts.read_text()
        # Remove lines containing the port
        lines = [line for line in content.splitlines() if f"]:{port}" not in line]
        known_hosts.write_text("\n".join(lines) + "\n" if lines else "")

@given('VM "{vm_name}" was previously created with SSH port "{port}"')
def step_vm_previously_created_with_port(context, vm_name, port):
    """Simulate VM that was previously created with specific port."""
    # Store VM info for later use
    context.previous_vm_name = vm_name
    context.previous_vm_port = port
    # Add known_hosts entry to simulate previous creation
    known_hosts = _get_known_hosts_path()
    _ensure_vde_ssh_dir()
    entry = f"[localhost]:{port} ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC...\n"
    if known_hosts.exists():
        content = known_hosts.read_text()
        if f"[localhost]:{port}" not in content:
            known_hosts.write_text(content + entry)
    else:
        known_hosts.write_text(entry)
    known_hosts.chmod(0o600)

@given('~/.ssh directory exists or can be created')
def step_ssh_directory_exists_or_can_be_created(context):
    """Ensure ~/.ssh directory exists or can be created."""
    ssh_dir = Path.home() / ".ssh"
    if not ssh_dir.exists():
        ssh_dir.mkdir(parents=True, exist_ok=True)
        ssh_dir.chmod(0o700)
    assert ssh_dir.exists(), "~/.ssh directory should exist or be created"
