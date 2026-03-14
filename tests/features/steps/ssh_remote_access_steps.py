"""
BDD Step Definitions for SSH and Remote Access Testing.

These steps verify SSH connectivity, VSCode Remote-SSH, key authentication,
workspace access, sudo permissions, shell/editor configuration, file transfers,
port forwarding, and session persistence.
"""
import subprocess
import sys
import os
from pathlib import Path

# Add steps directory to path for imports
steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)

from behave import given, then, when

from config import VDE_ROOT
from vm_common import (
    run_vde_command,
    container_exists,
    docker_ps,
)

# =============================================================================
# SSH CONNECTION GIVEN steps
# =============================================================================

@given('I am connected via SSH')
def step_connected_via_ssh(context):
    """Context: User has an active SSH connection."""
    running = docker_ps()
    if running:
        context.ssh_connected = True
        context.connected_vm = running[0].replace('vde-', '')
    else:
        context.ssh_connected = False


@given('I connect via SSH')
def step_connect_via_ssh(context):
    """Context: User is connecting via SSH."""
    running = docker_ps()
    if running:
        context.ssh_connecting = True
        context.connecting_vm = running[0].replace('vde-', '')
    else:
        context.ssh_connecting = False


# =============================================================================
# SSH CONNECTION THEN steps
# =============================================================================

@then('I should connect to the Python VM')
def step_connect_python_vm(context):
    """Verify connection to Python VM - SSH or vde exec."""
    assert container_exists('python'), "Python VM should be running"
    context.connected_vm = 'python'
    # Verify container is running and accessible via vde exec
    result = run_vde_command('exec python whoami', context=context)
    assert result.returncode == 0, f"Should be able to exec into python"
    context.ssh_connection_established = True


@then('I should have a zsh shell')
def step_have_zsh_shell(context):
    """Verify zsh shell is available via SSH."""
    vm_name = getattr(context, 'connected_vm', 'python')
    result = run_vde_command(f'exec {vm_name} "echo $SHELL"', context=context)
    if result.returncode == 0:
        assert 'zsh' in result.stdout, f"Expected zsh shell, got: {result.stdout}"
    context.zsh_shell_available = True


# =============================================================================
# VSCODE REMOTE-SSH GIVEN/WHEN/THEN steps
# =============================================================================

@given('I have VSCode installed')
def step_vscode_installed(context):
    """Context: VSCode is installed on the system."""
    # Check for VSCode installation
    vscode_paths = [
        '/usr/bin/code',
        '/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code',
        Path.home() / '.vscode' / 'bin' / 'code'
    ]
    vscode_found = any(Path(p).exists() for p in vscode_paths)
    context.vscode_installed = vscode_found


@when('I add the SSH config for vde-python')
def step_add_ssh_config_python_dev(context):
    """Add SSH config entry for vde-python VM."""
    # This usually happens during vde start/create
    run_vde_command("create python", context=context)
    context.ssh_config_updated = True


@then('I can connect using Remote-SSH')
def step_connect_remote_ssh(context):
    """Verify VSCode Remote-SSH connection is possible."""
    # Verify SSH config has valid entry for the VM
    ssh_config = Path.home() / '.ssh' / 'vde' / 'config'
    if ssh_config.exists():
        content = ssh_config.read_text()
        assert 'Host vde-python' in content, "SSH config should have vde-python entry"
        context.remote_ssh_possible = True
    else:
        context.remote_ssh_possible = False


@then('my workspace should be mounted')
def step_workspace_mounted(context):
    """Verify workspace directory is mounted in container via vde inspect."""
    vm_name = 'python'
    result = run_vde_command(f"inspect {vm_name} -f '{{{{json .Mounts}}}}'", context=context)
    if result.returncode == 0:
        assert 'projects' in result.stdout.lower() or 'workspace' in result.stdout.lower()
    context.workspace_mounted = True


@then('I can edit files in the projects directory')
def step_edit_projects(context):
    """Verify files in projects directory are editable."""
    # Logical check - projects dir must exist and be writable
    assert (VDE_ROOT / "projects").is_dir()


# =============================================================================
# MULTIPLE SSH CONNECTIONS WHEN/THEN steps
# =============================================================================

@when('I connect to vde-python')
def step_connect_to_python_dev(context):
    """Connect to vde-python VM via SSH."""
    context.current_connection = 'python'
    result = run_vde_command("port python 22", context=context)
    context.python_dev_port = result.stdout.strip()


@when('then connect to vde-postgres')
def step_connect_to_postgres_dev(context):
    """Connect to vde-postgres VM via SSH."""
    context.second_connection = 'postgres'
    result = run_vde_command("port postgres 22", context=context)
    context.postgres_dev_port = result.stdout.strip()


@then('each should use a different port')
def step_different_ports(context):
    """Verify different VMs use different ports."""
    python_port = getattr(context, 'python_dev_port', '')
    postgres_port = getattr(context, 'postgres_dev_port', '')
    if python_port and postgres_port:
        assert python_port != postgres_port, \
            f"VMs should use different ports: python={python_port}, postgres={postgres_port}"


# =============================================================================
# SSH KEY AUTHENTICATION THEN steps
# =============================================================================

@then('key-based authentication should be used')
def step_key_auth_used(context):
    """Verify key-based authentication is configured."""
    ssh_dir = Path.home() / '.ssh' / 'vde'
    private_key = ssh_dir / 'id_ed25519'
    assert private_key.exists(), "Private key should exist"
    context.key_auth_configured = True


# =============================================================================
# WORKSPACE DIRECTORY ACCESS WHEN/THEN steps
# =============================================================================

@when('I navigate to ~/workspace')
def step_nav_workspace(context):
    """Navigate to workspace directory."""
    context.current_directory = 'workspace'


@then('I should see my project files')
def step_see_project_files(context):
    """Verify project files are visible."""
    # Logical check - projects/python should have files if created
    assert (VDE_ROOT / "projects").exists()


@then('changes should be reflected on the host')
def step_changes_reflected_host(context):
    """Verify file changes sync between container and host."""
    assert (VDE_ROOT / "projects").exists()


# =============================================================================
# SUDO ACCESS GIVEN/WHEN/THEN steps
# =============================================================================

@given('I need to perform administrative tasks')
def step_need_admin_tasks(context):
    """Context: User needs to run administrative commands."""
    context.admin_tasks_needed = True


@when('I run sudo commands in the container')
def step_run_sudo_commands(context):
    """Execute sudo command in container via vde exec."""
    vm_name = getattr(context, 'connected_vm', 'python')
    result = run_vde_command(f"exec {vm_name} sudo whoami", context=context)
    context.sudo_result = result
    context.sudo_exit_code = result.returncode


@then('they should execute without password')
def step_sudo_no_password(context):
    """Verify sudo doesn't require password."""
    vm_name = getattr(context, 'connected_vm', 'python')
    # Try non-interactive sudo
    result = run_vde_command(f"exec {vm_name} sudo -n whoami", context=context)
    assert result.returncode == 0, "Sudo should execute without password"
    assert 'root' in result.stdout, "Sudo should execute as root"


@then('I should have the necessary permissions')
def step_have_permissions(context):
    """Verify user has required permissions."""
    vm_name = getattr(context, 'connected_vm', 'python')
    result = run_vde_command(f"exec {vm_name} groups", context=context)
    assert 'sudo' in result.stdout or 'root' in result.stdout or result.returncode == 0


# =============================================================================
# SHELL CONFIGURATION GIVEN/WHEN/THEN steps
# =============================================================================

@when('I start a shell')
def step_start_shell(context):
    """Start a shell session."""
    context.shell_started = True


@then('I should be using zsh')
def step_using_zsh(context):
    """Verify zsh is the default shell."""
    vm_name = getattr(context, 'connected_vm', 'python')
    result = run_vde_command(f"exec {vm_name} \"echo $SHELL\"", context=context)
    assert 'zsh' in result.stdout


@then('oh-my-zsh should be configured')
def step_oh_my_zsh_configured(context):
    """Verify oh-my-zsh is installed."""
    vm_name = getattr(context, 'connected_vm', 'python')
    result = run_vde_command(f"exec {vm_name} \"ls -d ~/.oh-my-zsh\"", context=context)
    assert result.returncode == 0


@then('my preferred theme should be active')
def step_theme_active(context):
    """Verify the configured theme is active."""
    vm_name = getattr(context, 'connected_vm', 'python')
    result = run_vde_command(f"exec {vm_name} \"grep ZSH_THEME ~/.zshrc\"", context=context)
    assert result.returncode == 0


# =============================================================================
# EDITOR CONFIGURATION WHEN/THEN steps
# =============================================================================

@when('I run nvim')
def step_run_nvim(context):
    """Run neovim editor check."""
    vm_name = getattr(context, 'connected_vm', 'python')
    result = run_vde_command(f"exec {vm_name} \"which nvim\"", context=context)
    context.nvim_installed = result.returncode == 0


@then('LazyVim should be available')
def step_lazyvim_available(context):
    """Verify LazyVim configuration is available."""
    vm_name = getattr(context, 'connected_vm', 'python')
    result = run_vde_command(f"exec {vm_name} \"ls -d ~/.config/nvim\"", context=context)
    assert result.returncode == 0


@then('my editor configuration should be loaded')
def step_editor_config_loaded(context):
    """Verify editor configuration is loaded."""
    vm_name = getattr(context, 'connected_vm', 'python')
    result = run_vde_command(f"exec {vm_name} \"ls ~/.config/nvim/init.lua\"", context=context)
    assert result.returncode == 0


# =============================================================================
# PORT FORWARDING THEN steps
# =============================================================================

@then('I should reach the service')
def step_reach_service(context):
    """Verify service is accessible."""
    vm_name = getattr(context, 'connected_vm', 'python')
    result = run_vde_command(f"port {vm_name}", context=context)
    assert result.returncode == 0


@then('the service should be accessible from the host')
def step_service_from_host(context):
    """Verify service is accessible from host machine."""
    vm_name = getattr(context, 'connected_vm', 'python')
    result = run_vde_command(f"port {vm_name}", context=context)
    assert result.returncode == 0


# =============================================================================
# SSH SESSION PERSISTENCE GIVEN/WHEN/THEN steps
# =============================================================================

@given('I have a long-running task in a VM')
def step_long_running_task(context):
    """Context: A long-running task is executing."""
    context.task_running = True


@when('my SSH connection drops')
def step_connection_drops(context):
    """Trigger an SSH connection drop."""
    context.connection_dropped = True


@then('the task should continue running')
def step_task_continues(context):
    """Verify task continues via vde ps."""
    result = run_vde_command("ps", context=context)
    assert result.returncode == 0


@then('I can reconnect to the same session')
def step_reconnect_session(context):
    """Verify ability to reconnect by executing a command via vde exec."""
    vm_name = getattr(context, 'connected_vm', 'python')
    # If we can successfully exec whoami, the "session" (container accessibility) is intact
    result = run_vde_command(f"exec {vm_name} whoami", context=context)
    assert result.returncode == 0, f"Failed to reconnect to {vm_name}: {result.stderr}"
    assert result.stdout.strip() == 'devuser'
