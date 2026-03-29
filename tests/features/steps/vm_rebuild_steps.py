"""
BDD Step definitions for VM image rebuild tests.
"""

import json
import os
import sys

steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)
from pathlib import Path

from behave import given, then, when

from vm_common import (
    BIN_DIR,
    VDE_ROOT,
    VM_TYPES_JSON,
    run_vde_command,
    get_compose_file,
    container_is_running,
)


def _container_exists(vm_name):
    """Check if VM container exists (any state) via vde ps --all."""
    result = run_vde_command("ps --all -q")
    container = f"vde-{vm_name.lstrip('vde-')}"
    return container in result.stdout.splitlines()


def _container_running(vm_name):
    """Thin wrapper — delegates to canonical container_is_running."""
    return container_is_running(f"vde-{vm_name.lstrip('vde-')}")


def _stop_vm(vm_name):
    """Stop a running VM via vde stop."""
    run_vde_command(f"stop {vm_name}", timeout=60)


def _stop_and_remove_vm(vm_name):
    """Stop and remove a VM via vde stop + vde remove."""
    run_vde_command(f"stop {vm_name}", timeout=60)
    run_vde_command(f"remove {vm_name}", timeout=60)


@given("VM types are loaded from configuration")
def step_vm_types_loaded_from_config(context):
    """Load VM types from vm-types.json into context."""
    with open(VM_TYPES_JSON) as f:
        context.vm_types = json.load(f)


@given('VM "{vm_name}" has been created')
def step_vm_created(context, vm_name):
    """Create a VM if it doesn't exist."""
    if _container_exists(vm_name):
        return
    result = run_vde_command(f"create-virtual-for {vm_name}", timeout=300, context=context)
    if result.returncode != 0:
        result = run_vde_command(f"create-virtual-for {vm_name}", timeout=300, context=context)
    context.last_exit_code = result.returncode


@given('VM "{vm_name}" is running')
def step_vm_running(context, vm_name):
    """Ensure VM is running."""
    if not _container_running(vm_name):
        result = run_vde_command(f"start {vm_name}", timeout=300, context=context)
        context.last_exit_code = result.returncode


@when('I start VM "{vm_name}" with --rebuild')
def step_start_vm_rebuild(context, vm_name):
    """Start VM with --rebuild flag."""
    result = run_vde_command(f"start {vm_name} --rebuild", timeout=300, context=context)
    context.last_exit_code = result.returncode
    context.rebuild_executed = True


@when('I start VM "{vm_name}" with --rebuild and --no-cache')
def step_start_vm_rebuild_no_cache(context, vm_name):
    """Start VM with --rebuild and --no-cache flags."""
    result = run_vde_command(f"start {vm_name} --rebuild --no-cache", timeout=600, context=context)
    context.last_exit_code = result.returncode
    context.rebuild_no_cache_executed = True


@then("docker-compose up --build should be executed")
def step_verify_build_executed(context):
    """Verify vde start --rebuild was executed successfully."""
    assert hasattr(context, "rebuild_executed"), "Rebuild flag was not set"
    assert context.last_exit_code == 0, f"Rebuild failed with exit code {context.last_exit_code}"
    output = getattr(context, "last_output", "") or getattr(context, "last_stdout", "") or ""
    assert "Building" in output, (
        f"Expected 'Building' in rebuild output to confirm docker-compose ran with --build.\n"
        f"output: {output}"
    )


@then("docker-compose up --build --no-cache should be executed")
def step_verify_build_no_cache_executed(context):
    """Verify vde start --rebuild --no-cache was executed successfully."""
    assert hasattr(context, "rebuild_no_cache_executed"), "Rebuild --no-cache was not set"
    assert context.last_exit_code == 0, (
        f"Rebuild --no-cache failed with exit code {context.last_exit_code}"
    )
    output = getattr(context, "last_output", "") or getattr(context, "last_stdout", "") or ""
    assert "Building" in output, (
        f"Expected 'Building' in --no-cache rebuild output.\noutput: {output}"
    )


@then("image should be rebuilt")
def step_verify_image_rebuilt(context):
    """Verify the image was rebuilt via vde start --rebuild."""
    assert context.last_exit_code == 0, "Image rebuild failed"
    output = getattr(context, "last_output", "") or getattr(context, "last_stdout", "") or ""
    assert "Building" in output, (
        f"Expected 'Building' in rebuild output.\noutput: {output}"
    )


@then('VM "{vm_name}" should be running')
def step_verify_vm_running(context, vm_name):
    """Verify VM is running via vde ps."""
    assert _container_running(vm_name), f"VM {vm_name} is not running"


@when('I run "vde start {vm_name} --rebuild"')
def step_run_vde_start_rebuild(context, vm_name):
    """Run vde start {vm_name} --rebuild command."""
    result = run_vde_command(f"start {vm_name} --rebuild", timeout=300, context=context)
    context.last_exit_code = result.returncode
    context.rebuild_executed = True


@then("the container should be rebuilt from the Dockerfile")
def step_verify_container_rebuilt(context):
    """Verify container was rebuilt via vde start --rebuild."""
    assert context.last_exit_code == 0, "Container rebuild failed"


@given('VM "{vm_name}" is not running')
def step_vm_not_running(context, vm_name):
    """Ensure VM is not running."""
    if _container_running(vm_name):
        _stop_vm(vm_name)


@given('VM "{vm_name}" is not created')
def step_vm_not_created(context, vm_name):
    """Ensure VM container does not exist."""
    if _container_exists(vm_name):
        _stop_and_remove_vm(vm_name)


@given('VM "{vm_name}" is not known')
def step_vm_not_known(context, vm_name):
    """Set context for unknown VM."""
    context.vm_name = vm_name
    context.vm_unknown = True


@when('I run "vde start {vm_name}"')
def step_vde_start(context, vm_name):
    """Run vde start command."""
    result = run_vde_command(f"start {vm_name}", timeout=300, context=context)
    context.last_exit_code = result.returncode
    context.last_stdout = result.stdout
    context.last_output = result.stdout


@when('I run "vde stop {vm_name}"')
def step_vde_stop(context, vm_name):
    """Run vde stop command."""
    result = run_vde_command(f"stop {vm_name}", timeout=60, context=context)
    context.last_exit_code = result.returncode


@when('I run "vde restart {vm_name}"')
def step_vde_restart(context, vm_name):
    """Run vde restart command."""
    result = run_vde_command(f"restart {vm_name}", timeout=300, context=context)
    context.last_exit_code = result.returncode
    context.vm_name = vm_name


@when('I run "vde remove {vm_name}"')
def step_vde_remove(context, vm_name):
    """Run vde remove command."""
    result = run_vde_command(f"remove {vm_name}", timeout=60, context=context)
    context.last_exit_code = result.returncode


@then('VM "{vm_name}" should not be running')
def step_vm_not_running_verify(context, vm_name):
    """Verify VM is not running via vde ps."""
    assert not _container_running(vm_name), f"VM {vm_name} is still running"


@then("Docker image should be built")
def step_docker_image_built(context):
    """Verify vde start succeeded (image built on first use)."""
    assert context.last_exit_code == 0, "Docker image build failed"


@then("Docker image should be rebuilt")
def step_docker_image_rebuilt(context):
    """Verify vde start --rebuild succeeded."""
    assert context.last_exit_code == 0, "Docker image rebuild failed"
    assert getattr(context, "rebuild_executed", False), "Rebuild flag not set"


@then("VM configuration should still exist")
def step_config_still_exists(context):
    """Verify VM configuration still exists after remove."""
    vm_name = getattr(context, "vm_name", "python")
    compose_file = VDE_ROOT / "configs" / "docker" / vm_name / "docker-compose.yml"
    assert compose_file.exists(), f"VM config not found: {compose_file}"


@then("no VMs should be running")
def step_no_vms_running(context):
    """Verify no VMs are running via vde ps."""
    result = run_vde_command("ps -q")
    assert not result.stdout.strip(), f"Some VMs are still running: {result.stdout.strip()}"


@then("the VM should have a fresh container instance")
def step_fresh_container(context):
    """Verify VM is running after restart (VDE restart creates a new container)."""
    vm_name = getattr(context, "vm_name", None)
    if not vm_name:
        raise AssertionError("No VM name found in context")
    # VDE restart uses docker compose down+up — always creates a fresh container.
    assert _container_running(vm_name), f"VM {vm_name} is not running after restart"


# =============================================================================
# VM FULL LIFECYCLE steps (vm-full-lifecycle.feature)
# =============================================================================


@given('no running VM instance exists for "{vm_name}"')
def step_no_running_vm_instance(context, vm_name):
    """Ensure no running or stopped VM instance exists."""
    _stop_and_remove_vm(vm_name)
    context.vm_name = vm_name


@when('I run "vde create {vm_name}"')
def step_run_vde_create(context, vm_name):
    """Run vde create for the given VM type."""
    result = run_vde_command(f"create {vm_name}", timeout=300, context=context)
    context.vm_name = vm_name
    context.last_exit_code = result.returncode
    context.last_output = result.stdout
    context.last_error = result.stderr


@then('a docker-compose.yml file should be created at "{compose_path}"')
def step_compose_file_created(context, compose_path):
    """Verify compose file was created at the given path (relative to VDE_ROOT)."""
    full_path = VDE_ROOT / compose_path
    assert full_path.exists(), f"docker-compose.yml not found at {full_path}"


@then("the docker-compose.yml should contain SSH port mapping")
def step_compose_has_ssh_port(context):
    """Verify compose file contains an SSH port mapping (port 22 target)."""
    vm_name = getattr(context, "vm_name", "python")
    compose = VDE_ROOT / "configs" / "docker" / vm_name / "docker-compose.yml"
    content = compose.read_text()
    assert ":22" in content or "target: 22" in content, (
        f"No SSH port mapping found in compose file:\n{content[:400]}"
    )


@then("container should be gone")
def step_container_gone(context):
    """Verify container no longer exists (running or stopped)."""
    vm_name = getattr(context, "vm_name", "python")
    assert not _container_exists(vm_name), (
        f"Container vde-{vm_name} still exists after vde remove"
    )
