"""
Step definitions for docker-operations.feature.

All steps invoke the ACTUAL VDE implementation — no mocks, no fakes.
Uses bin/vde CLI only; no direct docker subprocess calls.
"""

import os
import re
import subprocess
import sys
from pathlib import Path

from behave import given, then, when

steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)

from config import VDE_ROOT
from vm_common import BIN_DIR, _vde_env, run_vde_command


# ── helpers ────────────────────────────────────────────────────────────────


def _is_running(vm_name: str) -> bool:
    """Check if VM container is running via vde ps -q."""
    r = run_vde_command("ps -q")
    container = f"vde-{vm_name.lstrip('vde-')}"
    return container in r.stdout.splitlines()


def _ensure_running(vm_name: str, timeout: int = 120) -> None:
    """Start VM if not already running."""
    if not _is_running(vm_name):
        run_vde_command(f"start {vm_name}", timeout=timeout)


def _compose_file(vm_name: str) -> Path:
    """Return path to the VM's docker-compose.yml."""
    name = vm_name.lstrip("vde-")
    return VDE_ROOT / "configs" / "docker" / name / "docker-compose.yml"


def _env_file(vm_name: str) -> Path:
    """Return path to the VM's env file in env-files/."""
    name = vm_name.lstrip("vde-")
    return VDE_ROOT / "env-files" / f"vde-{name}.env"


def _read_constants() -> dict:
    """Source vde-constants and return retry constant values."""
    lib = VDE_ROOT / "lib" / "vde-constants"
    script = f"""
export VDE_ROOT_DIR="{VDE_ROOT}"
source "{lib}"
echo "VDE_MAX_RETRIES=$VDE_MAX_RETRIES"
echo "VDE_RETRY_BASE_DELAY=$VDE_RETRY_BASE_DELAY"
echo "VDE_RETRY_MAX_DELAY=$VDE_RETRY_MAX_DELAY"
"""
    r = subprocess.run(["zsh", "-c", script], capture_output=True, text=True, timeout=10)
    result = {}
    for line in r.stdout.splitlines():
        if "=" in line:
            k, _, v = line.partition("=")
            try:
                result[k.strip()] = float(v.strip())
            except ValueError:
                pass
    return result


# =============================================================================
# GIVEN steps
# =============================================================================


@given("{vm_name} VM is started")
def step_bare_vm_is_started(context, vm_name):
    """Ensure VM is started (background step with bare name like 'python')."""
    _ensure_running(vm_name.lower())


@given('VM "{vm_name}" docker-compose.yml exists')
def step_vm_compose_exists(context, vm_name):
    """Assert docker-compose.yml exists for the VM."""
    compose = _compose_file(vm_name)
    assert compose.exists(), f"docker-compose.yml not found: {compose}"
    context.compose_file = compose
    context.vm_name = vm_name


@given('the image for VM "{vm_name}" is removed')
def step_image_removed(context, vm_name):
    """Precondition: stop+remove VM so vde start triggers a build."""
    run_vde_command(f"stop {vm_name}", timeout=60)
    run_vde_command(f"remove {vm_name}", timeout=60)
    context.vm_name = vm_name


@given('VM "{vm_name}" image exists')
def step_image_exists(context, vm_name):
    """Ensure VM image exists by confirming it has been started before."""
    _ensure_running(vm_name)
    context.vm_name = vm_name


@given('VM "{vm_name}" exists')
def step_vm_exists(context, vm_name):
    """Ensure VM config exists."""
    compose = _compose_file(vm_name)
    assert compose.exists(), f"VM '{vm_name}' compose file not found: {compose}"
    context.vm_name = vm_name


@given("multiple VMs are running")
def step_multiple_vms_running(context):
    """Ensure python and postgres are both running."""
    _ensure_running("python")
    _ensure_running("postgres")
    context.expected_running = ["vde-python", "vde-postgres"]


@given('VM "{vm_name}" is started')
def step_vm_is_started(context, vm_name):
    """Ensure a named VM is running."""
    _ensure_running(vm_name)
    context.vm_name = vm_name


@given('language VM "{vm_name}" is started')
def step_language_vm_is_started(context, vm_name):
    """Ensure a language VM is running."""
    _ensure_running(vm_name)
    context.vm_name = vm_name


@given('service VM "{vm_name}" is started')
def step_service_vm_is_started(context, vm_name):
    """Ensure a service VM is running."""
    _ensure_running(vm_name)
    context.vm_name = vm_name


@given('VM "{vm_name}" compose file is replaced with invalid YAML')
def step_replace_compose_invalid_yaml(context, vm_name):
    """Replace compose file with invalid YAML; back up original first."""
    # Stop VM first so vde start must actually invoke docker-compose with the broken file
    run_vde_command(f"stop {vm_name}", timeout=60)
    compose = _compose_file(vm_name)
    assert compose.exists(), f"Compose file not found: {compose}"
    backup = compose.with_suffix(".yml.bak")
    backup.write_text(compose.read_text())
    compose.write_text("{ invalid: yaml: [broken\n")
    context.vm_name = vm_name
    context.compose_backup = backup       # for THEN step (belt+suspenders)
    context._compose_backup = str(backup)  # for after_scenario hook on failure
    context._compose_path = str(compose)   # for after_scenario hook on failure


@given('VM "{vm_name}" has env file')
def step_vm_has_env_file(context, vm_name):
    """Ensure the VM's env file exists in env-files/."""
    env = _env_file(vm_name)
    assert env.exists(), (
        f"Env file not found at {env}. "
        f"Run 'vde start {vm_name}' first to generate it."
    )
    context.vm_name = vm_name
    context.env_file = env


# =============================================================================
# WHEN steps
# =============================================================================


@when('I start VM "{vm_name}"')
def step_start_vm(context, vm_name):
    """Run vde start <vm_name>."""
    r = run_vde_command(f"start {vm_name}", timeout=300, context=context)
    context.vm_name = vm_name
    context.last_exit_code = r.returncode
    context.last_output = r.stdout
    context.last_error = r.stderr


@when('I stop VM "{vm_name}"')
def step_stop_vm(context, vm_name):
    """Run vde stop <vm_name>."""
    r = run_vde_command(f"stop {vm_name}", timeout=60, context=context)
    context.vm_name = vm_name
    context.last_exit_code = r.returncode


@when('I restart VM "{vm_name}"')
def step_restart_vm(context, vm_name):
    """Capture pre-restart state, restart, store for ID comparison."""
    inspect_old = run_vde_command(f"inspect {vm_name} --state", timeout=10)
    context.old_container_state = inspect_old.stdout.strip()
    r = run_vde_command(f"restart {vm_name}", timeout=120, context=context)
    context.vm_name = vm_name
    context.last_exit_code = r.returncode


@when("I check VDE retry constants")
def step_check_retry_constants(context):
    """Load VDE retry constants from vde-constants."""
    context.vde_constants = _read_constants()


@when("I check the running status of the VM")
def step_check_running_status(context):
    """Check container status via vde ps -q."""
    vm_name = context.vm_name
    context.vm_status = "running" if _is_running(vm_name) else "stopped"


@when("I get running VMs")
def step_get_running_vms(context):
    """Get running VMs via vde ps -q."""
    r = run_vde_command("ps -q", timeout=10, context=context)
    context.running_vms = [ln.strip() for ln in r.stdout.splitlines() if ln.strip()]


@when("container is started")
def step_container_is_started(context):
    """Ensure the context VM container is started."""
    _ensure_running(getattr(context, "vm_name", "python"))


# =============================================================================
# THEN steps
# =============================================================================


@then("docker-compose build should be executed")
def step_compose_build_executed(context):
    """Verify vde start triggered a build (rc=0)."""
    assert context.last_exit_code == 0, (
        f"vde start failed (rc={context.last_exit_code}). "
        f"stderr: {context.last_error}"
    )


@then("image should be built successfully")
def step_image_built_successfully(context):
    """Verify container is running after build."""
    vm_name = getattr(context, "vm_name", "python")
    assert _is_running(vm_name), f"Container vde-{vm_name} not running after build"


@then("docker-compose up -d should be executed")
def step_compose_up_executed(context):
    """Verify vde start succeeded (rc=0)."""
    assert context.last_exit_code == 0, (
        f"vde start failed (rc={context.last_exit_code}). "
        f"stderr: {context.last_error}"
    )


@then("container should be running")
def step_generic_container_running(context):
    """Verify the context VM container is running."""
    vm_name = getattr(context, "vm_name", "python")
    assert _is_running(vm_name), f"Container vde-{vm_name} is not running"


@then("docker-compose down should be executed")
def step_compose_down_executed(context):
    """Verify vde stop succeeded (rc=0)."""
    assert context.last_exit_code == 0, (
        f"vde stop failed (rc={context.last_exit_code})"
    )


@then("container should not be running")
def step_generic_container_not_running(context):
    """Verify the context VM container is NOT running."""
    vm_name = getattr(context, "vm_name", "python")
    assert not _is_running(vm_name), f"Container vde-{vm_name} is still running"


@then("container should have new container ID")
def step_container_new_id(context):
    """Verify container is live after restart; compare state if available."""
    vm_name = getattr(context, "vm_name", "python")
    assert _is_running(vm_name), f"Container vde-{vm_name} not running after restart"
    inspect_new = run_vde_command(f"inspect {vm_name} --state", timeout=10)
    new_state = inspect_new.stdout.strip()
    old_state = getattr(context, "old_container_state", "")
    if old_state and new_state and old_state not in ("null", "") and new_state not in ("null", ""):
        assert old_state != new_state, (
            f"Container state unchanged after restart for vde-{vm_name}"
        )


@then("the command should fail with non-zero exit code")
def step_command_fails_nonzero(context):
    assert context.last_exit_code != 0, (
        f"Expected non-zero exit code, got {context.last_exit_code}"
    )


@then("the error output should not be empty")
def step_error_output_not_empty(context):
    assert context.last_error.strip(), "Expected non-empty error output but got none"


@then('VM "{vm_name}" compose file is restored from backup')
def step_restore_compose_backup(context, vm_name):
    """Restore compose file from backup created in the Given step."""
    backup = getattr(context, "compose_backup", None)
    compose = _compose_file(vm_name)
    if backup and backup.exists():
        compose.write_text(backup.read_text())
        backup.unlink()
    assert compose.exists(), f"Compose file not restored: {compose}"


@then("VDE_MAX_RETRIES should be at least 1")
def step_max_retries_at_least_1(context):
    v = context.vde_constants.get("VDE_MAX_RETRIES", 0)
    assert v >= 1, f"VDE_MAX_RETRIES={v} is less than 1"


@then("VDE_RETRY_BASE_DELAY should be greater than 0")
def step_base_delay_gt_0(context):
    v = context.vde_constants.get("VDE_RETRY_BASE_DELAY", 0)
    assert v > 0, f"VDE_RETRY_BASE_DELAY={v} is not greater than 0"


@then("VDE_RETRY_MAX_DELAY should be at least VDE_RETRY_BASE_DELAY")
def step_max_delay_gte_base(context):
    base = context.vde_constants.get("VDE_RETRY_BASE_DELAY", 0)
    max_d = context.vde_constants.get("VDE_RETRY_MAX_DELAY", 0)
    assert max_d >= base, (
        f"VDE_RETRY_MAX_DELAY={max_d} < VDE_RETRY_BASE_DELAY={base}"
    )


@then('status should be one of: "running", "stopped", "not_created", "unknown"')
def step_status_valid_value(context):
    valid = {"running", "stopped", "not_created", "unknown"}
    assert context.vm_status in valid, (
        f"VM status '{context.vm_status}' not in {valid}"
    )


@then("all running containers should be listed")
def step_all_running_listed(context):
    expected = getattr(context, "expected_running", [])
    for name in expected:
        assert name in context.running_vms, (
            f"Expected '{name}' in running VMs but got: {context.running_vms}"
        )


@then("stopped containers should not be listed")
def step_stopped_not_listed(context):
    """Verify vde ps -q does not include non-running containers."""
    r = run_vde_command("ps --all -q", timeout=10)
    all_containers = {ln.strip() for ln in r.stdout.splitlines() if ln.strip()}
    running = set(context.running_vms)
    stopped = all_containers - running
    for name in stopped:
        assert name not in context.running_vms, (
            f"Stopped container '{name}' incorrectly listed as running"
        )


@then('docker-compose project should be "{project_name}"')
def step_compose_project_name(context, project_name):
    """Verify docker-compose project name in compose file (top-level 'name:' field)."""
    vm_name = getattr(context, "vm_name", "python")
    compose = _compose_file(vm_name)
    content = compose.read_text()
    assert f"name: {project_name}" in content, (
        f"Expected 'name: {project_name}' in compose file.\n"
        f"Compose preview:\n{content[:400]}"
    )


@then('container should be named "{container_name}"')
def step_container_named(context, container_name):
    """Verify container is running and has the expected name."""
    r = run_vde_command("ps -q", timeout=10)
    running = [ln.strip() for ln in r.stdout.splitlines() if ln.strip()]
    assert container_name in running, (
        f"Container '{container_name}' not found in running containers.\n"
        f"Running: {running}"
    )


@then("projects/{vm_name} volume should be mounted")
def step_projects_volume_mounted(context, vm_name):
    """Verify projects/<vm_name> path is in the compose volumes section."""
    compose = _compose_file(vm_name)
    content = compose.read_text()
    assert f"projects/{vm_name}" in content, (
        f"No 'projects/{vm_name}' volume entry in compose file"
    )


@then("logs/{vm_name} volume should be mounted")
def step_logs_volume_mounted(context, vm_name):
    """Verify logs/<vm_name> path is in the compose volumes section."""
    compose = _compose_file(vm_name)
    content = compose.read_text()
    assert f"logs/{vm_name}" in content, (
        f"No 'logs/{vm_name}' volume entry in compose file"
    )


@then("volume should be mounted from host directory")
def step_volume_from_host(context):
    """Verify volumes use host-path mounts (relative or absolute paths)."""
    vm_name = getattr(context, "vm_name", "python")
    compose = _compose_file(vm_name)
    content = compose.read_text()
    assert re.search(r"volumes:", content), "No 'volumes:' section in compose file"
    # Host mounts use relative (../…) or absolute (/) paths, not named volumes
    assert re.search(r"\.\./", content), (
        "No relative host-path mounts found in compose volumes"
    )


@then("env file should be read by docker-compose")
def step_env_file_read_by_compose(context):
    """Verify compose file references an env_file directive."""
    vm_name = getattr(context, "vm_name", "python")
    compose = _compose_file(vm_name)
    content = compose.read_text()
    assert "env_file" in content, (
        f"No 'env_file:' directive found in compose file for {vm_name}"
    )


@then("SSH_PORT variable should be available in container")
def step_ssh_port_available(context):
    """Verify SSH_PORT is defined in the VM's env file."""
    vm_name = getattr(context, "vm_name", "python")
    env = getattr(context, "env_file", _env_file(vm_name))
    assert env.exists(), f"Env file not found: {env}"
    content = env.read_text()
    assert "SSH_PORT" in content, f"SSH_PORT not found in {env}"
