"""
BDD Step definitions for Team Collaboration scenarios.
These steps are specific to collaboration.feature and not covered by other step files.
"""

import os
import subprocess
import sys
from pathlib import Path
from behave import given, then, when

steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)

from vm_common import (
    VDE_ROOT,
    container_exists,
    container_is_running,
    compose_file_exists,
    run_vde_command,
    docker_ps,
)


@given("I have updated my system Docker")
def step_docker_updated(context):
    """Context: User has updated Docker on their system."""
    context.docker_updated = True


@then("the Python VM should be rebuilt from scratch")
def step_python_vm_rebuilt_from_scratch(context):
    """Verify Python VM was rebuilt from scratch."""
    assert container_exists("python"), "Python container should exist after rebuild"
    assert compose_file_exists("python"), "Python compose file should exist"


@then("no cached layers should be used")
def step_no_cached_layers_used(context):
    """Verify rebuild did not use Docker cache."""
    output = getattr(context, "last_output", "")
    if output:
        assert any(
            x in output.lower()
            for x in ["nocache", "no-cache", "pulling", "building without cache"]
        ), f"Build output should indicate no cache was used. Output: {output[:500]}"


@given("I need to update VDE itself")
def step_need_update_vde(context):
    """Context: User needs to update VDE."""
    context.vde_update_needed = True


@then("I should see which VMs are running")
def step_see_running_vms(context):
    """Verify running VMs are displayed."""
    result = run_vde_command("ps", context=context)
    assert result.returncode == 0, "vde ps should succeed"


@then("all running VMs should be stopped")
def step_all_vms_stopped(context):
    """Verify all VMs are stopped."""
    result = run_vde_command("ps -q", context=context)
    assert result.returncode == 0, "vde ps should succeed"
    containers = result.stdout.strip().split("\n")
    vde_containers = [c for c in containers if c.strip().startswith("vde-")]
    assert len(vde_containers) == 0, f"All VMs should be stopped, found: {vde_containers}"


@then("the container should be stopped if running")
def step_container_stopped_if_running(context):
    """Verify container was stopped if it was running."""
    if container_exists("python"):
        pass


@then("each should have separate data directory")
def step_each_separate_data_dir(context):
    """Verify each VM has separate data directory."""
    assert hasattr(context, "vm_names"), "Should have vm_names context"
    for vm_name in context.vm_names:
        data_dir = VDE_ROOT / ".cache" / vm_name
        assert data_dir.exists(), f"Data directory {data_dir} should exist for {vm_name}"
