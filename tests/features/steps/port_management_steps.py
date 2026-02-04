"""
BDD Step definitions for Port Management.

These steps handle port allocation, verification, and management for VMs.
"""

import subprocess
import os
from pathlib import Path

from behave import given, then, when

# Import VM naming helpers
from vm_naming_helpers import _get_container_name

# Import Docker helpers
from docker_helpers import get_container_port, DockerVerificationError


# =============================================================================
# GIVEN steps - Setup port states
# =============================================================================

@given('port {port} is available')
def step_port_available(context, port):
    """Verify port is not currently in use."""
    result = subprocess.run(
        ['lsof', '-i', f':{port}'],
        capture_output=True,
        text=True
    )
    context.port_available = result.returncode != 0

    if not context.port_available:
        raise AssertionError(f"Port {port} is already in use")


@given('port {port} is in use')
def step_port_in_use(context, port):
    """Verify port is currently in use."""
    result = subprocess.run(
        ['lsof', '-i', f':{port}'],
        capture_output=True,
        text=True
    )
    context.port_in_use = result.returncode == 0

    if not context.port_in_use:
        raise AssertionError(f"Port {port} is not in use")


@given('SSH port range is configured')
def step_ssh_port_range_configured(context):
    """Verify SSH port range is configured."""
    # Check for port range configuration in VDE_ROOT/.cache/port-registry
    port_registry = Path(VDE_ROOT) / '.cache' / 'port-registry'
    context.port_range_configured = port_registry.exists()


# =============================================================================
# WHEN steps - Port operations
# =============================================================================

@when('I check available ports')
def step_check_available_ports(context):
    """Check which ports are available for allocation."""
    # Scan ports 2200-2299 for available ports
    available_ports = []
    for port in range(2200, 2300):
        result = subprocess.run(
            ['lsof', '-i', f':{port}'],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            available_ports.append(port)

    context.available_ports = available_ports


@when('I allocate port {port} for VM "{vm_name}"')
def step_allocate_port(context, port, vm_name):
    """Allocate a port for a VM in the port registry."""
    port_registry = Path(VDE_ROOT) / '.cache' / 'port-registry'
    port_registry.mkdir(parents=True, exist_ok=True)

    # Write port allocation
    port_file = port_registry / vm_name
    with open(port_file, 'w') as f:
        f.write(port)

    context.port_allocated = True
    context.allocated_port = port


@when('I release port {port} from VM "{vm_name}"')
def step_release_port(context, port, vm_name):
    """Release a port allocation from a VM."""
    port_registry = Path(VDE_ROOT) / '.cache' / 'port-registry'
    port_file = port_registry / vm_name

    if port_file.exists():
        port_file.unlink()

    context.port_released = True


# =============================================================================
# THEN steps - Port verification
# =============================================================================

@then('port {port} should be available for allocation')
def step_port_should_be_allocatable(context, port):
    """Verify port can be allocated."""
    result = subprocess.run(
        ['lsof', '-i', f':{port}'],
        capture_output=True,
        text=True
    )
    assert result.returncode != 0, f"Port {port} should be available"


@then('port {port} should not be available for allocation')
def step_port_not_allocatable(context, port):
    """Verify port cannot be allocated (already in use)."""
    result = subprocess.run(
        ['lsof', '-i', f':{port}'],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Port {port} should not be available"


@then('VM "{vm_name}" should have SSH port {port}')
def step_vm_should_have_ssh_port(context, vm_name, port):
    """Verify VM has correct SSH port mapped."""
    try:
        mapped_port = get_container_port(_get_container_name(vm_name), 22)
        assert mapped_port == int(port), \
            f"VM '{vm_name}' SSH port should be {port}, got {mapped_port}"
    except DockerVerificationError:
        raise AssertionError(f"VM '{vm_name}' does not have port {port} mapped")


@then('VM "{vm_name}" should have port {port} exposed')
def step_vm_should_have_port_exposed(context, vm_name, port):
    """Verify VM has specific port exposed."""
    container_name = _get_container_name(vm_name)

    result = subprocess.run(
        ['docker', 'port', container_name],
        capture_output=True,
        text=True,
        timeout=10
    )

    assert str(port) in result.stdout or f'"{port}"' in result.stdout, \
        f"VM '{vm_name}' should expose port {port}"


@then('I should be able to connect to port {port}')
def step_connect_to_port(context, port):
    """Verify port is reachable."""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    try:
        result = sock.connect_ex(('localhost', int(port)))
        context.port_reachable = result == 0
        assert result == 0, f"Cannot connect to port {port}"
    finally:
        sock.close()


@then('port allocation should be saved')
def step_port_allocation_saved(context):
    """Verify port allocation was saved to registry."""
    assert getattr(context, 'port_allocated', False), "Port was not allocated"
    assert getattr(context, 'allocated_port', None), "No port was allocated"
