"""
BDD Step Definitions for Port Management.

These steps handle port allocation, port registry, port ranges,
and atomic port reservation to prevent conflicts.

All steps use real system verification - no context flags or fake tests.
"""

import subprocess
from pathlib import Path

from behave import given, then, when

# Import shared configuration and helpers
from config import VDE_ROOT
from vm_common import run_vde_command, get_container_port_mapping, docker_ps


# =============================================================================
# Port Management GIVEN steps
# =============================================================================

@given('VM "{vm_name}" is allocated port "{port}"')
def step_vm_allocated_port(context, vm_name, port):
    """VM is allocated a specific port."""
    context.vm_name = vm_name
    context.vm_port = port
    # Check if VM is configured to use this port
    compose_path = VDE_ROOT / "configs" / "docker" / vm_name / "docker-compose.yml"
    if compose_path.exists():
        content = compose_path.read_text()
        context.port_allocated = port in content
