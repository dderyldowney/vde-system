# -*- coding: utf-8 -*-
"""
SSH Remote Access Step Definitions for VDE Behave Tests.

This module implements steps for verifying remote access tools like system SSH,
OpenSSH clients, and VSCode Remote-SSH.
"""

from behave import when, then
from config import VDE_ROOT, VDE_SSH_CONFIG
from vm_common import run_vde_command
from ssh_helpers import ssh_agent_has_keys
import os

@when("I use the system ssh command")
@when("I use OpenSSH clients")
def step_use_system_ssh(context):
    """Run 'ssh vde-python echo connected' using system ssh."""
    # Use the absolute path to /usr/bin/ssh to ensure we use the system client
    # and bypass any 'vde' aliases or wrappers that run_vde_command might prefix.
    # We specify the VDE-specific config file explicitly.
    ssh_cmd = f"/usr/bin/ssh -F {VDE_SSH_CONFIG} vde-python echo connected"
    result = run_vde_command(ssh_cmd, context=context)
    
    assert result.returncode == 0, (
        f"System SSH command failed for 'vde-python'. rc={result.returncode}\n"
        f"stderr: {result.stderr}\n"
        f"Ensure ~/.ssh/vde/config exists and the VM is running."
    )
    assert "connected" in result.stdout.strip(), (
        f"Expected 'connected' in SSH output, but got: '{result.stdout.strip()}'"
    )

@when("I use VSCode Remote-SSH")
def step_use_vscode_remote_ssh(context):
    """Dry-run check: verify 'vde ssh-setup generate' creates a config VSCode can read."""
    # VSCode Remote-SSH relies on a standard OpenSSH config file with valid Host entries.
    # We verify that VDE's generated config meets these requirements.
    assert VDE_SSH_CONFIG.exists(), f"VDE SSH config file not found at {VDE_SSH_CONFIG}"
    
    content = VDE_SSH_CONFIG.read_text()
    
    # VSCode needs specific host entries and standard SSH directives
    assert "Host vde-python" in content, (
        "SSH config missing 'Host vde-python' entry required for VSCode Remote-SSH discovery"
    )
    assert "HostName" in content, (
        "SSH config missing 'HostName' directive, which VSCode needs to resolve the target"
    )
    assert "User" in content, (
        "SSH config missing 'User' directive for VSCode connection defaults"
    )
    assert "IdentityFile" in content, (
        "SSH config missing 'IdentityFile' directive required for key-based authentication in VSCode"
    )

@then("all should work with the same configuration")
def step_all_work_with_same_config(context):
    """Verify 'ssh -F ~/.ssh/vde/config vde-python echo ok'."""
    # This step verifies that both VDE and manual system tools can use the same
    # configuration file for consistent access.
    ssh_cmd = f"/usr/bin/ssh -F {VDE_SSH_CONFIG} vde-python echo ok"
    result = run_vde_command(ssh_cmd, context=context)
    
    assert result.returncode == 0, (
        f"SSH connection failed using the shared configuration file {VDE_SSH_CONFIG}.\n"
        f"rc={result.returncode}, stderr: {result.stderr}"
    )
    assert "ok" in result.stdout.strip(), (
        f"Expected 'ok' from SSH command, but got: '{result.stdout.strip()}'"
    )

@then("all should use my SSH keys")
def step_all_use_ssh_keys(context):
    """Verify SSH agent has keys and identity is used."""
    # First, verify the prerequisites: SSH agent must have keys loaded
    assert ssh_agent_has_keys(), (
        "No SSH keys found in the SSH agent. VDE remote access depends on key-based authentication."
    )
    
    # Run SSH in verbose mode to inspect the authentication process
    ssh_cmd = f"/usr/bin/ssh -F {VDE_SSH_CONFIG} -v vde-python echo identity-check"
    result = run_vde_command(ssh_cmd, context=context)
    
    # Connection should succeed
    assert result.returncode == 0, (
        f"SSH connection failed during key identity verification. rc={result.returncode}\n"
        f"stderr: {result.stderr}"
    )
    
    # Verify that public key authentication was attempted and used
    debug_output = result.stderr
    auth_success_markers = [
        "Offering public key",
        "Authenticating with public key",
        "Next authentication method: publickey",
        "Authentication succeeded (publickey)"
    ]
    
    found_marker = any(marker in debug_output for marker in auth_success_markers)
    assert found_marker, (
        "SSH did not appear to use public key authentication based on verbose output.\n"
        f"Check the debug output for identity usage:\n{debug_output}"
    )
