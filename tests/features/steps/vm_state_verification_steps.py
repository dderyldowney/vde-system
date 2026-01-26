"""
BDD Step Definitions for VM State Verification.

These steps verify VM states including running, crashed, building, etc.
"""
import subprocess
import sys
import time

# Import shared configuration
steps_dir = sys.path.insert(0, steps_dir) if (steps_dir := __import__('os').path.dirname(__import__('os').path.abspath(__file__))) not in sys.path else None
from pathlib import Path

from behave import given

from config import VDE_ROOT
from vm_common import get_container_health, docker_ps, container_exists

# =============================================================================
# VM STATE GIVEN steps
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
# DOCKER OPERATION GIVEN steps
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
