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
