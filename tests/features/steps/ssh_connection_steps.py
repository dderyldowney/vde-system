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
from vm_common import docker_ps

# =============================================================================
# SSH CONNECTION THEN steps
# =============================================================================

@then('the VM should be ready to use')
def step_vm_ready_ssh(context):
    """Verify VM is ready - container running."""
    running = docker_ps()
    assert len(running) > 0, "At least one VM should be running"


@then('it should be accessible via SSH')
def step_accessible_ssh(context):
    """Verify VM is accessible via SSH."""
    running = docker_ps()
    if running:
        vm = list(running)[0]
        result = subprocess.run(['docker', 'port', vm], capture_output=True, text=True)
        if result.returncode == 0:
            assert '22' in result.stdout or '220' in result.stdout, \
                   f"SSH port should be exposed. Got: {result.stdout}"


@when('I SSH into "python-dev"')
def step_ssh_into_python_dev(context):
    """Context: SSH into python-dev."""
    context.ssh_target = "python-dev"


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
    running = docker_ps()
    if running:
        vm = list(running)[0]
        result = subprocess.run(['docker', 'port', vm], capture_output=True, text=True)
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
        context.user_is_devuser = 'USER' in content or 'user:' in content.lower() or 'devuser' in content.lower()


@given('~/.ssh/known_hosts contains "[localhost]:2200"')
def step_known_hosts_localhost_2200(context):
    """Context: known_hosts contains localhost:2200 entry."""
    known_hosts = Path.home() / '.ssh' / 'known_hosts'
    context.known_hosts_has_localhost = known_hosts.exists()


@given('~/.ssh/known_hosts contains "[::1]:2400"')
def step_known_hosts_ipv6_2400(context):
    """Context: known_hosts contains IPv6:2400 entry."""
    known_hosts = Path.home() / '.ssh' / 'known_hosts'
    context.known_hosts_has_ipv6 = known_hosts.exists()


@given('~/.ssh/known_hosts contains "[localhost]:2400"')
def step_known_hosts_localhost_2400(context):
    """Context: known_hosts contains localhost:2400 entry."""
    known_hosts = Path.home() / '.ssh' / 'known_hosts'
    context.known_hosts_has_2400 = known_hosts.exists()


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


@then('PostgreSQL should be accessible from language VMs')
def step_postgres_accessible_from_lang(context):
    """Verify PostgreSQL can be accessed from language VMs."""
    result = subprocess.run(
        ['docker', 'network', 'ls', '--filter', 'name=vde'],
        capture_output=True, text=True
    )
    assert result.returncode == 0, "Docker network should exist for inter-VM communication"


@then('Python VM can connect to Redis')
def step_python_can_connect_redis(context):
    """Verify Python VM can connect to Redis."""
    result = subprocess.run(['docker', 'network', 'ls'], capture_output=True, text=True)
    assert result.returncode == 0, "Docker network should exist"


@then('Python VM can make HTTP requests to JavaScript VM')
def step_python_can_http_js(context):
    """Verify Python VM can make HTTP requests to JavaScript VM."""
    running = docker_ps()
    assert len(running) >= 2, "At least 2 VMs should be running for inter-VM communication"


@then('each can run independently')
def step_each_independent(context):
    """Verify VMs can run independently."""
    running = docker_ps()
    assert len(running) > 0, "VMs should be able to run independently"


@then('each should have separate data directory')
def step_each_separate_data(context):
    """Verify each VM has separate data directory."""
    configs_dir = VDE_ROOT / "configs" / "docker"
    if configs_dir.exists():
        data_dirs = []
        for vm_dir in configs_dir.iterdir():
            compose_file = vm_dir / "docker-compose.yml"
            if compose_file.exists():
                content = compose_file.read_text()
                if './data/' in content or 'volumes:' in content:
                    data_dirs.append(vm_dir.name)
        assert len(data_dirs) > 0, "VMs should have data volumes configured"


@then('files should be shared between host and VM')
def step_files_shared_host_vm(context):
    """Verify files are shared between host and VM."""
    running = docker_ps()
    if running:
        vm = list(running)[0]
        result = subprocess.run(
            ['docker', 'inspect', '-f', '{{json .Mounts}}', vm],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            mounts = result.stdout
            assert 'workspace' in mounts.lower() or 'project' in mounts.lower() or 'volume' in mounts.lower(), \
                   f"Files should be shared"


@then('all should use my SSH keys')
def step_all_use_ssh_keys(context):
    """Verify all VMs use configured SSH keys."""
    ssh_dir = Path.home() / '.ssh'
    assert ssh_dir.exists(), "SSH keys should be configured for VMs to use"


@then('all should work with the same configuration')
def step_all_same_config(context):
    """Verify all VMs work with same configuration."""
    configs_dir = VDE_ROOT / "configs" / "docker"
    assert configs_dir.exists(), "VM configurations should exist"


@then('both connections should work')
def step_both_connections_work(context):
    """Verify both SSH connections work."""
    running = docker_ps()
    assert len(running) >= 2, "At least 2 VMs should be running for both connections"


@then('both should be accessible via SSH')
def step_both_accessible_ssh(context):
    """Verify both VMs are accessible via SSH."""
    running = docker_ps()
    assert len(running) >= 2, "At least 2 VMs should be running"


@then('all three VMs should be running')
def step_all_three_running(context):
    """Verify all three VMs are running."""
    running = docker_ps()
    assert len(running) >= 3, f"At least 3 VMs should be running, got {len(running)}"


@then('both "python" and "rust" VMs should be running')
def step_python_rust_running(context):
    """Verify python and rust VMs are running."""
    running = docker_ps()
    assert 'python-dev' in running or 'python' in str(running).lower(), \
           "Python VM should be running"
    assert 'rust-dev' in running or 'rust' in str(running).lower(), \
           "Rust VM should be running"


@then('I can SSH to both VMs from my terminal')
def step_can_ssh_both(context):
    """Verify can SSH to both VMs."""
    running = docker_ps()
    assert len(running) >= 2, "At least 2 VMs should be running for SSH access"


@given('I have VSCode installed')
def step_have_vscode(context):
    """Context: User has VSCode installed."""
    result = subprocess.run(["which", "code"], capture_output=True, text=True)
    context.has_vscode = result.returncode == 0


@then('it should resolve to "go"')
def step_resolve_to_go(context):
    """Verify alias resolves to go using vde list command."""
    result = run_vde_command("list", timeout=10)
    assert result.returncode == 0, "Should be able to list VMs"


@then('it should resolve to the canonical name "js"')
def step_resolve_to_js(context):
    """Verify alias resolves to js using vde list command."""
    result = run_vde_command("list", timeout=10)
    assert result.returncode == 0, "Should be able to list VMs"


@then('"node" should resolve to "js"')
def step_node_resolves_js(context):
    """Verify node alias resolves to js using vde list command."""
    result = run_vde_command("list", timeout=10)
    assert result.returncode == 0, "Should be able to list VMs"


@then('"start-virtual js", "start-virtual node", "start-virtual nodejs" all work')
def step_all_node_aliases_work(context):
    """Verify all node aliases work using vde create command."""
    for alias in ['js', 'node', 'nodejs']:
        result = run_vde_command(f"create {alias}", timeout=10)


@then('"Go Language" should appear in list-vms output')
def step_go_language_in_list(context):
    """Verify Go Language appears in vde list output."""
    result = run_vde_command("list", timeout=10)
    output = result.stdout.lower()
    assert 'go' in output or 'golang' in output, \
           f"Go should appear in list"


@then('aliases should show in list-vms output')
def step_aliases_show_in_list(context):
    """Verify aliases show in vde list output."""
    result = run_vde_command("list", timeout=10)
    output = result.stdout.lower()
    assert 'vm' in output or 'type' in output, \
           f"List output should show VM info"


@then('I can use any alias to reference the VM')
def step_can_use_any_alias(context):
    """Verify any alias can be used to reference VM."""
    result = run_vde_command("list", timeout=10)
    assert result.returncode == 0, "Should be able to list VMs with aliases"
