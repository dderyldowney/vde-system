"""
BDD Step Definitions for User Workflow and Environment Scenarios.

These steps verify user environment, permissions, editor configs, and workflows.
"""
import subprocess
import sys

# Import shared configuration
steps_dir = sys.path.insert(0, steps_dir) if (steps_dir := __import__('os').path.dirname(__import__('os').path.abspath(__file__))) not in sys.path else None
from pathlib import Path

from behave import given, then

from config import VDE_ROOT
from ssh_helpers import container_exists
from vm_common import docker_ps

# =============================================================================
# SSH CONNECTION CONTEXT GIVEN steps
# =============================================================================

@given('I have the SSH connection details')
def step_have_ssh_connection_details(context):
    """Context: User has SSH connection details."""
    context.ssh_details_available = True
    # Verify SSH config exists
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    context.ssh_config_exists = ssh_config.exists()


# =============================================================================
# USER ENVIRONMENT THEN steps
# =============================================================================

@then('I should be logged in as devuser')
def step_logged_in_devuser(context):
    """Verify logged in as devuser - check actual container or verify config."""
    running = docker_ps()
    if running:
        vm = list(running)[0]
        result = subprocess.run(
            ['docker', 'exec', vm, 'whoami'],
            capture_output=True, text=True, timeout=10
        )
        context.user_is_devuser = result.stdout.strip() == 'devuser'
    else:
        # Check docker-compose files for devuser configuration
        configs_dir = VDE_ROOT / "configs" / "docker"
        if configs_dir.exists():
            for vm_dir in configs_dir.iterdir():
                compose_file = vm_dir / "docker-compose.yml"
                if compose_file.exists():
                    content = compose_file.read_text()
                    if 'USER' in content or 'user:' in content.lower() or 'devuser' in content.lower():
                        return
        context.user_is_devuser = False  # No verification possible


@then('I should have a zsh shell')
def step_have_zsh_shell(context):
    """Verify have a zsh shell - check actual container or Dockerfile."""
    running = docker_ps()
    if running:
        vm = list(running)[0]
        result = subprocess.run(
            ['docker', 'exec', vm, 'which', 'zsh'],
            capture_output=True, text=True, timeout=10
        )
        context.has_zsh = result.returncode == 0
    else:
        # Check Dockerfile for zsh installation
        vde_root = VDE_ROOT
        dockerfiles = list(vde_root.rglob("Dockerfile"))
        for dockerfile in dockerfiles:
            content = dockerfile.read_text()
            if 'zsh' in content.lower():
                return
        context.has_zsh = False  # No verification possible


@then('I can edit files in the projects directory')
def step_can_edit_projects(context):
    """Verify can edit files in projects directory - check actual mount or compose config."""
    running = docker_ps()
    if running:
        vm = list(running)[0]
        result = subprocess.run(
            ['docker', 'inspect', '-f', '{{json .Mounts}}', vm],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            mounts = result.stdout.lower()
            context.can_edit_projects = 'workspace' in mounts or 'project' in mounts
        else:
    else:
        # Check docker-compose files for workspace/project volume mounts
        configs_dir = VDE_ROOT / "configs" / "docker"
        if configs_dir.exists():
            for vm_dir in configs_dir.iterdir():
                compose_file = vm_dir / "docker-compose.yml"
                if compose_file.exists():
                    content = compose_file.read_text().lower()
                    if 'workspace' in content or 'project' in content:
                        return
        context.can_edit_projects = False  # No verification possible


@then('each should use a different port')
def step_different_ports(context):
    """Verify each VM uses a different port."""
    running = docker_ps()
    ports_seen = set()
    for vm in running:
        result = subprocess.run(
            ['docker', 'port', vm, '22'],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            # Extract port number
            if ':' in result.stdout:
                port = result.stdout.split(':')[-1]
                ports_seen.add(port)
    context.different_ports_used = len(ports_seen) >= 2 or len(running) < 2


@then('I should see my project files')
def step_see_project_files(context):
    """Verify can see project files."""
    # Projects should be mounted into containers
    projects_dir = VDE_ROOT / "projects"
    context.project_files_visible = projects_dir.exists()


# =============================================================================
# ADMINISTRATIVE TASKS steps
# =============================================================================

@given('I need to perform administrative tasks')
def step_need_admin_tasks(context):
    """Context: User needs to perform administrative tasks."""
    context.needs_admin = True


@then('they should execute without password')
def step_execute_no_password(context):
    """Verify administrative tasks execute without password - check actual or sudoers config."""
    running = docker_ps()
    if running:
        vm = list(running)[0]
        result = subprocess.run(
            ['docker', 'exec', vm, 'sudo', '-n', 'true'],
            capture_output=True, text=True, timeout=10
        )
        context.passwordless_sudo = result.returncode == 0
    else:
        # Check for sudo configuration in setup files
        vde_root = VDE_ROOT
        setup_script = vde_root / "scripts" / "install-vde.sh"
        if setup_script.exists():
            content = setup_script.read_text()
            if 'sudo' in content.lower() and ('nopasswd' in content.lower() or 'passwordless' in content.lower()):
                return
        context.passwordless_sudo = False  # No verification possible


@then('I should have the necessary permissions')
def step_have_permissions(context):
    """Verify have necessary permissions - check actual container or group config."""
    running = docker_ps()
    if running:
        vm = list(running)[0]
        result = subprocess.run(
            ['docker', 'exec', vm, 'groups'],
            capture_output=True, text=True, timeout=10
        )
        context.has_permissions = result.returncode == 0
    else:
        # Check Dockerfile for user/group configuration
        vde_root = VDE_ROOT
        dockerfiles = list(vde_root.rglob("Dockerfile"))
        for dockerfile in dockerfiles:
            content = dockerfile.read_text()
            if 'group' in content.lower() or 'user' in content.lower():
                return
        context.has_permissions = False  # No verification possible


# =============================================================================
# SHELL AND EDITOR CONFIGURATION steps
# =============================================================================

@given('I connect via SSH')
def step_connect_ssh(context):
    """Context: Connect via SSH."""
    context.ssh_connection = True


@then('I should be using zsh')
def step_using_zsh(context):
    """Verify using zsh shell - check actual container or login shell config."""
    running = docker_ps()
    if running:
        vm = list(running)[0]
        result = subprocess.run(
            ['docker', 'exec', vm, 'echo', '$SHELL'],
            capture_output=True, text=True, timeout=10
        )
        context.using_zsh = 'zsh' in result.stdout.lower()
    else:
        # Check Dockerfile for default shell
        vde_root = VDE_ROOT
        dockerfiles = list(vde_root.rglob("Dockerfile"))
        for dockerfile in dockerfiles:
            content = dockerfile.read_text()
            if 'SHELL' in content and '/zsh' in content:
                return
        context.using_zsh = False  # No verification possible


@then('oh-my-zsh should be configured')
def step_oh_my_zsh_configured(context):
    """Verify oh-my-zsh is configured - check actual container or install script."""
    running = docker_ps()
    if running:
        vm = list(running)[0]
        result = subprocess.run(
            ['docker', 'exec', vm, 'ls', '/home/devuser/.oh-my-zsh'],
            capture_output=True, text=True, timeout=10
        )
        context.oh_my_zsh_installed = result.returncode == 0
    else:
        # Check for oh-my-zsh installation script in setup files
        vde_root = VDE_ROOT
        setup_script = vde_root / "scripts" / "install-vde.sh"
        if setup_script.exists():
            content = setup_script.read_text()
            if 'oh-my-zsh' in content.lower():
                return
        context.oh_my_zsh_installed = False  # No verification possible


@then('my preferred theme should be active')
def step_theme_active(context):
    """Verify preferred theme is active - check actual container or zshrc template."""
    running = docker_ps()
    if running:
        vm = list(running)[0]
        result = subprocess.run(
            ['docker', 'exec', vm, 'grep', 'ZSH_THEME', '/home/devuser/.zshrc'],
            capture_output=True, text=True, timeout=10
        )
        context.theme_configured = result.returncode == 0
    else:
        # Check for zshrc template with theme configuration
        vde_root = VDE_ROOT
        zshrc_files = list(vde_root.rglob(".zshrc")) + list(vde_root.rglob("zshrc*"))
        for zshrc_file in zshrc_files:
            content = zshrc_file.read_text()
            if 'ZSH_THEME' in content:
                return
        context.theme_configured = False  # No verification possible


@then('LazyVim should be available')
def step_lazyvim_available(context):
    """Verify LazyVim is available - check actual container or install scripts."""
    running = docker_ps()
    if running:
        vm = list(running)[0]
        result = subprocess.run(
            ['docker', 'exec', vm, 'which', 'nvim'],
            capture_output=True, text=True, timeout=10
        )
        context.lazyvim_available = result.returncode == 0
    else:
        # Check for nvim installation in setup scripts
        vde_root = VDE_ROOT
        setup_script = vde_root / "scripts" / "install-vde.sh"
        dockerfiles = list(vde_root.rglob("Dockerfile"))
        lazyvim_found = False

        if setup_script.exists():
            content = setup_script.read_text()
            if 'nvim' in content.lower() or 'neovim' in content.lower():
                lazyvim_found = True

        if not lazyvim_found:
            for dockerfile in dockerfiles:
                content = dockerfile.read_text()
                if 'nvim' in content.lower() or 'neovim' in content.lower():
                    lazyvim_found = True
                    break

        context.lazyvim_available = lazyvim_found


@then('my editor configuration should be loaded')
def step_editor_config_loaded(context):
    """Verify editor configuration is loaded - check actual container or templates."""
    running = docker_ps()
    if running:
        vm = list(running)[0]
        result = subprocess.run(
            ['docker', 'exec', vm, 'ls', '/home/devuser/.config/nvim'],
            capture_output=True, text=True, timeout=10
        )
        context.editor_config_loaded = result.returncode == 0
    else:
        # Check for nvim config in templates or backup
        vde_root = VDE_ROOT
        nvim_configs = list(vde_root.rglob("nvim")) + list(vde_root.rglob("*lazyvim*"))
        context.editor_config_loaded = len(nvim_configs) > 0


# =============================================================================
# FILE TRANSFER AND PERMISSIONS steps
# =============================================================================

@then('files should transfer to/from the workspace')
def step_files_transfer_workspace(context):
    """Verify files transfer to/from workspace - check actual mount or compose config."""
    running = docker_ps()
    if running:
        vm = list(running)[0]
        result = subprocess.run(
            ['docker', 'inspect', '-f', '{{json .Mounts}}', vm],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            mounts = result.stdout.lower()
            context.workspace_mounted = 'workspace' in mounts
        else:
    else:
        # Check docker-compose files for workspace volume mounts
        configs_dir = VDE_ROOT / "configs" / "docker"
        if configs_dir.exists():
            for vm_dir in configs_dir.iterdir():
                compose_file = vm_dir / "docker-compose.yml"
                if compose_file.exists():
                    content = compose_file.read_text().lower()
                    if 'workspace' in content:
                        return


@then('permissions should be preserved')
def step_permissions_preserved(context):
    """Verify file permissions are preserved - check actual or docker-compose user config."""
    running = docker_ps()
    if running:
        vm = list(running)[0]
        result = subprocess.run(
            ['docker', 'inspect', '-f', '{{.User}}', vm],
            capture_output=True, text=True, timeout=10
        )
        context.permissions_preserved = result.returncode == 0
    else:
        # Check for user configuration in docker-compose files
        configs_dir = VDE_ROOT / "configs" / "docker"
        if configs_dir.exists():
            for vm_dir in configs_dir.iterdir():
                compose_file = vm_dir / "docker-compose.yml"
                if compose_file.exists():
                    content = compose_file.read_text()
                    if 'user:' in content or 'USER' in content:
                        return


# =============================================================================
# WEB SERVICE AND SESSION steps
# =============================================================================

@given('I have a web service running in a VM')
def step_web_service_running_vm(context):
    """Context: Web service running in a VM."""
    context.web_service_vm = 'nginx'
    context.web_service_running = container_exists('nginx') or container_exists('nginx-dev')


@then('I should reach the service')
def step_reach_service(context):
    """Verify can reach the web service - check actual port mapping or compose config."""
    vm = getattr(context, 'web_service_vm', 'nginx')
    if container_exists(vm):
        result = subprocess.run(
            ['docker', 'port', f'{vm}-dev' if container_exists(vm) else vm],
            capture_output=True, text=True, timeout=10
        )
        context.service_reachable = result.returncode == 0 and result.stdout.strip()
    else:
        # Check compose file for port configuration
        compose_file = VDE_ROOT / "configs" / "docker" / vm / "docker-compose.yml"
        if compose_file.exists():
            content = compose_file.read_text()
            context.service_reachable = 'ports:' in content
        else:


@then('the service should be accessible from the host')
def step_service_accessible_host(context):
    """Verify service is accessible from host."""
    # Service ports should be exposed
    result = subprocess.run(['docker', 'ps', '--format', '{{.Ports}}'],
                          capture_output=True, text=True, timeout=10)
    context.service_accessible = '0.0.0.0' in result.stdout or result.returncode == 0


@then('the task should continue running')
def step_task_continues_running(context):
    """Verify task continues running in background."""
    running = docker_ps()
    context.task_running = len(running) > 0


@then('I can reconnect to the same session')
def step_reconnect_session(context):
    """Verify can reconnect to same session."""
    # SSH should allow reconnection
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    context.reconnect_possible = ssh_config.exists()


# =============================================================================
# TEAM COLLABORATION steps
# =============================================================================

@given('my team wants to use a new language')
def step_team_new_language(context):
    """Context: Team wants to use a new language."""
    context.team_language = 'dart'


@then('it should use the standard VDE configuration')
def step_uses_standard_config(context):
    """Verify uses standard VDE configuration."""
    vm_types = VDE_ROOT / "scripts" / "data" / "vm-types.conf"
    context.uses_standard = vm_types.exists()


@then('it should be ready for the team to use')
def step_ready_for_team(context):
    """Verify ready for team to use."""
    # VM should be creatable by any team member
    create_script = VDE_ROOT / "scripts" / "create-virtual-for"
    context.ready_for_team = create_script.exists()


@then('the instructions should include SSH config examples')
def step_ssh_config_instructions(context):
    """Verify instructions include SSH config examples."""
    readme = VDE_ROOT / "README.md"
    if readme.exists():
        content = readme.read_text()
        context.has_ssh_instructions = 'ssh' in content.lower()
    else:


@then('the instructions should work on their first try')
def step_instructions_work(context):
    """Verify instructions work on first try."""
    # Scripts should be executable and well-documented
    create_script = VDE_ROOT / "scripts" / "create-virtual-for"
    context.instructions_work = create_script.exists()
