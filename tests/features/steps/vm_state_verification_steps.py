"""
BDD Step Definitions for VM State Verification.

These steps verify VM states including running, crashed, building, etc.
"""
import subprocess
import os
import sys
import time
from pathlib import Path

# Add steps directory to path for imports
steps_dir = os.path.dirname(os.path.abspath(__file__))
if steps_dir not in sys.path:
    sys.path.insert(0, steps_dir)

from behave import given

from config import VDE_ROOT
from vm_common import run_vde_command, docker_ps, container_exists

# =============================================================================
# VM STATE GIVEN steps
# =============================================================================

@given('a VM is running')
def step_vm_running(context):
    """A VM is running."""
    running = docker_ps()
    vde_running = [c for c in running if c.startswith("vde-")]
    context.vm_running = len(vde_running) > 0
    if not hasattr(context, 'running_vms'):
        context.running_vms = set()
    for c in vde_running:
        context.running_vms.add(c.replace("vde-", ""))


@given('a VM has crashed')
def step_vm_crashed(context):
    """VM has crashed - check for exited containers via vde ps."""
    result = run_vde_command("ps -a --filter status=exited", context=context)
    # Output format includes container names
    crashed_containers = [line for line in result.stdout.split('\n') if 'vde-' in line]
    context.vm_crashed = len(crashed_containers) > 0
    if crashed_containers:
        # Simple extraction of VM name from output line
        import re
        m = re.search(r'vde-(\S+)', crashed_containers[0])
        if m:
            context.crashed_vm = m.group(1)


@given('a VM has been removed')
def step_vm_removed(context):
    """VM has been removed - check for VM where config directory is missing."""
    configs_dir = VDE_ROOT / "configs" / "docker"
    # This is a conceptual check for BDD - if we're testing removal, 
    # we expect some VMs to NOT have configs
    if configs_dir.exists():
        # Check for a VM type that exists in data but not in configs
        vm_types_file = VDE_ROOT / "data" / "vm-types.conf"
        if vm_types_file.exists():
            for line in vm_types_file.read_text().splitlines():
                if '|' in line and not line.startswith('#'):
                    vm_name = line.split('|')[1].replace('vde-', '')
                    if not (configs_dir / vm_name).exists():
                        context.vm_removed = True
                        context.removed_vm = vm_name
                        return
    context.vm_removed = False


@given('a VM is being built')
def step_vm_building(context):
    """VM is being built - check for active VDE build processes."""
    try:
        result = subprocess.run(["ps", "aux"], capture_output=True, text=True, timeout=5)
        # Check for vde start/rebuild or docker build
        context.vm_building = any(x in result.stdout.lower() for x in ["vde start", "vde rebuild", "docker build"])
    except Exception:
        context.vm_building = False


@given('a VM is not working correctly')
def step_vm_not_working(context):
    """VM is not working correctly - check for non-running state of an expected VM."""
    # If no containers are running, something might be wrong
    running = docker_ps()
    context.vm_not_working = len(running) == 0
