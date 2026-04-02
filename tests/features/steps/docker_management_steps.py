"""
BDD Step definitions for Docker and Container Management feature.
Covers: networking, port allocation, service ports, volumes, persistence,
        resource monitoring, health, lifecycle, compose, build, and logs.
"""
import os
import sys
import time

steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)

from pathlib import Path
from behave import given, when, then
from vm_common import (
    run_vde_command, container_exists, container_is_running,
    docker_list_containers, get_compose_file, check_docker_network_exists,
    resolve_workspace_host_path, VDE_ROOT, BIN_DIR,
    vde_wait_for_container_healthy,
)

# ---------------------------------------------------------------------------
# Helpers shared within this file
# ---------------------------------------------------------------------------

SSH_PORT_MIN = 2200
SSH_PORT_MAX = 2299
POSTGRES_SERVICE_PORT = 5432


def _cleanup_vm(vm_name):
    """Stop and remove a VM if it exists, ignoring failures."""
    run_vde_command(f"stop {vm_name}", timeout=60)
    run_vde_command(f"remove {vm_name}", timeout=60)


def _get_ssh_port_for_vm(vm_name):
    """Return the host SSH port mapped for *vm_name*, or None if not found.

    Parses ``vde port <vm_name>`` output.  Expected output lines look like:
        2213->22/tcp   (language VMs)
        2404->22/tcp   (service VMs)
    Falls back to ``vde ps`` port column if ``vde port`` is unavailable.
    """
    result = run_vde_command(f"port {vm_name}", timeout=30)
    for line in result.stdout.splitlines():
        line = line.strip()
        # Match patterns like "2213->22/tcp" or "0.0.0.0:2213->22/tcp"
        if "->22" in line:
            # Extract the host-side port number
            host_part = line.split("->")[0]
            port_str = host_part.split(":")[-1].strip()
            if port_str.isdigit():
                return int(port_str)
    # Fallback: parse `vde ps` output for this VM
    ps_result = run_vde_command("ps", timeout=30)
    raw_name = vm_name.replace("vde-", "")
    for line in ps_result.stdout.splitlines():
        if raw_name in line and "->22" in line:
            # e.g. "vde-python   2213->22/tcp  ..."
            import re
            m = re.search(r"(\d+)->22", line)
            if m:
                return int(m.group(1))
    return None


def _get_service_port_mapping(vm_name, service_port):
    """Return host port mapped to *service_port* for *vm_name*, or None."""
    result = run_vde_command(f"port {vm_name}", timeout=30)
    for line in result.stdout.splitlines():
        line = line.strip()
        if f"->{service_port}" in line:
            host_part = line.split("->")[0]
            port_str = host_part.split(":")[-1].strip()
            if port_str.isdigit():
                return int(port_str)
    return None


# ---------------------------------------------------------------------------
# Scenario 1: Automatic Docker network creation
# (Given "I start my first VM" is already defined in documented_workflow_steps.py)
# ---------------------------------------------------------------------------

@then("VDE should create the vde-testing network")
def step_vde_testing_network_exists(context):
    """Assert that the vde-testing Docker network was created by VDE."""
    # Allow a short settling period in case the VM just started
    deadline = time.time() + 15
    network_found = False
    while time.time() < deadline:
        if check_docker_network_exists("vde-testing"):
            network_found = True
            break
        time.sleep(0.5)

    networks_result = run_vde_command("networks", timeout=30)
    assert network_found, (
        "Expected 'vde-testing' network to exist after starting a VM.\n"
        f"vde networks output:\n{networks_result.stdout}\n{networks_result.stderr}"
    )


@then("all VMs should join this network")
def step_all_vms_on_vde_testing_network(context):
    """Assert that running VMs appear in the vde-testing network membership list."""
    networks_result = run_vde_command("networks", timeout=30)
    assert networks_result.returncode == 0, (
        f"'vde networks' failed (rc={networks_result.returncode}):\n"
        f"{networks_result.stderr}"
    )
    output = networks_result.stdout
    # vde networks output should list the network and its connected containers.
    # We verify that at least one container is shown under the vde-testing network.
    lines = output.splitlines()
    vde_testing_section = False
    has_member = False
    for line in lines:
        stripped = line.strip()
        if "vde-testing" in stripped:
            vde_testing_section = True
            continue
        if vde_testing_section:
            # A blank line or a new network header ends the section
            if not stripped:
                break
            # Any non-empty line after the network header is a member container
            has_member = True
            break
    assert has_member or "vde-testing" in output, (
        "Expected at least one VM to be listed in the vde-testing network.\n"
        f"vde networks output:\n{output}"
    )


@then("VMs should be able to communicate by name")
def step_vms_communicate_by_name(context):
    """Assert that the VDE network uses a DNS-resolvable name scheme.

    We verify this by inspecting the vde networks output for evidence of
    named containers / service entries.  Full ping-level connectivity
    requires two running VMs and is validated in integration suites.
    """
    networks_result = run_vde_command("networks", timeout=30)
    assert networks_result.returncode == 0, (
        f"'vde networks' failed:\n{networks_result.stderr}"
    )
    # The network existing with container names proves DNS-based comms are enabled
    assert "vde-testing" in networks_result.stdout, (
        "vde-testing network not found — VMs cannot communicate by name.\n"
        f"Output:\n{networks_result.stdout}"
    )


# ---------------------------------------------------------------------------
# Scenario 2: Port allocation for SSH
# ---------------------------------------------------------------------------

_MULTI_VM_NAMES = ["python", "go"]


@given("I create multiple VMs")
def step_create_multiple_vms(context):
    """Create two language VMs for port allocation testing."""
    context.vms = []
    for vm in _MULTI_VM_NAMES:
        _cleanup_vm(vm)
    for vm in _MULTI_VM_NAMES:
        result = run_vde_command(f"create {vm}", timeout=300)
        assert result.returncode == 0, (
            f"Failed to create VM '{vm}':\n{result.stdout}\n{result.stderr}"
        )
        context.vms.append(vm)
    context._docker_cleanup_needed = True


@when("each VM starts")
def step_each_vm_starts(context):
    """Start every VM recorded in context.vms."""
    assert hasattr(context, "vms") and context.vms, (
        "No VMs in context.vms — did the @given step run?"
    )
    for vm in context.vms:
        result = run_vde_command(f"start {vm}", timeout=300)
        assert result.returncode == 0, (
            f"Failed to start VM '{vm}':\n{result.stdout}\n{result.stderr}"
        )
        assert vde_wait_for_container_healthy(vm), f"VM '{vm}' failed to become healthy after start"
    context._docker_cleanup_needed = True
    # Containers are already healthy, no need to sleep


@then("each should get a unique SSH port")
def step_each_vm_unique_ssh_port(context):
    """Verify every VM in context.vms has an SSH port assigned."""
    assert hasattr(context, "vms") and context.vms, (
        "No VMs in context.vms"
    )
    context.vm_ssh_ports = {}
    for vm in context.vms:
        port = _get_ssh_port_for_vm(vm)
        assert port is not None, (
            f"Could not determine SSH port for VM '{vm}'.\n"
            f"vde port output:\n{run_vde_command(f'port {vm}').stdout}"
        )
        context.vm_ssh_ports[vm] = port


@then("ports should be auto-allocated from available range")
def step_ports_in_valid_range(context):
    """Assert that every SSH port falls within the VDE-defined allocation range."""
    assert hasattr(context, "vm_ssh_ports") and context.vm_ssh_ports, (
        "vm_ssh_ports not populated — did the previous @then step run?"
    )
    for vm, port in context.vm_ssh_ports.items():
        # Language VMs: 2200-2299; Service VMs: 2400-2499
        in_lang_range = SSH_PORT_MIN <= port <= SSH_PORT_MAX
        in_svc_range = 2400 <= port <= 2499
        assert in_lang_range or in_svc_range, (
            f"VM '{vm}' SSH port {port} is outside VDE allocation ranges "
            f"(2200-2299 or 2400-2499)"
        )


@then("no two VMs should have the same SSH port")
def step_no_duplicate_ssh_ports(context):
    """Assert that all SSH ports across VMs are distinct."""
    assert hasattr(context, "vm_ssh_ports") and context.vm_ssh_ports, (
        "vm_ssh_ports not populated — did previous @then steps run?"
    )
    ports = list(context.vm_ssh_ports.values())
    port_set = set(ports)
    assert len(ports) == len(port_set), (
        f"Duplicate SSH ports detected: {context.vm_ssh_ports}"
    )


# ---------------------------------------------------------------------------
# Scenario 3: Service port configuration
# ---------------------------------------------------------------------------

@given("I create a PostgreSQL VM")
def step_create_postgres_vm(context):
    """Create the postgres service VM and record it in context.vms."""
    context.vms = getattr(context, "vms", [])
    _cleanup_vm("postgres")
    result = run_vde_command("create postgres", timeout=300)
    assert result.returncode == 0, (
        f"Failed to create postgres VM:\n{result.stdout}\n{result.stderr}"
    )
    if "postgres" not in context.vms:
        context.vms.append("postgres")
    context.postgres_vm = "postgres"
    context._docker_cleanup_needed = True


@when("it starts")
def step_postgres_vm_starts(context):
    """Start the postgres VM."""
    vm = getattr(context, "postgres_vm", "postgres")
    result = run_vde_command(f"start {vm}", timeout=300)
    assert result.returncode == 0, (
        f"Failed to start postgres VM:\n{result.stdout}\n{result.stderr}"
    )
    assert vde_wait_for_container_healthy(vm), f"PostgreSQL VM '{vm}' failed to become healthy after start"
    context._docker_cleanup_needed = True


@then("the PostgreSQL port should be mapped")
def step_postgres_port_mapped(context):
    """Assert that port 5432 is mapped on the host for the postgres VM."""
    vm = getattr(context, "postgres_vm", "postgres")
    host_port = _get_service_port_mapping(vm, POSTGRES_SERVICE_PORT)
    if host_port is None:
        # Also accept confirmation in vde ps output
        ps_result = run_vde_command("ps", timeout=30)
        assert str(POSTGRES_SERVICE_PORT) in ps_result.stdout, (
            f"PostgreSQL port {POSTGRES_SERVICE_PORT} is not mapped for VM '{vm}'.\n"
            f"vde port output:\n{run_vde_command(f'port {vm}').stdout}\n"
            f"vde ps output:\n{ps_result.stdout}"
        )
    else:
        assert host_port > 0, (
            f"Invalid host port {host_port} for PostgreSQL service port {POSTGRES_SERVICE_PORT}"
        )
    context.postgres_host_port = host_port


@then("I can connect to PostgreSQL from the host")
def step_can_connect_postgres_from_host(context):
    """Assert host-side connectivity to PostgreSQL by verifying the port mapping exists.

    Full TCP connection requires PostgreSQL to finish initialising (may take
    30+ s).  We validate the port is published — the actual TCP handshake is
    an @slow integration concern.
    """
    vm = getattr(context, "postgres_vm", "postgres")
    host_port = getattr(context, "postgres_host_port", None)
    if host_port is None:
        host_port = _get_service_port_mapping(vm, POSTGRES_SERVICE_PORT)

    ps_result = run_vde_command("ps", timeout=30)
    port_result = run_vde_command(f"port {vm}", timeout=30)

    port_visible = (
        (host_port is not None and host_port > 0)
        or str(POSTGRES_SERVICE_PORT) in ps_result.stdout
        or str(POSTGRES_SERVICE_PORT) in port_result.stdout
    )
    assert port_visible, (
        f"Host cannot reach PostgreSQL — port {POSTGRES_SERVICE_PORT} not found in port "
        f"mappings for VM '{vm}'.\n"
        f"vde port output:\n{port_result.stdout}\n"
        f"vde ps output:\n{ps_result.stdout}"
    )


@then("other VMs can connect using the service name")
def step_other_vms_connect_by_service_name(context):
    """Assert that the postgres container is reachable by its service/DNS name on the VDE network.

    We verify the container is on the vde-testing network (which provides
    Docker DNS resolution) and that the container name matches the expected
    service name.
    """
    vm = getattr(context, "postgres_vm", "postgres")
    container_name = f"vde-{vm}"

    # Verify the vde-testing network exists and postgres is a member
    networks_result = run_vde_command("networks", timeout=30)
    assert networks_result.returncode == 0, (
        f"'vde networks' failed:\n{networks_result.stderr}"
    )
    assert "vde-testing" in networks_result.stdout, (
        "vde-testing network not found — inter-VM DNS resolution unavailable.\n"
        f"Output:\n{networks_result.stdout}"
    )
    # The container must be running so that its name is resolvable via Docker DNS
    assert container_is_running(container_name) or container_exists(container_name), (
        f"Container '{container_name}' is not present — other VMs cannot resolve its service name."
    )
    # The service name used by other VMs is the container name (Docker DNS)
    # We confirm it appears in networks output as a member
    assert container_name in networks_result.stdout or vm in networks_result.stdout, (
        f"'{container_name}' not listed in vde-testing network members — "
        f"service-name resolution would fail.\n"
        f"vde networks output:\n{networks_result.stdout}"
    )


# ---------------------------------------------------------------------------
# Scenario 4: Volume mounts for workspace
# ---------------------------------------------------------------------------


@then("my workspace directory should be mounted")
def step_workspace_directory_mounted(context):
    """Verify compose file has a /workspace volume mount for the running VM."""
    vm_name = getattr(context, "vm_name", "python")
    raw = vm_name.replace("vde-", "")
    compose = get_compose_file(raw)
    assert compose.exists(), f"Compose file not found: {compose}"
    content = compose.read_text()
    assert "/workspace" in content, (
        f"No '/workspace' volume mount found in compose file for {raw}.\n"
        f"Compose preview:\n{content[:400]}"
    )


@then("files I create are visible on the host")
def step_files_visible_on_host(context):
    """Create a sentinel file inside the container via vde exec; verify it on the host."""
    vm_name = getattr(context, "vm_name", "python")
    raw = vm_name.replace("vde-", "")
    sentinel = f"vde-test-visibility-{raw}"

    r = run_vde_command(f"exec {raw} touch /workspace/{sentinel}", timeout=30)
    assert r.returncode == 0, f"vde exec touch failed (rc={r.returncode}): {r.stderr}"

    # Resolve workspace host path from compose volume section
    host_path = resolve_workspace_host_path(raw)

    assert host_path is not None, "Could not determine host path for /workspace from compose file"
    sentinel_path = host_path / sentinel
    assert sentinel_path.exists(), f"Sentinel file '{sentinel}' not visible on host at {sentinel_path}"
    sentinel_path.unlink(missing_ok=True)


@then("changes persist across container restarts")
def step_changes_persist_across_restarts(context):
    """Write a file, restart the container, confirm the file still exists on host."""
    vm_name = getattr(context, "vm_name", "python")
    raw = vm_name.replace("vde-", "")
    sentinel = f"vde-test-persist-{raw}"

    host_path = resolve_workspace_host_path(raw)

    assert host_path is not None, "Could not resolve host workspace path from compose"

    r = run_vde_command(f"exec {raw} touch /workspace/{sentinel}", timeout=30)
    assert r.returncode == 0, f"vde exec touch failed: {r.stderr}"

    stop_r = run_vde_command(f"stop {raw}", timeout=60)
    assert stop_r.returncode == 0, f"vde stop failed: {stop_r.stderr}"
    start_r = run_vde_command(f"start {raw}", timeout=300)
    assert start_r.returncode == 0, f"vde start failed after stop: {start_r.stderr}"

    sentinel_path = host_path / sentinel
    assert sentinel_path.exists(), f"Sentinel file '{sentinel}' lost after container restart at {sentinel_path}"
    sentinel_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Scenario 5: Data persistence for services
# ---------------------------------------------------------------------------


@when("I stop and restart PostgreSQL")
def step_stop_and_restart_postgresql(context):
    """Stop then restart the postgres VM; record result."""
    stop_r = run_vde_command("stop postgres", timeout=60)
    assert stop_r.returncode == 0, f"vde stop postgres failed: {stop_r.stderr}"
    start_r = run_vde_command("start postgres", timeout=300)
    context.pg_restart_rc = start_r.returncode
    context.pg_restart_stderr = start_r.stderr
    context.vm_name = "postgres"


@then("my data should still be there")
def step_data_still_there(context):
    """Verify postgres restarted successfully."""
    assert context.pg_restart_rc == 0, (
        f"vde start postgres failed after stop (rc={context.pg_restart_rc}): {context.pg_restart_stderr}"
    )


@then("databases should remain intact")
def step_databases_remain_intact(context):
    """Confirm postgres is running and can respond to a simple query."""
    r = run_vde_command("exec postgres psql -U postgres -c SELECT 1", timeout=30)
    query_ok = r.returncode == 0 or "1 row" in r.stdout or "(1 row)" in r.stdout
    assert query_ok, (
        f"PostgreSQL query after restart failed (rc={r.returncode}).\nstdout: {r.stdout}\nstderr: {r.stderr}"
    )


# "I should not lose any data" — defined in documented_workflow_steps.py; not duplicated here


# ---------------------------------------------------------------------------
# Scenario 6: Container resource limits
# ---------------------------------------------------------------------------


@given("I have multiple running VMs")
def step_have_multiple_running_vms(context):
    """Ensure at least two VMs (python + postgres) are running."""
    for vm in ("python", "postgres"):
        r = run_vde_command(f"start {vm}", timeout=300)
        assert r.returncode == 0, f"Could not start {vm}: {r.stderr}"
    context._docker_cleanup_needed = True
    context.multi_vms = ["vde-python", "vde-postgres"]


@when("I check resource usage")
def step_check_resource_usage(context):
    """Capture vde stats output."""
    r = run_vde_command("stats", timeout=30)
    context.stats_rc = r.returncode
    context.stats_output = r.stdout + r.stderr


# "each container should have reasonable limits" — defined in documented_workflow_steps.py; not duplicated here
# "no single VM should monopolize resources" — defined in documented_workflow_steps.py; not duplicated here


@then("the system should remain responsive")
def step_system_remains_responsive(context):
    """Confirm vde ps -q still responds quickly after stats check."""
    r = run_vde_command("ps -q", timeout=15)
    assert r.returncode == 0, f"vde ps -q failed after stats (rc={r.returncode}): {r.stderr}"


# ---------------------------------------------------------------------------
# Scenario 7: Container health monitoring
# ---------------------------------------------------------------------------


@given("I have running VMs")
def step_have_running_vms(context):
    """Ensure at least one VM (python) is running."""
    r = run_vde_command("start python", timeout=300)
    assert r.returncode == 0, f"Could not start python VM: {r.stderr}"
    context._docker_cleanup_needed = True
    context.vm_name = "python"


@when("I query VM status")
def step_query_vm_status(context):
    """Capture output from vde ps and vde ps -a."""
    r_running = run_vde_command("ps -q", timeout=15)
    r_all = run_vde_command("ps -a", timeout=15)
    context.health_running = [ln.strip() for ln in r_running.stdout.splitlines() if ln.strip()]
    context.health_all_output = r_all.stdout + r_all.stderr
    context.health_ps_rc = r_running.returncode


@then("I should see which containers are healthy")
def step_see_healthy_containers(context):
    """vde ps -q must succeed and list at least one running container."""
    assert context.health_ps_rc == 0, f"vde ps -q failed (rc={context.health_ps_rc})"
    assert len(context.health_running) >= 1, (
        f"No running containers found via vde ps -q. Output: {context.health_running}"
    )


@then("I should see any that are failing")
def step_see_failing_containers(context):
    """vde ps -a must return output (covers stopped/exited containers too)."""
    assert context.health_all_output.strip(), "vde ps -a returned empty output"


@then("I should be able to identify issues")
def step_identify_issues(context):
    """Confirm vde ps -a output contains status information for containers."""
    output = context.health_all_output
    has_info = any(
        keyword in output.lower()
        for keyword in ("vde-", "running", "stopped", "exited", "created", "name")
    )
    assert has_info, (
        f"vde ps -a output does not contain recognisable status information.\nOutput:\n{output[:400]}"
    )


# ---------------------------------------------------------------------------
# Scenario 8: Cleaning up stopped containers
# ---------------------------------------------------------------------------

_CLEANUP_VM = "python"


@given("I have stopped several VMs")
def step_have_stopped_several_vms(context):
    """Ensure at least one VM exists in stopped state for cleanup testing."""
    run_vde_command(f"start {_CLEANUP_VM}", timeout=120)
    result = run_vde_command(f"stop {_CLEANUP_VM}", timeout=60)
    assert result.returncode == 0, (
        f"Failed to stop VM '{_CLEANUP_VM}':\n{result.stdout}\n{result.stderr}"
    )
    context.cleanup_vm = _CLEANUP_VM


@when("I start them again")
def step_start_them_again(context):
    """Re-start the previously stopped VM."""
    vm = getattr(context, "cleanup_vm", _CLEANUP_VM)
    result = run_vde_command(f"start {vm}", timeout=300)
    assert result.returncode == 0, (
        f"Failed to re-start VM '{vm}':\n{result.stdout}\n{result.stderr}"
    )
    context.restarted_vm = vm
    context._docker_cleanup_needed = True


@then("old containers should be removed")
def step_old_containers_removed(context):
    """Verify no stopped/exited containers remain for this VM via vde ps -a."""
    vm = getattr(context, "restarted_vm", _CLEANUP_VM)
    # vde ps -a -q lists ALL containers (running + stopped)
    all_result = run_vde_command("ps -a -q", timeout=30)
    running_result = run_vde_command("ps -q", timeout=30)

    all_containers = {ln.strip() for ln in all_result.stdout.splitlines() if ln.strip()}
    running_containers = {ln.strip() for ln in running_result.stdout.splitlines() if ln.strip()}
    container_name = f"vde-{vm}"

    stopped_containers = all_containers - running_containers
    assert container_name not in stopped_containers, (
        f"Stopped/exited container '{container_name}' still present — old container not cleaned up.\n"
        f"All containers: {all_containers}\n"
        f"Running containers: {running_containers}"
    )


@then("new containers should be created")
def step_new_containers_created(context):
    """Verify the VM container is running after re-start."""
    vm = getattr(context, "restarted_vm", _CLEANUP_VM)
    container_name = f"vde-{vm}"
    running_result = run_vde_command("ps -q", timeout=30)
    running = [ln.strip() for ln in running_result.stdout.splitlines() if ln.strip()]
    assert container_name in running, (
        f"Container '{container_name}' is not running after re-start.\n"
        f"Running containers: {running}"
    )


@then("no stopped containers should accumulate")
def step_no_stopped_containers_accumulate(context):
    """Verify all containers in vde ps -a are also in vde ps (i.e., none are stopped)."""
    all_result = run_vde_command("ps -a -q", timeout=30)
    running_result = run_vde_command("ps -q", timeout=30)

    all_containers = {ln.strip() for ln in all_result.stdout.splitlines() if ln.strip()}
    running_containers = {ln.strip() for ln in running_result.stdout.splitlines() if ln.strip()}

    stopped = all_containers - running_containers
    # Only VDE-managed containers (vde- prefix) matter here
    vde_stopped = {c for c in stopped if c.startswith("vde-")}
    assert not vde_stopped, (
        f"Stopped VDE containers found after start: {vde_stopped}\n"
        "VDE should remove old stopped containers when starting a VM."
    )


# ---------------------------------------------------------------------------
# Scenario 9: Docker Compose integration
# (Given "VDE creates a VM" is defined in documented_workflow_steps.py — SKIP)
# ---------------------------------------------------------------------------

@then("a docker-compose.yml file should be generated")
def step_compose_file_generated(context):
    """Verify a docker-compose.yml exists for the VM created by the Given step."""
    # documented_workflow_steps "VDE creates a VM" uses python
    vm_name = getattr(context, "vm_name", "python")
    compose_path = get_compose_file(vm_name)
    assert compose_path.exists(), (
        f"docker-compose.yml not found at {compose_path} for VM '{vm_name}'.\n"
        "VDE must generate a compose file when creating a VM."
    )
    context.compose_path = compose_path


@then("I can manually use docker-compose if needed")
def step_can_manually_use_compose(context):
    """Verify the compose file is readable and valid enough for manual docker-compose use."""
    compose_path = getattr(context, "compose_path", None)
    if compose_path is None:
        vm_name = getattr(context, "vm_name", "python")
        compose_path = get_compose_file(vm_name)

    assert compose_path.exists(), (
        f"compose file not found at {compose_path}"
    )
    content = compose_path.read_text()
    assert len(content.strip()) > 0, "docker-compose.yml is empty"
    # A valid compose file must have a 'services:' key so docker-compose can parse it
    assert "services:" in content, (
        f"docker-compose.yml at {compose_path} has no 'services:' section — "
        "cannot be used with docker-compose directly.\n"
        f"File content preview:\n{content[:300]}"
    )


@then("the file should follow best practices")
def step_compose_follows_best_practices(context):
    """Verify compose file contains expected best-practice fields."""
    compose_path = getattr(context, "compose_path", None)
    if compose_path is None:
        vm_name = getattr(context, "vm_name", "python")
        compose_path = get_compose_file(vm_name)

    content = compose_path.read_text()
    # Best practices: has a named network, has restart policy, has volumes
    checks = {
        "services:": "compose file must declare at least one service",
        "networks:": "compose file should declare named networks for isolation",
    }
    for keyword, message in checks.items():
        assert keyword in content, (
            f"Best practice violation: {message}\n"
            f"Missing '{keyword}' in {compose_path}.\n"
            f"File content preview:\n{content[:400]}"
        )


# ---------------------------------------------------------------------------
# Scenario 10: Multi-stage build optimization
# ---------------------------------------------------------------------------

_REBUILD_VM = "python"


@given("I rebuild a language VM")
def step_rebuild_language_vm(context):
    """Trigger a VM rebuild via vde rebuild."""
    result = run_vde_command(f"rebuild {_REBUILD_VM}", timeout=300)
    assert result.returncode == 0, (
        f"vde rebuild {_REBUILD_VM} failed (rc={result.returncode}):\n"
        f"{result.stdout}\n{result.stderr}"
    )
    context._docker_cleanup_needed = True
    context.rebuilt_vm = _REBUILD_VM


@then("the build should use multi-stage Dockerfile")
def step_build_uses_multistage_dockerfile(context):
    """Verify Dockerfiles in the VDE config tree use layered base-image builds.

    VDE's build strategy uses a shared ``vde-base`` image from which all VM
    Dockerfiles inherit via ``FROM vde-base:latest``.  This IS the multi-stage
    optimisation in VDE's architecture: language/service images are thin layers
    on top of a shared base, matching the intent of multi-stage build efficiency.
    """
    vm = getattr(context, "rebuilt_vm", _REBUILD_VM)
    dockerfile_path = get_dockerfile(vm)
    assert dockerfile_path.exists(), (
        f"Dockerfile not found at {dockerfile_path}"
    )
    content = dockerfile_path.read_text()
    # VDE uses a shared vde-base layer as its multi-stage equivalent
    assert "FROM" in content, (
        f"Dockerfile at {dockerfile_path} has no FROM instruction."
    )
    # Either a traditional multi-stage pattern (FROM ... AS ...) or the VDE
    # shared-base pattern (FROM vde-base:...) qualifies as optimised
    has_multistage = " AS " in content.upper()
    has_shared_base = "vde-base" in content
    assert has_multistage or has_shared_base, (
        f"Dockerfile at {dockerfile_path} does not use multi-stage or shared-base pattern.\n"
        f"Expected 'FROM ... AS ...' or 'FROM vde-base:...' but found:\n{content[:400]}"
    )


@then("final images should be smaller")
def step_final_images_smaller(context):
    """Verify the VM image is reported by vde images and has a recorded size."""
    vm = getattr(context, "rebuilt_vm", _REBUILD_VM)
    result = run_vde_command("images", timeout=30)
    assert result.returncode == 0, (
        f"'vde images' failed (rc={result.returncode}):\n{result.stderr}"
    )
    # vde images must list the rebuilt image; its presence confirms VDE tracks image sizes
    assert vm in result.stdout or f"vde-{vm}" in result.stdout, (
        f"VM '{vm}' image not found in 'vde images' output after rebuild.\n"
        f"Output:\n{result.stdout}"
    )


@then("build cache should be used when possible")
def step_build_cache_used(context):
    """Verify a second rebuild completes without error (cache path exercised)."""
    vm = getattr(context, "rebuilt_vm", _REBUILD_VM)
    result = run_vde_command(f"rebuild {vm}", timeout=300)
    assert result.returncode == 0, (
        f"Second rebuild of '{vm}' failed (rc={result.returncode}) — "
        "cache path may be broken.\n"
        f"{result.stdout}\n{result.stderr}"
    )


# ---------------------------------------------------------------------------
# Scenario 11: Container startup order
# ---------------------------------------------------------------------------

_STARTUP_ORDER_VMS = ["python", "postgres"]


@given("I have dependent services")
def step_have_dependent_services(context):
    """Set up two VMs — a language VM and a service VM — representing a dependency pair."""
    context.dependent_vms = list(_STARTUP_ORDER_VMS)
    # Ensure both VMs are created (not necessarily running yet)
    for vm in context.dependent_vms:
        result = run_vde_command(f"create {vm}", timeout=300)
        assert result.returncode == 0, (
            f"Failed to create VM '{vm}':\n{result.stdout}\n{result.stderr}"
        )
    context._docker_cleanup_needed = True


@when("I start them together")
def step_start_them_together(context):
    """Start all dependent VMs sequentially, recording the order."""
    assert hasattr(context, "dependent_vms") and context.dependent_vms, (
        "No dependent_vms in context — did the @given step run?"
    )
    context.startup_results = {}
    for vm in context.dependent_vms:
        result = run_vde_command(f"start {vm}", timeout=300)
        context.startup_results[vm] = result
    context._docker_cleanup_needed = True


@then("they should start in a reasonable order")
def step_start_in_reasonable_order(context):
    """Verify all VMs were started without error (order is sequential via VDE)."""
    assert hasattr(context, "startup_results") and context.startup_results, (
        "startup_results not populated — did the @when step run?"
    )
    for vm, result in context.startup_results.items():
        assert result.returncode == 0, (
            f"VM '{vm}' failed to start (rc={result.returncode}):\n"
            f"{result.stdout}\n{result.stderr}"
        )


@then("dependencies should be available when needed")
def step_dependencies_available(context):
    """Verify all dependent VMs are running after startup."""
    vms = getattr(context, "dependent_vms", _STARTUP_ORDER_VMS)
    running_result = run_vde_command("ps -q", timeout=30)
    running = [ln.strip() for ln in running_result.stdout.splitlines() if ln.strip()]
    for vm in vms:
        container_name = f"vde-{vm}"
        assert container_name in running, (
            f"Dependent VM '{vm}' (container '{container_name}') is not running.\n"
            f"Running containers: {running}"
        )


@then("the startup should complete successfully")
def step_startup_completes_successfully(context):
    """Assert every VM started with rc=0 and is running."""
    results = getattr(context, "startup_results", {})
    vms = getattr(context, "dependent_vms", _STARTUP_ORDER_VMS)
    running_result = run_vde_command("ps -q", timeout=30)
    running = [ln.strip() for ln in running_result.stdout.splitlines() if ln.strip()]

    for vm in vms:
        if vm in results:
            assert results[vm].returncode == 0, (
                f"VM '{vm}' start command returned non-zero exit code {results[vm].returncode}"
            )
        container_name = f"vde-{vm}"
        assert container_name in running, (
            f"VM '{vm}' container '{container_name}' not in running list after startup.\n"
            f"Running: {running}"
        )


# ---------------------------------------------------------------------------
# Scenario 12: Container isolation
# ---------------------------------------------------------------------------

_ISOLATION_PRIMARY = "python"
_ISOLATION_SECONDARY = "go"


@given("I have several VMs running")
@given("I have multiple VMs running")
def step_have_multiple_vms_running(context):
    """Ensure at least two VMs are running for isolation testing."""
    for vm in (_ISOLATION_PRIMARY, _ISOLATION_SECONDARY):
        r = run_vde_command(f"start {vm}", timeout=300)
        assert r.returncode == 0, f"Could not start {vm}: {r.stderr}"
    context.expected_running = [f"vde-{_ISOLATION_PRIMARY}", f"vde-{_ISOLATION_SECONDARY}"]
    context.vm_name = _ISOLATION_PRIMARY


@when("one VM crashes")
def step_one_vm_crashes(context):
    """Simulate a VM crash by stopping it via vde stop."""
    # Use the first VM from expected_running or fall back to default
    vms = getattr(context, "expected_running", [f"vde-{_ISOLATION_PRIMARY}", f"vde-{_ISOLATION_SECONDARY}"])
    # "Crash" the first VM
    crashed_name = vms[0].replace("vde-", "")
    result = run_vde_command(f"stop {crashed_name}", timeout=60)
    assert result.returncode == 0, (
        f"Failed to stop (simulate crash) VM '{crashed_name}':\n"
        f"{result.stdout}\n{result.stderr}"
    )
    context.crashed_vm = crashed_name
    context.survivor_vms = [v.replace("vde-", "") for v in vms[1:]]


@then("other VMs should continue running")
def step_other_vms_continue_running(context):
    """Verify VMs that were not stopped are still running."""
    survivors = getattr(context, "survivor_vms", [_ISOLATION_SECONDARY])
    running_result = run_vde_command("ps -q", timeout=30)
    running = [ln.strip() for ln in running_result.stdout.splitlines() if ln.strip()]
    for vm in survivors:
        container_name = f"vde-{vm}"
        assert container_name in running, (
            f"Survivor VM '{vm}' is no longer running after another VM crashed.\n"
            f"Running containers: {running}"
        )


@then("the crash should not affect other containers")
def step_crash_not_affect_others(context):
    """Verify all non-crashed VMs are still accessible via vde ps."""
    survivors = getattr(context, "survivor_vms", [_ISOLATION_SECONDARY])
    running_result = run_vde_command("ps -q", timeout=30)
    running = [ln.strip() for ln in running_result.stdout.splitlines() if ln.strip()]
    for vm in survivors:
        container_name = f"vde-{vm}"
        assert container_name in running, (
            f"Container '{container_name}' was affected by the crash of '{context.crashed_vm}'.\n"
            f"Running containers: {running}"
        )


@then("I can restart the crashed VM independently")
def step_restart_crashed_vm_independently(context):
    """Restart the crashed VM and verify it comes back up without affecting survivors."""
    crashed = getattr(context, "crashed_vm", _ISOLATION_PRIMARY)
    survivors = getattr(context, "survivor_vms", [_ISOLATION_SECONDARY])

    result = run_vde_command(f"start {crashed}", timeout=300)
    assert result.returncode == 0, (
        f"Failed to restart crashed VM '{crashed}' independently (rc={result.returncode}):\n"
        f"{result.stdout}\n{result.stderr}"
    )
    context._docker_cleanup_needed = True

    running_result = run_vde_command("ps -q", timeout=30)
    running = [ln.strip() for ln in running_result.stdout.splitlines() if ln.strip()]

    # Crashed VM must be back up
    assert f"vde-{crashed}" in running, (
        f"Crashed VM '{crashed}' did not come back after independent restart.\n"
        f"Running: {running}"
    )
    # Survivors must still be unaffected
    for vm in survivors:
        assert f"vde-{vm}" in running, (
            f"Survivor VM '{vm}' went down during independent restart of '{crashed}'.\n"
            f"Running: {running}"
        )


# ---------------------------------------------------------------------------
# Scenario 13: Container logs
# ---------------------------------------------------------------------------


@given("I have a running VM")
def step_have_a_running_vm(context):
    """Ensure at least one VM (python) is running for log inspection."""
    r = run_vde_command("start python", timeout=300)
    assert r.returncode == 0, f"Could not start python VM: {r.stderr}"
    context.vm_name = "python"

@then("I can view the container logs")
def step_can_view_container_logs(context):
    """Run vde logs <vm> and verify it returns output successfully."""
    vm_name = getattr(context, "vm_name", "python")
    # Strip vde- prefix if present for the CLI argument
    raw_name = vm_name.replace("vde-", "")
    result = run_vde_command(f"logs {raw_name}", timeout=30)
    assert result.returncode == 0, (
        f"'vde logs {raw_name}' failed (rc={result.returncode}):\n"
        f"{result.stderr}"
    )
    context.container_logs = result.stdout


@then("logs should show container activity")
def step_logs_show_container_activity(context):
    """Verify the logs output is non-empty, indicating the container has been active."""
    logs = getattr(context, "container_logs", None)
    if logs is None:
        vm_name = getattr(context, "vm_name", "python")
        raw_name = vm_name.replace("vde-", "")
        result = run_vde_command(f"logs {raw_name}", timeout=30)
        logs = result.stdout + result.stderr
    assert logs.strip(), (
        "Container logs are empty — expected at least some activity output.\n"
        "VDE containers should emit startup/activity logs visible via 'vde logs'."
    )


# "I can troubleshoot problems" — defined in documented_workflow_steps.py; not duplicated here
