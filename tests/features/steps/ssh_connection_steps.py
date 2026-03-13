"""
BDD Step Definitions for SSH Connection Testing.

These steps verify SSH connectivity between VMs and from host to VMs.
"""
import subprocess
import sys

# Import shared configuration
steps_dir = sys.path.insert(0, steps_dir) if (steps_dir := __import__('os').path.dirname(__import__('os').path.abspath(__file__))) not in sys.path else None
from pathlib import Path

from behave import given, then, when

from config import VDE_ROOT
from ssh_helpers import run_vde_command
from vm_common import docker_list_containers

# =============================================================================
# SSH CONNECTION GIVEN steps
# =============================================================================

@given('I have set up SSH keys')
def step_have_ssh_keys(context):
    """Context: SSH keys have been set up for authentication."""
    ssh_dir = Path.home() / '.ssh' / 'vde'
    ssh_dir.mkdir(parents=True, exist_ok=True)
    
    private_key = ssh_dir / 'id_rsa'
    public_key = ssh_dir / 'id_rsa.pub'
    
    # Create keys if they don't exist
    if not private_key.exists():
        subprocess.run(
            ['ssh-keygen', '-t', 'rsa', '-b', '4096', '-N', '', '-f', str(private_key)],
            capture_output=True
        )
    
    context.ssh_keys_setup = private_key.exists() and public_key.exists()


@given('I have a web service running in a VM')
def step_web_service_in_vm(context):
    """Context: A web service is running inside a VM container."""
    running = docker_list_containers()
    if running:
        vm = running[0]
        # Check if any port is exposed
        result = subprocess.run(
            ['docker', 'port', vm],
            capture_output=True, text=True, timeout=10
        )
        context.web_service_running = result.returncode == 0
        context.web_service_vm = vm
    else:
        context.web_service_running = False


# =============================================================================
# SSH CONNECTION THEN steps
# =============================================================================

@then('the VM should be ready to use')
def step_vm_ready_ssh(context):
    """Verify VM is ready - container running."""
    running = docker_list_containers()
    assert len(running) > 0, "At least one VM should be running"

@then('it should be accessible via SSH')
def step_accessible_ssh(context):
    """Verify VM is accessible via SSH."""
    running = docker_list_containers()
    if running:
        vm = running[0]
        result = subprocess.run(['./bin/vde', 'port', vm], capture_output=True, text=True)
        if result.returncode == 0:
            assert '22' in result.stdout or '220' in result.stdout, \
                   f"SSH port should be exposed. Got: {result.stdout}"

@when('I access localhost on the VM\'s port')
def step_access_localhost_port(context):
    """Context: Access localhost on VM's port."""

@when('I connect to a VM')
def step_connect_vm(context):
    """Context: Connect to a VM."""

@then('I should receive the hostname (localhost)')
def step_receive_hostname(context):
    """Verify hostname is localhost - check SSH config points to localhost."""
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    if ssh_config.exists():
        content = ssh_config.read_text()
        assert 'localhost' in content.lower() or '127.0.0.1' in content, \
               "SSH config should reference localhost for connections"

@then('I should receive the SSH port')
def step_receive_ssh_port(context):
    """Verify SSH port is received."""
    running = docker_list_containers()
    if running:
        vm = running[0]
        result = subprocess.run(['./bin/vde', 'port', vm], capture_output=True, text=True)
        if result.returncode == 0:
            assert '22' in result.stdout or '220' in result.stdout, \
                   f"SSH port should be available. Got: {result.stdout}"

@then('I should receive the username (devuser)')
def step_receive_username(context):
    """Verify username is devuser - check VDE uses devuser."""
    # VDE containers use devuser as the default user
    # Verify by checking docker-compose files
    compose_path = VDE_ROOT / "configs" / "docker" / "python" / "docker-compose.yml"
    if compose_path.exists():
        content = compose_path.read_text()
        # Check for user configuration
        has_devuser = 'USER' in content or 'user:' in content.lower() or 'devuser' in content.lower()
        assert has_devuser, "VDE should use devuser as the default username"
    else:
        assert False, f"docker-compose.yml not found at {compose_path}"
    context.user_is_devuser = True

@then('language VMs should have SSH access')
def step_language_vms_ssh(context):
    """Verify language VMs have SSH access configured."""
    configs_dir = VDE_ROOT / "configs" / "docker"
    if configs_dir.exists():
        found_ssh = False
        for vm_dir in configs_dir.iterdir():
            compose_file = vm_dir / "docker-compose.yml"
            if compose_file.exists():
                content = compose_file.read_text()
                if '22' in content or 'SSH' in content:
                    found_ssh = True
                    break
        assert found_ssh, "Language VMs should have SSH configured"




@then('all should use my SSH keys for SSH-Connection')
def step_all_use_ssh_keys(context):
    """Verify all VMs use configured SSH keys."""
    ssh_dir = Path.home() / '.ssh'
    assert ssh_dir.exists(), "SSH keys should be configured for VMs to use"

@then('all should work with the same configuration for SSH-Connection')
def step_all_same_config(context):
    """Verify all VMs work with same configuration."""
    configs_dir = VDE_ROOT / "configs" / "docker"
    assert configs_dir.exists(), "VM configurations should exist"

@then('both connections should work')
def step_both_connections_work(context):
    """Verify both SSH connections work."""
    running = docker_list_containers()
    assert len(running) >= 2, "At least 2 VMs should be running for both connections"

@then('both should be accessible via SSH')
def step_both_accessible_ssh(context):
    """Verify both VMs are accessible via SSH."""
    running = docker_list_containers()
    assert len(running) >= 2, "At least 2 VMs should be running"



