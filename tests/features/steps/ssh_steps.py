"""
BDD Step definitions for SSH Key Management.

These steps handle SSH key verification, agent management, and SSH operations.
"""

import os
import subprocess
from pathlib import Path

from behave import given, then, when


# =============================================================================
# GIVEN steps - Setup SSH states
# =============================================================================

@given('SSH agent is running')
def step_ssh_agent_running(context):
    """Verify SSH agent is available and running."""
    result = subprocess.run(
        ['ssh-add', '-l'],
        capture_output=True,
        text=True
    )

    # ssh-add returns 0 if keys are loaded, 1 if no keys, 2 if agent not running
    context.ssh_agent_running = result.returncode in [0, 1]

    if result.returncode == 2:
        # Try to start SSH agent
        raise AssertionError("SSH agent is not running")


@given('SSH agent is not running')
def step_ssh_agent_not_running(context):
    """Ensure SSH agent is not running."""
    result = subprocess.run(
        ['ssh-add', '-l'],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        # Agent has keys, kill it
        subprocess.run(['ssh-agent', '-k'], capture_output=True)


@given('available SSH keys should be loaded into agent')
def step_ssh_keys_loaded(context):
    """Verify SSH keys are loaded into the agent."""
    result = subprocess.run(
        ['ssh-add', '-l'],
        capture_output=True,
        text=True
    )

    has_keys = result.returncode == 0
    assert has_keys, f"No SSH keys loaded in agent: {result.stderr}"


@when('I load SSH key "{key_name}"')
def step_load_ssh_key(context, key_name):
    """Load an SSH key into the agent."""
    key_path = os.path.expanduser(f'~/.ssh/{key_name}')

    assert os.path.exists(key_path), f"SSH key '{key_name}' not found"

    result = subprocess.run(
        ['ssh-add', key_path],
        capture_output=True,
        text=True
    )

    context.ssh_key_loaded = result.returncode == 0
    context.loaded_key = key_name

    if result.returncode != 0:
        context.last_error = result.stderr


# =============================================================================
# THEN steps - SSH verification
# =============================================================================

@then('public key "{key_name}" should be available')
def step_public_key_available(context, key_name):
    """Verify public key file exists."""
    key_path = os.path.expanduser(f'~/.ssh/{key_name}')
    assert os.path.exists(key_path), f"Public key {key_name} not found at {key_path}"


@then('public key "{key_name}" should not be available')
def step_public_key_not_available(context, key_name):
    """Verify public key file doesn't exist."""
    key_path = os.path.expanduser(f'~/.ssh/{key_name}')
    assert not os.path.exists(key_path), f"Public key {key_name} should not exist"


@then('SSH key "{key_name}" should be loaded')
def step_ssh_key_should_be_loaded(context, key_name):
    """Verify specific SSH key is loaded in agent."""
    result = subprocess.run(
        ['ssh-add', '-l'],
        capture_output=True,
        text=True
    )

    # Check if key fingerprint is in output
    key_loaded = key_name in result.stdout or key_name.replace('.pub', '') in result.stdout
    assert key_loaded, f"SSH key '{key_name}' is not loaded in agent"


@then('SSH agent should have {count} key')
def step_ssh_agent_key_count(context, count):
    """Verify SSH agent has expected number of keys loaded."""
    result = subprocess.run(
        ['ssh-add', '-l'],
        capture_output=True,
        text=True
    )

    # Count lines in output (each line is a key)
    key_count = len([l for l in result.stdout.strip().split('\n') if l])
    expected = int(count)

    assert key_count == expected, \
        f"SSH agent should have {expected} keys, has {key_count}"


@then('I should be able to SSH to VM "{vm_name}"')
def step_ssh_to_vm(context, vm_name):
    """Verify SSH connection to VM works."""
    from docker_helpers import get_container_port

    try:
        port = get_container_port(f'{vm_name}-dev', 22)
        context.vm_ssh_port = port

        # Quick connection test (don't actually connect, just verify port is open)
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        try:
            result = sock.connect_ex(('localhost', port))
            assert result == 0, f"Cannot connect to SSH port {port}"
        finally:
            sock.close()

    except Exception as e:
        raise AssertionError(f"Cannot SSH to VM '{vm_name}': {e}")


@then('SSH config should contain host "{host}"')
def step_ssh_config_contains_host(context, host):
    """Verify SSH config contains specified host."""
    ssh_config = os.path.expanduser('~/.ssh/config')

    if not os.path.exists(ssh_config):
        raise AssertionError(f"SSH config not found at {ssh_config}")

    with open(ssh_config, 'r') as f:
        config_content = f.read()

    assert host in config_content, f"SSH config should contain host '{host}'"


@then('SSH connection to "{host}" should use key "{key_name}"')
def step_ssh_connection_uses_key(context, host, key_name):
    """Verify SSH config uses specific key for host."""
    ssh_config = os.path.expanduser('~/.ssh/config')

    if not os.path.exists(ssh_config):
        raise AssertionError(f"SSH config not found at {ssh_config}")

    with open(ssh_config, 'r') as f:
        config_content = f.read()

    # Check for host block containing both host and identity file
    import re
    host_pattern = rf'Host {host}.?.*?IdentityFile.*?{key_name}'
    match = re.search(host_pattern, config_content, re.DOTALL | re.IGNORECASE)

    assert match, f"SSH config should use key '{key_name}' for host '{host}'"


# =============================================================================
# WHEN steps - SSH operations
# =============================================================================

@when('I list loaded SSH keys')
def step_list_loaded_ssh_keys(context):
    """List all SSH keys currently loaded in the agent."""
    result = subprocess.run(
        ['ssh-add', '-l'],
        capture_output=True,
        text=True
    )

    context.loaded_ssh_keys = result.stdout


@when('I remove all SSH keys from agent')
def step_remove_all_ssh_keys(context):
    """Remove all keys from SSH agent."""
    subprocess.run(
        ['ssh-add', '-D'],
        capture_output=True,
        text=True
    )

    # Verify keys are removed
    result = subprocess.run(
        ['ssh-add', '-l'],
        capture_output=True,
        text=True
    )

    context.ssh_keys_removed = 'no identities' in result.stderr or result.returncode == 1
