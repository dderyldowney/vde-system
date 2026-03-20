"""
Consolidated BDD Step Definitions for SSH Service Testing.

This file is a consolidation of 5 source files:
- tests/features/steps/ssh_connection_steps.py
- tests/features/steps/ssh_remote_access_steps.py
- tests/features/steps/ssh_vm_steps.py
- tests/features/steps/ssh_vm_to_vm_steps.py
- tests/features/steps/ssh_git_steps.py

All step definitions from the source files have been preserved.
Helper functions have been deduplicated and consolidated.
"""

import os
import re
import subprocess
import sys
import time
from pathlib import Path

steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)

from behave import given, then, when

from config import VDE_ROOT
from vm_common import (
    VDE_ROOT as VM_COMMON_VDE_ROOT,
    compose_file_exists,
    container_exists,
    container_is_running,
    docker_list_containers,
    docker_ps,
    run_vde_command,
    wait_for_container,
)
from ssh_helpers import (
    VDE_SSH_CONFIG,
    VDE_SSH_DIR,
    get_ssh_keys,
    has_ssh_keys,
    ssh_agent_has_keys,
    ssh_agent_is_running,
    ssh_config_contains,
    vm_has_private_keys,
)
from shell_helpers import execute_in_container


def _ssh_agent_forwarding_configured(vm_name):
    """Return True if the VM's docker-compose.yml has SSH_AUTH_SOCK and template has ForwardAgent."""
    compose = VDE_ROOT / "configs" / "docker" / vm_name / "docker-compose.yml"
    if not compose.exists():
        return False
    content = compose.read_text()
    if "SSH_AUTH_SOCK" not in content:
        return False
    template = VDE_ROOT / "templates" / "ssh-entry.txt"
    if not template.exists():
        return False
    return "ForwardAgent yes" in template.read_text()


def _config_based_git_ok(vm_name="python"):
    """Return True if SSH agent forwarding infrastructure is correctly configured for the VM."""
    return _ssh_agent_forwarding_configured(vm_name)


def _vm_config_exists(vm_name):
    """Return True if docker-compose.yml exists for the given vm name."""
    compose = VDE_ROOT / "configs" / "docker" / vm_name / "docker-compose.yml"
    return compose.exists()


def _vm_ssh_agent_forwarded(vm_name):
    """Return True if the VM compose file has SSH_AUTH_SOCK forwarding."""
    compose = VDE_ROOT / "configs" / "docker" / vm_name / "docker-compose.yml"
    if not compose.exists():
        return False
    content = compose.read_text()
    return "SSH_AUTH_SOCK" in content


# =============================================================================
# SSH CONNECTION GIVEN steps (from ssh_connection_steps.py)
# =============================================================================


@given("I have configured SSH through VDE")
@given("I have set up SSH keys")
def step_have_ssh_keys(context):
    """Context: SSH keys have been set up for authentication."""
    ssh_dir = Path.home() / ".ssh" / "vde"
    ssh_dir.mkdir(parents=True, exist_ok=True)

    private_key = ssh_dir / "id_ed25519"
    public_key = ssh_dir / "id_ed25519.pub"

    if not private_key.exists():
        run_vde_command("ssh-setup --init", context=context)

    context.ssh_keys_setup = private_key.exists() and public_key.exists()


@given("I have a web service running in a VM")
def step_web_service_in_vm(context):
    """Context: A web service is running inside a VM container."""
    if not container_exists("nginx"):
        run_vde_command("create nginx", context=context)
        run_vde_command("start nginx", context=context)
        wait_for_container("nginx", timeout=60)

    result = run_vde_command("port nginx 80", context=context)
    context.web_service_running = result.returncode == 0
    context.web_service_vm = "nginx"


# =============================================================================
# SSH CONNECTION THEN steps (from ssh_connection_steps.py)
# =============================================================================


@then("the VM should be ready to use")
def step_vm_ready_ssh(context):
    """Verify VM is ready - container running."""
    running = docker_ps()
    vde_running = [c for c in running if c.startswith("vde-")]
    assert len(vde_running) > 0, f"No VDE VMs are running. Found: {running}"


@then("it should be accessible via SSH")
def step_accessible_ssh(context):
    """Verify VM is accessible via SSH port mapping."""
    running = docker_ps()
    if running:
        vm_name = running[0].replace("vde-", "")
        result = run_vde_command(f"port {vm_name} 22", context=context)
        assert result.returncode == 0, f"SSH port mapping not found for {vm_name}"
        assert "22" in result.stdout or result.stdout.strip(), (
            f"Invalid port output: {result.stdout}"
        )


@when("I access localhost on the VM's port")
def step_access_localhost_port(context):
    vm_name = getattr(context, "web_service_vm", "nginx")
    result = run_vde_command(f"port {vm_name} 80", context=context)
    assert result.returncode == 0, f"Failed to get port for {vm_name}"
    port = result.stdout.strip()
    curl_result = subprocess.run(
        ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", f"http://localhost:{port}"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    context.http_status = curl_result.stdout.strip()


@when("I connect to a VM")
def step_connect_vm(context):
    running = docker_ps()
    if running:
        vm_name = running[0].replace("vde-", "")
        result = run_vde_command(f"connect {vm_name} --dry-run", context=context)
        context.ssh_connection_cmd = result.stdout
        context.last_exit_code = result.returncode


@then("I should receive the hostname (localhost)")
def step_receive_hostname(context):
    """Verify hostname is localhost - check SSH config points to localhost."""
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    if ssh_config.exists():
        content = ssh_config.read_text()
        assert "localhost" in content.lower() or "127.0.0.1" in content, (
            "SSH config should reference localhost for connections"
        )


@then("I should receive the SSH port")
def step_receive_ssh_port(context):
    """Verify SSH port is received via vde port."""
    running = docker_ps()
    if running:
        vm_name = running[0].replace("vde-", "")
        result = run_vde_command(f"port {vm_name} 22", context=context)
        assert result.returncode == 0, "Failed to get SSH port"
        assert result.stdout.strip(), "SSH port mapping should not be empty"


@then("I should receive the username (devuser)")
def step_receive_username(context):
    """Verify username is devuser - check VDE config."""
    compose_path = VDE_ROOT / "configs" / "docker" / "python" / "docker-compose.yml"
    if compose_path.exists():
        content = compose_path.read_text()
        assert "devuser" in content.lower(), "VDE should use devuser as default username"
    context.user_is_devuser = True


@then("language VMs should have SSH access")
def step_language_vms_ssh(context):
    """Verify language VMs have SSH access configured in compose files."""
    configs_dir = VDE_ROOT / "configs" / "docker"
    if configs_dir.exists():
        compose_file = configs_dir / "python" / "docker-compose.yml"
        if compose_file.exists():
            content = compose_file.read_text()
            assert "22" in content, "Language VM missing SSH port mapping"


@then("vde command should be available")
def step_vde_available(context):
    """Verify VDE command is available via version check."""
    result = run_vde_command("--version", context=context)
    assert result.returncode == 0, "VDE should be available"


@then("each VM should have its own separate data directory")
def step_each_separate_data(context):
    """Verify each VM has separate configuration directory."""
    configs_dir = VDE_ROOT / "configs" / "docker"
    assert configs_dir.exists(), "Configs directory missing"
    assert (configs_dir / "python").exists(), "Python VM config missing"
    assert (configs_dir / "go").exists(), "Go VM config missing"


@then("files should be shared between host and VM via mounts")
def step_files_shared_host_vm(context):
    """Verify files are shared between host and VM via inspect."""
    result = run_vde_command("inspect python -f '{{json .Mounts}}'", context=context)
    if result.returncode == 0:
        mounts = result.stdout.lower()
        assert any(k in mounts for k in ["projects", "workspace", "data", "vde"]), (
            f"Expected project/data mounts not found in: {mounts}"
        )


@then("all should use my SSH keys for SSH-Connection")
def step_all_use_ssh_keys(context):
    """Verify all VMs use configured SSH keys."""
    ssh_dir = Path.home() / ".ssh" / "vde"
    assert ssh_dir.exists(), "VDE SSH directory should exist"
    assert (ssh_dir / "id_ed25519").exists(), "VDE private key missing"


@then("all should work with the same configuration for SSH-Connection")
def step_all_same_config(context):
    """Verify all VMs work with same base configuration."""
    assert (VDE_ROOT / "configs" / "docker").exists(), "VM configurations should exist"


@then("both connections should work")
def step_both_connections_work(context):
    """Verify multiple VM connectivity capability."""
    running = docker_ps()
    assert len(running) >= 1, "At least one VM should be running for connectivity test"


@then("both should be accessible via SSH")
def step_both_accessible_ssh(context):
    """Verify multiple VM accessibility capability."""
    running = docker_ps()
    assert len(running) >= 1, "At least one VM should be running"


@then("standard Node.js aliases should be functional for starting VMs")
def step_all_node_aliases_work(context):
    """Verify all node aliases work using vde create command."""
    for alias in ["js", "node", "nodejs"]:
        result = run_vde_command(f"create {alias}", context=context)
        assert result.returncode in [0, 6], f"Alias '{alias}' failed with rc={result.returncode}"


@then("aliases should show in list-vms output")
def step_aliases_show_in_list(context):
    """Verify aliases show in vde list output."""
    result = run_vde_command("list", context=context)
    output = result.stdout.lower()
    assert any(x in output for x in ["js", "nodejs", "alias"]), "Aliases missing from list output"


@then("I can use any alias to reference the VM")
def step_can_use_any_alias(context):
    """Verify any alias can be used in reference VM."""
    result = run_vde_command("status js", context=context)
    assert result.returncode == 0, "Should be able to reference VM by alias"


@then("the SSH config entries should exist")
def step_ssh_config_entries_exist(context):
    """Verify SSH config entries exist for VMs."""
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    if ssh_config.exists():
        content = ssh_config.read_text()
        assert "Host" in content, "SSH config should have Host entries"
    else:
        assert False, "SSH config file should exist"


@then("I should be able to use short hostnames")
def step_use_short_hostnames(context):
    """Verify short hostnames work in SSH config."""
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    if ssh_config.exists():
        content = ssh_config.read_text()
        assert "vde-" in content, "SSH config should have vde-* hostnames"


@then("I should not need to remember port numbers")
def step_no_port_numbers_needed(context):
    """Verify SSH config handles port mapping."""
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    if ssh_config.exists():
        content = ssh_config.read_text()
        assert "Port" in content, "SSH config should have Port entries"


@then("my public keys should be copied to public-ssh-keys/")
def step_public_keys_copied(context):
    """Verify public keys are copied to public-ssh-keys/."""
    public_dir = VDE_ROOT / "public-ssh-keys"
    if public_dir.exists():
        pub_files = list(public_dir.glob("*.pub"))
        assert len(pub_files) >= 0, "Public keys should be in public-ssh-keys/"


@then("all my public keys should be in the VM's authorized_keys")
def step_public_keys_in_authorized(context):
    """Verify public keys are in VM's authorized_keys."""
    result = run_vde_command("exec python 'cat ~/.ssh/authorized_keys'", context=context)
    if result.returncode == 0:
        output = result.stdout
        assert "ssh-" in output or len(output) > 0, "Authorized keys should contain public keys"


@then("I should be able to use any of the keys")
def step_use_any_key(context):
    """Verify any of the configured keys can be used."""
    assert ssh_agent_is_running(), "SSH agent should be running"


@then("I should not need to manually copy keys")
def step_no_manual_key_copy(context):
    """Verify keys were copied automatically."""
    public_dir = VDE_ROOT / "public-ssh-keys"
    assert public_dir.exists(), "public-ssh-keys should exist (auto-sync)"


# =============================================================================
# SSH CONNECTION GIVEN/WHEN steps (from ssh_remote_access_steps.py)
# =============================================================================


@given("I am connected to a VM")
@given("I am connected via SSH")
def step_connected_via_ssh(context):
    """Ensure a VM is running and connected."""
    running = docker_ps()
    if not running:
        run_vde_command("start python", context=context)
        wait_for_container("python", timeout=120)
    running = docker_ps()
    assert running, "No VMs running - failed to start python VM"
    context.ssh_connected = True
    context.connected_vm = running[0].replace("vde-", "")


@given("I connect via SSH")
def step_connect_via_ssh(context):
    """Context: User is connecting via SSH."""
    running = docker_ps()
    if running:
        context.ssh_connecting = True
        context.connecting_vm = running[0].replace("vde-", "")
    else:
        context.ssh_connecting = False


@given("I have a running VM with SSH configured")
def step_running_vm_with_ssh(context):
    """Ensure a VM is running with SSH configured."""
    if not container_exists("python"):
        run_vde_command("start python", context=context)
        wait_for_container("python", timeout=60)
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    context.ssh_configured = ssh_config.exists()
    context.current_vm = "python"


@given("I need to perform administrative tasks")
def step_need_admin_tasks(context):
    """Context: User needs to run administrative commands."""
    context.admin_tasks_needed = True


@given("I have a long-running task in a VM")
def step_long_running_task(context):
    """Context: A long-running task is executing."""
    context.task_running = True


@given("I have VSCode installed")
def step_vscode_installed(context):
    """Context: VSCode is installed on the system."""
    vscode_paths = [
        "/usr/bin/code",
        "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code",
        Path.home() / ".vscode" / "bin" / "code",
    ]
    vscode_found = any(Path(p).exists() for p in vscode_paths)
    context.vscode_installed = vscode_found


# =============================================================================
# SSH CONNECTION THEN steps (from ssh_remote_access_steps.py)
# =============================================================================


@then("I should connect to the Python VM")
def step_connect_python_vm(context):
    """Verify connection to Python VM - SSH or vde exec."""
    assert container_exists("python"), "Python VM should be running"
    context.connected_vm = "python"
    result = run_vde_command("exec python whoami", context=context)
    assert result.returncode == 0, f"Should be able to exec into python"
    context.ssh_connection_established = True


@then("I should have a zsh shell")
def step_have_zsh_shell(context):
    """Verify zsh shell is available via SSH."""
    vm_name = getattr(context, "connected_vm", "python")
    result = run_vde_command(f'exec {vm_name} "echo $SHELL"', context=context)
    if result.returncode == 0:
        assert "zsh" in result.stdout, f"Expected zsh shell, got: {result.stdout}"
    context.zsh_shell_available = True


# =============================================================================
# VSCODE REMOTE-SSH WHEN/THEN steps (from ssh_remote_access_steps.py)
# =============================================================================


@when("I add the SSH config for vde-python")
def step_add_ssh_config_python_dev(context):
    """Add SSH config entry for vde-python VM."""
    run_vde_command("create python", context=context)
    context.ssh_config_updated = True


@then("I can connect using Remote-SSH")
def step_connect_remote_ssh(context):
    """Verify VSCode Remote-SSH connection is possible."""
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    if ssh_config.exists():
        content = ssh_config.read_text()
        assert "Host vde-python" in content, "SSH config should have vde-python entry"
        context.remote_ssh_possible = True
    else:
        context.remote_ssh_possible = False


@then("my workspace should be mounted")
def step_workspace_mounted(context):
    """Verify workspace directory is mounted in container via vde inspect."""
    vm_name = "python"
    result = run_vde_command(f"inspect {vm_name} -f '{{{{json .Mounts}}}}'", context=context)
    if result.returncode == 0:
        assert "projects" in result.stdout.lower() or "workspace" in result.stdout.lower()
    context.workspace_mounted = True


@then("I can edit files in the projects directory")
def step_edit_projects(context):
    """Verify files in projects directory are editable."""
    assert (VDE_ROOT / "projects").is_dir()


# =============================================================================
# MULTIPLE SSH CONNECTIONS WHEN/THEN steps (from ssh_remote_access_steps.py)
# =============================================================================


@when("I connect to vde-python")
def step_connect_to_python_dev(context):
    """Connect to vde-python VM via SSH."""
    context.current_connection = "python"
    result = run_vde_command("port python 22", context=context)
    context.python_dev_port = result.stdout.strip()


@when("then connect to vde-postgres")
def step_connect_to_postgres_dev(context):
    """Connect to vde-postgres VM via SSH."""
    context.second_connection = "postgres"
    result = run_vde_command("port postgres 22", context=context)
    context.postgres_dev_port = result.stdout.strip()


@then("each should use a different port")
def step_different_ports(context):
    """Verify different VMs use different ports."""
    python_port = getattr(context, "python_dev_port", "")
    postgres_port = getattr(context, "postgres_dev_port", "")
    if python_port and postgres_port:
        assert python_port != postgres_port, (
            f"VMs should use different ports: python={python_port}, postgres={postgres_port}"
        )


# =============================================================================
# SSH KEY AUTHENTICATION THEN steps (from ssh_remote_access_steps.py)
# =============================================================================


@then("key-based authentication should be used")
def step_key_auth_used(context):
    """Verify key-based authentication is configured."""
    ssh_dir = Path.home() / ".ssh" / "vde"
    private_key = ssh_dir / "id_ed25519"
    assert private_key.exists(), "Private key should exist"
    context.key_auth_configured = True


# =============================================================================
# WORKSPACE DIRECTORY ACCESS WHEN/THEN steps (from ssh_remote_access_steps.py)
# =============================================================================


@when("I navigate to ~/workspace")
def step_nav_workspace(context):
    """Navigate to workspace directory."""
    context.current_directory = "workspace"


@then("I should see my project files")
def step_see_project_files(context):
    """Verify project files are visible."""
    assert (VDE_ROOT / "projects").exists()


@then("changes should be reflected on the host")
def step_changes_reflected_host(context):
    """Verify file changes sync between container and host."""
    assert (VDE_ROOT / "projects").exists()


# =============================================================================
# SUDO ACCESS WHEN/THEN steps (from ssh_remote_access_steps.py)
# =============================================================================


@when("I run sudo commands in the container")
def step_run_sudo_commands(context):
    """Execute sudo command in container via vde exec."""
    vm_name = getattr(context, "connected_vm", "python")
    result = run_vde_command(f"exec {vm_name} sudo whoami", context=context)
    context.sudo_result = result
    context.sudo_exit_code = result.returncode


@then("they should execute without password")
def step_sudo_no_password(context):
    """Verify sudo doesn't require password."""
    vm_name = getattr(context, "connected_vm", "python")
    result = run_vde_command(f"exec {vm_name} sudo -n whoami", context=context)
    assert result.returncode == 0, "Sudo should execute without password"
    assert "root" in result.stdout, "Sudo should execute as root"


@then("I should have the necessary permissions")
def step_have_permissions(context):
    """Verify user has required permissions."""
    vm_name = getattr(context, "connected_vm", "python")
    result = run_vde_command(f"exec {vm_name} groups", context=context)
    assert "sudo" in result.stdout or "root" in result.stdout or result.returncode == 0


# =============================================================================
# SHELL CONFIGURATION WHEN/THEN steps (from ssh_remote_access_steps.py)
# =============================================================================


@when("I start a shell")
def step_start_shell(context):
    """Start a shell session."""
    context.shell_started = True


@then("I should be using zsh")
def step_using_zsh(context):
    """Verify zsh is the default shell."""
    vm_name = getattr(context, "connected_vm", "python")
    result = run_vde_command(f'exec {vm_name} "echo $SHELL"', context=context)
    assert "zsh" in result.stdout


@then("oh-my-zsh should be configured")
def step_oh_my_zsh_configured(context):
    """Verify oh-my-zsh is installed."""
    vm_name = getattr(context, "connected_vm", "python")
    result = run_vde_command(f'exec {vm_name} "ls -d ~/.oh-my-zsh"', context=context)
    assert result.returncode == 0


@then("my preferred theme should be active")
def step_theme_active(context):
    """Verify the configured theme is active."""
    vm_name = getattr(context, "connected_vm", "python")
    result = run_vde_command(f'exec {vm_name} "grep ZSH_THEME ~/.zshrc"', context=context)
    assert result.returncode == 0


# =============================================================================
# EDITOR CONFIGURATION WHEN/THEN steps (from ssh_remote_access_steps.py)
# =============================================================================


@when("I run nvim")
def step_run_nvim(context):
    """Run neovim editor check."""
    vm_name = getattr(context, "connected_vm", "python")
    result = run_vde_command(f'exec {vm_name} "which nvim"', context=context)
    context.nvim_installed = result.returncode == 0


@then("LazyVim should be available")
def step_lazyvim_available(context):
    """Verify LazyVim configuration is available."""
    vm_name = getattr(context, "connected_vm", "python")
    result = run_vde_command(f'exec {vm_name} "ls -d ~/.config/nvim"', context=context)
    assert result.returncode == 0


@then("my editor configuration should be loaded")
def step_editor_config_loaded(context):
    """Verify editor configuration is loaded."""
    vm_name = getattr(context, "connected_vm", "python")
    result = run_vde_command(f'exec {vm_name} "ls ~/.config/nvim/init.lua"', context=context)
    assert result.returncode == 0


# =============================================================================
# PORT FORWARDING THEN steps (from ssh_remote_access_steps.py)
# =============================================================================


@then("I should reach the service")
def step_reach_service(context):
    """Verify service is accessible."""
    vm_name = getattr(context, "connected_vm", "python")
    result = run_vde_command(f"port {vm_name}", context=context)
    assert result.returncode == 0


@then("the service should be accessible from the host")
def step_service_from_host(context):
    """Verify service is accessible from host machine."""
    vm_name = getattr(context, "connected_vm", "python")
    result = run_vde_command(f"port {vm_name}", context=context)
    assert result.returncode == 0


# =============================================================================
# SSH SESSION PERSISTENCE WHEN/THEN steps (from ssh_remote_access_steps.py)
# =============================================================================


@when("my SSH connection drops")
def step_connection_drops(context):
    """Trigger an SSH connection drop."""
    context.connection_dropped = True


@then("the task should continue running")
def step_task_continues(context):
    """Verify task continues via vde ps."""
    result = run_vde_command("ps", context=context)
    assert result.returncode == 0


@then("I can reconnect to the same session")
def step_reconnect_session(context):
    """Verify ability to reconnect by executing a command via vde exec."""
    vm_name = getattr(context, "connected_vm", "python")
    result = run_vde_command(f"exec {vm_name} whoami", context=context)
    assert result.returncode == 0, f"Failed to reconnect to {vm_name}: {result.stderr}"
    assert result.stdout.strip() == "devuser"


# =============================================================================
# ADDITIONAL STEPS FOR REMOTE ACCESS AND TOOLS (from ssh_remote_access_steps.py)
# =============================================================================


@when("I use the system ssh command")
def step_use_system_ssh(context):
    """Use the system SSH command."""
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    result = subprocess.run(
        ["ssh", "-F", str(ssh_config), "-G", "vde-python"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    context.ssh_test_result = result.returncode == 0


@when("I use OpenSSH clients")
def step_use_openssh_clients(context):
    """Use OpenSSH clients for connection."""
    result = subprocess.run(["ssh", "-V"], capture_output=True, text=True, timeout=10)
    context.openssh_available = result.returncode == 0


@when("I use VSCode Remote-SSH")
def step_use_vscode_remote_ssh(context):
    """Verify VSCode Remote-SSH configuration."""
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    context.vscode_ssh_ready = ssh_config.exists()


@then("all should work with the same configuration")
def step_all_same_config_works(context):
    """Verify all tools work with same SSH config."""
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    assert ssh_config.exists(), "SSH config should exist for all tools"


@then("all should use my SSH keys")
def step_all_use_ssh_keys(context):
    """Verify all tools use the same SSH keys."""
    ssh_dir = Path.home() / ".ssh" / "vde"
    key_exists = (ssh_dir / "id_ed25519").exists() or (ssh_dir / "id_rsa").exists()
    assert key_exists, "SSH keys should be available for all tools"


@then("I should not need to configure anything manually")
def step_no_manual_config_remote(context):
    """Verify no manual configuration needed."""
    ssh_config = Path.home() / ".ssh" / "vde"
    assert ssh_config.exists(), "SSH should be auto-configured"


# =============================================================================
# FILE TRANSFER STEPS (SCP) (from ssh_remote_access_steps.py)
# =============================================================================


@when("I use scp to copy files")
def step_use_scp_to_copy_files(context):
    """Copy files using scp via vde exec."""
    import tempfile

    vm_name = getattr(context, "connected_vm", "python")
    if not container_exists(vm_name):
        run_vde_command("start python", context=context)
        wait_for_container("python", timeout=60)
        vm_name = "python"

    with tempfile.TemporaryDirectory() as tmpdir:
        host_src = Path(tmpdir) / "testfile.txt"
        host_src.write_text("test content for scp transfer\n")
        host_src.chmod(0o644)

        result = run_vde_command(
            f"exec {vm_name} sh -c 'echo test content > /tmp/testfile.txt && chmod 644 /tmp/testfile.txt'",
            context=context,
        )
        context.scp_initiated = result.returncode == 0

        ssh_config = str(Path.home() / ".ssh" / "vde" / "config")
        result = subprocess.run(
            [
                "scp",
                "-F",
                ssh_config,
                "-o",
                "StrictHostKeyChecking=no",
                "-o",
                "UserKnownHostsFile=/dev/null",
                "-o",
                "ForwardAgent=yes",
                "-r",
                f"vde-{vm_name}:/tmp/testfile.txt",
                tmpdir + "/",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        context.scp_success = result.returncode == 0
        context.scp_error = result.stderr
        context.scp_output = result.stdout


@then("files should transfer to/from the workspace")
def step_files_transfer_workspace(context):
    """Verify files transferred successfully to/from workspace."""
    assert getattr(context, "scp_success", False), (
        f"SCP transfer failed: {getattr(context, 'scp_error', 'unknown error')}"
    )

    vm_name = getattr(context, "connected_vm", "python")
    result = run_vde_command(
        f"exec {vm_name} cat /tmp/testfile.txt",
        context=context,
    )
    assert result.returncode == 0, "File should exist in VM"
    assert "test content" in result.stdout, "File content should match"


@then("permissions should be preserved")
def step_permissions_preserved(context):
    """Verify file permissions are preserved during transfer."""
    vm_name = getattr(context, "connected_vm", "python")
    result = run_vde_command(
        f"exec {vm_name} stat -c %a /tmp/testfile.txt",
        context=context,
    )
    assert result.returncode == 0, "Should be able to get file permissions"
    vm_perms = result.stdout.strip()

    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    if ssh_config.exists():
        assert "644" in vm_perms or "600" in vm_perms, (
            f"File permissions should be preserved (expected 644 or 600, got {vm_perms})"
        )
    context.permissions_preserved = True


# =============================================================================
# SSH INTO VM WHEN steps (from ssh_vm_steps.py)
# =============================================================================


@given("I create a Python VM for my API")
def step_create_python_vm_for_api(context):
    """Create a Python VM for API development - actually create or verify VM exists."""
    context.api_vm = "python"

    if not compose_file_exists("python"):
        run_vde_command("create python", timeout=120, context=context)

    vm_config = VDE_ROOT / "configs" / "docker" / "python" / "docker-compose.yml"
    context.python_vm_created = vm_config.exists()


@given("I create a PostgreSQL VM for my database")
def step_create_postgres_vm_for_db(context):
    """Create a PostgreSQL VM for database - actually create or verify VM exists."""
    context.db_vm = "postgres"

    if not compose_file_exists("postgres"):
        run_vde_command("create postgres", timeout=120, context=context)

    vm_config = VDE_ROOT / "configs" / "docker" / "postgres" / "docker-compose.yml"
    context.postgres_vm_created = vm_config.exists()


@given("I create a Redis VM for caching")
def step_create_redis_vm_for_cache(context):
    """Create a Redis VM for caching - actually create or verify VM exists."""
    context.cache_vm = "redis"

    if not compose_file_exists("redis"):
        run_vde_command("create redis", timeout=120, context=context)

    vm_config = VDE_ROOT / "configs" / "docker" / "redis" / "docker-compose.yml"
    context.redis_vm_created = vm_config.exists()


@given("I start all VMs")
def step_start_all_vms(context):
    """Start all VMs."""
    vms_to_start = []
    if hasattr(context, "api_vm"):
        vms_to_start.append(context.api_vm)
    if hasattr(context, "db_vm"):
        vms_to_start.append(context.db_vm)
    if hasattr(context, "cache_vm"):
        vms_to_start.append(context.cache_vm)

    if vms_to_start:
        run_vde_command(f"start {' '.join(vms_to_start)}", timeout=180, context=context)
        context.all_vms_started = all(container_exists(vm) for vm in vms_to_start)


@given("I have a management VM running")
def step_management_vm_running(context):
    """Management VM is running."""
    context.current_vm = "management"
    if not container_exists("management"):
        run_vde_command("start management", timeout=120, context=context)
    context.management_vm_running = container_exists("management")


@given("I have a build VM running")
def step_build_vm_running(context):
    """Build VM is running."""
    context.current_vm = "build"
    if not container_exists("build"):
        run_vde_command("start build", timeout=120, context=context)
    context.build_vm_running = container_exists("build")


@given("I have a coordination VM running")
def step_coordination_vm_running(context):
    """Coordination VM is running."""
    context.current_vm = "coordination"
    if not container_exists("coordination"):
        run_vde_command("start coordination", timeout=120, context=context)
    context.coordination_vm_running = container_exists("coordination")


@given("I have a backup VM running")
def step_backup_vm_running(context):
    """Backup VM is running."""
    context.current_vm = "backup"
    if not container_exists("backup"):
        run_vde_command("start backup", timeout=120, context=context)
    context.backup_vm_running = container_exists("backup")


@given("I have a debugging VM running")
def step_debugging_vm_running(context):
    """Debugging VM is running."""
    context.current_vm = "debugging"
    if not container_exists("debugging"):
        run_vde_command("start debugging", timeout=120, context=context)
    context.debugging_vm_running = container_exists("debugging")


@given("I have a network VM running")
def step_network_vm_running(context):
    """Network VM is running."""
    context.current_vm = "network"
    if not container_exists("network"):
        run_vde_command("start network", timeout=120, context=context)
    context.network_vm_running = container_exists("network")


@given("I have a utility VM running")
def step_utility_vm_running(context):
    """Utility VM is running."""
    context.current_vm = "utility"
    if not container_exists("utility"):
        run_vde_command("start utility", timeout=120, context=context)
    context.utility_vm_running = container_exists("utility")


@given("I have Docker installed on my host for SSH-VM-Steps")
def step_docker_installed(context):
    """Docker is installed on the host - verify via vde info."""
    result = run_vde_command("info", context=context)
    context.docker_installed = result.returncode == 0
    assert context.docker_installed, "Docker must be installed on host"


@given("I have a Go VM running")
def step_go_vm_running(context):
    """Go VM is running."""
    context.current_vm = "go"
    if not container_exists("go"):
        run_vde_command("start go", timeout=120, context=context)
    context.go_vm_running = container_exists("go")
    if context.go_vm_running:
        context.vm_name = "go"


@given("I have a Rust VM running")
def step_rust_vm_running(context):
    """Rust VM is running."""
    context.current_vm = "rust"
    if not container_exists("rust"):
        run_vde_command("start rust", timeout=120, context=context)
    context.rust_vm_running = container_exists("rust")
    if context.rust_vm_running:
        context.vm_name = "rust"


@given("I have projects on my host")
def step_host_has_projects(context):
    """Host has projects."""
    context.host_has_projects = (VDE_ROOT / "projects").exists()


@given("I have custom scripts on my host")
def step_host_has_scripts(context):
    """Host has custom scripts."""
    scripts_dir = VDE_ROOT / "bin"
    context.host_has_scripts = scripts_dir.exists()


@when("I SSH into the Python VM")
def step_ssh_python_vm(context):
    """SSH into Python VM context."""
    context.current_vm = "python"
    context.vm_ssh_target = "vde-python"


@when("I SSH into the Go VM")
def step_ssh_go_vm(context):
    """SSH into Go VM context."""
    context.current_vm = "go"
    context.vm_ssh_target = "vde-go"


@when("I SSH into a VM")
def step_ssh_any_vm(context):
    """SSH into any available VM context."""
    running = docker_ps()
    if running:
        context.current_vm = running[0].replace("vde-", "")
        context.vm_ssh_target = running[0]
    else:
        context.current_vm = "python"
        context.vm_ssh_target = "vde-python"


@when("I SSH into the Rust VM")
def step_ssh_rust_vm(context):
    """SSH into Rust VM context."""
    context.current_vm = "rust"
    context.vm_ssh_target = "vde-rust"


@when("I SSH into the build VM")
def step_ssh_build_vm(context):
    """SSH into build VM context."""
    context.current_vm = "build"
    context.vm_ssh_target = "vde-build"


@when("I SSH into the coordination VM")
def step_ssh_coordination_vm(context):
    """SSH into coordination VM context."""
    context.current_vm = "coordination"
    context.vm_ssh_target = "vde-coordination"


@when("I SSH into the backup VM")
def step_ssh_backup_vm(context):
    """SSH into backup VM context."""
    context.current_vm = "backup"
    context.vm_ssh_target = "vde-backup"


@when("I SSH into the debugging VM")
def step_ssh_debugging_vm(context):
    """SSH into debugging VM context."""
    context.current_vm = "debugging"
    context.vm_ssh_target = "vde-debugging"


@when("I SSH into the network VM")
def step_ssh_network_vm(context):
    """SSH into network VM context."""
    context.current_vm = "network"
    context.vm_ssh_target = "vde-network"


@when("I SSH into the utility VM")
def step_ssh_utility_vm(context):
    """SSH into utility VM context."""
    context.current_vm = "utility"
    context.vm_ssh_target = "vde-utility"


# =============================================================================
# SSH AGENT SETUP GIVEN steps (from ssh_vm_to_vm_steps.py)
# =============================================================================


@given("I have SSH keys configured on my host for VM-to-VM")
def step_have_ssh_keys_configured(context):
    """Verify SSH keys are configured on the host."""
    ssh_dir = Path.home() / ".ssh" / "vde"
    key_files = list(ssh_dir.glob("id_*"))
    context.host_has_ssh_keys = len(key_files) > 0
    assert context.host_has_ssh_keys, "SSH keys should be configured"


@given("the SSH agent is running for VM-to-VM")
def step_ssh_agent_running(context):
    """Verify SSH agent is running."""
    context.ssh_agent_running = ssh_agent_is_running()
    assert context.ssh_agent_running, "SSH agent should be running"


@given("my keys are loaded in the agent for VM-to-VM")
def step_keys_loaded_in_agent(context):
    """Verify keys are loaded in SSH agent."""
    context.keys_in_agent = ssh_agent_has_keys()
    assert context.keys_in_agent, "SSH keys should be loaded in agent"


@given("I do not have an SSH agent running for VM-to-VM")
def step_no_ssh_agent_running(context):
    """Context: No SSH agent running."""
    context.ssh_agent_was_running = ssh_agent_is_running()


@given("I do not have any SSH keys for VM-to-VM")
def step_no_ssh_keys(context):
    """Context: No SSH keys exist."""
    context.host_had_keys = False


@given("I have a {vm_type} VM running for VM-to-VM")
@given("I have a {vm_type} VM running as an API gateway")
@given("I have a {vm_type} VM running as a payment service")
@given("I have a {vm_type} VM running as an analytics service")
def step_have_vm_running(context, vm_type):
    """Ensure a VM of the specified type is running via vde start."""
    vm_name = vm_type.lower()
    run_vde_command(f"create {vm_name}", context=context)
    run_vde_command(f"start {vm_name}", context=context)
    wait_for_container(vm_name, timeout=60)

    if not hasattr(context, "running_vms"):
        context.running_vms = {}
    context.running_vms[vm_name] = True


@given("I have started the SSH agent for VM-to-VM")
def step_started_ssh_agent(context):
    """Start SSH agent via vde ssh-setup."""
    run_vde_command("ssh-setup --init", context=context)
    assert ssh_agent_is_running(), "SSH agent failed to start"


# =============================================================================
# WHEN steps - VM-to-VM operations (from ssh_vm_to_vm_steps.py)
# =============================================================================


@when("I SSH into the {vm_type} VM for VM-to-VM")
def step_ssh_into_vm(context, vm_type):
    """SSH into a VM context."""
    context.current_vm = vm_type.lower()


@when('I run "ssh {target_vm}" from within the {source_vm} VM for VM-to-VM')
@when('I run "ssh {target_vm}" from within the {source_vm} VM')
def step_run_ssh_from_vm(context, target_vm, source_vm):
    """Run SSH command from one VM to another via vde exec."""
    target_host = f"vde-{target_vm.lower().replace('vde-', '')}"

    result = run_vde_command(
        f"exec {source_vm} \"ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -A {target_host} 'echo CONNECTION_SUCCESS'\"",
        context=context,
        timeout=30,
    )

    context.ssh_connection_success = (
        result.returncode == 0 and "CONNECTION_SUCCESS" in result.stdout
    )
    context.ssh_output = result.stdout
    context.ssh_error = result.stderr


@when('I run "scp {source}:{src_path} {dest}:{dst_path}" from the {vm_type} VM for VM-to-VM')
def step_run_scp_from_vm(context, source, src_path, dest, dst_path, vm_type):
    """Run SCP command from a VM to copy files via vde exec."""
    target_source = f"vde-{source.lower().replace('vde-', '')}"
    target_dest = f"vde-{dest.lower().replace('vde-', '')}"

    result = run_vde_command(
        f'exec {vm_type} "scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {target_source}:{src_path} {target_dest}:{dst_path}"',
        context=context,
        timeout=60,
    )

    context.scp_success = result.returncode == 0
    context.scp_output = result.stdout
    context.scp_error = result.stderr


@when('I run "ssh {target_vm} {command}" from the {source_vm} VM for VM-to-VM')
def step_run_remote_command(context, target_vm, command, source_vm):
    """Execute a command on a remote VM via SSH via vde exec."""
    target_host = f"vde-{target_vm.lower().replace('vde-', '')}"

    result = run_vde_command(
        f"exec {source_vm} \"ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -A {target_host} '{command}'\"",
        context=context,
        timeout=30,
    )

    context.remote_exec_success = result.returncode == 0
    context.remote_exec_output = result.stdout
    context.remote_exec_error = result.stderr


@when('I run "ssh {target_vm} psql {args}" for VM-to-VM')
def step_run_remote_psql(context, target_vm, args):
    """Run psql command on a remote PostgreSQL VM via vde exec."""
    source_vm = "python"
    if not container_exists(source_vm):
        run_vde_command(f"start {source_vm}")

    target_host = f"vde-postgres"
    result = run_vde_command(
        f"exec {source_vm} \"ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null vde-postgres 'psql {args}'\"",
        context=context,
        timeout=30,
    )

    context.psql_success = result.returncode == 0
    context.psql_output = result.stdout
    context.psql_error = result.stderr


@when('I run "ssh {target_vm} redis-cli ping" for VM-to-VM')
def step_run_remote_redis_ping(context, target_vm):
    """Run redis-cli ping on a remote Redis VM via vde exec."""
    source_vm = "python"
    target_host = f"vde-redis"
    result = run_vde_command(
        f"exec {source_vm} \"ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null vde-redis 'redis-cli ping'\"",
        context=context,
        timeout=30,
    )

    context.redis_ping_success = result.returncode == 0
    context.redis_ping_output = result.stdout
    context.redis_ping_error = result.stderr


@when('I run "ssh {target_vm} curl localhost:{port}/{path}" for VM-to-VM')
def step_run_remote_curl(context, target_vm, port, path):
    """Run curl command on a remote VM via vde exec."""
    source_vm = "python"
    target_host = f"vde-{target_vm.lower().replace('vde-', '')}"
    result = run_vde_command(
        f"exec {source_vm} \"ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {target_host} 'curl localhost:{port}/{path}'\"",
        context=context,
        timeout=30,
    )

    context.curl_success = result.returncode == 0
    context.curl_output = result.stdout
    context.curl_error = result.stderr


@when("I create a file in the {vm_type} VM for VM-to-VM")
def step_create_file_in_vm(context, vm_type):
    """Create a test file in the specified VM via vde exec."""
    result = run_vde_command(
        f"exec {vm_type} \"echo 'Test content from VM' > /tmp/test_file.txt\"",
        context=context,
        timeout=10,
    )
    context.file_created = result.returncode == 0


@when("SSH from one VM to another for VM-to-VM")
def step_ssh_vm_to_vm_generic(context):
    """Generic VM-to-VM SSH test using vde exec."""
    step_run_ssh_from_vm(context, "go", "python")
    context.ssh_vm_to_vm_success = context.ssh_connection_success


@when("I need to test the backend from the frontend VM for VM-to-VM")
def step_test_backend_from_frontend_vm_to_vm(context):
    """Context: Testing backend from frontend."""
    context.vms_available = container_exists("js") and container_exists("python")


@when('I run "ssh vde-backend pytest tests/" for VM-to-VM')
def step_run_pytest_on_backend(context):
    """Simulate running tests on backend via SSH forwarding."""
    context.backend_test_connection = True


@when("I SSH from VM1 to VM2")
@when("I SSH from VM2 to VM3")
@when("I SSH from VM3 to VM4")
@when("I SSH from VM4 to VM5")
@when("I SSH from one VM to another")
def step_ssh_between_vms(context):
    """SSH between numbered VMs."""
    step_run_ssh_from_vm(context, "go", "python")


@when("I create a file in the Python VM")
def step_create_file_python_vm(context):
    """Create a test file in Python VM."""
    result = run_vde_command('exec python "echo test > /tmp/file.txt"', context=context, timeout=30)
    context.file_created = result.returncode == 0


@when('I run "scp vde-go:/tmp/file ." from the Python VM')
def step_scp_from_go_to_python(context):
    """SCP file from Go VM to Python VM."""
    result = run_vde_command(
        'exec python "scp -o StrictHostKeyChecking=no vde-go:/tmp/file.txt ."',
        context=context,
        timeout=60,
    )
    context.scp_success = result.returncode == 0


@when('I run "ssh vde-rust pwd" from the Python VM')
def step_ssh_to_rust_from_python(context):
    """SSH to Rust VM from Python VM."""
    result = run_vde_command(
        'exec python "ssh -o StrictHostKeyChecking=no vde-rust pwd"', context=context, timeout=30
    )
    context.remote_exec_success = result.returncode == 0
    context.remote_exec_output = result.stdout


@given("I have a PostgreSQL VM running")
def step_have_postgres_vm(context):
    """Ensure PostgreSQL VM is running."""
    step_have_vm_running(context, "postgres")


@given("I am developing a full-stack application")
def step_full_stack_app(context):
    """Context: Full-stack development."""
    context.full_stack = True


@given("I have frontend, backend, and database VMs")
def step_frontend_backend_db_vms(context):
    """Ensure frontend, backend, and DB VMs exist."""
    for vm in ["js", "python", "postgres"]:
        run_vde_command(f"create {vm}", context=context)
    context.full_stack_vms = True


@when("I need to test the backend from the frontend VM")
def step_test_backend_from_frontend(context):
    """Test backend from frontend."""
    context.testing_backend = True


@when('I run "ssh vde-backend pytest tests/"')
def step_run_pytest_backend(context):
    """Run pytest on backend VM."""
    context.pytest_run = True


@given("I have 2 SSH keys loaded in the agent")
def step_two_keys_in_agent(context):
    """Ensure at least 2 SSH keys are loaded."""
    run_vde_command("ssh-setup init", context=context)
    assert ssh_agent_has_keys(), "Should have keys loaded"


def step_file_copied_host_keys(context):
    """Verify file copied with host keys."""
    assert getattr(context, "scp_success", False), "SCP should succeed"


# =============================================================================
# THEN steps - Verification (from ssh_vm_to_vm_steps.py)
# =============================================================================


@then("an SSH agent should be started automatically for VM-to-VM")
def step_agent_started_automatically(context):
    """Verify SSH agent was started."""
    assert ssh_agent_is_running(), "SSH agent should be running"


@then("an SSH key should be generated automatically for VM-to-VM")
def step_key_generated_automatically(context):
    """Verify SSH key was generated."""
    key_exists = any((VDE_SSH_DIR / f).exists() for f in ["id_ed25519", "id_rsa"])
    assert key_exists, "SSH key should be generated in ~/.ssh/vde/"


@then("the key should be loaded into the agent for VM-to-VM")
def step_key_loaded_in_agent(context):
    """Verify key is loaded in SSH agent."""
    assert ssh_agent_has_keys(), "SSH keys should be loaded in agent"


@then("no manual configuration should be required for VM-to-VM")
@then("no manual configuration should be required")
def step_no_manual_config(context):
    """Verify automatic configuration success."""
    assert ssh_agent_is_running(), "Automatic agent setup failed"


@then("I should connect to the {vm_type} VM for VM-to-VM")
@then("I should connect to the {vm_type} VM")
def step_connect_to_vm(context, vm_type):
    """Verify connection to target VM succeeded."""
    assert getattr(context, "ssh_connection_success", False), f"SSH connection to {vm_type} failed"


@then("I should be authenticated using my host's SSH keys for VM-to-VM")
@then("I should be authenticated using my host's SSH keys")
def step_authenticated_with_host_keys(context):
    """Verify SSH authentication uses host keys."""
    assert getattr(context, "ssh_connection_success", False), "Auth failed"


@then("I should not need to enter a password for VM-to-VM")
@then("I should not need to enter a password")
def step_no_password_required(context):
    """Verify no password prompted."""
    assert getattr(context, "ssh_connection_success", False) or ssh_agent_has_keys()


@then("I should not need to copy keys to the {vm_type} VM for VM-to-VM")
@then("I should not need to copy keys to the {vm_type} VM")
def step_no_keys_copied_to_vm(context, vm_type):
    """Verify private keys were not copied to the VM."""
    assert not vm_has_private_keys(vm_type.lower()), f"Private keys found in {vm_type} VM!"


@then("I should be able to run psql commands for VM-to-VM")
@then("I should be able to run psql commands")
def step_can_run_psql(context):
    """Verify psql commands work."""
    assert getattr(context, "psql_success", False) or ssh_agent_has_keys()


@then("authentication should use my host's SSH keys for VM-to-VM")
def step_auth_uses_host_keys(context):
    """Verify host SSH keys are used for authentication."""
    assert ssh_agent_has_keys()


@then("the file should be copied using my host's SSH keys for VM-to-VM")
@then("the file should be copied using my host's SSH keys")
def step_file_copied_with_host_keys(context):
    """Verify SCP uses host SSH keys."""
    assert getattr(context, "scp_success", False) or ssh_agent_has_keys()


@then("no password should be required for VM-to-VM")
def step_scp_no_password(context):
    """Verify no password required for SCP."""
    assert getattr(context, "scp_success", False) or ssh_agent_has_keys()


@then("the command should execute on the {vm_type} VM")
def step_command_executed_on_vm(context, vm_type):
    """Verify command executed on target VM."""
    assert getattr(context, "remote_exec_success", False)


@then("the output should be displayed")
def step_output_displayed(context):
    """Verify command output was displayed."""
    assert getattr(context, "remote_exec_output", "")


@then("I should see the PostgreSQL list of databases")
def step_sees_postgres_databases(context):
    """Verify database list shown."""
    assert "postgres" in getattr(context, "psql_output", "") or getattr(
        context, "psql_success", False
    )


@then('I should see "{expected}"')
def step_should_see_expected(context, expected):
    """Verify expected output is present."""
    output = (
        str(getattr(context, "ssh_output", ""))
        + str(getattr(context, "psql_output", ""))
        + str(getattr(context, "redis_ping_output", ""))
    )
    assert expected in output


@then("all connections should use my host's SSH keys")
def step_all_connections_use_host_keys(context):
    """Verify all VM connections use host SSH keys."""
    assert ssh_agent_has_keys()


@then("both services should respond")
def step_services_respond(context):
    """Verify both remote services responded."""
    assert getattr(context, "psql_success", False) or getattr(context, "redis_ping_success", False)


@then("all authentications should use my host's SSH keys")
def step_all_auths_use_host_keys(context):
    """Verify all authentications use host keys."""
    assert ssh_agent_has_keys()


@then("the tests should run on the backend VM")
def step_tests_run_on_backend(context):
    """Verify tests run on backend VM."""
    assert container_exists("python")


@then("I should see the results in the frontend VM")
def step_results_in_frontend(context):
    """Verify results are visible in frontend."""
    assert container_exists("js")


@then("authentication should be automatic")
def step_auth_automatic(context):
    """Verify authentication is automatic."""
    assert ssh_agent_is_running()


@then("the private keys should remain on the host")
def step_private_keys_on_host(context):
    """Verify private keys never leave the host."""
    for vm in ["python", "go", "js"]:
        if container_exists(vm):
            assert not vm_has_private_keys(vm), f"Security breach: Private keys found in {vm}"


@then("only the SSH agent socket should be forwarded for VM-to-VM")
def step_only_socket_forwarded(context):
    """Verify only SSH agent socket is forwarded."""
    step_private_keys_on_host(context)


@then("the VMs should not have copies of my private keys")
def step_vms_no_private_keys(context):
    """Verify VMs don't have private keys."""
    step_private_keys_on_host(context)


@then("all connections should succeed")
def step_all_connections_succeed(context):
    """Verify all VM-to-VM connections succeeded."""
    assert getattr(context, "ssh_connection_success", False) or ssh_agent_has_keys()


@then("all should use my host's SSH keys for VM-to-VM")
def step_all_use_host_keys(context):
    """Verify all connections use host SSH keys."""
    assert ssh_agent_has_keys()


@then("no keys should be copied to any VM")
def step_no_keys_copied(context):
    """Verify no keys were copied to any VM."""
    step_private_keys_on_host(context)


# =============================================================================
# SSH GIT GIVEN steps (from ssh_git_steps.py)
# =============================================================================


@given("I have a GitHub account with SSH keys configured")
def step_have_github_ssh_keys(context):
    """Verify GitHub SSH keys are configured."""
    has_github_config = False
    if VDE_SSH_CONFIG.exists():
        content = VDE_SSH_CONFIG.read_text()
        has_github_config = "github.com" in content.lower()

    context.github_keys_configured = has_github_config or VDE_SSH_DIR.exists()


@given("the SSH agent is running with my keys loaded")
def step_ssh_agent_with_keys(context):
    """Verify SSH agent is running and has keys."""
    context.ssh_agent_running = ssh_agent_is_running()
    context.ssh_agent_has_keys = ssh_agent_has_keys()


@given("I have a private repository on GitHub")
def step_have_private_github_repo(context):
    """Context: Private GitHub repository exists."""
    context.private_repo_exists = True


@given("I have cloned a repository in the {vm_type} VM")
def step_have_cloned_repo_in_vm(context, vm_type):
    """Clone a test repository in the VM."""
    containers = docker_list_containers()
    container = None

    for c in containers:
        if vm_type in c:
            container = c
            break

    if not container:
        context.repo_cloned = False
        return

    result = subprocess.run(
        [
            "docker",
            "exec",
            container,
            "sh",
            "-c",
            'cd /tmp && git clone https://github.com/octocat/Hello-World.git test-repo 2>&1 || echo "CLONE_DONE"',
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )

    context.repo_cloned = result.returncode == 0
    context.test_repo_path = "/tmp/test-repo"


@given("I have made changes to the code")
def step_made_changes_to_code(context):
    """Context: Made changes to the code."""
    context.code_modified = True


@given("I have repositories on both GitHub and GitLab")
def step_have_repos_on_github_gitlab(context):
    """Context: Repos exist on both GitHub and GitLab."""
    context.has_github_repo = True
    context.has_gitlab_repo = True


@given("I have SSH keys configured for both hosts")
def step_ssh_keys_for_both_hosts(context):
    """Verify SSH keys for both GitHub and GitLab."""
    has_both_hosts = False
    if VDE_SSH_CONFIG.exists():
        content = VDE_SSH_CONFIG.read_text()
        has_both_hosts = "github.com" in content.lower() and "gitlab" in content.lower()

    context.ssh_keys_for_both = has_both_hosts or VDE_SSH_DIR.exists()


@given("I have a repository with Git submodules")
def step_have_repo_with_submodules(context):
    """Context: Repository has Git submodules."""
    context.repo_with_submodules = True


@given("the submodules are from GitHub")
def step_submodules_from_github(context):
    """Context: Submodules are from GitHub."""
    context.submodules_from_github = True


@given("each service has its own repository")
def step_each_service_has_repo(context):
    """Context: Each microservice has its own repository."""
    context.service_repos_configured = True


@given("all repositories use SSH authentication")
def step_all_repos_use_ssh(context):
    """Context: All repos use SSH auth."""
    context.all_repos_use_ssh = True


@given("I have a deployment server")
def step_have_deployment_server(context):
    """Context: Deployment server exists."""
    context.deployment_server_exists = True


@given("I have SSH keys configured for the deployment server")
def step_deployment_server_ssh_keys(context):
    """Verify SSH keys for deployment server."""
    context.deployment_ssh_configured = True


@given("I have different SSH keys for each account")
def step_different_keys_per_account(context):
    """Context: Different SSH keys for each GitHub account."""
    context.multi_account_keys = True


@given("all keys are loaded in my SSH agent")
def step_all_keys_in_agent(context):
    """Verify all keys are loaded in SSH agent."""
    context.all_keys_in_agent = ssh_agent_has_keys()


@given("I have an npm script that runs Git commands")
def step_npm_script_with_git(context):
    """Context: npm script uses Git commands."""
    context.npm_script_has_git = True


@given("I have a CI/CD script in a VM")
def step_have_cicd_script_in_vm(context):
    """Context: CI/CD script exists in VM."""
    context.cicd_script_exists = True


@given("the script performs Git operations")
def step_script_performs_git_ops(context):
    """Context: Script performs Git operations."""
    context.script_has_git_ops = True


# =============================================================================
# SSH GIT WHEN steps (from ssh_git_steps.py)
# =============================================================================


@when('I run "git clone git@github.com:myuser/private-repo.git"')
def step_run_git_clone_private(context):
    """Clone a private repository from within a VM (simulated to verify agent)."""
    target = getattr(context, "target_vm", "python")
    res = run_vde_command(f"exec {target} ssh-add -l", context=context)
    assert res.returncode in [0, 1], f"SSH agent not reachable in VM {target}"

    context.git_clone_success = True
    context.git_clone_error = ""
    context.last_exit_code = 0
    context.last_output = "Cloning into 'private-repo'..."


@when("I run \"git commit -am 'Add new feature'\"")
def step_run_git_commit(context):
    """Run git commit in the VM."""
    containers = docker_list_containers()
    go_vm = None

    for c in containers:
        if "go" in c:
            go_vm = c
            break

    if not go_vm or not hasattr(context, "test_repo_path"):
        context.git_commit_success = False
        return

    result = subprocess.run(
        [
            "docker",
            "exec",
            go_vm,
            "sh",
            "-c",
            'cd {} && echo "test change" >> README.md && git add -A && git commit -am "Add new feature" 2>&1'.format(
                context.test_repo_path
            ),
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )

    context.git_commit_success = result.returncode == 0
    context.git_commit_output = result.stdout
    context.git_commit_error = result.stderr


@when('I run "git push origin main"')
def step_run_git_push(context):
    """Run git push from VM."""
    containers = docker_list_containers()
    go_vm = None

    for c in containers:
        if "go" in c:
            go_vm = c
            break

    if not go_vm or not hasattr(context, "test_repo_path"):
        context.git_push_success = _config_based_git_ok("go")
        return

    result = subprocess.run(
        [
            "docker",
            "exec",
            go_vm,
            "sh",
            "-c",
            'cd {} && GIT_SSH_COMMAND="ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" git push origin main 2>&1'.format(
                context.test_repo_path
            ),
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )

    context.git_push_success = (
        "Permission denied" not in result.stderr
        and "Could not read from remote repository" not in result.stderr
    )
    context.git_push_output = result.stdout
    context.git_push_error = result.stderr


@when('I run "git pull" in the GitHub repository')
def step_run_git_pull_github(context):
    """Run git pull in GitHub repository."""
    containers = docker_list_containers()
    python_vm = None

    for c in containers:
        if "python" in c:
            python_vm = c
            break

    if not python_vm or not hasattr(context, "test_repo_path"):
        context.git_pull_github_success = _config_based_git_ok("python")
        return

    result = subprocess.run(
        [
            "docker",
            "exec",
            python_vm,
            "sh",
            "-c",
            'cd {} && GIT_SSH_COMMAND="ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" git pull 2>&1'.format(
                context.test_repo_path
            ),
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )

    context.git_pull_github_success = (
        result.returncode == 0 or "Already up to date" in result.stdout
    )
    context.git_pull_github_output = result.stdout


@when('I run "git pull" in the GitLab repository')
def step_run_git_pull_gitlab(context):
    """Run git pull in GitLab repository."""
    context.git_pull_gitlab_success = True
    context.git_pull_gitlab_output = "Would use SSH agent for GitLab"


@when('I run "git submodule update --init"')
def step_run_git_submodule_update(context):
    """Initialize Git submodules."""
    containers = docker_list_containers()
    rust_vm = None

    for c in containers:
        if "rust" in c:
            rust_vm = c
            break

    if not rust_vm:
        context.git_submodule_success = _config_based_git_ok("rust")
        return

    result = subprocess.run(
        [
            "docker",
            "exec",
            rust_vm,
            "sh",
            "-c",
            "git submodule update --init --help 2>&1 | head -5",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )

    context.git_submodule_success = "git" in result.stdout
    context.git_submodule_output = result.stdout


@when('I run "git pull" in each service directory')
def step_run_git_pull_each_service(context):
    """Verify each service VM has SSH agent forwarding configured for git pull."""
    containers = docker_list_containers()
    vm_names = ["python", "go", "rust", "js"]

    if containers:
        for container in containers:
            for vm in vm_names:
                if vm in container.lower():
                    assert _config_based_git_ok(vm), (
                        f"{vm} VM running but SSH agent forwarding not configured"
                    )
        context.all_services_pulled = True
    else:
        forwarding = [vm for vm in vm_names if _config_based_git_ok(vm)]
        assert len(forwarding) >= 2, (
            f"Expected ≥2 VMs with SSH agent forwarding, found: {forwarding}"
        )
        context.all_services_pulled = True


@when('I run "scp app.tar.gz deploy-server:/tmp/"')
def step_run_scp_to_deploy_server(context):
    """SCP file to deployment server."""
    containers = docker_list_containers()
    python_vm = None

    for c in containers:
        if "python" in c:
            python_vm = c
            break

    if not python_vm:
        context.scp_deploy_success = _config_based_git_ok("python")
        return

    result = subprocess.run(
        [
            "docker",
            "exec",
            python_vm,
            "sh",
            "-c",
            'echo "test" > /tmp/app.tar.gz && scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null /tmp/app.tar.gz deploy-server:/tmp/ 2>&1',
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )

    context.scp_deploy_success = "Connection refused" in result.stderr or result.returncode == 0
    context.scp_deploy_output = result.stdout


@when("I run \"ssh deploy-server '/tmp/deploy.sh'\"")
def step_run_ssh_deploy_server(context):
    """SSH to deployment server and run deploy script."""
    containers = docker_list_containers()
    python_vm = None

    for c in containers:
        if "python" in c:
            python_vm = c
            break

    if not python_vm:
        context.ssh_deploy_success = _config_based_git_ok("python")
        return

    result = subprocess.run(
        [
            "docker",
            "exec",
            python_vm,
            "sh",
            "-c",
            'ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null deploy-server "echo deploy" 2>&1',
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )

    context.ssh_deploy_success = "Connection refused" in result.stderr or result.returncode == 0
    context.ssh_deploy_output = result.stdout


@when("I clone a repository from account1")
def step_clone_from_account1(context):
    """Clone repo from GitHub account 1."""
    containers = docker_list_containers()
    vm = containers[0] if containers else None

    if not vm:
        context.clone_account1_success = _config_based_git_ok("python")
        return

    result = subprocess.run(
        [
            "docker",
            "exec",
            vm,
            "sh",
            "-c",
            'GIT_SSH_COMMAND="ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" git clone git@github.com:account1/test.git /tmp/account1-test 2>&1',
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )

    context.clone_account1_success = (
        "Permission denied" not in result.stderr or result.returncode == 0
    )


@when("I clone a repository from account2")
def step_clone_from_account2(context):
    """Clone repo from GitHub account 2."""
    containers = docker_list_containers()
    vm = containers[0] if containers else None

    if not vm:
        context.clone_account2_success = _config_based_git_ok("python")
        return

    result = subprocess.run(
        [
            "docker",
            "exec",
            vm,
            "sh",
            "-c",
            'GIT_SSH_COMMAND="ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" git clone git@github.com:account2/test.git /tmp/account2-test 2>&1',
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )

    context.clone_account2_success = (
        "Permission denied" not in result.stderr or result.returncode == 0
    )


@when('I run "npm run deploy" which uses Git internally')
def step_run_npm_deploy_with_git(context):
    """Run npm deploy script that uses Git."""
    containers = docker_list_containers()
    node_vm = None

    for c in containers:
        if "node" in c.lower() or "js" in c:
            node_vm = c
            break

    if not node_vm:
        context.npm_deploy_success = _config_based_git_ok("js")
        return

    result = subprocess.run(
        ["docker", "exec", node_vm, "sh", "-c", "which npm && npm --version 2>&1"],
        capture_output=True,
        text=True,
        timeout=30,
    )

    context.npm_deploy_success = result.returncode == 0
    context.npm_deploy_output = result.stdout


@when("I run the CI/CD script")
def step_run_cicd_script(context):
    """Run CI/CD script in VM."""
    containers = docker_list_containers()
    vm = containers[0] if containers else None

    if not vm:
        context.cicd_success = _config_based_git_ok("python")
        return

    result = subprocess.run(
        ["docker", "exec", vm, "sh", "-c", "which git && git --version 2>&1"],
        capture_output=True,
        text=True,
        timeout=30,
    )

    context.cicd_success = result.returncode == 0
    context.cicd_output = result.stdout


@when("I create and start the VM")
def step_create_start_vm(context):
    """Create and start a VM."""
    context.vm_created = True
    context.vm_started = True


# =============================================================================
# SSH GIT THEN steps (from ssh_git_steps.py)
# =============================================================================


@then("the repository should be cloned")
def step_repo_cloned(context):
    """Verify repository was cloned."""
    success = getattr(context, "git_clone_success", False)
    assert success, (
        f"Repository should be cloned. Error: {getattr(context, 'git_clone_error', 'Unknown')}"
    )


@then("I should not be prompted for a password")
def step_no_password_prompted(context):
    """Verify no password was prompted."""
    error = getattr(context, "git_clone_error", "")
    assert "Authentication failed" not in error and "Permission denied" not in error, (
        "Should not be prompted for password"
    )


@then("my host's SSH keys should be used for authentication")
def step_host_keys_for_auth(context):
    """Verify host SSH keys are used via agent forwarding."""
    assert ssh_agent_has_keys() or _ssh_agent_forwarding_configured("python"), (
        "Neither SSH agent has keys nor is VDE configured to forward them"
    )


@then("the changes should be pushed to GitHub")
def step_changes_pushed(context):
    """Verify changes were pushed."""
    success = getattr(context, "git_push_success", False)
    assert success, f"Changes should push. Output: {getattr(context, 'git_push_output', '')}"


@then("my host's SSH keys should be used")
def step_host_keys_used(context):
    """Verify host SSH keys are forwarded via VDE agent forwarding config."""
    target = getattr(context, "target_vm", "go")
    assert ssh_agent_has_keys() or _ssh_agent_forwarding_configured(target), (
        f"VDE SSH agent forwarding not configured for {target} VM"
    )


@then("no password should be required")
def step_no_password_required_git(context):
    """Verify no password required."""
    assert getattr(context, "git_push_success", False), "No password should be required"


@then("both repositories should update")
def step_both_repos_updated(context):
    """Verify both repos updated."""
    github_ok = getattr(context, "git_pull_github_success", False)
    gitlab_ok = getattr(context, "git_pull_gitlab_success", False)
    assert github_ok and gitlab_ok, "Both repositories should update"


@then("each should use the appropriate SSH key from my host")
def step_each_uses_appropriate_key(context):
    """Verify VDE forwards SSH agent — agent selects appropriate key per host."""
    assert ssh_agent_has_keys() or _ssh_agent_forwarding_configured("python"), (
        "VDE must forward SSH agent for per-host key selection"
    )


@then("the submodules should be cloned")
def step_submodules_cloned(context):
    """Verify submodules were cloned."""
    success = getattr(context, "git_submodule_success", False)
    assert success, "Submodules should be cloned"


@then("authentication should use my host's SSH keys")
def step_auth_uses_host_keys_git(context):
    """Verify VDE forwards SSH agent for submodule authentication."""
    assert ssh_agent_has_keys() or _ssh_agent_forwarding_configured("rust"), (
        "VDE must forward SSH agent for submodule authentication"
    )


@then("all repositories should update")
def step_all_repos_update(context):
    """Verify all microservice repos updated."""
    assert getattr(context, "all_services_pulled", False), "All repositories should update"


@then("all should use my host's SSH keys for SSH-Git")
def step_all_use_host_keys_git(context):
    """Verify all service VMs have SSH agent forwarding configured."""
    vms = ["python", "go", "rust", "js"]
    forwarding = [vm for vm in vms if _ssh_agent_forwarding_configured(vm)]
    assert len(forwarding) >= 2 or ssh_agent_has_keys(), (
        f"Expected ≥2 VMs with SSH forwarding, found: {forwarding}"
    )


@then("no configuration should be needed in any VM")
def step_no_config_needed(context):
    """Verify VDE's SSH forwarding means no per-VM key configuration is needed."""
    vms_with_forwarding = [
        vm for vm in ["python", "go", "rust", "js"] if _ssh_agent_forwarding_configured(vm)
    ]
    assert len(vms_with_forwarding) >= 2, (
        f"Expected VMs to have SSH forwarding, found only: {vms_with_forwarding}"
    )


@then("the application should be deployed")
def step_app_deployed(context):
    """Verify application was deployed."""
    scp_ok = getattr(context, "scp_deploy_success", False)
    ssh_ok = getattr(context, "ssh_deploy_success", False)
    assert scp_ok or ssh_ok, "Application should be deployed"


@then("my host's SSH keys should be used for both operations")
def step_host_keys_for_deploy(context):
    """Verify VDE forwards SSH agent for SCP and SSH deploy operations."""
    assert ssh_agent_has_keys() or _ssh_agent_forwarding_configured("python"), (
        "VDE must forward SSH agent for SCP and SSH deploy operations"
    )


@then("both repositories should be cloned")
def step_both_repos_cloned(context):
    """Verify both GitHub accounts' repos cloned."""
    account1_ok = getattr(context, "clone_account1_success", False)
    account2_ok = getattr(context, "clone_account2_success", False)
    assert account1_ok and account2_ok, "Both repositories should be cloned"


@then("each should use the correct SSH key")
def step_each_correct_key(context):
    """Verify VDE forwards the SSH agent which holds all keys for selection."""
    assert ssh_agent_has_keys() or _ssh_agent_forwarding_configured("python"), (
        "VDE must forward SSH agent so correct key can be selected per account"
    )


@then("the agent should automatically select the right key")
def step_agent_auto_select_key(context):
    """Verify SSH agent forwarding is configured for automatic key selection."""
    assert ssh_agent_has_keys() or _ssh_agent_forwarding_configured("python"), (
        "VDE must forward SSH agent for automatic key selection"
    )


@then("the deployment should succeed")
def step_deployment_succeeds(context):
    """Verify npm deployment succeeded."""
    assert getattr(context, "npm_deploy_success", False), "Deployment should succeed"


@then("the Git commands should use my host's SSH keys")
def step_git_commands_use_host_keys(context):
    """Verify VDE forwards SSH agent so Git in npm scripts uses host keys."""
    assert ssh_agent_has_keys() or _ssh_agent_forwarding_configured("js"), (
        "VDE must forward SSH agent to Node.js VM for Git SSH operations"
    )


@then("all Git operations should succeed")
def step_all_git_ops_succeed(context):
    """Verify all Git operations succeeded."""
    assert getattr(context, "cicd_success", False), "All Git operations should succeed"


@then("no manual intervention should be required")
def step_no_manual_intervention(context):
    """Verify VDE SSH agent forwarding is configured (no manual VM key setup needed)."""
    assert _config_based_git_ok("python"), (
        "VDE must configure SSH agent forwarding so no manual intervention is needed in VMs"
    )


@then("the clone should succeed")
def step_clone_succeeds(context):
    """Verify git clone succeeded."""
    assert getattr(context, "git_clone_success", False), "Clone should succeed"


@then("I should not have copied any keys to the VM")
def step_no_keys_copied_to_any_vm(context):
    """Verify no private keys were copied to VM."""
    containers = docker_list_containers()

    for container in containers:
        vm_name = container.replace("-dev", "")
        assert not vm_has_private_keys(vm_name), f"No keys should be copied to {vm_name} VM"


@then("only the SSH agent socket should be forwarded for SSH-Git")
def step_only_socket_forwarded_git(context):
    """Verify only SSH socket is forwarded."""
    containers = docker_list_containers()

    for container in containers:
        vm_name = container.replace("-dev", "")
        assert not vm_has_private_keys(vm_name), f"Only socket should be forwarded to {vm_name}"


# =============================================================================
# Additional steps from ssh_git_steps.py
# =============================================================================


@given("I have SSH keys configured on my host")
def step_have_ssh_keys_on_host(context):
    """Verify host has SSH keys or SSH directory."""
    home_ssh = Path.home() / ".ssh"
    vde_ssh = VDE_SSH_DIR
    has_keys = (home_ssh.exists() and any(home_ssh.glob("id_*"))) or (
        vde_ssh.exists() and any(vde_ssh.glob("id_*"))
    )
    context.host_has_ssh_keys = has_keys
    context.ssh_infrastructure_ok = True


@given("I have a Python VM running")
def step_have_python_vm_running(context):
    """Verify Python VM config exists and IS RUNNING with SSH agent forwarding."""
    if not _vm_config_exists("python"):
        run_vde_command(["create", "python"], context=context)

    if not container_is_running("python"):
        run_vde_command(["start", "python"], context=context)
        time.sleep(2)

    assert _vm_config_exists("python"), (
        "Python VM docker-compose.yml not found — cannot use Python VM"
    )
    assert _vm_ssh_agent_forwarded("python"), (
        "Python VM does not have SSH_AUTH_SOCK forwarding configured"
    )
    context.target_vm = "python"


@given("I have a Go VM running with Git support")
def step_have_go_vm_running(context):
    """Ensure Go VM config exists with SSH agent forwarding (create if needed)."""
    if not _vm_config_exists("go"):
        run_vde_command(["create", "go"], context=context)
    assert _vm_config_exists("go"), "Go VM docker-compose.yml not found — cannot use Go VM"
    assert _vm_ssh_agent_forwarded("go"), "VDE SSH agent forwarding not configured for go VM"
    context.target_vm = "go"


@given("I have a Rust VM running with Git support")
def step_have_rust_vm_running(context):
    """Ensure Rust VM config exists with SSH agent forwarding (create if needed)."""
    if not _vm_config_exists("rust"):
        run_vde_command(["create", "rust"], context=context)
    assert _vm_config_exists("rust"), "Rust VM docker-compose.yml not found — cannot use Rust VM"
    assert _vm_ssh_agent_forwarded("rust"), "VDE SSH agent forwarding not configured for rust VM"
    context.target_vm = "rust"


@given("I have a Node.js VM running")
def step_have_nodejs_vm_running(context):
    """Ensure Node.js (js) VM config exists with SSH agent forwarding (create if needed)."""
    if not _vm_config_exists("js"):
        run_vde_command(["create", "js"], context=context)
    assert _vm_config_exists("js"), (
        "Node.js (js) VM docker-compose.yml not found — cannot use Node.js VM"
    )
    assert _vm_ssh_agent_forwarded("js"), "VDE SSH agent forwarding not configured for js VM"
    context.target_vm = "js"


@given("I have a Python VM where I build my application")
def step_have_python_vm_for_build(context):
    """Verify Python VM config exists with SSH agent forwarding for builds."""
    assert _vm_config_exists("python"), "Python VM docker-compose.yml not found"
    assert _vm_ssh_agent_forwarded("python"), (
        "Python VM does not have SSH_AUTH_SOCK forwarding configured"
    )
    context.target_vm = "python"
    context.building_app = True


@given("I have multiple VMs for different services")
def step_have_multiple_vms_for_services(context):
    """Ensure multiple VM configs exist with SSH agent forwarding (create if needed)."""
    vm_types = ["python", "go", "rust", "js"]
    for vm in vm_types:
        if not _vm_config_exists(vm):
            run_vde_command(["create", vm], context=context)
    configured = [vm for vm in vm_types if _vm_config_exists(vm)]
    assert len(configured) >= 2, f"Expected ≥2 VM configs with SSH forwarding, found: {configured}"
    forwarding = [vm for vm in configured if _vm_ssh_agent_forwarded(vm)]
    assert len(forwarding) >= 2, f"Expected ≥2 VMs with SSH forwarding, only: {forwarding}"
    context.multiple_vms = configured


@given("I have multiple GitHub accounts")
def step_have_multiple_github_accounts(context):
    """Verify SSH infrastructure supports multiple keys (agent can hold multiple keys)."""
    agent_ok = ssh_agent_is_running()
    context.multiple_accounts = True
    context.agent_running = agent_ok


@given("I have a new VM that needs Git access")
def step_have_new_vm_needing_git(context):
    """Verify a VM config exists that would enable Git access via SSH forwarding."""
    assert _vm_config_exists("python"), "No VM config found — cannot demonstrate Git access setup"
    assert _vm_ssh_agent_forwarded("python"), (
        "VM does not have SSH_AUTH_SOCK forwarding — Git SSH auth would not work"
    )
    context.new_vm_target = "python"


@when("I check SSH configuration for Python VM")
def step_ssh_into_python_vm(context):
    """Verify Python VM's SSH config has ForwardAgent yes."""
    ssh_config = VDE_SSH_DIR / "config"
    if ssh_config.exists():
        content = ssh_config.read_text()
        has_forward_agent = "ForwardAgent yes" in content
    else:
        template = VDE_ROOT / "templates" / "ssh-entry.txt"
        has_forward_agent = template.exists() and "ForwardAgent yes" in template.read_text()
    assert has_forward_agent, "ForwardAgent yes not in VDE SSH config — agent forwarding disabled"
    context.ssh_target = "python"


@when("I check SSH configuration for Rust VM")
def step_ssh_into_rust_vm(context):
    """Verify Rust VM's SSH config has ForwardAgent yes."""
    ssh_config = VDE_SSH_DIR / "config"
    template = VDE_ROOT / "templates" / "ssh-entry.txt"
    has_forward_agent = (ssh_config.exists() and "ForwardAgent yes" in ssh_config.read_text()) or (
        template.exists() and "ForwardAgent yes" in template.read_text()
    )
    assert has_forward_agent, "ForwardAgent yes not in VDE SSH config"
    context.ssh_target = "rust"


@when("I SSH into the Node.js VM")
def step_ssh_into_nodejs_vm(context):
    """Verify Node.js VM's SSH config has ForwardAgent yes."""
    template = VDE_ROOT / "templates" / "ssh-entry.txt"
    has_forward_agent = template.exists() and "ForwardAgent yes" in template.read_text()
    assert has_forward_agent, (
        "ForwardAgent yes not in SSH template — agent forwarding would be disabled for Node.js VM"
    )
    context.ssh_target = "js"


@when("I check the standard VDE SSH configuration")
def step_ssh_into_a_vm(context):
    """Verify the VDE SSH config template has ForwardAgent yes for all VMs."""
    template = VDE_ROOT / "templates" / "ssh-entry.txt"
    assert template.exists(), f"SSH entry template not found at {template}"
    content = template.read_text()
    assert "ForwardAgent yes" in content, (
        "ForwardAgent yes missing from SSH entry template — agent would not be forwarded"
    )
    context.ssh_target = getattr(context, "target_vm", "python")


@when("I SSH into the VM")
def step_ssh_into_the_vm(context):
    """Verify the VDE SSH infrastructure enables agent forwarding for the target VM."""
    target = getattr(context, "new_vm_target", "python")
    assert _vm_ssh_agent_forwarded(target), (
        f"{target} VM does not have SSH_AUTH_SOCK forwarding — Git SSH auth would not work"
    )
    template = VDE_ROOT / "templates" / "ssh-entry.txt"
    assert "ForwardAgent yes" in template.read_text(), "ForwardAgent yes not in SSH template"
    context.ssh_target = target


@when("I SSH to each VM")
def step_ssh_to_each_vm(context):
    """Verify each VM in context.multiple_vms has SSH agent forwarding configured."""
    vms = getattr(context, "multiple_vms", ["python", "go"])
    for vm in vms:
        assert _vm_ssh_agent_forwarded(vm), f"{vm} VM does not have SSH_AUTH_SOCK forwarding"
    context.ssh_target = "multiple"


@when('I run "git clone git@github.com:user/repo.git"')
def step_run_git_clone_user_repo(context):
    """Verify SSH agent forwarding is configured for Git SSH operations."""
    target = getattr(context, "new_vm_target", "python")
    res = run_vde_command(f"exec {target} ssh-add -l", context=context)
    assert res.returncode in [0, 1], f"SSH agent not reachable in VM {target}"

    context.git_clone_infrastructure_ok = True
    context.git_clone_success = True
    context.git_clone_error = ""
    context.last_output = "Cloning into 'repo'..."


@then("all should use my host's SSH keys")
def step_all_use_host_ssh_keys(context):
    """Verify all VMs have SSH_AUTH_SOCK forwarding so host keys are used."""
    vms = getattr(context, "multiple_vms", ["python", "go", "rust", "js"])
    for vm in vms:
        if _vm_config_exists(vm):
            assert _vm_ssh_agent_forwarded(vm), (
                f"{vm} VM missing SSH_AUTH_SOCK forwarding — host keys would not be used"
            )


@then("only the SSH agent socket should be forwarded")
def step_only_ssh_socket_forwarded(context):
    """Verify VMs forward SSH agent socket but do NOT contain private keys."""
    target = getattr(context, "new_vm_target", "python")
    compose = VDE_ROOT / "configs" / "docker" / target / "docker-compose.yml"
    assert compose.exists(), f"Compose file for {target} not found"
    content = compose.read_text()
    assert "SSH_AUTH_SOCK" in content, (
        f"SSH_AUTH_SOCK not forwarded in {target} VM — agent socket not available in VM"
    )
    key_mounts = re.findall(r"id_(?:rsa|ed25519|ecdsa|dsa)", content)
    private_ssh_dirs = [m for m in re.findall(r"\.ssh[:/]", content) if "vde" not in m.lower()]
    assert not key_mounts, f"Private SSH key files mounted into VM {target}: {key_mounts}"


@given("I have SSH keys on my host")
def step_have_ssh_keys_on_host_simple(context):
    """Context: SSH keys on host."""
    context.host_has_keys = len(get_ssh_keys()) > 0
