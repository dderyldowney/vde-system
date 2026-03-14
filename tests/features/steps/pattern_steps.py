"""
Comprehensive catch-all step definitions for VDE BDD tests.

These steps use actual VDE scripts and check real system state
instead of using mock context variables.
"""
import os
import sys
import subprocess
from pathlib import Path

# Add steps directory to path for config import
steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)

from behave import given, then, when

from config import VDE_ROOT
from vm_common import run_vde_command, docker_ps, container_exists, wait_for_container

# =============================================================================
# Shell Compatibility Helper Functions
# =============================================================================

def run_shell_command(command, shell='zsh'):
    """Run a command in the specified shell with vde-shell-compat loaded."""
    # Ensure VDE_ROOT is absolute
    root = str(VDE_ROOT.resolve())
    cmd = f"{shell} -c 'source {root}/lib/vde-shell-compat && {command}'"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=root, encoding='utf-8')
    return result


# =============================================================================
# VM STATE PATTERNS
# =============================================================================

@given('"{vm}" VM is created but not running')
def step_vm_created_not_running(context, vm):
    """VM is created but not running - check actual filesystem and Docker state."""
    vm_name = vm.strip('"')
    compose_path = VDE_ROOT / "configs" / "docker" / vm_name / "docker-compose.yml"
    context.vm_created = compose_path.exists()
    context.vm_not_running = not container_exists(vm_name)
    assert context.vm_created, f"VM {vm_name} config missing"
    assert context.vm_not_running, f"VM {vm_name} should not be running"


@given('I have "{vm}" VM running')
def step_i_have_vm_running(context, vm):
    """Ensure VM is running (start if needed)."""
    vm_name = vm.strip('"')
    if not container_exists(vm_name):
        run_vde_command(f"start {vm_name}", context=context)
        wait_for_container(vm_name, timeout=60)
    assert container_exists(vm_name), f"Expected VM {vm_name} to be running"
    context.vm_running = True


@given('I have several VMs running')
def step_have_several_vms_running(context):
    """Check how many VDE VMs are running via vde ps."""
    running = docker_ps()
    vde_running = [c for c in running if c.startswith("vde-")]
    context.num_vms_running = len(vde_running)
    context.running_vms = {c.replace("vde-", "") for c in vde_running}


# Alias for "I have several VMs running"
@given('I have multiple VMs running for VM-to-Host')
def step_have_multiple_vms_running(context):
    """Alias for checking how many VMs are running."""
    step_have_several_vms_running(context)


@given('I have {num} VMs running')
def step_have_n_vms_running(context, num):
    """Check if N VDE VMs are running via vde ps."""
    # Handle descriptive numbers
    if num.lower() in ['several', 'multiple', 'some']:
        min_count = 2
    else:
        try:
            min_count = int(num)
        except ValueError:
            min_count = 1

    running = docker_ps()
    vde_running = [c for c in running if c.startswith("vde-")]
    context.num_vms_running = len(vde_running)
    assert context.num_vms_running >= min_count, f"Expected at least {min_count} VMs, found {context.num_vms_running}"


@given('I have {num} VMs configured for my project')
def step_n_vms_configured(context, num):
    """Check if N VMs are configured in configs/docker."""
    if num.lower() in ['several', 'multiple', 'some']:
        min_count = 2
    else:
        try:
            min_count = int(num)
        except ValueError:
            min_count = 1

    configs_dir = VDE_ROOT / "configs" / "docker"
    if configs_dir.exists():
        count = len([d for d in configs_dir.iterdir() if d.is_dir() and d.name != "vde-base"])
        context.num_vms_configured = count
        assert count >= min_count, f"Expected at least {min_count} configured VMs, found {count}"
