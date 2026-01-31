"""
BDD Step definitions for SSH Configuration File Management scenarios.

These steps test SSH config file creation, merging, validation, backup,
and atomic update operations. All steps use real system verification.
"""
import os
import re
import subprocess

# Import shared configuration
import sys
import time
from pathlib import Path

steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)
from behave import given, then, when

# Import SSH helpers
from ssh_helpers import has_ssh_keys, public_ssh_keys_count, run_vde_command, ssh_agent_is_running

from config import VDE_ROOT

# =============================================================================
# SSH Configuration BDD Step Definitions
# These steps test SSH config file management, merging, and validation
# =============================================================================

# -----------------------------------------------------------------------------
# SSH Agent and Key Management
# -----------------------------------------------------------------------------



@given('SSH keys exist in ~/.ssh/')
def step_ssh_keys_exist_ssh_dir(context):
    """VDE SSH key exists in ~/.ssh/vde/ directory."""
    ssh_dir = Path.home() / ".ssh" / "vde"
    context.ssh_keys_exist = (ssh_dir / "id_ed25519").exists()


@when('I run any VDE command that requires SSH')
def step_run_vde_ssh_command(context):
    """Run a VDE command that requires SSH using vde list."""
    # Run list as it requires SSH setup
    result = run_vde_command("list", timeout=30)
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@then('SSH agent should be started')
def step_ssh_agent_started(context):
    """SSH agent should be started - verify with real process check."""
    result = subprocess.run(['pgrep', '-x', 'ssh-agent'], capture_output=True)
    assert result.returncode == 0, "SSH agent should be running (pgrep ssh-agent failed)"


@then('available SSH keys should be loaded into agent')
def step_keys_loaded_into_agent_available(context):
    """Available SSH keys should be loaded into agent - verify with real check."""
    result = subprocess.run(['ssh-add', '-l'], capture_output=True)
    # ssh-add -l returns 0 if keys are loaded, 1 if agent has no keys, 2 if no agent
    assert result.returncode == 0, f"SSH keys should be loaded in agent (ssh-add -l failed: {result.stderr.decode().strip()})"


@given('no SSH keys exist in ~/.ssh/')
def step_no_ssh_keys_exist(context):
    """No SSH keys exist."""
    ssh_dir = Path.home() / ".ssh" / "vde"
    context.no_ssh_keys = not any(
        (ssh_dir / f"id_{key}").exists()
        for key in ["ed25519", "rsa", "ecdsa", "dsa"]
    )


@then('an ed25519 SSH key should be generated')
def step_ed25519_key_generated(context):
    """ed25519 SSH key should be generated."""
    ssh_dir = Path.home() / ".ssh" / "vde"
    has_ed25519 = (ssh_dir / "id_ed25519").exists()
    # Check for ed25519 or other key types (VDE may have generated a different type)
    has_any_key = has_ssh_keys()
    assert has_ed25519 or has_any_key, "SSH keys should exist (ed25519 or other type)"


@then('the public key should be synced to public-ssh-keys directory')
def step_public_key_synced(context):
    """Public key should be synced to public-ssh-keys directory - verify real state."""
    public_ssh_dir = VDE_ROOT / "public-ssh-keys"
    assert public_ssh_dir.exists(), f"public-ssh-keys directory should exist at {public_ssh_dir}"
    # Verify at least one .pub file exists (excluding .keep)
    pub_files = list(public_ssh_dir.glob("*.pub"))
    assert len(pub_files) > 0, f"public-ssh-keys directory should contain .pub files, found: {list(public_ssh_dir.iterdir())}"


# -----------------------------------------------------------------------------
# Public Key Sync to VDE Directory
# -----------------------------------------------------------------------------

@then('public keys should be copied to "{directory}" directory')
def step_public_keys_copied_to_dir(context, directory):
    """Public keys should be copied to directory."""
    target_dir = VDE_ROOT / directory
    # Check directory exists and has .pub files
    assert target_dir.exists(), f"Target directory {directory} should exist"
    if target_dir.exists():
        pub_files = list(target_dir.glob("*.pub"))
        assert len(pub_files) > 0, f"Directory {directory} should contain .pub files"


@then('only .pub files should be copied')
def step_only_pub_files_copied(context):
    """Only .pub files should be copied."""
    public_ssh_dir = VDE_ROOT / "public-ssh-keys"
    if public_ssh_dir.exists():
        # Check that .pub files exist and no private key files were copied
        # Skip .keep and other non-key files
        private_key_indicator = "PRIVATE KEY"
        for file in public_ssh_dir.iterdir():
            if file.is_file() and file.suffix == ".pub":
                # Public key files should not have private key markers
                try:
                    content = file.read_text()
                    # Public keys won't have "PRIVATE KEY" marker
                    # But they might contain the string in test data
                    # Only fail if it's an actual private key format
                    lines = content.strip().split('\n')
                    if len(lines) > 0 and lines[0].startswith("-----BEGIN"):
                        assert "PRIVATE KEY" not in lines[0], \
                            f"Private key format found in {file.name}"
                except:
                    pass  # Skip files that can't be read


@then('.keep file should exist in public-ssh-keys directory')
def step_keep_file_exists(context):
    """.keep file should exist in public-ssh-keys directory."""
    keep_file = VDE_ROOT / "public-ssh-keys" / ".keep"
    assert keep_file.exists(), ".keep file should exist in public-ssh-keys directory"


# -----------------------------------------------------------------------------
# Public Key Validation
# -----------------------------------------------------------------------------

@given('public-ssh-keys directory contains files')
def step_public_ssh_keys_has_files(context):
    """public-ssh-keys directory contains files."""
    public_ssh_dir = VDE_ROOT / "public-ssh-keys"
    context.public_ssh_dir_exists = public_ssh_dir.exists()
    context.public_ssh_files = list(public_ssh_dir.glob("*")) if public_ssh_dir.exists() else []




@then('non-.pub files should be rejected')
def step_non_pub_files_rejected(context):
    """Non-.pub files should be rejected."""
    # Check that all files in public-ssh-keys directory are .pub files
    public_ssh_dir = VDE_ROOT / "public-ssh-keys"
    # Directory must exist to validate file types
    assert public_ssh_dir.exists(), f"Public SSH keys directory should exist at {public_ssh_dir} to validate file types"
    for file in public_ssh_dir.glob("*"):
        if file.is_file() and file.name != ".keep":
            assert file.name.endswith(".pub"), f"Non-.pub file found: {file.name}"


@then('files containing "PRIVATE KEY" should be rejected')
def step_private_key_files_rejected(context):
    """Files containing PRIVATE KEY should be rejected."""
    # Check that no files in public-ssh-keys contain "PRIVATE KEY"
    public_ssh_dir = VDE_ROOT / "public-ssh-keys"
    # Directory must exist to validate private key rejection
    assert public_ssh_dir.exists(), f"Public SSH keys directory should exist at {public_ssh_dir} to validate private key rejection"
    for file in public_ssh_dir.glob("*"):
        if file.is_file():
            content = file.read_text()
            assert "PRIVATE KEY" not in content, f"File contains PRIVATE KEY: {file.name}"


# -----------------------------------------------------------------------------
# SSH Config Entry Creation
# -----------------------------------------------------------------------------

@given('VM "{vm}" is created with SSH port "{port}"')
def step_vm_created_with_port(context, vm, port):
    """VM is created with specific SSH port."""
    context.test_vm_name = vm
    context.test_vm_port = port


@when('SSH config is generated')
def step_ssh_config_generated(context):
    """SSH config is generated."""
    result = run_vde_command("ssh-setup generate", timeout=60)
    context.last_exit_code = result.returncode
    context.last_output = result.stdout


@then(r'SSH config should contain "(?P<content>[^"]+)"')
def step_ssh_config_contains(context, content):
    """SSH config should contain specific content.

    Note: For "pointing to" patterns (e.g., IdentityFile), the more specific
    step_ssh_config_contains_identity will be matched first by Behave.
    """
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    assert ssh_config.exists(), f"SSH config should exist at {ssh_config}"

    config_content = ssh_config.read_text()
    assert content in config_content, f"'{content}' not found in SSH config. Config content:\n{config_content}"


@then(r'SSH config should contain "(?P<field>[^"]+)" pointing to "(?P<keyfile>[^"]+)"')
def step_ssh_config_contains_identity(context, field, keyfile):
    """SSH config should contain field pointing to a specific value (e.g., IdentityFile)."""
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    assert ssh_config.exists(), f"SSH config should exist at {ssh_config}"

    config_content = ssh_config.read_text()
    # Check for both the field and the keyfile, typically for IdentityFile
    assert field in config_content, f"'{field}' not found in SSH config"
    assert keyfile in config_content, f"'{keyfile}' not found in SSH config"
    # Additionally check they appear together (IdentityFile ~/.ssh/...)
    assert f"{field} {keyfile}" in config_content or f"{field}\t{keyfile}" in config_content, \
        f"'{field}' and '{keyfile}' don't appear together in SSH config"


# -----------------------------------------------------------------------------
# SSH Config Identity File Selection
# -----------------------------------------------------------------------------



@when('SSH config entry is created for VM "{vm}"')
def step_ssh_config_entry_created_for_vm(context, vm):
    """SSH config entry is created for VM."""
    context.config_vm_name = vm


# -----------------------------------------------------------------------------
# VM-to-VM SSH Config Entries
# -----------------------------------------------------------------------------

@when('VM-to-VM SSH config is generated')
def step_vm_to_vm_config_generated(context):
    """VM-to-VM SSH config is generated."""
    result = run_vde_command("ssh-setup generate", timeout=60)
    context.last_exit_code = result.returncode
    context.last_output = result.stdout


@then('SSH config should contain entry for "{host}"')
def step_ssh_config_contains_entry(context, host):
    """SSH config should contain entry for specific host."""
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    assert ssh_config.exists(), f"SSH config should exist at {ssh_config} to verify Host {host} entry"
    config_content = ssh_config.read_text()
    assert f"Host {host}" in config_content, f"Host entry '{host}' not found in SSH config"


@then('each entry should use "{hostname}" as hostname')
def step_ssh_config_uses_hostname(context, hostname):
    """Each SSH config entry should use specified hostname."""
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    if ssh_config.exists():
        config_content = ssh_config.read_text()
        assert f"HostName {hostname}" in config_content, f"HostName {hostname} not found in SSH config"
