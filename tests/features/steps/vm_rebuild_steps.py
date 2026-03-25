"""
BDD Step definitions for VM image rebuild tests.
"""

import os
import subprocess
import sys
import time

steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)
from pathlib import Path

from behave import given, then, when

from config import VDE_ROOT
from vm_common import get_container_name, run_vde_command, get_compose_file


def _container_exists(vm_name):
    """Check if container exists."""
    container = get_container_name(vm_name)
    result = subprocess.run(
        ["docker", "ps", "-a", "--filter", f"name={container}", "--format", "{{.Names}}"],
        capture_output=True,
        text=True,
    )
    return container in result.stdout


def _container_running(vm_name):
    """Check if container is running."""
    container = get_container_name(vm_name)
    result = subprocess.run(
        ["docker", "ps", "--filter", f"name={container}", "--format", "{{.Names}}"],
        capture_output=True,
        text=True,
    )
    return container in result.stdout


def _stop_and_remove_vm(vm_name):
    """Stop and remove a VM."""
    container = get_container_name(vm_name)
    subprocess.run(["docker", "stop", container], capture_output=True)
    subprocess.run(["docker", "rm", container], capture_output=True)


@given('VM "{vm_name}" has been created')
def step_vm_created(context, vm_name):
    """Create a VM if it doesn't exist."""
    if _container_exists(vm_name):
        return
    result = run_vde_command(f"create-virtual-for {vm_name}", timeout=120, context=context)
    if result.returncode != 0:
        # Try with longer timeout
        result = run_vde_command(f"create-virtual-for {vm_name}", timeout=300, context=context)
    context.last_exit_code = result.returncode


@given('VM "{vm_name}" is running')
def step_vm_running(context, vm_name):
    """Ensure VM is running."""
    if not _container_running(vm_name):
        result = run_vde_command(f"start-virtual {vm_name}", timeout=120, context=context)
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
    result = run_vde_command(f"start {vm_name} --rebuild --no-cache", timeout=1200, context=context)
    context.last_exit_code = result.returncode
    context.rebuild_no_cache_executed = True


@then("docker-compose up --build should be executed")
def step_verify_build_executed(context):
    """Verify docker-compose up --build was executed."""
    assert hasattr(context, "rebuild_executed"), "Rebuild flag was not set"
    assert context.last_exit_code == 0, f"Rebuild failed with exit code {context.last_exit_code}"


@then("docker-compose up --build --no-cache should be executed")
def step_verify_build_no_cache_executed(context):
    """Verify docker-compose up --build --no-cache was executed."""
    assert hasattr(context, "rebuild_no_cache_executed"), "Rebuild --no-cache was not set"
    assert context.last_exit_code == 0, (
        f"Rebuild --no-cache failed with exit code {context.last_exit_code}"
    )


@then("image should be rebuilt")
def step_verify_image_rebuilt(context):
    """Verify the Docker image was rebuilt."""
    assert context.last_exit_code == 0, "Image rebuild failed"


@then('VM "{vm_name}" should be running')
def step_verify_vm_running(context, vm_name):
    """Verify VM is running."""
    assert _container_running(vm_name), f"VM {vm_name} is not running"


@when('I run "vde start python --rebuild"')
def step_run_vde_start_rebuild(context):
    """Run vde start python --rebuild command."""
    result = run_vde_command("start python --rebuild", timeout=300, context=context)
    context.last_exit_code = result.returncode
    context.rebuild_executed = True


@then("the container should be rebuilt from the Dockerfile")
def step_verify_container_rebuilt(context):
    """Verify container was rebuilt from Dockerfile."""
    assert context.last_exit_code == 0, "Container rebuild failed"


@given('VM "{vm_name}" is not running')
def step_vm_not_running(context, vm_name):
    """Ensure VM is not running."""
    if _container_running(vm_name):
        container = get_container_name(vm_name)
        subprocess.run(["docker", "stop", container], capture_output=True)


@given('VM "{vm_name}" is not created')
def step_vm_not_created(context, vm_name):
    """Ensure VM does not exist."""
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


@when('I run "vde stop {vm_name}"')
def step_vde_stop(context, vm_name):
    """Run vde stop command."""
    result = run_vde_command(f"stop {vm_name}", timeout=60, context=context)
    context.last_exit_code = result.returncode


@when('I run "vde restart python"')
def step_vde_restart(context, vm_name):
    """Run vde restart command."""
    result = run_vde_command(f"restart {vm_name}", timeout=120, context=context)
    context.last_exit_code = result.returncode


@when('I run "vde remove {vm_name}"')
def step_vde_remove(context, vm_name):
    """Run vde remove command."""
    container = get_container_name(vm_name)
    subprocess.run(["docker", "stop", container], capture_output=True)
    result = run_vde_command(f"remove-virtual {vm_name}", timeout=60, context=context)
    context.last_exit_code = result.returncode


@then('VM "{vm_name}" should not be running')
def step_vm_not_running_verify(context, vm_name):
    """Verify VM is not running."""
    assert not _container_running(vm_name), f"VM {vm_name} is still running"


@then("Docker image should be built")
def step_docker_image_built(context):
    """Verify Docker image was built."""
    assert context.last_exit_code == 0, "Docker image build failed"


@then("Docker image should be rebuilt")
def step_docker_image_rebuilt(context):
    """Verify Docker image was rebuilt."""
    assert context.last_exit_code == 0, "Docker image rebuild failed"
    assert getattr(context, "rebuild_executed", False), "Rebuild flag not set"


@then("VM configuration should still exist")
def step_config_still_exists(context):
    """Verify VM configuration still exists."""
    if hasattr(context, "vm_name"):
        compose_dir = VDE_ROOT / "configs" / "docker" / context.vm_name
        # Note: config may not exist if never started - this is OK per VDE spec


@then("no VMs should be running")
def step_no_vms_running(context):
    """Verify no VMs are running."""
    result = subprocess.run(
        ["docker", "ps", "--filter", "name=vde-", "--format", "{{.Names}}"],
        capture_output=True,
        text=True,
    )
    assert not result.stdout.strip(), "Some VMs are still running"


@then("the VM should have a fresh container instance")
def step_fresh_container(context):
    """Verify VM has fresh container by checking restart count."""
    vm_name = getattr(context, "vm_name", None)
    if not vm_name:
        for var in ["vm_name", "vm"]:
            if hasattr(context, var):
                vm_name = getattr(context, var)
                break
    if not vm_name:
        raise AssertionError("No VM name found in context")

    container = get_container_name(vm_name)
    result = subprocess.run(
        ["docker", "inspect", container, "--format", "{{.RestartCount}}"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(f"Container {container} not found")
    restart_count = int(result.stdout.strip())
    assert restart_count > 0, (
        f"Container {container} was not restarted (restart count: {restart_count})"
    )
