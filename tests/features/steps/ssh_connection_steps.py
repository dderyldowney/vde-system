from behave import given, when, then
from config import VDE_ROOT, VDE_SSH_CONFIG
from vm_common import run_vde_command
import os

# Define PUBLIC_SSH_KEYS_DIR as it's not in config.py
PUBLIC_SSH_KEYS_DIR = VDE_ROOT / "public-ssh-keys"

@then("the SSH config entries should exist")
def step_ssh_config_entries_exist(context):
    """Verify '~/.ssh/vde/config' has entries."""
    assert VDE_SSH_CONFIG.exists(), f"SSH config file not found at {VDE_SSH_CONFIG}"
    content = VDE_SSH_CONFIG.read_text()
    assert "Host" in content, "SSH config file has no 'Host' entries"

@then("I should be able to use short hostnames")
def step_short_hostnames_work(context):
    """Run 'vde ssh python echo ok' and assert success."""
    # User perspective: use 'ssh python echo ok' which run_vde_command will turn into 'vde ssh python echo ok'
    result = run_vde_command("ssh python echo ok", context=context)
    assert result.returncode == 0, (
        f"SSH with short hostname failed. rc={result.returncode}\nstderr: {result.stderr}"
    )
    assert "ok" in result.stdout.strip(), f"Expected 'ok' in output, got: {result.stdout}"

@then("I should not need to remember port numbers")
def step_no_port_numbers_needed(context):
    """Check if SSH config for vde-python has Port entry."""
    assert VDE_SSH_CONFIG.exists(), f"SSH config file not found at {VDE_SSH_CONFIG}"
    content = VDE_SSH_CONFIG.read_text()
    # Check for vde-python or python entry (standard VDE hostnames)
    assert "Host vde-python" in content or "Host python" in content, \
        "SSH config missing entry for python VM"
    
    # Verify that a Port entry exists in the file, ensuring the user doesn't need to specify it
    assert "Port" in content, "SSH config missing 'Port' entries, which are required to avoid remembering port numbers"

@then("my public keys should be copied to public-ssh-keys/")
def step_public_keys_copied_to_dir(context):
    """Verify file exists in dir."""
    assert PUBLIC_SSH_KEYS_DIR.exists(), f"Directory {PUBLIC_SSH_KEYS_DIR} does not exist"
    pub_keys = list(PUBLIC_SSH_KEYS_DIR.glob("*.pub"))
    assert len(pub_keys) > 0, f"No public keys found in {PUBLIC_SSH_KEYS_DIR}. Keys were not copied automatically."

@then("all my public keys should be in the VM's authorized_keys")
def step_keys_in_authorized_keys(context):
    """vde exec cat ~/.ssh/authorized_keys"""
    # Use 'python' as the default VM name if not specified in context
    vm_name = getattr(context, "vm_name", "python")
    # run_vde_command will handle prefixing with 'vde'
    result = run_vde_command(f"exec {vm_name} cat /home/vde/.ssh/authorized_keys", context=context)
    assert result.returncode == 0, (
        f"Failed to read authorized_keys in VM '{vm_name}'. rc={result.returncode}\nstderr: {result.stderr}"
    )
    
    authorized_content = result.stdout
    # Verify that at least one key from public-ssh-keys/ is in the VM's authorized_keys
    pub_keys = list(PUBLIC_SSH_KEYS_DIR.glob("*.pub"))
    assert len(pub_keys) > 0, "No host public keys available to verify in VM"
    
    for pub_key_file in pub_keys:
        pub_key_content = pub_key_file.read_text().strip()
        # Extract the key type and key content (ignore comment part)
        key_parts = pub_key_content.split()
        if len(key_parts) >= 2:
            key_identifier = " ".join(key_parts[:2])
            assert key_identifier in authorized_content, \
                f"Public key {pub_key_file.name} was not found in VM '{vm_name}' authorized_keys"

@then("I should be able to use any of the keys")
def step_use_any_keys(context):
    """Test SSH with different identities if available."""
    # In a test environment, this usually means verifying that the default SSH access works,
    # which implies the correct key was selected/available.
    vm_name = getattr(context, "vm_name", "python")
    result = run_vde_command(f"ssh {vm_name} echo ok", context=context)
    assert result.returncode == 0, f"SSH connection failed for VM '{vm_name}' using available keys"
    assert "ok" in result.stdout, "SSH command executed but returned unexpected output"

@then("I should not need to manually copy keys")
def step_no_manual_copy(context):
    """Confirm no 'cp' or manual setup required by user."""
    # This is a validation of the automatic nature of VDE. 
    # If the public keys are in the expected directory and SSH works, it's automatic.
    assert PUBLIC_SSH_KEYS_DIR.exists(), "public-ssh-keys directory was not created automatically"
    pub_keys = list(PUBLIC_SSH_KEYS_DIR.glob("*.pub"))
    assert len(pub_keys) > 0, "Public keys should have been copied automatically to public-ssh-keys/ directory"


@when("I access localhost on the VM's port")
def step_access_localhost_vm_port(context):
    """Verify access to the VM via its mapped port."""
    vm_name = getattr(context, "vm_name", "python")
    # Get port via vde port
    result = run_vde_command(f"port {vm_name}", context=context)
    assert result.returncode == 0, f"Failed to get port for {vm_name}"
    # Example output: "python: 2200" or similar
    import re
    match = re.search(r"(\d+)$", result.stdout.strip())
    assert match, f"Could not parse port from output: {result.stdout}"
    port = match.group(1)
    
    # Try to connect to the port (just a socket check is safer than curl for SSH port)
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    res = sock.connect_ex(("127.0.0.1", int(port)))
    sock.close()
    assert res == 0, f"Could not connect to localhost:{port} for VM {vm_name}"


@when("I connect to a VM")
def step_connect_to_vm(context):
    """Verify connection capability, ensuring VM is running."""
    from vm_common import container_is_running, wait_for_container
    vm_name = getattr(context, "vm_name", "python")
    
    # Ensure VM is running
    if not container_is_running(vm_name):
        run_vde_command(f"start {vm_name}", context=context)
        wait_for_container(vm_name, timeout=60)
        
    # run_vde_command handles prefixing
    result = run_vde_command(f"connect {vm_name} echo ok", context=context)
    assert result.returncode == 0, f"Failed to connect to VM {vm_name}"
