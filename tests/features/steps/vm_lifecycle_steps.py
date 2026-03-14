"""
BDD Step Definitions for VM Lifecycle scenarios.
Covers: create-virtual-for, start-virtual, shutdown-virtual, list-vms,
        remove-virtual, add-vm-type, and VDE parser (vde ask) requests.
"""

import json
import os
import shutil
import subprocess
import sys
import time

steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)

from behave import given, then, when
from config import VDE_ROOT

# Import vm_common helpers for real Docker verification
from vm_common import container_exists, compose_file_exists, run_vde_command, container_is_running, wait_for_container, docker_ps, _vm_conf_dir


# =============================================================================
# Helper functions - call real vde-parser
# =============================================================================

def _add_vm_type_temporarily(context, vm_name, vm_type, install_cmd, port=None):
    """Dynamically add a VM type to data/vm-types.conf for testing."""
    conf_file = VDE_ROOT / "data" / "vm-types.conf"
    
    # Backup if not already backed up
    if not hasattr(context, "vm_types_conf_original"):
        context.vm_types_conf_original = conf_file.read_text()
    
    port_str = str(port) if port else ""
    line = f"{vm_type}|vde-{vm_name}|{vm_name}|Test VM|{install_cmd}||{port_str}"
    
    # Append to file
    with open(conf_file, "a") as f:
        f.write(f"\n{line}\n")
    
    # Invalidate cache to ensure it's loaded
    cache_file = VDE_ROOT / ".cache" / "vm-types.cache"
    if cache_file.exists():
        cache_file.unlink()

def _ensure_vm_stopped(vm_name):
    """Stop container if running."""
    from vm_common import container_is_running
    if container_is_running(vm_name):
        run_vde_command(f"stop {vm_name}")

# =============================================================================
# GIVEN — setup steps
# =============================================================================

# Natural language given steps for vm-lifecycle-management.feature


@given("I want to work with a new language")
def step_want_new_language(context):
    """Setup: User wants a new language."""
    context.vm_name = "rust"


@given("I have created a Go VM")
def step_have_go_vm(context):
    """Ensure Go VM is created."""
    if not compose_file_exists("go"):
        run_vde_command("create-virtual-for go", timeout=120)
    context.vm_name = "go"


@given("I have created several VMs")
def step_have_several_created(context):
    """Ensure multiple VMs are created."""
    for vm in ("python", "go", "postgres"):
        if not compose_file_exists(vm):
            run_vde_command(f"create-virtual-for {vm}", timeout=120)


@given("I have several VMs")
def step_have_several_vms(context):
    """Setup: User has multiple VMs."""
    context.vms = ["python", "rust", "postgres"]


@given("I have a running Python VM")
def step_have_running_python(context):
    """Ensure Python VM is running."""
    if not container_is_running("python"):
        run_vde_command("start-virtual python", timeout=180)
    context.vm_name = "python"


@given("I have multiple running VMs")
def step_multiple_running(context):
    """Ensure multiple VMs are active."""
    for vm in ("python", "postgres"):
        if not container_is_running(vm):
            run_vde_command(f"start-virtual {vm}", timeout=180)


@given("I have a running VM")
def step_have_running_vm(context):
    """Ensure at least one VM is running."""
    if not container_is_running("python"):
        run_vde_command("start-virtual python", timeout=180)
    context.vm_name = "python"


@given("I need to refresh a VM")
def step_need_refresh(context):
    """Setup: User wants to restart a VM."""
    context.vm_name = "rust"


@given("I no longer need a VM")
def step_no_longer_need(context):
    """Setup: User wants to remove a VM."""
    context.vm_name = "ruby"


@given("I have modified the Dockerfile")
def step_modified_dockerfile(context):
    """Simulate modifying a Dockerfile."""
    context.vm_name = "python"
    context.rebuild_required = True


@given("I want to update the base image")
def step_update_base(context):
    """Setup: User wants to rebuild all VMs."""
    context.rebuild_all = True


@given("I have updated VDE scripts")
def step_updated_scripts(context):
    """Setup: User updated VDE scripts."""
    context.update_required = True


# =============================================================================
# WHEN — actions
# =============================================================================

@when('I run "{command}"')
def step_run_command(context, command):
    """Execute a VDE command."""
    # Special handling for pipe/chained commands
    if " && " in command:
        parts = [p.strip() for p in command.split(" && ")]
        for part in parts:
            result = run_vde_command(part, timeout=300, context=context)
            if result.returncode != 0:
                break
    else:
        run_vde_command(command, timeout=300, context=context)


@when('I request to "{request}"')
def step_request_to(context, request):
    """Natural language request through vde ask."""
    # Run generate_plan directly to capture intent for verification steps
    vde_parser = VDE_ROOT / "lib" / "vde-parser"
    vde_vm_common = VDE_ROOT / "lib" / "vm-common"
    vde_shell_compat = VDE_ROOT / "lib" / "vde-shell-compat"
    
    cmd = f"source {vde_shell_compat} && source {vde_vm_common} && source {vde_parser} && generate_plan '{request}'"
    res = subprocess.run(["zsh", "-c", cmd], capture_output=True, text=True, cwd=VDE_ROOT)
    
    if res.returncode == 0:
        for line in res.stdout.split('\n'):
            if line.startswith("INTENT:"):
                context.detected_intent = line.replace("INTENT:", "").strip()
                break
    
    # Actually execute it via vde-ask - often requires confirmation - pass 'y' to stdin
    result = run_vde_command(f"vde-ask {request}", timeout=300, context=context, input_text="y\n")
    context.last_request = request


@when('I request "{request}"')
def step_request(context, request):
    """Natural language request (status/info variant)."""
    result = run_vde_command(f"vde-ask {request}", timeout=60, context=context)
    context.last_request = request


@when("I remove its configuration")
def step_remove_vm_configuration(context):
    """Remove current VM config."""
    vm_name = getattr(context, "vm_name", "python")
    run_vde_command(f"remove-virtual {vm_name}", timeout=60, context=context)


@when("I rebuild the VM")
def step_rebuild_vm(context):
    """Rebuild current VM."""
    vm_name = getattr(context, "vm_name", "python")
    run_vde_command(f"start-virtual {vm_name} --rebuild", timeout=300, context=context)


@when("I rebuild my VMs")
def step_rebuild_all_vms(context):
    """Rebuild multiple VMs."""
    for vm in ("python", "postgres"):
        if compose_file_exists(vm):
            run_vde_command(f"start-virtual {vm} --rebuild", timeout=300, context=context)


# ---------------------------------------------------------------------------
# THEN — verification steps
# ---------------------------------------------------------------------------

@then("only service VMs should be listed")
def step_only_service_vms_listed(context):
    output = getattr(context, "last_output", "") or ""
    assert output.strip(), "list-vms --all --svc produced no output"
    assert "Service VMs:" in output, f"'Service VMs:' header not found:\n{output}"
    assert "Language VMs:" not in output, f"'Language VMs:' header should not appear:\n{output}"

@then("the VM configuration should be generated")
def step_vm_config_generated(context):
    vm_name = getattr(context, "vm_name", "rust")
    assert compose_file_exists(vm_name), f"Compose config not generated for {vm_name}"

@then("all three VMs should be created")
def step_all_three_vms_created(context):
    for vm in ("python", "postgres", "redis"):
        assert compose_file_exists(vm), f"VM {vm} not created"

@then("the Go container should start")
def step_go_container_starts(context):
    assert container_is_running("go"), "Go container not running"

@then("all three VMs should start")
def step_all_three_vms_start(context):
    from vm_common import wait_for_container, container_is_running
    for vm in ("python", "go", "postgres"):
        if compose_file_exists(vm):
            wait_for_container(vm, timeout=60)
            assert container_is_running(vm), f"VM {vm} not running"
    context.network_configured = True
