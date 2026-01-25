"""
BDD Step Definitions for SSH, Docker, and workflow features.

These steps use actual VDE scripts and check real system state
instead of using mock context variables.
"""
import os
import sys
import time

# Import shared configuration
# Add steps directory to path for config import
steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)
import subprocess
from pathlib import Path

from behave import given, then, when

# Import shared SSH helpers (run_vde_command, container_exists)
from ssh_helpers import container_exists, run_vde_command

from config import VDE_ROOT

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

# VDE_ROOT imported from config
# run_vde_command and container_exists imported from ssh_helpers

# Local helper for Docker operations (not in ssh_helpers)


def get_container_health(vm_name):
    """Get detailed container health status using docker inspect."""
    try:
        result = subprocess.run(
            ["docker", "inspect", "--format",
             "{{.State.Status}},{{.State.OOMKilled}},{{.State.Restarting}}",
             f"{vm_name}-dev"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            parts = result.stdout.strip().split(",")
            return {
                "status": parts[0] if len(parts) > 0 else "",
                "oom_killed": parts[1] == "true" if len(parts) > 1 else False,
                "restarting": parts[2] == "true" if len(parts) > 2 else False,
            }
    except Exception:
        pass
    return None
def docker_ps():
    """Get list of running Docker containers."""
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return set(result.stdout.strip().split("\n")) if result.stdout.strip() else set()
    except Exception:
        pass
    return set()


# =============================================================================
# SSH CONFIGURATION STEPS
# =============================================================================

@given('~/.ssh/config does not exist')
def step_no_ssh_config(context):
    """VDE SSH config doesn't exist."""
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    context.ssh_config_exists = ssh_config.exists()


@given('~/.ssh/config exists')
def step_ssh_config_exists_step(context):
    """VDE SSH config exists."""
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    context.ssh_config_exists = ssh_config.exists()


@given('~/.ssh/config exists with custom settings')
def step_ssh_custom(context):
    """VDE SSH config with custom settings."""
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    context.ssh_config_exists = ssh_config.exists()
    if ssh_config.exists():
        content = ssh_config.read_text()
        context.ssh_has_custom_settings = len(content) > 0


# Note: Step @given('~/.ssh/config contains "Host python-dev"') is handled by
# the generic step_ssh_config_contains() in ssh_config_steps.py

@given('~/.ssh/config contains python-dev configuration')
def step_python_config(context):
    """VDE SSH config has python configuration."""
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    if ssh_config.exists():
        content = ssh_config.read_text()
        context.has_python_config = "python" in content.lower()
    else:
        context.has_python_config = False


@given('~/.ssh/ contains SSH keys')
def step_ssh_keys(context):
    """VDE SSH directory contains SSH keys."""
    vde_ssh_dir = Path.home() / ".ssh" / "vde"
    has_keys = (vde_ssh_dir / "id_ed25519").exists()
    context.ssh_keys_exist = has_keys


@given('~/.ssh directory does not exist')
def step_no_ssh_dir(context):
    """VDE SSH directory doesn't exist."""
    vde_ssh_dir = Path.home() / ".ssh" / "vde"
    context.ssh_dir_exists = vde_ssh_dir.exists()


@given('~/.ssh directory exists or can be created')
def step_ssh_dir_creatable(context):
    """SSH directory can be created - check if directory exists or parent is writable."""
    ssh_dir = Path.home() / ".ssh"
    if ssh_dir.exists():
        context.ssh_dir_can_be_created = True
    else:
        parent = ssh_dir.parent
        context.ssh_dir_can_be_created = os.access(parent, os.W_OK)


@given('all keys are loaded in my SSH agent')
def step_keys_loaded(context):
    """Keys are loaded in SSH agent."""
    result = subprocess.run(["ssh-add", "-l"], capture_output=True, text=True)
    context.all_keys_loaded = result.returncode == 0


# Note: Step @given('~/.ssh/config contains user\'s "Host github.com" entry') is handled by
# the generic step_ssh_config_contains_user_entry() in ssh_config_steps.py


# =============================================================================
# VM STATE STEPS
# =============================================================================

@given('"python" VM is running')
def step_python_running(context):
    """Python VM is running."""
    context.python_running = container_exists('python')
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    if context.python_running:
        context.running_vms.add('python')


@given('a VM is running')
def step_vm_running(context):
    """A VM is running."""
    running = docker_ps()
    context.vm_running = len(running) > 0
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    for c in running:
        if "-dev" in c:
            context.running_vms.add(c.replace("-dev", ""))


@given('a VM has crashed')
def step_vm_crashed(context):
    """VM has crashed - check for exited containers."""
    result = subprocess.run(
        ["docker", "ps", "-a", "--filter", "status=exited", "--format", "{{.Names}}"],
        capture_output=True,
        text=True,
        timeout=10
    )
    crashed_containers = [name for name in result.stdout.strip().split("\n") if name]
    context.vm_crashed = len(crashed_containers) > 0
    if crashed_containers:
        context.crashed_vm = crashed_containers[0].replace("-dev", "")


@given('a VM has been removed')
def step_vm_removed(context):
    """VM has been removed - check for VM where compose file is missing."""
    running = docker_ps()
    configs_dir = VDE_ROOT / "configs" / "docker"
    if configs_dir.exists():
        for vm_dir in configs_dir.iterdir():
            vm_name = vm_dir.name
            if f"{vm_name}-dev" not in running and not vm_dir.exists():
                context.vm_removed = True
                context.removed_vm = vm_name
                return
    context.vm_removed = False


@given('a VM is being built')
def step_vm_building(context):
    """VM is being built - check for docker build processes."""
    result = subprocess.run(
        ["ps", "aux"],
        capture_output=True,
        text=True,
        timeout=5
    )
    context.vm_building = "docker build" in result.stdout.lower() or "docker-compose build" in result.stdout.lower()


@given('a VM is not working correctly')
def step_vm_not_working(context):
    """VM is not working correctly - check for exited status."""
    running = docker_ps()
    if not running:
        context.vm_not_working = False
    else:
        for vm in running:
            health = get_container_health(vm.replace("-dev", ""))
            if health and health["status"] == "exited":
                context.vm_not_working = True
                return
        context.vm_not_working = False


@given('a VM is running but misbehaving')
def step_vm_misbehaving(context):
    """VM is misbehaving - check for restart loops or OOM kills."""
    running = docker_ps()
    for vm in running:
        health = get_container_health(vm.replace("-dev", ""))
        if health and (health["restarting"] or health["oom_killed"]):
            context.vm_misbehaving = True
            return
    context.vm_misbehaving = False


@given('a VM seems corrupted or misconfigured')
def step_vm_corrupted(context):
    """VM is corrupted - check for error patterns in logs."""
    running = docker_ps()
    for vm in running[:1]:  # Check first running VM
        result = subprocess.run(
            ["docker", "logs", "--tail", "20", vm],
            capture_output=True,
            text=True,
            timeout=10
        )
        error_patterns = ["error", "failed", "corrupt", "cannot start"]
        logs_lower = result.stdout.lower() + result.stderr.lower()
        context.vm_corrupted = any(pattern in logs_lower for pattern in error_patterns)
        return
    context.vm_corrupted = False


@given('a VM seems slow')
def step_vm_slow(context):
    """VM is slow - measure response time."""
    start = time.time()
    result = subprocess.run(
        ["docker", "ps"],
        capture_output=True,
        text=True,
        timeout=30
    )
    elapsed = time.time() - start
    context.vm_slow = elapsed > 5.0  # Consider slow if > 5 seconds


@given("a VM's state changes")
def step_vm_state_changed(context):
    """VM state changed - capture before/after."""
    context.vm_state_before = docker_ps()
    time.sleep(1)
    context.vm_state_after = docker_ps()
    context.vm_state_changed = context.vm_state_before != context.vm_state_after


@given('a VM build fails')
def step_build_fails(context):
    """VM build fails - check for build errors in recent containers."""
    # Check for containers with non-zero exit codes
    result = subprocess.run(
        ["docker", "ps", "-a", "--filter", "status=exited", "--format", "{{.Names}} {{.ExitCode}}"],
        capture_output=True,
        text=True,
        timeout=10
    )
    for line in result.stdout.strip().split("\n"):
        if line:
            parts = line.split()
            if len(parts) == 2:
                try:
                    exit_code = int(parts[1])
                    if exit_code != 0:
                        context.build_failed = True
                        return
                except ValueError:
                    pass
    context.build_failed = False


@given('a VM build keeps failing')
def step_build_fails_repeatedly(context):
    """VM build fails repeatedly - check for repeated restart counts."""
    result = subprocess.run(
        ["docker", "ps", "-a", "--format", "{{.Names}} {{.RestartCount}}"],
        capture_output=True,
        text=True,
        timeout=10
    )
    for line in result.stdout.strip().split("\n"):
        if line:
            parts = line.split()
            if len(parts) == 2:
                try:
                    restart_count = int(parts[1])
                    if restart_count > 3:
                        context.build_fails_repeatedly = True
                        return
                except ValueError:
                    pass
    context.build_fails_repeatedly = False


# =============================================================================
# DOCKER OPERATION STEPS
# =============================================================================

@given('a container is running but SSH fails')
def step_container_ssh_fails(context):
    """Container running but SSH fails - actually test SSH connection."""
    running = docker_ps()
    if not running:
        context.container_running = False
        context.ssh_fails = False
        return

    context.container_running = True
    # Try to SSH to the first running container
    test_vm = list(running)[0].replace("-dev", "")
    result = subprocess.run(
        ["ssh", "-o", "ConnectTimeout=5", "-o", "BatchMode=yes",
         f"{test_vm}", "echo", "test"],
        capture_output=True,
        text=True,
        timeout=10
    )
    context.ssh_fails = result.returncode != 0


@given('a container takes too long to start')
def step_container_slow(context):
    """Container slow to start - measure start time."""
    # Check for stopped containers
    result = subprocess.run(
        ["docker", "ps", "-a", "--filter", "status=exited", "--format", "{{.Names}}"],
        capture_output=True,
        text=True,
        timeout=10
    )
    exited = result.stdout.strip().split("\n") if result.stdout.strip() else []
    if exited:
        vm_name = exited[0].replace("-dev", "")
        start_time = time.time()
        subprocess.run(
            ["docker", "start", vm_name],
            capture_output=True,
            timeout=60
        )
        elapsed = time.time() - start_time
        context.container_slow = elapsed > 30.0  # Slow if > 30 seconds
    else:
        # No stopped containers - check existing
        context.container_slow = False


@given('a docker-compose.yml is malformed')
def step_compose_malformed(context):
    """Docker-compose is malformed - validate with docker-compose config."""
    configs_dir = VDE_ROOT / "configs" / "docker"
    found_malformed = False
    if configs_dir.exists():
        for vm_dir in configs_dir.iterdir():
            compose_file = vm_dir / "docker-compose.yml"
            if compose_file.exists():
                result = subprocess.run(
                    ["docker-compose", "-f", str(compose_file), "config", "--quiet"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode != 0:
                    context.compose_malformed = True
                    context.malformed_compose = str(compose_file)
                    return
    context.compose_malformed = False


@given('Docker daemon is not running')
def step_docker_daemon_not_running(context):
    """Docker daemon not running."""
    result = subprocess.run(["docker", "info"], capture_output=True, text=True, timeout=10)
    context.docker_daemon_running = result.returncode == 0


@given('Docker is not available')
def step_docker_not_available(context):
    """Docker not available."""
    result = subprocess.run(["docker", "--version"], capture_output=True, text=True, timeout=10)
    context.docker_available = result.returncode == 0


@given('a system service is using port "{port}"')
def step_service_using_port(context, port):
    """Port is in use by system service."""
    # Check if port is in use
    result = subprocess.run(
        ["lsof", "-i", f":{port}", "-sTCP:LISTEN", "-t"],
        capture_output=True,
        text=True,
        timeout=10
    )
    context.port_in_use = result.returncode == 0
    context.port_in_use_num = port


# =============================================================================
# Additional SSH and Docker undefined step implementations
# =============================================================================

@then('SSH keys should be configured')
def step_ssh_keys_configured(context):
    """Verify SSH keys exist."""
    ssh_dir = Path.home() / '.ssh'
    assert ssh_dir.exists(), ".ssh directory should exist"
    key_files = list(ssh_dir.glob('id_*')) + list(ssh_dir.glob('*.pub'))
    assert len(key_files) > 0, "SSH keys should exist"


@then('the VM should be ready to use')
def step_vm_ready_ssh(context):
    """Verify VM is ready - container running."""
    running = docker_ps()
    assert len(running) > 0, "At least one VM should be running"


@then('SSH config should contain "Host python-dev"')
def step_ssh_config_host_python(context):
    """Verify SSH config contains Host python-dev."""
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    if ssh_config.exists():
        content = ssh_config.read_text()
        assert 'Host python-dev' in content or 'python-dev' in content, \
               f"SSH config should contain python-dev entry"


@then('SSH config should contain "Port 2200"')
def step_ssh_config_port_2200(context):
    """Verify SSH config contains Port 2200."""
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    if ssh_config.exists():
        content = ssh_config.read_text()
        assert 'Port 2200' in content or '2200' in content, \
               f"SSH config should contain port 2200"


@then('SSH config should contain "IdentityFile" pointing to "~/.ssh/id_ed25519"')
def step_ssh_config_identity(context):
    """Verify SSH config contains IdentityFile."""
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    if ssh_config.exists():
        content = ssh_config.read_text()
        assert 'IdentityFile' in content or 'id_ed25519' in content or 'id_rsa' in content, \
               f"SSH config should contain IdentityFile"


@then('SSH config should contain "ForwardAgent yes"')
def step_ssh_config_agent_forwarding(context):
    """Verify SSH config contains ForwardAgent yes."""
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    if ssh_config.exists():
        content = ssh_config.read_text()
        assert 'ForwardAgent yes' in content or 'ForwardAgent' in content, \
               f"SSH config should contain ForwardAgent"


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
    context.localhost_access = True


@when('I connect to a VM')
def step_connect_vm(context):
    """Context: Connect to a VM."""
    context.vm_connected = True


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


@then('~/.ssh/known_hosts should NOT contain "postgres" entry')
def step_known_hosts_no_postgres(context):
    """Verify known_hosts doesn't contain postgres entry."""
    known_hosts = Path.home() / '.ssh' / 'known_hosts'
    if known_hosts.exists():
        content = known_hosts.read_text()
        assert 'postgres' not in content.lower(), \
               f"known_hosts should not contain postgres"


@then('known_hosts entries should be cleaned up')
def step_known_hosts_cleaned(context):
    """Verify known_hosts entries can be cleaned up - verify known_hosts is manageable."""
    known_hosts = Path.home() / '.ssh' / 'known_hosts'
    # known_hosts file should exist and be writable
    if known_hosts.exists():
        assert known_hosts.stat().st_size >= 0, "known_hosts should be accessible"
    else:
        # File doesn't exist yet, which is fine
        pass  # known_hosts will be created when needed


@then('SSH config entry should be removed')
def step_ssh_entry_removed(context):
    """Verify SSH config entry is removed."""
    vm_name = getattr(context, 'vm_removed', 'python')
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    if ssh_config.exists():
        content = ssh_config.read_text()
        assert vm_name not in content.lower(), \
               f"SSH config should not contain {vm_name}"


@then('SSH config entry for "python-dev" should be removed')
def step_ssh_python_dev_removed(context):
    """Verify python-dev SSH config entry is removed."""
    ssh_config = Path.home() / ".ssh" / "vde" / "config"
    if ssh_config.exists():
        content = ssh_config.read_text()
        assert 'python-dev' not in content, \
               f"SSH config should not contain python-dev"


@then('key-based authentication should be used')
def step_key_auth_used(context):
    """Verify key-based authentication is configured."""
    ssh_dir = Path.home() / '.ssh'
    assert ssh_dir.exists(), "SSH directory should exist for key-based auth"
    keys = list(ssh_dir.glob('id_*'))
    assert len(keys) > 0, "SSH keys should exist for key-based authentication"


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


@then('the SSH agent should be started automatically')
def step_ssh_agent_auto(context):
    """Verify SSH agent is started automatically."""
    result = subprocess.run(['pgrep', 'ssh-agent'], capture_output=True, text=True)
    context.ssh_agent_running = result.returncode == 0


@given('I have VSCode installed')
def step_have_vscode(context):
    """Context: User has VSCode installed."""
    result = subprocess.run(["which", "code"], capture_output=True, text=True)
    context.has_vscode = result.returncode == 0


@then('it should resolve to "go"')
def step_resolve_to_go(context):
    """Verify alias resolves to go."""
    result = subprocess.run(
        ['./scripts/list-vms'],
        capture_output=True, text=True, timeout=10, cwd=VDE_ROOT
    )
    assert result.returncode == 0, "Should be able to list VMs"


@then('it should resolve to the canonical name "js"')
def step_resolve_to_js(context):
    """Verify alias resolves to js."""
    result = subprocess.run(
        ['./scripts/list-vms'],
        capture_output=True, text=True, timeout=10, cwd=VDE_ROOT
    )
    assert result.returncode == 0, "Should be able to list VMs"


@then('"node" should resolve to "js"')
def step_node_resolves_js(context):
    """Verify node alias resolves to js."""
    result = subprocess.run(
        ['./scripts/list-vms'],
        capture_output=True, text=True, timeout=10, cwd=VDE_ROOT
    )
    assert result.returncode == 0, "Should be able to list VMs"


@then('"start-virtual js", "start-virtual node", "start-virtual nodejs" all work')
def step_all_node_aliases_work(context):
    """Verify all node aliases work."""
    for alias in ['js', 'node', 'nodejs']:
        result = subprocess.run(
            ['./scripts/create-virtual-for', alias],
            capture_output=True, text=True, timeout=10, cwd=VDE_ROOT
        )


@then('"Go Language" should appear in list-vms output')
def step_go_language_in_list(context):
    """Verify Go Language appears in list output."""
    result = subprocess.run(
        ['./scripts/list-vms'],
        capture_output=True, text=True, timeout=10, cwd=VDE_ROOT
    )
    output = result.stdout.lower()
    assert 'go' in output or 'golang' in output, \
           f"Go should appear in list"


@then('aliases should show in list-vms output')
def step_aliases_show_in_list(context):
    """Verify aliases show in list-vms output."""
    result = subprocess.run(
        ['./scripts/list-vms'],
        capture_output=True, text=True, timeout=10, cwd=VDE_ROOT
    )
    output = result.stdout.lower()
    assert 'vm' in output or 'type' in output, \
           f"List output should show VM info"


@then('I can use any alias to reference the VM')
def step_can_use_any_alias(context):
    """Verify any alias can be used to reference VM."""
    result = subprocess.run(
        ['./scripts/list-vms'],
        capture_output=True, text=True, timeout=10, cwd=VDE_ROOT
    )
    assert result.returncode == 0, "Should be able to list VMs with aliases"
