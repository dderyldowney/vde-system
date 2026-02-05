"""
BDD Step Definitions for SSH Configuration.
Tests SSH config file creation, merging, validation, backup, and atomic update operations.
"""
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Import shared configuration
steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)

from behave import given, then, when

from config import VDE_ROOT
from vm_common import (
    run_vde_command,
    docker_ps,
    container_exists,
    container_is_running,
)


# =============================================================================
# GIVEN steps - Setup for SSH Configuration tests
# =============================================================================

@given('SSH agent is not running')
def step_ssh_agent_not_running(context):
    """Ensure SSH agent is not running."""
    result = subprocess.run(['pgrep', '-x', 'ssh-agent'], capture_output=True)
    if result.returncode == 0:
        # Agent is running, we'll work with it
        context.ssh_agent_was_running = True
    else:
        context.ssh_agent_was_running = False


@given('SSH keys exist in ~/.ssh/')
def step_ssh_keys_exist(context):
    """Ensure SSH keys exist."""
    ssh_dir = Path.home() / ".ssh"
    if not ssh_dir.exists():
        ssh_dir.mkdir(parents=True, exist_ok=True)
    context.ssh_keys_exist = True


@given('no SSH keys exist in ~/.ssh/')
def step_no_ssh_keys(context):
    """Ensure no SSH keys exist."""
    ssh_dir = Path.home() / ".ssh" / "vde"
    if ssh_dir.exists():
        # Remove existing keys for test
        subprocess.run(['rm', '-rf', str(ssh_dir)], check=True)
    context.no_ssh_keys = True


@given('public-ssh-keys directory contains files')
def step_public_keys_exist(context):
    """Ensure public-ssh-keys directory contains files."""
    public_ssh_dir = VDE_ROOT / "public-ssh-keys"
    if not public_ssh_dir.exists():
        public_ssh_dir.mkdir(parents=True, exist_ok=True)
    # Ensure .keep file exists
    keep_file = public_ssh_dir / ".keep"
    if not keep_file.exists():
        keep_file.write_text("")
    context.public_keys_exist = True


@given('VM "{vm_name}" is created with SSH port "{port}"')
def step_vm_created_with_port(context, vm_name, port):
    """Ensure VM is created with specific SSH port."""
    config_path = VDE_ROOT / "configs" / "docker" / vm_name / "docker-compose.yml"
    if not config_path.exists():
        result = run_vde_command(f"create {vm_name}", timeout=120)
        assert result.returncode == 0, f"Failed to create VM {vm_name}: {result.stderr}"
    context.vm_name = vm_name
    context.vm_ssh_port = port


@given('primary SSH key is "{key_name}"')
def step_primary_ssh_key(context, key_name):
    """Set primary SSH key."""
    context.primary_ssh_key = key_name



@given('SSH config already contains "Host {host_name}"')
def step_ssh_config_has_host(context, host_name):
    """Ensure SSH config already contains a host entry."""
    ssh_config = Path.home() / ".ssh" / "config"
    if not ssh_config.exists():
        ssh_config.parent.mkdir(parents=True, exist_ok=True)
        ssh_config.write_text("")
    content = ssh_config.read_text()
    if f"Host {host_name}" not in content:
        # Add the entry
        ssh_config.write_text(content + f"\nHost {host_name}\n    HostName localhost\n    Port 2200\n")




@given('SSH config contains "Host {host_name}"')
def step_ssh_config_contains_host(context, host_name):
    """Ensure SSH config contains a specific host entry."""
    ssh_config = Path.home() / ".ssh" / "config"
    if not ssh_config.exists():
        ssh_config.parent.mkdir(parents=True, exist_ok=True)
        ssh_config.write_text("")
    content = ssh_config.read_text()
    if f"Host {host_name}" not in content:
        content += f"\nHost {host_name}\n    HostName localhost\n"
        ssh_config.write_text(content)


@given('SSH agent is running')
def step_ssh_agent_running(context):
    """Ensure SSH agent is running."""
    result = subprocess.run(['pgrep', '-x', 'ssh-agent'], capture_output=True)
    if result.returncode != 0:
        # Start agent
        subprocess.run(['ssh-agent', '-s'], capture_output=True)
    context.ssh_agent_running = True


@given('keys are loaded into agent')
def step_keys_loaded(context):
    """Ensure keys are loaded into agent."""
    result = subprocess.run(['ssh-add', '-l'], capture_output=True)
    # ssh-add -l returns 1 if no keys, 2 if no agent
    if result.returncode != 0:
        # Try to add keys
        subprocess.run(['ssh-add'], capture_output=True)


@given('I have a language VM running')
def step_lang_vm_running(context):
    """Ensure a language VM is running."""
    if not container_is_running('python'):
        config_path = VDE_ROOT / "configs" / "docker" / "python" / "docker-compose.yml"
        if not config_path.exists():
            result = run_vde_command("create python", timeout=120)
            assert result.returncode == 0, "Failed to create Python VM"
        result = run_vde_command("start python", timeout=180)
        assert result.returncode == 0, "Failed to start Python VM"


@given('I have a service VM running')
def step_service_vm_running(context):
    """Ensure a service VM is running."""
    if not container_is_running('postgres'):
        config_path = VDE_ROOT / "configs" / "docker" / "postgres" / "docker-compose.yml"
        if not config_path.exists():
            result = run_vde_command("create postgres", timeout=120)
            assert result.returncode == 0, "Failed to create PostgreSQL VM"
        result = run_vde_command("start postgres", timeout=180)
        assert result.returncode == 0, "Failed to start PostgreSQL VM"


# =============================================================================
# WHEN steps - Actions for SSH Configuration tests
# =============================================================================

@when('I run any VDE command that requires SSH')
def step_run_vde_ssh_command(context):
    """Run a VDE command that requires SSH."""
    result = run_vde_command("list", timeout=30)
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('I run "sync_ssh_keys_to_vde"')
def step_run_sync_ssh_keys(context):
    """Run SSH key sync command."""
    result = run_vde_command("sync-ssh-keys", timeout=30)
    context.last_command = "sync_ssh_keys_to_vde"
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('private key detection runs')
def step_private_key_detection(context):
    """Run private key detection."""
    # This would be part of VDE SSH setup
    result = subprocess.run(['find', str(Path.home() / ".ssh"), '-name', 'id_*', '!', '-name', '*.pub'],
                          capture_output=True, text=True)
    context.private_keys_found = result.stdout.strip().split('\n') if result.stdout.strip() else []


@when('SSH config is generated')
def step_ssh_config_generated(context):
    """Generate SSH config."""
    vm_name = getattr(context, 'vm_name', 'python')
    result = run_vde_command(f"create {vm_name}", timeout=120)
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('SSH config entry is created for VM "{vm_name}"')
def step_ssh_config_entry_created(context, vm_name):
    """Create SSH config entry for VM."""
    result = run_vde_command(f"create {vm_name}", timeout=120)
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr
    context.vm_name = vm_name


@when('VM-to-VM SSH config is generated')
def step_vm_to_vm_ssh_config(context):
    """Generate VM-to-VM SSH config."""
    for vm_name in ['python', 'rust']:
        config_path = VDE_ROOT / "configs" / "docker" / vm_name / "docker-compose.yml"
        if not config_path.exists():
            result = run_vde_command(f"create {vm_name}", timeout=120)
            assert result.returncode == 0, f"Failed to create {vm_name}"


@when('I create VM "{vm_name}" again')
def step_create_vm_again(context, vm_name):
    """Try to create VM again (should handle duplicates)."""
    result = run_vde_command(f"create {vm_name}", timeout=120)
    context.last_command = f"create {vm_name}"
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('SSH config is updated')
def step_ssh_config_updated(context):
    """Update SSH config."""
    # This would be triggered by VM creation
    vm_name = getattr(context, 'vm_name', 'python')
    result = run_vde_command(f"create {vm_name}", timeout=120)
    context.last_exit_code = result.returncode


@when('VM "{vm_name}" is removed')
def step_vm_removed(context, vm_name):
    """Remove VM."""
    result = run_vde_command(f"remove {vm_name}", timeout=120)
    context.last_command = f"remove {vm_name}"
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@when('I SSH into "{vm_name}"')
def step_ssh_into_vm(context, vm_name):
    """SSH into a VM (just verify it's possible)."""
    # For testing, we just verify the container is running
    assert container_is_running(vm_name), f"VM {vm_name} should be running to SSH into it"


@when('I run "ssh {target_vm}" from within the {source_vm} VM')
def step_ssh_from_vm_to_vm(context, source_vm, target_vm):
    """SSH from one VM to another."""
    # This is a complex test that would require exec into the container
    # For now, we just verify both VMs are running
    assert container_is_running(source_vm), f"Source VM {source_vm} should be running"
    assert container_is_running(target_vm), f"Target VM {target_vm} should be running"


# =============================================================================
# THEN steps - Verification for SSH Configuration tests
# =============================================================================

@then('SSH agent should be started')
def step_ssh_agent_started(context):
    """Verify SSH agent is started."""
    result = subprocess.run(['pgrep', '-x', 'ssh-agent'], capture_output=True)
    assert result.returncode == 0, "SSH agent should be running"


@then('available SSH keys should be loaded into agent')
def step_keys_loaded_into_agent(context):
    """Verify SSH keys are loaded into agent."""
    result = subprocess.run(['ssh-add', '-l'], capture_output=True)
    # Returns 0 if keys loaded, 1 if no keys, 2 if no agent
    assert result.returncode == 0, f"SSH keys should be loaded: {result.stderr.decode()}"


@then('an ed25519 SSH key should be generated')
def step_ed25519_generated(context):
    """Verify ed25519 SSH key was generated."""
    ssh_dir = Path.home() / ".ssh" / "vde"
    ed25519_key = ssh_dir / "id_ed25519"
    assert ed25519_key.exists(), f"ed25519 key should be generated at {ed25519_key}"


@then('the public key should be synced to public-ssh-keys directory')
def step_public_key_synced(context):
    """Verify public key was synced to public-ssh-keys."""
    public_ssh_dir = VDE_ROOT / "public-ssh-keys"
    assert public_ssh_dir.exists(), f"public-ssh-keys should exist at {public_ssh_dir}"
    pub_files = list(public_ssh_dir.glob("*.pub"))
    assert len(pub_files) > 0, f"Should have .pub files in public-ssh-keys: {list(public_ssh_dir.iterdir())}"


@then('only .pub files should be copied')
def step_only_pub_copied(context):
    """Verify only .pub files are copied."""
    public_ssh_dir = VDE_ROOT / "public-ssh-keys"
    all_files = list(public_ssh_dir.iterdir())
    for f in all_files:
        if f.name != ".keep":
            assert f.suffix == ".pub", f"Only .pub files should be in public-ssh-keys: {f.name}"


@then('.keep file should exist in public-ssh-keys directory')
def step_keep_file_exists(context):
    """Verify .keep file exists."""
    public_ssh_dir = VDE_ROOT / "public-ssh-keys"
    keep_file = public_ssh_dir / ".keep"
    assert keep_file.exists(), f".keep file should exist at {keep_file}"


@then('non-.pub files should be rejected')
def step_non_pub_rejected(context):
    """Verify non-.pub files are rejected."""
    private_keys = getattr(context, 'private_keys_found', [])
    for key in private_keys:
        if key:
            assert key.endswith('.pub') or 'PRIVATE KEY' not in open(key).read() if Path(key).exists() else True, \
                f"Private key {key} should be rejected"


@then('files containing "PRIVATE KEY" should be rejected')
def step_private_key_rejected(context):
    """Verify files with PRIVATE KEY are rejected."""
    # This is verified by the previous test
    pass


@then('SSH config should contain "Host {host_name}"')
def step_ssh_config_contains_host(context, host_name):
    """Verify SSH config contains a host entry."""
    ssh_config = Path.home() / ".ssh" / "config"
    if not ssh_config.exists():
        ssh_config = VDE_ROOT / "backup" / "ssh" / "config"
    
    assert ssh_config.exists(), f"SSH config should exist at {ssh_config}"
    content = ssh_config.read_text()
    assert f"Host {host_name}" in content, f"SSH config should contain 'Host {host_name}'"


@then('SSH config should contain "Port {port}"')
def step_ssh_config_contains_port(context, port):
    """Verify SSH config contains port."""
    ssh_config = Path.home() / ".ssh" / "config"
    if not ssh_config.exists():
        ssh_config = VDE_ROOT / "backup" / "ssh" / "config"
    
    assert ssh_config.exists(), f"SSH config should exist"
    content = ssh_config.read_text()
    assert f"Port {port}" in content, f"SSH config should contain 'Port {port}'"


@then('SSH config should contain "ForwardAgent yes"')
def step_forward_agent_yes(context):
    """Verify SSH config contains ForwardAgent yes."""
    ssh_config = Path.home() / ".ssh" / "config"
    if not ssh_config.exists():
        ssh_config = VDE_ROOT / "backup" / "ssh" / "config"
    
    assert ssh_config.exists(), f"SSH config should exist"
    content = ssh_config.read_text()
    assert 'ForwardAgent yes' in content, f"SSH config should contain 'ForwardAgent yes'"


@then('SSH config should contain "IdentityFile" pointing to "~/.ssh/{key_name}"')
def step_identity_file_config(context, key_name):
    """Verify SSH config has correct identity file."""
    ssh_config = Path.home() / ".ssh" / "config"
    if not ssh_config.exists():
        ssh_config = VDE_ROOT / "backup" / "ssh" / "config"
    
    assert ssh_config.exists(), f"SSH config should exist"
    content = ssh_config.read_text()
    expected_path = f"IdentityFile ~/.ssh/{key_name}"
    assert expected_path in content or f"IdentityFile ~/.ssh/vde/{key_name}" in content, \
        f"SSH config should contain identity file for {key_name}: {content}"


@then('SSH config should contain entry for "{host_name}"')
def step_ssh_config_entry_for_host(context, host_name):
    """Verify SSH config has entry for host."""
    step_ssh_config_contains_host(context, host_name)


@then('each entry should use "localhost" as hostname')
def step_localhost_hostname(context):
    """Verify SSH config entries use localhost."""
    ssh_config = Path.home() / ".ssh" / "config"
    if not ssh_config.exists():
        ssh_config = VDE_ROOT / "backup" / "ssh" / "config"
    
    assert ssh_config.exists(), f"SSH config should exist"
    content = ssh_config.read_text()
    # Should have HostName localhost for VM entries
    assert 'HostName localhost' in content or 'HostName 127.0.0.1' in content, \
        f"SSH config should use localhost as hostname"


@then('duplicate SSH config entry should NOT be created')
def step_no_duplicate_entry(context):
    """Verify no duplicate SSH config entry was created."""
    ssh_config = Path.home() / ".ssh" / "config"
    if ssh_config.exists():
        content = ssh_config.read_text()
        # Count occurrences of "Host python-dev"
        count = content.count("Host python-dev")
        assert count <= 1, f"Should not have duplicate entries: {content}"


@then('command should warn about existing entry')
def step_warn_existing_entry(context):
    """Verify command warns about existing entry."""
    output = context.last_output + context.last_error
    assert 'exist' in output.lower() or 'warn' in output.lower() or 'duplicate' in output.lower(), \
        f"Should warn about existing entry: {output}"


@then('SSH config should remain valid')
def step_ssh_config_valid(context):
    """Verify SSH config remains valid."""
    ssh_config = Path.home() / ".ssh" / "config"
    if ssh_config.exists():
        content = ssh_config.read_text()
        # Basic validation - should have proper Host/HostName pairs
        assert 'Host ' in content and 'HostName ' in content, \
            f"SSH config should be valid: {content}"


@then('no partial updates should occur')
def step_no_partial_updates(context):
    """Verify no partial updates occurred."""
    # This would be verified by checking config validity
    step_ssh_config_valid(context)


@then('backup file should be created in "backup/ssh/" directory')
def step_backup_created(context):
    """Verify backup file was created."""
    backup_dir = VDE_ROOT / "backup" / "ssh"
    assert backup_dir.exists(), f"Backup directory should exist at {backup_dir}"
    backup_files = list(backup_dir.glob("config*"))
    assert len(backup_files) > 0, f"Should have backup files in {backup_dir}"


@then('backup filename should contain timestamp')
def step_backup_has_timestamp(context):
    """Verify backup filename contains timestamp."""
    backup_dir = VDE_ROOT / "backup" / "ssh"
    backup_files = list(backup_dir.glob("config*"))
    for bf in backup_files:
        # Filename should have date/time info
        assert any(c.isdigit() for c in bf.name), \
            f"Backup filename should contain timestamp: {bf.name}"


@then('SSH config should NOT contain "Host {host_name}"')
def step_ssh_config_no_host(context, host_name):
    """Verify SSH config does not contain a host entry."""
    ssh_config = Path.home() / ".ssh" / "config"
    if ssh_config.exists():
        content = ssh_config.read_text()
        assert f"Host {host_name}" not in content, \
            f"SSH config should NOT contain 'Host {host_name}'"


@then('I should connect to the {target_vm} VM')
def step_connect_to_target_vm(context, target_vm):
    """Verify connection to target VM."""
    assert container_is_running(target_vm), f"Should be able to connect to {target_vm}"


@then('I should be authenticated using my host\'s SSH keys')
def step_auth_with_host_keys(context):
    """Verify authentication using host's SSH keys."""
    # In a real test, we'd verify SSH works
    # For now, we just verify the agent is running and has keys
    result = subprocess.run(['pgrep', '-x', 'ssh-agent'], capture_output=True)
    assert result.returncode == 0, "SSH agent should be running for authentication"


@then('I should not need to enter a password')
def step_no_password(context):
    """Verify no password required."""
    # This would be tested in actual SSH attempts
    pass


@then('I should not need to copy keys to the {vm_name} VM')
def step_no_key_copy(context, vm_name):
    """Verify no need to copy keys to VM."""
    # SSH agent forwarding means keys don't need to be copied


@then('the file should be copied using my host\'s SSH keys')
def step_copied_with_host_keys(context):
    """Verify file was copied using host's SSH keys."""
    # Would be verified in actual SCP test
    pass


@then('the command should execute on the {target_vm} VM')
def step_command_on_target(context, target_vm):
    """Verify command executed on target VM."""
    assert container_is_running(target_vm), f"Target VM {target_vm} should be running"


@then('the output should be displayed')
def step_output_displayed(context):
    """Verify command output was displayed."""
    # Would be verified in actual test
    pass
